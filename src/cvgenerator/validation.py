from __future__ import annotations

import re

from .models import Collaborateur, Projet, valider_id

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_REFERENCE_REGEX = re.compile(r"^[\w][\w\-]*$", re.UNICODE)


def valider_collaborateur(c: Collaborateur) -> list[str]:
    erreurs: list[str] = []
    if not valider_id(c.id):
        erreurs.append(f"id invalide: {c.id!r}")
    if not c.nom.strip() or not c.prenom.strip():
        erreurs.append("nom et prenom sont obligatoires")
    if c.email and not _EMAIL_REGEX.match(c.email):
        erreurs.append(f"email invalide: {c.email!r}")
    for i, d in enumerate(c.diplomes):
        if not d.intitule.strip():
            erreurs.append(f"diplomes[{i}]: intitule obligatoire")
    for i, cert in enumerate(c.certifications):
        if not cert.nom.strip():
            erreurs.append(f"certifications[{i}]: nom obligatoire")
    for i, comp in enumerate(c.competences):
        if not comp.domaine.strip():
            erreurs.append(f"competences[{i}]: domaine obligatoire")
    for i, l in enumerate(c.langues):
        if not l.langue.strip():
            erreurs.append(f"langues[{i}]: langue obligatoire")
    for i, e in enumerate(c.experiences):
        if not e.entreprise.strip() or not e.poste.strip():
            erreurs.append(f"experiences[{i}]: entreprise et poste obligatoires")
    for i, m in enumerate(c.projets):
        if not m.reference.strip():
            erreurs.append(f"projets[{i}]: reference obligatoire")
    return erreurs


def valider_projet(p: Projet) -> list[str]:
    erreurs: list[str] = []
    if not p.reference.strip() or not _REFERENCE_REGEX.match(p.reference):
        erreurs.append(f"reference invalide: {p.reference!r}")
    if p.montant is not None and p.montant < 0:
        erreurs.append(f"montant négatif: {p.montant}")
    return erreurs
