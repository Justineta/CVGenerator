from __future__ import annotations

import json
from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from typing import Any, Callable, get_args, get_origin, get_type_hints

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..models import from_dict


def _est_complexe(annotation: Any) -> bool:
    origine = get_origin(annotation)
    if origine is list or origine is dict:
        return True
    return isinstance(annotation, type) and is_dataclass(annotation)


class DialogueFiche(QDialog):
    """Formulaire générique construit à partir des champs du dataclass."""

    def __init__(self, cls_modele: type, donnees: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.cls_modele = cls_modele
        self._champs: dict[str, tuple[Any, Any]] = {}
        layout = QVBoxLayout(self)
        formulaire = QFormLayout()
        hints = get_type_hints(cls_modele)
        for f in fields(cls_modele):
            annotation = hints.get(f.name, f.type)
            valeur = donnees.get(f.name)
            if _est_complexe(annotation):
                if get_origin(annotation) is list and valeur is None:
                    valeur = []
                if get_origin(annotation) is dict and valeur is None:
                    valeur = {}
                widget = QPlainTextEdit(json.dumps(valeur, ensure_ascii=False, indent=2))
                widget.setMinimumHeight(120)
            elif isinstance(annotation, type) and issubclass(annotation, Enum):
                widget = QComboBox()
                widget.addItems([e.value for e in annotation])
                courant = valeur.value if isinstance(valeur, Enum) else valeur
                if courant:
                    widget.setCurrentText(str(courant))
            elif annotation is bool:
                widget = QCheckBox()
                widget.setChecked(bool(valeur))
            else:
                widget = QLineEdit("" if valeur is None else str(valeur))
            formulaire.addRow(f.name, widget)
            self._champs[f.name] = (annotation, widget)
        layout.addLayout(formulaire)
        boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        boutons.accepted.connect(self.accept)
        boutons.rejected.connect(self.reject)
        layout.addWidget(boutons)

    def valeurs(self) -> dict:
        brut: dict[str, Any] = {}
        for nom, (annotation, widget) in self._champs.items():
            if isinstance(widget, QPlainTextEdit):
                brut[nom] = json.loads(widget.toPlainText() or "null")
            elif isinstance(widget, QComboBox):
                brut[nom] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                brut[nom] = widget.isChecked()
            else:
                texte = widget.text().strip()
                brut[nom] = texte if texte != "" else None
        return from_dict(self.cls_modele, brut)


class FenetreCrud(QMainWindow):
    """Fenêtre liste + actions CRUD générique pour un modèle donné."""

    def __init__(
        self,
        titre: str,
        cls_modele: type,
        cle: str,
        lister: Callable[[], list],
        charger: Callable[[str], Any],
        enregistrer: Callable[[Any], None],
        supprimer: Callable[[str], None],
        etiquette: Callable[[Any], str],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(titre)
        self._cls_modele = cls_modele
        self._cle = cle
        self._lister = lister
        self._charger = charger
        self._enregistrer = enregistrer
        self._supprimer = supprimer
        self._etiquette = etiquette

        central = QWidget(self)
        layout = QVBoxLayout(central)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([cle, "label"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        barre = QHBoxLayout()
        self.bouton_nouveau = QPushButton("Nouveau")
        self.bouton_modifier = QPushButton("Modifier")
        self.bouton_supprimer = QPushButton("Supprimer")
        self.bouton_rafraichir = QPushButton("Rafraîchir")
        for b in (self.bouton_nouveau, self.bouton_modifier, self.bouton_supprimer, self.bouton_rafraichir):
            barre.addWidget(b)
        layout.addLayout(barre)
        self.setCentralWidget(central)
        self.resize(720, 480)

        self.bouton_nouveau.clicked.connect(self.nouveau)
        self.bouton_modifier.clicked.connect(self.modifier)
        self.bouton_supprimer.clicked.connect(self.supprimer)
        self.bouton_rafraichir.clicked.connect(self.rafraichir)
        self.rafraichir()

    def rafraichir(self) -> None:
        objets = self._lister()
        self.table.setRowCount(len(objets))
        for i, obj in enumerate(objets):
            cle_valeur = getattr(obj, self._cle)
            self.table.setItem(i, 0, QTableWidgetItem(str(cle_valeur)))
            self.table.setItem(i, 1, QTableWidgetItem(self._etiquette(obj)))

    def _selection(self) -> str | None:
        lignes = self.table.selectionModel().selectedRows()
        if not lignes:
            return None
        return self.table.item(lignes[0].row(), 0).text()

    def nouveau(self) -> None:
        dialogue = DialogueFiche(self._cls_modele, {}, self)
        if dialogue.exec() == QDialog.Accepted:
            self._enregistrer(dialogue.valeurs())
            self.rafraichir()

    def modifier(self) -> None:
        cle = self._selection()
        if cle is None:
            return
        objet = self._charger(cle)
        from dataclasses import asdict

        dialogue = DialogueFiche(self._cls_modele, asdict(objet), self)
        if dialogue.exec() == QDialog.Accepted:
            self._enregistrer(dialogue.valeurs())
            self.rafraichir()

    def supprimer(self) -> None:
        cle = self._selection()
        if cle is None:
            return
        if QMessageBox.question(self, "Confirmation", f"Supprimer {cle} ?") == QMessageBox.Yes:
            self._supprimer(cle)
            self.rafraichir()


def lancer(titre: str, cls_modele: type, cle: str, **fonctions: Callable) -> None:
    import sys

    app = QApplication(sys.argv)
    fenetre = FenetreCrud(titre, cls_modele, cle, **fonctions)
    fenetre.show()
    sys.exit(app.exec())
