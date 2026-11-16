# Cahier des charges v1.0 — synthèse (octobre 2026)

Document de référence : `Cahier des Charges - Outil de Gestion et de Génération de CV / Dossiers de Compétences`.

## 1. Contexte et objectifs
Automatiser la production de CV et dossiers de compétences multilingues pour les appels d'offres :
gestion collaborateurs, gestion projets, génération multilingue, fonctionnement 100 % hors ligne.

## 2. Principes généraux
Application autonome, sans Internet, sans cloud, sans IA générative, indépendante de Microsoft 365.

## 3. Architecture générale
Trois exécutables : `GestionCollaborateur.exe`, `GestionProjets.exe`, `GenerateurCV.exe`.

## 4. Architecture des données
JSON : un fichier par collaborateur ; référentiel `Projets/Projets.json` maintenu centralement.

## 5. Données collaborateurs
Identité, expérience, diplômes, certifications, publications, compétences, langues, expériences projets.

## 6. Gestion des projets
Référence, client, secteur, pays, dates, montants, descriptions multilingues, confidentialité.

## 7. Templates
DOCX, un template par client ; moteur `docxtpl` + Jinja2.

## 8. Multilingue
FR, EN, DE, NL, ES, IT ; traductions dans des fichiers JSON dédiés.

## 9. Génération
Sélection collaborateur + template + langue + projets ; export DOCX et PDF.

## 10. Sécurité
Hors ligne, compatible air-gap, aucun service externe.

## 11. Arborescence cible
`Collaborateurs/*.json`, `Projets/Projets.json`, `Templates/*.docx`, `Translations/*.json`, `Exports/`.

## 12. Technologies
Python, PySide6, docxtpl, Jinja2, python-docx, PyInstaller.

## 13. Critères de réception
Création/mise à jour des données ; génération correcte DOCX/PDF ; fonctionnement sans Internet ; 6 langues.

## Implémentation dans ce dépôt
| Exigence CdC | Où |
| --- | --- |
| §3 trois exécutables | `pyproject.toml [project.scripts]` + `specs/*.spec` (PyInstaller) |
| §4 données JSON | `cvgenerator/storage.py` (écriture atomique, `.bak`, audit) |
| §5–6 modèles | `cvgenerator/models.py`, `cvgenerator/validation.py` |
| §7 templates docxtpl | `cvgenerator/generator.py`, `tools/make_sample_template.py` |
| §8 6 langues | `src/cvgenerator/translations/*.json`, `tests/golden/contexte_*.json` |
| §9 DOCX/PDF | `generator.py` + `pdf.py` (LibreOffice headless) |
| §10 air-gap | aucun appel réseau à l'exécution ; voir `docs/INSTALLATION_AIRGAP.md` |
| §13 réception | `tests/` (unittest + golden 6 langues), CI `.github/workflows/tests.yml` |
