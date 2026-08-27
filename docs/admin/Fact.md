# DeepTrans - 事实记录文档

## 用户偏好约束

### 禁止事项
- **禁止使用 EMOJI**：文档中不得包含任何表情符号（包括 ✅ 之类符号标记）
- **禁止全局 AI Agent**：本项目不引入全局 AI Agent 进行自动化决策
- **轻量化优先**：如无必要，不使用大的外部包或复杂依赖，优先标准库
- **模块开关机制**：项目中的模块必须设置开关（源码级 `ENABLE_XXX` 或配置开关）

### 本轮用户明确指示（2026-08-27 会话）
- **API 密钥保持原样**：config.json 中现有 DeepSeek 密钥不得改动或替换；为启用小米引擎仅**新增** `xiaomi_api_key` 字段
- **AI 引擎升级方案**：双引擎（DeepSeek 官方 + 小米 token-plan MiMo），**默认小米 mimo-v2.5**
- **机翻国内引擎**：搞不到就直接走 AI（已探测：国内免Key端点全线反爬，按授权落地 mech_ai_fallback）
- **GitHub 发布**：仓库 DeverAI/DeepTrans 设为 **Public**；因本机无可用国际通道，由**用户手动上传**；发布包含 exe 资产；密钥占位符化（config.example.json）；用户提供的 ghp_ token 已暴露，建议立即撤销
- **升级范围授权**：允许顺手升级与 UI 更改；唯一红线是不做 rm -rf 式销毁操作
- **测试深度**：接受在本机安装/复用 Miniforge 环境进行真机验收

## 项目状态事实

### 当前版本
- **版本号**：v1.4.0（发布准备完成；GitHub 上传由用户按 UPLOAD_GUIDE 手动执行）
- **开发状态**：双 AI 引擎版本完成真机验收
- **部署状态**：PyInstaller onefile 构建成功（dist/DeepTrans.exe 约 62MB，已排除 PyQt5 多绑定冲突）；GitHub 发布包就绪于 backups/github_release_20260827/，上传由用户手动执行

### 已实现功能
- 双 AI 翻译引擎（DeepSeek 官方 / 小米 token-plan MiMo，OpenAI 兼容协议），设置窗口内可切换
- 机械翻译（deep-translator 库：MyMemory 主选 + Google 回退，可关闭回退）
- 悬浮翻译窗口（拖动、右下角尺寸手柄、屏幕边界自适应定位）
- 系统托盘（菜单控制；支持 --no-tray 关闭与源码级 ENABLE_TRAY 开关）
- 全局热键（监听开关 Ctrl+Alt+T、复制结果 Ctrl+Shift+C）
- 配置管理（JSON、原子写入、损坏备份、值校验、恢复默认时保留 API 密钥）
- 错误自动存错机制（utils/errlog.py：RE 追加写入根目录 Err.log，含全局 excepthook）
- 国际化（中/英界面语言包；设置窗口文案无硬编码遗留）
- 命令行参数（--config PATH / --debug / --no-tray / --portable）

### 技术架构事实
- **GUI 框架**：PyQt6
- **实际依赖**：PyQt6、pynput、pyperclip、openai、deep-translator、pillow、keyboard、pyautogui（见 requirements.txt）
- **AI 协议**：两家引擎均为 OpenAI Chat Completions 兼容接口（openai SDK 统一调用）
- **配置格式**：JSON
- **打包工具**：PyInstaller（build.py，onefile + noconsole）
- **本机运行环境**：Miniforge Python 3.13.13（C:\Users\Administrator\miniforge3\python.exe）

### 已知限制（当前环境实测确认）
- **机械翻译网络不可达**：本机到 api.mymemory.translated.net 与 translate.googleapis.com 均 ConnectTimeout，属部署网络限制而非代码缺陷；失败会写入 Err.log 并在悬浮窗以告警按钮展示详情
- 依赖网络连接进行翻译
- 主要针对 Windows 平台优化
- settings/ui_language 变更需重启程序生效（界面有明确提示）

## 冲突记录

### [冲突记录] 国内机翻引擎需求 与 免Key端点全线反爬
**冲突描述**：用户要求为机械翻译接入国内引擎，搞不到则回落 AI。实测（2026-08-27）：百度 transapi 返回 errno 1022 反爬、basetrans 返回空响应；有道 aidemo 返回 errorCode 102（需签名）；腾讯 rewordc 405；均无法作为免配置引擎稳定使用。
**处理方案**：不发布未经真机验证的爬取式引擎；按用户授权实现 mech_ai_fallback——全部机翻引擎失败后自动用当前 AI 引擎兜底（默认开启）。另将引擎尝试加 12 秒看门狗线程硬限时，修复黑洞域名下 DNS 解析(getaddrinfo)不受 socket 超时约束导致的永久阻塞。

