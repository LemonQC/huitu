"""GEO-REPLAN: measured state, ordinary regrasp and native motion planning.
Same pd_joint_pos controller as demonstrations; no learned/novel planner.
"""
import numpy as np,sapien
from transforms3d.euler import euler2quat
from transforms3d.quaternions import quat2mat
from .legacy_v2 import SafeV2Planner,vec,transport_tool
from .env import CFG

def hold(env,planner,n):
 q=vec(env.unwrapped.agent.robot.get_qpos())[:7]
 for _ in range(n):env.step(np.r_[q,planner.gripper_state])

def grasp_tool(env,planner,label):
 raw=env.unwrapped;tool=raw.l_shape_tool.pose.sp
 closing=quat2mat(tool.q)@np.array([0.,1.,0.]);closing[2]=0;closing/=np.linalg.norm(closing)
 current=raw.agent.tcp.pose.to_transformation_matrix()[0,:3,1].cpu().numpy()
 if np.dot(closing,current)<0:closing=-closing
 center=(tool*sapien.Pose([.02,0,0])).p
 grasp=raw.agent.build_grasp_pose(np.array([0,0,-1]),closing,center)
 planner.move(grasp*sapien.Pose([0,0,-.05]),label+'-approach');planner.move(grasp,label+'-grasp');planner.close_gripper(t=12)
 if not bool(raw.agent.is_grasping(raw.l_shape_tool).item()):raise RuntimeError(label+': tool grasp not verified')
 planner.move(sapien.Pose(grasp.p+[0,0,.20],grasp.q),label+'-lift')
 if not bool(raw.agent.is_grasping(raw.l_shape_tool).item()):raise RuntimeError(label+': grasp lost on lift')

def pull_cube(env,planner,cube,goal,label):
 raw=env.unwrapped;current=vec(cube.pose.p);delta=np.asarray(goal)-current[:2];length=float(np.linalg.norm(delta))
 if delta[0]>=-.20:raise ValueError('goal must require >=0.20m toward robot')
 # Orient L's inner face to the real pull direction; retain the same tool.
 direction=-delta/length;yaw=np.arctan2(direction[1],direction[0]);quat=euler2quat(0,0,yaw);R=quat2mat(quat)
 cube_R=quat2mat(vec(cube.pose.q));extent=raw.cube_half_size*np.sum(np.abs(direction@cube_R[:2,:2]))
 face=current.copy();face[:2]+=direction*(extent+.025)
 tool=face-R@np.array([.15,.05,0]);tool[2]=raw.height/2
 high=tool.copy();high[2]=.20
 transport_tool(raw,planner,sapien.Pose(high,quat),label+'-prepare')
 transport_tool(raw,planner,sapien.Pose(tool,quat),label+'-contact-approach')
 final=tool.copy();final[:2]+=delta
 transport_tool(raw,planner,sapien.Pose(final,quat),label+'-pull')
 hold(env,planner,8)

def place_release(env,planner,pose_name):
 raw=env.unwrapped;spec=CFG[pose_name];q=euler2quat(0,0,spec['yaw']);xy=spec['xy']
 high=vec(raw.l_shape_tool.pose.p);high[2]+=.15
 transport_tool(raw,planner,sapien.Pose(high,raw.l_shape_tool.pose.sp.q),'lift-before-place')
 transport_tool(raw,planner,sapien.Pose(np.r_[xy,.20],q),'place-high')
 transport_tool(raw,planner,sapien.Pose(np.r_[xy,raw.height/2],q),'place-low')
 planner.open_gripper(t=20)
 tcp=raw.agent.tcp.pose.sp;planner.move(sapien.Pose(tcp.p+[0,0,.10],tcp.q),'release-retreat');hold(env,planner,10)
 if int(raw.stage_id.item())<3:raise RuntimeError('same first-task postcondition not met: tool not stably released')

def solve_geo(env,planner,pose_name,events):
 raw=env.unwrapped
 grasp_tool(env,planner,'first-grasp')
 p=vec(raw.cube.pose.p);pull_cube(env,planner,raw.cube,p[:2]+[-.35,0],'cube1')
 if int(raw.stage_id.item())<2:raise RuntimeError('cube1 displacement/contact postcondition failed')
 from .audit import serial
 events['prefix_state']=serial(raw.get_state_dict())
 place_release(env,planner,pose_name);events['intermediate_state']=serial(raw.get_state_dict());events['intermediate_stage']=int(raw.stage_id.item())
 grasp_tool(env,planner,'second-grasp');events['regrasp_stage']=int(raw.stage_id.item())
 pull_cube(env,planner,raw.cube2,CFG['second_goals'][raw.goal_name],'cube2')
 if not bool(raw.evaluate()['success'].item()):raise RuntimeError('cube2 contact/displacement/goal postcondition failed')
