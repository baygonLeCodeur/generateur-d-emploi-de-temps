from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from integerLineEdit import IntegerLineEdit
from saisie_jours_de_devoirs import Saisie_jours_de_devoirs
from mes_dictionnaires import Les_interfaces

class Saisie_nombres_de_classes(QWidget):
    def __init__(self, title, mainForm):
        super().__init__()
        self.setFixedSize(1000, 250)
        self.mainForm = mainForm
        #self.mainForm.setFixedHeight(500)
        self.nextComponent = Saisie_jours_de_devoirs("RENSEIGNEZ LES JOURS DE DEVOIRS COMMUNS POUR CHAQUE NIVEAU", mainForm, self)
        self.mainForm.WFStackedWidget.addWidget(self.nextComponent)
        niveaux = ["6ème", "5ème", "4ème", "3ème", "2nde A", "2nde C", "1ère A1", "1ère A2", "1ère C", "1ère D", "Tle A1", "Tle A2", "Tle C", "Tle D"]
        
        self.boutSuivant = QPushButton("Suivant")
        self.boutSuivant.clicked.connect(self.niveauClasse_salles)
        
        self.nbSalles_label = QLabel("NOMBRES DE SALLES")
        self.nbSalles = IntegerLineEdit(width=50, height=30, cas=2)
        # Pré-remplir avec les données sauvegardées si disponibles
        if Les_interfaces.salles:
            self.nbSalles.setText(str(len(Les_interfaces.salles)))
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        
        self.inner2_layout = QGridLayout()
        self.nbClasse_par_niveau = {}
        for ligne, niveau in enumerate(niveaux):
            label = QLabel(niveau + ":")
            self.inner2_layout.addWidget(label, 0, ligne)
            line_edit = IntegerLineEdit(width=50, height=30)
            le_niveau = niveau.replace("è", "e").replace(" ", "")
            self.nbClasse_par_niveau[le_niveau] = line_edit
            # Pré-remplir avec les données sauvegardées si disponibles
            if le_niveau in Les_interfaces.niveaux_classes:
                line_edit.setText(str(len(Les_interfaces.niveaux_classes[le_niveau])))
            self.inner2_layout.addWidget(line_edit, 1, ligne)
            
        self.inner311_layout =QHBoxLayout()
        self.inner311_layout.addStretch() 
        self.inner311_layout.addWidget(self.nbSalles_label)
        self.inner311_layout.addStretch()
        
        self.inner312_layout =QHBoxLayout()
        self.inner312_layout.addStretch() 
        self.inner312_layout.addWidget(self.nbSalles)
        self.inner312_layout.addStretch() 
        
        self.inner31_layout =QVBoxLayout()
        self.inner31_layout.addLayout(self.inner311_layout)
        self.inner31_layout.addLayout(self.inner312_layout) 
        
        self.inner3_layout =QHBoxLayout()
        self.inner3_layout.addStretch()
        self.inner3_layout.addLayout(self.inner31_layout)
        self.inner3_layout.addStretch() 
        
        self.inner4_layout = QHBoxLayout()
        self.inner4_layout.addStretch()
        self.inner4_layout.addWidget(self.boutSuivant)
        self.inner4_layout.addStretch()
        
        self.inner1_layout = QVBoxLayout()
        self.inner1_layout.addWidget(self.title_label)
        self.inner1_layout.addLayout(self.inner2_layout)
        self.inner1_layout.addStretch()
        self.inner1_layout.addLayout(self.inner3_layout)
        self.inner1_layout.addLayout(self.inner4_layout)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.inner1_layout)
        self.main_layout.addStretch()
        
    def niveauClasse_salles(self):
        niveaux = ["TleA1", "TleA2", "TleD", "TleC", "3eme", "6eme", "5eme", "4eme", "2ndeA", "2ndeC", "1ereA1", "1ereA2", "1ereC", "1ereD"]
        # Réinitialiser les structures de données avant de les remplir
        Les_interfaces.niveaux_classes = {}
        Les_interfaces.salles = []
        for niveau in niveaux:
            les_classes_du_niveau = []
            if int(self.nbClasse_par_niveau[niveau].text()) != 0:
                for cpt in range(int(self.nbClasse_par_niveau[niveau].text())):
                    les_classes_du_niveau.append(niveau + " " + str(cpt +1))
                Les_interfaces.niveaux_classes[niveau] = les_classes_du_niveau
        for cpt in range(int(self.nbSalles.text())):
            Les_interfaces.salles.append("S" + str(cpt + 1))
        # Sauvegarder les données après cette étape
        Les_interfaces.save_data()
        self.nextComponent.boutSuivant.setEnabled(True)
        self.mainForm.WFStackedWidget.setCurrentWidget(self.nextComponent)