### [冲突记录] 默认小米引擎 与 密钥保持原样
**冲突描述**：用户要求默认 AI 引擎为小米 token-plan，同时要求"不改 config.json 里任何密钥"；而默认小米引擎没有密钥将直接报错。
**处理方案**：严格区分"改"与"增"——现有 `deepseek_api_key` 一字不动，仅**新增** `xiaomi_api_key` 字段并写入 DSH 凭据托管的 tp- 密钥。已向用户说明并在验收中确认 DeepSeek 旧键完好。

### [冲突记录] 命令行禁改项目文件 与 整项目备份/dev_log 合并
**冲突描述**：工作流禁止用命令行修改删除项目文件，但整项目备份与重复文档合并需要文件操作。
**处理方案**：所有修改一律走内置文件工具；命令行只执行**纯备份性质**操作（复制到 backups/），合并产生的多余副本以"移入 backups/ 保存"代替删除。

## 开发决策记录

### [决策记录] PyQt6 选择
**决策**：选择 PyQt6 作为 GUI 框架
**理由**：功能完善、性能优秀、跨平台支持良好、文档丰富，与项目需求匹配度高。

### [决策记录] 双 AI 引擎架构（v1.3.0 落地）
**决策**：AI 翻译支持 deepseek 与 xiaomi 两个后端，配置项 `ai_provider` 切换，默认 xiaomi/mimo-v2.5
**理由**：
- 小米 token-plan（https://token-plan-cn.xiaomimimo.com/v1）为 OpenAI 兼容接口，与 DeepSeek 共用 openai SDK，改动集中在 core/config.py 的 AI_PROVIDERS 定义与 translator 的客户端装配层
- DeepSeek 保留作为对照与备用引擎
- 两家各自保存密钥，切换引擎无需重填

### [决策记录] 路径解析集中化
**决策**：app_dir()/resource_dir()/icon_path() 集中于 core/config.py；冻结态从 exe 所在目录读写、从 _MEIPASS 读资源；导入期解析 --config/--portable 保证 cfg 创建前路径即正确
**理由**：消除相对路径假设，任意 cwd 与 PyInstaller 场景均成立；utils/errlog 自带同规则的独立解析避免循环导入（已注释说明该取舍）。

### [决策记录] 恢复默认保留 API 密钥
**决策**：ConfigManager.reset(keep_keys=("deepseek_api_key","xiaomi_api_key")) 
**理由**：误点恢复默认不应导致两家密钥全被清空；确认弹窗文案同步注明。

### [决策记录] socket.setdefaulttimeout(20) 兜底
**决策**：在 core/translator.py 设置进程级默认 socket 超时
**理由**：deep-translator/requests 无总超时参数，端点黑洞时请求无限悬挂拖死 Worker；OpenAI 客户端自带 30s 显式超时不受影响。

### [决策记录] Worker 线程兜底错误结果
**决策**：Worker 增加 error_result 参数，run() 内异常时按同构类型返回兜底结果并记录 Err.log
**理由**：防止线程静默死亡导致界面永远停留在"翻译中..."状态。

## 测试结果事实（2026-08-27 真机验收）

### 编译与启动
- 全部模块 py_compile 通过
- QT_QPA_PLATFORM=offscreen 启动冒烟：--no-tray 与含托盘两种模式均 EXEC-CODE 0，监听器正常启动，配置文件正确解析

### AI 翻译实测
- 小米 mimo-v2.5："The quick brown fox jumps over the lazy dog." 正常返回中文译文
- DeepSeek deepseek-chat：同一输入正常返回中文译文（沿用 config.json 原有密钥，未替换）
- 两轮往返实测均 PASS（终端乱码仅为 GBK 控制台显示问题，数据本身 UTF-8 正常）

### 机械翻译实测
- MyMemory 语言码大小写缺陷修复后请求参数合法
- 实际 HTTP 到 api.mymemory.translated.net / translate.googleapis.com 均超时（本机网络限制）；错误按设计进入 Err.log 并由悬浮窗告警承接

### 自动存错机制实测
- 人为触发机翻异常后 Err.log 收到完整堆栈（LanguageNotSupportedException 等），机制有效

## 维护资源事实
- 维护方式：文档单套制（根目录），每轮修改记入 dev_log/
- 测试脚本策略：验收临时脚本放系统 TEMP 目录，不进项目仓库

---

以上事实基于 2026-08-27 完整更新验收轮的真实代码与真实测试输出，替代此前文档中的模拟与设想类数据。
