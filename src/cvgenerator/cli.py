from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import generer_docx
from .models import LANGUES
from .pdf import convertir_pdf
from .storage import DataStore


def _cmd_collaborateurs(store: DataStore, args) -> int:
    collaborateurs = store.lister_collaborateurs()
    if not collaborateurs:
        print("Aucun collaborateur.")
    for c in collaborateurs:
        print(f"{c.id}\t{c.nom_complet()}\t{c.email}")
    return 0


def _cmd_projets(store: DataStore, args) -> int:
    projets = store.charger_projets()
    if not projets:
        print("Aucun projet.")
    for p in projets:
        marque = " [confidentiel]" if p.confidentiel else ""
        print(f"{p.reference}\t{p.client}\t{p.pays}{marque}")
    return 0


def _cmd_generer(store: DataStore, args) -> int:
    references = [r.strip() for r in args.projets.split(",") if r.strip()] if args.projets else None
    sortie = Path(args.sortie) if args.sortie else None
    docx = generer_docx(
        store,
        args.collaborateur,
        args.modele,
        args.langue,
        references=references,
        inclure_confidentiels=args.confidentiels,
        sortie=sortie,
    )
    print(f"DOCX: {docx}")
    if args.pdf:
        pdf = convertir_pdf(docx, docx.parent)
        print(f"PDF: {pdf}")
    return 0


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cvgenerator",
        description="CVGenerator 100 % hors ligne (ligne de commande, air-gap compatible)",
    )
    parser.add_argument("--home", default=None, help="Dossier de données (défaut : CVGENERATOR_HOME ou dossier courant)")
    sub = parser.add_subparsers(dest="commande", required=True)

    sub.add_parser("collaborateurs", help="Lister les collaborateurs").set_defaults(func=_cmd_collaborateurs)
    sub.add_parser("projets", help="Lister le référentiel projets").set_defaults(func=_cmd_projets)

    p_gen = sub.add_parser("generer", help="Générer un CV en DOCX (et PDF avec --pdf)")
    p_gen.add_argument("--collaborateur", required=True)
    p_gen.add_argument("--modele", required=True, help="Nom du modèle dans Templates/")
    p_gen.add_argument("--langue", default="fr", choices=list(LANGUES))
    p_gen.add_argument("--projets", default=None, help="Références séparées par des virgules (défaut : tous les non confidentiels)")
    p_gen.add_argument("--confidentiels", action="store_true", help="Inclure les projets confidentiels")
    p_gen.add_argument("--pdf", action="store_true", help="Convertir aussi en PDF via LibreOffice local")
    p_gen.add_argument("--sortie", default=None, help="Fichier de sortie (défaut : Exports/<id>_<langue>.docx)")
    p_gen.set_defaults(func=_cmd_generer)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construire_parser().parse_args(argv)
    store = DataStore(args.home) if args.home else DataStore.defaut()
    store.initialiser()
    try:
        return args.func(store, args)
    except Exception as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
