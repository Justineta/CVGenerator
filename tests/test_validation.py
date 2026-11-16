import tempfile
import unittest

import _path  # noqa: F401

from cvgenerator.models import Collaborateur, Projet
from cvgenerator.storage import DataStore
from cvgenerator.validation import valider_collaborateur, valider_projet


class TestValidationCollaborateur(unittest.TestCase):
    def test_valide(self):
        c = Collaborateur(id="dupont-jean", nom="Dupont", prenom="Jean", email="jean.dupont@example.com")
        self.assertEqual(valider_collaborateur(c), [])

    def test_id_invalide(self):
        c = Collaborateur(id="../pirate", nom="X", prenom="Y")
        self.assertTrue(any("id invalide" in e for e in valider_collaborateur(c)))

    def test_nom_prenom_obligatoires(self):
        c = Collaborateur(id="a-b", nom="", prenom="")
        self.assertTrue(any("nom et prenom" in e for e in valider_collaborateur(c)))

    def test_email_invalide(self):
        c = Collaborateur(id="a-b", nom="X", prenom="Y", email="pas-un-email")
        self.assertTrue(any("email invalide" in e for e in valider_collaborateur(c)))

    def test_sous_objets(self):
        from cvgenerator.models import Competence, ExperiencePro, MissionProjet

        c = Collaborateur(
            id="a-b", nom="X", prenom="Y",
            competences=[Competence(domaine="")],
            experiences=[ExperiencePro(entreprise="", poste="")],
            projets=[MissionProjet(reference="")],
        )
        erreurs = valider_collaborateur(c)
        self.assertTrue(any("competences[0]" in e for e in erreurs))
        self.assertTrue(any("experiences[0]" in e for e in erreurs))
        self.assertTrue(any("projets[0]" in e for e in erreurs))


class TestValidationProjet(unittest.TestCase):
    def test_valide(self):
        self.assertEqual(valider_projet(Projet(reference="PROJ-001", montant=100.0)), [])

    def test_reference_invalide(self):
        self.assertTrue(valider_projet(Projet(reference="../x")))
        self.assertTrue(valider_projet(Projet(reference="")))

    def test_montant_negatif(self):
        self.assertTrue(any("montant" in e for e in valider_projet(Projet(reference="P-1", montant=-5))))


class TestValidationBrancheeDansLeStockage(unittest.TestCase):
    def test_save_collaborateur_invalide_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = DataStore(tmp)
            store.initialiser()
            with self.assertRaises(ValueError):
                store.save_collaborateur(Collaborateur(id="a-b", nom="", prenom=""))
            self.assertEqual(store.lister_collaborateurs(), [])

    def test_save_projets_invalide_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = DataStore(tmp)
            store.initialiser()
            with self.assertRaises(ValueError):
                store.save_projets([Projet(reference="PROJ-001", montant=-1)])
            self.assertEqual(store.charger_projets(), [])


if __name__ == "__main__":
    unittest.main()
