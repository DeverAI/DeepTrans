# DeepTrans - 常见错误记录文档

## 运行时错误 (RE)

### [错误类型] API密钥无效或缺失
**错误描述**：
- 程序启动时提示 "API key not found"
- 翻译功能无法使用，返回 "Invalid API key" 错误
- 控制台显示 401 或 403 错误码

**技术表现**：
```python
# 错误日志示例
[ERROR] Deepseek API returned 401 Unauthorized
[ERROR] Invalid API key: sk-xxxxxxxx
```

**正确做法**：
1. 检查 `config.json` 文件中的 `deepseek_api_key` 字段
2. 确认API密钥格式正确（以 "sk-" 开头）
3. 验证API密钥是否有效且未过期
4. 登录 Deepseek 控制台确认密钥权限
5. 重新获取有效的API密钥并更新配置文件

**预防措施**：
- 在配置文件中添加API密钥格式验证
- 实现密钥有效性检查机制
- 提供密钥管理界面

### [错误类型] 网络连接失败
**错误描述**：
- 翻译请求超时
- 无法连接到翻译API服务器
- 网络不稳定导致翻译失败

**技术表现**：
```python
# 错误日志示例
[ERROR] Connection timeout: request timed out
[ERROR] Failed to establish connection to api.deepseek.com
[ERROR] Network is unreachable
```

**正确做法**：
1. 检查网络连接是否正常
2. 确认防火墙设置是否阻止API访问
3. 尝试切换网络环境（WiFi/有线）
4. 检查DNS设置是否正确
5. 使用 `ping api.deepseek.com` 测试连通性
6. 考虑使用代理或VPN（如果需要）

**预防措施**：
- 实现网络状态检测
- 添加重试机制和超时控制
- 提供网络错误提示和解决建议

### [错误类型] 翻译结果为空
**错误描述**：
- 翻译功能正常调用，但返回空结果
- 界面显示空白或 "无翻译结果"
- API调用成功但内容为空

**技术表现**：
```python
# 错误日志示例
[WARNING] Translation result is empty
[WARNING] API response contains no data
[ERROR] Empty translation result for input: "test"
```

**正确做法**：
1. 检查输入文本是否为空或仅包含特殊字符
2. 确认语言对配置是否正确
3. 尝试翻译其他文本验证功能是否正常
4. 检查API返回的完整响应内容
5. 查看是否有字符编码问题
6. 尝试切换翻译引擎

**预防措施**：
- 添加输入文本验证
- 实现翻译结果质量检查
- 提供详细的API响应日志

### [错误类型] 内存不足
**错误描述**：
- 程序运行缓慢或无响应
- 系统提示内存不足
- 翻译大文本时程序崩溃

**技术表现**：
```python
# 错误日志示例
[ERROR] MemoryError: Unable to allocate memory
[WARNING] Memory usage exceeded 90%
[CRASH] Application crashed due to out of memory
```

**正确做法**：
1. 关闭其他占用内存的程序
2. 重启程序释放内存
3. 减少同时处理的文本量
4. 检查是否有内存泄漏
5. 增加系统虚拟内存
6. 考虑升级硬件配置

**预防措施**：
- 实现内存使用监控
- 优化内存管理策略
- 添加内存限制和警告机制

## 配置错误

### [错误类型] 配置文件格式错误
**错误描述**：
- 程序启动时提示配置文件解析错误
- JSON格式不正确导致配置加载失败
- 配置项缺失或类型错误

**技术表现**：
```python
# 错误日志示例
[ERROR] Failed to parse config.json: Invalid JSON
[ERROR] Missing required configuration: deepseek_api_key
[ERROR] Invalid configuration type: overlay_width must be integer
```

**正确做法**：
1. 使用JSON验证工具检查文件格式
2. 确认所有必需的配置项都存在
3. 检查配置项的数据类型是否正确
4. 备份当前配置文件
5. 删除或重命名配置文件让程序生成默认配置
6. 手动编辑配置文件确保格式正确

