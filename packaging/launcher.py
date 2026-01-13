import sys
import os
import streamlit.web.cli as stcli

import traceback

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    try:
        print("Initializing Bradesco Remessa App...")
        # Point to the internal app.py
        app_path = resolve_path("app.py")
        print(f"Target App Path: {app_path}")
        
        if not os.path.exists(app_path):
             print(f"ERROR: app.py not found at {app_path}")
             # List dir to debug
             print(f"Contents of base dir: {os.listdir(os.path.dirname(app_path))}")
        
        sys.argv = [
            "streamlit",
            "run",
            app_path,
            "--global.developmentMode=false",
        ]
        sys.exit(stcli.main())
    except Exception as e:
        print("\nCRITICAL ERROR:")
        traceback.print_exc()
        print("\n" + "="*60)
        print("Por favor, tire um print desta tela e envie para o desenvolvedor.")
        print("Please take a screenshot of this screen.")
        print("="*60 + "\n")
        input("Pressione ENTER para fechar / Press ENTER to exit...")
