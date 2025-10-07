from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox, QApplication
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from mes_dictionnaires import Les_interfaces
from affect_class_a_prof import Affect_class_a_prof
import sys

class Nommer_profs_edhc(QWidget):
    def __init__(self, title, mainForm, prevComponent):
        super().__init__()
        self.classes_par_matiere = {}
        self.setFixedSize(1000, 200)
        self.mainForm = mainForm
        self.nextComponent = Affect_class_a_prof("REPARTISSEZ LES CLASSES ENTRE LES PROFESSEURS DANS LES DIFFERENTES MATIERES", mainForm, self)
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
        for matiere in self.matieres:
            bouton = QPushButton(matiere)
            bouton.setObjectName(matiere)
            bouton.setFixedSize(60, 30)
            if matiere == "EDHC":
                bouton.setDisabled(True)
            bouton.clicked.connect(self.on_button_clicked)
            self.inner12_layout.addWidget(bouton)
            self.inner12_layout.addStretch()
        self.inner12_layout.addStretch()
        
        self.ajout_label = QLabel("Ajouter")
        self.ajout_label.setAlignment(Qt.AlignCenter)
        self.ajout_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.inner1411_layout = QHBoxLayout()
        self.inner1411_layout.addStretch()
        self.inner1411_layout.addWidget(self.ajout_label)
        self.inner1411_layout.addStretch()
        
        self.combo_ajout = QComboBox()
        self.combo_ajout.setFixedSize(90, 30)
        self.combo_ajout.activated.connect(self.on_combo_ajout_item_clicked)
        
        self.inner1412_layout = QHBoxLayout()
        self.inner1412_layout.addStretch()
        self.inner1412_layout.addWidget(self.combo_ajout)
        self.inner1412_layout.addStretch()
        
        self.inner141_layout = QVBoxLayout()
        self.inner141_layout.addLayout(self.inner1411_layout)
        self.inner141_layout.addLayout(self.inner1412_layout)
        
        self.retrait_label = QLabel("Retirer")
        self.retrait_label.setAlignment(Qt.AlignCenter)
        self.retrait_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.inner1421_layout = QHBoxLayout()
        self.inner1421_layout.addStretch()
        self.inner1421_layout.addWidget(self.retrait_label)
        self.inner1421_layout.addStretch()
        
        self.combo_retrait = QComboBox()
        self.combo_retrait.setFixedSize(90, 30)
        self.combo_retrait.activated.connect(self.on_combo_retrait_item_clicked)
        
        self.inner1422_layout = QHBoxLayout()
        self.inner1422_layout.addStretch()
        self.inner1422_layout.addWidget(self.combo_retrait)
        self.inner1422_layout.addStretch()
        
        self.inner142_layout = QVBoxLayout()
        self.inner142_layout.addLayout(self.inner1421_layout)
        self.inner142_layout.addLayout(self.inner1422_layout)
        
        self.inner14_layout = QHBoxLayout()
        self.inner14_layout.addStretch(2)
        self.inner14_layout.addLayout(self.inner141_layout)
        self.inner14_layout.addStretch(1)
        self.inner14_layout.addLayout(self.inner142_layout)
        self.inner14_layout.addStretch(2)
         
        
        self.boutSuivant = QPushButton("Suivant")
        self.boutSuivant.setFixedHeight(30)
        self.boutSuivant.clicked.connect(self.suivant)
        self.boutPrecedent = QPushButton("Précédent")
        self.boutPrecedent.setFixedHeight(30)
        self.boutPrecedent.clicked.connect(self.precedent)
        
        self.inner15_layout = QHBoxLayout()
        self.inner15_layout.addStretch(2)
        self.inner15_layout.addWidget(self.boutPrecedent)
        self.inner15_layout.addStretch(1)
        self.inner15_layout.addWidget(self.boutSuivant)
        self.inner15_layout.addStretch(2)
        
        self.inner1_layout = QVBoxLayout()
        self.inner1_layout.addLayout(self.inner11_layout)
        self.inner1_layout.addLayout(self.inner12_layout)
        self.inner1_layout.addLayout(self.inner14_layout)
        self.inner1_layout.addLayout(self.inner15_layout)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.inner1_layout)
        self.main_layout.addStretch()
        
    @Slot()
    def on_button_clicked(self):
        bouton = self.sender()
        self.matiere = bouton.objectName()
        self.combo_ajout.clear()
        self.combo_retrait.clear()
        for prof in Les_interfaces.noms_professeurs[self.matiere]:
            if prof not in Les_interfaces.repartition_classes["EDHC"]:
                self.combo_ajout.addItem(Les_interfaces.noms_professeurs[self.matiere][prof])
            else:
                self.combo_retrait.addItem(Les_interfaces.noms_professeurs[self.matiere][prof])
    
    @Slot(int)
    def on_combo_ajout_item_clicked(self, index):
        texte = self.combo_ajout.itemText(index)
        self.combo_ajout.removeItem(index)
        self.combo_ajout.hidePopup()
        for prof in Les_interfaces.noms_professeurs[self.matiere]:
            if Les_interfaces.noms_professeurs[self.matiere][prof] == texte:
                Les_interfaces.repartition_classes["EDHC"][prof] = []
                Les_interfaces.noms_professeurs["EDHC"][prof] = texte
                self.combo_retrait.addItem(texte)
                break
    
    @Slot(int)
    def on_combo_retrait_item_clicked(self, index):
        texte = self.combo_retrait.itemText(index)
        self.combo_retrait.removeItem(index)
        self.combo_retrait.hidePopup()
        for prof in Les_interfaces.noms_professeurs[self.matiere]:
            if Les_interfaces.noms_professeurs[self.matiere][prof] == texte:
                del Les_interfaces.repartition_classes["EDHC"][prof]
                del Les_interfaces.noms_professeurs["EDHC"][prof]
                self.combo_ajout.addItem(texte)
                break

    def suivant(self):
        if not Les_interfaces.repartition_classes["EDHC"]:
            QMessageBox.critical(None, "Erreur", "Vous n'avez désigné aucun professeur d'EDHC")
        else:
            self.mainForm.WFStackedWidget.setCurrentWidget(self.nextComponent)
    
    def precedent(self):
         self.mainForm.WFStackedWidget.setCurrentWidget(self.prevComponent)
         
""" if __name__ == '__main__':
    app = QApplication(sys.argv)
    workForm = Nommer_profs_edhc("VEUILLEZ, PAR MATIERE, NOMMER CHAQUE PROFESSEUR", None, None)
    workForm.setFixedHeight(300)
    workForm.show()
    sys.exit(app.exec()) """