"""
Générateur d'emplois du temps rapide avec approche gourmande.
Version optimisée pour les performances au détriment de l'exhaustivité.

Auteur: Claude AI - Version rapide du générateur
Date: Décembre 2025
"""

import copy
import random
from typing import Dict, List, Tuple, Optional
from optimized_scheduler import (
    TimeSlot, Course, ScheduleValidator, SalleManager, OptimizedScheduler
)
from mes_dictionnaires import Les_interfaces


class FastScheduler(OptimizedScheduler):
    """
    Générateur rapide avec approche gourmande.
    Privilégie la vitesse sur l'exhaustivité.
    """
    
    def solve_greedy(
        self,
        courses: List[Course],
        edt_classes: Dict,
        edt_profs: Dict,
        edt_salles: Dict,
        max_retries: int = 10
    ) -> Tuple[bool, int]:
        """
        Résout le problème avec une approche gourmande.
        Retourne (succès, nombre_de_cours_placés).
        """
        placed_count = 0
        retry_count = 0
        
        while retry_count < max_retries:
            # Réinitialiser pour un nouveau try
            if retry_count > 0:
                edt_classes = copy.deepcopy(edt_classes)
                edt_profs = copy.deepcopy(edt_profs)
                edt_salles = copy.deepcopy(edt_salles)
                placed_count = 0
            
            # Mélanger l'ordre des cours pour diversifier
            courses_shuffled = courses.copy()
            random.shuffle(courses_shuffled)
            
            # Essayer de placer chaque cours
            for course in courses_shuffled:
                # Obtenir les créneaux possibles
                possible_slots = self._get_smart_slots(course, edt_classes, edt_profs)
                
                # Essayer chaque créneau
                placed = False
                for slot in possible_slots:
                    if self.can_place_course(course, slot, edt_classes, edt_profs, edt_salles):
                        self.place_course(course, slot, edt_classes, edt_profs, edt_salles)
                        placed_count += 1
                        placed = True
                        break
                
                # Si on ne peut pas placer ce cours, on abandonne cette tentative
                if not placed:
                    break
            
            # Si tous les cours sont placés, succès!
            if placed_count == len(courses):
                # Mettre à jour les emplois du temps de l'objet
                self.emplois_classes = edt_classes
                self.emplois_profs = edt_profs
                self.emplois_salles = edt_salles
                return True, placed_count
            
            retry_count += 1
        
        # Échec après toutes les tentatives
        # Garder le meilleur résultat
        self.emplois_classes = edt_classes
        self.emplois_profs = edt_profs
        self.emplois_salles = edt_salles
        return False, placed_count
    
    def _get_smart_slots(
        self,
        course: Course,
        edt_classes: Dict,
        edt_profs: Dict
    ) -> List[TimeSlot]:
        """
        Retourne les créneaux les plus prometteurs en premier.
        Heuristiques pour accélérer le placement.
        """
        classe = course.classe
        prof = course.prof
        duree = course.duree
        
        slots = []
        
        # Priorité 1: Jours avec peu de cours
        jour_heures = {}
        for jour in ScheduleValidator.JOURS:
            heures = self.validator.count_heures_jour(edt_classes[classe], jour)
            jour_heures[jour] = heures
        
        # Trier les jours par nombre d'heures croissant
        jours_tries = sorted(jour_heures.keys(), key=lambda j: jour_heures[j])
        
        for jour in jours_tries:
            # Priorité 2: Matin d'abord (généralement moins de conflits)
            for moment in ["Matin", "Soir"]:
                if moment not in edt_classes[classe].get(jour, {}):
                    continue
                
                if moment not in edt_profs[prof].get(jour, {}):
                    continue
                
                # Priorité 3: Début de plage (pour faciliter la contiguïté)
                max_heure = 5 - duree
                for heure in range(max_heure + 1):
                    slots.append(TimeSlot(jour, moment, heure))
        
        return slots
    
    def generate_fast(self) -> Tuple[Dict, Dict, Dict]:
        """
        Génère les emplois du temps avec l'approche rapide.
        Retourne (emplois_classes, emplois_profs, emplois_salles)
        """
        print("🚀 Démarrage de la génération rapide...")
        
        # Initialiser les structures
        self.initialize_schedules()
        print(f"✅ Structures initialisées: {len(self.emplois_classes)} classes, "
              f"{len(self.emplois_profs)} professeurs, {len(self.emplois_salles)} salles")
        
        # Construire la liste des cours à placer
        courses = self.build_courses_list()
        print(f"📚 {len(courses)} cours à placer (hors EPS)")
        
        # Trier les cours par contraintes (les plus contraints en premier)
        courses.sort(key=lambda c: (-c.duree, c.classe, c.matiere))
        
        # Résoudre avec approche gourmande
        print("🔍 Résolution avec algorithme glouton...")
        success, placed_count = self.solve_greedy(
            courses,
            self.emplois_classes,
            self.emplois_profs,
            self.emplois_salles,
            max_retries=20  # Augmenter le nombre de tentatives
        )
        
        if success:
            print(f"✅ Tous les cours ({placed_count}/{len(courses)}) ont été placés avec succès!")
        else:
            print(f"⚠️  Génération partielle: {placed_count}/{len(courses)} cours placés")
        
        # Placer les cours d'EPS
        self.place_eps_courses()
        
        return self.emplois_classes, self.emplois_profs, self.emplois_salles


def generate_fast_schedule() -> Optional[Tuple[Dict, Dict, Dict]]:
    """
    Point d'entrée pour la génération rapide.
    Retourne (emplois_classes, emplois_profs, emplois_salles) ou None en cas d'erreur.
    """
    try:
        scheduler = FastScheduler()
        return scheduler.generate_fast()
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
        return None
