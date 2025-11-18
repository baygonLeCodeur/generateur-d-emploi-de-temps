"""Solveur hybride combinant l'approche originale et les contraintes strictes.

Cette version utilise l'algorithme de permutations de l'original mais avec
des vérifications strictes des contraintes à chaque étape.
"""
from copy import deepcopy
from itertools import permutations
from mes_dictionnaires import Les_interfaces
import random


def la_salle_dediee(classe, salle_dediees_or):
    """Trouver la salle dédiée d'une classe"""
    for salle in salle_dediees_or:
        if classe in salle_dediees_or[salle]:
            return salle
    return None


def prog_deux_heures_strict(matiere, tab_de_seances, edt_classe, edt_prof, jour, heure1, heure2, 
                              moment_arg, niveau, edt_salles, s_d, Les_interfaces_local):
    """Vérifier et placer une séance de 2h avec toutes les contraintes"""
    # 1. Vérifier qu'il reste une séance de 2h
    if 2 not in tab_de_seances:
        return False
    
    # 2. Contrainte: pas plus d'une séance de la même matière le même jour
    for moment in edt_classe[jour]:
        for cours in edt_classe[jour][moment]:
            if cours is not None and cours.get("matiere") == matiere:
                return False
    
    # 3. Contrainte: max heures/jour
    nb_heures_deja_fait = sum(
        sum(1 for c in edt_classe[jour][m] if c is not None)
        for m in edt_classe[jour]
    )
    max_heures = 5 if niveau in ["6eme", "5eme", "4eme", "3eme"] else 7
    if nb_heures_deja_fait + 2 > max_heures:
        return False
    
    # 4. Contrainte: si matin complet, soir commence à H7 (indice 1)
    if moment_arg == "Soir" and heure1 == 0:
        if "Matin" in edt_classe[jour] and all(c is not None for c in edt_classe[jour]["Matin"]):
            return False
    
    # 5. Vérifier disponibilité prof
    if edt_prof[jour][moment_arg][heure1] is not None or edt_prof[jour][moment_arg][heure2] is not None:
        return False
    
    # 6. Contrainte: prof max 7h/jour
    nb_heures_prof = sum(
        sum(1 for c in edt_prof[jour][m] if c is not None)
        for m in edt_prof[jour]
    )
    if nb_heures_prof + 2 > 7:
        return False
    
    # 7. Trouver une salle
    if s_d is not None and moment_arg in edt_salles[s_d][jour]:
        if edt_salles[s_d][jour][moment_arg][heure1] is None and edt_salles[s_d][jour][moment_arg][heure2] is None:
            Les_interfaces_local.s_v = s_d
            return True
    
    for salle in Les_interfaces_local.salles:
        if moment_arg in edt_salles[salle][jour]:
            if edt_salles[salle][jour][moment_arg][heure1] is None and edt_salles[salle][jour][moment_arg][heure2] is None:
                Les_interfaces_local.s_v = salle
                return True
    
    return False


def prog_une_heure_strict(matiere, tab_de_seances, edt_classe, edt_prof, jour, heure, 
                           moment_arg, niveau, edt_salles, s_d, Les_interfaces_local):
    """Vérifier et placer une séance de 1h avec toutes les contraintes"""
    # 1. Vérifier qu'il reste une séance de 1h
    if 1 not in tab_de_seances:
        return False
    
    # 2. Contrainte: pas plus d'une séance de la même matière le même jour
    for moment in edt_classe[jour]:
        for cours in edt_classe[jour][moment]:
            if cours is not None and cours.get("matiere") == matiere:
                return False
    
    # 3. Contrainte: max heures/jour
    nb_heures_deja_fait = sum(
        sum(1 for c in edt_classe[jour][m] if c is not None)
        for m in edt_classe[jour]
    )
    max_heures = 5 if niveau in ["6eme", "5eme", "4eme", "3eme"] else 7
    if nb_heures_deja_fait + 1 > max_heures:
        return False
    
    # 4. Contrainte: si matin complet, soir commence à H7 (indice 1)
    if moment_arg == "Soir" and heure == 0:
        if "Matin" in edt_classe[jour] and all(c is not None for c in edt_classe[jour]["Matin"]):
            return False
    
    # 5. Vérifier disponibilité prof
    if edt_prof[jour][moment_arg][heure] is not None:
        return False
    
    # 6. Contrainte: prof max 7h/jour
    nb_heures_prof = sum(
        sum(1 for c in edt_prof[jour][m] if c is not None)
        for m in edt_prof[jour]
    )
    if nb_heures_prof + 1 > 7:
        return False
    
    # 7. Trouver une salle
    if s_d is not None and moment_arg in edt_salles[s_d][jour]:
        if edt_salles[s_d][jour][moment_arg][heure] is None:
            Les_interfaces_local.s_v = s_d
            return True
    
    for salle in Les_interfaces_local.salles:
        if moment_arg in edt_salles[salle][jour]:
            if edt_salles[salle][jour][moment_arg][heure] is None:
                Les_interfaces_local.s_v = salle
                return True
    
    return False


