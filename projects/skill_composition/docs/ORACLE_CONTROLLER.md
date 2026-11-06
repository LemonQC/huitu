# Oracle 与学习策略的动作控制模式不能混淆

ManiSkill 官方 `PandaArmMotionPlanningSolver`（StackCube source）明确校验 `pd_joint_pos` 或 `pd_joint_pos_vel`；项目第一阶段学习模型选 `pd_ee_delta_pose`。因此：

1. `scripts/collect_oracle.py` 必须使用 `pd_joint_pos` 采集可行性和演示轨迹；它是拥有 simulator ground truth 的**特权数据生成器**，不是与视觉策略同观察约束的可比强 baseline。
2. 同一套物理场景和目标任务不变；通过 ManiSkill 官方 `mani_skill.trajectory.replay_trajectory` 转换动作控制和观测到目标 `pd_ee_delta_pose + state`，然后验证成功率/重放物理误差。
3. 对正式 BC/DP/ACT/STAP/GSC/SPIN 等学习策略**统一部署目标控制接口**，如果某方法需要别的 action representation 则记录转换映射和误差，不得偷换试验动作权限。
4. 演示初态不能跨 train/val/test 泄漏；真实技能组合数据需要新环境和单技能分段采样。
5. Oracle 源码借鉴官方 StackCube motionplanning solver 的真实 grasp/pose 规划，**目前未在服务器成功执行，不能报告成功率**。

官方来源：https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/examples/motionplanning/panda/solutions/stack_cube.py

当前命令：
```bash
python scripts/collect_oracle.py --episodes 3 --seed 200000 --record-dir outputs/oracle --video
```
失败时保留堆栈、`oracle_report.json`、trajectory.h5、video，用于 Codex 修正策略可行性和 API。