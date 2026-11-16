# Installation et déploiement air-gap

Aucune connexion Internet n'est requise à l'installation ni à l'exécution.

## 1. Prérequis sur le poste cible (hors ligne)

- Windows 10/11 64 bits
- Python n'est **pas** requis si vous déployez les exécutables packagés
- LibreOffice (pour l'export PDF) : installer depuis un paquet MSI hors ligne ; l'application
  appelle `soffice --headless --convert-to pdf` en local

## 2. Contenu du paquet de déploiement

```
CVGenerator/
├── GestionCollaborateur.exe
├── GestionProjets.exe
├── GenerateurCV.exe
├── Collaborateurs/     # *.json (un par collaborateur)
├── Projets/Projets.json
├── Templates/          # *.docx (un par client, balises Jinja2)
├── Translations/       # amorcé automatiquement depuis les exécutables (fr/en/de/nl/es/it)
├── Exports/            # CV générés
└── Journaux/           # audit.jsonl (créé automatiquement)
```

Copier ce dossier sur chaque poste (clé USB, partage interne autorisé) — aucun téléchargement.

## 3. Données initiales

- Collaborateurs : copier les fiches `*.json` dans `Collaborateurs/`
- Projets : renseigner `Projets/Projets.json`
- Modèles : déposer les templates clients dans `Templates/`
  (exemple généré hors ligne : `python tools/make_sample_template.py Templates/modele_standard.docx`
  sur un poste de développement)

## 4. Variable d'environnement (optionnel)

`CVGENERATOR_HOME` : dossier de données personnalisé. Sans variable, le dossier de données est
celui de l'exécutable lancé.

## 5. Génération en ligne de commande (postes sans interface graphique)

```bash
cvgenerator --home "D:\CVGenerator" collaborateurs
cvgenerator --home "D:\CVGenerator" projets
cvgenerator --home "D:\CVGenerator" generer --collaborateur dupont-jean --modele modele_standard.docx --langue en --pdf
```

Les projets `confidentiel: true` sont exclus par défaut ; utiliser `--confidentiels` pour les inclure explicitement.

## 6. Sauvegardes

- Chaque réécriture conserve l'ancien fichier en `*.bak`
- Le journal `Journaux/audit.jsonl` trace chaque mutation (date UTC, action, cible)
- Sauvegarder régulièrement le dossier `CVGenerator/` entier (données + modèles) sur un support externe chiffré
