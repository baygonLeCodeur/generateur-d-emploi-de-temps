import copy
from itertools import permutations
from pdfLibrary import LesEmploisDeTpsClasses
from les_dependances import prog_deux_heures, prog_une_heure, la_salle_dediee, emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or
from mes_dictionnaires import Les_interfaces
# tenter d'utiliser le nouveau solveur CSP heuristique si disponible
try:
    from app.solver.csp_solver import solve_emplois
except Exception:
    solve_emplois = None
from app.model.validation import validate_for_generation, ValidationError

def genere_emploi_du_temps():
    # Valider les préconditions
    try:
        validate_for_generation()
    except ValidationError as e:
        # afficher l'erreur et sortir proprement
        print(f"Erreur de validation avant génération : {e}")
        return

    # première tentative : solver CSP heuristique (plus efficace)
    if solve_emplois is not None:
        try:
            res = solve_emplois(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or)
            if res is not None:
                emplois_du_temps_classes, emplois_du_temps_profs, edt_salles = res
                # génération PDF et sortie
                lesEmploisDeTpsClasses = LesEmploisDeTpsClasses()
                for classe in emplois_du_temps_classes:
                    lesEmploisDeTpsClasses.rediger_edt(classe, emplois_du_temps_classes[classe])
                lesEmploisDeTpsClasses.output("lesEmploisDeTpsClasses.pdf")
                return
        except Exception:
            # si le solveur échoue, on retombe sur l'algorithme original
            pass

    emplois_du_temps_classes = copy.deepcopy(emplois_du_temps_classes_or)
    emplois_du_temps_profs = copy.deepcopy(emplois_du_temps_profs_or)
    edt_salles = copy.deepcopy(emplois_du_temps_salles_or)
    arreter_tout = False
    for niveau in Les_interfaces.niveaux_classes:
        del Les_interfaces.matieres_seances[niveau]['EPS']
        items = list(Les_interfaces.matieres_seances[niveau].items())
        perms = permutations(items)
        les_permut_n = [dict(perm) for perm in perms]
        for classe in Les_interfaces.niveaux_classes[niveau]:
            s_d = la_salle_dediee(classe)
            les_permut_c = iter([copy.deepcopy(perm_n) for perm_n in les_permut_n])
            les_tab_de_seances_de_classe = next(les_permut_c)
            les_profs_de_la_classe = {}
            for matiere in les_tab_de_seances_de_classe:
                for prof in Les_interfaces.repartition_classes[matiere]:
                    if classe in Les_interfaces.repartition_classes[matiere][prof]:
                        les_profs_de_la_classe[matiere] = prof
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
                        for nom_matiere in Les_interfaces.matieres_seances[niveau]:
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
                            arreter_tout = True
                            reprendre_edt = False
            if arreter_tout:
                break
        if arreter_tout:
            break
    if not arreter_tout:
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
                        
        lesEmploisDeTpsClasses = LesEmploisDeTpsClasses()
        for classe in emplois_du_temps_classes:
            lesEmploisDeTpsClasses.rediger_edt(classe, emplois_du_temps_classes[classe])
        lesEmploisDeTpsClasses.output("lesEmploisDeTpsClasses.pdf")