# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件 - 人口信息查询系统桌面端
Windows 打包配置

使用方法:
    pyinstaller build_windows.spec
"""

import os
import sys

block_cipher = None

# 获取当前目录
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))

# 分析入口文件
a = Analysis(
    ['main.py'],
    pathex=[SPEC_DIR],
    binaries=[],
    datas=[
        # 包含资源文件（如果有）
        # ('ui/*.png', 'ui'),
        # ('ui/*.ico', 'ui'),
        # ('data', 'data'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.dialects.sqlite',
        'pandas',
        'openpyxl',
        'PIL',
        'PIL.Image',
        'cryptography',
        'cryptography.fernet',
        'keyring',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy.f2py',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤重复文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='人口信息查询系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # 如果有图标文件
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='人口信息查询系统',
)
