from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from pynput import mouse, keyboard
import pyperclip
import pyautogui
from threading import Lock
from .config import cfg

class SelectionMonitor(QObject):
    # Signals
    text_selected = pyqtSignal(str) # Emitted when text is captured (Mechanical trigger)
    input_activity = pyqtSignal()   # Emitted on mouse move/click to cancel AI timer
    global_click = pyqtSignal(int, int) # Emitted on global mouse click (x, y)
    toggle_status = pyqtSignal(bool) # Emitted when enabled/disabled
    copy_trigger = pyqtSignal()      # Emitted when copy shortcut is pressed
    settings_trigger = pyqtSignal()  # Emitted when settings shortcut is pressed
    ai_trigger = pyqtSignal(str)     # Emitted when AI hold is triggered

    # Internal signals to bridge threads
    _mouse_event = pyqtSignal(bool) # pressed
    _mouse_move_event = pyqtSignal(int, int) # x, y - bridges move from pynput thread
    _check_clipboard_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._enabled = True
        self._enabled_lock = Lock()
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # State
        self.last_clipboard = ""
        self.current_text = ""
        self.ai_timer = QTimer()
        self.ai_timer.setSingleShot(True)
        self.ai_timer.timeout.connect(self._on_ai_timer)
        
        self.is_monitoring_hold = False
        self.last_mouse_pos = (0, 0)
        self.ignore_next_clipboard = False  # 初始化属性
        self._hotkey_handles = []  # 存储热键句柄以便清理
        
        # Connect internal signals to ensure thread safety
        self._mouse_event.connect(self._handle_mouse_event)
        self._mouse_move_event.connect(self._handle_mouse_move)
        self._check_clipboard_signal.connect(self._check_selection)

    @property
    def enabled(self):
        with self._enabled_lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value):
        with self._enabled_lock:
            self._enabled = value

    def start(self):
        try:
            self.mouse_listener = mouse.Listener(
                on_click=self._on_click,
                on_move=self._on_move
            )
            self.mouse_listener.start()
        except Exception as e:
            print(f"Failed to start mouse listener: {e}")
            raise RuntimeError(f"无法启动鼠标监听: {e}. 请检查系统权限。")
        
        try:
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Failed to start keyboard listener: {e}")
            if self.mouse_listener:
                self.mouse_listener.stop()
            raise RuntimeError(f"无法启动键盘监听: {e}. 请检查系统权限。")
        
        print("Monitor started")

    def stop(self):
        # 先注销全局热键，避免事件循环结束后回调仍被触发
        try:
            import keyboard as kb
            for handle in self._hotkey_handles:
                try:
                    kb.remove_hotkey(handle)
                except Exception:
                    pass
            self._hotkey_handles = []
        except Exception:
            pass  # keyboard 库不可用或已卸载时忽略
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def _on_click(self, x, y, button, pressed):
        if not self.enabled:
            return
        
        # Emit signal to handle in main thread
        self._mouse_event.emit(pressed)
        
        if pressed:
             self.global_click.emit(int(x), int(y))

        if not pressed and button == mouse.Button.left:
            # We need a small delay to let the OS register the selection finishing
            # Emit signal to run check_selection on main thread
            self._check_clipboard_signal.emit()

    def _handle_mouse_event(self, pressed):
        if pressed:
            # Mouse Down: Cancel any pending actions
            if self.ai_timer.isActive():
                self.ai_timer.stop()
            self.is_monitoring_hold = False

    def _on_move(self, x, y):
        # pynput thread - emit signal to handle on main thread
        if self.is_monitoring_hold:
            self._mouse_move_event.emit(int(x), int(y))

    def _handle_mouse_move(self, x, y):
        # Main thread - safe to access is_monitoring_hold
        if self.is_monitoring_hold:
            dx = abs(x - self.last_mouse_pos[0])
            dy = abs(y - self.last_mouse_pos[1])
            if dx > 5 or dy > 5:  # Threshold
                self.is_monitoring_hold = False

    def _check_selection(self):
        # Called via signal, runs on Main Thread
        # Optimization: Only check if enabled
        if cfg.get("auto_translate_enabled"):
             # Increase delay to avoid triggering on caret moves or clicks without selection
             # Also gives time for selection to finalize
             QTimer.singleShot(300, self._process_clipboard_delayed) 

    def _process_clipboard_delayed(self):
        if not cfg.get("auto_translate_enabled"):
            return
            
        # Optimization: Check if clipboard access is safe (simple try-except is good)
        try:
            # 0. Check if we should ignore this check (e.g. we just copied text ourselves)
            if self.ignore_next_clipboard:
                self.ignore_next_clipboard = False
                return
            
            # Save current clipboard to detect changes
            old_clipboard = pyperclip.paste()

            # Speed up pyautogui
            old_pause = pyautogui.PAUSE
            pyautogui.PAUSE = 0.01
            # Disable FAILSAFE to prevent KeyboardInterrupt when mouse is in corner
            old_failsafe = pyautogui.FAILSAFE
            pyautogui.FAILSAFE = False
            
            try:
                # Use hotkey function which handles key up/down better
                pyautogui.hotkey('ctrl', 'c')
            finally:
                pyautogui.PAUSE = old_pause # Restore
                pyautogui.FAILSAFE = old_failsafe
                
            # Use QTimer instead of time.sleep to avoid blocking the main thread
            QTimer.singleShot(50, lambda: self._read_clipboard_after_copy(old_clipboard))
            
        except Exception as e:
            print(f"Clipboard check failed: {e}")

    def _read_clipboard_after_copy(self, old_clipboard):
        """Read clipboard after Ctrl+C and emit signal if content changed."""
        try:
            new_clipboard = pyperclip.paste()
            
            if new_clipboard and new_clipboard != self.last_clipboard:
                 # It's a new valid selection
                 self.last_clipboard = new_clipboard
                 self.current_text = new_clipboard
                 
                 # Emit signal
                 if len(new_clipboard.strip()) > 0:
                     self.text_selected.emit(new_clipboard)
                     
                     # Start AI Timer
                     self.is_monitoring_hold = True
                     self.last_mouse_pos = mouse.Controller().position
                     self.ai_timer.start(int(cfg.get("trigger_delay") * 1000))
        except Exception as e:
            print(f"Clipboard read failed: {e}")



    def _on_ai_timer(self):
        # Runs on Main Thread
        if self.is_monitoring_hold:
            self.ai_trigger.emit(self.current_text)
            self.is_monitoring_hold = False

    def _on_key_press(self, key):
        pass

    def _on_key_release(self, key):
        pass

    # Using 'keyboard' library for hotkeys is better than pynput for global hotkeys
    def setup_global_hotkeys(self):
        import keyboard as kb
        
        # 清除之前注册的热键
        for handle in self._hotkey_handles:
            try:
                kb.remove_hotkey(handle)
            except Exception:
                pass
        self._hotkey_handles = []
        
        # Toggle Shortcut
        toggle_shortcut = cfg.get("shortcut_toggle")
        try:
            handle = kb.add_hotkey(toggle_shortcut, self.toggle_enabled)
            self._hotkey_handles.append(handle)
        except Exception as e:
            print(f"Invalid toggle shortcut: {toggle_shortcut} - {e}")

        # Copy Shortcut
        copy_shortcut = cfg.get("shortcut_copy_result")
        try:
            handle = kb.add_hotkey(copy_shortcut, lambda: self.copy_trigger.emit())
            self._hotkey_handles.append(handle)
        except Exception as e:
            print(f"Invalid copy shortcut: {copy_shortcut} - {e}")
            
    def toggle_enabled(self):
        with self._enabled_lock:
            self._enabled = not self._enabled
            new_state = self._enabled
        self.toggle_status.emit(new_state)
        print(f"Monitor enabled: {new_state}")

    def get_clipboard_content(self):
        try:
            return pyperclip.paste()
        except Exception:
            return ""

# Global instance
monitor = SelectionMonitor()
