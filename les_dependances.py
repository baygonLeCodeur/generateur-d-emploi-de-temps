from mes_dictionnaires import Les_interfaces

def la_salle_dediee(classe):
    for salle in salle_dediees_or:
        if classe in salle_dediees_or[salle]:
            return salle
    else:
        return None
    
def prog_deux_heures(matiere, tab_de_seances, edt_classe,  edt_prof, jour, heure1, heure2, moment_arg, niveau, edt_salles, s_d):
    if len(tab_de_seances) == 0:
        return False
    
    for moment in edt_classe[jour]:
        for cours in edt_classe[jour][moment]:
            if cours is not None and cours["matiere"] == matiere:
                return False
            
    nb_heures_deja_fait = 0
    for moment in edt_classe[jour]:
        nb_heures_deja_fait += len([i for i in edt_classe[jour][moment] if i is not None])
    if (5 if niveau in ["6eme", "5eme", "4eme", "3eme"] else 7) - nb_heures_deja_fait < 2:
        return False
    
    if edt_prof[jour][moment_arg][heure1] is not None or edt_prof[jour][moment_arg][heure2] is not None:
        return False
    
    for i in tab_de_seances:
        if i == 2:
            break
    else:
        return False
    
    if s_d is not None and moment_arg in edt_salles[s_d][jour] and edt_salles[s_d][jour][moment_arg][heure1] is None and edt_salles[s_d][jour][moment_arg][heure2] is None:
        Les_interfaces.s_v = s_d
    else:
        for salle in Les_interfaces.salles:
            if moment_arg in edt_salles[salle][jour]:
                if edt_salles[salle][jour][moment_arg][heure1] is None and edt_salles[salle][jour][moment_arg][heure2] is None:
                    Les_interfaces.s_v = salle
                    break
        else:
            return False
    
    return True
            

def prog_une_heure(matiere, tab_de_seances, edt_classe,  edt_prof, jour, heure, moment_arg, niveau, edt_salles, s_d):
    if len(tab_de_seances) == 0:
        return False
    
    for moment in edt_classe[jour]:
        for cours in edt_classe[jour][moment]:
            if cours is not None and cours["matiere"] == matiere:
                return False
            
    nb_heures_deja_fait = 0
    for moment in edt_classe[jour]:
        nb_heures_deja_fait += len([i for i in edt_classe[jour][moment] if i is not None])
    if (5 if niveau in ["6eme", "5eme", "4eme", "3eme"] else 7) - nb_heures_deja_fait < 1:
        return False
    
    if edt_prof[jour][moment_arg][heure] is not None:
        return False
    
    for i in tab_de_seances:
        if i == 1:
            break
    else:
        return False
    
    if s_d is not None and moment_arg in edt_salles[s_d][jour] and edt_salles[s_d][jour][moment_arg][heure] is None:
        Les_interfaces.s_v = s_d
    else:
        for salle in Les_interfaces.salles:
            if moment_arg in edt_salles[salle][jour]:
                if edt_salles[salle][jour][moment_arg][heure] is None:
                    Les_interfaces.s_v = salle
                    break
        else:
            return False
    
    return True
                    
emplois_du_temps_classes_or = {}
emplois_du_temps_profs_or = {}
emplois_du_temps_salles_or = {}
salle_dediees_or = {}

cpt1 = 0
cpt2 = 0
cpt3 = 0
for niveau in Les_interfaces.niveaux_classes:
    for classe in Les_interfaces.niveaux_classes[niveau]:
        try:
            if niveau in ["6eme", "5eme", "4eme", "3eme"]:
                if cpt2 % 2 == 0:
                    emplois_du_temps_classes_or[classe] = {
                        'Lundi': {"Matin": [None] * 5},
                        'Mardi': {"Matin": [None] * 5},
                        'Mercredi': {"Matin": [None] * 5},
                        'Jeudi': {"Soir": [None] * 5},
                        'Vendredi': {"Soir": [None] * 5}
                    }
                    salle_dediees_or[Les_interfaces.salles[cpt2 // 2 + cpt1]] = [classe]
                else:
                    emplois_du_temps_classes_or[classe] = {
                        'Lundi': {"Soir": [None] * 5},
                        'Mardi': {"Soir": [None] * 5},
                        'Mercredi': {"Matin": [None] * 5},
                        'Jeudi': {"Matin": [None] * 5},
                        'Vendredi': {"Matin": [None] * 5}
                    }
                    salle_dediees_or[Les_interfaces.salles[cpt2 // 2 + cpt1]].append(classe)
                cpt2 = cpt2 + 1
                cpt3 = cpt2 // 2 + cpt1 if cpt2 % 2 == 0 else cpt2 // 2 + cpt1 + 1
            elif niveau in ["TleA2", "TleD", "TleC", "TleA1"]:
                emplois_du_temps_classes_or[classe] = {
                    'Lundi': {"Matin": [None] * 5, "Soir": [None] * 5},
                    'Mardi': {"Matin": [None] * 5, "Soir": [None] * 5},
                    'Mercredi': {"Matin": [None] * 5},
                    'Jeudi': {"Matin": [None] * 5, "Soir": [None] * 5},
                    'Vendredi': {"Matin": [None] * 5, "Soir": [None] * 5}
                }
                salle_dediees_or[Les_interfaces.salles[cpt1]] = [classe]
                cpt1 = cpt1 + 1
            else:
                emplois_du_temps_classes_or[classe] = {
                    'Lundi': {"Matin": [None] * 5, "Soir": [None] * 5},
                    'Mardi': {"Matin": [None] * 5, "Soir": [None] * 5},
                    'Mercredi': {"Matin": [None] * 5},
                    'Jeudi': {"Matin": [None] * 5, "Soir": [None] * 5},
                    'Vendredi': {"Matin": [None] * 5, "Soir": [None] * 5}
                }
                salle_dediees_or[Les_interfaces.salles[cpt3]] = [classe]
                cpt3 = cpt3 + 1
        except IndexError:
            pass
        for jour in Les_interfaces.devoirs_de_niveaux:
            if niveau in Les_interfaces.devoirs_de_niveaux[jour]:
                emplois_du_temps_classes_or[classe][jour] = {"Matin": [None] * 5}

for matiere in Les_interfaces.repartition_classes:
    for professeur in Les_interfaces.repartition_classes[matiere]:
        emplois_du_temps_profs_or[professeur] = {
            'Lundi': {"Matin": [None] * 5, "Soir": [None] * 5},
            'Mardi': {"Matin": [None] * 5, "Soir": [None] * 5},
            'Mercredi': {"Matin": [None] * 5},
            'Jeudi': {"Matin": [None] * 5, "Soir": [None] * 5},
            'Vendredi': {"Matin": [None] * 5, "Soir": [None] * 5}
        }
        
for salle in Les_interfaces.salles:
    emplois_du_temps_salles_or[salle] = {
            'Lundi': {"Matin": [None] * 5, "Soir": [None] * 5},
            'Mardi': {"Matin": [None] * 5, "Soir": [None] * 5},
            'Mercredi': {"Matin": [None] * 5},
            'Jeudi': {"Matin": [None] * 5, "Soir": [None] * 5},
            'Vendredi': {"Matin": [None] * 5, "Soir": [None] * 5}
        }
    for jour in Les_interfaces.salles_devoir_de_niveau:
        if salle in Les_interfaces.salles_devoir_de_niveau[jour]:
            emplois_du_temps_salles_or[salle][jour] = {"Matin": [None] * 5}