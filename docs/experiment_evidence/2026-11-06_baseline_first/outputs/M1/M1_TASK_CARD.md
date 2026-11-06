# Candidate task cards — NOT FINALIZED

共同平台：ManiSkill3.0.1 / SAPIEN3.0.3 / Panda，CPU PhysX主pilot，20Hz控制/100Hz物理。GPU PhysX与CUDA仅M0实际验收；主pilot没有混用后端。Oracle为pd_joint_pos特权运动规划；旧BC控制器pd_ee_delta_pose尚未转换验证。无学习数据拆分、无未见组合测试、无视觉部署结论。

## T1 RegraspStackCandidate-v1
继承恢复的HandoffRegraspStack-v0：40mm方块，初始A中心(-0.14,-0.02)m附近XY各30mm范围；连续staging区域x∈[-0.02,0.08]、y∈[-0.18,-0.10]m；三个后继B目标中心(0.14,0.10)/(0.08,0.17)/(-0.04,0.16)m，XY有30mm全宽随机化。真实pick→place/release→regrasp→stack。部分配置第二次抓取轴旋转90度，但方块对称性意味着尚不能证明不同抓法有实质长期依赖。

24独立开发初态、三配置各8；23/24，单一失败未判定为无解。未改变原物理成功阈值。对象质量/摩擦继承安装版本StackCube默认值，并非预注册随机化轴；可从锁定源码核查。尚需显式导出物理材料与质量参数，独立终态可行性、多路径和后继反事实选择检验。

## T2 PullCubeTool-v1 + physical return
复用本地已安装ManiSkill3原生L形工具环境。工具形状、质量/摩擦和初始化按该版本源码默认值；保留原随机初态。真实抓取L形工具→接触拉方块→抬升/重新定位→放回释放。三个工具返回目标(-0.20,-0.18)/(-0.20,0.02)/(-0.05,-0.22)m。接触、位移、稳定和位置判据见M1_REPORT，最大600控制步。

v2三配置共24独立初态19/24；失败包括不发生有效工具接触、放回时工具压到方块、规划/空路径错误。v3尝试改变抓法和工具回放朝向，但未验收成功。不是Compose-by-Focus Tools Usage复现；只属于原生任务的适配工程候选，不能把单次使用+放回替代已验证的复杂工具重用任务。

## 与公开任务的核对
Compose-by-Focus官方README称基于ManiSkill2；实际下载固定提交66a3c810552648e8f420d094ed03664341c43671的Tools代码使用mani_skill、torch批量状态、GPUMemoryConfig等接口。不能只凭README判为纯MS2移植；源码与ManiSkill3接口的兼容性应实际核验。入口还有clip导入/类级模型加载、自定义reset_agent及旧运动规划utils路径，未在本环境运行。参考源码存references/compose_audit，禁止把它的原论文成绩并入本pilot。
