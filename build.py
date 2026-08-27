import PyInstaller.__main__
import os
import shutil

def build():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, "main.py")
    icon_path = os.path.join(base_dir, "assets", "icon.ico")
    dist_dir = os.path.join(base_dir, "dist")
    work_dir = os.path.join(base_dir, "build")
    
    # Ensure icon exists
    if not os.path.exists(icon_path):
        print("Generating icon...")
        from utils.icon_gen import generate_icon
        generate_icon(output_path=icon_path)

    # PyInstaller arguments
    args = [
        main_script,
        '--name=DeepTrans',
        '--onefile',
        '--noconsole',  # Hide CMD
        f'--icon={icon_path}',
        '--clean',
        '--add-data=assets;assets', # Include assets folder
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
        '--hidden-import=PIL',
        # 环境中同时存在 PyQt5（第三方依赖带入），PyInstaller 不允许多 Qt 绑定共存
        '--exclude-module=PyQt5',
        '--exclude-module=pyqt5',
    ]
    
    print(f"Building with args: {args}")
    
    try:
        PyInstaller.__main__.run(args)
        print("Build successful!")
        print(f"Executable is located at: {os.path.join(dist_dir, 'DeepTrans.exe')}")
    except Exception as e:
        print(f"Build failed: {e}")

if __name__ == "__main__":
    build()