**预防措施**：
- 实现配置文件格式验证
- 提供配置文件模板
- 添加配置向导功能

### [错误类型] 配置项值无效
**错误描述**：
- 配置项值超出有效范围
- 语言代码不正确
- 颜色格式错误

**技术表现**：
```python
# 错误日志示例
[ERROR] Invalid language code: 'en_US', expected 'en-US'
[ERROR] Color value must be in hex format: '#3C6EF0'
[ERROR] Overlay width must be between 200 and 800
```

**正确做法**：
1. 查看配置文件中的无效值
2. 参考文档确认正确的格式
3. 使用配置界面的验证功能
4. 恢复默认配置重新设置
5. 检查是否有拼写错误

**预防措施**：
- 实现配置项值验证
- 提供配置项说明和示例
- 添加实时配置验证

## 界面错误

### [错误类型] 窗口显示异常
**错误描述**：
- 悬浮翻译窗口无法显示
- 窗口位置偏移或超出屏幕
- 窗口样式显示异常

**技术表现**：
```python
# 错误日志示例
[ERROR] Failed to create overlay window
[WARNING] Window position out of screen bounds
[ERROR] Failed to load stylesheet
```

**正确做法**：
1. 检查屏幕分辨率设置
2. 尝试调整 `overlay_width` 配置项
3. 重启程序重置窗口状态
4. 检查系统主题设置
5. 更新显卡驱动程序
6. 以管理员权限运行程序

**预防措施**：
- 实现窗口位置自适应
- 添加窗口创建错误处理
- 提供窗口重置功能

### [错误类型] 热键冲突
**错误描述**：
- 全局热键无法注册
- 热键与其他程序冲突
- 热键触发无响应

**技术表现**：
```python
# 错误日志示例
[ERROR] Failed to register hotkey: ctrl+alt+t
[WARNING] Hotkey already registered by another application
[ERROR] Hotkey callback not triggered
```

**正确做法**：
1. 更换热键组合
2. 检查是否有其他程序使用相同热键
3. 以管理员权限运行程序
4. 在系统中禁用冲突的热键
5. 重启程序尝试重新注册热键
6. 检查系统热键注册表设置

**预防措施**：
- 实现热键冲突检测
- 提供热键自定义界面
- 添加热键状态显示

## 打包和部署错误

### [错误类型] 打包失败
**错误描述**：
- PyInstaller打包过程出错
- 依赖包缺失导致打包失败
- 生成的可执行文件无法运行

**技术表现**：
```python
# 错误日志示例
[ERROR] Failed to build executable: Missing dependency 'PyQt6.QtWebEngine'
[ERROR] PyInstaller failed with exit code 1
[ERROR] Executable crashes on startup
```

**正确做法**：
1. 检查所有依赖包是否正确安装
2. 更新PyInstaller到最新版本
3. 使用 `--hidden-import` 参数添加缺失的模块
4. 检查是否有路径包含空格或特殊字符
5. 在干净的虚拟环境中重新打包
6. 查看详细的打包日志信息

**预防措施**：
- 使用虚拟环境进行打包
- 创建详细的打包脚本
- 测试打包后的程序

### [错误类型] 运行时库缺失
**错误描述**：
- 可执行文件运行时提示库文件缺失
- DLL文件加载失败
- 运行环境不兼容

**技术表现**：
```python
# 错误日志示例
[ERROR] The code execution cannot proceed because VCRUNTIME140.dll was not found
[ERROR] Failed to load Qt platform plugin "windows"
[ERROR] Application failed to initialize properly (0xc0000135)
```

**正确做法**：
1. 安装相应的运行时库（如Visual C++ Redistributable）
2. 确保目标系统有相同的运行环境
3. 检查系统架构匹配（32位/64位）
4. 重新打包包含所有必要的库文件
5. 使用 `--onedir` 模式替代 `--onefile` 模式
6. 在目标系统上安装Python运行时

**预防措施**：
- 打包时包含所有必要的运行时库
- 提供运行时环境检查
- 创建安装程序而非仅可执行文件

