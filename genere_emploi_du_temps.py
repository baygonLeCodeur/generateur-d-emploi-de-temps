import copy
from itertools import permutations
from pdfLibrary import LesEmploisDeTpsClasses, LesEmploisDeTpsProfs
from les_dependances import prog_deux_heures, prog_une_heure, la_salle_dediee, emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or
from mes_dictionnaires import Les_interfaces
# tenter d'utiliser le nouveau solveur CSP hybride
try:
    from app.solver.csp_solver_hybrid import solve_emplois
except Exception:
    solve_emplois = None
from app.model.validation import validate_for_generation, ValidationError


def ajouter_eps_aux_emplois(emplois_du_temps_classes, emplois_du_temps_profs):
    """Ajouter les cours d'EPS aux emplois du temps"""
    print("📚 Ajout des cours d'EPS...")
    
    # Mapping classe -> prof d'EPS
    le_prof_d_eps_de = {}
    for classe in emplois_du_temps_classes:
        for prof in Les_interfaces.repartition_classes.get("EPS", {}):
            if classe in Les_interfaces.repartition_classes["EPS"][prof]:
                le_prof_d_eps_de[classe] = prof
                break
    
    # Mapping classe -> niveau
    niveau_classe = {}
    for classe in emplois_du_temps_classes:
        for niveau in Les_interfaces.niveaux_classes:
            if classe in Les_interfaces.niveaux_classes[niveau]:
                niveau_classe[classe] = niveau
                break
    
    # Pour chaque classe, essayer de placer 2 heures d'EPS consécutives
    for classe in emplois_du_temps_classes:
        if classe not in le_prof_d_eps_de:
            continue
        
        le_prof = le_prof_d_eps_de[classe]
        niveau = niveau_classe.get(classe)
        eps_placee = False
        
        for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
            if eps_placee:
                break
            
            # Calculer le nombre d'heures déjà occupées ce jour
            nb_heures_deja_fait = 0
            for moment in emplois_du_temps_classes[classe].get(jour, {}):
                nb_heures_deja_fait += sum(1 for cours in emplois_du_temps_classes[classe][jour][moment] if cours is not None)
            
            # Limite selon le niveau
            max_heures = 5 if niveau in ["6eme", "5eme", "4eme", "3eme"] else 7
            
            if max_heures - nb_heures_deja_fait >= 2:
                # Essayer le matin d'abord
                if "Matin" in emplois_du_temps_classes[classe][jour]:
                    for i in range(3):  # Positions 0-2 pour avoir de la place pour 2h consécutives
                        if all(emplois_du_temps_classes[classe][jour]["Matin"][j] is None for j in range(i, min(i+2, 5))):
                            # Vérifier disponibilité du prof
                            if (le_prof in emplois_du_temps_profs and 
                                "Matin" in emplois_du_temps_profs[le_prof][jour] and
                                emplois_du_temps_profs[le_prof][jour]["Matin"][i] is None and 
                                emplois_du_temps_profs[le_prof][jour]["Matin"][i+1] is None):
                                
                                emplois_du_temps_classes[classe][jour]["Matin"][i] = {
                                    "prof": le_prof, "matiere": "EPS", "salle": "Terrain"
                                }
                                emplois_du_temps_classes[classe][jour]["Matin"][i+1] = {
                                    "prof": le_prof, "matiere": "EPS", "salle": "Terrain"
                                }
                                emplois_du_temps_profs[le_prof][jour]["Matin"][i] = {
                                    'classe': classe, 'salle': "Terrain"
                                }
                                emplois_du_temps_profs[le_prof][jour]["Matin"][i+1] = {
                                    'classe': classe, 'salle': "Terrain"
                                }
                                eps_placee = True
                                break
                
                # Sinon essayer l'après-midi
                if not eps_placee and "Soir" in emplois_du_temps_classes[classe][jour]:
                    for i in range(1, 4):  # Positions 1-3 pour éviter H6 si matin complet
                        if all(emplois_du_temps_classes[classe][jour]["Soir"][j] is None for j in range(i, min(i+2, 5))):
                            # Vérifier disponibilité du prof
                            if (le_prof in emplois_du_temps_profs and
                                "Soir" in emplois_du_temps_profs[le_prof][jour] and
                                emplois_du_temps_profs[le_prof][jour]["Soir"][i] is None and 
                                emplois_du_temps_profs[le_prof][jour]["Soir"][i+1] is None):
                                
                                emplois_du_temps_classes[classe][jour]["Soir"][i] = {
                                    "prof": le_prof, "matiere": "EPS", "salle": "Terrain"
                                }
                                emplois_du_temps_classes[classe][jour]["Soir"][i+1] = {
                                    "prof": le_prof, "matiere": "EPS", "salle": "Terrain"
                                }
                                emplois_du_temps_profs[le_prof][jour]["Soir"][i] = {
                                    'classe': classe, 'salle': "Terrain"
                                }
                                emplois_du_temps_profs[le_prof][jour]["Soir"][i+1] = {
                                    'classe': classe, 'salle': "Terrain"
                                }
                                eps_placee = True
                                break
        
        if not eps_placee:
            print(f"⚠️  Impossible de placer l'EPS pour la classe {classe}")
    
    print("✅ Cours d'EPS ajoutés")
    return emplois_du_temps_classes, emplois_du_temps_profs

