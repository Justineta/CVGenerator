from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from .models import Collaborateur, Projet, from_dict, to_dict, valider_id

DOSSIERS_DONNEES = ("Collaborateurs", "Projets", "Templates", "Translations", "Exports")
FICHIER_PROJETS = "Projets.json"


class DataStore:
    """Accès aux données JSON du déploiement (un dossier racine par installation)."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    @classmethod
    def defaut(cls) -> "DataStore":
        env = os.environ.get("CVGENERATOR_HOME")
        if env:
            return cls(Path(env))
        if getattr(sys, "frozen", False):
            return cls(Path(sys.executable).parent)
        return cls(Path.cwd())

    def initialiser(self) -> None:
        for nom in DOSSIERS_DONNEES:
            (self.root / nom).mkdir(parents=True, exist_ok=True)
        self._amorcer_traductions()

    def _amorcer_traductions(self) -> None:
        source = Path(__file__).parent / "translations"
        cible = self.translations_dir
        if any(cible.glob("*.json")):
            return
        for p in sorted(source.glob("*.json")):
            shutil.copyfile(p, cible / p.name)

    @property
    def collaborateurs_dir(self) -> Path:
        return self.root / "Collaborateurs"

    @property
    def projets_dir(self) -> Path:
        return self.root / "Projets"

    @property
    def templates_dir(self) -> Path:
        return self.root / "Templates"

    @property
    def translations_dir(self) -> Path:
        return self.root / "Translations"

    @property
    def exports_dir(self) -> Path:
        return self.root / "Exports"

    @staticmethod
    def _lire_json(path: Path) -> dict | list:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _ecrire_json(path: Path, data) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def lister_collaborateurs(self) -> list[Collaborateur]:
        if not self.collaborateurs_dir.is_dir():
            return []
        resultat = []
        for p in sorted(self.collaborateurs_dir.glob("*.json")):
            resultat.append(from_dict(Collaborateur, self._lire_json(p)))
        return resultat

    def get_collaborateur(self, id_collaborateur: str) -> Collaborateur:
        path = self.collaborateurs_dir / f"{id_collaborateur}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Collaborateur introuvable: {id_collaborateur}")
        return from_dict(Collaborateur, self._lire_json(path))

    def save_collaborateur(self, collaborateur: Collaborateur) -> None:
        if not valider_id(collaborateur.id):
            raise ValueError(f"Identifiant invalide: {collaborateur.id!r}")
        self._ecrire_json(self.collaborateurs_dir / f"{collaborateur.id}.json", to_dict(collaborateur))

    def delete_collaborateur(self, id_collaborateur: str) -> None:
        path = self.collaborateurs_dir / f"{id_collaborateur}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Collaborateur introuvable: {id_collaborateur}")
        path.unlink()

    def charger_projets(self) -> list[Projet]:
        path = self.projets_dir / FICHIER_PROJETS
        if not path.is_file():
            return []
        return [from_dict(Projet, p) for p in self._lire_json(path)]

    def save_projets(self, projets: list[Projet]) -> None:
        self._ecrire_json(self.projets_dir / FICHIER_PROJETS, [to_dict(p) for p in projets])

    def lister_modeles(self) -> list[str]:
        if not self.templates_dir.is_dir():
            return []
        return sorted(p.name for p in self.templates_dir.glob("*.docx"))
