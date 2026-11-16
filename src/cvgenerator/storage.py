from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .models import Collaborateur, Projet, from_dict, to_dict
from .validation import valider_collaborateur, valider_projet

DOSSIERS_DONNEES = ("Collaborateurs", "Projets", "Templates", "Translations", "Exports", "Journaux")
FICHIER_PROJETS = "Projets.json"
FICHIER_JOURNAL = "audit.jsonl"


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

    @property
    def journaux_dir(self) -> Path:
        return self.root / "Journaux"

    @staticmethod
    def _lire_json(path: Path) -> dict | list:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _ecrire_json(path: Path, data) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            shutil.copyfile(path, path.with_name(path.name + ".bak"))
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

    def _journaliser(self, action: str, cible: str) -> None:
        self.journaux_dir.mkdir(parents=True, exist_ok=True)
        ligne = {
            "date": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "cible": cible,
        }
        with open(self.journaux_dir / FICHIER_JOURNAL, "a", encoding="utf-8") as f:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")

    def lire_journal(self) -> list[dict]:
        path = self.journaux_dir / FICHIER_JOURNAL
        if not path.is_file():
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(ligne) for ligne in f if ligne.strip()]

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
        erreurs = valider_collaborateur(collaborateur)
        if erreurs:
            raise ValueError("; ".join(erreurs))
        self._ecrire_json(self.collaborateurs_dir / f"{collaborateur.id}.json", to_dict(collaborateur))
        self._journaliser("save_collaborateur", collaborateur.id)

    def delete_collaborateur(self, id_collaborateur: str) -> None:
        path = self.collaborateurs_dir / f"{id_collaborateur}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Collaborateur introuvable: {id_collaborateur}")
        path.unlink()
        self._journaliser("delete_collaborateur", id_collaborateur)

    def charger_projets(self) -> list[Projet]:
        path = self.projets_dir / FICHIER_PROJETS
        if not path.is_file():
            return []
        return [from_dict(Projet, p) for p in self._lire_json(path)]

    def save_projets(self, projets: list[Projet]) -> None:
        for p in projets:
            erreurs = valider_projet(p)
            if erreurs:
                raise ValueError(f"{p.reference}: " + "; ".join(erreurs))
        self._ecrire_json(self.projets_dir / FICHIER_PROJETS, [to_dict(p) for p in projets])
        self._journaliser("save_projets", f"{len(projets)} projet(s)")

    def lister_modeles(self) -> list[str]:
        if not self.templates_dir.is_dir():
            return []
        return sorted(p.name for p in self.templates_dir.glob("*.docx"))
