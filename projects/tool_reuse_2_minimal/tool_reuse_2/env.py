import json
from pathlib import Path
import torch
from mani_skill.envs.tasks.tabletop.pull_cube_tool import PullCubeToolEnv
from mani_skill.utils.building import actors
from mani_skill.utils.structs.pose import Pose
from mani_skill.utils.registration import register_env
CFG=json.loads(Path(__file__).with_name('task_config.json').read_text())

@register_env('Tool-Reuse-2-v0',max_episode_steps=1200)
class ToolReuse2Env(PullCubeToolEnv):
 def __init__(self,*args,goal_id='A',**kwargs):
  self.goal_name=goal_id;self.stage_id=None;self._advance=False
  super().__init__(*args,**kwargs)
 def _load_scene(self,options):
  super()._load_scene(options)
  self.cube2=actors.build_cube(self.scene,half_size=self.cube_half_size,color=[.9,.7,.1,1],name='cube2',body_type='dynamic')
 def _initialize_episode(self,env_idx,options):
  super()._initialize_episode(env_idx,options)
  n=len(env_idx)
  with torch.device(self.device):
   xyz=torch.tensor(CFG['cube2_center']).repeat(n,1);xyz[:,:2]+=(torch.rand((n,2))-.5)*CFG['cube2_xy_jitter_fullwidth']
   self.cube2.set_pose(Pose.create_from_pq(p=xyz))
   if self.stage_id is None:
    self.stage_id=torch.zeros(self.num_envs,dtype=torch.long,device=self.device)
    self.contact1=torch.zeros(self.num_envs,dtype=torch.bool,device=self.device);self.contact2=self.contact1.clone()
    self.initial1=torch.zeros((self.num_envs,3),device=self.device);self.initial2=self.initial1.clone()
   self.stage_id[env_idx]=0;self.contact1[env_idx]=False;self.contact2[env_idx]=False
   self.initial1[env_idx]=self.cube.pose.p[env_idx].clone();self.initial2[env_idx]=self.cube2.pose.p[env_idx].clone()
 def step(self,action):
  self._advance=True
  try:return super().step(action)
  finally:self._advance=False
 def evaluate(self):
  if self.stage_id is None:
   z=torch.zeros(self.num_envs,dtype=torch.bool,device=self.device)
   return {'success':z,'stage_id':torch.zeros(self.num_envs,dtype=torch.long,device=self.device)}
  grasped=self.agent.is_grasping(self.l_shape_tool);z=self.l_shape_tool.pose.p[:,2]
  dx1=self.initial1[:,0]-self.cube.pose.p[:,0];dx2=self.initial2[:,0]-self.cube2.pose.p[:,0]
  target=torch.tensor(CFG['second_goals'][self.goal_name],device=self.device)
  error=torch.linalg.norm(self.cube2.pose.p[:,:2]-target,dim=-1)
  if self._advance:
   c1=torch.linalg.norm(self.scene.get_pairwise_contact_forces(self.l_shape_tool,self.cube),dim=-1)>1e-5
   c2=torch.linalg.norm(self.scene.get_pairwise_contact_forces(self.l_shape_tool,self.cube2),dim=-1)>1e-5
   self.contact1|=c1;self.contact2|=c2
   old=self.stage_id.clone();static=self.l_shape_tool.is_static(lin_thresh=.01,ang_thresh=.5)
   stage1=(old==0)&grasped&(z>.10)
   stage2=(old==1)&self.contact1&(dx1>=.20)
   stage3=(old==2)&(~grasped)&static&(torch.abs(z-self.height/2)<.015)
   stage4=(old==3)&grasped&(z>.10)
   stage5=(old==4)&self.contact2&(dx2>=.20)&(error<.06)
   self.stage_id=old+stage1.long()+stage2.long()+stage3.long()+stage4.long()+stage5.long();self._advance=False
  success=(self.stage_id>=5)&(dx1>=.20)&(dx2>=.20)&(error<.06)
  return {'success':success,'stage_id':self.stage_id.clone(),'cube1_dx':dx1,'cube2_dx':dx2,'goal2_error':error,'contact1':self.contact1.clone(),'contact2':self.contact2.clone(),'tool_grasped':grasped}
 def _get_obs_extra(self,info):
  obs=super()._get_obs_extra(info)
  if self.obs_mode_struct.use_state:
   obs.update(cube2_pose=self.cube2.pose.raw_pose,second_goal=torch.tensor(CFG['second_goals'][self.goal_name],device=self.device).repeat(self.num_envs,1),stage_onehot=torch.nn.functional.one_hot(self.stage_id.clamp(0,5),6).float())
  return obs
 def get_state_dict(self):
  s=super().get_state_dict()
  if self.stage_id is not None:s.update(task_stage=self.stage_id.clone().unsqueeze(-1),task_goal=torch.tensor(CFG['second_goals'][self.goal_name],device=self.device).repeat(self.num_envs,1))
  return s
