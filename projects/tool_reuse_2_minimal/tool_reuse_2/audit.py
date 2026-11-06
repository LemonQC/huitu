"""Instrumentation for real CPU-PhysX oracle rollouts, never changes physics."""
import gymnasium as gym
import numpy as np,torch,json,hashlib

def serial(x):
 if isinstance(x,dict):return {k:serial(v) for k,v in sorted(x.items())}
 if isinstance(x,(list,tuple)):return [serial(v) for v in x]
 if isinstance(x,torch.Tensor):return x.detach().cpu().numpy().tolist()
 if isinstance(x,np.ndarray):return x.tolist()
 return x

class PhysicalAudit(gym.Wrapper):
 def __init__(self,env,max_steps=400):
  super().__init__(env);self.max_steps=max_steps;self.resets=0;self.trace=[];self.initial=None;self.guards=[]
 def reset(self,**kw):
  # Undo guards only immediately before the episode's one permitted reset.
  for actor,fun in self.guards:actor.set_pose=fun
  self.guards=[];result=self.env.reset(**kw);self.resets+=1;self.trace=[]
  self.initial=serial(self.unwrapped.get_state_dict())
  for actor in self.unwrapped.scene.actors.values():
   fun=actor.set_pose
   def forbidden(*a,**k):raise AssertionError('actor.set_pose forbidden after reset')
   self.guards.append((actor,fun));actor.set_pose=forbidden
  return result
 def step(self,action):
  limit=self.max_steps
  if limit is not None and len(self.trace)>=limit:
   raise TimeoutError(f"Physical action budget exhausted: {limit}")
  result=self.env.step(action);raw=self.unwrapped
  contacts=[]
  for c in raw.scene.get_contacts():
   contacts.append({'bodies':[c.bodies[0].entity.name,c.bodies[1].entity.name],'points':[{'position':serial(p.position),'impulse':serial(p.impulse),'separation':float(p.separation)} for p in c.points]})
  self.trace.append({'step':len(self.trace),'action':serial(action),'state':serial(raw.get_state_dict()),'tcp_pose':serial(raw.agent.tcp.pose.raw_pose),'qpos':serial(raw.agent.robot.get_qpos()),'qvel':serial(raw.agent.robot.get_qvel()),'contacts':contacts,'info':serial(result[-1])})
  return result
 def digest(self):return hashlib.sha256(json.dumps(self.initial,sort_keys=True).encode()).hexdigest()
