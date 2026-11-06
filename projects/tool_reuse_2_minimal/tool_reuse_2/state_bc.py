"""Goal-conditioned state BC, pd_joint_pos labels and execution throughout.
Small demonstration feasibility baseline, not diffusion/ACT or a novel method.
"""
import json,time,random
from pathlib import Path
import numpy as np,torch
from torch import nn
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/T2_reuse_one_shot'
class Policy(nn.Module):
 def __init__(self,obs_dim,act_dim):
  super().__init__();self.net=nn.Sequential(nn.Linear(obs_dim,256),nn.ReLU(),nn.Linear(256,256),nn.ReLU(),nn.Linear(256,act_dim))
 def forward(self,x):return self.net(x)

def train_bc():
 seed=17;random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
 paths=[]
 for p in sorted((OUT/'runs').glob('b1_GEO-REPLAN_*/bc_transitions.npz')):
  d=np.load(p)
  if bool(d['success']):paths.append((p,d))
 seeds=sorted({int(d['seed']) for p,d in paths})
 if len(seeds)<2:raise RuntimeError('Need independent train/validation initial states; no frame leakage')
 train_seed=seeds[0];train=[d for p,d in paths if int(d['seed'])==train_seed];val=[d for p,d in paths if int(d['seed'])!=train_seed]
 x=np.concatenate([d['obs'] for d in train]);y=np.concatenate([d['actions'] for d in train]);vx=np.concatenate([d['obs'] for d in val]);vy=np.concatenate([d['actions'] for d in val]);phase=np.concatenate([d['phase'] for d in train])
 device=torch.device('cuda' if torch.cuda.is_available() else 'cpu');start=time.monotonic();model=Policy(x.shape[1],y.shape[1]).to(device)
 mean=x.mean(0);std=np.maximum(x.std(0),1e-4);am=y.mean(0);astd=np.maximum(y.std(0),1e-3)
 tx=torch.tensor((x-mean)/std,device=device);ty=torch.tensor((y-am)/astd,device=device);tvx=torch.tensor((vx-mean)/std,device=device);tvy=torch.tensor((vy-am)/astd,device=device)
 optimizer=torch.optim.Adam(model.parameters(),lr=3e-4);best=float('inf');stall=0;history=[];dest=OUT/'models';dest.mkdir(exist_ok=True)
 for epoch in range(300):
  model.train();indices=torch.randperm(len(tx),device=device)
  for idx in indices.split(256):
   loss=(model(tx[idx])-ty[idx]).square().mean();optimizer.zero_grad(set_to_none=True);loss.backward();optimizer.step()
  model.eval()
  with torch.no_grad():vl=float((model(tvx)-tvy).square().mean().item())
  history.append({'epoch':epoch+1,'validation_normalized_mse':vl})
  if vl<best:
   best=vl;stall=0;torch.save({'model':model.state_dict(),'obs_dim':x.shape[1],'act_dim':y.shape[1],'obs_mean':torch.tensor(mean),'obs_std':torch.tensor(std),'act_mean':torch.tensor(am),'act_std':torch.tensor(astd),'seed':seed,'control_mode':'pd_joint_pos'},dest/'gc_bc.pt')
  else:stall+=1
  if stall>=40:break
 phase_to_skill={0:'GRASP',1:'PULL',2:'PLACE_RELEASE',3:'GRASP',4:'PULL',5:'COMPLETE'}
 def counts(ds):
  r={}
  for d in ds:
   for s in set(phase_to_skill.values()):
    if any(np.any(d['phase']==p) for p,k in phase_to_skill.items() if k==s):r[s]=r.get(s,0)+sum(np.any(d['phase']==p) for p,k in phase_to_skill.items() if k==s)
  return {k:int(v) for k,v in r.items()}
 tc,vc=counts(train),counts(val);assert all(v<=64 for v in tc.values()) and all(v<=16 for v in vc.values())
 card={'status':'TRAINED_VALIDATION_ONLY_PENDING_PHYSICS_GATE','seed':seed,'train_initial_states':[train_seed],'validation_initial_states':seeds[1:],'full_chain_train_demos':len(train),'full_chain_validation_demos':len(val),'atomic_train_segments':tc,'atomic_validation_segments':vc,'train_steps':len(x),'validation_steps':len(vx),'control_mode':'pd_joint_pos','observations':'same native flattened state + cube2 pose + public future goal + phase','privileged_contact_difference':'GEO also uses exact grasp/contact checks; no claim of equal low-level contact-feature inputs','epochs':len(history),'seconds':time.monotonic()-start,'training_gpu_hours':(time.monotonic()-start)/3600 if device.type=='cuda' else 0,'validation_normalized_action_mse':best,'history':history,'warning':'Tiny R1 full-chain dataset; validation action loss is not physical task success.'}
 (OUT/'bc_training.json').write_text(json.dumps(card,indent=2));print(json.dumps({k:card[k] for k in ['status','train_steps','validation_steps','epochs','validation_normalized_action_mse']}))

def rollout_bc(env,audit,checkpoint):
 pack=torch.load(checkpoint,map_location='cpu',weights_only=True);assert pack['control_mode']=='pd_joint_pos'
 model=Policy(pack['obs_dim'],pack['act_dim']);model.load_state_dict(pack['model']);model.eval()
 for _ in range(1200):
  obs=torch.tensor(audit.last_obs,dtype=torch.float32).reshape(1,-1)
  with torch.no_grad():action=(model((obs-pack['obs_mean'])/pack['obs_std'])*pack['act_std']+pack['act_mean']).numpy().reshape(-1)
  action[-1]=np.clip(action[-1],-1,1)
  env.step(action)
  if bool(env.unwrapped.evaluate()['success'].item()):return
 raise TimeoutError('BC physical control budget exhausted')
if __name__=='__main__':train_bc()
