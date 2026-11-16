from __future__ import annotations

import datetime
from pathlib import Path

from .i18n import charger_traductions
from .models import LANGUE_PAR_DEFAUT, Collaborateur, Projet, to_dict
from .storage import DataStore


def description_localisee(valeur, langue: str) -> str:
    """Retourne la traduction demandée, avec repli sur la langue par défaut puis sur la première valeur."""
    if not isinstance(valeur, dict):
        return valeur or ""
    if valeur.get(langue):
        return valeur[langue]
    if valeur.get(LANGUE_PAR_DEFAUT):
        return valeur[LANGUE_PAR_DEFAUT]
    for v in valeur.values():
        if v:
            return v
    return ""


def filtrer_projets(
    projets: list[Projet],
    references: list[str] | None = None,
    inclure_confidentiels: bool = False,
) -> list[Projet]:
    resultat = projets
    if references is not None:
        refs = set(references)
        resultat = [p for p in resultat if p.reference in refs]
    if not inclure_confidentiels:
        resultat = [p for p in resultat if not p.confidentiel]
    return sorted(resultat, key=lambda p: p.reference)


def construire_contexte(
    collaborateur: Collaborateur,
    projets: list[Projet],
    langue: str,
    traductions: dict,
) -> dict:
    return {
        "collaborateur": {
            "id": collaborateur.id,
            "nom_complet": collaborateur.nom_complet(),
            "nom": collaborateur.nom,
            "prenom": collaborateur.prenom,
            "email": collaborateur.email,
            "telephone": collaborateur.telephone,
            "adresse": collaborateur.adresse,
            "titre": description_localisee(collaborateur.titre, langue),
            "resume": description_localisee(collaborateur.resume, langue),
        },
        "diplomes": [to_dict(d) for d in collaborateur.diplomes],
        "certifications": [to_dict(c) for c in collaborateur.certifications],
        "publications": [to_dict(p) for p in collaborateur.publications],
        "competences": [to_dict(c) for c in collaborateur.competences],
        "langues": [to_dict(l) for l in collaborateur.langues],
        "experiences": [
            {**to_dict(e), "description": description_localisee(e.description, langue)}
            for e in collaborateur.experiences
        ],
        "projets": [
            {**to_dict(p), "description": description_localisee(p.description, langue)}
            for p in projets
        ],
        "missions": [to_dict(m) for m in collaborateur.projets],
        "langue": langue,
        "date_generation": datetime.date.today().isoformat(),
        "traductions": traductions,
    }


def generer_docx(
    store: DataStore,
    id_collaborateur: str,
    modele,
    langue: str,
    references: list[str] | None = None,
    inclure_confidentiels: bool = False,
    sortie: str | Path | None = None,
) -> Path:
    from docxtpl import DocxTemplate

    collaborateur = store.get_collaborateur(id_collaborateur)
    projets = filtrer_projets(store.charger_projets(), references, inclure_confidentiels)
    traductions = charger_traductions(store.translations_dir, langue)
    contexte = construire_contexte(collaborateur, projets, langue, traductions)

    modele_path = Path(modele)
    if not modele_path.is_absolute():
        modele_path = store.templates_dir / modele_path
    if not modele_path.is_file():
        raise FileNotFoundError(f"Modèle introuvable: {modele_path}")

    if sortie is None:
        sortie = store.exports_dir / f"{id_collaborateur}_{langue}.docx"
    sortie = Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)

    doc = DocxTemplate(str(modele_path))
    doc.render(contexte)
    doc.save(str(sortie))
    return sortie
