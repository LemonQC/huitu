# ManiSkill 官方数据准备与检查

第一步先查看脚本帮助和实际数据路径；下面是官方文档提供的命令结构，未声称本机已执行成功。

```bash
# 在项目虚拟环境中执行
python -m mani_skill.utils.download_demo StackCube-v1

# 查看已下载到哪个位置
find . "$HOME/.maniskill" -name trajectory.h5 -o -name 'trajectory*.json' 2>/dev/null | head -40

# 将 RAW 的 trajectory.h5 按目标动作接口、状态观测重放，得到新的 H5 + JSON。
python -m mani_skill.trajectory.replay_trajectory \
    --traj-path /ABS/PATH/TO/trajectory.h5 \
    -c pd_ee_delta_pose -o state --save-traj

# 确认新 H5 及同名 JSON 对应正确 controller 和 obs_mode 后，运行：
python scripts/make_dataset.py \
    --traj /ABS/PATH/TO/REPLAYED_TRAJECTORY.h5 \
    --out outputs/stackcube_state_bc.npz

python scripts/train_bc.py --data outputs/stackcube_state_bc.npz \
    --epochs 100 --seed 42 --checkpoint outputs/bc_best.pt

python scripts/eval_bc.py --checkpoint outputs/bc_best.pt \
    --episodes 50 --base-seed 500000 --out outputs/eval_bc.csv

pytest -q tests/
```

**严格要求**：

- 官方原始下载的 H5 常不含 obs，不能直接输入 `make_dataset.py`。
- 必须检查与 `pd_ee_delta_pose` 相同的控制器；仅改脚本名称不能完成控制转换。
- 环境抽象阶段顺序仅用于 sanity check，不是互相独立训练的技能策略。
- 用于最终论文的组合数据应由 Phase1 新环境真实收集，覆盖组合入口状态。
- GPU/CPU physics 的复现误差必须单独记录；官方示范无法自动保证 100% 回放。
- 来源：https://maniskill.readthedocs.io/en/latest/user_guide/datasets/replay.html
