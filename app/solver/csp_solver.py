"""Solveur CSP heuristique pour la génération d'emplois du temps.

Approche : backtracking avec ordre par charge (classes avec le plus d'heures en premier),
sélection de la matière la plus contraignante et forward-checking simple en vérifiant
disponibilités prof/salle via les fonctions existantes dans `les_dependances.py`.
Ce solveur vise à être plus efficace que l'approche par permutations en limitéant
les réordonnancements et en utilisant du backtracking global.
"""
from copy import deepcopy
from les_dependances import prog_deux_heures, prog_une_heure, la_salle_dediee
from mes_dictionnaires import Les_interfaces


def solve_emplois(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or):
    """Tentative de résolution via backtracking.

    Retourne (emplois_classes, emplois_profs, edt_salles) ou None si échec.
    """
    emplois_classes = deepcopy(emplois_du_temps_classes_or)
    emplois_profs = deepcopy(emplois_du_temps_profs_or)
    edt_salles = deepcopy(emplois_du_temps_salles_or)

    # Préparer la liste des classes et leurs sessions restantes
    classes = list(emplois_classes.keys())

    # Construire map classe -> niveau
    classe_to_niveau = {}
    for niveau in Les_interfaces.niveaux_classes:
        for classe in Les_interfaces.niveaux_classes[niveau]:
            classe_to_niveau[classe] = niveau

    # Pour chaque classe, construire dict matiere -> list(seances)
    remaining = {}
    for classe in classes:
        niveau = classe_to_niveau.get(classe)
        if niveau is None:
            remaining[classe] = {}
            continue
        # copie des matieres de ce niveau
        remaining[classe] = {m: list(Les_interfaces.matieres_seances[niveau][m]) for m in Les_interfaces.matieres_seances[niveau]}
        # retirer EPS si présent (comportement original)
        if 'EPS' in remaining[classe]:
            del remaining[classe]['EPS']

    # Ordre des classes : celles avec plus d'heures totales en premier
    def total_hours(classe):
        s = 0
        for m, lst in remaining[classe].items():
            s += sum(lst)
        return s

    classes.sort(key=lambda c: -total_hours(c))

    # Pour chaque classe, déterminer les profs possibles par matiere (unique mapping attendu)
    profs_for_class = {}
    for classe in classes:
        profs_for_class[classe] = {}
        for matiere in remaining[classe]:
            for prof in Les_interfaces.repartition_classes.get(matiere, {}):
                if classe in Les_interfaces.repartition_classes[matiere][prof]:
                    profs_for_class[classe][matiere] = prof
                    break

    # Fonction pour essayer de placer toutes les séances d'une classe avec backtracking
    def place_for_class(classe):
        # si tout est vide -> success
        if all(len(lst) == 0 for lst in remaining[classe].values()):
            return True

        # choisir la matière la plus contraignante (celle avec le plus d'heures restantes)
        mat_choisie = max((m for m in remaining[classe] if remaining[classe][m]),
                          key=lambda m: sum(remaining[classe][m]), default=None)
        if mat_choisie is None:
            return True

        tab_de_seances = remaining[classe][mat_choisie]
        prof = profs_for_class[classe].get(mat_choisie)
        edt_classe = emplois_classes[classe]
        edt_prof = emplois_profs.get(prof, None) if prof is not None else None
        s_d = la_salle_dediee(classe)

        # Parcourir jours et moments
        niveau = classe_to_niveau.get(classe)
        for jour in ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']:
            # respecter contrainte Mercredi si nécessaire (original skip for certain niveaux)
            if jour == 'Mercredi' and niveau in ['6eme', '5eme']:
                continue
            moments = list(emplois_classes[classe][jour].keys())
            for moment in moments:
                les_heures_vides = [i for i in range(len(emplois_classes[classe][jour][moment])) if emplois_classes[classe][jour][moment][i] is None]
                # essayer sur chaque position vide
                for heure1 in list(les_heures_vides):
                    # essayer deux heures si possible
                    tried = False
                    if heure1 + 1 < len(emplois_classes[classe][jour][moment]) and emplois_classes[classe][jour][moment][heure1+1] is None:
                        if 2 in tab_de_seances:
                            # vérifier contrainte via fonction existante
                            if prog_deux_heures(mat_choisie, tab_de_seances, edt_classe, edt_prof, jour, heure1, heure1+1, moment, niveau, edt_salles, s_d):
                                # appliquer placement
                                save = (deepcopy(emplois_classes[classe]), deepcopy(emplois_profs.get(prof, None)), deepcopy(edt_salles))
                                emplois_classes[classe][jour][moment][heure1] = {"prof": prof, "matiere": mat_choisie, "salle": Les_interfaces.s_v}
                                emplois_classes[classe][jour][moment][heure1+1] = {"prof": prof, "matiere": mat_choisie, "salle": Les_interfaces.s_v}
                                if prof is not None:
                                    emplois_profs[prof][jour][moment][heure1] = {'classe': classe, 'salle': Les_interfaces.s_v}
                                    emplois_profs[prof][jour][moment][heure1+1] = {'classe': classe, 'salle': Les_interfaces.s_v}
                                edt_salles[Les_interfaces.s_v][jour][moment][heure1] = {'classe': classe, 'matiere': mat_choisie}
                                edt_salles[Les_interfaces.s_v][jour][moment][heure1+1] = {'classe': classe, 'matiere': mat_choisie}
                                # consommer la séance 2
                                tab_de_seances.remove(2)
                                # recursing
                                if place_for_class(classe):
                                    return True
                                # backtrack
                                tab_de_seances.append(2)
                                emplois_classes[classe] = save[0]
                                if prof is not None:
                                    emplois_profs[prof] = save[1]
                                edt_salles.clear()
                                edt_salles.update(save[2])
                                tried = True
                    # essayer une heure
                    if 1 in tab_de_seances:
                        if prog_une_heure(mat_choisie, tab_de_seances, edt_classe, edt_prof, jour, heure1, moment, niveau, edt_salles, s_d):
                            save = (deepcopy(emplois_classes[classe]), deepcopy(emplois_profs.get(prof, None)), deepcopy(edt_salles))
                            emplois_classes[classe][jour][moment][heure1] = {"prof": prof, "matiere": mat_choisie, "salle": Les_interfaces.s_v}
                            if prof is not None:
                                emplois_profs[prof][jour][moment][heure1] = {'classe': classe, 'salle': Les_interfaces.s_v}
                            edt_salles[Les_interfaces.s_v][jour][moment][heure1] = {'classe': classe, 'matiere': mat_choisie}
                            tab_de_seances.remove(1)
                            if place_for_class(classe):
                                return True
                            # backtrack
                            tab_de_seances.append(1)
                            emplois_classes[classe] = save[0]
                            if prof is not None:
                                emplois_profs[prof] = save[1]
                            edt_salles.clear()
                            edt_salles.update(save[2])
                            tried = True
                    # si on a essayé et rien ne marche on continue aux autres positions
                # fin positions
        # impossible de placer cette matière -> échec
        return False

    # Boucle principale : pour chaque classe, appeler place_for_class
    for classe in classes:
        success = place_for_class(classe)
        if not success:
            return None

    return emplois_classes, emplois_profs, edt_salles

__all__ = ["solve_emplois"]
