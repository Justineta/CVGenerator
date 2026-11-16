# CVGenerator

Outil **100 % hors ligne** de gestion et de génération de CV / dossiers de compétences multilingues
pour les appels d'offres, conforme au cahier des charges v1.0 (octobre 2026) :

- application autonome, sans Internet, sans cloud, sans IA générative, indépendante de Microsoft 365 ;
- trois exécutables : `GestionCollaborateur.exe`, `GestionProjets.exe`, `GenerateurCV.exe` ;
- données en JSON (un fichier par collaborateur, référentiel `Projets/Projets.json` central) ;
- modèles DOCX par client rendus avec **docxtpl + Jinja2** ;
- 6 langues : FR, EN, DE, NL, ES, IT, traductions stockées dans des fichiers JSON dédiés ;
- export DOCX et PDF (conversion headless via LibreOffice, compatible air-gap).

Aucune dépendance externe n'est appelée à l'exécution : l'application fonctionne sans réseau.

## Arborescence

```
CVGenerator/
├── GestionCollaborateur.exe      # packaging PyInstaller (voir specs/)
├── GestionProjets.exe
├── GenerateurCV.exe
├── Collaborateurs/*.json        # un fichier par collaborateur
├── Projets/Projets.json          # référentiel projets central
├── Templates/*.docx              # un modèle par client (balises Jinja2)
├── Translations/*.json           # amorcé depuis le package (fr/en/de/nl/es/it)
└── Exports/                      # CV générés (DOCX/PDF)
```

En développement, le code source vit dans `src/cvgenerator/` et les données d'exécution sont
créées dans le dossier courant (ou `CVGENERATOR_HOME`, ou le dossier de l'exécutable packagé).

## Installation (poste de développement)

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Utilisation

```bash
GestionCollaborateur    # CRUD collaborateurs
GestionProjets          # CRUD du référentiel projets
GenerateurCV            # sélection collaborateur + modèle + langue + projets → DOCX/PDF
```

Modèle DOCX d'exemple (à placer dans `Templates/`) :

```bash
python tools/make_sample_template.py Templates/modele_standard.docx
```

Données de démonstration : copier `examples/collaborateur_exemple.json` dans `Collaborateurs/`
et `examples/projets_exemple.json` dans `Projets/Projets.json`.

## Génération hors ligne (API)

```python
from cvgenerator.storage import DataStore
from cvgenerator.generator import generer_docx
from cvgenerator.pdf import convertir_pdf

store = DataStore.defaut()
store.initialiser()
docx = generer_docx(store, "dupont-jean", "modele_standard.docx", "en",
                    references=["PROJ-001"], inclure_confidentiels=False)
pdf = convertir_pdf(docx, store.exports_dir)   # nécessite LibreOffice installé localement
```

Les projets marqués `confidentiel: true` sont **exclus par défaut** de tout CV généré.

## Packaging (air-gap)

```bash
pyinstaller specs/GestionCollaborateur.spec --distpath dist --workpath build
pyinstaller specs/GestionProjets.spec      --distpath dist --workpath build
pyinstaller specs/GenerateurCV.spec        --distpath dist --workpath build
```

Distribuer `dist/` + un installeur LibreOffice hors ligne sur les postes isolés.
La conversion PDF requiert `soffice`/`libreoffice` présent localement (aucun appel réseau).

## Tests

```bash
python -m unittest discover -s tests -v     # ou : pytest tests/
```

Les tests couvrent la sérialisation des modèles, le stockage JSON atomique, le repli de langue
et le filtrage des projets confidentiels. Le test de rendu DOCX est ignoré si
`docxtpl`/`python-docx` ne sont pas installés.

## Sécurité

- Écritures JSON atomiques (fichier temporaire + `os.replace` + `fsync`) pour éviter la corruption
  lors d'un arrêt brutal ou d'un accès concurrent.
- Identifiants de collaborateurs restreints à `[a-z0-9][a-z0-9\-_]*` (pas de traversée de dossiers).
- Aucun service externe, aucune donnée envoyée sur le réseau : compatible environnement air-gap.

## Technologies (cahier des charges §12)

Python, PySide6, docxtpl, Jinja2, python-docx, PyInstaller. LibreOffice (binaire système) pour le PDF.
