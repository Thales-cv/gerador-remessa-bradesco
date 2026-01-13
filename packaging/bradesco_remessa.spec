# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import copy_metadata
import streamlit

datas = [
    ('../app.py', '.'),
    ('../src', 'src'),
    ('../templates', 'templates'),
    ('../config.json', '.')
]

# Helper to safely copy metadata
# Helper to safely copy metadata
def safe_copy_metadata(package):
    try:
        return copy_metadata(package)
    except Exception:
        return []

from PyInstaller.utils.hooks import collect_all

# Collect all Streamlit data, binaries, and hidden imports
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]
binaries = tmp_ret[1]
hiddenimports = tmp_ret[2]

# Add other dependencies metadata
datas += safe_copy_metadata('tqdm')
datas += safe_copy_metadata('regex')
datas += safe_copy_metadata('requests')
datas += safe_copy_metadata('packaging')
datas += safe_copy_metadata('filelock')
datas += safe_copy_metadata('numpy')
datas += safe_copy_metadata('tokenizers')
datas += safe_copy_metadata('altair')
datas += safe_copy_metadata('pandas')
datas += safe_copy_metadata('pillow')
datas += safe_copy_metadata('pyarrow')
datas += safe_copy_metadata('rich')
datas += safe_copy_metadata('gitpython')
datas += safe_copy_metadata('pydeck')
datas += safe_copy_metadata('tornado')
datas += safe_copy_metadata('watchdog')

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BradescoRemessa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BradescoRemessa',
)
