from core.config import cfg

def get_stylesheet():
    theme_color = cfg.get("theme_color")
    
    # We can inject variables here
    return f"""
QWidget {{
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}}

QFrame#OverlayFrame {{
    background-color: rgba(255, 255, 255, 245);
    border-radius: 10px;
    border: 1px solid #E0E0E0;
}}

QTextEdit {{
    background-color: transparent;
    border: none;
    color: #333333;
    padding: 5px;
}}

QTextEdit#AIText {{
    color: #1a1a1a;
    font-weight: bold;
    background-color: rgba(0, 0, 0, 0.03); /* Slight background for AI */
    border-radius: 5px;
}}

QPushButton {{
    background-color: #E0E0E0;
    border: 1px solid #C0C0C0;
    border-radius: 4px;
    padding: 6px 12px;
    color: #333;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: #D0D0D0;
}}

QPushButton#PrimaryButton {{
    background-color: {theme_color};
    color: white;
    border: none;
}}

QPushButton#PrimaryButton:hover {{
    background-color: {theme_color}; /* Maybe darken slightly in code or use opacity */
    opacity: 0.9;
}}

QPushButton#ErrorButton {{
    background-color: transparent;
    color: #D32F2F;
    border: none;
    font-weight: bold;
    font-size: 16px;
    padding: 0px;
}}

QPushButton#ErrorButton:hover {{
    background-color: rgba(211, 47, 47, 0.1);
    border-radius: 12px;
}}

QToolTip {{
    background-color: #f0f0f0;
    color: #333;
    border: 1px solid #ccc;
}}
"""

