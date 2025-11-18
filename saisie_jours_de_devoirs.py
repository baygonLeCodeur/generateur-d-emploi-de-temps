from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox
from saisie_nbres_de_profs import Saisie_nbres_de_profs
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from mes_dictionnaires import Les_interfaces
from test_de_faisabilite import faisabilite_emploi_du_temps

class Saisie_jours_de_devoirs(QWidget):
    def __init__(self, title, mainForm, prevComponent):
        super().__init__()
        self.setFixedSize(1000, 150)
        self.mainForm = mainForm
        #self.mainForm.setFixedHeight(200)
        self.nextComponent = Saisie_nbres_de_profs("RENSEIGNEZ LE NOMBRE DE PROFS PAR MATIERE", mainForm, self)
        self.mainForm.WFStackedWidget.addWidget(self.nextComponent)
        self.prevComponent = prevComponent
        niveaux = ["6ème", "5ème", "4ème", "3ème", "2nde A", "2nde C", "1ère A1", "1ère A2", "1ère C", "1ère D", "Tle A1", "Tle A2", "Tle C", "Tle D"]
        
        self.boutSuivant = QPushButton("Suivant")
        self.boutSuivant.clicked.connect(self.suivant)
        self.boutPrecedent = QPushButton("Précédent")
        self.boutPrecedent.clicked.connect(self.precedent)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        
        self.inner2_layout = QGridLayout()
        self.niveaux_par_jours = {}
        for ligne, niveau in enumerate(niveaux):
            label = QLabel(niveau + ":")
            self.inner2_layout.addWidget(label, 0, ligne)
            combo = QComboBox()
            combo.currentIndexChanged.connect(self.on_index_changed)
            combo.addItem("jour de devoir de niveau")
            combo.setCurrentIndex(-1) # Ceci assure que le placeholder est affiché
            combo.addItems(["Lun", "Mar", "Mer", "Jeu", "Ven"])
            le_niveau = niveau.replace("è", "e").replace(" ", "")
            self.niveaux_par_jours[le_niveau] = combo
            # Pré-remplir avec les données sauvegardées si disponibles
            for jour, niveaux_list in Les_interfaces.devoirs_de_niveaux.items():
                if le_niveau in niveaux_list:
                    jours_abbr = {"Lundi": "Lun", "Mardi": "Mar", "Mercredi": "Mer", "Jeudi": "Jeu", "Vendredi": "Ven"}
                    if jour in jours_abbr:
                        index = combo.findText(jours_abbr[jour])
                        if index != -1:
                            combo.setCurrentIndex(index)
                            break
            self.inner2_layout.addWidget(combo, 1, ligne)
        
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
        
    def on_index_changed(self):
        self.boutSuivant.setEnabled(True)
    
    def suivant(self):
        self.insuffisance_de_salle = False
        niveaux = ["TleA1", "TleA2", "TleD", "TleC", "3eme", "6eme", "5eme", "4eme", "2ndeA", "2ndeC", "1ereA1", "1ereA2", "1ereC", "1ereD"]
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        for niveau in niveaux:
            if int(self.niveaux_par_jours[niveau].currentIndex()) != -1:
                index = int(self.niveaux_par_jours[niveau].currentIndex() - 1)
                if jours[index] not in Les_interfaces.devoirs_de_niveaux:
                    Les_interfaces.devoirs_de_niveaux[jours[index]] = [niveau]
                else:
                    Les_interfaces.devoirs_de_niveaux[jours[index]].append(niveau)
        for jour in Les_interfaces.devoirs_de_niveaux:
            nbSalle = 0
            for niveau in Les_interfaces.devoirs_de_niveaux[jour]:
                if niveau in Les_interfaces.niveaux_classes:
                    nbSalle += len(Les_interfaces.niveaux_classes[niveau])
            #print(jour, nbSalle, len(Les_interfaces.salles))
            if nbSalle <= len(Les_interfaces.salles):
                for cpt in range(1, nbSalle + 1):
                    if jour not in Les_interfaces.salles_devoir_de_niveau:
                        Les_interfaces.salles_devoir_de_niveau[jour] = ["S" + str(cpt)]
                    else:
                        Les_interfaces.salles_devoir_de_niveau[jour].append("S" + str(cpt))
            else:
                if jour != "Mercredi":
                    self.insuffisance_de_salle = True
                    QMessageBox.critical(None, "Erreur", "Le nombre de salles requis pour les devoirs de niveaux du " + jour + " soir est supérieur au nombre de salle disponible!")
                    self.boutSuivant.setDisabled(True)
                    break
        if not self.insuffisance_de_salle and faisabilite_emploi_du_temps():
            # Sauvegarder les données après cette étape
            Les_interfaces.save_data()
            self.mainForm.WFStackedWidget.setCurrentWidget(self.nextComponent)
        elif not self.insuffisance_de_salle:
            self.boutSuivant.setDisabled(True)
            QMessageBox.critical(None, "Erreur", "Le nombre de salles disponibles ne couvre pas le volume horaire total hebdomadaire requis")
        
    def precedent(self):
        # Réinitialiser les données de devoirs de niveaux
        Les_interfaces.devoirs_de_niveaux = {}
        Les_interfaces.salles_devoir_de_niveau = {}
        self.mainForm.WFStackedWidget.setCurrentWidget(self.prevComponent)
