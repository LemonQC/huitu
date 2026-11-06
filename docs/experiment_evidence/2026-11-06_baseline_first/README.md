# Baseline First：M0通过、M1未通过的阶段证据

用户于本轮明确授权“证据可以直接推送到https://github.com/LemonQC/huitu”，覆盖此前仅本地保留证据的限制。本次只新增证据归档，不修改已有研究实现。

**本次实验没有完成M0–M4全流程。** M0通过；M1未通过；M2–M4未运行，训练GPU小时为0。原型Oracle19/20，T1开发批23/24，T2v2开发批19/24。不得用这些Oracle调试结果声称算法缺口或T-RO创新成立。

先读 [阶段判断](reports/TRO_GO_NO_GO.md)、[M0报告](outputs/M0/M0_REPORT.md)、[M1报告](outputs/M1/M1_REPORT.md)，再查[统计表](reports/stage_statistics.md)和[逐回合台账](reports/per_episode_results.csv)。126条完成审计记录对应70个唯一初态哈希；跨版本重复不能计为新增独立初态。预算违规、失败和中断已披露。

## 上传范围

上传：全部阶段报告、逐回合结果、原始回合索引、初态哈希、物理检查摘要、环境锁定、命令与失败日志、候选配置和完整数据SHA256清单。

未上传：研究源码、模型、视频、大体积物理轨迹/H5、第三方源码镜像、conda二进制环境。报告内的trajectory_path/video_path是服务器本地相对路径，不是此仓库内下载链接。部分历史报告中的“没有上传”描述的是实验结束时的事实；证据上传是之后获得用户授权的独立操作。

完整证据ZIP仍在服务器：`/home/users/lemon/TRO/TRO_BaselineFirst_M0_PASS_M1_FAILED_GATE_20261106.zip`，209157954字节。ZIP SHA256：`cb8ff6099e6b14c5e2d10ac33a627c0b404c5b6cfbb858f73102e1716251a08c`。本目录的CHECKSUMS.sha256针对完整本地证据包内容，不能当作GitHub已含全部原始文件的证明。

本目录新增的 `PUBLISHED_FILES_SHA256.json` 单独列明实际上传文件及校验哈希。两项清单范围不同。
