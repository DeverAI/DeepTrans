import argparse
import json
import os
import re
import sys
import tempfile

from utils.errlog import log_error, log_warning


# ---------------------------------------------------------------------------
# 路径解析
#
# 设计目标：
# - 开发环境：无论从哪个工作目录启动，配置/日志/资源都定位到仓库根目录；
# - PyInstaller 单文件打包：可写文件（config.json、Err.log）固定在 exe
#   所在目录，只读资源（assets/）优先从 sys._MEIPASS 解包目录读取。
# ---------------------------------------------------------------------------

def app_dir():
    """可写数据目录：开发环境为仓库根目录，冻结后为 exe 所在目录。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_dir():
    """只读资源目录：冻结时为 PyInstaller 解包目录，否则等于 app_dir()。"""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", app_dir())
    return app_dir()


def default_config_path():
    return os.path.join(app_dir(), "config.json")


def icon_path():
    """返回存在的图标绝对路径（先解包目录，后程序目录）。"""
    candidates = [
        os.path.join(resource_dir(), "assets", "icon.ico"),
        os.path.join(app_dir(), "assets", "icon.ico"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]


def _resolve_config_path_from_argv():
    """导入期解析命令行中的 --config/--portable，使配置路径在任何模块
    创建 cfg 实例之前就已确定（对 import 顺序不敏感）。"""
    argv = sys.argv[1:] if isinstance(getattr(sys, "argv"), list) else []
    if not argv:
        return None
    parser = argparse.ArgumentParser(prog="DeepTrans", add_help=False)
    parser.add_argument("--config", default=None)
    parser.add_argument("--portable", action="store_true")
    try:
        ns, _extra = parser.parse_known_args(argv)
    except SystemExit:
        return None
    if ns.config:
        return os.path.abspath(os.path.expanduser(ns.config))
    if ns.portable:
        # 便携模式：始终读写程序旁边的配置文件
        return os.path.join(app_dir(), "config.json")
    return None


CONFIG_FILE = _resolve_config_path_from_argv() or default_config_path()


def set_config_file(path):
    """显式覆盖配置文件路径（必须在首次创建 cfg 之前调用才有效）。"""
    global CONFIG_FILE
    CONFIG_FILE = os.path.abspath(os.path.expanduser(path))


# ---------------------------------------------------------------------------
# 双 AI 引擎定义（均为 OpenAI 兼容 Chat Completions 接口）
# ---------------------------------------------------------------------------

AI_PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "api_key_field": "deepseek_api_key",
        "default_model": "chat",
        "models": {
            "chat": "deepseek-chat",
            "reasoner": "deepseek-reasoner",
        },
    },
    "xiaomi": {
        "label": "Xiaomi MiMo",
        "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "api_key_field": "xiaomi_api_key",
        "default_model": "mimo-v2.5",
        "models": {
            "mimo-v2.5": "mimo-v2.5",
            "mimo-v2.5-pro": "mimo-v2.5-pro",
            "mimo-v2-pro": "mimo-v2-pro",
        },
    },
}


def all_ai_model_ids():
    ids = set()
    for _pid, p in AI_PROVIDERS.items():
        ids.update(p["models"].keys())
    return ids


DEFAULT_CONFIG = {
    "deepseek_api_key": "",
    "xiaomi_api_key": "",
    "ai_provider": "xiaomi",          # deepseek | xiaomi
    "trigger_delay": 1.0,
    "shortcut_toggle": "ctrl+alt+t",
    "shortcut_copy_result": "ctrl+shift+c",
    "theme_color": "#3C6EF0",  # Blue (Buttons/Borders)
    "text_color": "#000000",   # Black (Text)
    "ui_bg_color": "#FFFFFF",  # White (Background)
    "source_lang": "en-US",
    "target_lang": "zh-CN",
    "mech_translator": "mymemory",  # google, mymemory
    "mech_fallback": True,
    "mech_ai_fallback": True,  # 机翻引擎全失败后，用当前 AI 引擎兜底翻译
    "overlay_width": 450,
    "ui_language": "zh",  # en, zh
    "window_opacity": 0.95,
    "window_shadow": True,
    "window_soft_edges": 10,
    "ai_prompt_style": "None",  # None, Native, Professional
    "ai_model": "mimo-v2.5",    # 必须属于当前引擎模型集，见 AI_PROVIDERS
    "auto_translate_enabled": True,
    "mech_trans_enabled": False  # Allow disabling mechanical translation entirely
}

# 配置值验证器
# 注意：isinstance(True, int) 在 Python 中为真，布尔键必须用 type() 精确判定，
# 否则手改 config.json 写入任意非布尔值会穿透校验并在 GUI 构造期崩溃。
def _is_bool(v):
    return type(v) is bool


def _is_str(v):
    # 字符串键（语言码/快捷键/密钥）：允许空串，但必须是字符串类型
    return isinstance(v, str)


VALIDATORS = {
    "trigger_delay": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 10,
    "overlay_width": lambda v: isinstance(v, int) and not isinstance(v, bool) and 200 <= v <= 2000,
    "window_opacity": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and 0.1 <= v <= 1.0,
    "window_soft_edges": lambda v: isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 50,
    "theme_color": lambda v: isinstance(v, str) and bool(re.match(r'^#[0-9A-Fa-f]{6}$', v)),
    "text_color": lambda v: isinstance(v, str) and bool(re.match(r'^#[0-9A-Fa-f]{6}$', v)),
    "ui_bg_color": lambda v: isinstance(v, str) and bool(re.match(r'^#[0-9A-Fa-f]{6}$', v)),
    "ai_provider": lambda v: v in AI_PROVIDERS,
    "ai_model": lambda v: v in all_ai_model_ids(),
    "ai_prompt_style": lambda v: v in ("None", "Native", "Professional"),
    "mech_translator": lambda v: v in ("google", "mymemory"),
    "ui_language": lambda v: v in ("en", "zh"),
    "mech_trans_enabled": _is_bool,
    "mech_fallback": _is_bool,
    "mech_ai_fallback": _is_bool,
    "window_shadow": _is_bool,
    "auto_translate_enabled": _is_bool,
    "source_lang": _is_str,
    "target_lang": _is_str,
    "shortcut_toggle": _is_str,
    "shortcut_copy_result": _is_str,
}


class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 验证并过滤无效配置
                    validated_config = self._validate_config(saved_config)
                    self.config.update(validated_config)
            except json.JSONDecodeError as e:
                msg = f"Error loading config: Invalid JSON format - {e}"
                print(msg)
                log_error(msg)
                self._backup_corrupted_config()
            except Exception as e:
                msg = f"Error loading config: {e}"
                print(msg)
                log_error(msg)

    def _validate_config(self, config):
        """验证配置值，过滤无效值"""
        validated = {}
        for key, value in config.items():
            if key in VALIDATORS:
                try:
                    if VALIDATORS[key](value):
                        validated[key] = value
                    else:
                        wmsg = f"Invalid value for '{key}': {value}, using default"
                        print(f"Warning: {wmsg}")
                        log_warning(wmsg)
                except Exception:
                    wmsg = f"Validation error for '{key}': {value}, using default"
                    print(f"Warning: {wmsg}")
                    log_warning(wmsg)
            else:
                validated[key] = value
        return validated

    def _backup_corrupted_config(self):
        """备份损坏的配置文件"""
        try:
            if os.path.exists(CONFIG_FILE):
                backup_path = CONFIG_FILE + ".corrupted"
                os.replace(CONFIG_FILE, backup_path)
                print(f"Corrupted config backed up to {backup_path}")
                log_warning(f"Corrupted config backed up to {backup_path}")
        except OSError as e:
            msg = f"Failed to backup corrupted config: {e}"
            print(msg)
            log_error(msg)

    def save(self):
        try:
            # Atomic write: write to temp file first, then rename
            dir_name = os.path.dirname(os.path.abspath(CONFIG_FILE))
            fd, tmp_path = tempfile.mkstemp(suffix='.tmp', dir=dir_name)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                # Rename is atomic on most filesystems
                os.replace(tmp_path, CONFIG_FILE)
            except Exception:
                # Clean up temp file on failure
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
        except Exception as e:
            msg = f"Error saving config: {e}"
            print(msg)
            log_error(msg)

    def get(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        # 验证配置值
        if key in VALIDATORS:
            try:
                if not VALIDATORS[key](value):
                    wmsg = f"Invalid value for '{key}': {value}"
                    print(f"Warning: {wmsg}")
                    log_warning(wmsg)
                    return False
            except Exception:
                wmsg = f"Validation error for '{key}': {value}"
                print(f"Warning: {wmsg}")
                log_warning(wmsg)
                return False
        self.config[key] = value
        self.save()
        return True

    def reset(self, keep_keys=("deepseek_api_key", "xiaomi_api_key")):
        """恢复默认配置；API 密钥默认保留，避免误清空导致必须重填。"""
        preserved = {}
        for k in keep_keys:
            v = self.config.get(k)
            if v:
                preserved[k] = v
        self.config = DEFAULT_CONFIG.copy()
        self.config.update(preserved)
        self.save()

    def provider(self):
        """当前 AI 引擎定义（含非法值兜底）。"""
        provider_id = self.get("ai_provider")
        if provider_id not in AI_PROVIDERS:
            provider_id = "xiaomi"
        return AI_PROVIDERS[provider_id]

    def resolve_ai_model(self):
        """返回 (provider_id, 实际请求用的模型名)；配置跨引擎错配时回落默认。"""
        provider_id = self.get("ai_provider")
        if provider_id not in AI_PROVIDERS:
            provider_id = "xiaomi"
        p = AI_PROVIDERS[provider_id]
        model_key = self.get("ai_model")
        if model_key not in p["models"]:
            if model_key:
                wmsg = (f"Model '{model_key}' not in provider '{provider_id}', "
                        f"fallback to '{p['default_model']}'")
                print(f"Warning: {wmsg}")
                log_warning(wmsg)
            model_key = p["default_model"]
        return provider_id, p["models"][model_key]


# Global instance
cfg = ConfigManager()
