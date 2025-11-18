#!/usr/bin/env python3
"""Script d'analyse de faisabilité des emplois du temps"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mes_dictionnaires import Les_interfaces

def analyser_charge_professeurs():
    """Analyser la charge de travail des professeurs"""
    print("=" * 70)
    print("ANALYSE DE LA CHARGE DES PROFESSEURS")
    print("=" * 70)
    
    charges_profs = {}
    
    for matiere in Les_interfaces.repartition_classes:
        for prof in Les_interfaces.repartition_classes[matiere]:
            if prof not in charges_profs:
                charges_profs[prof] = {'total': 0, 'classes': [], 'matieres': set()}
            
            classes = Les_interfaces.repartition_classes[matiere][prof]
            charges_profs[prof]['classes'].extend(classes)
            charges_profs[prof]['matieres'].add(matiere)
            
            # Calculer les heures pour chaque classe
            for classe in classes:
                # Trouver le niveau
                niveau = None
                for n in Les_interfaces.niveaux_classes:
                    if classe in Les_interfaces.niveaux_classes[n]:
                        niveau = n
                        break
                
                if niveau and matiere in Les_interfaces.matieres_seances.get(niveau, {}):
                    heures = sum(Les_interfaces.matieres_seances[niveau][matiere])
                    charges_profs[prof]['total'] += heures
    
    # Afficher les professeurs surchargés
    print("\nProfesseurs avec le plus d'heures:")
    profs_tries = sorted(charges_profs.items(), key=lambda x: x[1]['total'], reverse=True)
    
    for prof, info in profs_tries[:15]:
        nom = None
        for mat in Les_interfaces.noms_professeurs:
            if prof in Les_interfaces.noms_professeurs[mat]:
                nom = Les_interfaces.noms_professeurs[mat][prof]
                break
        
        print(f"\n{prof} ({nom if nom else 'Nom inconnu'}):")
        print(f"  Total heures/semaine: {info['total']}h")
        print(f"  Nombre de classes: {len(set(info['classes']))}")
        print(f"  Matières: {', '.join(info['matieres'])}")
        
        if info['total'] > 35:
            print(f"  ⚠️  SURCHARGÉ ! (> 35h/semaine, max 7h/jour impossible)")
        elif info['total'] > 28:
            print(f"  ⚠️  Charge élevée (> 28h/semaine)")

def analyser_confls_horaires():
    """Analyser les conflits potentiels d'horaires"""
    print("\n" + "=" * 70)
    print("ANALYSE DES CONFLITS POTENTIELS")
    print("=" * 70)
    
    # Pour chaque professeur, vérifier s'il doit enseigner à des classes
    # qui ont des contraintes horaires incompatibles
    for matiere in Les_interfaces.repartition_classes:
        for prof in Les_interfaces.repartition_classes[matiere]:
            classes = Les_interfaces.repartition_classes[matiere][prof]
            
            # Vérifier si certaines classes ont des jours de devoirs
            classes_avec_devoirs = []
            for classe in classes:
                niveau = None
                for n in Les_interfaces.niveaux_classes:
                    if classe in Les_interfaces.niveaux_classes[n]:
                        niveau = n
                        break
                
                if niveau:
                    for jour in Les_interfaces.devoirs_de_niveaux:
                        if niveau in Les_interfaces.devoirs_de_niveaux[jour]:
                            classes_avec_devoirs.append((classe, jour))
            
            if len(classes_avec_devoirs) > 0:
                print(f"\n{prof} ({matiere}):")
                print(f"  Classes avec jours de devoirs: {len(classes_avec_devoirs)}")
                for classe, jour in classes_avec_devoirs:
                    print(f"    {classe}: pas de cours {jour} après-midi")

if __name__ == "__main__":
    analyser_charge_professeurs()
    analyser_confls_horaires()
