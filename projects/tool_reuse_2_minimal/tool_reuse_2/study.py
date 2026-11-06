"""Strict reservation-before-launch physical trial budget. No implicit retries."""
import csv,json,os,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/T2_reuse_one_shot';PY=ROOT/'.conda/tro-baseline/bin/python'

def read_rows():
 return list(csv.DictReader((OUT/'episodes.csv').open())) if (OUT/'episodes.csv').exists() else []

def run_batch(batch,items,method='GEO-REPLAN'):
 ledger=OUT/'attempts.json';attempts=json.loads(ledger.read_text()) if ledger.exists() else []
 assert len(attempts)+len(items)<=16,'16 complete physical trials cap reached'
 for seed,goal,pose in items:
  rid=f'b{batch}_{method}_{seed}_{goal}_{pose}'
  assert not any(x['run_id']==rid for x in attempts),'no duplicate attempts'
  attempt={'attempt':len(attempts)+1,'run_id':rid,'batch':batch,'seed':seed,'goal':goal,'pose':pose,'method':method,'status':'RESERVED'};attempts.append(attempt);ledger.write_text(json.dumps(attempts,indent=2))
  env=os.environ.copy();env.pop('DISPLAY',None);env.pop('WAYLAND_DISPLAY',None);env['PYTHONHASHSEED']=str(seed)
  cmd=[str(PY),'-m','tool_reuse_2.run_episode','--seed',str(seed),'--goal',goal,'--pose',pose,'--batch',str(batch),'--method',method,'--run-id',rid]
  with (OUT/(rid+'.log')).open('w') as log:
   try:code=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=150).returncode
   except subprocess.TimeoutExpired:code='WALLTIME_TIMEOUT'
  attempt['status']=str(code);ledger.write_text(json.dumps(attempts,indent=2))
  path=OUT/'runs'/rid/'result.json'
  if path.exists():row=json.loads(path.read_text())
  else:row={'run_id':rid,'batch':batch,'method':method,'seed':seed,'goal':goal,'pose':pose,'success':False,'error':f'process failed, returncode={code}; see {rid}.log','steps':'UNKNOWN','initial_state_sha256':'','intermediate_legal':False,'second_regrasp_success':False,'video_path':''}
  rows=read_rows();rows.append(row)
  # Keep the first two actual success and first two failure videos, all state
  # traces retained. This follows the explicit 2+2 clip cap, no hand selection.
  for outcome in ['True','False']:
   matches=[x for x in rows if str(x['success'])==outcome and x.get('video_path')]
   for x in matches[2:]:
    (OUT/x['video_path']).unlink(missing_ok=True);x['video_path']=''
    x['video_note']='not retained: first-two-per-outcome video cap; full state trace retained'
  fields=list(dict.fromkeys(k for r in rows for k in r))
  with (OUT/'episodes.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
  print(rid,'PASS' if str(row['success'])=='True' else 'FAIL',row.get('steps'),flush=True)
  if batch==2 and str(row.get('intermediate_legal'))!='True' and int(row.get('stage',0) or 0)>=2:
   (OUT/'counterfactual_stop.json').write_text(json.dumps({'decision':'NO_NOVEL_GAP','reason':'intermediate scheme failed common first-task legality; cannot claim a counterfactual second-task gap','run_id':rid},indent=2))
   break

def main():
 batch=int(sys.argv[1]);rows=read_rows()
 if batch==1:
  assert not rows
  files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'tool_reuse_2').glob('*') if p.is_file()}
  (OUT/'implementation_frozen_v1.json').write_text(json.dumps(files,indent=2))
  run_batch(1,[(s,g,'P') for s in [310000,310001] for g in ['A','B']])
 elif batch==2:
  assert len(rows)==4
  if not any(r['success']=='True' for r in rows):raise RuntimeError('STOP_TASK: 0/4, no batch2')
  run_batch(2,[(s,g,p) for s in [310002,310003] for g in ['A','B'] for p in ['P','Q']])
 else:raise ValueError('Only pre-registered batches 1/2; batch3 needs gate assessment')
if __name__=='__main__':main()