def solve_emplois(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or):
    """Solveur hybride avec algorithme de permutations et contraintes strictes"""
    print("🚀 Solveur hybride démarré...")
    
    # Calculer les salles dédiées
    salle_dediees_or = {}
    cpt1, cpt2, cpt3 = 0, 0, 0
    for niveau in Les_interfaces.niveaux_classes:
        for classe in Les_interfaces.niveaux_classes[niveau]:
            try:
                if niveau in ["6eme", "5eme", "4eme", "3eme"]:
                    salle_idx = cpt2 // 2 + cpt1
                    if salle_idx < len(Les_interfaces.salles):
                        if Les_interfaces.salles[salle_idx] not in salle_dediees_or:
                            salle_dediees_or[Les_interfaces.salles[salle_idx]] = []
                        salle_dediees_or[Les_interfaces.salles[salle_idx]].append(classe)
                    cpt2 += 1
                    cpt3 = cpt2 // 2 + cpt1 if cpt2 % 2 == 0 else cpt2 // 2 + cpt1 + 1
                elif niveau in ["TleA2", "TleD", "TleC", "TleA1"]:
                    if cpt1 < len(Les_interfaces.salles):
                        salle_dediees_or[Les_interfaces.salles[cpt1]] = [classe]
                    cpt1 += 1
                else:
                    if cpt3 < len(Les_interfaces.salles):
                        salle_dediees_or[Les_interfaces.salles[cpt3]] = [classe]
                    cpt3 += 1
            except IndexError:
                pass
    
    emplois_du_temps_classes = deepcopy(emplois_du_temps_classes_or)
    emplois_du_temps_profs = deepcopy(emplois_du_temps_profs_or)
    edt_salles = deepcopy(emplois_du_temps_salles_or)
    
    # Utiliser un nombre limité de permutations aléatoires
    MAX_PERMUTATIONS = 100
    arreter_tout = False
    
    for niveau in Les_interfaces.niveaux_classes:
        # Filtrer les matières qui ont des profs assignés (sans EPS)
        matieres_du_niveau = {
            mat: seances 
            for mat, seances in Les_interfaces.matieres_seances[niveau].items() 
            if mat != 'EPS' and mat in Les_interfaces.repartition_classes 
            and any(Les_interfaces.repartition_classes[mat].values())
        }
        
        if not matieres_du_niveau:
            continue
        
        # Générer quelques permutations aléatoires plutôt que toutes
        items = list(matieres_du_niveau.items())
        
        for classe in Les_interfaces.niveaux_classes[niveau]:
            print(f"Résolution {classe}...")
            s_d = la_salle_dediee(classe, salle_dediees_or)
            
            # Trouver les profs de cette classe
            les_profs_de_la_classe = {}
            for matiere in matieres_du_niveau:
                for prof in Les_interfaces.repartition_classes[matiere]:
                    if classe in Les_interfaces.repartition_classes[matiere][prof]:
                        les_profs_de_la_classe[matiere] = prof
                        break
            
            # Essayer avec différents ordres aléatoires
            succes = False
            for tentative in range(MAX_PERMUTATIONS):
                if tentative > 0:
                    random.shuffle(items)
                
                les_tab_de_seances_de_classe = dict(items)
                les_tab_de_seances_de_classe = deepcopy(les_tab_de_seances_de_classe)
                
                # Réinitialiser l'emploi du temps de cette classe
                emplois_du_temps_classes[classe] = deepcopy(emplois_du_temps_classes_or[classe])
                for la_matiere in Les_interfaces.repartition_classes:
                    for prof in Les_interfaces.repartition_classes[la_matiere]:
                        if classe in Les_interfaces.repartition_classes[la_matiere][prof]:
                            for jour_ in emplois_du_temps_profs[prof]:
                                for moment_ in emplois_du_temps_profs[prof][jour_]:
                                    for i in range(len(emplois_du_temps_profs[prof][jour_][moment_])):
                                        cours = emplois_du_temps_profs[prof][jour_][moment_][i]
                                        if cours is not None and cours.get("classe") == classe:
                                            emplois_du_temps_profs[prof][jour_][moment_][i] = None
                
                for salle in Les_interfaces.salles:
                    for jour_ in edt_salles[salle]:
                        for moment_ in edt_salles[salle][jour_]:
                            for i in range(len(edt_salles[salle][jour_][moment_])):
                                cours = edt_salles[salle][jour_][moment_][i]
                                if cours is not None and cours.get("classe") == classe:
                                    edt_salles[salle][jour_][moment_][i] = None
                
                # Essayer de placer toutes les séances
                echec = False
                for jour in ['Lundi', 'Mardi', "Mercredi", 'Jeudi', 'Vendredi']:
                    if jour == "Mercredi" and niveau in ["6eme", "5eme"]:
                        continue
                    
                    for moment in emplois_du_temps_classes[classe][jour]:
                        les_heures_vides = [
                            i for i in range(len(emplois_du_temps_classes[classe][jour][moment])) 
                            if emplois_du_temps_classes[classe][jour][moment][i] is None
                        ]
                        
                        while len(les_heures_vides) != 0:
                            edt_classe = emplois_du_temps_classes[classe]
                            heure1 = les_heures_vides[0]
                            deux_heures_prg = False
                            une_heure_prg = False
                            
                            # Essayer 2 heures
                            if heure1 < 4 and edt_classe[jour][moment][heure1 + 1] is None:
                                heure2 = heure1 + 1
                                for matiere in les_tab_de_seances_de_classe:
                                    if matiere not in les_profs_de_la_classe:
                                        continue
                                    tab_de_seances = les_tab_de_seances_de_classe[matiere]
                                    le_prof = les_profs_de_la_classe[matiere]
                                    edt_prof = emplois_du_temps_profs[le_prof]
                                    
                                    if prog_deux_heures_strict(matiere, tab_de_seances, edt_classe, edt_prof, 
                                                               jour, heure1, heure2, moment, niveau, edt_salles, 
                                                               s_d, Les_interfaces):
                                        emplois_du_temps_classes[classe][jour][moment][heure1] = {
                                            "prof": le_prof, "matiere": matiere, "salle": Les_interfaces.s_v
                                        }
                                        emplois_du_temps_profs[le_prof][jour][moment][heure1] = {
                                            'classe': classe, 'salle': Les_interfaces.s_v
                                        }
                                        edt_salles[Les_interfaces.s_v][jour][moment][heure1] = {
                                            'classe': classe, "matiere": matiere
                                        }
                                        emplois_du_temps_classes[classe][jour][moment][heure2] = {
                                            "prof": le_prof, "matiere": matiere, "salle": Les_interfaces.s_v
                                        }
                                        emplois_du_temps_profs[le_prof][jour][moment][heure2] = {
                                            'classe': classe, 'salle': Les_interfaces.s_v
                                        }
                                        edt_salles[Les_interfaces.s_v][jour][moment][heure2] = {
                                            'classe': classe, "matiere": matiere
                                        }
                                        les_tab_de_seances_de_classe[matiere].remove(2)
                                        deux_heures_prg = True
                                        break
                            
                            # Essayer 1 heure
                            if not deux_heures_prg:
                                for matiere in les_tab_de_seances_de_classe:
                                    if matiere not in les_profs_de_la_classe:
                                        continue
                                    tab_de_seances = les_tab_de_seances_de_classe[matiere]
                                    le_prof = les_profs_de_la_classe[matiere]
                                    edt_prof = emplois_du_temps_profs[le_prof]
                                    
                                    if prog_une_heure_strict(matiere, tab_de_seances, edt_classe, edt_prof, 
                                                             jour, heure1, moment, niveau, edt_salles, 
                                                             s_d, Les_interfaces):
                                        emplois_du_temps_classes[classe][jour][moment][heure1] = {
                                            "prof": le_prof, "matiere": matiere, "salle": Les_interfaces.s_v
                                        }
                                        emplois_du_temps_profs[le_prof][jour][moment][heure1] = {
                                            'classe': classe, 'salle': Les_interfaces.s_v
                                        }
                                        edt_salles[Les_interfaces.s_v][jour][moment][heure1] = {
                                            'classe': classe, "matiere": matiere
                                        }
                                        les_tab_de_seances_de_classe[matiere].remove(1)
                                        une_heure_prg = True
                                        break
                            
                            if not une_heure_prg and not deux_heures_prg:
                                echec = True
                                break
                            
                            les_heures_vides = [
                                i for i in range(len(emplois_du_temps_classes[classe][jour][moment])) 
                                if emplois_du_temps_classes[classe][jour][moment][i] is None
                            ]
                        
                        if echec:
                            break
                    
                    if echec:
                        break
                
                # Vérifier si tout est placé
                if not echec:
                    tout_place = all(len(seances) == 0 for seances in les_tab_de_seances_de_classe.values())
                    if tout_place:
                        print(f"✅ Succès {classe} (tentative {tentative + 1})")
                        succes = True
                        break
            
            if not succes:
                print(f"❌ Échec {classe} après {MAX_PERMUTATIONS} tentatives")
                arreter_tout = True
                break
        
        if arreter_tout:
            break
    
    if arreter_tout:
        print("❌ Échec de la génération")
        return None
    
    print("✅ Génération réussie!")
    return emplois_du_temps_classes, emplois_du_temps_profs, edt_salles


__all__ = ["solve_emplois"]
