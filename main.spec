# -*- mode: python ; coding: utf-8 -*-
# Akeno Downloader - PyInstaller spec (one-file exe)
# External next to exe: ffmpeg.exe, cookies.txt, YouTube_Downloads/, config.json

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
project_dir = Path(SPECPATH)

# UI theme assets only (not ffmpeg/cookies)
datas = [
    (str(project_dir / "Res"), "Res"),
]
datas += collect_data_files("customtkinter")

# yt-dlp: include YouTube stack + postprocessors, skip unrelated extractors when possible
yt_dlp_hidden = collect_submodules("yt_dlp.extractor.youtube")
yt_dlp_hidden += collect_submodules("yt_dlp.postprocessor")
yt_dlp_hidden += [
    "yt_dlp",
    "yt_dlp.compat",
    "yt_dlp.utils",
    "yt_dlp.cookies",
    "yt_dlp.networking",
    "yt_dlp.downloader",
    "yt_dlp.extractor.common",
    "yt_dlp.extractor.generic",
    "yt_dlp.extractor.youtube",
]

app_hidden = [
    "config_manager",
    "constants",
    "cookies",
    "downloader",
    "exceptions",
    "gui",
    "helpers",
    "network",
    "PIL",
    "PIL.Image",
]

# Drop heavy/unused packages to keep the exe smaller
excludes = [
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "pytest",
    "setuptools",
    "tkinter.test",
    "unittest",
    "lib2to3",
    "pydoc",
    "doctest",
]

a = Analysis(
    [str(project_dir / "main.py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=yt_dlp_hidden + app_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AkenoDownloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        "python313.dll",
        "python3.dll",
        "vcruntime140.dll",
        "vcruntime140_1.dll",
        "libcrypto-3.dll",
        "libssl-3.dll",
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / "Res" / "icon.ico"),
)
