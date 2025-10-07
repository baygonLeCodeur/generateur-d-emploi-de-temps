from mes_dictionnaires import Les_interfaces

def faisabilite_emploi_du_temps():
    global salles
    total_heure_classes = 0
    total_heure_salles = 45 * len(Les_interfaces.salles)
    for niveau in Les_interfaces.matieres_seances:
        if niveau in Les_interfaces.niveaux_classes:
            total_heure_niveau = 0
            for matiere in Les_interfaces.matieres_seances[niveau]:
                if matiere != "EPS":
                    for seance in Les_interfaces.matieres_seances[niveau][matiere]:
                        total_heure_niveau = total_heure_niveau + seance
            total_heure_classes = total_heure_classes + total_heure_niveau * len(Les_interfaces.niveaux_classes[niveau])
        
    for jour in Les_interfaces.salles_devoir_de_niveau:
        if jour != "Mercredi":
            total_heure_salles = total_heure_salles - 5 * len(Les_interfaces.salles_devoir_de_niveau[jour])

    return total_heure_salles > total_heure_classes