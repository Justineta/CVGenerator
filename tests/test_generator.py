import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import _path  # noqa: F401

from cvgenerator.generator import (
    construire_contexte,
    description_localisee,
    filtrer_projets,
    generer_docx,
)
from cvgenerator.models import Collaborateur, Projet, from_dict
from cvgenerator.storage import DataStore

DOSXTPL_DISPONIBLE = importlib.util.find_spec("docxtpl") is not None
PYTHON_DOCX_DISPONIBLE = importlib.util.find_spec("docx") is not None


def _exemple_collaborateur() -> Collaborateur:
    return from_dict(Collaborateur, json.loads(Path(
        Path(__file__).parent.parent / "examples" / "collaborateur_exemple.json"
    ).read_text(encoding="utf-8")))


def _exemple_projets() -> list[Projet]:
    return [from_dict(Projet, p) for p in json.loads(Path(
        Path(__file__).parent.parent / "examples" / "projets_exemple.json"
    ).read_text(encoding="utf-8"))]


class TestFiltrage(unittest.TestCase):
    def test_confidentiels_exclus_par_defaut(self):
        projets = _exemple_projets()
        refs = [p.reference for p in filtrer_projets(projets)]
        self.assertEqual(refs, ["PROJ-001"])

    def test_confidentiels_inclus_sur_demande(self):
        projets = _exemple_projets()
        refs = [p.reference for p in filtrer_projets(projets, inclure_confidentiels=True)]
        self.assertEqual(refs, ["PROJ-001", "PROJ-002"])

    def test_selection_par_reference(self):
        projets = _exemple_projets()
        refs = [p.reference for p in filtrer_projets(projets, references=["PROJ-002"], inclure_confidentiels=True)]
        self.assertEqual(refs, ["PROJ-002"])


class TestLocalisation(unittest.TestCase):
    def test_repli_langue_puis_fr(self):
        d = {"fr": "Bonjour", "en": "Hello"}
        self.assertEqual(description_localisee(d, "de"), "Bonjour")
        self.assertEqual(description_localisee(d, "en"), "Hello")

    def test_premiere_valeur_si_aucune_correspondance(self):
        self.assertEqual(description_localisee({"de": "Hallo"}, "en"), "Hallo")
        self.assertEqual(description_localisee({}, "en"), "")
        self.assertEqual(description_localisee("texte", "en"), "texte")


class TestContexte(unittest.TestCase):
    def test_contexte_complet(self):
        c = _exemple_collaborateur()
        projets = filtrer_projets(_exemple_projets())
        ctx = construire_contexte(c, projets, "en", {"profil": "Profile"})
        self.assertEqual(ctx["collaborateur"]["nom_complet"], "Jean Dupont")
        self.assertEqual(ctx["collaborateur"]["titre"], "Senior project management consultant")
        self.assertEqual(ctx["projets"][0]["description"], "Overhaul of the grant management information system.")
        self.assertEqual(ctx["langue"], "en")
        self.assertEqual(ctx["traductions"]["profil"], "Profile")
        self.assertTrue(ctx["date_generation"])


@unittest.skipUnless(DOSXTPL_DISPONIBLE and PYTHON_DOCX_DISPONIBLE, "docxtpl/python-docx non installés")
class TestRenduDocx(unittest.TestCase):
    def test_generation_docx_depuis_modele(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = DataStore(tmp)
            store.initialiser()
            c = _exemple_collaborateur()
            store.save_collaborateur(c)
            store.save_projets(_exemple_projets())

            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
            from make_sample_template import fabriquer_modele

            modele = fabriquer_modele(store.templates_dir / "modele_standard.docx")
            sortie = generer_docx(store, c.id, modele.name, "fr", inclure_confidentiels=False)
            self.assertTrue(sortie.is_file())
            with zipfile.ZipFile(sortie) as z:
                xml = z.read("word/document.xml").decode("utf-8")
            self.assertIn("Jean Dupont", xml)
            self.assertIn("PROJ-001", xml)
            self.assertNotIn("PROJ-002", xml)


if __name__ == "__main__":
    unittest.main()
