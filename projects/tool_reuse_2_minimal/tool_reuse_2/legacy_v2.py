"""Bounded v2-only engineering patch; no task/threshold changes or v3 import."""
import ctypes,random
from pathlib import Path
import numpy as np,torch,sapien
from transforms3d.quaternions import quat2mat
from mani_skill.examples.motionplanning.panda.motionplanner import PandaArmMotionPlanningSolver
from mani_skill.examples.motionplanning.base_motionplanner.utils import compute_grasp_info_by_obb,get_actor_obb

def seed_planners(seed):
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
 libc=ctypes.CDLL(None);libc.srand.argtypes=[ctypes.c_uint];libc.srand(seed)
 libs=Path('/home/users/lemon/TRO/.conda/tro-baseline/lib/python3.10/site-packages/mplib.libs')
 ompl=ctypes.CDLL(str(next(libs.glob('libompl*.so*'))))
 setter=getattr(ompl,'_ZN4ompl3RNG7setSeedEm');setter.argtypes=[ctypes.c_ulong];setter.restype=None;setter(seed)
 getter=getattr(ompl,'_ZN4ompl3RNG7getSeedEv');getter.restype=ctypes.c_ulong
 assert getter()==seed
 return {'python_numpy_torch_libc_seed':seed,'ompl_seed':getter(),'pinocchio_note':'libc srand fixed for Eigen random configuration source; no claim old runs had controlled seeds'}

def vec(t):return t.detach().cpu().numpy().reshape(-1)

class SafeV2Planner(PandaArmMotionPlanningSolver):
 def __init__(self,env):
  super().__init__(env,base_pose=env.unwrapped.agent.robot.pose,vis=False,debug=False,visualize_target_grasp_pose=False,print_env_info=False,joint_vel_limits=0.75,joint_acc_limits=0.75)
  self.calls=[];self.empty_paths=0;self.phase='init'
 def follow_path(self,result,refine_steps=0):
  if len(result['position'])==0:
   self.empty_paths+=1;q=vec(self.base_env.agent.robot.get_qpos())[:7]
   return self.env.step(np.r_[q,self.gripper_state])
  return super().follow_path(result,refine_steps)
 def move(self,pose,name):
  self.phase=name
  if len(self.calls)>=32:raise TimeoutError('32 movement planning calls exhausted')
  result=self.move_to_pose_with_screw(pose,dry_run=True);kind='screw'
  if isinstance(result,(int,np.integer)) and result==-1:
   result=self.move_to_pose_with_RRTConnect(pose,dry_run=True);kind='RRTConnect'
  if isinstance(result,(int,np.integer)) and result==-1:
   self.calls.append({'phase':name,'kind':kind,'status':'FAILED'})
   raise RuntimeError('planning failed: '+name)
  self.calls.append({'phase':name,'kind':kind,'waypoints':len(result['position']),'status':'PATH_FOUND'})
  value=self.follow_path(result)
  if len(result['position'])==0:
   actual=self.base_env.agent.tcp.pose.sp
   angle=2*np.arccos(np.clip(abs(np.dot(actual.q,pose.q)),0,1))
   if np.linalg.norm(actual.p-pose.p)>0.015 or angle>0.10:
    raise RuntimeError('empty path does not achieve requested pose: '+name)
  return value

def transport_tool(raw,planner,desired,name):
 # Desired TCP is recomputed from the measured in-hand rigid transform.
 tool=raw.l_shape_tool.pose.sp;tcp=raw.agent.tcp.pose.sp
 return planner.move(desired*tool.inv()*tcp,name)

