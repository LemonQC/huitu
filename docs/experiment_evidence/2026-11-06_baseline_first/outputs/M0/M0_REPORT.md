# M0 — PASS (2026-11-06)

已读取全部五份执行文档及 trial_manifest.yaml。无上传、push、PR 或远程写入。仅从指定固定提交下载旧代码。

## 工程来源与环境
原路径 huitu-main/projects/skill_composition 不存在。输入 ZIP 仅含恢复脚本和 BOSS 辅助文件；恢复脚本实际取回 23 个原型文件到 `skill_composition/restored`。固定提交 cfbfab361848835124956b31abb7483364296992。逐文件清单及修复前 SHA256 见 code_inventory.csv。

按用户要求用 conda clone 创建独立环境 `/home/users/lemon/TRO/.conda/tro-baseline`，安装工程及 ManiSkill 3.0.1；没有直接使用旧环境当作已验收环境。版本与 CUDA 实算见 environment.json，锁定见 pip_freeze.txt / conda_environment.yml。缓存/资产均定向本工作目录；软件依赖安装到本目录 conda prefix。

## 实际检查
- RTX3090 24GB，535.230.02，PyTorch 2.4.1+cu121，CUDA 矩阵计算 PASS。
- 原始 pytest 2/2 PASS，但仅测试数据拆分，不证明物理。
- 原始两项 smoke 均 SIGSEGV(-11)：继承 SSH DISPLAY 并报 GLX。保留原失败日志；启动器清除 DISPLAY/WAYLAND_DISPLAY 后两项均 PASS，各 2 episodes。
- CPU PhysX 与 CUDA PhysX 均创建/重置/step/读取物理状态/RGB 渲染成功。同 seed 初态 SHA256 相同且 10 步全轨迹一致；不同 seed 哈希不同。各测试 seed 150000（重复确定性检查）和150001，共2独立初态，不能计作3。
- 官方 StackCube motionplanning：2/2成功，93与107步，原始 H5/JSON、完整视频在 official_stack/；仅为官方任务安装验证。
- 修复原型阶段自动机：evaluate 只读，只有 step 推进；get/set_state_dict 纳入 task_stage_id。修复前文件保存在 original_source/。新增物理接口回归检查后 pytest 3/3 PASS。修改后 CPU/GPU 确定性检查均重新 PASS。

## 限制与后续门槛
HandoffRegraspStack 尚未证明 oracle 可行；现有随机动作失败不构成科研证据。旧工程仅单一固定 staging marker、固定顺序，不具备未见合法组合拆分，不能充当唯一 T-RO 正式任务。原 Oracle pd_joint_pos 与学习 pd_ee_delta_pose 不同，M2 前须真实重放转换并校验，不能混用标签。尚无 STAP/GSC/SPIN 实现、训练和评测成绩。正式 T1/T2 均未验收。

M0 Gate PASS：目标机器 CPU/GPU 物理与 headless RGB 可运行、确定性初态检查通过。允许进入 M1 物理 Oracle 调试；不允许开始训练。

## 重放
从 /home/users/lemon/TRO 执行：
```
python skill_composition/scripts/run_logged.py verify_cpu_repeat .conda/tro-baseline/bin/python skill_composition/scripts/verify_env.py --backend physx_cpu
python skill_composition/scripts/run_logged.py verify_gpu_repeat .conda/tro-baseline/bin/python skill_composition/scripts/verify_env.py --backend physx_cuda
python skill_composition/scripts/run_logged.py pytest_repeat .conda/tro-baseline/bin/python -m pytest skill_composition/restored/tests -q
```
commands.log 含启动器命令、返回码、运行时间；恢复/conda/pip 安装单独保留完整日志。早期交互系统检查命令不在启动器台账中，此限制明确披露。
