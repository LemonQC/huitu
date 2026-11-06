import os,sys,json,time,traceback,hashlib,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/T2_reuse_one_shot'
os.environ.pop('DISPLAY',None);os.environ.pop('WAYLAND_DISPLAY',None)
os.environ.update(MS_ASSET_DIR=str(ROOT/'skill_composition/assets'),MS_SKIP_ASSET_DOWNLOAD_PROMPT='1',XDG_CACHE_HOME=str(ROOT/'skill_composition/cache'))
import numpy as np,torch,gymnasium as gym
from .env import CFG
from .audit import PhysicalAudit,serial
from .legacy_v2 import seed_planners,SafeV2Planner,vec
from .controller import solve_geo
from mani_skill.utils.wrappers.record import RecordEpisode

def digest(state,physical_only=False):
 if physical_only:state={k:state[k] for k in ['actors','articulations'] if k in state}
 return hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()

class ReuseAudit(PhysicalAudit):
 def __init__(self,env):
  super().__init__(env,max_steps=1200);self.data=[];self.last_obs=None
 def reset(self,**kw):
  if self.resets:raise AssertionError('only one explicit reset allowed')
  result=super().reset(**kw);self.last_obs=serial(result[0]);return result
 def step(self,action):
  before=self.last_obs;phase=int(self.unwrapped.stage_id.item());result=super().step(action)
  self.data.append((before,serial(action),phase));self.last_obs=serial(result[0]);return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True);p.add_argument('--goal',choices=['A','B'],required=True);p.add_argument('--pose',choices=['P','Q'],required=True);p.add_argument('--batch',type=int,required=True);p.add_argument('--method',choices=['GEO-REPLAN','GC-BC'],default='GEO-REPLAN');p.add_argument('--run-id',required=True);a=p.parse_args()
 dest=OUT/'runs'/a.run_id;dest.mkdir(parents=True,exist_ok=False);started=time.monotonic();rng=seed_planners(a.seed)
 audit=None;env=None;planner=None;guards=[];events={};err='';close_error='';success=False;raw=None
 try:
  base=gym.make('Tool-Reuse-2-v0',num_envs=1,obs_mode='state',control_mode='pd_joint_pos',sim_backend='physx_cpu',goal_id=a.goal,reward_mode='sparse',max_episode_steps=1200,render_mode='rgb_array')
  audit=ReuseAudit(base);env=RecordEpisode(audit,output_dir=str(dest),save_video=True,save_trajectory=True,trajectory_name='physical',save_on_reset=True,source_type='motionplanning' if a.method=='GEO-REPLAN' else 'policy',source_desc='Bounded Tool-Reuse-2 dual-operation task')
  env.reset(seed=a.seed);raw=env.unwrapped
  for attr in ['set_pose','set_qpos','set_qvel']:
   guards.append((raw.agent.robot,attr,getattr(raw.agent.robot,attr)))
   def forbidden(*args,**kw):raise AssertionError('robot teleport prohibited')
   setattr(raw.agent.robot,attr,forbidden)
  if a.method=='GEO-REPLAN':
   planner=SafeV2Planner(env);solve_geo(env,planner,a.pose,events)
  else:
   from .state_bc import rollout_bc
   rollout_bc(env,audit,OUT/'models/gc_bc.pt')
  success=bool(raw.evaluate()['success'].item())
 except Exception:err=traceback.format_exc();(dest/'error.txt').write_text(err)
 finally:
  row={'run_id':a.run_id,'batch':a.batch,'method':a.method,'seed':a.seed,'goal':a.goal,'pose':a.pose,'success':bool(success),'steps':len(audit.trace) if audit else 0,'reset_count':audit.resets if audit else 0,'initial_state_sha256':digest(audit.initial,True) if audit and audit.initial else '', 'full_initial_state_sha256':digest(audit.initial) if audit and audit.initial else '', 'prefix_hash':digest(events['prefix_state'],True) if 'prefix_state' in events else '', 'intermediate_legal':events.get('intermediate_stage',0)>=3,'second_regrasp_success':events.get('regrasp_stage',0)>=4,'cube1_dx':None,'cube2_dx':None,'second_contact':False,'goal2_error':None,'stage':int(raw.stage_id.item()) if raw and raw.stage_id is not None else 0,'planner_calls':len(planner.calls) if planner else 0,'seconds':time.monotonic()-started,'error':err,'close_error':'','trajectory_path':f'runs/{a.run_id}/physical_trace.json','video_path':'','control_mode':'pd_joint_pos','observation':'goal-conditioned state','planner_seed':a.seed}
  if raw and audit and audit.initial:
   info=raw.evaluate();row.update(cube1_dx=float(info['cube1_dx'].item()),cube2_dx=float(info['cube2_dx'].item()),second_contact=bool(info['contact2'].item()),goal2_error=float(info['goal2_error'].item()))
  try:
   if audit:
    assert row['steps']<=1200 and row['reset_count']<=1
    payload={'initial':audit.initial,'initial_state_sha256':row['initial_state_sha256'],'events':events,'trace':audit.trace,'row':row,'rng':rng,'planner_calls':planner.calls if planner else []}
    (dest/'physical_trace.json').write_text(json.dumps(payload,default=lambda x:x.item() if isinstance(x,np.generic) else serial(x)))
    if audit.data:
     np.savez_compressed(dest/'bc_transitions.npz',obs=np.asarray([d[0] for d in audit.data],dtype=np.float32).reshape(len(audit.data),-1),actions=np.asarray([d[1] for d in audit.data],dtype=np.float32).reshape(len(audit.data),-1),phase=np.asarray([d[2] for d in audit.data]),seed=np.array(a.seed),success=np.array(success))
  finally:
   for robot,attr,fun in guards:setattr(robot,attr,fun)
   if planner:planner.close()
   if env:
    try:env.close()
    except Exception:close_error=traceback.format_exc()
  row['close_error']=close_error
  if (dest/'0.mp4').exists():row['video_path']=f'runs/{a.run_id}/0.mp4'
  (dest/'result.json').write_text(json.dumps(row,indent=2))
  print(json.dumps({k:row[k] for k in ['run_id','success','steps','stage','cube1_dx','cube2_dx','second_regrasp_success']}))
if __name__=='__main__':main()
