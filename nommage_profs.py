from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox, QApplication
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from mes_dictionnaires import Les_interfaces
from nommer_profs_edhc import Nommer_profs_edhc
import sys


class Nommage_profs(QWidget):
    def __init__(self, title, mainForm, prevComponent):
        super().__init__()
        self.setFixedSize(1000, 250)
        self.mainForm = mainForm
        self.nextComponent = Nommer_profs_edhc("POUR CHAQUE MATIÈRE, CHOISISSEZ LES PROFS QUI DISPENSERONT LES COURS D'EDHC", mainForm, self)
        self.mainForm.WFStackedWidget.addWidget(self.nextComponent)
        #self.mainForm.setFixedHeight(200)
        self.prevComponent = prevComponent
        self.matieres = ["MATHS", "PHYS", "FRAN", "ANGL", "SVT", "HGEO", "LV2", "PHIL", "ART", "EPS", "EDHC"]#Les profs d'edhc sont pris parmi les autres pro
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        
        self.inner11_layout = QHBoxLayout()
        self.inner11_layout.addStretch()
        self.inner11_layout.addWidget(self.title_label)
        self.inner11_layout.addStretch()
        
        self.inner12_layout = QHBoxLayout()
        self.inner12_layout.addStretch()
        self.boutons = {}
        for matiere in self.matieres:
            bouton = QPushButton(matiere)
            bouton.setObjectName(matiere)
            bouton.setFixedSize(60, 30)
            if matiere == "EDHC":
                bouton.setDisabled(True)
            # Désactiver les boutons des matières avec 0 profs dans les données sauvegardées
            elif matiere in Les_interfaces.repartition_classes and len(Les_interfaces.repartition_classes[matiere]) == 0:
                bouton.setDisabled(True)
            bouton.clicked.connect(self.on_button_clicked)
            self.boutons[matiere] = bouton
            self.inner12_layout.addWidget(bouton)
            self.inner12_layout.addStretch()
        self.inner12_layout.addStretch()
        
        self.combo = QComboBox()
        self.combo.setFixedSize(150, 30)
        self.combo.currentTextChanged.connect(self.on_combo_text_changed)
        
        self.inner13_layout = QHBoxLayout()
        self.inner13_layout.addStretch()
        self.inner13_layout.addWidget(self.combo)
        self.inner13_layout.addStretch()
        
        self.name_field = QLineEdit()
        self.name_field.setFixedSize(200, 30)
        self.name_field.setAlignment(Qt.AlignCenter)
        self.name_field.textChanged.connect(self.on_text_changed)
        
        self.inner14_layout = QHBoxLayout()
        self.inner14_layout.addStretch()
        self.inner14_layout.addWidget(self.name_field)
        self.inner14_layout.addStretch()
        
        self.bout_valid_noms = QPushButton("Validez ce nom")
        self.bout_valid_noms.setFixedHeight(30)
        self.bout_valid_noms.setDisabled(True)
        self.bout_valid_noms.clicked.connect(self.valid_noms)
        
        self.inner15_layout = QHBoxLayout()
        self.inner15_layout.addStretch()
        self.inner15_layout.addWidget(self.bout_valid_noms)
        self.inner15_layout.addStretch()
        
        self.boutSuivant = QPushButton("Suivant")
        self.boutSuivant.setFixedHeight(30)
        self.boutSuivant.clicked.connect(self.suivant)
        self.boutPrecedent = QPushButton("Précédent")
        self.boutPrecedent.setFixedHeight(30)
        self.boutPrecedent.clicked.connect(self.precedent)
        
        self.inner16_layout = QHBoxLayout()
        self.inner16_layout.addStretch(2)
        self.inner16_layout.addWidget(self.boutPrecedent)
        self.inner16_layout.addStretch(1)
        self.inner16_layout.addWidget(self.boutSuivant)
        self.inner16_layout.addStretch(2)
        
        self.inner1_layout = QVBoxLayout()
        self.inner1_layout.addLayout(self.inner11_layout)
        self.inner1_layout.addLayout(self.inner12_layout)
        self.inner1_layout.addLayout(self.inner13_layout)
        self.inner1_layout.addLayout(self.inner14_layout)
        self.inner1_layout.addLayout(self.inner15_layout)
        self.inner1_layout.addLayout(self.inner16_layout)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.inner1_layout)
        self.main_layout.addStretch()
        
    @Slot()
    def on_button_clicked(self):
        bouton = self.sender()
        self.matiere = bouton.objectName()
        self.combo.clear()
        for prof in Les_interfaces.repartition_classes[self.matiere]:
            self.combo.addItem(prof)
        # Pré-remplir le champ nom avec le premier prof si disponible
        if self.combo.count() > 0:
            nom_du_prof_1 = Les_interfaces.noms_professeurs[self.matiere][self.combo.itemText(0)]
            self.name_field.setText(nom_du_prof_1)
            # Si le nom est déjà rempli, activer le bouton de validation
            if nom_du_prof_1 != "":
                self.bout_valid_noms.setEnabled(True)
            else:
                self.bout_valid_noms.setDisabled(True)
        else:
            self.bout_valid_noms.setDisabled(True)
    
    @Slot(str)
    def on_combo_text_changed(self, text):
        if text != "": # ce gestionnaire est souvent appelé en double pour je ne sais quelle raison le cas echeant le 1er appel se fait avec text==""
            nom_du_prof = Les_interfaces.noms_professeurs[self.matiere][text]
            self.name_field.setText(nom_du_prof)
            # Si le nom est déjà rempli, activer le bouton de validation
            if nom_du_prof != "":
                self.bout_valid_noms.setEnabled(True)
            else:
                self.bout_valid_noms.setDisabled(True)
    
    def valid_noms(self):
        Les_interfaces.noms_professeurs[self.matiere][self.combo.currentText()] = self.name_field.text()
        self.name_field.setText("")
        self.bout_valid_noms.setDisabled(True)
    
    def on_text_changed(self):
        self.bout_valid_noms.setEnabled(True)
    
    def suivant(self):
        self.casser_boucle = False
        for matiere in Les_interfaces.noms_professeurs:
            if matiere != "EDHC":
                for prof in Les_interfaces.noms_professeurs[matiere]:
                    if Les_interfaces.noms_professeurs[matiere][prof] == "":
                        QMessageBox.critical(None, "Erreur", "Vous devez renseigner le nom du prof de " + matiere + " qui a le code " + prof + "!")
                        self.casser_boucle = True
                        break
                if self.casser_boucle:
                    break
        if not self.casser_boucle:
            # Sauvegarder les données après cette étape
            Les_interfaces.save_data()
            self.mainForm.WFStackedWidget.setCurrentWidget(self.nextComponent)
    
    def precedent(self):
        # Réinitialiser les noms de professeurs (sauf EDHC qui est géré séparément)
        for matiere in Les_interfaces.noms_professeurs:
            if matiere != "EDHC":
                for prof in Les_interfaces.noms_professeurs[matiere]:
                    Les_interfaces.noms_professeurs[matiere][prof] = ""
        self.mainForm.WFStackedWidget.setCurrentWidget(self.prevComponent)