## 性能问题

### [错误类型] 翻译响应缓慢
**错误描述**：
- 翻译请求响应时间过长
- 界面卡顿无响应
- CPU占用过高

**技术表现**：
```python
# 性能日志示例
[WARNING] Translation took 15.2 seconds (normal: <5s)
[ERROR] UI thread blocked for 3.5 seconds
[WARNING] CPU usage: 85% (normal: <20%)
```

**正确做法**：
1. 检查网络连接速度
2. 减少同时进行的翻译请求
3. 启用翻译结果缓存
4. 优化翻译引擎配置
5. 关闭不必要的后台功能
6. 重启程序释放系统资源

**预防措施**：
- 实现翻译请求队列管理
- 添加性能监控和警告
- 提供性能优化设置

### [错误类型] 内存泄漏
**错误描述**：
- 程序运行时间越长内存占用越大
- 长时间运行后系统变慢
- 程序最终因内存不足崩溃

**技术表现**：
```python
# 性能日志示例
[WARNING] Memory usage increasing: 50MB -> 150MB -> 300MB
[ERROR] Memory allocation failed after 2 hours of runtime
[CRASH] Out of memory after prolonged use
```

**正确做法**：
1. 重启程序释放内存
2. 减少程序运行时间
3. 监控内存使用情况
4. 检查是否有未释放的资源
5. 更新到最新版本修复内存泄漏
6. 联系技术支持报告问题

**预防措施**：
- 实现内存使用监控
- 定期检查和释放资源
- 使用内存分析工具优化代码

## 安装和环境错误

### [错误类型] Python环境问题
**错误描述**：
- Python版本不兼容
- 依赖包安装失败
- 环境变量配置错误

**技术表现**：
```python
# 错误日志示例
[ERROR] Python version 3.8 is not supported, requires 3.10+
[ERROR] Failed to install package: PyQt6
[ERROR] PYTHONPATH not configured correctly
```

**正确做法**：
1. 安装正确版本的Python（3.10+）
2. 使用虚拟环境管理依赖
3. 更新pip到最新版本
4. 清理pip缓存后重试安装
5. 检查系统PATH环境变量
6. 以管理员权限安装依赖包

**预防措施**：
- 提供环境检查脚本
- 创建详细的环境配置指南
- 使用conda等环境管理工具

### [错误类型] 权限问题
**错误描述**：
- 无法访问配置文件
- 系统托盘功能无法使用
- 全局钩子注册失败

**技术表现**：
```python
# 错误日志示例
[ERROR] Permission denied: cannot write to config.json
[ERROR] Failed to create system tray icon
[ERROR] Global hook registration failed
```

**正确做法**：
1. 以管理员权限运行程序
2. 检查文件和文件夹权限
3. 将程序安装到有写入权限的目录
4. 关闭UAC或调整安全设置
5. 检查用户账户控制设置
6. 确保程序有足够的系统权限

**预防措施**：
- 提供权限检查和提示
- 创建便携版本减少权限需求
- 提供权限配置向导

## 数据和文件错误

### [错误类型] 配置文件损坏
**错误描述**：
- 配置文件内容被意外修改
- 文件编码问题导致解析失败
- 配置文件被其他程序锁定

**技术表现**：
```python
# 错误日志示例
[ERROR] Config file corrupted: unexpected end of JSON input
[ERROR] Failed to read config: file is locked by another process
[ERROR] Unicode decode error: invalid UTF-8 sequence
```

**正确做法**：
1. 备份当前配置文件
2. 删除损坏的配置文件
3. 重启程序生成新的默认配置
4. 手动创建新的配置文件
5. 检查文件编码格式
6. 确保文件没有被其他程序占用

**预防措施**：
- 实现配置文件备份机制
- 添加配置文件完整性检查
- 提供配置文件恢复功能

### [错误类型] 日志文件过大
**错误描述**：
- 日志文件占用过多磁盘空间
- 程序写入日志失败
- 日志文件影响程序性能

