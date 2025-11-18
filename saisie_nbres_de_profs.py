from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from integerLineEdit import IntegerLineEdit
from mes_dictionnaires import Les_interfaces
from nommage_profs import Nommage_profs

class Saisie_nbres_de_profs(QWidget):
    def __init__(self, title, mainForm, prevComponent):
        super().__init__()
        self.setFixedSize(1000, 150)
        self.mainForm = mainForm
        self.nextComponent = Nommage_profs("VEUILLEZ, PAR MATIERE, NOMMER CHAQUE PROFESSEUR", mainForm, self)
        self.mainForm.WFStackedWidget.addWidget(self.nextComponent)
        #self.mainForm.setFixedHeight(200)
        self.prevComponent = prevComponent
        self.matieres = ["MATHS", "PHYS", "FRAN", "ANGL", "SVT", "HGEO", "LV2", "PHIL", "ART", "EPS", "EDHC"]#Les profs d'edhc sont pris parmi les autres profs
        
        self.boutSuivant = QPushButton("Suivant")
        self.boutSuivant.clicked.connect(self.suivant)
        self.boutPrecedent = QPushButton("Précédent")
        self.boutPrecedent.clicked.connect(self.precedent)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        
        self.inner2_layout = QGridLayout()
        self.nbres_de_prof_par_matiere = {}
        for ligne, matiere in enumerate(self.matieres):
            label = QLabel(matiere + ":")
            self.inner2_layout.addWidget(label, 0, ligne)
            line_edit = IntegerLineEdit(width=50, height=30)
            if matiere == "EDHC":
                line_edit = IntegerLineEdit(width=50, height=30, cas=3)
            self.nbres_de_prof_par_matiere[matiere] = line_edit
            # Pré-remplir avec les données sauvegardées si disponibles
            if matiere in Les_interfaces.repartition_classes:
                nb_profs = len(Les_interfaces.repartition_classes[matiere])
                if nb_profs > 0:
                    line_edit.setText(str(nb_profs))
            self.inner2_layout.addWidget(line_edit, 1, ligne)
        
        self.inner3_layout = QHBoxLayout()
        self.inner3_layout.addStretch(2)
        self.inner3_layout.addWidget(self.boutPrecedent)
        self.inner3_layout.addStretch(1)
        self.inner3_layout.addWidget(self.boutSuivant)
        self.inner3_layout.addStretch(2)
        
        self.inner1_layout = QVBoxLayout()
        self.inner1_layout.addWidget(self.title_label)
        self.inner1_layout.addLayout(self.inner2_layout)
        self.inner1_layout.addLayout(self.inner3_layout)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.inner1_layout)
        self.main_layout.addStretch()
    
    def suivant(self):
        # Sauvegarder les noms existants avant de reconstruire les structures
        noms_existants = Les_interfaces.noms_professeurs.copy() if hasattr(Les_interfaces, 'noms_professeurs') and Les_interfaces.noms_professeurs else {}
        repartition_existante = Les_interfaces.repartition_classes.copy() if hasattr(Les_interfaces, 'repartition_classes') and Les_interfaces.repartition_classes else {}

        # Réinitialiser les structures de données avant de les remplir
        Les_interfaces.repartition_classes = {}
        Les_interfaces.noms_professeurs = {}
        for matiere in self.matieres:
            Les_interfaces.repartition_classes[matiere] = {}
            Les_interfaces.noms_professeurs[matiere] = {}
            if matiere != "EDHC":
                for cpt in range(int(self.nbres_de_prof_par_matiere[matiere].text())):
                    prof_key = matiere + "_" + str(cpt + 1).zfill(2)
                    Les_interfaces.repartition_classes[matiere][prof_key] = repartition_existante.get(matiere, {}).get(prof_key, [])
                    # Restaurer le nom s'il existe dans les données sauvegardées
                    Les_interfaces.noms_professeurs[matiere][prof_key] = noms_existants.get(matiere, {}).get(prof_key, "")
        # Restaurer EDHC si présent
        if "EDHC" in repartition_existante:
            Les_interfaces.repartition_classes["EDHC"] = repartition_existante["EDHC"]
        if "EDHC" in noms_existants:
            Les_interfaces.noms_professeurs["EDHC"] = noms_existants["EDHC"]
        # Désactiver les boutons des matières avec 0 profs dans l'écran suivant
        for matiere in self.matieres:
            if matiere == "EDHC" or matiere != "EDHC" and len(Les_interfaces.repartition_classes[matiere]) == 0:
                self.nextComponent.boutons[matiere].setDisabled(True)
            else:
                self.nextComponent.boutons[matiere].setEnabled(True)
        # Sauvegarder les données après cette étape
        Les_interfaces.save_data()
        self.nextComponent.name_field.setText("")
        self.mainForm.setFixedHeight(300)
        self.mainForm.WFStackedWidget.setCurrentWidget(self.nextComponent)
    def precedent(self):
         self.mainForm.WFStackedWidget.setCurrentWidget(self.prevComponent)