def genere_emploi_du_temps():
    # Valider les préconditions
    try:
        validate_for_generation()
        print("✅ Validation réussie")
    except ValidationError as e:
        # afficher l'erreur et sortir proprement
        print(f"❌ Erreur de validation avant génération : {e}")
        return
    except Exception as e:
        print(f"❌ Erreur inattendue lors de la validation : {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("🚀 Démarrage de la génération...")

    # Désactiver temporairement le nouveau solveur pour utiliser l'algorithme original amélioré
    use_new_solver = False
    if use_new_solver and solve_emplois is not None:
        try:
            res = solve_emplois(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or)
            if res is not None:
                emplois_du_temps_classes, emplois_du_temps_profs, edt_salles = res
                
                # Ajouter les cours d'EPS
                emplois_du_temps_classes, emplois_du_temps_profs = ajouter_eps_aux_emplois(
                    emplois_du_temps_classes, emplois_du_temps_profs
                )
                
                # Génération PDF pour les classes
                print("📄 Génération des emplois du temps des classes...")
                lesEmploisDeTpsClasses = LesEmploisDeTpsClasses()
                for classe in emplois_du_temps_classes:
                    lesEmploisDeTpsClasses.rediger_edt(classe, emplois_du_temps_classes[classe])
                lesEmploisDeTpsClasses.output("lesEmploisDeTpsClasses.pdf")
                print("✅ PDF des classes généré : lesEmploisDeTpsClasses.pdf")
                
                # Génération PDF pour les professeurs
                print("📄 Génération des emplois du temps des professeurs...")
                lesEmploisDeTpsProfs = LesEmploisDeTpsProfs()
                for prof_id in emplois_du_temps_profs:
                    # Trouver le nom du professeur
                    prof_nom = None
                    for matiere in Les_interfaces.noms_professeurs:
                        if prof_id in Les_interfaces.noms_professeurs[matiere]:
                            prof_nom = Les_interfaces.noms_professeurs[matiere][prof_id]
                            break
                    lesEmploisDeTpsProfs.rediger_edt(prof_id, prof_nom, emplois_du_temps_profs[prof_id])
                lesEmploisDeTpsProfs.output("lesEmploisDeTpsProfs.pdf")
                print("✅ PDF des professeurs généré : lesEmploisDeTpsProfs.pdf")
                
                print("\n🎉 Génération terminée avec succès !")
                return
        except Exception as e:
            # si le solveur échoue, on retombe sur l'algorithme original
            print(f"⚠️  Le solveur amélioré a échoué : {e}")
            import traceback
            traceback.print_exc()
            pass

    emplois_du_temps_classes = copy.deepcopy(emplois_du_temps_classes_or)
    emplois_du_temps_profs = copy.deepcopy(emplois_du_temps_profs_or)
    edt_salles = copy.deepcopy(emplois_du_temps_salles_or)
    arreter_tout = False
    
    print("📚 Génération des emplois du temps (hors EPS)...")
    
    for niveau in Les_interfaces.niveaux_classes:
        # Filter subjects that have at least one professor assigned (sans EPS)
        filtered_matieres = {
            matiere: seances 
            for matiere, seances in Les_interfaces.matieres_seances[niveau].items() 
            if matiere != 'EPS' and matiere in Les_interfaces.repartition_classes 
            and any(Les_interfaces.repartition_classes[matiere].values())
        }
        items = list(filtered_matieres.items())
        
        if not items:
            print(f"⚠️  Niveau {niveau}: aucune matière à placer")
            continue
        
        print(f"\n📖 Traitement du niveau {niveau} - {len(items)} matières")
        
        # Limiter le nombre de permutations (factorielle peut être énorme!)
        # 7 matières = 5040 permutations, 8 matières = 40320 permutations
        import random
        MAX_PERMUTATIONS = 100  # Limiter à 100 permutations aléatoires
        
        all_perms = list(permutations(items))
        if len(all_perms) > MAX_PERMUTATIONS:
            random.shuffle(all_perms)
            les_permut_n = [dict(perm) for perm in all_perms[:MAX_PERMUTATIONS]]
            print(f"  Utilisation de {MAX_PERMUTATIONS} permutations aléatoires sur {len(all_perms)}")
        else:
            les_permut_n = [dict(perm) for perm in all_perms]
            print(f"  Utilisation de toutes les {len(les_permut_n)} permutations")
        for classe in Les_interfaces.niveaux_classes[niveau]:
            print(f"  - Classe {classe}...")
            s_d = la_salle_dediee(classe)
            les_permut_c = iter([copy.deepcopy(perm_n) for perm_n in les_permut_n])
            les_tab_de_seances_de_classe = next(les_permut_c, None)
            
            if les_tab_de_seances_de_classe is None:
                print(f"    ❌ Aucune permutation disponible")
                arreter_tout = True
                break
            les_profs_de_la_classe = {}
            # Filtrer les matières qui ont des professeurs assignés
            matieres_avec_profs = {mat: seances for mat, seances in les_tab_de_seances_de_classe.items() if len(Les_interfaces.repartition_classes.get(mat, {})) > 0}
            for matiere in matieres_avec_profs:
                for prof in Les_interfaces.repartition_classes[matiere]:
                    if classe in Les_interfaces.repartition_classes[matiere][prof]:
                        les_profs_de_la_classe[matiere] = prof
            # Utiliser les matières filtrées pour la génération
            les_tab_de_seances_de_classe = matieres_avec_profs
            reprendre_edt = True
            while reprendre_edt:
                for jour in ['Lundi', 'Mardi', "Mercredi", 'Jeudi', 'Vendredi']:
                    if jour == "Mercredi" and niveau in ["6eme", "5eme"]:
                        continue
                    for moment in emplois_du_temps_classes[classe][jour]:
                        les_heures_vides = [i for i in range(len(emplois_du_temps_classes[classe][jour][moment])) if emplois_du_temps_classes[classe][jour][moment][i] is None]
                        while len(les_heures_vides) != 0:
                            edt_classe = emplois_du_temps_classes[classe]
                            heure1 = les_heures_vides[0]
                            deux_heures_prg = False
                            une_heure_prg = False
                            if heure1 < 4 and edt_classe[jour][moment][heure1 + 1] is None:
                                heure2 = heure1 + 1 
                                for matiere in les_tab_de_seances_de_classe:
                                    tab_de_seances = les_tab_de_seances_de_classe[matiere]
                                    le_prof = les_profs_de_la_classe[matiere]
                                    edt_prof = emplois_du_temps_profs[le_prof]
                                    if prog_deux_heures(matiere, tab_de_seances, edt_classe,  edt_prof, jour, heure1, heure2, moment, niveau, edt_salles, s_d):
                                        emplois_du_temps_classes[classe][jour][moment][heure1] = {"prof": le_prof, "matiere": matiere, "salle": Les_interfaces.s_v}
                                        emplois_du_temps_profs[le_prof][jour][moment][heure1] = {'classe': classe, 'salle': Les_interfaces.s_v}
                                        edt_salles[Les_interfaces.s_v][jour][moment][heure1] = {'classe': classe, "matiere": matiere}
                                        emplois_du_temps_classes[classe][jour][moment][heure2] = {"prof": le_prof, "matiere": matiere, "salle": Les_interfaces.s_v}
                                        emplois_du_temps_profs[le_prof][jour][moment][heure2] = {'classe': classe, 'salle': Les_interfaces.s_v}
                                        edt_salles[Les_interfaces.s_v][jour][moment][heure2] = {'classe': classe, "matiere": matiere}
                                        les_tab_de_seances_de_classe[matiere].remove(2)
                                        deux_heures_prg = True
                                        break
                            if not deux_heures_prg:
                                for matiere in les_tab_de_seances_de_classe:
                                    tab_de_seances = les_tab_de_seances_de_classe[matiere]
                                    le_prof = les_profs_de_la_classe[matiere]
                                    edt_prof = emplois_du_temps_profs[le_prof]
                                    if prog_une_heure(matiere, tab_de_seances, edt_classe,  edt_prof, jour, heure1, moment, niveau, edt_salles, s_d):
                                        emplois_du_temps_classes[classe][jour][moment][heure1] = {"prof": le_prof, "matiere": matiere, "salle": Les_interfaces.s_v}
                                        emplois_du_temps_profs[le_prof][jour][moment][heure1] = {'classe': classe, 'salle': Les_interfaces.s_v}
                                        edt_salles[Les_interfaces.s_v][jour][moment][heure1] = {'classe': classe, "matiere": matiere}
                                        les_tab_de_seances_de_classe[matiere].remove(1)
                                        une_heure_prg = True
                                        break
                            if not une_heure_prg and not deux_heures_prg:
                                break
                            les_heures_vides = [i for i in range(len(emplois_du_temps_classes[classe][jour][moment])) if emplois_du_temps_classes[classe][jour][moment][i] is None]
                    if jour == "Vendredi":
                        for nom_matiere in les_tab_de_seances_de_classe:
                            if len(les_tab_de_seances_de_classe[nom_matiere]) != 0:
                                break
                        else:
                            reprendre_edt = False
                            break
                        try:
                            emplois_du_temps_classes[classe] = copy.deepcopy(emplois_du_temps_classes_or[classe])
                            for la_matiere in Les_interfaces.repartition_classes:
                                for prof in Les_interfaces.repartition_classes[la_matiere]:
                                    if classe in Les_interfaces.repartition_classes[la_matiere][prof]:
                                        for jour_ in emplois_du_temps_profs[prof]:
                                            for moment_ in emplois_du_temps_profs[prof][jour_]:
                                                for i in range(len(emplois_du_temps_profs[prof][jour_][moment_])):
                                                    cours = emplois_du_temps_profs[prof][jour_][moment_][i]
                                                    if cours is not None and cours["classe"] == classe:
                                                        emplois_du_temps_profs[prof][jour_][moment_][i] = None
                            for salle in Les_interfaces.salles:
                                for jour_ in edt_salles[salle]:
                                    for moment_ in edt_salles[salle][jour_]:
                                        for i in range(len(edt_salles[salle][jour_][moment_])):
                                            cours = edt_salles[salle][jour_][moment_][i]
                                            if cours is not None and cours["classe"] == classe:
                                                edt_salles[salle][jour_][moment_][i] = None
                            les_tab_de_seances_de_classe = next(les_permut_c)
                        except StopIteration:
                            print(f"    ❌ Échec: toutes les permutations épuisées")
                            arreter_tout = True
                            reprendre_edt = False
            if arreter_tout:
                print(f"    ⚠️  Arrêt du traitement de la classe {classe}")
                break
        if arreter_tout:
            print(f"\n⚠️  Arrêt pour le niveau {niveau} - génération partielle")
            break
    
    if not arreter_tout:
        print("\n✅ Génération complète réussie pour tous les niveaux !")
        le_prof_d_eps_de = {}
        niveau_classe = {}
        for classe in emplois_du_temps_classes:
            for prof in Les_interfaces.repartition_classes["EPS"]:
                if classe in Les_interfaces.repartition_classes["EPS"][prof]:
                    le_prof_d_eps_de[classe] = prof
            for niveau in Les_interfaces.niveaux_classes:
                if classe in Les_interfaces.niveaux_classes[niveau]:
                    niveau_classe[classe] = niveau
        for classe in emplois_du_temps_classes:
            for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
                if "Matin" not in emplois_du_temps_classes[classe][jour]:
                    emplois_du_temps_classes[classe][jour]["Matin"] = [None] * 5
                if "Soir" not in emplois_du_temps_classes[classe][jour]:
                    for niveau in Les_interfaces.niveaux_classes:
                        if classe in Les_interfaces.niveaux_classes[niveau]:
                            if niveau not in Les_interfaces.devoirs_de_niveaux[jour]:
                                emplois_du_temps_classes[classe][jour]["Soir"] = [None] * 5
        for classe in emplois_du_temps_classes:
            classe_svt = False
            le_prof = le_prof_d_eps_de[classe]
            for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
                nb_heures_deja_fait = 0
                for moment in emplois_du_temps_classes[classe][jour]:
                    nb_heures_deja_fait += len([i for i in edt_classe[jour][moment] if i is not None])
                if (5 if niveau_classe[classe] in ["6eme", "5eme", "4eme", "3eme"] else 7) - nb_heures_deja_fait >= 2:
                    for i in range(3):
                        if all([j is None for j in emplois_du_temps_classes[classe][jour]["Matin"][i:i+3]]):
                            if emplois_du_temps_profs[le_prof][jour]["Matin"][i] is None or emplois_du_temps_profs[le_prof][jour]["Matin"][i+1] is None:
                                emplois_du_temps_classes[classe][jour]["Matin"][i] = {"prof": le_prof, "matiere": matiere, "salle": ""}
                                emplois_du_temps_profs[le_prof][jour]["Matin"][i] = {'classe': classe, 'salle': ""}
                                emplois_du_temps_classes[classe][jour]["Matin"][i+1] = {"prof": le_prof, "matiere": matiere, "salle": ""}
                                emplois_du_temps_profs[le_prof][jour]["Matin"][i+1] = {'classe': classe, 'salle': ""}
                                classe_svt = True
                                break
                    if classe_svt:
                        break
                    for i in range(1, 4, 1):
                        condition = False
                        if i == 1 or i == 2:
                            condition = all([j is None for j in emplois_du_temps_classes[classe][jour]["Soir"][i:i+3]])
                        else:
                            condition = emplois_du_temps_classes[classe][jour]["Soir"][i] is None and emplois_du_temps_classes[classe][jour]["Soir"][i] is None
                        if condition:
                            if emplois_du_temps_profs[le_prof][jour]["Soir"][i] is None or emplois_du_temps_profs[le_prof][jour]["Soir"][i+1] is None:
                                emplois_du_temps_classes[classe][jour]["Soir"][i] = {"prof": le_prof, "matiere": matiere, "salle": ""}
                                emplois_du_temps_profs[le_prof][jour]["Soir"][i] = {'classe': classe, 'salle': ""}
                                emplois_du_temps_classes[classe][jour]["Soir"][i+1] = {"prof": le_prof, "matiere": matiere, "salle": ""}
                                emplois_du_temps_profs[le_prof][jour]["Soir"][i+1] = {'classe': classe, 'salle': ""}
                                classe_svt = True
                                break
                    if classe_svt:
                        break
    else:
        print("\n⚠️  Génération partielle - Certaines classes n'ont pas pu être complétées")
    
    # Générer les PDFs même si la génération est partielle
    print("\n" + "=" * 70)
    
    # Ajouter les cours d'EPS
    print("📚 Ajout des cours d'EPS...")
    try:
        emplois_du_temps_classes, emplois_du_temps_profs = ajouter_eps_aux_emplois(
            emplois_du_temps_classes, emplois_du_temps_profs
        )
    except Exception as e:
        print(f"⚠️  Erreur lors de l'ajout de l'EPS : {e}")
    
    # Génération PDF pour les classes
    print("📄 Génération des emplois du temps des classes...")
    try:
        lesEmploisDeTpsClasses = LesEmploisDeTpsClasses()
        for classe in emplois_du_temps_classes:
            lesEmploisDeTpsClasses.rediger_edt(classe, emplois_du_temps_classes[classe])
        lesEmploisDeTpsClasses.output("lesEmploisDeTpsClasses.pdf")
        print("✅ PDF des classes généré : lesEmploisDeTpsClasses.pdf")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF des classes : {e}")
    
    # Génération PDF pour les professeurs
    print("📄 Génération des emplois du temps des professeurs...")
    try:
        lesEmploisDeTpsProfs = LesEmploisDeTpsProfs()
        for prof_id in emplois_du_temps_profs:
            # Trouver le nom du professeur
            prof_nom = None
            for matiere in Les_interfaces.noms_professeurs:
                if prof_id in Les_interfaces.noms_professeurs[matiere]:
                    prof_nom = Les_interfaces.noms_professeurs[matiere][prof_id]
                    break
            lesEmploisDeTpsProfs.rediger_edt(prof_id, prof_nom, emplois_du_temps_profs[prof_id])
        lesEmploisDeTpsProfs.output("lesEmploisDeTpsProfs.pdf")
        print("✅ PDF des professeurs généré : lesEmploisDeTpsProfs.pdf")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF des professeurs : {e}")
    
    if not arreter_tout:
        print("\n🎉 Génération terminée avec succès !")
    else:
        print("\n⚠️  Génération partielle terminée (certaines classes incomplètes)")