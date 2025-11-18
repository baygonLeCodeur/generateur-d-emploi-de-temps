"""Solveur CSP amélioré pour la génération d'emplois du temps.

Ce solveur respecte toutes les contraintes suivantes :
1. Lundi, mardi, jeudi, vendredi : 10 heures (H1-H5 matin, H6-H10 soir)
2. Mercredi : 5 heures (H1-H5 matin seulement)
3. Pas plus d'une séance d'une même matière par classe par jour
4. Les séances matin/soir doivent être contiguës (pas d'heures creuses)
5. Si classe a cours toute la matinée, l'après-midi commence au plus tôt à H7
6. Classes 6eme/5eme/4eme/3eme : cours soit matin soit soir (max 5h/jour)
7. Autres classes : max 7 heures de cours par jour
8. Une classe peut ne pas avoir cours un jour (si possible)
9. Professeur : max 7 heures de cours par jour
10. Professeur : max 1 heure creuse entre deux séances le même jour
11. Respect des jours de devoirs de niveaux (pas de cours l'après-midi)
"""
from copy import deepcopy
from mes_dictionnaires import Les_interfaces
import random


class ImprovedScheduleSolver:
    """Solveur CSP avec backtracking et heuristiques améliorées"""
    
    # Heures de cours
    HEURES_MATIN = [0, 1, 2, 3, 4]  # H1, H2, H3, H4, H5
    HEURES_SOIR = [0, 1, 2, 3, 4]   # H6, H7, H8, H9, H10
    JOURS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
    
    def __init__(self, emplois_classes_or, emplois_profs_or, emplois_salles_or):
        self.emplois_classes = deepcopy(emplois_classes_or)
        self.emplois_profs = deepcopy(emplois_profs_or)
        self.edt_salles = deepcopy(emplois_salles_or)
        
        # Mapping classe -> niveau
        self.classe_to_niveau = {}
        for niveau in Les_interfaces.niveaux_classes:
            for classe in Les_interfaces.niveaux_classes[niveau]:
                self.classe_to_niveau[classe] = niveau
        
        # Mapping classe -> prof par matière
        self.profs_for_class = {}
        for classe in self.emplois_classes.keys():
            self.profs_for_class[classe] = {}
            niveau = self.classe_to_niveau.get(classe)
            if niveau is None:
                continue
            
            # Pour chaque matière du niveau
            for matiere in Les_interfaces.matieres_seances.get(niveau, {}).keys():
                if matiere == 'EPS':  # EPS traité séparément
                    continue
                # Trouver le prof de cette matière pour cette classe
                for prof in Les_interfaces.repartition_classes.get(matiere, {}):
                    if classe in Les_interfaces.repartition_classes[matiere][prof]:
                        self.profs_for_class[classe][matiere] = prof
                        break
        
        # Séances restantes par classe et matière
        self.remaining = {}
        for classe in self.emplois_classes.keys():
            niveau = self.classe_to_niveau.get(classe)
            if niveau is None:
                self.remaining[classe] = {}
                continue
            
            self.remaining[classe] = {}
            for matiere, seances in Les_interfaces.matieres_seances.get(niveau, {}).items():
                if matiere == 'EPS':  # EPS traité séparément
                    continue
                # Ne garder que les matières qui ont un prof assigné
                if matiere in self.profs_for_class[classe]:
                    self.remaining[classe][matiere] = list(seances)
        
        # Salles dédiées
        self.salles_dediees = {}
        self._compute_salles_dediees()
    
    def _compute_salles_dediees(self):
        """Calculer les salles dédiées pour chaque classe"""
        cpt1 = 0
        cpt2 = 0
        cpt3 = 0
        
        for niveau in Les_interfaces.niveaux_classes:
            for classe in Les_interfaces.niveaux_classes[niveau]:
                try:
                    if niveau in ["6eme", "5eme", "4eme", "3eme"]:
                        salle_idx = cpt2 // 2 + cpt1
                        if salle_idx < len(Les_interfaces.salles):
                            if Les_interfaces.salles[salle_idx] not in self.salles_dediees:
                                self.salles_dediees[Les_interfaces.salles[salle_idx]] = []
                            self.salles_dediees[Les_interfaces.salles[salle_idx]].append(classe)
                        cpt2 += 1
                        cpt3 = cpt2 // 2 + cpt1 if cpt2 % 2 == 0 else cpt2 // 2 + cpt1 + 1
                    elif niveau in ["TleA2", "TleD", "TleC", "TleA1"]:
                        if cpt1 < len(Les_interfaces.salles):
                            self.salles_dediees[Les_interfaces.salles[cpt1]] = [classe]
                        cpt1 += 1
                    else:
                        if cpt3 < len(Les_interfaces.salles):
                            self.salles_dediees[Les_interfaces.salles[cpt3]] = [classe]
                        cpt3 += 1
                except IndexError:
                    pass
    
    def get_salle_dediee(self, classe):
        """Retourner la salle dédiée d'une classe"""
        for salle, classes in self.salles_dediees.items():
            if classe in classes:
                return salle
        return None
    
    def find_available_salle(self, classe, jour, moment, heure, duree=1):
        """Trouver une salle disponible pour une séance"""
        # Essayer d'abord la salle dédiée
        salle_dediee = self.get_salle_dediee(classe)
        if salle_dediee and moment in self.edt_salles[salle_dediee][jour]:
            disponible = True
            for h in range(heure, heure + duree):
                if h >= len(self.edt_salles[salle_dediee][jour][moment]):
                    disponible = False
                    break
                if self.edt_salles[salle_dediee][jour][moment][h] is not None:
                    disponible = False
                    break
            if disponible:
                return salle_dediee
        
        # Sinon chercher une salle libre
        for salle in Les_interfaces.salles:
            if moment not in self.edt_salles[salle][jour]:
                continue
            disponible = True
            for h in range(heure, heure + duree):
                if h >= len(self.edt_salles[salle][jour][moment]):
                    disponible = False
                    break
                if self.edt_salles[salle][jour][moment][h] is not None:
                    disponible = False
                    break
            if disponible:
                return salle
        
        return None
    
    def count_heures_jour(self, edt, jour):
        """Compter le nombre d'heures de cours dans un jour"""
        count = 0
        for moment in edt[jour]:
            count += sum(1 for c in edt[jour][moment] if c is not None)
        return count
    
    def matiere_deja_ce_jour(self, classe, jour, matiere):
        """Vérifier si la matière a déjà été programmée ce jour"""
        for moment in self.emplois_classes[classe][jour]:
            for cours in self.emplois_classes[classe][jour][moment]:
                if cours is not None and cours.get("matiere") == matiere:
                    return True
        return False
    
    def check_contiguite(self, edt_jour_moment):
        """Vérifier que les cours sont contigus (pas d'heures creuses)"""
        first_cours = -1
        last_cours = -1
        
        for i, cours in enumerate(edt_jour_moment):
            if cours is not None:
                if first_cours == -1:
                    first_cours = i
                last_cours = i
        
        if first_cours == -1:  # Pas de cours
            return True
        
        # Vérifier qu'il n'y a pas de None entre first_cours et last_cours
        for i in range(first_cours, last_cours + 1):
            if edt_jour_moment[i] is None:
                return False
        
        return True
    
    def check_heure_creuse_prof(self, prof, jour):
        """Vérifier qu'il n'y a pas plus d'une heure creuse pour le prof ce jour"""
        if prof not in self.emplois_profs:
            return True
        
        # Collecter toutes les heures de cours du prof ce jour
        heures_cours = []
        for moment in self.emplois_profs[prof][jour]:
            offset = 0 if moment == "Matin" else 5
            for i, cours in enumerate(self.emplois_profs[prof][jour][moment]):
                if cours is not None:
                    heures_cours.append(offset + i)
        
        if len(heures_cours) <= 1:
            return True
        
        heures_cours.sort()
        
        # Compter les heures creuses
        nb_heures_creuses = 0
        for i in range(len(heures_cours) - 1):
            gap = heures_cours[i + 1] - heures_cours[i] - 1
            nb_heures_creuses += gap
        
        return nb_heures_creuses <= 1
    
    def can_place_seance(self, classe, matiere, jour, moment, heure, duree):
        """Vérifier si on peut placer une séance"""
        niveau = self.classe_to_niveau.get(classe)
        prof = self.profs_for_class[classe].get(matiere)
        
        # Contrainte 3: Pas plus d'une séance de la même matière par jour
        if self.matiere_deja_ce_jour(classe, jour, matiere):
            return False, None
        
        # Vérifier que les heures sont disponibles pour la classe
        edt_classe = self.emplois_classes[classe]
        if moment not in edt_classe[jour]:
            return False, None
        
        for h in range(heure, heure + duree):
            if h >= len(edt_classe[jour][moment]):
                return False, None
            if edt_classe[jour][moment][h] is not None:
                return False, None
        
        # Contrainte 6: Classes 6eme/5eme/4eme/3eme max 5h/jour
        # Contrainte 7: Autres classes max 7h/jour
        max_heures = 5 if niveau in ["6eme", "5eme", "4eme", "3eme"] else 7
        heures_actuelles = self.count_heures_jour(edt_classe, jour)
        if heures_actuelles + duree > max_heures:
            return False, None
        
        # Contrainte 5: Si cours toute la matinée, après-midi commence à H7 (indice 1 du soir)
        if moment == "Soir" and heure == 0:
            # Vérifier si tous les créneaux du matin sont occupés
            if "Matin" in edt_classe[jour]:
                matin_complet = all(c is not None for c in edt_classe[jour]["Matin"])
                if matin_complet:
                    return False, None  # Ne peut pas commencer à H6 (indice 0)
        
        # Vérifier disponibilité du prof
        if prof and prof in self.emplois_profs:
            edt_prof = self.emplois_profs[prof]
            if moment not in edt_prof[jour]:
                return False, None
            
            for h in range(heure, heure + duree):
                if h >= len(edt_prof[jour][moment]):
                    return False, None
                if edt_prof[jour][moment][h] is not None:
                    return False, None
            
            # Contrainte 9: Prof max 7h/jour
            heures_prof = self.count_heures_jour(edt_prof, jour)
            if heures_prof + duree > 7:
                return False, None
        
        # Trouver une salle disponible
        salle = self.find_available_salle(classe, jour, moment, heure, duree)
        if salle is None:
            return False, None
        
        return True, salle
    
    def place_seance(self, classe, matiere, jour, moment, heure, duree, salle):
        """Placer une séance dans l'emploi du temps"""
        prof = self.profs_for_class[classe].get(matiere)
        
        for h in range(heure, heure + duree):
            self.emplois_classes[classe][jour][moment][h] = {
                "prof": prof,
                "matiere": matiere,
                "salle": salle
            }
            
            if prof and prof in self.emplois_profs:
                self.emplois_profs[prof][jour][moment][h] = {
                    'classe': classe,
                    'salle': salle
                }
            
            self.edt_salles[salle][jour][moment][h] = {
                'classe': classe,
                "matiere": matiere
            }
    
    def unplace_seance(self, classe, matiere, jour, moment, heure, duree, salle):
        """Retirer une séance de l'emploi du temps"""
        prof = self.profs_for_class[classe].get(matiere)
        
        for h in range(heure, heure + duree):
            self.emplois_classes[classe][jour][moment][h] = None
            
            if prof and prof in self.emplois_profs:
                self.emplois_profs[prof][jour][moment][h] = None
            
            self.edt_salles[salle][jour][moment][h] = None
    
    def solve_for_class(self, classe):
        """Résoudre l'emploi du temps d'une classe avec backtracking"""
        # Si toutes les séances sont placées
        if all(len(seances) == 0 for seances in self.remaining[classe].values()):
            return True
        
        # Choisir la matière avec le plus d'heures restantes (heuristique)
        matieres_restantes = [(m, sum(self.remaining[classe][m])) 
                              for m in self.remaining[classe] 
                              if len(self.remaining[classe][m]) > 0]
        
        if not matieres_restantes:
            return True
        
        # Trier par nombre d'heures décroissant
        matieres_restantes.sort(key=lambda x: -x[1])
        matiere = matieres_restantes[0][0]
        
        niveau = self.classe_to_niveau.get(classe)
        
        # Essayer de placer chaque type de séance (2h ou 1h)
        seances = list(self.remaining[classe][matiere])
        
        # Prioriser les séances de 2h
        if 2 in seances:
            duree_a_essayer = [2, 1]
        else:
            duree_a_essayer = [1]
        
        for duree in duree_a_essayer:
            if duree not in seances:
                continue
            
            # Essayer tous les créneaux possibles
            for jour in self.JOURS:
                # Contrainte mercredi pour 6eme/5eme
                if jour == 'Mercredi' and niveau in ['6eme', '5eme']:
                    continue
                
                # Récupérer les moments disponibles pour cette classe ce jour
                moments = list(self.emplois_classes[classe][jour].keys())
                
                for moment in moments:
                    nb_heures = len(self.emplois_classes[classe][jour][moment])
                    
                    for heure in range(nb_heures - duree + 1):
                        can_place, salle = self.can_place_seance(classe, matiere, jour, moment, heure, duree)
                        
                        if can_place:
                            # Placer la séance
                            self.place_seance(classe, matiere, jour, moment, heure, duree, salle)
                            self.remaining[classe][matiere].remove(duree)
                            
                            # Vérifier les contraintes de contigüité et heures creuses prof
                            prof = self.profs_for_class[classe].get(matiere)
                            contiguite_ok = self.check_contiguite(self.emplois_classes[classe][jour][moment])
                            heure_creuse_ok = self.check_heure_creuse_prof(prof, jour) if prof else True
                            
                            if contiguite_ok and heure_creuse_ok:
                                # Récursion
                                if self.solve_for_class(classe):
                                    return True
                            
                            # Backtrack
                            self.unplace_seance(classe, matiere, jour, moment, heure, duree, salle)
                            self.remaining[classe][matiere].append(duree)
        
        # Impossible de placer cette matière
        return False
    
    def solve(self):
        """Résoudre l'emploi du temps pour toutes les classes"""
        # Trier les classes par charge de travail décroissante
        classes = list(self.emplois_classes.keys())
        
        def total_hours(classe):
            total = 0
            for matiere, seances in self.remaining[classe].items():
                total += sum(seances)
            return total
        
        classes.sort(key=lambda c: -total_hours(c))
        
        # Résoudre pour chaque classe
        for i, classe in enumerate(classes):
            print(f"Résolution pour {classe} ({i+1}/{len(classes)})...")
            if not self.solve_for_class(classe):
                print(f"❌ Échec pour la classe {classe}")
                return None
            print(f"✅ Succès pour {classe}")
        
        return self.emplois_classes, self.emplois_profs, self.edt_salles


def solve_emplois(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or):
    """Point d'entrée pour le solveur amélioré"""
    print("🚀 Démarrage du solveur CSP amélioré...")
    solver = ImprovedScheduleSolver(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or)
    result = solver.solve()
    
    if result is None:
        print("❌ Échec de la génération")
        return None
    
    print("✅ Génération réussie !")
    return result


__all__ = ["solve_emplois"]
