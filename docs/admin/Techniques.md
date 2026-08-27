# DeepTrans - 技术方案文档

## 技术栈选型

| 技术 | 实际版本基准 | 用途 | 说明 |
|------|------|------|----------|
| Python | 3.10+（实测 3.13.13 通过） | 主要开发语言 | Miniforge 环境验证 |
| PyQt6 | 6.x | GUI 框架 | 悬浮窗/托盘/设置界面 |
| openai SDK | >=1.0 | 双 AI 引擎统一调用层 | 两家后端均为 OpenAI 兼容 Chat Completions |
| deep-translator | >=1.11 | 机械翻译 | MyMemory 主选 + Google 回退 |
| pynput | >=1.7 | 全局鼠标/键盘监听 | 划词捕获 |
| keyboard | >=0.13.5 | 全局热键注册 | 开关/复制快捷键 |
| pyautogui | - | 模拟 Ctrl+C | 划词取文本（PAUSE 与 FAILSAFE 运行期调优） |
| pyperclip | >=1.8 | 剪贴板读写 | 选中文本获取与结果复制 |
| pillow | >=9.0 | 图标生成 | utils/icon_gen.py |
| PyInstaller | >=5.0 | 打包 | build.py（onefile + noconsole） |

明确不引入的依赖：requests（openai/deep-translator 内部已带传输层）、cryptography（密钥采用本地明文策略）、jieba（已移除）。

## 核心技术实现

### 1. 路径解析与冻结适配 (core/config.py)

```python
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resource_dir():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", app_dir())
    return app_dir()
```

- 可写文件（config.json、Err.log）固定 app_dir()；只读资源走 resource_dir()
- `CONFIG_FILE` 在模块导入期由 `_resolve_config_path_from_argv()` 解析 --config/--portable，
  对 import 顺序不敏感：任何模块先创建 cfg 单例都能拿到正确路径
- 图标解析 icon_path() 先查解包目录再查程序目录，双候选兜底

### 2. 双 AI 引擎装配 (core/config.py + core/translator.py)

AI_PROVIDERS 表驱动：

```python
AI_PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "api_key_field": "deepseek_api_key",
        "default_model": "chat",
        "models": {"chat": "deepseek-chat", "reasoner": "deepseek-reasoner"},
    },
    "xiaomi": {
        "label": "Xiaomi MiMo",
        "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "api_key_field": "xiaomi_api_key",
        "default_model": "mimo-v2.5",
        "models": {"mimo-v2.5": "mimo-v2.5", ...},
    },
}
```

要点：
- 客户端签名 `(api_key, base_url)` 变化才重建 OpenAI 实例，timeout=30s
- `resolve_ai_model()` 将配置中的 ai_model 解析为当前引擎的有效模型；
  跨引擎错配时回落该引擎默认模型并记录警告
- 配置校验器动态引用 AI_PROVIDERS（ai_provider 合法值 = 表键集；ai_model = 全模型并集）

### 3. 机械翻译引擎映射与回退 (core/translator.py)

- 语言检测：文本含 CJK 字符视为中文侧输入；`source_lang=auto` 时自动定向
- **语言码映射是关键坑位**：deep_translator 的 MyMemory 表大小写敏感且不含裸 zh/en，

```python
if provider == "mymemory":
    if lang_l.startswith("zh"):   # zh/zh-cn/zh-tw -> zh-CN
        return "zh-CN"
    if lang_l == "en" or lang_l.startswith("en-"):  # en* -> en-US
        return "en-US"
```

- 回退链：主机翻异常时收集错误继续尝试备选，最终返回合并错误信息（悬浮窗告警承接）
- **看门狗硬限时**（MECH_ATTEMPT_TIMEOUT=12s）：requests 无总超时且连接内 DNS 解析(getaddrinfo)
  不受 socket.setdefaulttimeout 约束——黑洞域名会永久阻塞。每个引擎尝试跑在守护线程里，
  join(timeout) 放弃后不结果；daemon 线程随进程退出回收（已知取舍）
- 总超时兜底：`socket.setdefaulttimeout(8)` 约束建立连接后的读写分段；
  OpenAI 客户端显式 timeout=30 不受影响
- **AI 最终兜底**（mech_ai_fallback，默认开）：全部机翻引擎失败后调用当前 AI 引擎
  （复用 ai_translate 同款提示词路径），输出的 "AI Error:"/"Error:" 前缀被识别为
  兜底同样失败、继续走原错误提示；保证机翻栏在受限网络下也能给出结果
- 触发链路优化沿用原设计：鼠标左键抬起 -> QTimer(300ms) -> 模拟 Ctrl+C ->
  QTimer(50ms) 读剪贴板比对变化，避免阻塞主线程（禁止 time.sleep 于 Qt 主线程）

### 4. 异步任务处理 (main.py)

```python
class Worker(QThread):
    result_ready = pyqtSignal(object)
    def __init__(self, func, *args, error_result=None): ...
    def run(self):
        try:
            result = self.func(*self.args)
        except Exception:
            log_exception("worker.run", ...)      # 先落盘 Err.log
            result = self.error_result            # 同构兜底结果
        self.result_ready.emit(result)
```

