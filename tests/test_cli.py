import io
import json
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import _path  # noqa: F401

from cvgenerator.cli import main
from cvgenerator.models import Collaborateur, Projet, from_dict
from cvgenerator.storage import DataStore

RACINE = Path(__file__).parent.parent


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = self._tmp.name
        store = DataStore(self.home)
        store.initialiser()
        c = from_dict(Collaborateur, json.loads((RACINE / "examples" / "collaborateur_exemple.json").read_text(encoding="utf-8")))
        store.save_collaborateur(c)
        store.save_projets([
            from_dict(Projet, p)
            for p in json.loads((RACINE / "examples" / "projets_exemple.json").read_text(encoding="utf-8"))
        ])

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["--home", self.home] + argv)
        return code, out.getvalue(), err.getvalue()

    def test_lister_collaborateurs(self):
        code, out, _ = self._run(["collaborateurs"])
        self.assertEqual(code, 0)
        self.assertIn("dupont-jean", out)
        self.assertIn("Jean Dupont", out)

    def test_lister_projets_avec_marque_confidentiel(self):
        code, out, _ = self._run(["projets"])
        self.assertEqual(code, 0)
        self.assertIn("PROJ-001", out)
        self.assertIn("PROJ-002", out)
        self.assertIn("[confidentiel]", out)

    def test_generer_docx_hors_confidentiels_par_defaut(self):
        sys.path.insert(0, str(RACINE / "tools"))
        from make_sample_template import fabriquer_modele

        store = DataStore(self.home)
        fabriquer_modele(store.templates_dir / "modele_standard.docx")
        sortie = Path(self.home) / "out" / "cv_en.docx"
        code, out, _ = self._run([
            "generer", "--collaborateur", "dupont-jean", "--modele", "modele_standard.docx",
            "--langue", "en", "--sortie", str(sortie),
        ])
        self.assertEqual(code, 0, out)
        self.assertTrue(sortie.is_file())
        with zipfile.ZipFile(sortie) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        self.assertIn("Jean Dupont", xml)
        self.assertIn("Senior project management consultant", xml)
        self.assertIn("PROJ-001", xml)
        self.assertNotIn("PROJ-002", xml)

    def test_generer_avec_confidentiels_sur_demande(self):
        sys.path.insert(0, str(RACINE / "tools"))
        from make_sample_template import fabriquer_modele

        store = DataStore(self.home)
        fabriquer_modele(store.templates_dir / "modele_standard.docx")
        sortie = Path(self.home) / "out" / "cv_fr.docx"
        code, _, _ = self._run([
            "generer", "--collaborateur", "dupont-jean", "--modele", "modele_standard.docx",
            "--langue", "fr", "--projets", "PROJ-001,PROJ-002", "--confidentiels",
            "--sortie", str(sortie),
        ])
        self.assertEqual(code, 0)
        with zipfile.ZipFile(sortie) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        self.assertIn("PROJ-002", xml)

    def test_generer_collaborateur_inconnu_retourne_2(self):
        code, _, err = self._run([
            "generer", "--collaborateur", "inconnu", "--modele", "modele_standard.docx",
        ])
        self.assertEqual(code, 2)
        self.assertIn("Erreur", err)


if __name__ == "__main__":
    unittest.main()
