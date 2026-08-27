from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QApplication, QGraphicsDropShadowEffect,
                             QTextEdit, QSizePolicy, QMessageBox, QSizeGrip)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor, QColor, QGuiApplication, QMouseEvent
import pyperclip
from core.config import cfg
from core.i18n import tr
from core.monitor import monitor

from core.errors import analyze_error

class OverlayWindow(QWidget):
    toggle_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Dragging state
        self.old_pos = None
        
        self.mech_text = ""
        self.ai_text = ""
        self.current_error = None
        
        self.init_ui()
        self.apply_settings()
        self.hide() # Ensure hidden by default

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # Margin for shadow

        # Fix QFont::setPointSize: Point size <= 0
        font = self.font()
        if font.pointSize() <= 0:
             font.setPointSize(10) # Default safe size
             self.setFont(font)

        self.container = QFrame()
        self.container.setObjectName("OverlayFrame")
        self.container_layout = QVBoxLayout(self.container)
        
        # Section 1: Mechanical
        self.mech_widget = QWidget()
        self.mech_layout = QVBoxLayout(self.mech_widget)
        self.mech_layout.setContentsMargins(0, 0, 0, 0)
        
        self.mech_header = QHBoxLayout()
        
        # Alert Icon (Top-Left) - Hidden by default
        self.alert_btn = QPushButton("⚠️")
        self.alert_btn.setFixedSize(32, 32) # Larger for visibility
        self.alert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.alert_btn.setStyleSheet("""
            QPushButton { 
                font-size: 20px; 
                color: #FFA500; 
                border: none; 
                background: rgba(255, 255, 255, 0.9);
                border-radius: 16px;
            }
            QPushButton:hover {
                background: #FFF3E0;
            }
        """)
        self.alert_btn.clicked.connect(self.show_error_details)
        self.alert_btn.hide()
        self.mech_header.addWidget(self.alert_btn)

        self.mech_title = QLabel(tr("mech_title"))
        self.mech_title.setObjectName("SectionTitle")
        
        self.copy_mech_btn = QPushButton(tr("copy"))
        self.copy_mech_btn.setFixedSize(80, 28) 
        self.copy_mech_btn.setStyleSheet("font-size: 12px;") # Smaller font for Chinese
        self.copy_mech_btn.clicked.connect(lambda: self.copy_text(self.mech_text))
        
        # Toggle/Close Button (Red X)
        self.toggle_btn = QPushButton("✕")
        self.toggle_btn.setObjectName("ErrorButton")
        self.toggle_btn.setFixedSize(24, 24)
        self.toggle_btn.setToolTip(tr("toggle_shortcut")) 
        self.toggle_btn.clicked.connect(self.request_toggle_off)
        
        self.mech_header.addWidget(self.mech_title)
        self.mech_header.addStretch()
        self.mech_header.addWidget(self.copy_mech_btn)
        self.mech_header.addWidget(self.toggle_btn)
        self.mech_layout.addLayout(self.mech_header)

        self.mech_edit = QTextEdit()
        self.mech_edit.setReadOnly(True)
        self.mech_edit.setObjectName("TranslationText")
        self.mech_edit.setFixedHeight(80) 
        self.mech_layout.addWidget(self.mech_edit)
        
        self.container_layout.addWidget(self.mech_widget)

        # Section 2: AI (Initially Hidden)
        self.ai_widget = QWidget()
        self.ai_layout = QVBoxLayout(self.ai_widget)
        self.ai_layout.setContentsMargins(0, 10, 0, 0) # Top margin separator
        
        self.ai_header = QHBoxLayout()
        self.ai_title = QLabel(tr("ai_title"))
        self.ai_title.setObjectName("SectionTitle")
        
        self.copy_ai_btn = QPushButton(tr("copy"))
        self.copy_ai_btn.setFixedSize(80, 28)
        self.copy_ai_btn.setStyleSheet("font-size: 12px;") # Smaller font
        self.copy_ai_btn.setObjectName("PrimaryButton")
        self.copy_ai_btn.clicked.connect(lambda: self.copy_text(self.ai_text))
        
        self.ai_header.addWidget(self.ai_title)
        self.ai_header.addStretch()
        self.ai_header.addWidget(self.copy_ai_btn)
        self.ai_layout.addLayout(self.ai_header)

        self.ai_edit = QTextEdit()
        self.ai_edit.setReadOnly(True)
        self.ai_edit.setObjectName("AIText")
        self.ai_edit.setMinimumHeight(100)
        self.ai_layout.addWidget(self.ai_edit)
        
        self.ai_widget.hide()
        self.container_layout.addWidget(self.ai_widget)
        
        # Add Resize Grip to Container (Bottom-Right)
        # We need a layout that allows putting the grip at the bottom right
        self.grip_layout = QHBoxLayout()
        self.grip_layout.addStretch()
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(20, 20)
        # Make grip transparent or subtle? Default is usually dots.
        self.grip_layout.addWidget(self.size_grip)
        self.container_layout.addLayout(self.grip_layout)
        # Remove margins for grip layout to sit tight
        self.grip_layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.container)
        
        # Set initial width but allow resizing
        self.resize(cfg.get("overlay_width"), 200) 

    # Implement Dragging
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None

    def copy_text(self, text):
        if not text:
            return
        
        # Tell monitor to ignore next clipboard change
        monitor.ignore_next_clipboard = True
        
        # Use QClipboard to set text
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)
        else:
            # Fallback to pyperclip
            pyperclip.copy(text)
        
        QTimer.singleShot(100, lambda: self.hide())

    def copy_smart(self):
        # Triggered by shortcut
        # Priority: AI text, then Mech text (error strings are not copyable results)
        ai_copyable = bool(self.ai_text) and not (
            self.ai_text.startswith("AI Error:") or self.ai_text.startswith("Error:")
        )
        mech_copyable = bool(self.mech_text)
        if ai_copyable:
             self.copy_text(self.ai_text)
        elif mech_copyable:
             self.copy_text(self.mech_text)

    def apply_settings(self):
        # Update Width (Use resize instead of setFixedWidth to allow manual resizing)
        current_height = self.height()
        target_width = cfg.get("overlay_width")
        self.resize(target_width, current_height)
        self.setMinimumWidth(300) # Ensure it doesn't get too small

        # Apply Shadow
        if cfg.get("window_shadow"):
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 0)
            self.container.setGraphicsEffect(shadow)
        else:
            self.container.setGraphicsEffect(None)

        # Opacity
        self.setWindowOpacity(cfg.get("window_opacity"))
        
        # Colors
        theme_color = cfg.get("theme_color") # Blue
        text_color = cfg.get("text_color")   # Black
        bg_color = cfg.get("ui_bg_color")    # White
        
        # Simple contrast check
        # If text is too close to bg, force black/white
        # (This is a basic check, can be improved)
        
        self.container.setStyleSheet(f"""
            QFrame#OverlayFrame {{
                background-color: {bg_color};
                border-radius: {cfg.get("window_soft_edges")}px;
                border: 2px solid {theme_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QTextEdit {{
                background-color: transparent;
                color: {text_color};
                border: none;
            }}
            QPushButton {{
                color: {theme_color};
                border: 1px solid {theme_color};
                border-radius: 4px;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: {theme_color};
                color: {bg_color};
            }}
            QPushButton#ErrorButton {{
                border: none;
                color: #D32F2F; /* Always Red for X */
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton#ErrorButton:hover {{
                background-color: #FFEBEE;
                color: #B71C1C;
            }}
            QLabel#SectionTitle {{
                font-weight: bold; 
                font-size: 12px;
            }}
        """)
        
        # Update Titles (Language)
        self.mech_title.setText(tr("mech_title"))
        self.ai_title.setText(tr("ai_title"))
        self.copy_mech_btn.setText(tr("copy"))
        self.copy_ai_btn.setText(tr("copy"))

    def update_mech_text(self, text, error=None, reset_ai=True):
        # 空更新：未产生任何内容时不做状态重置，避免界面残留错位
        if not text and not error:
            return

        # Reset previous state
        self.current_error = None
        self.mech_edit.show()
        self.copy_mech_btn.show()
        self.alert_btn.hide()
        
        # 恢复机械翻译区域标题和布局状态
        self.mech_title.setText(tr("mech_title"))
        self.ai_title.show()  # 确保 AI 标题可见
        
        # Reset AI view only if requested (New translation flow)
        if reset_ai:
            self.ai_widget.hide()
            self.ai_text = ""
        
        if error:
            # Handle Error
            self.current_error = error
            self.mech_text = ""
            
            # Hide the text box and copy button for errors
            self.mech_edit.hide()
            self.copy_mech_btn.hide()
            
            # Show Alert Button
            self.alert_btn.show()
            
            # Adjust height (minimal since text is hidden)
            self.mech_edit.setFixedHeight(0)
            
        elif text:
            # Normal Text
            self.mech_text = text
            self.mech_edit.setText(text)
            self.mech_edit.setStyleSheet("") # Reset style
            
            # Adjust height
            doc_height = self.mech_edit.document().size().height()
            new_height = min(max(60, int(doc_height + 20)), 300) # Increased max height
            self.mech_edit.setFixedHeight(new_height)
            
        # Atomically update geometry to prevent off-screen drawing
        width = self.width()
        height = self.layout.sizeHint().height()
        x, y = self.calculate_pos(width, height)
        self.setGeometry(x, y, width, height)
        self.show()
        self.raise_()
        self.activateWindow()

    def show_error_details(self):
        if not self.current_error:
            return
            
        friendly, detail = analyze_error(self.current_error)
        
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("err_title"))
        msg.setText(friendly)
        msg.setIcon(QMessageBox.Icon.Warning)
        
        # Add "Learn More" functionality
        msg.setDetailedText(detail)
        
        # Buttons
        close_btn = msg.addButton(tr("err_close"), QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()

    def update_ai_text(self, text):
        self.ai_text = text
        
        # Detect error strings from AI translation
        if text and (text.startswith("AI Error:") or text.startswith("Error:")):
            self.ai_edit.setStyleSheet("color: #D32F2F; font-style: italic;")
        else:
            self.ai_edit.setStyleSheet("")  # Reset to default
        
        self.ai_edit.setText(text)
        
        # Adjust AI height
        doc_height = self.ai_edit.document().size().height()
        new_height = min(max(100, int(doc_height + 20)), 500)
        self.ai_edit.setFixedHeight(new_height)
        
        # If mech translation is disabled, we need to hide the mech_widget parts
        # BUT we need to keep the close button visible which is in mech_header.
        # This is messy. Let's do a cleaner toggle.
        
        if not cfg.get("mech_trans_enabled"):
             # Hide mechanical text area
             self.mech_edit.hide()
             self.mech_edit.setFixedHeight(0)
             self.copy_mech_btn.hide()
             self.mech_title.setText(tr("ai_title")) # Reuse title space
             
             # Show AI widget, but maybe hide AI title since we used top title?
             self.ai_widget.show()
             self.ai_title.hide() # Hide redundant title
             # We might need the AI copy button though.
             
        else:
             # Normal Mode
             self.mech_edit.show()
             self.mech_title.setText(tr("mech_title"))
             self.copy_mech_btn.show()
             
             self.ai_widget.show()
             self.ai_title.show()

        # Atomically update geometry
        width = self.width()
        height = self.layout.sizeHint().height()
        x, y = self.calculate_pos(width, height)
        self.setGeometry(x, y, width, height)
        self.show()
        self.raise_()
        self.activateWindow()

    def calculate_pos(self, width, height):
        cursor_pos = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_pos)
        if not screen:
            screen = QGuiApplication.primaryScreen()
        if not screen:
            return 0, 0  # 极端情况
        
        geo = screen.availableGeometry()  # Use available geometry (excludes taskbar)
        
        # 确保窗口不超出屏幕
        width = min(width, geo.width() - 20)
        height = min(height, geo.height() - 20)
        
        # Padding
        PAD = 20
        
        # Default: Bottom Right of cursor
        x = cursor_pos.x() + PAD
        y = cursor_pos.y() + PAD 
        
        # 1. Horizontal Strategy
        # If too far right, move to Left of cursor
        if x + width > geo.right() - PAD:
            x = cursor_pos.x() - width - PAD
        
        # 2. Vertical Strategy
        # If too far down, move to Top of cursor
        if y + height > geo.bottom() - PAD:
            y = cursor_pos.y() - height - PAD
            
        # 3. Final Clamping (Safety Net)
        # Ensure it never goes off screen edges
        x = max(geo.left() + 5, min(x, geo.right() - width - 5))
        y = max(geo.top() + 5, min(y, geo.bottom() - height - 5))
        
        return x, y

    def show_at_cursor(self):
        x, y = self.calculate_pos(self.width(), self.height())
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()





    def request_toggle_off(self):
        self.toggle_requested.emit()



    def focusOutEvent(self, event):
        super().focusOutEvent(event)
