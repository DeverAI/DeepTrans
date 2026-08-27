import argparse
import os
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QIcon

from gui.overlay import OverlayWindow
from gui.settings import SettingsWindow
from gui.tray import ENABLE_TRAY, TrayIcon
from gui.about import AboutWindow
from gui.styles import get_stylesheet
from core.monitor import monitor
from core.translator import translator
from core.config import CONFIG_FILE, app_dir, cfg, icon_path
from core.i18n import tr
from utils.errlog import log_error, log_exception


# ---------------------------------------------------------------------------
# 全局异常钩子：任何未被捕获的运行时错误都写入 Err.log 后再交给原处理链。
# ---------------------------------------------------------------------------
_prev_excepthook = sys.excepthook


def _global_excepthook(exc_type, exc_value, exc_tb):
    try:
        log_exception("unhandled exception", exc_value)
    except Exception:
        pass
    _prev_excepthook(exc_type, exc_value, exc_tb)


sys.excepthook = _global_excepthook


class Worker(QThread):
    result_ready = pyqtSignal(object)  # Changed to object to support tuples

    def __init__(self, func, *args, error_result=None):
        super().__init__()
        self.func = func
        self.args = args
        # 线程内发生未预期异常时返回的兜底结果（与正常结果同构）
        self.error_result = error_result

    def run(self):
        try:
            result = self.func(*self.args)
        except Exception as e:
            # 翻译函数内部已捕获所有异常，此分支仅兜底防线程静默死亡，
            # 否则界面会永远停留在"翻译中..."状态。
            log_exception("worker.run", e)
            result = self.error_result
        self.result_ready.emit(result)


