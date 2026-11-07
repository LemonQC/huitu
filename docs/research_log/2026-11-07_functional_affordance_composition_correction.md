# 2026-11-07 修正决议：真正的 3D Functional Affordance 组合（NO LLM）

> **CORRECTION — 新的研究定义，不等于可投稿的成果。**
> 上一个 KeyedPartPickInsert-v0 方案已撤回：它实质是 grasp / IK / collision / insertion，不是 3D affordance 研究。不要把旧任务交给 Codex 开发。本文件是其替代说明。**没有启动新实验。**

## 1. 研究对象与定义

暂定方向：**3D Functional Affordance Composition and Evolution for Long-Horizon Robotic Manipulation**。

Affordance 不是单一可抓点或 6D grasp。对物体的功能部件/区域及技能，表示：
`(object_id, part_id, 3D region/mask, function_type, contact_direction, availability, action_precondition, state_change)`。
功能如 grasp / pull / press / hang / support / contain / open 等，依据物体和交互任务。

**核心假设**：先行技能实际接触、抓持、移动或遮挡某功能部件，改变后继技能所需 affordance 的可用性。算法要基于当前观察预测和更新**跨技能功能兼容性**，而不是只基于几何最短路径或固定的 affordance 标签来排序。

**关键反事实**：某一功能区域当下可操作，但选择其作为前序接触面会阻碍后续功能操作；更换后继任务时，最佳交互部件应改变。必须与允许正常重抓、重规划、几何搜索的强 baseline 比较。单个“杯柄抓取与挂杯”例子只是 sanity check，不能作为创新宣称。

**全程不调用 LLM/VLM API，不基于 LLM 生成任务或规划**。任务以固定的结构化目标/技能集合表示。现成数据的历史标注方式与算法运行方式区分，若要完全排除 LLM 派生标签，首批仅使用 3D AffordanceNet / GAPartNet 人工或任务定义的标注。

## 2. 现成真正的 affordance 数据/基准

- **3D AffordanceNet**：3D 点云、逐点功能类型（grasp、pour、pull、press 等）；作为初始功能区域学习与预测 benchmark，不是机器人长序列成功证据。项目 https://github.com/wliu88/3DAffordanceNet
- **GAPartNet / PartNet-Mobility**：物体功能部件、关节与可交互几何、可执行的关节物体；适用于门柄/抽屉/盖板等功能区域。项目 https://pku-epic.github.io/GAPartNet/
- **MOPS (2026)**：ManiSkill 3 + SAPIEN 的多模态功能区域标注和仿真资产；可复用运行环境与 RGB-D/part masks，代码 https://github.com/LiXiling/mops-repo 。注意其数据标注开发曾使用 LLM；不能说原始数据完全不涉及 LLM，**本研究推理/规划中不使用 LLM**。
- **AffordSim (NeurIPS 2026)**：50 个 affordance-aware 操作、含长序列，作为外部竞争性验证候选。它基于 Isaac Sim 且原流程含语言/MLLM，不应为短期 smoke 重新搭建 Isaac 或移植代码。项目 https://affordsim-platform.github.io/AffordSim.io/
- **O3Afford、Where2Act**：相邻工作与功能 grounding 的重要 baseline，不声称它们已完成技能组合 benchmark。

## 3. 锁定第一个功能驱动的操作族：可用功能部件冲突

结构化任务（非自造可达性陷阱）：`Open storage → Retrieve a handled object → Use a different functional region for final manipulation`。

实例：打开柜门/抽屉（pullable handle）→ 拿出带柄杯子（graspable body / handle）→ 以杯柄挂到架上（hangable handle + hookable rack）。前序抓法可能占用杯柄；必须检测功能部件被夹爪占用时，是否能直接完成挂放、是否需要换抓，以及经正常恢复后整体是否更优。

此实例仅作第一套具体测试，须同时具备：
1) 真实功能部件/点云区域标注，而非使用物体中心位姿代替；
2) 可见的 part masks、局部表面方向、占用/遮挡状态；出示前后 affordance 可用性叠加图；
3) 在正常控制与真实接触中验证功能操作；禁止瞬移、隐藏改成功标签；
4) 两个后续任务目标与两种合法前序功能区选择，反事实偏好由完整物理执行得出；
5) 允许常规重抓、完整 IK/碰撞/运动规划与有限预算 CEM，避免“禁用 baseline 能力”制造创新。

这不是现成 benchmark 的完整任务，不声称 MOPS/ManiSkill 已自带此长序列任务。需要评估资产可用性，再尽可能复用已有示范/控制器。物理 affordance 可用性的真值需交互结果支持，不能仅由语义标签推断。

## 4. 最低风险实验次序（避免重复一个月）

**Gate A（纯数据验证，先不写环境）**
- 从公开数据抽 5–10 个有 2 种以上真实功能部件的物体，展示点云、功能点/面 mask 和不同技能所需的部件关系。
- 训练或调用现成 3D-affordance predictor（可先 GT mask 作为上限），检查任务目标切换能否导致**不同功能区**决策。
- 对比 Part-only、6D-only、GT Affordance、Predicted Affordance，确认 affordance 信息并非与位姿等价。

**Gate B（单一功能长序列，不上新网络）**
- 选择上面的 storage / handled-object / hang 示例的可执行资产，先逐技能验收并可见化真正的功能区。
- 对相同状态、合法 A/B 后继任务和 P/Q 前序接触区域比较：
  (a) Myopic stable grasp;
  (b) static task-affordance + TAMP;
  (c) feedback TAMP + normal regrasp;
  (d) matched-budget physical rollout/CEM;
  (e) GT functional-mask oracle upper bound。
- 测试仅从 affordance masks 和当前状态作推理，不泄露仿真未来真值。

**Gate C（符合 A/B 才学习）**
- 学习基于点云/部件功能区的动态 availability 或 compatibility predictor；对比静态 affordance、state-only、same-budget rollout；需要 held-out objects 与复合任务测试。
- 核心不是热力图 mIoU，而是 functional-region choice、unseen combination success、unnecessary regrasp、recovery cost、planner calls。

### NO-GO

- 如果功能部件不能得到可信可见的 3D 标注，**停止，先修数据基础**。
- 如果正常重抓 + TAMP + rollout 解决同样的长序列任务，**本任务不足以证明新方法的算法必要性**，不得调低 baseline 或收紧成功规则。
- 如 6D+几何规划达到相同结果，静态/dynamic affordance 模型也无效，停止这一论文假设。
- 任何一个单示例都不构成 T-RO 完整验证。以后需跨物体类别、交互机制及真机验证。所有真实运行的模型须说明官方/改写身份，不造性能数字。

## 5. 下一步给 Codex 的唯一动作

**禁止执行旧 `KeyedPartPickInsert-v0` 和 320-episode 计划。**
本次只做 **affordance data feasibility audit**，不训练新规划器：
1. 核查 3D AffordanceNet、GAPartNet、MOPS 的资产可下载和协议兼容性；
2. 选 5–10 个拥有不同功能区域/交互部件的真实 3D 资产，渲染 RGB-D、点云及逐点功能区域 mask；
3. 输出 `asset_manifest.csv`、`affordance_masks/`、功能部件示意、各类可用动作映射、`AFFORDANCE_DATA_GATE.md`；
4. 只在数据可用后准备功能操作单技能验证，不新增特殊 toy 插入任务，也不替换已有研究线。

**当前状态：PLAN_ONLY；无新实验，无新论文贡献已验证。**
