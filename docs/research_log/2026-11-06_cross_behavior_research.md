# 研究对话阶段归档 — 2026-11-06

> 来源：**仅此聊天链接**截至本次消息的讨论与用户提供的终端结果。这里整理研究内容、已运行结果、代码/环境问题、决策及待完成工作；不粘贴长段源代码。为研究记录的结构化复述，并非 ChatGPT 会话逐字导出。

## 1. 对标论文及初始问题

**Cross-Behavior Learning With Object Flow Prediction for Robotic Manipulation（IEEE T-RO）**：强调不同人类/机器人操作行为可以通过任务相关物体运动形成共享监督。方法利用物体区域随时间变化的 Object Flow 预测，并用 flow-conditioned policy 产生机器人动作。

讨论要点：
- 作者主要依赖自己采集的小规模人类与机器人示范，主要五个任务，其中四个围绕推动目标物体，第五个是擦除；无需全量大型公开数据集。
- 论文的价值在明确的跨行为问题、任务表示、真实机器人验证和实验闭环，而不是新发明大规模网络。
- 局限：任务多样性不足，复杂长序列成功率仍低；方法和已有点流、物体运动表征工作存在关联。
- 用户要求寻找**更新、更有创新、单卡4090可复现且能自然产出精致论文科学图**的课题。

## 2. 研究方向的迭代

### 2.1 已否决：未知动力学下的主动效果验证

构想：不同物理摩擦/质量/阻力下主动探测与在线适应。用户指出真机人为模拟这些变化非常不自然，且容易沦为专门给新方法设计的仿真场景。

**决议：撤回此方案**，不再把随机改变摩擦等作为核心研究创新。

### 2.2 当前候选：Learning Task-Equivalent Behaviors Across Embodiments

核心设想：相同目标可以通过不同操作路径达到。跨本体迁移应学习任务过程中**不可违反的约束**与**可以改变的行为自由度**，并用此条件生成目标机器人自己的动作，而不是要求执行源示范的物体轨迹。

两个拟议模块（待验证）：
1. Process-Constrained Task Equivalence Learning：对多种成功行为形成任务等价表示，并与视觉相似但违反任务约束的近失败行为区分。
2. Equivalence-Conditioned Policy Learning：将任务等价表示用于动作生成，允许与源示范路径不同而任务结果一致。

**核心风险**：CORE 已关注共同任务结果，Human2Any 涉及可执行性，Cross-Behavior Object Flow 和 Im2Flow2Act 也共享物体运动信息。必须用统一实验说明为何“过程约束下的等价行为”比共同终态、普通目标条件策略或流预测多了真正必要的机制。现在不能声称创新已成立。

## 3. 用户明确约束

- 单卡 RTX 4090（24GB）；
- 下载数据必须可控、最好放当前项目目录，避免 `~/.maniskill` 空间不足；
- 无 VPN，Hugging Face 官方连接受阻，但 `hf-mirror.com` 下载已成功；
- 优先同一个 Conda 环境/同一仿真环境；论文方法可重新实现，但必须如实记录是否忠实；
- 不用大量人工采集或 TB 级数据；
- 真机条件应自然、可复现；
- 实验应产生轨迹叠加、任务表征分布、物体运动时序、动作采样多样性、跨本体迁移视频、失败诊断等真实科学图，而不是装饰性框架图；
- **此聊天每次更新研究进展，都保存 Markdown 到 `LemonQC/huitu`**，不使用其他对话记忆。

## 4. 数据和环境现状

- 使用 ManiSkill 3，任务为 PickCube-v1；100条机器人示范用于训练。
- 官方 Motion Planning 数据已由 HF 镜像成功下载，原始 HDF5 metadata 记录1000 episodes，重放其中100条，并转换到 `state + pd_ee_delta_pos + physx_cpu`。
- 初始下载脚本的 `--num-procs` 不兼容，已删除；SSH 的 `DISPLAY=localhost:12.0` 导致 GLX 段错误，关闭 DISPLAY 后可运行。
- Gymnasium 1.4.0 和 ManiSkill 官方 DP/ACT 评估代码不兼容：曾缺 `final_info`，之后 `numpy.ndarray` 不支持 `.float()`；已针对 same-step autoreset 和 `torch.as_tensor` 做补丁，训练评估可启动。
- 物理仿真 `physx_cpu` 不代表策略 PyTorch 训练一定在CPU；使用CUDA与否需查看模型实际 device。
- 不建议下载完整 RoboTwin（官方原始版本体积 TB 级），ManiSkill 小数据优先。

## 5. 已有实验结果（不能当正式 T-RO 统计）

### 5.1 Pilot

PickCube-v1、100示范、seed=42，测试20 episodes：

| Method | Success Once | Success at End | 身份 |
|---|---:|---:|---|
| BC | 5% | 0% | 本项目自实现 pilot |
| Chunked BC | 5% | 0% | 本项目自实现 pilot |
| Tiny DDPM | 0% | 0% | 本项目自实现 pilot |

这些模型未与官方 ACT/DP 统一完全匹配训练和评测条件。

### 5.2 官方 ManiSkill DP / ACT

100条示范，seed 42，每次评估20 episodes：

| 方法 | 最后TensorBoard记录位置 | 最后Success Once | 最后Success at End | 全程最佳 Success Once | 全程最佳 Success at End |
|---|---:|---:|---:|---:|---:|
| DP | iter 30000 | **100%** | **70%** | 100% | 100% |
| ACT | iter 29000 | **30%** | **0%** | 65% | 25% |

注意：最佳 Once 与最佳 End 可能不是同一 checkpoint；_success_once 等带下划线指标不是成功率；尚需独立测试和多个种子。PickCube-v1 对 DP 可能出现天花板效应，无法仅靠提升标准成功率验证新课题。

