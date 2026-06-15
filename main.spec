# -*- mode: python ; coding: utf-8 -*-
import logging.config

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('alembic.ini', '.'),
        ('./db/alembic', './db/alembic')
    ],
    hiddenimports=['logging.config'],
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
    [],
    exclude_binaries=True,
    name='Controlo de Produção',
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
    contents_directory='.',
    icon=['ui\designer\images\logo-uartronica.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Controlo de Produção',
)
