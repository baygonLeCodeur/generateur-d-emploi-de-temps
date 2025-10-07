import json

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