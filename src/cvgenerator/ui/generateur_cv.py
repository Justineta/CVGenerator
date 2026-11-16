from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..generator import generer_docx
from ..models import LANGUES
from ..pdf import convertir_pdf
from ..storage import DataStore


class FenetreGenerateur(QMainWindow):
    def __init__(self, store: DataStore, parent: QWidget | None = None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("GenerateurCV")
        self.resize(640, 520)

        central = QWidget(self)
        layout = QVBoxLayout(central)

        ligne_collab = QHBoxLayout()
        ligne_collab.addWidget(QLabel("Collaborateur"))
        self.combo_collaborateur = QComboBox()
        ligne_collab.addWidget(self.combo_collaborateur)
        layout.addLayout(ligne_collab)

        ligne_modele = QHBoxLayout()
        ligne_modele.addWidget(QLabel("Modèle"))
        self.combo_modele = QComboBox()
        ligne_modele.addWidget(self.combo_modele)
        ligne_langue = QHBoxLayout()
        ligne_langue.addWidget(QLabel("Langue"))
        self.combo_langue = QComboBox()
        self.combo_langue.addItems(LANGUES)
        ligne_langue.addWidget(self.combo_langue)
        layout.addLayout(ligne_modele)
        layout.addLayout(ligne_langue)

        layout.addWidget(QLabel("Projets à inclure"))
        self.liste_projets = QListWidget()
        layout.addWidget(self.liste_projets)

        self.case_confidentiels = QCheckBox("Inclure les projets confidentiels")
        layout.addWidget(self.case_confidentiels)

        barre = QHBoxLayout()
        self.bouton_docx = QPushButton("Générer DOCX")
        self.bouton_pdf = QPushButton("Générer DOCX + PDF")
        barre.addWidget(self.bouton_docx)
        barre.addWidget(self.bouton_pdf)
        layout.addLayout(barre)
        self.setCentralWidget(central)

        self.bouton_docx.clicked.connect(lambda: self.generer(pdf=False))
        self.bouton_pdf.clicked.connect(lambda: self.generer(pdf=True))
        self.combo_collaborateur.currentTextChanged.connect(self._rafraichir_projets)
        self.case_confidentiels.toggled.connect(self._rafraichir_projets)
        self.rafraichir()

    def rafraichir(self) -> None:
        self.combo_collaborateur.clear()
        self.combo_collaborateur.addItems([c.id for c in self.store.lister_collaborateurs()])
        self.combo_modele.clear()
        self.combo_modele.addItems(self.store.lister_modeles())
        self._rafraichir_projets()

    def _rafraichir_projets(self, *_args) -> None:
        self.liste_projets.clear()
        for p in self.store.charger_projets():
            item = QListWidgetItem(f"{p.reference} — {p.client}")
            item.setData(32, p.reference)
            item.setFlags(item.flags() | 2)
            item.setCheckState(2 if not p.confidentiel else 0)
            self.liste_projets.addItem(item)

    def _projets_selectionnes(self) -> list[str]:
        refs = []
        for i in range(self.liste_projets.count()):
            item = self.liste_projets.item(i)
            if item.checkState() == 2:
                refs.append(item.data(32))
        return refs

    def generer(self, pdf: bool) -> None:
        id_collab = self.combo_collaborateur.currentText()
        modele = self.combo_modele.currentText()
        langue = self.combo_langue.currentText()
        if not id_collab or not modele:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un collaborateur et un modèle.")
            return
        dossier = QFileDialog.getExistingDirectory(self, "Dossier d'export", str(self.store.exports_dir))
        if not dossier:
            return
        try:
            from pathlib import Path

            sortie = Path(dossier) / f"{id_collab}_{langue}.docx"
            sortie = generer_docx(
                self.store,
                id_collab,
                modele,
                langue,
                references=self._projets_selectionnes(),
                inclure_confidentiels=self.case_confidentiels.isChecked(),
                sortie=sortie,
            )
            if pdf:
                convertir_pdf(sortie, dossier)
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", str(exc))
            return
        QMessageBox.information(self, "OK", f"CV généré : {sortie}")


def main() -> None:
    store = DataStore.defaut()
    store.initialiser()
    app = QApplication(sys.argv)
    fenetre = FenetreGenerateur(store)
    fenetre.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    sys.exit(main())
