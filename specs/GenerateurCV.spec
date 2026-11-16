# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("cvgenerator", includes=["translations/*.json"])

a = Analysis(
    ["../src/cvgenerator/ui/generateur_cv.py"],
    pathex=["../src"],
    binaries=[],
    datas=datas,
    hiddenimports=["cvgenerator", "cvgenerator.models", "cvgenerator.storage", "cvgenerator.i18n", "cvgenerator.generator", "cvgenerator.pdf"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GenerateurCV",
    console=False,
)
