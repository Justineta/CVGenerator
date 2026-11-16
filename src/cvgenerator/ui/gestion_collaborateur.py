from __future__ import annotations

import sys

from ..storage import DataStore
from .crud import lancer


def main() -> None:
    store = DataStore.defaut()
    store.initialiser()
    lancer(
        "GestionCollaborateur",
        __import__("cvgenerator.models", fromlist=["Collaborateur"]).Collaborateur,
        "id",
        lister=store.lister_collaborateurs,
        charger=store.get_collaborateur,
        enregistrer=store.save_collaborateur,
        supprimer=store.delete_collaborateur,
        etiquette=lambda c: c.nom_complet(),
    )


if __name__ == "__main__":
    sys.exit(main())
