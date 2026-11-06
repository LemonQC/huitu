# 本地阶段证据包

M0通过；M1未通过；M2–M4未运行。本包不是完成全部T-RO实验的证据。

先读 TRO_GO_NO_GO.md、../outputs/M0/M0_REPORT.md、../outputs/M1/M1_REPORT.md，再查 stage_statistics.md 和 per_episode_results.csv。

六份交付入口：TRO_GO_NO_GO.md、task_cards.md、baseline_implementation_ledger.csv、per_episode_results.csv、failure_interventions.csv（仅表头，因为M4未运行）、videos_index.md。failure_interventions_README.md解释空表。

所有路径均以skill_composition/为根。完整数据、未剪辑视频、异常堆栈在outputs/；源码在restored/和scripts/；参考官方源码在references/。原始失败与超预算数据没有删除。带INVALID状态的轨迹不可用于正式成功率。官方和早期smoke保留原生记录，未与审计试次重复混计。

环境在服务器当前目录../.conda/tro-baseline。ZIP不包含conda二进制环境和通用缓存，包含conda_environment.yml、pip_freeze.txt与源码校验，可重建。原始输入协议也另外保留在包内。没有任何远程上传。

raw_episode_index.csv逐一索引136个原始H5回合组：126个已完成审计行、早期原型3回合、官方StackCube2回合、官方工具3回合、2个被中断的活动回合（结果unknown）。中断的unknown不填造为成功/失败。
