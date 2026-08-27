# DeepTrans - 本轮已完成任务记录（2026-08-27）

# ============ 第二轮：国内机翻回落 AI + GitHub 发布准备（2026-08-27）============

## 已完成任务

### 国内机翻引擎探测与决策
- 实测国内免Key端点：百度 transapi errno 1022 反爬、basetrans 空响应、有道 aidemo errorCode 102 需签名、腾讯 405 —— 全线不可用
- 按用户授权实现 mech_ai_fallback：全部机翻引擎失败后自动用当前 AI 引擎兜底（默认开启，可在设置关闭）
- 修复黑洞网络下机翻永久悬挂：DNS 解析(getaddrinfo)不受 socket.setdefaulttimeout 约束（faulthandler 定位于 urllib3 create_connection），改为每引擎 12 秒看门狗守护线程硬限时；socket 兜底收紧至 8s
- 真机验证：受限网络下整链路 28.6s 收敛并经 AI 兜底返回正确译文（"你好，世界。"）

### 全量检修回归（第二轮）
- 全模块 py_compile OK；i18n 55 键双语零缺失；损坏配置存活；双模式冒烟 EXEC-CODE 0；悬浮窗微测 PASS；端到端 AI 管线 PASS

### GitHub 发布准备（用户决策：手动上传 + Public 仓库）
- 网络事实：本机到 api.github.com/github.com/pypi.org/google 全部超时，且本机无代理监听、WinHTTP 直连 —— 上传通道不可用；用户选择自行上传
- 脱敏核验：真实密钥仅存在于 config.json 与 backups/（全部排除在发布包外）；新增 config.example.json（密钥占位符为空串）、.gitignore（排除 config.json/Err.log/backups/updates/dist/build/__pycache__）、LICENSE(MIT/DeverAI)、README 密钥指引与许可证更新
- 构建发布资产：PyInstaller 首次构建因环境中 PyQt5 共存失败，build.py 增加 --exclude-module=PyQt5 后成功；dist/DeepTrans.exe 约 62MB
- 发布包就绪于 backups/github_release_20260827/：DeepTrans_src_v1.4.0.zip（25 文件，无 __pycache__）、DeepTrans-v1.4.0-win64.exe、RELEASE_NOTES.md、UPLOAD_GUIDE.md（网页与 git 双路线）
- 回答用户 VPN(GA/加速器) 与 Clash 订阅引导问题：订阅拉取属一次性引导需求，节点可直连时 Clash 可脱离加速器独立运行

## 第二轮遗留
- GitHub 实际上传与 Release 发布由用户按 UPLOAD_GUIDE.md 手动执行
- 用户提供过的 ghp_ token 已在会话中暴露，已在指南中建议立即撤销重建

# ============ 第一轮：完整更新验收（2026-08-27，已于目标完成时归档）============


## 轮次概述
本轮为"完整更新验收"：修复已知缺陷、落地自动存错机制、升级双 AI 引擎、真机验收、文档全量同步。执行环境 Miniforge Python 3.13.13。

## 已完成任务清单

### 阶段0：初始化与环境核查
- 文档单套制检查；README/Design/Fact/FreqErr/todo 全量读取
- Fact.md 记录用户偏好与本轮授权范围（密钥保持原样、默认小米、UI 可顺手升级）
- 定位 Miniforge Python（C:\Users\Administrator\miniforge3\python.exe），确认依赖缺口后安装 PyQt6/pynput/pyperclip/deep-translator/keyboard/pyautogui（清华镜像）

### 阶段1：核心升级
- core/config.py 重写性改造：集中路径解析 app_dir()/resource_dir()/icon_path()/default_config_path()；--config/--portable 导入期解析；AI_PROVIDERS 双引擎表；VALIDATORS 扩展 ai_provider/ai_model 动态校验；reset(keep_keys) 保留密钥
- core/translator.py：双 AI 引擎装配（deepseek 官方 / xiaomi token-plan mimo-v2.5 默认）；resolve_ai_model 错配回落；socket.setdefaulttimeout(20) 兜底悬挂
- config.json：新增 xiaomi_api_key 与 ai_provider，ai_model 改 mimo-v2.5；原 deepseek_api_key 逐字节保持原样（用户决定）
- gui/settings.py：新增引擎切换下拉（联动模型列表）、小米密钥输入框；硬编码文案全面国际化

### 阶段2：Err.log 自动存错机制
- 新增 utils/errlog.py（log_error/log_warning/log_exception）
- main.py 安装 sys.excepthook 全局钩子；core/errors.py、translator.py、config.py 关键失败路径全部落盘

### 阶段3：缺陷修复（问题1-9）
1. i18n 英文界面缺 text_color/bg_color 键导致渲染原始键名
2. MyMemory 语言码大小写敏感且无裸码（en-us/zh 不识别）→ 映射 zh-CN/en-US
3. 机械翻译无总超时导致 Worker 无限悬挂
4. 机翻 except 分支引用未导入 log_exception 的 NameError
5. 图标/配置相对路径在换目录与 PyInstaller 场景失效
6. 恢复默认设置误清空 API 密钥
7. build.py 残留 jieba hidden-import；styles.py 过期 STYLESHEET 常量
8. README/build_instructions 虚构承诺（build.spec/LICENSE/--参数）→ 全部对齐现实并兑现参数实现
9. dev_log 同日重复文件违规单套制 → 正本保留、副本移入 backups/dev_log_merged_20260827/

