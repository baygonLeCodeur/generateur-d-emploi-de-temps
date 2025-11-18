from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox, QApplication
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from mes_dictionnaires import Les_interfaces
from genere_emploi_du_temps import genere_emploi_du_temps
import sys

class Affect_class_a_prof(QWidget):
    def __init__(self, title, mainForm, prevComponent):
        super().__init__()
        self.classes_par_matiere = {}
        self.setFixedSize(1000, 280)
        self.mainForm = mainForm
        self.nextComponent = None
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
            bouton.clicked.connect(self.on_button_clicked)
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
        
        self.vh_label = QLabel("Volume horaire")
        self.vh_label.setAlignment(Qt.AlignCenter)
        self.vh_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.inner16_layout = QHBoxLayout()
        self.inner16_layout.addStretch()
        self.inner16_layout.addWidget(self.vh_label)
        self.inner16_layout.addStretch()
        
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
        self.inner1_layout.addLayout(self.inner13_layout)
        self.inner1_layout.addLayout(self.inner16_layout)
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
        self.combo.clear()
        for prof in Les_interfaces.noms_professeurs[self.matiere]:
            self.combo.addItem(Les_interfaces.noms_professeurs[self.matiere][prof])
        # Sélectionner automatiquement le premier prof si disponible
        if self.combo.count() > 0:
            self.combo.setCurrentIndex(0)
            self.on_combo_text_changed(self.combo.currentText())
    
    @Slot(str)
    def on_combo_text_changed(self, text):
        if text != "": # ce gestionnaire est souvent appelé en double pour je ne sais quelle raison le cas echeant le 1er appel se fait avec text==""
            if self.matiere not in self.classes_par_matiere:
                self.classes_par_matiere[self.matiere] = []
                for niveau in Les_interfaces.matieres_seances:
                    if self.matiere in Les_interfaces.matieres_seances[niveau]:
                        self.classes_par_matiere[self.matiere] += Les_interfaces.niveaux_classes[niveau]
                # Remove already assigned classes
                assigned = set()
                for prof in Les_interfaces.repartition_classes.get(self.matiere, {}):
                    assigned.update(Les_interfaces.repartition_classes[self.matiere][prof])
                self.classes_par_matiere[self.matiere] = [c for c in self.classes_par_matiere[self.matiere] if c not in assigned]
            self.combo_ajout.clear()
            self.combo_ajout.addItems(self.classes_par_matiere[self.matiere])
            self.combo_retrait.clear()
            for prof in Les_interfaces.noms_professeurs[self.matiere]:
                if Les_interfaces.noms_professeurs[self.matiere][prof] == text:
                    les_classes_du_prof = Les_interfaces.repartition_classes[self.matiere].get(prof, [])
                    self.combo_retrait.addItems(les_classes_du_prof)
                    break
            self.update_vh_label()
    
    @Slot(int)
    def on_combo_ajout_item_clicked(self, index):
        texte = self.combo_ajout.itemText(index)
        self.classes_par_matiere[self.matiere].remove(texte)
        self.combo_ajout.removeItem(index)
        self.combo_ajout.hidePopup()
        for prof in Les_interfaces.noms_professeurs[self.matiere]:
            if Les_interfaces.noms_professeurs[self.matiere][prof] == self.combo.currentText():
                if prof not in Les_interfaces.repartition_classes[self.matiere]:
                    Les_interfaces.repartition_classes[self.matiere][prof] = []
                Les_interfaces.repartition_classes[self.matiere][prof].append(texte)
                self.combo_retrait.addItem(texte)
                break
        self.update_vh_label()
    
    @Slot(int)
    def on_combo_retrait_item_clicked(self, index):
        texte = self.combo_retrait.itemText(index)
        for prof in Les_interfaces.noms_professeurs[self.matiere]:
            if Les_interfaces.noms_professeurs[self.matiere][prof] == self.combo.currentText():
                if prof in Les_interfaces.repartition_classes[self.matiere]:
                    Les_interfaces.repartition_classes[self.matiere][prof].remove(texte)
                self.combo_retrait.removeItem(index)
                self.combo_retrait.hidePopup()
                break
        self.classes_par_matiere[self.matiere].append(texte)
        self.combo_ajout.addItem(texte)
        self.update_vh_label()
        
    def update_vh_label(self):
        vh = 0
        id_prof = ""
        for prof in Les_interfaces.noms_professeurs[self.matiere]:
            if Les_interfaces.noms_professeurs[self.matiere][prof] == self.combo.currentText():
                id_prof = prof
                classes_prof = Les_interfaces.repartition_classes[self.matiere].get(prof, [])
                for classe in classes_prof:
                    for niveau in Les_interfaces.niveaux_classes:
                        if classe in Les_interfaces.niveaux_classes[niveau]:
                            vh += sum(Les_interfaces.matieres_seances[niveau][self.matiere])
                break
        if self.matiere != "EDHC":
            edhc_repartition = Les_interfaces.repartition_classes.get("EDHC", {})
            if id_prof in edhc_repartition:
                for classe in edhc_repartition[id_prof]:
                    for niveau in Les_interfaces.niveaux_classes:
                        if classe in Les_interfaces.niveaux_classes[niveau]:
                            vh += sum(Les_interfaces.matieres_seances[niveau]["EDHC"])
        else:
            for matiere in Les_interfaces.repartition_classes:
                if matiere != "EDHC":
                    matiere_repartition = Les_interfaces.repartition_classes.get(matiere, {})
                    if id_prof in matiere_repartition:
                        for classe in matiere_repartition[id_prof]:
                            for niveau in Les_interfaces.niveaux_classes:
                                if classe in Les_interfaces.niveaux_classes[niveau]:
                                    vh += sum(Les_interfaces.matieres_seances[niveau][matiere])
                        break
        self.vh_label.setText(str(vh) + (" heure" if vh <= 1 else " heures"))

    def suivant(self):
        self.casser_boucle = False
        for matiere in self.classes_par_matiere:
            if len(self.classes_par_matiere[matiere]) != 0:
                QMessageBox.critical(None, "Erreur", "Une ou plusieurs classes n'ont été attribuées à aucun professeur de " + matiere)
                self.casser_boucle = True
                break
        if not self.casser_boucle:
            # Sauvegarder les données après cette étape (avant génération)
            Les_interfaces.save_data()
            genere_emploi_du_temps()
    
    def precedent(self):
        # Réinitialiser les affectations de classes aux professeurs
        for matiere in Les_interfaces.repartition_classes:
            matiere_dict = Les_interfaces.repartition_classes[matiere]
            for prof in matiere_dict:
                matiere_dict[prof] = []
        self.mainForm.WFStackedWidget.setCurrentWidget(self.prevComponent)
         
""" if __name__ == '__main__':
    app = QApplication(sys.argv)
    workForm = Affect_class_a_prof("VEUILLEZ, PAR MATIERE, NOMMER CHAQUE PROFESSEUR", None, None)
    workForm.setFixedHeight(300)
    workForm.show()
    sys.exit(app.exec()) """