def return_xy(raw,target):
 cube=vec(raw.cube.pose.p);q=vec(raw.cube.pose.q);R=quat2mat(q)[:2,:2]
 half=np.abs(R)@np.array([raw.cube_half_size,raw.cube_half_size])
 options=[(0,0),(.05,0),(-.05,0),(0,.05),(0,-.05),(.035,.035),(.035,-.035),(-.035,.035),(-.035,-.035)]
 candidates=[]
 for off in options:
  xy=target+off;local=cube[:2]-xy
  gaps=[]
  for center,toolhalf in [(np.array([.10,0]),np.array([.10,.025])),(np.array([.175,.05]),np.array([.025,.05]))]:
   separation=np.abs(local-center)-(toolhalf+half)
   gaps.append(float(np.max(separation)))
  clearance=min(gaps)
  if clearance>=.008:candidates.append((np.linalg.norm(off),-clearance,xy,clearance))
 if not candidates:raise RuntimeError('no supported cube-clear return point in unchanged 0.06m goal region')
 chosen=min(candidates,key=lambda x:(x[0],x[1]))
 return chosen[2],chosen[3]

def solve_v2_patch(env,planner,config):
 raw=env.unwrapped;approaching=np.array([0,0,-1]);closing=raw.agent.tcp.pose.to_transformation_matrix()[0,:3,1].cpu().numpy()
 info=compute_grasp_info_by_obb(get_actor_obb(raw.l_shape_tool),approaching=approaching,target_closing=closing,depth=.03)
 # Correct frame of handle offset; keep v2 grasp axis selection.
 grasp=raw.agent.build_grasp_pose(approaching,info['closing'],vec(raw.l_shape_tool.pose.p)+np.array([.02,0,0]))
 planner.move(grasp*sapien.Pose([0,0,-.05]),'reach-tool');planner.move(grasp,'grasp-tool');planner.close_gripper(t=12)
 if not bool(raw.agent.is_grasping(raw.l_shape_tool).item()):raise RuntimeError('tool grasp not verified before lift')
 planner.move(sapien.Pose(grasp.p+np.array([0,0,.20]),grasp.q),'lift-tool')
 if vec(raw.l_shape_tool.pose.p)[2]<.10 or not bool(raw.agent.is_grasping(raw.l_shape_tool).item()):raise RuntimeError('tool grasp lost after lift')
 cube=vec(raw.cube.pose.p);cube_q=vec(raw.cube.pose.q);cubehalf=float(np.sum(np.abs(quat2mat(cube_q)[0,:2]))*raw.cube_half_size)
 # Inner vertical face of hook: local x=.15, local y=.05; place just right
 # of actual cube extent, then translate left using world coordinates.
 hook=np.array([cube[0]+cubehalf+.025-.15,cube[1]-.05,raw.height/2])
 high=hook.copy();high[2]=.20
 transport_tool(raw,planner,sapien.Pose(high),'hook-approach')
 transport_tool(raw,planner,sapien.Pose(hook),'hook-lower')
 pull=hook.copy();pull[0]-=.35
 transport_tool(raw,planner,sapien.Pose(pull),'physical-pull')
 if not bool(raw.agent.is_grasping(raw.l_shape_tool).item()):raise RuntimeError('tool grasp lost after pull')
 high=vec(raw.l_shape_tool.pose.p);high[2]+=.15
 transport_tool(raw,planner,sapien.Pose(high),'lift-after-contact')
 target=np.array([[-.20,-.18],[-.20,.02],[-.05,-.22]][config]);xy,clearance=return_xy(raw,target)
 high=np.r_[xy,.18];transport_tool(raw,planner,sapien.Pose(high),'return-high')
 transport_tool(raw,planner,sapien.Pose(np.r_[xy,raw.height/2]),'return-lower')
 planner.open_gripper(t=20)
 tcp=raw.agent.tcp.pose.sp;planner.move(sapien.Pose(tcp.p+np.array([0,0,.10]),tcp.q),'retreat-after-release')
 # Execute real quiet hold; unchanged static/position criteria below.
 q=vec(raw.agent.robot.get_qpos())[:7]
 for _ in range(10):env.step(np.r_[q,planner.OPEN])
 return {'return_target':target.tolist(),'chosen_supported_xy':xy.tolist(),'clearance':clearance}
