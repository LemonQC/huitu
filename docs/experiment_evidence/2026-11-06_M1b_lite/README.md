# M1b-Lite 专家分析结果

**执行结束；唯一结论：DESIGN_T2_REUSE_NEXT。仅值得进一步定义工具再次使用任务，不进入M2训练。**

## 阅读顺序

1. [DECISION.md](DECISION.md)：阶段判断和限制。
2. [P0_ROOT_CAUSE.md](P0_ROOT_CAUSE.md)：指定五个原失败的根因证据，P0新仿真0次。
3. [P1_DECISION.md](P1_DECISION.md)、[P1_EPISODES.csv](P1_EPISODES.csv)、[P1_PATCH.diff](P1_PATCH.diff)：P1共12次，已到上限。首次补丁0/5，唯一二次修改后原失败修复4/5，成功回归2/2；最终补丁6/7仅为选定开发集，不是总体成功率估计。
4. [P2_TASK_DISCRIMINATION.md](P2_TASK_DISCRIMINATION.md)：P2仅静态检查，新仿真0次。T1没有非平凡后继依赖证据；X/Y不能同时满足同一固定marker判据。
5. [FINAL_AUDIT.json](FINAL_AUDIT.json)、[P1_ATTEMPTS.json](P1_ATTEMPTS.json)：实际次数/预算。最大453步，单回合600硬上限、一次reset，初态hash匹配旧结果。

## 可下载原始证据与重要限制

- 本目录包含全部12回合完整物理trace的无损gzip文件：`P1_runs/<version>_<seed>/physical_trace.json.gz`。解压后含逐步动作、关节/物体位姿、接触和初态，内容与服务器原JSON一致。台账中的`.json`路径在GitHub对应`.json.gz`。
- 8个实际保存的完整MP4视频一并上传。4个二次修改成功回合在完整状态轨迹保存后遇到numpy.bool_序列化异常，视频没有flush；结果由完整轨迹和未改判据离线恢复，台账明确标注，**这4个视频不存在，没有补拍或合成**。失败序列化文件与异常日志保留。
- 240014仍为拉动时抓取丢失；不能由规划失败断言物理无解，不能把工程改进当作T-RO组合创新。
- 未训练任何算法、未重装环境、未下载已有源码、未额外运行P2。P2中的再次使用任务仅定义，未实现。
- H5副本和Python实现仍留服务器；本次上传结果、补丁diff、全部逐步JSON轨迹及现有视频。当前目录不是完成M0–M4的证据。

## 上传授权与校验

用户在本轮明确要求“相应的结果需要上传的，专家需要读取分析”。此次授权覆盖M1b执行时只留本地的指令。原报告中的“未上传”字段描述的是运行完成时状态，保持历史原件不改；实际发布范围见本README和PUBLISHED_FILES_SHA256.json。根CHECKSUMS.sha256针对服务器原文件，PUBLISHED_FILES_SHA256.json针对实际发布文件（包含gzip后的字节哈希）。
