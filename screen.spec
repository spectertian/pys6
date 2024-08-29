# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['8.py'],
    pathex=[],
    binaries=[],
    datas=[('icons/*', 'icons/'), ('screenshots/*', 'screenshots/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='screen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons\\link.png'],
)
import os
from PyInstaller.compat import is_win

if is_win:
    # 添加 Visual C++ Redistributable
    a.binaries += [
        ('msvcp140.dll', 'C:\\Windows\\System32\\msvcp140.dll', 'BINARY'),
        ('vcruntime140.dll', 'C:\\Windows\\System32\\vcruntime140.dll', 'BINARY'),
        # 如果需要，还可以添加其他版本，如 vcruntime140_1.dll
    ]