**技术表现**：
```python
# 错误日志示例
[ERROR] Disk space low: cannot write to log file
[WARNING] Log file size exceeds 100MB
[ERROR] Failed to rotate log files
```

**正确做法**：
1. 清理或删除旧的日志文件
2. 配置日志文件大小限制
3. 启用日志文件轮转功能
4. 将日志文件存储到其他位置
5. 压缩或归档历史日志
6. 定期清理日志文件

**预防措施**：
- 实现日志文件自动管理
- 设置日志文件大小限制
- 提供日志清理工具

## 用户操作错误

### [错误类型] 错误的文本选择
**错误描述**：
- 选择了不完整的文本
- 文本包含格式字符
- 文本过长导致翻译失败

**技术表现**：
```python
# 错误日志示例
[WARNING] Selected text contains formatting characters
[ERROR] Text too long for translation: 5000 characters (max: 1000)
[WARNING] Incomplete text selection detected
```

**正确做法**：
1. 重新选择完整的文本内容
2. 清理文本中的格式字符
3. 将长文本分割为多个短文本
4. 使用纯文本模式选择
5. 检查文本编码是否正确
6. 避免选择包含特殊符号的文本

**预防措施**：
- 添加文本预处理功能
- 提供文本选择建议
- 实现文本长度限制

### [错误类型] 错误的配置修改
**错误描述**：
- 修改了不支持的配置项
- 配置值格式不正确
- 配置保存失败

**技术表现**：
```python
# 错误日志示例
[ERROR] Invalid configuration value: 'not_a_color' for theme_color
[WARNING] Unknown configuration option: custom_option
[ERROR] Failed to save configuration: permission denied
```

**正确做法**：
1. 使用配置界面修改设置
2. 参考文档确认正确的配置格式
3. 恢复默认配置重新设置
4. 检查文件权限
5. 重启程序应用新配置
6. 联系技术支持获取配置帮助

**预防措施**：
- 提供安全的配置界面
- 添加配置验证功能
- 提供配置备份和恢复

## 代码质量问题

### [错误类型] 配置文件写入中途损坏
**错误描述**：
- 程序运行中突然断电或崩溃后，config.json文件损坏
- 下次启动时提示JSON解析错误
- 配置文件内容为空或不完整

**技术表现**：
```python
# 错误日志示例
[ERROR] Error loading config: Expecting value: line 1 column 1 (char 0)
[ERROR] Failed to parse config.json: Invalid JSON
```

**正确做法**：
1. 使用原子写入：先写入临时文件，成功后重命名
2. 写入前备份原配置文件
3. 加载失败时使用默认配置并提示用户
4. 实现配置文件完整性检查

**预防措施**：
- 实现原子写入机制（tempfile + os.replace）
- 添加配置文件备份功能
- 加载失败时优雅降级到默认配置

### [错误类型] QThread强制终止导致资源泄漏
**错误描述**：
- 使用QThread.terminate()终止线程
- 线程中的网络连接未正确关闭
- 锁未释放导致死锁
- 程序运行时间越长，资源占用越大

**技术表现**：
```python
# 错误代码示例
self.worker.terminate()  # 危险！强制终止
self.worker.wait()
```

**正确做法**：
1. 使用协作式取消机制（设置标志位让Worker自行退出）
2. 断开信号连接，让旧线程自然结束
3. 使用QThreadPool + QRunnable管理线程
4. 确保线程中的资源在退出时正确释放

**预防措施**：
- 避免使用terminate()，改用信号断开
- 实现线程安全的取消机制
- 使用上下文管理器确保资源释放

### [错误类型] 主线程阻塞导致UI卡顿
**错误描述**：
- 在Qt主线程中使用time.sleep()
- UI事件循环被阻塞
- 界面无响应或卡顿
- 用户操作延迟明显

**技术表现**：
```python
# 错误代码示例
def process_data(self):
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.05)  # 阻塞主线程！
    clipboard = pyperclip.paste()
```

