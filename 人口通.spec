# -*- mode: python ; coding: utf-8 -*-
import os

# ============================================================
# PyQt6 运行时 DLL 手工收集
# 背景：PyInstaller 的 PyQt6 hook 在本机（PyQt6 6.x + venv_build）
# 未把 Qt6/bin 下的 DLL 收进产物，导致打包后
# "DLL load failed while importing QtWidgets"。这里显式指定
# 运行必需的最小 DLL 集合与 plugins（platforms/qwindows.dll 必须）。
# venv_build 是仓库内打包专用虚拟环境；找不到时跳过（保持原行为）。
# ============================================================
_QT6_DIR = os.path.join(
    r'D:\luybqi\split\db-population-system-desktop',
    'venv_build', 'Lib', 'site-packages', 'PyQt6', 'Qt6',
)
_QT_BIN = os.path.join(_QT6_DIR, 'bin')
_QT_PLUGINS = os.path.join(_QT6_DIR, 'plugins')

_qt_datas = []

# Qt 核心 DLL（运行必需的最小集合）
_qt_required_dlls = [
    'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll', 'Qt6Network.dll',
    'Qt6Sql.dll', 'Qt6Xml.dll', 'Qt6DBus.dll', 'Qt6PrintSupport.dll',
    # VC 运行库 + 图形依赖
    'msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll',
    'vcruntime140.dll', 'vcruntime140_1.dll', 'concrt140.dll',
    'opengl32sw.dll', 'd3dcompiler_47.dll',
]
if os.path.isdir(_QT_BIN):
    for _f in _qt_required_dlls:
        _src = os.path.join(_QT_BIN, _f)
        if os.path.exists(_src):
            _qt_datas.append((_src, 'PyQt6/Qt6/bin'))

# Qt plugins：platforms(窗口平台)/imageformats(图片)/sqldrivers(sqlite)/tls(网络)
if os.path.isdir(_QT_PLUGINS):
    for _sub in ('platforms', 'imageformats', 'styles', 'iconengines', 'sqldrivers', 'tls'):
        _pdir = os.path.join(_QT_PLUGINS, _sub)
        if not os.path.isdir(_pdir):
            continue
        for _f in os.listdir(_pdir):
            _src = os.path.join(_pdir, _f)
            if os.path.isfile(_src):
                _qt_datas.append((_src, f'PyQt6/Qt6/plugins/{_sub}'))

_datas = [
    ('app.ico', '.'), ('window_icon.png', '.'), ('tray_icon.png', '.'),
    ('updates/version.json', 'updates'), ('network/version_config.json', 'network'),
    ('certs/server.crt', 'certs'), ('certs/client.crt', 'certs'), ('certs/client.key', 'certs'),
] + _qt_datas


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=_datas,
    hiddenimports=['PyQt6.sip', 'sqlalchemy.dialects.sqlite'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='人口通',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='人口通',
)
