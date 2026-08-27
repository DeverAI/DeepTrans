import re

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QCheckBox, QComboBox, QSlider,
                             QTabWidget, QPushButton, QFormLayout, QColorDialog,
                             QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

from core.config import AI_PROVIDERS, cfg
from core.i18n import tr


def _validate_color(color_str):
    """验证颜色值格式"""
    return isinstance(color_str, str) and bool(re.match(r'^#[0-9A-Fa-f]{6}$', color_str))


class SettingsWindow(QWidget):
    settings_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("settings_title"))
        self.setFixedSize(500, 680)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tabs
        self.tabs.addTab(self.create_general_tab(), tr("general_tab"))
        self.tabs.addTab(self.create_behavior_tab(), tr("behavior_tab"))
        self.tabs.addTab(self.create_appearance_tab(), tr("appearance_tab"))

        # Save Button
        btn_layout = QHBoxLayout()

        restore_btn = QPushButton(tr("restore_default"))
        restore_btn.clicked.connect(self.restore_defaults)

        save_btn = QPushButton(tr("save_close"))
        save_btn.clicked.connect(self.save_settings)

        btn_layout.addWidget(restore_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def restore_defaults(self):
        reply = QMessageBox.question(self, tr("restore_default"),
                                     tr("confirm_restore"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # API 密钥被保留，避免误清空导致所有引擎都必须重新填写
            cfg.reset(keep_keys=("deepseek_api_key", "xiaomi_api_key"))
            self.close()
            QMessageBox.information(self, tr("settings_title"), tr("restore_done"))

    def create_general_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        # AI Engine (provider switch: 切换时联动刷新模型下拉框)
        self.provider_combo = QComboBox()
        for pid, p in AI_PROVIDERS.items():
            self.provider_combo.addItem(p["label"], pid)
        current_provider = cfg.get("ai_provider")
        idx = self.provider_combo.findData(current_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        else:
            self.provider_combo.setCurrentIndex(0)  # fallback -> deepseek
        layout.addRow(tr("ai_provider"), self.provider_combo)

        # API Keys（两个引擎各自保留密钥，切换引擎无需重填）
        self.api_key_input = QLineEdit(cfg.get("deepseek_api_key"))
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow(tr("api_key"), self.api_key_input)

        self.xiaomi_key_input = QLineEdit(cfg.get("xiaomi_api_key"))
        self.xiaomi_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow(tr("xiaomi_key"), self.xiaomi_key_input)

        # AI Model（随引擎联动刷新选项）
        self.model_combo = QComboBox()
        self._reload_model_items(cfg.get("ai_model"))
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        layout.addRow(tr("ai_model"), self.model_combo)

        # Prompt Style
        self.prompt_style_combo = QComboBox()
        self.prompt_style_combo.setEditable(True)
        self.prompt_style_combo.addItems(["None", "Native", "Professional"])
        self.prompt_style_combo.setCurrentText(cfg.get("ai_prompt_style"))
        layout.addRow(tr("prompt_style"), self.prompt_style_combo)

        # Interface Language
        self.ui_lang_combo = QComboBox()
        # Add items with userData: (Label, Data)
        self.ui_lang_combo.addItem("English", "en")
        self.ui_lang_combo.addItem("简体中文", "zh")

        current_lang = cfg.get("ui_language")
        # Find index for current lang
        index = self.ui_lang_combo.findData(current_lang)
        if index >= 0:
            self.ui_lang_combo.setCurrentIndex(index)
        else:
            # Fallback
            if "zh" in str(current_lang).lower():
                self.ui_lang_combo.setCurrentIndex(1)  # zh
            else:
                self.ui_lang_combo.setCurrentIndex(0)  # en

        layout.addRow(tr("ui_language"), self.ui_lang_combo)

        return widget

    def _reload_model_items(self, preferred_model):
        """按当前选中的引擎刷新模型列表，尽量保持用户原选择。"""
        pid = self.provider_combo.currentData()
        provider = AI_PROVIDERS.get(pid, AI_PROVIDERS["deepseek"])
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItems(list(provider["models"].keys()))
        if preferred_model in provider["models"]:
            self.model_combo.setCurrentText(preferred_model)
        else:
            self.model_combo.setCurrentText(provider["default_model"])
        self.model_combo.blockSignals(False)

    def on_provider_changed(self):
        """切换引擎时：模型列表联动到该引擎的模型集。"""
        self._reload_model_items(self.model_combo.currentText())

    def create_behavior_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        # Trigger Delay
        self.delay_input = QLineEdit(str(cfg.get("trigger_delay")))
        layout.addRow(tr("trigger_delay"), self.delay_input)

        # Shortcuts
        self.toggle_shortcut = QLineEdit(cfg.get("shortcut_toggle"))
        layout.addRow(tr("toggle_shortcut"), self.toggle_shortcut)

        self.copy_shortcut = QLineEdit(cfg.get("shortcut_copy_result"))
        layout.addRow(tr("copy_shortcut"), self.copy_shortcut)

        # Languages
        self.src_lang = QLineEdit(cfg.get("source_lang"))
        layout.addRow(tr("src_lang"), self.src_lang)

        self.tgt_lang = QLineEdit(cfg.get("target_lang"))
        layout.addRow(tr("tgt_lang"), self.tgt_lang)

        # Enable Mechanical Translation
        self.mech_enable_cb = QCheckBox()
        self.mech_enable_cb.setChecked(bool(cfg.get("mech_trans_enabled")))
        layout.addRow(tr("mech_trans_enable"), self.mech_enable_cb)

        # Mechanical Translator
        self.translator_combo = QComboBox()
        self.translator_combo.addItems(["google", "mymemory"])
        self.translator_combo.setCurrentText(cfg.get("mech_translator"))
        layout.addRow(tr("mech_trans"), self.translator_combo)

        # Fallback
        self.fallback_cb = QCheckBox()
        self.fallback_cb.setChecked(bool(cfg.get("mech_fallback")))
        layout.addRow(tr("fallback"), self.fallback_cb)

        # AI Fallback (机翻全失败时用当前 AI 引擎兜底)
        self.ai_fallback_cb = QCheckBox()
        self.ai_fallback_cb.setChecked(bool(cfg.get("mech_ai_fallback")))
        layout.addRow(tr("ai_fallback"), self.ai_fallback_cb)

        return widget

    def create_appearance_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        # Theme Color (Buttons/Borders)
        self.color_input = QLineEdit(cfg.get("theme_color"))
        color_btn = QPushButton(tr("pick_color"))
        color_btn.clicked.connect(lambda: self.pick_color(self.color_input))
        color_row = QHBoxLayout()
        color_row.addWidget(self.color_input)
        color_row.addWidget(color_btn)
        layout.addRow(tr("theme_color"), color_row)

        # Text Color
        self.text_color_input = QLineEdit(cfg.get("text_color"))
        text_color_btn = QPushButton(tr("pick_color"))
        text_color_btn.clicked.connect(lambda: self.pick_color(self.text_color_input))
        text_color_row = QHBoxLayout()
        text_color_row.addWidget(self.text_color_input)
        text_color_row.addWidget(text_color_btn)
        layout.addRow(tr("text_color"), text_color_row)

        # Background Color
        self.bg_color_input = QLineEdit(cfg.get("ui_bg_color"))
        bg_color_btn = QPushButton(tr("pick_color"))
        bg_color_btn.clicked.connect(lambda: self.pick_color(self.bg_color_input))
        bg_color_row = QHBoxLayout()
        bg_color_row.addWidget(self.bg_color_input)
        bg_color_row.addWidget(bg_color_btn)
        layout.addRow(tr("bg_color"), bg_color_row)

        # Width
        self.width_input = QSlider(Qt.Orientation.Horizontal)
        self.width_input.setRange(400, 1200)  # Increased range
        self.width_input.setValue(cfg.get("overlay_width"))
        width_layout = QHBoxLayout()
        self.width_label = QLabel(str(cfg.get("overlay_width")))
        self.width_input.valueChanged.connect(lambda v: self.width_label.setText(str(v)))
        width_layout.addWidget(self.width_input)
        width_layout.addWidget(self.width_label)
        layout.addRow(tr("overlay_width"), width_layout)

        # Opacity
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(cfg.get("window_opacity") * 100))
        layout.addRow(tr("opacity"), self.opacity_slider)

        # Shadow
        self.shadow_cb = QCheckBox()
        self.shadow_cb.setChecked(bool(cfg.get("window_shadow")))
        layout.addRow(tr("shadow"), self.shadow_cb)

        # Soft Edges
        self.edges_slider = QSlider(Qt.Orientation.Horizontal)
        self.edges_slider.setRange(0, 30)
        self.edges_slider.setValue(cfg.get("window_soft_edges"))
        layout.addRow(tr("soft_edges"), self.edges_slider)

        return widget

    def pick_color(self, input_field):
        color = QColorDialog.getColor()
        if color.isValid():
            input_field.setText(color.name())

    def save_settings(self):
        # 验证颜色值
        for field, key, label in [
            (self.color_input, "theme_color", tr("theme_color")),
            (self.text_color_input, "text_color", tr("text_color")),
            (self.bg_color_input, "ui_bg_color", tr("bg_color"))
        ]:
            color = field.text().strip()
            if not _validate_color(color):
                QMessageBox.warning(self, tr("invalid_color_title"),
                    tr("invalid_color_msg").format(value=color or "(empty)"))
                return  # 不关闭窗口，让用户修正

        # General
        cfg.set("ai_provider", self.provider_combo.currentData())
        cfg.set("deepseek_api_key", self.api_key_input.text().strip())
        cfg.set("xiaomi_api_key", self.xiaomi_key_input.text().strip())
        cfg.set("ai_model", self.model_combo.currentText())
        cfg.set("ai_prompt_style", self.prompt_style_combo.currentText())

        old_lang = cfg.get("ui_language")
        # Use currentData() for language code
        new_lang = self.ui_lang_combo.currentData()
        cfg.set("ui_language", new_lang)

        # Behavior - 验证 delay 输入
        try:
            delay = float(self.delay_input.text())
            if delay < 0 or delay > 10:
                raise ValueError("Out of range")
            cfg.set("trigger_delay", delay)
        except ValueError:
            QMessageBox.warning(self, tr("invalid_input_title"),
                tr("invalid_delay_msg").format(value=self.delay_input.text()))
            return  # 不关闭窗口，让用户修正

        cfg.set("shortcut_toggle", self.toggle_shortcut.text())
        cfg.set("shortcut_copy_result", self.copy_shortcut.text())
        cfg.set("source_lang", self.src_lang.text())
        cfg.set("target_lang", self.tgt_lang.text())
        cfg.set("mech_trans_enabled", self.mech_enable_cb.isChecked())
        cfg.set("mech_translator", self.translator_combo.currentText())
        cfg.set("mech_fallback", self.fallback_cb.isChecked())
        cfg.set("mech_ai_fallback", self.ai_fallback_cb.isChecked())

        # Appearance
        cfg.set("theme_color", self.color_input.text())
        cfg.set("text_color", self.text_color_input.text())
        cfg.set("ui_bg_color", self.bg_color_input.text())
        cfg.set("overlay_width", self.width_input.value())
        cfg.set("window_opacity", self.opacity_slider.value() / 100.0)
        cfg.set("window_shadow", self.shadow_cb.isChecked())
        cfg.set("window_soft_edges", self.edges_slider.value())

        if old_lang != new_lang:
            QMessageBox.information(self, tr("settings_title"), tr("lang_changed_msg"))

        # 保存结果校验：被验证器拒绝的键向用户明确提示且不关闭窗口
        expected = {
            "ai_provider": self.provider_combo.currentData(),
            "ai_model": self.model_combo.currentText(),
            "ai_prompt_style": self.prompt_style_combo.currentText(),
            "trigger_delay": delay,
            "mech_translator": self.translator_combo.currentText(),
            "overlay_width": self.width_input.value(),
            "ui_language": new_lang,
        }
        failed = [k for k, v in expected.items() if cfg.get(k) != v]
        if failed:
            QMessageBox.warning(self, tr("invalid_input_title"),
                                f"{tr('save_failed_msg')}\n{', '.join(failed)}")
            return

        self.settings_saved.emit()
        self.close()