**正确做法**：
1. 使用QTimer.singleShot替代time.sleep
2. 将耗时操作移到后台线程
3. 使用信号槽机制进行异步通信
4. 避免在主线程中执行任何阻塞操作

**预防措施**：
- 所有UI相关操作在主线程，耗时操作在后台线程
- 使用QTimer进行延迟操作
- 定期检查主线程是否有阻塞调用

### [错误类型] 跨线程竞争条件
**错误描述**：
- 多个线程同时读写同一变量
- 变量值不确定，取决于线程执行顺序
- 程序行为不可预测
- 难以复现的随机崩溃

**技术表现**：
```python
# 错误代码示例
# 线程A (pynput)
self.is_monitoring_hold = False

# 线程B (Qt主线程)
if self.is_monitoring_hold:  # 可能读到旧值
    self.start_timer()
```

**正确做法**：
1. 使用信号槽机制桥接线程间通信
2. 使用threading.Lock保护共享变量
3. 将共享变量的操作限制在单一线程
4. 使用Qt的跨线程信号机制

**预防措施**：
- 识别所有跨线程访问的变量
- 使用信号槽替代直接变量访问
- 代码审查时重点关注线程安全

### [错误类型] bare except子句掩盖错误
**错误描述**：
- 使用except:不指定异常类型
- 捕获了KeyboardInterrupt、SystemExit等系统异常
- 真正的错误被吞没，难以调试
- 程序行为异常但无错误日志

**技术表现**：
```python
# 错误代码示例
try:
    risky_operation()
except:  # 危险！捕获所有异常
    pass  # 错误被吞没
```

**正确做法**：
1. 始终指定异常类型：except Exception as e
2. 记录异常信息到日志
3. 根据异常类型采取不同的处理策略
4. 只捕获预期的异常类型

**预防措施**：
- 代码规范禁止使用bare except
- 使用lint工具检查bare except
- 代码审查时重点关注异常处理

### [错误类型] Worker 线程信号竞争条件
**错误描述**：
- 新旧 Worker 线程结果互相覆盖
- 旧 Worker 完成时覆盖新 Worker 的结果
- 翻译结果显示混乱或丢失

**技术表现**：
```python
# 错误代码示例
self.mech_worker = Worker(translator.mechanical_translate, text)
self.mech_worker.result_ready.connect(self.on_mech_result)
# 旧 Worker 仍在运行，其结果会覆盖新结果
```

**正确做法**：
1. 使用 Worker ID 区分新旧结果
2. 在回调中检查 Worker ID 是否匹配
3. 丢弃过期 Worker 的结果

**预防措施**：
- 实现 Worker ID 追踪机制
- 在回调中验证 Worker ID
- 断开旧 Worker 的信号连接

### [错误类型] 配置值类型未验证
**错误描述**：
- 用户手动编辑 config.json 导致类型错误
- 配置值超出有效范围
- 程序使用无效配置导致崩溃

**技术表现**：
```python
# 错误日志示例
[ERROR] TypeError: unsupported operand type(s) for *: 'str' and 'int'
[ERROR] ValueError: invalid literal for int() with base 10
```

**正确做法**：
1. 实现配置值验证器
2. 在加载和设置时验证类型
3. 使用默认值作为后备

**预防措施**：
- 定义配置值验证规则
- 在 ConfigManager 中实现验证
- 提供友好的错误提示

### [错误类型] 热键重复注册
**错误描述**：
- 设置保存后热键被重复注册
- 同一热键触发多次回调
- 程序行为异常

**技术表现**：
```python
# 错误代码示例
def setup_global_hotkeys(self):
    kb.add_hotkey(toggle_shortcut, self.toggle_enabled)
    # 多次调用会导致重复注册
```

**正确做法**：
1. 清除之前注册的热键
2. 保存热键句柄以便清理
3. 重新注册前先移除旧热键

**预防措施**：
- 实现热键句柄管理
- 注册前清除旧热键
- 避免重复调用注册函数