### 阶段4：验证与验收
- 全模块 py_compile 通过（多轮回归）
- offscreen 启动冒烟：--no-tray 与含托盘两条路径均 EXEC-CODE 0、监听器启动正常
- 小米 mimo-v2.5 真机调用 PASS；DeepSeek deepseek-chat 真机调用 PASS（同一英文输入均正确返回中文）
- 端到端集成测试 PASS：Qt 信号链 -> Worker -> 小米实调 -> 悬浮窗渲染（"Hello world..." 正确显示中文译文）
- 悬浮窗错误路径微测 PASS：机翻失败时告警按钮承接展示；正常文本分支恢复显示
- --config 重定向 PASS：导入期解析，CONFIG_FILE 正确指向外部路径
- reset(keep_keys) 语义 PASS：磁盘核验双密钥在恢复默认后原样保留
- 跨引擎模型错配回落 PASS：xiaomi+chat 组合自动回落 mimo-v2.5 并记录警告
- i18n 全量机械核对：55 个使用键两语言表零缺失，format 占位符完备
- README 配置表一致性核对：19 行逐项与 DEFAULT_CONFIG 匹配（1 处占位符表述已修正）
- Err.log 自动存错实测：机翻异常带完整堆栈落盘成功
- config.json 完整性核验：deepseek_api_key 未被改动

### 阶段5：文档同步
- README.md 全量重写（双引擎说明、命令行参数、目录结构含 utils/errlog.py、故障排除更新）
- Design.md 按修改纪律定向修订章节（架构图、translator/config/tray 设计、新增存错设计与线程模型补充）
- Techniques.md 重写为与实现一致的技术方案
- Fact.md 清除模拟数据，记录真实事实与测试结果
- FreqErr.md 新增 6 类错误条目
- 新增 dev_log/20260827.md 版本更新文档

### 阶段6：子AGENT故障检测
- 第一轮宽范围审查AGENT因范围过大超时未收束，两度中断并要求收束后仍持续运行；改用收紧范围的同步审查AGENT（8个源文件、7类焦点）当轮交付
- 审查结论：1xP1、2xP2、4xP3、无P0（i18n与信号签名基线核对通过）

## 补充节：审查发现与处置（全部已修复）

### P1 配置布尔/自由键无验证器导致损坏配置启动崩溃
- 问题：mech_trans_enabled/mech_fallback/window_shadow/auto_translate_enabled 等布尔键与 source_lang/target_lang/快捷键等字符串键不在 VALIDATORS 内，手改 config.json 写入任意类型会穿透校验，SettingsWindow 启动即构造时 setChecked(非bool) 直接 TypeError 崩溃
- 修复：补齐 _is_bool/_is_str 验证器（type(v) is bool 精确判定防 bool 冒充 int）；数值验证器排除 bool 穿透；settings.py 三处 setChecked 增加 bool() 归一化兜底
- 回归：六种类型破坏配置实测全部回落默认值、设置窗口构造存活

### P2 结果信号 disconnect 目标不匹配（形同虚设）
- 问题：connect 用 lambda 而disconnect(self.on_mech_result)，目标永不匹配必然 TypeError 被吞掉，旧 Worker 连接实际从未断开，仅靠 worker_id 兜底
- 修复：新增 _mech_last_slot/_ai_last_slot 保存最近连接的 lambda 引用，断开真实目标后再重建新连接

### P2 退出等待 2 秒 vs 最长 30 秒请求
- 问题：run() finally 固定 wait(2000)，AI 请求进行中退出必超时，带活跃 QThread 进入 sys.exit 可能触发 "QThread: Destroyed while thread is still running"
- 修复：新增 _wait_worker 有界轮询等待（200ms 步进 x 上限 10s），超时写 Err.log 告警后放弃线程

### P3 处置明细
- monitor.stop() 不清理热键句柄 -> 已修：stop 时遍历 remove_hotkey 后清空列表
- update_mech_text 双 falsy 入参先重置后 return 造成界面残留 -> 已修：函数入口提前返回，删除尾部死代码分支
- copy_smart 会把 AI 错误串复制进剪贴板 -> 已修：按 "AI Error:"/"Error:" 前缀过滤可复制结果
- save_settings 忽略 cfg.set 拒绝结果静默假成功 -> 已修：保存后核对七个关键配置项实际生效值，失败列出键名弹窗提示且不关窗（新增 i18n 键 save_failed_msg 双语）
- --no-tray 无界面退出途径 -> 记录为已接受限制（no-tray 定位为演示/排查模式，README 已注明可用任务管理器结束进程），未做半成品退出热键

### 本轮自查另修（非审查发现）
- 设置保存后热键未按新配置重新注册 -> on_settings_saved 中调用 monitor.setup_global_hotkeys()（其内置旧句柄清理）
- build_instructions.txt 引用不存在的 build.spec -> 改为 python build.py
- README 配置表 xiaomi_api_key 默认值表述统一为 ""
- main.py 局部 import 规范化提升至模块顶部