class DeepTransApp(QObject):
    def __init__(self, args=None):
        super().__init__()
        self.args = args or argparse.Namespace(debug=False, no_tray=False)

        if self.args.debug:
            print("[DEBUG] Starting DeepTrans in debug mode")
            print(f"[DEBUG] Config file: {CONFIG_FILE}")

        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        app_icon = QIcon(icon_path())
        if not app_icon.isNull():
            self.app.setWindowIcon(app_icon)
        self.update_stylesheet()

        # Windows
        self.overlay = OverlayWindow()
        self.settings = SettingsWindow()
        self.about = AboutWindow()

        # Tray (--no-tray 或模块开关关闭时不创建托盘，隐藏全部入口)
        self.tray = None
        if ENABLE_TRAY and not self.args.no_tray:
            self.tray = TrayIcon(self)
            self.tray.show()

        # Connect Monitor Signals
        monitor.text_selected.connect(self.on_mech_trigger)
        monitor.ai_trigger.connect(self.on_ai_trigger)
        monitor.toggle_status.connect(self.on_monitor_toggle)
        monitor.copy_trigger.connect(self.overlay.copy_smart)
        monitor.settings_trigger.connect(self.show_settings)
        monitor.global_click.connect(self.on_global_click)

        # Connect Settings Signals
        self.settings.settings_saved.connect(self.on_settings_saved)

        # Connect Overlay Signals
        self.overlay.toggle_requested.connect(self.disable_monitoring)

        # Start Monitor
        monitor.start()
        monitor.setup_global_hotkeys()

        # Keep track of workers
        self.mech_worker = None
        self.ai_worker = None
        self.mech_worker_id = 0  # 用于区分新旧 Worker 结果
        self.ai_worker_id = 0
        self._mech_last_slot = None  # 最近一次连接的结果槽（lambda 引用，供 disconnect）
        self._ai_last_slot = None

        # Timer for global delay
        self.mech_timer = QTimer()
        self.mech_timer.setSingleShot(True)
        self.mech_timer.timeout.connect(self.process_mech_trigger)
        self.pending_text = ""

        # Check First Run / Missing Config
        self.check_setup()

    def update_stylesheet(self):
        self.app.setStyleSheet(get_stylesheet())

    def on_settings_saved(self):
        self.update_stylesheet()
        # Also force overlay to re-apply specific settings (like width, shadow) that are not just stylesheet
        self.overlay.apply_settings()
        # 快捷键可能已变更：清旧句柄并按新配置重注册（setup_global_hotkeys 内置清理逻辑）
        monitor.setup_global_hotkeys()

    def check_setup(self):
        # 1. Check Icon (Should have been handled by build/run, but double check)
        if not os.path.exists(icon_path()):
            # Try to generate it silently into the writable assets dir
            try:
                from utils.icon_gen import generate_icon
                target = os.path.join(app_dir(), "assets", "icon.ico")
                generate_icon(output_path=target)
                icon = QIcon(icon_path())
                if not icon.isNull() and self.tray is not None:
                    self.tray.setIcon(icon)
            except Exception as e:
                msg = f"Failed to generate icon: {e}"
                print(msg)
                log_error(msg)

        # 2. Check API Key(s): 任一引擎配置了密钥即可使用 AI 翻译
        has_key = bool(cfg.get("deepseek_api_key") or cfg.get("xiaomi_api_key"))
        if not has_key:
            QMessageBox.information(None, tr("setup_title"),
                                    tr("setup_msg"))
            self.show_settings()

    def _wait_worker(self, worker, timeout_ms=10000):
        """有界等待 Worker 结束；超时记录告警，避免带活跃线程退出。"""
        if worker is None or not worker.isRunning():
            return
        waited = 0
        while worker.isRunning() and waited < timeout_ms:
            worker.wait(200)
            waited += 200
        if worker.isRunning():
            log_warning(
                f"Worker still running after {timeout_ms}ms at exit; abandoning thread"
            )

    def run(self):
        try:
            exit_code = self.app.exec()
        finally:
            # 清理资源：先停监听器与热键，再等待 Worker 收尾
            monitor.stop()
            self._wait_worker(self.mech_worker)
            self._wait_worker(self.ai_worker)
        sys.exit(exit_code)

    def show_settings(self):
        self.settings.show()
        self.settings.activateWindow()

    def show_about(self):
        self.about.show_corner()

    def toggle_monitoring(self, enabled):
        monitor.enabled = enabled
        print(f"Monitoring: {enabled}")

    def disable_monitoring(self):
        monitor.enabled = False
        self.on_monitor_toggle(False)

    def on_monitor_toggle(self, enabled):
        # Sync tray state if toggled via hotkey
        if self.tray is None:
            if not enabled:
                self.overlay.hide()
            return
        self.tray.toggle_action.setChecked(enabled)
        self.tray.update_menu_style()
        if not enabled:
            self.overlay.hide()

    def on_mech_trigger(self, text):
        if not text:
            self.overlay.hide()
            return

        self.pending_text = text

        # Start timer with configured delay
        try:
            delay_ms = max(0, int(float(cfg.get("trigger_delay")) * 1000))
        except (ValueError, TypeError):
            delay_ms = 1000  # fallback to default
        self.mech_timer.start(delay_ms)

    def process_mech_trigger(self):
        text = self.pending_text
        if not text:
            return

        # Check if mechanical translation is enabled
        if not cfg.get("mech_trans_enabled"):
            return

        # Show overlay immediately with "..."
        self.overlay.update_mech_text(tr("mech_translating"), reset_ai=True)

        # Disconnect and abandon old worker (let it finish naturally)
        if self.mech_worker and self.mech_worker.isRunning():
            if self._mech_last_slot is not None:
                try:
                    self.mech_worker.result_ready.disconnect(self._mech_last_slot)
                except TypeError:
                    pass  # Already disconnected
            self._mech_last_slot = None

        # 增加 worker ID 以区分新旧结果
        self.mech_worker_id += 1
        current_id = self.mech_worker_id

        self.mech_worker = Worker(
            translator.mechanical_translate, text,
            error_result=(None, "Internal worker error"),
        )
        slot = lambda result: self.on_mech_result(result, current_id)  # noqa: E731
        self._mech_last_slot = slot
        self.mech_worker.result_ready.connect(slot)

        self.mech_worker.start()

    def on_mech_result(self, result_tuple, worker_id=None):
        # 丢弃过期 Worker 的结果
        if worker_id is not None and worker_id != self.mech_worker_id:
            return

        # 安全解包结果
        if not isinstance(result_tuple, tuple) or len(result_tuple) != 2:
            self.overlay.update_mech_text(None, "Internal error: invalid result format")
            return

        text, error = result_tuple
        self.overlay.update_mech_text(text, error, reset_ai=False)

    def on_ai_trigger(self, text):
        if not text:
            return

        # Ensure overlay is visible if it was hidden (e.g. mech trans disabled)
        if not self.overlay.isVisible():
            self.overlay.show_at_cursor()

        self.overlay.update_ai_text(tr("ai_thinking"))

        # Disconnect and abandon old worker (let it finish naturally)
        if self.ai_worker and self.ai_worker.isRunning():
            if self._ai_last_slot is not None:
                try:
                    self.ai_worker.result_ready.disconnect(self._ai_last_slot)
                except TypeError:
                    pass  # Already disconnected
            self._ai_last_slot = None

        # 增加 worker ID 以区分新旧结果
        self.ai_worker_id += 1
        current_id = self.ai_worker_id

        self.ai_worker = Worker(
            translator.ai_translate, text,
            error_result="AI Error: unexpected worker failure",
        )
        slot = lambda result: self._on_ai_result(result, current_id)  # noqa: E731
        self._ai_last_slot = slot
        self.ai_worker.result_ready.connect(slot)
        self.ai_worker.start()

    def _on_ai_result(self, result, worker_id=None):
        # 丢弃过期 Worker 的结果
        if worker_id is not None and worker_id != self.ai_worker_id:
            return
        self.overlay.update_ai_text(result)

    def on_global_click(self, x, y):
        if self.overlay.isVisible():
            # Check if click is outside overlay
            # x, y are global coordinates
            # overlay geometry is also global
            geo = self.overlay.geometry()
            if not geo.contains(x, y):
                self.overlay.hide()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="DeepTrans",
        description="DeepTrans - AI powered desktop translation assistant",
    )
    parser.add_argument("--config", metavar="PATH",
                        help="Path to config.json (default: alongside the program)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--no-tray", action="store_true",
                        help="Do not create the system tray icon")
    parser.add_argument("--portable", action="store_true",
                        help="Portable mode: always read/write config next to the program")
    args, extra = parser.parse_known_args(argv)
    if extra and args.debug:
        print(f"[DEBUG] Ignoring unknown arguments: {extra}")
    return args


if __name__ == "__main__":
    cli_args = parse_args(sys.argv[1:])
    app = DeepTransApp(cli_args)
    app.run()