### [错误类型] 跨线程变量访问未加锁
**错误描述**：
- 多个线程同时读写同一变量
- 变量值不确定，取决于线程执行顺序
- 程序行为不可预测

**技术表现**：
```python
# 错误代码示例
# 线程 A (pynput)
self.is_monitoring_hold = False

# 线程 B (Qt 主线程)
if self.is_monitoring_hold:  # 可能读到旧值
    self.start_timer()
```

**正确做法**：
1. 使用 threading.Lock 保护共享变量
2. 使用属性装饰器实现线程安全访问
3. 将共享变量的操作限制在单一线程

**预防措施**：
- 识别所有跨线程访问的变量
- 使用锁或信号槽替代直接访问
- 代码审查时重点关注线程安全

### [错误类型] 配置文件 JSON 解析失败
**错误描述**：
- 配置文件格式损坏
- 程序启动时提示 JSON 解析错误
- 配置丢失或使用默认值

**技术表现**：
```python
# 错误日志示例
[ERROR] Error loading config: Invalid JSON format - Expecting value: line 1 column 1
```

**正确做法**：
1. 捕获 JSONDecodeError 异常
2. 备份损坏的配置文件
3. 使用默认配置继续运行
4. 提示用户配置文件已损坏

**预防措施**：
- 实现原子写入机制
- 添加配置文件完整性检查
- 加载失败时优雅降级

### [错误类型] AI 翻译无超时控制
**错误描述**：
- 网络不稳定时 AI 翻译请求无限等待
- Worker 线程被长时间阻塞
- 界面无响应

**技术表现**：
```python
# 错误代码示例
response = self.client.chat.completions.create(
    model=model_name,
    messages=[...],
    stream=False
    # 无 timeout 参数
)
```

**正确做法**：
1. 在 OpenAI 客户端中设置 timeout
2. 使用合理的超时时间（如 30 秒）
3. 捕获超时异常并提示用户

**预防措施**：
- 创建客户端时设置 timeout
- 实现超时重试机制
- 提供网络状态检测

这些常见错误记录为用户和开发者提供了详细的错误信息和解决方案，帮助快速定位和解决问题，提升用户体验和系统稳定性。

## 全量更新验收新增条目（2026-08-27）

### [错误类型] MyMemory 语言码大小写敏感且无裸码
**技术表现**：`LanguageNotSupportedException: en-us --> No support for the provided language` 或 `zh --> 不支持`。deep_translator 的 MyMemory 支持表为 `english us: en-US`、`chinese simplified: zh-CN` 等完整形式，传入小写 `en-us` 或裸 `zh` 都会抛异常。
**现象表现**：机械翻译任何文本都失败，错误堆栈写入 Err.log。
**正确做法**：映射函数不得整体 lower 后透传；必须归一化为表内精确形式——zh 开头一律映射 zh-CN，en 及 en-* 一律映射 en-US。

### [错误类型] deep-translator 无总超时导致 Worker 悬挂
**技术表现**：requests 库无默认超时参数，端点 TCP 黑洞时 connect/read 无限等待；悬浮窗永远停留在"翻译中"，进程正常但线程卡死。
**正确做法**：设置 `socket.setdefaulttimeout(20)` 进程级兜底（OpenAI 客户端自带显式 timeout=30 不受影响）；同时 Err.log 会记录最终异常供诊断。

### [错误类型] except 处理路径内的 NameError 被掩盖成翻译失败
**技术描述**：异常处理代码里调用了未导入的辅助函数（如 log_exception），py_compile 完全无法发现，只有真实触发该 except 分支才爆炸。
**正确做法**：所有第三方导入集中在模块顶部不使用内联 import；编译检查之后必须构造真实异常路径的运行用例验证错误处理链路本身。

