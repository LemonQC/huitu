# Codex 执行说明 — Skill Composition 项目（只修改本目录）

优先级：**不可改动其他研究方向（尤其根目录 README 和 docs/UNIFIED_BENCHMARK_PROTOCOL.md）**。独立实验：`projects/skill_composition/`。

## 当前先做什么

M0 — 在 Linux GPU 服务器完成 smoke：安装 requirements；运行 `scripts/smoke.py`；官方 `StackCube-v1` motion planning 示范；输出版本及 seed、视频链接。验证官方演示数据的控制模式、obs 模式和 h5/JSON metadata。

M1 — 已提供 `src/skillcomp/oracle.py` 和 `scripts/collect_oracle.py` 初稿；先依据官方 Panda solver 核验/调通真实四阶段轨迹（注意 Oracle 使用 `pd_joint_pos`，学习统一用 `pd_ee_delta_pose`），再使用官方 StackCube 演示转成 `state + pd_ee_delta_pose`，再跑 `scripts/make_dataset.py`、`scripts/train_bc.py`、`scripts/eval_bc.py`。避免 action/obs controller 错配；train/val 按 episode 分组。记录不依赖视频的成功判据。当前示范包含单任务完整轨迹，不可当成独立技能组合数据。

M2 — **最重要**：实现 `HandoffRegraspStack-v0` 在同一个 Panda/SAPIEN scene 中不重置地完成 Pick→PlaceOnStaging→Regrasp→Stack。先给出能成功的 oracle/scripted policy 和真实视频，检验可行性；至少两个具有实际操作意义的合法路径；不得通过直接 set_pose 改善交接。实现 train/val/test split freeze，失败类别日志，以及原子技能单测覆盖组合入口状态。

M3 — 给每个原子技能训练 BC、BC-RNN、Diffusion Policy、ACT，并在**同一 Scene、相同 controller/obs 上**评估；对长程决策加入带可用未来信息的 Future Q+CEM，以及 correct-state replanning/geometry 参照。

M4 — P2 不要求一次性全部做完。优先 STAP，再 GSC，再 SPIN；逐篇重实现 Q/dynamics/planner 或分布/联合采样或 RRT/connector/蒸馏。建立论文公式到文件/测试的一一对应清单；必须原任务 sanity check + 对新场景的忠实重实现验证。不可用 MLP 分数冒充原论文。

M5 — 先整理 baseline failure report。**不开发新 IHCL，不写提议算法，除非 A–D 研究门槛得到数据支持。**

## 报告必须包含

每一项附 `git commit`, `pip freeze`, CUDA/PyTorch/ManiSkill 版本，命令及返回码；训练和测试 seed，完整 episode CSV，checkpoint metadata，失误视频，训练时间和搜索预算。把所有结果区分 VERIFIED、PARTIAL、FAILED、NOT_STARTED，不得伪造结果。

## 验收质量要求

- 运行环境仅 Linux NVIDIA；没有图形化桌面的服务端使用 headless，禁止强制 human render。
- 禁止 silent exception / dummy success / 基于 GT 状态的“普通观察策略”。
- 单技能和连续执行的 `reset` 调用次数必须区分；handoff 不 reset。
- 测试：同一个初始状态的相关配置不能被计为独立 reset，至少随机数记录。
- GitHub 只存源码、轻量实验摘要、日志与追溯指针，不提交模型权重、大 H5、视频。
- 先把 M0/M1/M2 发到独立 commit，再处理 P2 算法。任何 API 不兼容请根据该版本官方源码修复并记下，而不是编造运行结果。
- 评审拒绝条件：任务仅是简单双选一停放；物理上不可能成功；所有 baseline 饱和却宣称新机制必要；没有独立未见组合测试。

## 日志规则

每次由用户/助手/Codex 更新重要研究决策时，追加独立 Markdown 至 `docs/research_log/DATE_skill_composition*.md` 或本项目 `logs/`。该规则由对话或运行触发，**不是自动获取 ChatGPT 全部聊天内容**。公共仓库不得写密码、token、私人数据。