### 5.3 扩展简化模型

新编写的 BC-GMM、BC-RNN、BC-Transformer：2 epoch、2 episode 冒烟测试三个均0% success，**只说明运行流程可用，不代表算法性能**。后续正在尝试更长训练，但尚无在本对话中证实的新结果。明确禁止将简化版直接称为 RoboMimic 官方方法。

## 6. Baseline 体系与代码迭代

### 标准模仿学习

- 官方：ManiSkill Diffusion Policy、ACT（已训练）。
- 已实现原型：BC、Chunked BC、Tiny DDPM、简化 BC-GMM/BC-RNN/BC-Transformer。
- RoboMimic 官方配置适配包已提供，但**未在用户服务器完成端到端核验**：BC、BC-GMM、BC-RNN、BC-RNN-GMM、BC-Transformer、BC-Transformer-GMM。
- 未来候选：VQ-BeT、Flow Matching Policy（需先选择具体论文官方实现并核查）。

### 跨本体/跨行为论文方法

| 方法 | 本对话中已确认情况 | 下一动作 |
|---|---|---|
| Im2Flow2Act | GitHub官方源码已获取，训练/评估入口真实存在于 `scripts/controll/`（注意作者拼写）；尚未运行模型 | 使用统一仿真协议重实现/适配，原生预训练可作自检 |
| XSkill | 官方代码获取；Kitchen 跨本体流程入口存在 | 明确技能原型/标签/迁移机制并适配相同目标 |
| UniSkill | 部分代码公开，策略/权重可能缺失 | 核验后选择标注为 adapted/reimpl 或延期 |
| CORE | 未核实可靠可运行官方仓库 | 根据论文严谨重实现，不能冒充官方 |
| Cross-Behavior Object Flow | 未核实可用官方仓库 | 根据论文严谨重实现并披露差异 |
| Human2Any / KITE | 文献相关，部分实施门槛高 | 评估是否可比后再决定 |

此前 v4 `cross_paper_audit.csv` 对 Im2Flow2Act 报 `ENTRY_NOT_VERIFIED`，后经用户 `find` 确认是代码路径写成 `control` 而实际为 `controll`，并非论文缺少入口。

## 7. Im2Flow2Act 配置与下载验证

用户提供的评估 YAML：
- `model_path=${DEV_PATH}/im2flow2act/checkpoints/manipulation_policy`, `ckpt=300`
- 数据：`simulation_evaluation/drawer_open`、`pickNplace`、`pouring`
- 相机标定路径位于 `data_local/simulation`
- 128个点，32帧，`filters: [mv]`。

用户提供的训练 YAML：
- `training.epochs=1001`、`batch_size=52`，动作维度7，Flow Encoder / Transformer / ConditionalUnet1D，DDIM 50训练timesteps、16推理steps。
- 数据来自 `simulated_play/rigid`、`articulated`、`deformable`，与 PickCube 状态HDF5不兼容。
- Stanford下载链接响应：`checkpoints.zip` 6,303,833,294 bytes；`simulation_evaluation.zip` 1,932,834,883 bytes，共约8.24 GB；**仅确认HEAD可访问，尚未确认实际下载**。

最新重要决策：**不再强制以各方法的作者原生仿真作为论文主实验**；统一迁移到我们自己的 ManiSkill 仿真协议。能忠实复现的论文机制优先；重实现必须清楚区分 OFFICIAL / FAITHFUL_REIMPL / ADAPTED / PROXY，不能编造性能。

## 8. 为什么不能简单混合几个标准任务

PickCube、PushCube、PushT 分属不同任务类型，不能简单合并成 Cross-Behavior 数据。统一跨行为任务必须具有：
- 同一任务目标与成功条件；
- 至少两种自然可执行的操作方式（如 push 与 pick-place）；
- 同一目标机器人动作/观察接口；
- 额外源端示范、失败近邻或过程约束标签；
- 被比较方法相同可用监督条件，或显式注明额外数据/预训练差异。

## 9. 后续执行清单

1. 使用 `LemonQC/huitu` 集中保存本项目文档、复现计划、运行记录，并持续更新本对话的 Markdown 日志；必要时后续另建 `src/`、`configs/`、`scripts/`。
2. 锁定统一 ManiSkill 任务、状态/RGB/物体轨迹输入、动作定义、评测seed和记录Schema；先做最小的 push-or-pick 同目标操作任务。
3. 在单卡4090下对 DP/ACT 与 RoboMimic 官方模型分别做可复现训练与独立评估。
4. 对 Im2Flow2Act、XSkill、Object Flow、CORE 按论文机制逐步做同环境重实现，不以拿到 GitHub 仓库替代跑通。
5. 基于对照结果决定核心研究创新是否值得做，尤其检验终态表示、过程约束、目标条件策略之间是否确有差距。
6. 论文最终图需要真实模型结果：跨行为轨迹、潜在表征、时序物体状态、失败因素、动作多模态、跨机器人操作视频及统计误差。

## 10. 尚未完成及关键风险

- 当前没有同任务、多操作方式的正式跨行为数据；**无法凭现有 PickCube 证明新方法的价值**。
- 很多论文 Baseline 尚无统一环境的可运行复现；不同输入模态导致公平性难题。
- “等价行为”可能与已有任务结果/约束表示方法重叠；必须先验证真正的新机制。
- 一张表堆砌十几个算法不代表 T-RO 创新；优先建立合理科学问题和可验证性能缺口。
- 本日志只更新在当前对话被触发时，不承诺自动后台录制对话或持续监控。
