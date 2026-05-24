# -*- mode: python ; coding: utf-8 -*-
# Build: scripts/build_kopano_context.ps1  (or: pyinstaller KopanoContext.spec --noconfirm --clean)

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

kopano_hidden = collect_submodules("kopano")
litellm_datas = collect_data_files("litellm")

added_files = [
    ("kopano-core/studio/dist", "studio/dist"),
    ("db/datalake.db", "db"),
] + litellm_datas

a = Analysis(
    ["kopano_desktop.py"],
    pathex=["kopano-core"],
    binaries=[],
    datas=added_files,
    hiddenimports=kopano_hidden
    + [
        "webview",
        "webview.platforms.winforms",
        "webview.platforms.edgechromium",
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "fastapi",
        "starlette.routing",
        "starlette.middleware.cors",
        "pydantic_settings",
        "email.mime.multipart",
        "email.mime.text",
        "anyio._backends._asyncio",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tkinter"],
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
    name="KopanoContext",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
