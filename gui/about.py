from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from core.config import cfg
from core.i18n import tr

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setWindowTitle(tr("about_title"))
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("DeepTrans")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel(f"{cfg.provider()['label']} | {cfg.get('ai_model')}")
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        
        footer = QLabel(tr("about_slogan"))
        footer.setStyleSheet("font-style: italic; color: #888; margin-top: 10px;")
        layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)

    def show_corner(self):
        # Update text in case language changed
        self.setWindowTitle(tr("about_title"))
        
        # Show at bottom right corner of primary screen
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                geo.left() + geo.width() - self.width() - 20,
                geo.top() + geo.height() - self.height() - 20
            )
        self.show()
        self.raise_()
        self.activateWindow()