- 过期结果防护：mech_worker_id / ai_worker_id 递增，回调中 id 不匹配直接丢弃
- 旧 Worker 不 terminate()：仅断开信号连接让其自然结束，退出时 wait(2000) 收尸
- monitor 的跨线程桥接全部经信号槽（_mouse_event/_mouse_move_event/_check_clipboard_signal），
  enabled 属性用 threading.Lock 保护

### 5. 错误自动存错机制 (utils/errlog.py)

- log_error/log_warning/log_exception 三个入口，时间戳格式 `[ISO] [ERROR]`
- log_exception 写入完整 traceback；message 中换行折叠为 " | "
- main.py 全局钩子：

```python
_prev_excepthook = sys.excepthook
def _global_excepthook(t, v, tb):
    log_exception("unhandled exception", v)
    _prev_excepthook(t, v, tb)
sys.excepthook = _global_excepthook
```

- 目录独立解析与 core/config 相同规则但互不导入（防循环）
- 所有 print 类错误输出同步落盘（配置加载失败、图标生成失败等）

### 6. 配置管理与校验 (core/config.py)

- 原子写入：tempfile.mkstemp 在同目录生成临时文件 -> os.replace 原子替换；失败清理临时文件
- 损坏自愈：JSONDecodeError 时 os.replace 备份为 config.json.corrupted，默认配置继续运行
- VALIDATORS 校验表覆盖数值范围/颜色格式/枚举项；load 与 set 双入口都校验
- reset(keep_keys)：恢复默认但保留 API 密钥

### 7. 划词监控细节 (core/monitor.py)

- 防抖链路：click(left, released) -> _check_clipboard_signal(300ms) -> Ctrl+C -> _read_clipboard_after_copy(50ms)
- ignore_next_clipboard 标志：程序自身复制结果时不把翻译内容误当新划词
- is_monitoring_hold 判定拖动超阈值取消 AI 计时；信号桥接到主线程操作，消除竞态
- setup_global_hotkeys 维护句柄列表 _hotkey_handles，重注册前先 remove_hotkey 清理

### 8. 国际化 (core/i18n.py)

- TRANSLATIONS 双语言全量键表；tr(key) 带 key 原文兜底
- 本轮补齐英文侧缺失键（text_color/bg_color），新增引擎相关键（ai_provider/xiaomi_key 等），
  设置窗口所有硬编码文案迁移到 i18n（含 .format(value=...) 参数化模板）

### 9. 模块开关机制

- 源码级：gui/tray.py `ENABLE_TRAY = True/False`（False 彻底隐藏托盘入口）
- 运行时：--no-tray 参数（优先级低于源码开关的组合逻辑：两者任一关闭即无托盘）
- 配置级：mech_trans_enabled（机械翻译栏整体隐藏）、auto_translate_enabled（划词总闸）、mech_fallback

## 性能与稳定性技术

- 结果自适应高度：QTextEdit 按 document 高度钳制（机翻 60-300px，AI 100-500px）
- 几何原子更新：先 sizeHint 再 setGeometry(x,y,w,h) 计算，防离屏绘制；
  calculate_pos 含屏幕边界三段式夹紧（右溢出->光标左侧、下溢出->上方、最终 clamp）
- 颜色可读性：设置窗口保存前 #RRGGBB 正则校验，QColorDialog 快捷取色
- 字体兜底：QFont pointSize<=0 时显式 setPointSize(10)，规避 Qt 警告路径

## 安全技术

- 密钥明文本地存储（不加密不上传）；设置窗口密码模式显示（EchoMode.Password）
- 输入以 API 参数传输，无本地持久化翻译历史；Err.log 可能含请求错误片段但不含完整原文
- HTTP 全部 TLS；socket 默认超时 20s 降低挂起面

## 部署和打包技术 (build.py)

```
pyinstaller --name=DeepTrans --onefile --noconsole --icon=assets/icon.ico
            --clean --add-data=assets;assets
            --hidden-import=pynput.keyboard._win32 --hidden-import=pynput.mouse._win32
            --hidden-import=PIL main.py
```

- 打包前置检查：icon 缺失则调用 generate_icon(output_path=assets/icon.ico)
- 已清理失效的 jieba hidden-import
- 冻结态运行契约：exe 同目录读写 config.json/Err.log；_MEIPASS 只读资源

## 测试技术（本轮实际执行的验收口径）

1. 全模块 py_compile 字节编译
2. offscreen 冒烟（QT_QPA_PLATFORM=offscreen + 系统级临时脚本，不进仓库）：
   - 断言 overlay/settings/tray 构建状态、monitor 监听器存活、exec 退出码 0
   - --no-tray 与含托盘两种路径分别执行
3. AI 引擎真机联测：注入密钥于内存 cfg，不改磁盘配置；
   断言返回非空且非 "AI Error:"/"Error:" 前缀
4. 机翻语言映射回归：英->中、中->英双向构造用例（网络受限环境下验证错误路径与 Err.log 落盘）
5. 文档一致性核对：README 配置默认值 vs DEFAULT_CONFIG，命令行承诺 vs parse_args 实现
