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
        
        # Diagnostic: Check for Streamlit static files
        import streamlit
        # In a frozen app, streamlit.__file__ might be pointing to a place inside the bundle.
        # We try to infer where 'static' should be.
        # Typically in PyInstaller one-file/one-dir: sys._MEIPASS/streamlit/static
        if getattr(sys, "frozen", False):
            base_sl_dir = os.path.join(sys._MEIPASS, "streamlit")
            static_index = os.path.join(base_sl_dir, "static", "index.html")
            print(f"Checking for Streamlit static files at: {static_index}")
            if os.path.exists(static_index):
                print(" -> SUCCESS: streamline/static/index.html found.")
            else:
                print(" -> ERROR: streamline/static/index.html NOT FOUND!")
                if os.path.exists(base_sl_dir):
                    print(f"    Contents of {base_sl_dir}: {os.listdir(base_sl_dir)}")
                    if os.path.exists(os.path.join(base_sl_dir, "static")):
                         print(f"    Contents of {os.path.join(base_sl_dir, 'static')}: {os.listdir(os.path.join(base_sl_dir, 'static'))}")
                else:
                    print(f"    Directory {base_sl_dir} does not exist.")
                    print(f"    Root _MEIPASS contents: {os.listdir(sys._MEIPASS)}")
        
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
