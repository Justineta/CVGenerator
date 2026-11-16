from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any, Union, get_args, get_origin, get_type_hints

LANGUES = ("fr", "en", "de", "nl", "es", "it")
LANGUE_PAR_DEFAUT = "fr"

_ID_REGEX = re.compile(r"[a-z0-9][a-z0-9\-_]*")


def valider_id(valeur: str) -> bool:
    return bool(valeur) and _ID_REGEX.fullmatch(valeur) is not None


class NiveauLangue(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class NiveauCompetence(str, Enum):
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"
    EXPERT = "expert"


class Confidentialite(str, Enum):
    PUBLIC = "public"
    INTERNE = "interne"
    CONFIDENTIEL = "confidentiel"


def _convertir(annotation: Any, valeur: Any) -> Any:
    if valeur is None:
        return None
    origine = get_origin(annotation)
    if origine is list:
        (interieur,) = get_args(annotation) or (Any,)
        return [_convertir(interieur, v) for v in valeur]
    if origine is dict:
        args = get_args(annotation) or (Any, Any)
        return {k: _convertir(args[1], v) for k, v in valeur.items()}
    if origine is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return _convertir(args[0], valeur)
        return valeur
    if isinstance(annotation, type):
        if issubclass(annotation, Enum):
            return annotation(valeur)
        if is_dataclass(annotation):
            return from_dict(annotation, valeur)
        if annotation in (str, int, float, bool):
            return annotation(valeur)
    return valeur


def from_dict(cls: type, data: dict) -> Any:
    hints = get_type_hints(cls)
    kwargs = {}
    for f in fields(cls):
        if f.name in data:
            kwargs[f.name] = _convertir(hints.get(f.name, f.type), data[f.name])
    return cls(**kwargs)


def to_dict(obj: Any) -> dict:
    return asdict(obj)


@dataclass
class Diplome:
    intitule: str
    etablissement: str = ""
    annee: int | None = None
    pays: str = ""


@dataclass
class Certification:
    nom: str
    organisme: str = ""
    annee: int | None = None
    url: str = ""


@dataclass
class Publication:
    titre: str
    revue: str = ""
    annee: int | None = None
    doi: str = ""


@dataclass
class Competence:
    domaine: str
    niveau: NiveauCompetence = NiveauCompetence.INTERMEDIAIRE
    description: str = ""


@dataclass
class LangueParlee:
    langue: str
    niveau: NiveauLangue = NiveauLangue.B2


@dataclass
class ExperiencePro:
    entreprise: str
    poste: str
    debut: str = ""
    fin: str | None = None
    description: dict[str, str] = field(default_factory=dict)


@dataclass
class MissionProjet:
    reference: str
    role: str = ""
    periode: str = ""


@dataclass
class Collaborateur:
    id: str
    nom: str = ""
    prenom: str = ""
    email: str = ""
    telephone: str = ""
    adresse: str = ""
    titre: dict[str, str] = field(default_factory=dict)
    resume: dict[str, str] = field(default_factory=dict)
    diplomes: list[Diplome] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    competences: list[Competence] = field(default_factory=list)
    langues: list[LangueParlee] = field(default_factory=list)
    experiences: list[ExperiencePro] = field(default_factory=list)
    projets: list[MissionProjet] = field(default_factory=list)

    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}".strip()


@dataclass
class Projet:
    reference: str
    client: str = ""
    secteur: str = ""
    pays: str = ""
    debut: str = ""
    fin: str | None = None
    montant: float | None = None
    description: dict[str, str] = field(default_factory=dict)
    confidentiel: bool = False
