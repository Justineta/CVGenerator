from __future__ import annotations

import argparse
from pathlib import Path

MODELE_PAR_DEFAUT = "modele_standard.docx"


def fabriquer_modele(chemin: str | Path) -> Path:
    """Génère un modèle DOCX d'exemple contenant des balises Jinja2 (docxtpl)."""
    from docx import Document

    chemin = Path(chemin)
    doc = Document()
    doc.add_heading("{{ collaborateur.nom_complet }}", level=0)
    doc.add_paragraph(
        "{{ collaborateur.email }} | {{ collaborateur.telephone }} | {{ collaborateur.adresse }}"
    )
    doc.add_paragraph("{{ collaborateur.titre }}")

    doc.add_heading("{{ traductions.profil }}", level=1)
    doc.add_paragraph("{{ collaborateur.resume }}")

    doc.add_heading("{{ traductions.diplomes }}", level=1)
    doc.add_paragraph(
        "{% for d in diplomes %}{{ d.intitule }} — {{ d.etablissement }} ({{ d.annee }})\n{% endfor %}"
    )

    doc.add_heading("{{ traductions.certifications }}", level=1)
    doc.add_paragraph(
        "{% for c in certifications %}{{ c.nom }} — {{ c.organisme }} ({{ c.annee }})\n{% endfor %}"
    )

    doc.add_heading("{{ traductions.competences }}", level=1)
    doc.add_paragraph(
        "{% for c in competences %}{{ c.domaine }} ({{ c.niveau }})\n{% endfor %}"
    )

    doc.add_heading("{{ traductions.langues }}", level=1)
    doc.add_paragraph("{% for l in langues %}{{ l.langue }} : {{ l.niveau }}\n{% endfor %}")

    doc.add_heading("{{ traductions.experiences }}", level=1)
    doc.add_paragraph(
        "{% for e in experiences %}{{ e.poste }} — {{ e.entreprise }} ({{ e.debut }} - {{ e.fin }})\n"
        "{{ e.description }}\n{% endfor %}"
    )

    doc.add_heading("{{ traductions.projets }}", level=1)
    doc.add_paragraph(
        "{% for p in projets %}{{ p.reference }} — {{ p.client }} ({{ p.pays }})\n"
        "{{ p.description }}\n{% endfor %}"
    )

    doc.add_paragraph("{{ date_generation }} — {{ langue }}")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(chemin))
    return chemin


def main() -> None:
    parser = argparse.ArgumentParser(description="Crée un modèle DOCX d'exemple avec balises Jinja2.")
    parser.add_argument("sortie", nargs="?", default=MODELE_PAR_DEFAUT)
    args = parser.parse_args()
    chemin = fabriquer_modele(args.sortie)
    print(f"Modèle créé : {chemin}")


if __name__ == "__main__":
    main()
