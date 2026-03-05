# -*- mode: python ; coding: utf-8 -*-
# sigma_netmon.spec  – PyInstaller build specification

import sys
from pathlib import Path

SRC = Path("src")

block_cipher = None

a = Analysis(
    [str(SRC / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[
        # Include the resources folder if it exists
        ("resources", "resources"),
    ],
    hiddenimports=[
        # PyQt6 extras
        "PyQt6.sip",
        "PyQt6.QtSvg",
        # pyqtgraph
        "pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt6",
        "pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt6",
        "pyqtgraph.imageview.ImageViewTemplate_pyqt6",
        # psutil
        "psutil._pswindows",
        # standard library
        "statistics",
        "socket",
        "subprocess",
        "csv",
        "json",
        "re",
        # optional
        "reportlab",
        "scapy",
        "netifaces",
        "winsound",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "unittest"],
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
    name="SigmaNetMon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icon (generate or add your .ico to resources/)
    # icon="resources/icon.ico",
    version_file=None,
    uac_admin=False,         # Set True if admin rights needed for raw sockets
    uac_uiaccess=False,
)
