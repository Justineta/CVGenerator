from __future__ import annotations

import json
from pathlib import Path

from .models import LANGUE_PAR_DEFAUT


def _lire(dossier: str | Path, langue: str) -> dict:
    path = Path(dossier) / f"{langue}.json"
    if not path.is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def charger_traductions(dossier: str | Path, langue: str) -> dict:
    """Charge les traductions d'une langue avec repli sur la langue par défaut."""
    fusion = _lire(dossier, LANGUE_PAR_DEFAUT)
    if langue != LANGUE_PAR_DEFAUT:
        fusion.update(_lire(dossier, langue))
    return fusion


def t(traductions: dict, cle: str, **kwargs) -> str:
    texte = traductions.get(cle, cle)
    if kwargs:
        return texte.format(**kwargs)
    return texte
