import json
import unittest
from pathlib import Path

import _path  # noqa: F401

from cvgenerator.generator import construire_contexte, filtrer_projets
from cvgenerator.models import LANGUES, Collaborateur, Projet, from_dict

RACINE = Path(__file__).parent.parent
GOLDEN = RACINE / "tests" / "golden"


def _donnees_exemple():
    c = from_dict(Collaborateur, json.loads((RACINE / "examples" / "collaborateur_exemple.json").read_text(encoding="utf-8")))
    projets = [
        from_dict(Projet, p)
        for p in json.loads((RACINE / "examples" / "projets_exemple.json").read_text(encoding="utf-8"))
    ]
    return c, projets


class TestGoldenParLangue(unittest.TestCase):
    """Le contexte de génération doit correspondre aux fichiers golden pour les 6 langues (CdC §13)."""

    def test_golden_existe_pour_chaque_langue(self):
        for langue in LANGUES:
            self.assertTrue((GOLDEN / f"contexte_{langue}.json").is_file(), f"golden manquant: {langue}")

    def test_contexte_identique_au_golden(self):
        c, projets = _donnees_exemple()
        projets = filtrer_projets(projets, inclure_confidentiels=True)
        for langue in LANGUES:
            golden = json.loads((GOLDEN / f"contexte_{langue}.json").read_text(encoding="utf-8"))
            ctx = construire_contexte(c, projets, langue, {})
            self.assertEqual(ctx["langue"], golden["langue"])
            self.assertEqual(ctx["collaborateur"]["nom_complet"], golden["nom_complet"], langue)
            self.assertEqual(ctx["collaborateur"]["titre"], golden["titre"], langue)
            self.assertEqual(ctx["collaborateur"]["resume"], golden["resume"], langue)
            self.assertEqual(
                {p["reference"]: p["description"] for p in ctx["projets"]},
                golden["projets"],
                langue,
            )


if __name__ == "__main__":
    unittest.main()
