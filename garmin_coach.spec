# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Garmin Running AI Coach.

Build command:
    pyinstaller garmin_coach.spec
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

# Collect all necessary packages
datas = []
hiddenimports = []
binaries = []

# Streamlit requires many data files and submodules
streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all('streamlit')
datas += streamlit_datas
binaries += streamlit_binaries
hiddenimports += streamlit_hiddenimports

# Plotly
plotly_datas, plotly_binaries, plotly_hiddenimports = collect_all('plotly')
datas += plotly_datas
binaries += plotly_binaries
hiddenimports += plotly_hiddenimports

# Altair
altair_datas, altair_binaries, altair_hiddenimports = collect_all('altair')
datas += altair_datas
binaries += altair_binaries
hiddenimports += altair_hiddenimports

# Google GenAI (new SDK)
try:
    datas += collect_data_files('google.genai')
    hiddenimports += collect_submodules('google.genai')
except Exception:
    pass

# Additional hidden imports
hiddenimports += [
    'garminconnect',
    'pandas',
    'numpy',
    'PIL',
    'dotenv',
    'pyarrow',
    'packaging',
    'pkg_resources',
    'pydeck',
    'validators',
    'gitdb',
    'watchdog',
    'tornado',
    'click',
    'toml',
    'cachetools',
    'protobuf',
    'google.protobuf',
    'google.auth',
    'google.api_core',
    'httpx',
    'httpcore',
    'anyio',
    'certifi',
    'charset_normalizer',
    'idna',
    'sniffio',
    'h11',
    'google.genai',
]

# Add application files
datas += [
    ('app.py', '.'),
    ('garmin_client.py', '.'),
    ('ai_coach.py', '.'),
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
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
    name='GarminRunningCoach',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=True,  # For macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GarminRunningCoach',
)

# For macOS .app bundle (optional)
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='GarminRunningCoach.app',
        icon=None,  # Add .icns icon path here if available
        bundle_identifier='com.garmin.runningcoach',
        info_plist={
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '1.0.0',
        },
    )
