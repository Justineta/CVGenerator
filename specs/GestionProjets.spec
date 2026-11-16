# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("cvgenerator", includes=["translations/*.json"])

a = Analysis(
    ["../src/cvgenerator/ui/gestion_projets.py"],
    pathex=["../src"],
    binaries=[],
    datas=datas,
    hiddenimports=["cvgenerator", "cvgenerator.models", "cvgenerator.storage", "cvgenerator.i18n"],
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
    name="GestionProjets",
    console=False,
)
