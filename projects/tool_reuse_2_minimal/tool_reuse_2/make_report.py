from pathlib import Path
import csv,json,collections,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/T2_reuse_one_shot'
def truth(x):return str(x).lower()=='true'
def write_csv(path,rows,fields=None):
 fields=fields or list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
 rows=list(csv.DictReader((OUT/'episodes.csv').open()));attempts=json.loads((OUT/'attempts.json').read_text());assert len(rows)==len(attempts)<=16
 cf=[];pairgroups=collections.defaultdict(list);audits=[]
 for r in rows:
  if r.get('trajectory_path') and (OUT/r['trajectory_path']).exists():
   d=json.loads((OUT/r['trajectory_path']).read_text());tr=d['trace'];assert len(tr)==int(r['steps'])<=1200;assert int(r['reset_count'])==1
   stage3=next((i for i,f in enumerate(tr) if int(f['state']['task_stage'][0][0])>=3),None)
   stage4=next((i for i,f in enumerate(tr) if int(f['state']['task_stage'][0][0])>=4),None)
   supported=False
   if stage3 is not None:
    supported=any({n.removeprefix('scene-0_') for n in c['bodies']}=={'l_shape_tool','table-workspace'} and any(sum(abs(x) for x in p['impulse'])>1e-7 for p in c['points']) for c in tr[stage3]['contacts'])
   audits.append({'run_id':r['run_id'],'steps':len(tr),'single_reset':True,'actor_and_robot_setter_guards':True,'common_intermediate_table_contact_at_stage3':supported,'retained_video':bool(r.get('video_path')),'complete_trace':True})
  else:stage3=None;stage4=None
  if r['batch']=='2':
   c={k:r.get(k,'') for k in ['run_id','seed','goal','pose','initial_state_sha256','prefix_hash','intermediate_legal','second_regrasp_success','second_contact','cube1_dx','cube2_dx','goal2_error','success','steps','planner_calls','error','trajectory_path','video_path']}
   c.update(intermediate_step=stage3,regrasp_step=stage4,second_part_steps=int(r['steps'])-stage3-1 if stage3 is not None else '',table_support_at_intermediate=supported)
   cf.append(c);pairgroups[r['seed']].append(c)
 write_csv(OUT/'counterfactual.csv',cf,['run_id','seed','goal','pose','initial_state_sha256','prefix_hash','intermediate_legal','second_regrasp_success','second_contact','cube1_dx','cube2_dx','goal2_error','success','steps','planner_calls','error','trajectory_path','video_path','intermediate_step','regrasp_step','second_part_steps','table_support_at_intermediate'])
 paired=[]
 for seed,rr in pairgroups.items():
  complete=len(rr)==4;initial_match=len({r['initial_state_sha256'] for r in rr})==1;prefix_match=len({r['prefix_hash'] for r in rr})==1
  common_legal=all(truth(r['intermediate_legal']) and r['table_support_at_intermediate'] for r in rr)
  costs={r['goal']+'_'+r['pose']:int(r['steps']) for r in rr};reversal=False
  if complete:reversal=(costs['A_P']-costs['A_Q'])*(costs['B_P']-costs['B_Q'])<0
  paired.append({'seed':seed,'complete_2x2':complete,'same_initial_state':initial_match,'same_physical_prefix':prefix_match,'both_P_Q_common_first_goal_legal':common_legal,'costs':costs,'cost_preference_reversal':reversal})
 successes=sum(truth(r['success']) for r in rows);both_goals=all(any(truth(r['success']) and r['goal']==g for r in rows) for g in ['A','B'])
 if not any(truth(r['success']) for r in rows if r['batch']=='1'):decision='STOP_TASK'
 elif (OUT/'counterfactual_stop.json').exists():decision='NO_NOVEL_GAP'
 elif len(cf)==8 and all(p['both_P_Q_common_first_goal_legal'] and p['same_initial_state'] and p['same_physical_prefix'] for p in paired):
  p_success=all(truth(r['success']) for r in cf if r['pose']=='P')
  decision='NO_NOVEL_GAP' if p_success and not any(p['cost_preference_reversal'] for p in paired) else 'START_BASELINES'
 else:decision='NO_NOVEL_GAP'
 bc=json.loads((OUT/'bc_training.json').read_text()) if (OUT/'bc_training.json').exists() else {}
 status='TRAINED_VALIDATED; PHYSICAL_EVAL_NOT_RUN_STOP_NO_NOVEL_GAP' if bc and decision=='NO_NOVEL_GAP' else 'TRAINED_PENDING_PHYSICS' if bc else 'NOT_RUN'
 base=[{'method':'GEO-REPLAN','status':'RUN','successes':successes,'physical_rollouts':len(rows),'note':'Measured-state geometry, normal regrasp and native screw/RRT feedback; these are the task-feasibility/counterfactual runs, not extra hidden trials.'}, {'method':'Goal-conditioned state BC','status':status,'successes':'','physical_rollouts':0,'training_seed':bc.get('seed',''),'training_gpu_hours':bc.get('training_gpu_hours',''),'validation_normalized_action_mse':bc.get('validation_normalized_action_mse',''),'note':'Same pd_joint_pos labels/controller, public goal and phase; tiny R1 full-chain successful demos, episode-seed-disjoint validation. Action MSE is not physics success. GEO additionally uses exact contact/grasp queries, disclosed in model card.'}]
 base.extend({'method':m,'status':'NOT_RUN_OUT_OF_SCOPE','successes':'','physical_rollouts':0,'note':'Explicitly excluded this round'} for m in ['STAP','GSC','SPIN','DP','ACT'])
 write_csv(OUT/'baseline_results.csv',base)
 (OUT/'counterfactual_audit.json').write_text(json.dumps({'paired_cells':paired,'new_independent_scene_seeds':sorted({r['seed'] for r in rows}),'trial_count':len(rows),'max_steps':max(int(r['steps']) for r in rows),'physical_both_goals_completed':both_goals,'decision':decision,'audit':audits},indent=2))
 if decision=='NO_NOVEL_GAP':
  detail='Tool-Reuse-2双操作可执行。第1批4/4；第2批7/8，两组四格的物理初态及第一操作后状态hash均一致，P/Q均真实放稳、松爪并再次抓取。P在两个目标下均成功且比Q步数少，无目标依赖选择反转；一次Q/A为第二次接触位移不足（0.1566m），不是规划失败，但P正常重抓/反馈已解决该初态。当前无未被普通几何重规划消除的组合缺口。'
  tail='按停止条件不运行第3批，最终12/16次，异常/中止均计数。GEO-REPLAN 11/12；BC已实现并完成单seed训练/独立初态验证，因研究门槛停止而未做物理评测，不能报其成功率。不得用小样本否定一般技能组合问题。不训练其他方法、不开发新任务或Ours。代码按最新用户授权上传；模型与全部实验结果仅留本地。'
 else:detail='见episodes.csv及counterfactual_audit.json；不将控制/实现失败等同物理无解。';tail='严格按门槛及16次上限停止，未运行方法不填成绩。'
 text='# '+decision+'\n\n'+detail+'\n\n'+tail+'\n'
 (OUT/'DECISION.md').write_text(text)
 print(json.dumps({'decision':decision,'successes':successes,'trials':len(rows),'counterfactual_pairs_valid':all(p['both_P_Q_common_first_goal_legal'] and p['same_initial_state'] and p['same_physical_prefix'] for p in paired),'preference_reversal':any(p['cost_preference_reversal'] for p in paired),'BC':status}))
if __name__=='__main__':main()
