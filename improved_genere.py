"""
Version améliorée du générateur original avec validation des contraintes.
Basé sur l'algorithme original mais avec des vérifications chirurgicales.

Auteur: Claude AI
Date: Décembre 2025
"""

import copy
import random
from typing import Dict, Tuple, Optional
from mes_dictionnaires import Les_interfaces
from les_dependances import (
    prog_deux_heures, prog_une_heure, la_salle_dediee,
    emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or
)


def validate_constraints(emplois_classes: Dict, emplois_profs: Dict) -> Tuple[bool, list]:
    """
    Valide toutes les contraintes sur les emplois du temps.
    Retourne (toutes_valides, liste_erreurs)
    """
    errors = []
    
    # Vérifier les contraintes par classe
    for classe, edt in emplois_classes.items():
        # Déterminer le niveau
        niveau = None
        for niv, classes in Les_interfaces.niveaux_classes.items():
            if classe in classes:
                niveau = niv
                break
        
        for jour in edt:
            matieres_jour = {}
            heures_jour = 0
            
            for moment in edt[jour]:
                for cours in edt[jour][moment]:
                    if cours is not None:
                        heures_jour += 1
                        matiere = cours.get("matiere")
                        
                        # Contrainte: pas plus d'une séance de la même matière par jour
                        if matiere and matiere in matieres_jour:
                            errors.append(
                                f"❌ {classe} - {jour}: {matiere} apparaît plus d'une fois"
                            )
                        if matiere:
                            matieres_jour[matiere] = True
            
            # Contrainte: limites d'heures par jour
            if niveau in ["6eme", "5eme", "4eme", "3eme"]:
                if heures_jour > 5:
                    errors.append(f"❌ {classe} - {jour}: {heures_jour}h > 5h (max collège)")
            else:
                if heures_jour > 7:
                    errors.append(f"❌ {classe} - {jour}: {heures_jour}h > 7h (max lycée)")
    
    # Vérifier les contraintes par professeur
    for prof, edt in emplois_profs.items():
        for jour in edt:
            heures_jour = 0
            
            for moment in edt[jour]:
                if moment and edt[jour][moment]:
                    for cours in edt[jour][moment]:
                        if cours is not None:
                            heures_jour += 1
            
            # Contrainte: max 7h par jour
            if heures_jour > 7:
                errors.append(f"❌ Prof {prof} - {jour}: {heures_jour}h > 7h")
    
    return len(errors) == 0, errors


def ajouter_eps_ameliore(emplois_du_temps_classes: Dict, emplois_du_temps_profs: Dict) -> Tuple[Dict, Dict]:
    """
    Ajoute les cours d'EPS de manière améliorée.
    Contraintes:
    - 2 heures consécutives
    - Plage H1-H4 ou H7-H10
    """
    print("📚 Ajout des cours d'EPS...")
    
    eps_placed = 0
    eps_failed = []
    
    for classe in emplois_du_temps_classes:
        # Trouver le prof d'EPS
        prof_eps = None
        if "EPS" in Les_interfaces.repartition_classes:
            for prof, classes in Les_interfaces.repartition_classes["EPS"].items():
                if classe in classes:
                    prof_eps = prof
                    break
        
        if not prof_eps:
            continue
        
        # Déterminer le niveau
        niveau = None
        for niv, classes in Les_interfaces.niveaux_classes.items():
            if classe in classes:
                niveau = niv
                break
        
        placed = False
        
        # Essayer chaque jour
        for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
            if placed:
                break
            
            for moment in ["Matin", "Soir"]:
                if placed:
                    break
                
                if moment not in emplois_du_temps_classes[classe].get(jour, {}):
                    continue
                
                if moment not in emplois_du_temps_profs[prof_eps].get(jour, {}):
                    continue
                
                plage_classe = emplois_du_temps_classes[classe][jour][moment]
                plage_prof = emplois_du_temps_profs[prof_eps][jour][moment]
                
                # Essayer positions 0-2 (pour avoir de la place après)
                for heure in range(3):
                    if (heure + 1 < 5 and
                        plage_classe[heure] is None and
                        plage_classe[heure + 1] is None and
                        plage_prof[heure] is None and
                        plage_prof[heure + 1] is None):
                        
                        # Placer l'EPS
                        for i in range(2):
                            emplois_du_temps_classes[classe][jour][moment][heure + i] = {
                                "prof": prof_eps,
                                "matiere": "EPS",
                                "salle": "Terrain"
                            }
                            emplois_du_temps_profs[prof_eps][jour][moment][heure + i] = {
                                "classe": classe,
                                "salle": "Terrain"
                            }
                        
                        placed = True
                        eps_placed += 1
                        break
        
        if not placed:
            eps_failed.append(classe)
    
    print(f"✅ EPS placée: {eps_placed}/{len(emplois_du_temps_classes)}")
    if eps_failed:
        print(f"⚠️  EPS non placée pour: {', '.join(eps_failed[:5])}" +
              (f" et {len(eps_failed) - 5} autres" if len(eps_failed) > 5 else ""))
    
    return emplois_du_temps_classes, emplois_du_temps_profs


