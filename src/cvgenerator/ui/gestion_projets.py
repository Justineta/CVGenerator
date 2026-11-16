from __future__ import annotations

import sys

from ..models import Projet
from ..storage import DataStore
from .crud import lancer


def main() -> None:
    store = DataStore.defaut()
    store.initialiser()

    def lister() -> list[Projet]:
        return store.charger_projets()

    def charger(reference: str) -> Projet:
        for p in store.charger_projets():
            if p.reference == reference:
                return p
        raise FileNotFoundError(f"Projet introuvable: {reference}")

    def enregistrer(projet: Projet) -> None:
        projets = [p for p in store.charger_projets() if p.reference != projet.reference]
        projets.append(projet)
        store.save_projets(projets)

    def supprimer(reference: str) -> None:
        store.save_projets([p for p in store.charger_projets() if p.reference != reference])

    lancer(
        "GestionProjets",
        Projet,
        "reference",
        lister=lister,
        charger=charger,
        enregistrer=enregistrer,
        supprimer=supprimer,
        etiquette=lambda p: f"{p.client} — {p.secteur} ({p.pays})",
    )


if __name__ == "__main__":
    sys.exit(main())