### [错误类型] 测试假象：pwsh 将 stderr 警告误判为命令失败
**技术表现**：pwsh 包装的原生命令把 stderr 输出升级为 NativeCommandError，导致 exit code 1，但程序实际成功（如 pip 的 PATH 警告、Qt offscreen 字体警告）。
**正确做法**：判定成败以关键 stdout 标记（如 EXEC-CODE/SMOKE-PASS）与业务断言为准，不能单看 exit code；必要时设 `$env:PYTHONIOENCODING='utf-8'` 并显式 UTF-8 控制台编码避免 GBK 打印崩溃干扰判读。

### [错误类型] 相对路径资源与配置在打包/换目录后失效
**技术表现**：源码内硬编码 "assets/icon.ico"、"config.json" 相对 cwd 解析；打包后 exe 换位置运行出现图标丢失、配置读写到未知目录。
**正确做法**：统一路径解析层 app_dir()/resource_dir()/icon_path()（冻结态取 exe 目录与 sys._MEIPASS），全项目禁止散落相对路径假设。

### [错误类型] argparse 在导入期解析引发的意外退出
**技术描述**：若在模块导入期解析命令行并使用了默认 help 行为，`--help` 或非法参数会让 parse_args 直接 SystemExit，程序未启动就退出。
**正确做法**：导入期只做 `parse_known_args(..., add_help=False)` 并捕获 SystemExit 返回 None；完整解析与帮助放在 main 入口。

### [错误类型] lambda 连接配对命名函数断开导致 disconnect 永不生效
**技术描述**：`signal.connect(lambda ...)` 后用 `signal.disconnect(self.slot)` 断开——目标不匹配必然抛 TypeError，若外层有 except TypeError: pass 则静默吞掉，旧连接实际仍在发射。配合 worker_id 校验时被掩盖，一旦移除校验立即复现结果覆盖。
**正确做法**：connect 前把 lambda 存入实例属性（如 self._last_slot），disconnect 时使用同一引用；或改用具名方法/携带 ID 参数的自定义信号直连。

### [错误类型] 数值校验器放行布尔值（isinstance(True, int) == True）
**技术描述**：Python 布尔是 int 子类，`isinstance(v, (int, float))` 对 True/False 返回真，手改 JSON 写入 true 会穿透范围校验进入运算或 UI 类型转换。
**正确做法**：数值验证器显式排除 `not isinstance(v, bool)`；布尔键用 `type(v) is bool` 精确判定。

### [错误类型] GUI 构造期消费未校验配置使损坏配置变成启动死锁
**技术描述**：SettingsWindow 在主程序构造期即实例化，QCheckBox.setChecked(非bool) 直接抛 TypeError——用户一次手改配置即可让程序永远无法启动（比运行时崩溃更严重）。
**正确做法**：所有配置入口（load/set）做全字段类型校验回落默认；GUI 设值处再作一层 bool()/int() 归一化兜底（防御纵深）。

### [错误类型] socket.setdefaulttimeout 无法约束 DNS 解析导致"超时设置无效"
**技术描述**：requests/urllib3 建连过程分 DNS(getaddrinfo) 与 TCP/TLS 两段；setdefaulttimeout 只影响后者。getaddrinfo 在被污染/黑洞的解析环境可无限阻塞（faulthandler 定位到 urllib3 create_connection 内），表现为"设了超时仍卡死"。
**正确做法**：对不可控第三方调用使用守护线程 + join(timeout) 的看门狗模式硬限时；放弃等待的线程必须是 daemon（进程退出自动回收），并在文档中声明该取舍。

### [错误类型] 免Key网页翻译端点全线反爬（国内）
**技术描述**：百度 fanyi.baidu.com/transapi 返回 errno 1022、/basetrans 返回空响应；有道 aidemo.youdao.com 需 _sign/_tsalt 签名参数（裸请求 errorCode 102）；腾讯相关接口 405。这些接口随时可能变化，不能作为无配置依赖项。
**正确做法**：只内置经真机验证的通道（deep-translator 官方支持的 MyMemory/Google + OpenAI 兼容 AI 引擎）；未验证的网页爬取式方案一律不进主干，需要时引导用户走带密钥的正规开放平台。