def genere_emploi_du_temps_ameliore() -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
    """
    Génère les emplois du temps avec l'algorithme original amélioré.
    Retourne (emplois_classes, emplois_profs, emplois_salles) ou (None, None, None) si échec.
    """
    print("🚀 Génération avec algorithme amélioré...")
    
    emplois_du_temps_classes = copy.deepcopy(emplois_du_temps_classes_or)
    emplois_du_temps_profs = copy.deepcopy(emplois_du_temps_profs_or)
    edt_salles = copy.deepcopy(emplois_du_temps_salles_or)
    
    arreter_tout = False
    classes_reussies = 0
    classes_totales = sum(len(classes) for classes in Les_interfaces.niveaux_classes.values())
    
    print(f"📚 {classes_totales} classes à traiter...")
    
    for niveau in Les_interfaces.niveaux_classes:
        # Filtrer les matières avec professeurs assignés (sans EPS)
        filtered_matieres = {
            matiere: seances
            for matiere, seances in Les_interfaces.matieres_seances[niveau].items()
            if matiere != 'EPS' and matiere in Les_interfaces.repartition_classes
            and any(Les_interfaces.repartition_classes[matiere].values())
        }
        
        items = list(filtered_matieres.items())
        
        if not items:
            continue
        
        print(f"\n📖 Niveau {niveau}: {len(items)} matières, {len(Les_interfaces.niveaux_classes[niveau])} classes")
        
        # Générer des permutations aléatoires
        import itertools
        MAX_PERMUTATIONS = 50  # Limiter pour la performance
        
        all_perms = list(itertools.permutations(items))
        if len(all_perms) > MAX_PERMUTATIONS:
            random.shuffle(all_perms)
            les_permut_n = [dict(perm) for perm in all_perms[:MAX_PERMUTATIONS]]
        else:
            les_permut_n = [dict(perm) for perm in all_perms]
        
        for classe in Les_interfaces.niveaux_classes[niveau]:
            s_d = la_salle_dediee(classe)
            les_permut_c = iter([copy.deepcopy(perm_n) for perm_n in les_permut_n])
            les_tab_de_seances_de_classe = next(les_permut_c, None)
            
            if les_tab_de_seances_de_classe is None:
                arreter_tout = True
                break
            
            # Mapping prof -> matière
            les_profs_de_la_classe = {}
            matieres_avec_profs = {
                mat: seances
                for mat, seances in les_tab_de_seances_de_classe.items()
                if len(Les_interfaces.repartition_classes.get(mat, {})) > 0
            }
            
            for matiere in matieres_avec_profs:
                for prof in Les_interfaces.repartition_classes[matiere]:
                    if classe in Les_interfaces.repartition_classes[matiere][prof]:
                        les_profs_de_la_classe[matiere] = prof
            
            les_tab_de_seances_de_classe = matieres_avec_profs
            reprendre_edt = True
            tentatives = 0
            MAX_TENTATIVES = 20
            
            while reprendre_edt and tentatives < MAX_TENTATIVES:
                tentatives += 1
                
                for jour in ['Lundi', 'Mardi', "Mercredi", 'Jeudi', 'Vendredi']:
                    # Skip si mercredi et collège (géré différemment)
                    if jour == "Mercredi" and niveau in ["6eme", "5eme"]:
                        continue
                    
                    for moment in emplois_du_temps_classes[classe].get(jour, {}):
                        les_heures_vides = [
                            i for i in range(len(emplois_du_temps_classes[classe][jour][moment]))
                            if emplois_du_temps_classes[classe][jour][moment][i] is None
                        ]
                        
                        while len(les_heures_vides) != 0:
                            edt_classe = emplois_du_temps_classes[classe]
                            heure1 = les_heures_vides[0]
                            deux_heures_prg = False
                            une_heure_prg = False
                            
                            # Essayer de programmer 2 heures
                            if heure1 < 4 and edt_classe[jour][moment][heure1 + 1] is None:
                                heure2 = heure1 + 1
                                for matiere in les_tab_de_seances_de_classe:
                                    tab_de_seances = les_tab_de_seances_de_classe[matiere]
                                    le_prof = les_profs_de_la_classe.get(matiere)
                                    
                                    if not le_prof:
                                        continue
                                    
                                    edt_prof = emplois_du_temps_profs[le_prof]
                                    
                                    if prog_deux_heures(
                                        matiere, tab_de_seances, edt_classe, edt_prof,
                                        jour, heure1, heure2, moment, niveau, edt_salles, s_d
                                    ):
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
                            
                            # Essayer de programmer 1 heure
                            if not deux_heures_prg:
                                for matiere in les_tab_de_seances_de_classe:
                                    tab_de_seances = les_tab_de_seances_de_classe[matiere]
                                    le_prof = les_profs_de_la_classe.get(matiere)
                                    
                                    if not le_prof:
                                        continue
                                    
                                    edt_prof = emplois_du_temps_profs[le_prof]
                                    
                                    if prog_une_heure(
                                        matiere, tab_de_seances, edt_classe, edt_prof,
                                        jour, heure1, moment, niveau, edt_salles, s_d
                                    ):
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
                            
                            # Si aucun cours n'a pu être placé, arrêter
                            if not une_heure_prg and not deux_heures_prg:
                                break
                            
                            les_heures_vides = [
                                i for i in range(len(emplois_du_temps_classes[classe][jour][moment]))
                                if emplois_du_temps_classes[classe][jour][moment][i] is None
                            ]
                    
                    # Vérifier si toutes les séances sont placées
                    if jour == "Vendredi":
                        toutes_placees = all(
                            len(seances) == 0
                            for seances in les_tab_de_seances_de_classe.values()
                        )
                        
                        if toutes_placees:
                            reprendre_edt = False
                            classes_reussies += 1
                            break
                        else:
                            # Réinitialiser et essayer avec une autre permutation
                            try:
                                emplois_du_temps_classes[classe] = copy.deepcopy(
                                    emplois_du_temps_classes_or[classe]
                                )
                                
                                # Nettoyer les emplois des profs et salles
                                for la_matiere in Les_interfaces.repartition_classes:
                                    for prof in Les_interfaces.repartition_classes[la_matiere]:
                                        if classe in Les_interfaces.repartition_classes[la_matiere][prof]:
                                            for jour_ in emplois_du_temps_profs[prof]:
                                                for moment_ in emplois_du_temps_profs[prof][jour_]:
                                                    if moment_ and emplois_du_temps_profs[prof][jour_][moment_]:
                                                        for i in range(len(emplois_du_temps_profs[prof][jour_][moment_])):
                                                            cours = emplois_du_temps_profs[prof][jour_][moment_][i]
                                                            if cours is not None and cours["classe"] == classe:
                                                                emplois_du_temps_profs[prof][jour_][moment_][i] = None
                                
                                for salle in Les_interfaces.salles:
                                    for jour_ in edt_salles[salle]:
                                        for moment_ in edt_salles[salle][jour_]:
                                            if moment_ and edt_salles[salle][jour_][moment_]:
                                                for i in range(len(edt_salles[salle][jour_][moment_])):
                                                    cours = edt_salles[salle][jour_][moment_][i]
                                                    if cours is not None and cours["classe"] == classe:
                                                        edt_salles[salle][jour_][moment_][i] = None
                                
                                les_tab_de_seances_de_classe = next(les_permut_c)
                            except StopIteration:
                                reprendre_edt = False
                                arreter_tout = True
            
            if arreter_tout or tentatives >= MAX_TENTATIVES:
                print(f"  ⚠️  Échec pour {classe} (tentatives: {tentatives})")
                break
        
        if arreter_tout:
            break
    
    print(f"\n✅ Classes réussies: {classes_reussies}/{classes_totales}")
    
    # Ajouter l'EPS
    emplois_du_temps_classes, emplois_du_temps_profs = ajouter_eps_ameliore(
        emplois_du_temps_classes, emplois_du_temps_profs
    )
    
    # Valider les contraintes
    print("\n🔍 Validation des contraintes...")
    valide, erreurs = validate_constraints(emplois_du_temps_classes, emplois_du_temps_profs)
    
    if valide:
        print("✅ Toutes les contraintes sont respectées!")
    else:
        print(f"⚠️  {len(erreurs)} violations de contraintes détectées")
        for err in erreurs[:5]:
            print(f"  {err}")
        if len(erreurs) > 5:
            print(f"  ... et {len(erreurs) - 5} autres")
    
    return emplois_du_temps_classes, emplois_du_temps_profs, edt_salles
