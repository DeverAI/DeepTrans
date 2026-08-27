from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QCoreApplication
from core.config import icon_path
from core.i18n import tr

# 模块开关：False 时完全隐藏托盘入口（demo/排查用），
# 运行时仍可通过命令行 --no-tray 临时关闭。
ENABLE_TRAY = True


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(icon_path()))
        self.setToolTip("DeepTrans")
        
        self.menu = QMenu()
        
        # Actions
        self.toggle_action = self.menu.addAction(tr("tray_enabled"))
        self.toggle_action.triggered.connect(self.on_toggle)
        self.toggle_action.setCheckable(True)
        self.toggle_action.setChecked(True)
        
        self.menu.addSeparator()
        
        self.settings_action = self.menu.addAction(tr("tray_settings"))
        self.settings_action.triggered.connect(parent.show_settings)
        
        self.about_action = self.menu.addAction(tr("tray_about"))
        self.about_action.triggered.connect(parent.show_about)
        
        self.menu.addSeparator()
        
        self.exit_action = self.menu.addAction(tr("tray_exit"))
        self.exit_action.triggered.connect(QCoreApplication.quit)
        
        self.setContextMenu(self.menu)
        self.update_menu_style()

    def on_toggle(self):
        # Logic is handled via connecting signals in main.py usually, 
        # or we call parent method.
        # But here we just emit signal or let parent handle.
        # Let's assume parent has 'toggle_monitoring' method.
        self.parent().toggle_monitoring(self.toggle_action.isChecked())
        self.update_menu_style()

    def update_menu_style(self):
        font = QFont()
        font.setPointSize(9) # Explicitly set size to avoid warning
        
        if self.toggle_action.isChecked():
            font.setBold(True)
            self.toggle_action.setFont(font)
            self.toggle_action.setText(tr("tray_enabled"))
            self.setIcon(QIcon(icon_path()))  # Normal icon
        else:
            font.setStrikeOut(True)
            font.setItalic(True)
            self.toggle_action.setFont(font)
            self.toggle_action.setText(tr("tray_paused"))
            # We could change icon to grayscale or something if we had one

    def show_message(self, title, msg):
        self.showMessage(title, msg, QSystemTrayIcon.MessageIcon.Information, 2000)
