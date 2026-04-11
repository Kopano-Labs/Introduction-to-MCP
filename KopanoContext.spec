# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define the data files to include
added_files = [
    ('kopano-core/studio/dist', 'studio/dist'),
    ('kopano-core/kopano', 'kopano'),
]

a = Analysis(
    ['main.py'],
    pathex=['kopano-core'],
    binaries=[],
    datas=added_files,
    hiddenimports=['uvicorn.protocols.http.httptools_impl', 'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.websockets.websockets_impl', 'uvicorn.protocols.websockets.wsproto_impl', 'uvicorn.lifespan.on', 'uvicorn.lifespan.off', 'email.mime.multipart', 'email.mime.text'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KopanoContext',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # Set to False for no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
