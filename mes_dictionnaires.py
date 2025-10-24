import json
import os

with open('matieres_seances.json') as f:
    matieres_seances_ = json.load(f)

class Les_interfaces:
    niveaux_classes = {}
    salles = []
    devoirs_de_niveaux = {}
    salles_devoir_de_niveau = {}
    repartition_classes = {}
    noms_professeurs = {}
    matieres_seances = matieres_seances_
    s_v = ""

    @staticmethod
    def save_data():
        """Sauvegarde les données de session dans un fichier JSON"""
        data = {
            'niveaux_classes': Les_interfaces.niveaux_classes,
            'salles': Les_interfaces.salles,
            'devoirs_de_niveaux': Les_interfaces.devoirs_de_niveaux,
            'salles_devoir_de_niveau': Les_interfaces.salles_devoir_de_niveau,
            'repartition_classes': Les_interfaces.repartition_classes,
            'noms_professeurs': Les_interfaces.noms_professeurs
        }
        with open('session_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_data():
        """Charge les données de session depuis un fichier JSON si il existe"""
        if os.path.exists('session_data.json'):
            try:
                with open('session_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                Les_interfaces.niveaux_classes = data.get('niveaux_classes', {})
                Les_interfaces.salles = data.get('salles', [])
                Les_interfaces.devoirs_de_niveaux = data.get('devoirs_de_niveaux', {})
                Les_interfaces.salles_devoir_de_niveau = data.get('salles_devoir_de_niveau', {})
                Les_interfaces.repartition_classes = data.get('repartition_classes', {})
                Les_interfaces.noms_professeurs = data.get('noms_professeurs', {})
                return True
            except (json.JSONDecodeError, KeyError):
                # En cas d'erreur, on garde les valeurs par défaut
                return False
        return False

# Charger automatiquement les données au démarrage
Les_interfaces.load_data()
