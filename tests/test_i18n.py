import tempfile
import unittest
from pathlib import Path

import _path  # noqa: F401

from cvgenerator.i18n import charger_traductions, t
from cvgenerator.models import LANGUES
from cvgenerator.storage import DataStore


class TestI18n(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.store = DataStore(self._tmp.name)
        self.store.initialiser()

    def tearDown(self):
        self._tmp.cleanup()

    def test_six_langues_chargent(self):
        for langue in LANGUES:
            tr = charger_traductions(self.store.translations_dir, langue)
            self.assertIn("app_generateur_cv", tr)
            self.assertTrue(tr["app_generateur_cv"])

    def test_repli_sur_francais(self):
        tr = charger_traductions(self.store.translations_dir, "de")
        self.assertEqual(tr["nouveau"], "Neu")
        self.assertIn("profil", tr)

    def test_cle_inconnue_repli_sur_la_cle(self):
        tr = charger_traductions(self.store.translations_dir, "fr")
        self.assertEqual(t(tr, "cle_inexistante"), "cle_inexistante")

    def test_interpolation(self):
        tr = {"confirmation_suppression": "Supprimer {id} ?"}
        self.assertEqual(t(tr, "confirmation_suppression", id="abc"), "Supprimer abc ?")


if __name__ == "__main__":
    unittest.main()
