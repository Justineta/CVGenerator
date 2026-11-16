from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _executable_libreoffice() -> str | None:
    for nom in ("soffice", "libreoffice"):
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    return None


def convertir_pdf(docx_path: str | Path, dossier_sortie: str | Path) -> Path:
    """Convertit un DOCX en PDF via LibreOffice en ligne de commande (hors ligne, air-gap compatible)."""
    exe = _executable_libreoffice()
    if exe is None:
        raise RuntimeError(
            "LibreOffice (soffice/libreoffice) est introuvable : impossible de produire le PDF hors ligne."
        )
    docx_path = Path(docx_path)
    dossier_sortie = Path(dossier_sortie)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [exe, "--headless", "--convert-to", "pdf", "--outdir", str(dossier_sortie), str(docx_path)],
        check=True,
        capture_output=True,
        timeout=120,
    )
    pdf = dossier_sortie / (docx_path.stem + ".pdf")
    if not pdf.is_file():
        raise RuntimeError(f"Échec de la conversion PDF pour {docx_path}")
    return pdf
