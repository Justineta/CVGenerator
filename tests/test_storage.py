import json
import tempfile
import unittest
from pathlib import Path

import _path  # noqa: F401

from cvgenerator.models import Collaborateur, Projet, from_dict, to_dict
from cvgenerator.storage import DataStore


class TestDataStore(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.store = DataStore(self._tmp.name)
        self.store.initialiser()

    def tearDown(self):
        self._tmp.cleanup()

    def test_initialiser_cree_arborescence_et_traductions(self):
        for nom in ("Collaborateurs", "Projets", "Templates", "Translations", "Exports"):
            self.assertTrue((Path(self._tmp.name) / nom).is_dir())
        for langue in ("fr", "en", "de", "nl", "es", "it"):
            self.assertTrue((self.store.translations_dir / f"{langue}.json").is_file())

    def test_crud_collaborateur(self):
        c = Collaborateur(id="dupont-jean", nom="Dupont", prenom="Jean")
        self.store.save_collaborateur(c)
        relu = self.store.get_collaborateur("dupont-jean")
        self.assertEqual(relu.nom, "Dupont")
        self.assertEqual([x.id for x in self.store.lister_collaborateurs()], ["dupont-jean"])
        self.store.delete_collaborateur("dupont-jean")
        self.assertEqual(self.store.lister_collaborateurs(), [])
        with self.assertRaises(FileNotFoundError):
            self.store.get_collaborateur("dupont-jean")

    def test_id_invalide_refuse(self):
        with self.assertRaises(ValueError):
            self.store.save_collaborateur(Collaborateur(id="../pirate"))

    def test_ecriture_atomique_json_valide(self):
        c = Collaborateur(id="a-b", nom="Nom", diplomes=[])
        self.store.save_collaborateur(c)
        brut = (self.store.collaborateurs_dir / "a-b.json").read_text(encoding="utf-8")
        donnees = json.loads(brut)
        self.assertEqual(donnees["id"], "a-b")
        self.assertEqual(from_dict(Collaborateur, donnees), c)
        self.assertEqual(list(self.store.collaborateurs_dir.glob("*.tmp")), [])

    def test_projets_aller_retour(self):
        projets = [
            Projet(reference="PROJ-001", client="Client A", confidentiel=False),
            Projet(reference="PROJ-002", client="Client B", confidentiel=True),
        ]
        self.store.save_projets(projets)
        relus = self.store.charger_projets()
        self.assertEqual(relus, projets)
        brut = json.loads((self.store.projets_dir / "Projets.json").read_text(encoding="utf-8"))
        self.assertEqual(len(brut), 2)

    def test_projets_absent_retourne_liste_vide(self):
        store2 = DataStore(Path(self._tmp.name) / "vide")
        self.assertEqual(store2.charger_projets(), [])
        self.assertEqual(store2.lister_collaborateurs(), [])

    def test_to_dict_json_serialisable(self):
        c = from_dict(Collaborateur, json.loads(json.dumps(to_dict(Collaborateur(id="x", nom="N")))))
        self.assertEqual(c.id, "x")


if __name__ == "__main__":
    unittest.main()
