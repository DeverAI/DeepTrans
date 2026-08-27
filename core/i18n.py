from core.config import cfg

TRANSLATIONS = {
    "en": {
        "settings_title": "DeepTrans Settings",
        "general_tab": "General",
        "behavior_tab": "Behavior",
        "appearance_tab": "Appearance",
        "translation_tab": "Translation",
        "save_close": "Save & Close",
        "pick_color": "Pick Color",

        "api_key": "DeepSeek API Key:",
        "xiaomi_key": "Xiaomi MiMo API Key:",
        "ai_provider": "AI Engine:",
        "ai_model": "AI Model:",
        "prompt_style": "Prompt Style:",
        "trigger_delay": "Trigger Delay (s):",
        "toggle_shortcut": "Toggle Shortcut:",
        "copy_shortcut": "Copy Shortcut:",
        "src_lang": "Source Language (or 'auto'):",
        "tgt_lang": "Target Language:",
        "mech_trans_enable": "Enable Mechanical Translation",
        "mech_trans": "Mechanical Translator:",
        "fallback": "Allow Fallback",
        "ai_fallback": "Fall back to AI when mechanical fails",
        "theme_color": "Theme Color:",
        "text_color": "Text Color:",
        "bg_color": "Background Color:",
        "opacity": "Opacity:",
        "shadow": "Window Shadow:",
        "soft_edges": "Soft Edges (Radius):",
        "overlay_width": "Window Width:",
        "ui_language": "Interface Language (Restart Required):",
        "restore_default": "Restore Defaults",
        "confirm_restore": "Are you sure you want to restore default settings?\n(API keys are kept.)",
        "restore_done": "Settings restored. Please restart the application for all changes to take effect.",

        "tray_enabled": "Enabled",
        "tray_paused": "Paused",
        "tray_settings": "Settings",
        "tray_about": "About",
        "tray_exit": "Exit",

        "mech_title": "Mechanical",
        "ai_title": "AI Translation",
        "copy": "Copy",

        "err_title": "Translation Error",
        "err_msg": "Mechanical translation failed.",
        "err_more": "More Details",
        "err_close": "Close",
        "err_lang_support": "Language not supported. Please check settings.",
        "err_network": "Network error. Please check your connection.",
        "err_timeout": "Request timed out.",
        "err_unknown": "Unknown error occurred.",

        "about_title": "About",
        "about_slogan": "Writing the future with AI",

        "setup_title": "DeepTrans Setup",
        "setup_msg": "Welcome to DeepTrans!\n\nPlease configure an API Key to enable AI translation.",

        "invalid_color_title": "Invalid Color",
        "invalid_color_msg": "Invalid color value: {value}\nExpected format: #RRGGBB",
        "invalid_input_title": "Invalid Input",
        "invalid_delay_msg": "Trigger delay must be a number between 0 and 10.\nGot: {value}",
        "lang_changed_msg": "Language changed. Please restart application.",
        "ai_thinking": "AI is thinking...",
        "mech_translating": "Translating...",
        "save_failed_msg": "Some settings were rejected and not saved:"
    },
    "zh": {
        "settings_title": "DeepTrans 设置",
        "general_tab": "常规",
        "behavior_tab": "行为",
        "appearance_tab": "外观",
        "translation_tab": "翻译",
        "save_close": "保存并关闭",
        "pick_color": "选择颜色",

        "api_key": "DeepSeek API 密钥:",
        "xiaomi_key": "小米 MiMo API 密钥:",
        "ai_provider": "AI 引擎:",
        "ai_model": "AI 模型:",
        "prompt_style": "提示词风格:",
        "trigger_delay": "触发延迟 (秒):",
        "toggle_shortcut": "开关快捷键:",
        "copy_shortcut": "复制快捷键:",
        "src_lang": "源语言 (或 'auto'):",
        "tgt_lang": "目标语言:",
        "mech_trans_enable": "启用机器翻译",
        "mech_trans": "机翻引擎:",
        "fallback": "允许自动降级 (Fallback)",
        "ai_fallback": "机翻失败时回落 AI 引擎",
        "theme_color": "主题颜色:",
        "text_color": "文字颜色:",
        "bg_color": "背景颜色:",
        "opacity": "不透明度:",
        "shadow": "窗口阴影:",
        "soft_edges": "柔化边缘 (圆角):",
        "overlay_width": "窗口宽度:",
        "ui_language": "界面语言 (需重启):",
        "restore_default": "恢复默认设置",
        "confirm_restore": "确定要恢复默认设置吗？\n（API 密钥将被保留。）",
        "restore_done": "设置已恢复。请重启程序以生效。",

        "tray_enabled": "启用中",
        "tray_paused": "已暂停",
        "tray_settings": "设置",
        "tray_about": "关于",
        "tray_exit": "退出",

        "mech_title": "机器翻译",
        "ai_title": "AI 翻译",
        "copy": "复制",

        "err_title": "翻译错误",
        "err_msg": "机器翻译失败。",
        "err_more": "详细信息",
        "err_close": "关闭",
        "err_lang_support": "语言不支持，请检查设置。",
        "err_network": "网络连接错误。",
        "err_timeout": "请求超时。",
        "err_unknown": "发生未知错误。",

        "about_title": "关于",
        "about_slogan": "携手AI书写未来",

        "setup_title": "DeepTrans 设置向导",
        "setup_msg": "欢迎使用 DeepTrans！\n\n请配置任一 AI 引擎的 API 密钥以启用 AI 翻译功能。",

        "invalid_color_title": "颜色值无效",
        "invalid_color_msg": "无效的颜色值：{value}\n正确格式应为：#RRGGBB",
        "invalid_input_title": "输入无效",
        "invalid_delay_msg": "触发延迟必须是 0 到 10 之间的数字。\n当前输入：{value}",
        "lang_changed_msg": "语言已更改，请重启程序后生效。",
        "ai_thinking": "AI 思考中...",
        "mech_translating": "翻译中...",
        "save_failed_msg": "以下设置未通过校验、未能保存："
    }
}


def tr(key):
    lang = cfg.get("ui_language")
    if lang not in TRANSLATIONS:
        lang = "zh"
    return TRANSLATIONS[lang].get(key, key)
