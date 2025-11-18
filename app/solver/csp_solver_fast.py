"""Solveur CSP rapide avec heuristiques optimisées.

Cette version utilise une approche gourmande avec des heuristiques fortes
pour réduire drastiquement le temps de calcul tout en respectant les contraintes.
"""
from copy import deepcopy
from mes_dictionnaires import Les_interfaces
import random


class FastScheduleSolver:
    """Solveur rapide avec approche gourmande et heuristiques"""
    
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
            
            for matiere in Les_interfaces.matieres_seances.get(niveau, {}).keys():
                if matiere == 'EPS':
                    continue
                for prof in Les_interfaces.repartition_classes.get(matiere, {}):
                    if classe in Les_interfaces.repartition_classes[matiere][prof]:
                        self.profs_for_class[classe][matiere] = prof
                        break
        
        # Séances restantes
        self.remaining = {}
        for classe in self.emplois_classes.keys():
            niveau = self.classe_to_niveau.get(classe)
            if niveau is None:
                self.remaining[classe] = {}
                continue
            
            self.remaining[classe] = {}
            for matiere, seances in Les_interfaces.matieres_seances.get(niveau, {}).items():
                if matiere == 'EPS':
                    continue
                if matiere in self.profs_for_class[classe]:
                    self.remaining[classe][matiere] = list(seances)
        
        # Salles dédiées
        self.salles_dediees = self._compute_salles_dediees()
    
    def _compute_salles_dediees(self):
        """Calculer les salles dédiées"""
        salles_dediees = {}
        cpt1, cpt2, cpt3 = 0, 0, 0
        
        for niveau in Les_interfaces.niveaux_classes:
            for classe in Les_interfaces.niveaux_classes[niveau]:
                try:
                    if niveau in ["6eme", "5eme", "4eme", "3eme"]:
                        salle_idx = cpt2 // 2 + cpt1
                        if salle_idx < len(Les_interfaces.salles):
                            if Les_interfaces.salles[salle_idx] not in salles_dediees:
                                salles_dediees[Les_interfaces.salles[salle_idx]] = []
                            salles_dediees[Les_interfaces.salles[salle_idx]].append(classe)
                        cpt2 += 1
                        cpt3 = cpt2 // 2 + cpt1 if cpt2 % 2 == 0 else cpt2 // 2 + cpt1 + 1
                    elif niveau in ["TleA2", "TleD", "TleC", "TleA1"]:
                        if cpt1 < len(Les_interfaces.salles):
                            salles_dediees[Les_interfaces.salles[cpt1]] = [classe]
                        cpt1 += 1
                    else:
                        if cpt3 < len(Les_interfaces.salles):
                            salles_dediees[Les_interfaces.salles[cpt3]] = [classe]
                        cpt3 += 1
                except IndexError:
                    pass
        return salles_dediees
    
    def get_salle_dediee(self, classe):
        """Obtenir la salle dédiée d'une classe"""
        for salle, classes in self.salles_dediees.items():
            if classe in classes:
                return salle
        return None
    
    def find_salle(self, classe, jour, moment, heure, duree):
        """Trouver une salle disponible"""
        # Essayer salle dédiée
        salle_ded = self.get_salle_dediee(classe)
        if salle_ded and moment in self.edt_salles[salle_ded][jour]:
            ok = all(
                h < len(self.edt_salles[salle_ded][jour][moment]) and
                self.edt_salles[salle_ded][jour][moment][h] is None
                for h in range(heure, heure + duree)
            )
            if ok:
                return salle_ded
        
        # Chercher autre salle
        for salle in Les_interfaces.salles:
            if moment not in self.edt_salles[salle][jour]:
                continue
            ok = all(
                h < len(self.edt_salles[salle][jour][moment]) and
                self.edt_salles[salle][jour][moment][h] is None
                for h in range(heure, heure + duree)
            )
            if ok:
                return salle
        return None
    
    def count_heures_jour(self, edt, jour):
        """Compter heures dans un jour"""
        return sum(
            sum(1 for c in edt[jour][m] if c is not None)
            for m in edt[jour]
        )
    
    def matiere_ce_jour(self, classe, jour, matiere):
        """Vérifier si matière déjà placée ce jour"""
        for m in self.emplois_classes[classe][jour]:
            if any(c and c.get("matiere") == matiere for c in self.emplois_classes[classe][jour][m]):
                return True
        return False
    
    def peut_placer(self, classe, matiere, jour, moment, heure, duree):
        """Vérifier si placement possible avec toutes les contraintes"""
        niveau = self.classe_to_niveau.get(classe)
        prof = self.profs_for_class[classe].get(matiere)
        
        # Contrainte: pas deux fois la même matière le même jour
        if self.matiere_ce_jour(classe, jour, matiere):
            return False, None
        
        # Vérifier disponibilité classe
        edt_cl = self.emplois_classes[classe]
        if moment not in edt_cl[jour]:
            return False, None
        
        if not all(
            h < len(edt_cl[jour][moment]) and edt_cl[jour][moment][h] is None
            for h in range(heure, heure + duree)
        ):
            return False, None
        
        # Contrainte: max heures/jour
        max_h = 5 if niveau in ["6eme", "5eme", "4eme", "3eme"] else 7
        if self.count_heures_jour(edt_cl, jour) + duree > max_h:
            return False, None
        
        # Contrainte: si matin complet, soir commence à H7 (indice 1)
        if moment == "Soir" and heure == 0:
            if "Matin" in edt_cl[jour] and all(c is not None for c in edt_cl[jour]["Matin"]):
                return False, None
        
        # Vérifier prof
        if prof and prof in self.emplois_profs:
            edt_pr = self.emplois_profs[prof]
            if moment not in edt_pr[jour]:
                return False, None
            
            if not all(
                h < len(edt_pr[jour][moment]) and edt_pr[jour][moment][h] is None
                for h in range(heure, heure + duree)
            ):
                return False, None
            
            # Max 7h/jour pour prof
            if self.count_heures_jour(edt_pr, jour) + duree > 7:
                return False, None
        
        # Trouver salle
        salle = self.find_salle(classe, jour, moment, heure, duree)
        if not salle:
            return False, None
        
        return True, salle
    
    def placer(self, classe, matiere, jour, moment, heure, duree, salle):
        """Placer une séance"""
        prof = self.profs_for_class[classe].get(matiere)
        
        for h in range(heure, heure + duree):
            self.emplois_classes[classe][jour][moment][h] = {
                "prof": prof, "matiere": matiere, "salle": salle
            }
            if prof and prof in self.emplois_profs:
                self.emplois_profs[prof][jour][moment][h] = {
                    'classe': classe, 'salle': salle
                }
            self.edt_salles[salle][jour][moment][h] = {
                'classe': classe, "matiere": matiere
            }
    
    def solve_greedy_classe(self, classe, debug=False):
        """Résoudre pour une classe avec approche gourmande"""
        niveau = self.classe_to_niveau.get(classe)
        
        # Créer une liste de toutes les séances à placer
        seances_a_placer = []
        for matiere in self.remaining[classe]:
            for duree in self.remaining[classe][matiere]:
                seances_a_placer.append((matiere, duree))
        
        # Trier: d'abord les séances de 2h, puis 1h
        seances_a_placer.sort(key=lambda x: x[1], reverse=True)
        
        if debug:
            print(f"  {len(seances_a_placer)} séances à placer")
        
        for i, (matiere, duree) in enumerate(seances_a_placer):
            placee = False
            
            # Créer une liste de créneaux possibles
            creneaux = []
            for jour in self.JOURS:
                # Skip mercredi pour 6eme/5eme
                if jour == 'Mercredi' and niveau in ['6eme', '5eme']:
                    continue
                
                moments = list(self.emplois_classes[classe][jour].keys())
                for moment in moments:
                    nb_slots = len(self.emplois_classes[classe][jour][moment])
                    for heure in range(nb_slots - duree + 1):
                        creneaux.append((jour, moment, heure))
            
            # Essayer les créneaux
            raisons_echec = []
            for jour, moment, heure in creneaux:
                ok, salle = self.peut_placer(classe, matiere, jour, moment, heure, duree)
                
                if ok:
                    self.placer(classe, matiere, jour, moment, heure, duree, salle)
                    self.remaining[classe][matiere].remove(duree)
                    placee = True
                    if debug:
                        print(f"  ✓ Séance {i+1}/{len(seances_a_placer)}: {matiere} {duree}h placée")
                    break
            
            if not placee:
                if debug:
                    print(f"  ✗ Impossible de placer {matiere} {duree}h")
                    print(f"    Créneaux testés: {len(creneaux)}")
                return False
        
        return True
    
    def reinit_from_original(self, emplois_classes_or, emplois_profs_or, emplois_salles_or):
        """Réinitialiser depuis les structures originales"""
        self.emplois_classes = deepcopy(emplois_classes_or)
        self.emplois_profs = deepcopy(emplois_profs_or)
        self.edt_salles = deepcopy(emplois_salles_or)
        
        # Réinitialiser remaining
        for classe in self.emplois_classes.keys():
            niveau = self.classe_to_niveau.get(classe)
            if niveau is None:
                self.remaining[classe] = {}
                continue
            
            self.remaining[classe] = {}
            for matiere, seances in Les_interfaces.matieres_seances.get(niveau, {}).items():
                if matiere == 'EPS':
                    continue
                if matiere in self.profs_for_class[classe]:
                    self.remaining[classe][matiere] = list(seances)
    
    def solve(self, max_retries=5, emplois_classes_or=None, emplois_profs_or=None, emplois_salles_or=None):
        """Résoudre pour toutes les classes avec plusieurs tentatives"""
        classes = list(self.emplois_classes.keys())
        
        # Trier par charge décroissante
        def charge(c):
            return sum(sum(self.remaining[c][m]) for m in self.remaining[c])
        
        classes.sort(key=charge, reverse=True)
        
        for retry in range(max_retries):
            if retry > 0:
                print(f"\n🔄 Tentative {retry + 1}/{max_retries}...")
                # Réinitialiser depuis les originaux
                if emplois_classes_or and emplois_profs_or and emplois_salles_or:
                    self.reinit_from_original(emplois_classes_or, emplois_profs_or, emplois_salles_or)
                # Mélanger légèrement l'ordre (garder les plus chargées en premier)
                import random
                # Séparer en groupes
                top = classes[:len(classes)//3]
                middle = classes[len(classes)//3:2*len(classes)//3]
                bottom = classes[2*len(classes)//3:]
                random.shuffle(top)
                random.shuffle(middle)
                random.shuffle(bottom)
                classes = top + middle + bottom
            
            success = True
            for i, classe in enumerate(classes):
                print(f"Résolution {classe} ({i+1}/{len(classes)})...")
                # Activer le debug occasionnellement
                debug = False  # Désactiver pour accélérer
                if not self.solve_greedy_classe(classe, debug=debug):
                    print(f"❌ Échec pour {classe}")
                    if retry == max_retries - 1:
                        # Afficher les détails à la dernière tentative
                        print(f"  Séances non placées:")
                        for mat, seances in self.remaining[classe].items():
                            if seances:
                                print(f"    {mat}: {seances}")
                    success = False
                    break
                print(f"✅ Succès {classe}")
            
            if success:
                return self.emplois_classes, self.emplois_profs, self.edt_salles
        
        return None


def solve_emplois(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or):
    """Point d'entrée du solveur rapide"""
    print("🚀 Solveur rapide démarré...")
    solver = FastScheduleSolver(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or)
    result = solver.solve(
        max_retries=5,
        emplois_classes_or=emplois_du_temps_classes_or,
        emplois_profs_or=emplois_du_temps_profs_or,
        emplois_salles_or=emplois_du_temps_salles_or
    )
    
    if result is None:
        print("❌ Échec")
        return None
    
    print("✅ Génération réussie!")
    return result


__all__ = ["solve_emplois"]
