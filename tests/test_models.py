import unittest

import _path  # noqa: F401

from cvgenerator.models import (
    LANGUES,
    Collaborateur,
    Competence,
    NiveauCompetence,
    Projet,
    from_dict,
    to_dict,
    valider_id,
)


class TestModeles(unittest.TestCase):
    def test_langues_cdc(self):
        self.assertEqual(LANGUES, ("fr", "en", "de", "nl", "es", "it"))

    def test_valider_id(self):
        self.assertTrue(valider_id("dupont-jean"))
        self.assertTrue(valider_id("a1"))
        self.assertFalse(valider_id(""))
        self.assertFalse(valider_id("../etc"))
        self.assertFalse(valider_id("Espace Ici"))

    def test_aller_retour_collaborateur(self):
        donnees = {
            "id": "dupont-jean",
            "nom": "Dupont",
            "prenom": "Jean",
            "titre": {"fr": "Consultant", "en": "Consultant"},
            "competences": [{"domaine": "Gestion de projet", "niveau": "expert"}],
            "experiences": [
                {"entreprise": "Exemple", "poste": "Chef de projet", "debut": "2020-01", "fin": None,
                 "description": {"fr": "Pilotage"}}
            ],
            "projets": [{"reference": "PROJ-001", "role": "Chef de projet", "periode": "2020-2023"}],
        }
        c = from_dict(Collaborateur, donnees)
        self.assertEqual(c.nom_complet(), "Jean Dupont")
        self.assertIsInstance(c.competences[0], Competence)
        self.assertEqual(c.competences[0].niveau, NiveauCompetence.EXPERT)
        self.assertIsNone(c.experiences[0].fin)
        aller_retour = to_dict(c)
        c2 = from_dict(Collaborateur, aller_retour)
        self.assertEqual(c2, c)

    def test_aller_retour_projet(self):
        p = from_dict(Projet, {
            "reference": "PROJ-001",
            "client": "Client X",
            "montant": 1000.5,
            "description": {"fr": "Desc", "en": "Desc EN"},
            "confidentiel": True,
        })
        self.assertTrue(p.confidentiel)
        self.assertEqual(p.montant, 1000.5)
        p2 = from_dict(Projet, to_dict(p))
        self.assertEqual(p2, p)


if __name__ == "__main__":
    unittest.main()
