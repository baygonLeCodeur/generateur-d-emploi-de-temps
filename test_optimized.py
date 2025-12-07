#!/usr/bin/env python3
"""
Script de test pour le moteur optimisé de génération d'emplois du temps.
Charge les données de session et génère les emplois du temps.
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mes_dictionnaires import Les_interfaces
from optimized_scheduler import generate_optimized_schedule
from pdfLibrary import LesEmploisDeTpsClasses, LesEmploisDeTpsProfs


def print_schedule_stats(emplois_classes, emplois_profs):
    """Affiche des statistiques sur les emplois du temps générés"""
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES DES EMPLOIS DU TEMPS")
    print("=" * 70)
    
    # Statistiques par classe
    print("\n📚 Classes:")
    for classe in sorted(emplois_classes.keys()):
        total_heures = 0
        matieres = set()
        
        for jour in emplois_classes[classe]:
            for moment in emplois_classes[classe][jour]:
                for cours in emplois_classes[classe][jour][moment]:
                    if cours is not None:
                        total_heures += 1
                        matieres.add(cours.get("matiere", ""))
        
        print(f"  {classe:15s} : {total_heures:2d}h/semaine, {len(matieres)} matières")
    
    # Statistiques par professeur
    print("\n👨‍🏫 Professeurs:")
    for prof in sorted(emplois_profs.keys()):
        total_heures = 0
        classes = set()
        
        for jour in emplois_profs[prof]:
            for moment in emplois_profs[prof][jour]:
                if moment and emplois_profs[prof][jour][moment]:
                    for cours in emplois_profs[prof][jour][moment]:
                        if cours is not None:
                            total_heures += 1
                            classes.add(cours.get("classe", ""))
        
        # Trouver le nom du prof
        prof_nom = None
        for matiere in Les_interfaces.noms_professeurs:
            if prof in Les_interfaces.noms_professeurs[matiere]:
                prof_nom = Les_interfaces.noms_professeurs[matiere][prof]
                break
        
        nom_affiche = f"{prof} ({prof_nom})" if prof_nom else prof
        print(f"  {nom_affiche:30s} : {total_heures:2d}h/semaine, {len(classes)} classes")
    
    print("\n" + "=" * 70)


def validate_all_constraints(emplois_classes, emplois_profs):
    """Valide toutes les contraintes sur les emplois du temps générés"""
    print("\n" + "=" * 70)
    print("🔍 VALIDATION DES CONTRAINTES")
    print("=" * 70)
    
    errors = []
    warnings = []
    
    # Validation par classe
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
                for i, cours in enumerate(edt[jour][moment]):
                    if cours is not None:
                        heures_jour += 1
                        matiere = cours.get("matiere")
                        
                        # Vérifier: pas plus d'une séance de la même matière par jour
                        if matiere in matieres_jour:
                            errors.append(
                                f"❌ {classe} - {jour}: matière {matiere} apparaît plus d'une fois"
                            )
                        matieres_jour[matiere] = True
            
            # Vérifier: limites d'heures par jour
            if niveau in ["6eme", "5eme", "4eme", "3eme"]:
                if heures_jour > 5:
                    errors.append(
                        f"❌ {classe} - {jour}: {heures_jour}h > 5h (max pour collège)"
                    )
                
                # Vérifier: matin OU soir uniquement pour le collège
                has_matin = "Matin" in edt[jour] and any(
                    c is not None for c in edt[jour]["Matin"]
                )
                has_soir = "Soir" in edt[jour] and any(
                    c is not None for c in edt[jour]["Soir"]
                )
                
                if has_matin and has_soir:
                    errors.append(
                        f"❌ {classe} - {jour}: cours matin ET soir (interdit pour collège)"
                    )
            else:
                if heures_jour > 7:
                    errors.append(
                        f"❌ {classe} - {jour}: {heures_jour}h > 7h (max pour lycée)"
                    )
            
            # Vérifier la contiguïté
            for moment in ["Matin", "Soir"]:
                if moment in edt[jour]:
                    plage = edt[jour][moment]
                    first = None
                    last = None
                    
                    for i, cours in enumerate(plage):
                        if cours is not None:
                            if first is None:
                                first = i
                            last = i
                    
                    if first is not None and last is not None:
                        for i in range(first, last + 1):
                            if plage[i] is None:
                                errors.append(
                                    f"❌ {classe} - {jour} {moment}: heure creuse détectée (index {i})"
                                )
            
            # Vérifier la règle: matin complet => début après-midi à H7 minimum
            if "Matin" in edt[jour] and "Soir" in edt[jour]:
                nb_matin = sum(1 for c in edt[jour]["Matin"] if c is not None)
                if nb_matin == 5:  # Matin complet
                    if edt[jour]["Soir"][0] is not None:  # H6 occupé
                        errors.append(
                            f"❌ {classe} - {jour}: matin complet mais cours à H6 (doit commencer à H7)"
                        )
    
    # Validation par professeur
    for prof, edt in emplois_profs.items():
        for jour in edt:
            heures_jour = 0
            cours_positions = []
            
            for moment in edt[jour]:
                if moment and edt[jour][moment]:
                    for i, cours in enumerate(edt[jour][moment]):
                        if cours is not None:
                            heures_jour += 1
                            pos = i if moment == "Matin" else i + 5
                            cours_positions.append(pos)
            
            # Vérifier: max 7h par jour
            if heures_jour > 7:
                errors.append(
                    f"❌ Prof {prof} - {jour}: {heures_jour}h > 7h"
                )
            
            # Vérifier: max 1h creuse entre deux cours
            if len(cours_positions) > 1:
                cours_positions.sort()
                for i in range(len(cours_positions) - 1):
                    ecart = cours_positions[i + 1] - cours_positions[i] - 1
                    if ecart > 1:
                        errors.append(
                            f"❌ Prof {prof} - {jour}: {ecart} heures creuses entre cours"
                        )
    
    # Afficher les résultats
    if errors:
        print("\n❌ CONTRAINTES VIOLÉES:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ Toutes les contraintes sont respectées !")
    
    if warnings:
        print("\n⚠️  AVERTISSEMENTS:")
        for warning in warnings:
            print(f"  {warning}")
    
    print("\n" + "=" * 70)
    
    return len(errors) == 0


def main():
    """Fonction principale"""
    print("=" * 70)
    print("TEST DU MOTEUR OPTIMISÉ DE GÉNÉRATION D'EMPLOIS DU TEMPS")
    print("=" * 70)
    
    # Vérifier que les données sont chargées
    if not Les_interfaces.niveaux_classes:
        print("❌ Aucune donnée chargée. Veuillez d'abord configurer l'application.")
        return 1
    
    print(f"\n📚 Configuration chargée:")
    print(f"  - Niveaux: {len(Les_interfaces.niveaux_classes)}")
    print(f"  - Classes: {sum(len(c) for c in Les_interfaces.niveaux_classes.values())}")
    print(f"  - Salles: {len(Les_interfaces.salles)}")
    print(f"  - Matières: {len(Les_interfaces.matieres_seances)}")
    
    # Générer les emplois du temps
    print("\n" + "=" * 70)
    result = generate_optimized_schedule()
    
    if result is None:
        print("\n❌ La génération a échoué")
        return 1
    
    emplois_classes, emplois_profs, emplois_salles = result
    
    # Afficher les statistiques
    print_schedule_stats(emplois_classes, emplois_profs)
    
    # Valider les contraintes
    all_valid = validate_all_constraints(emplois_classes, emplois_profs)
    
    # Générer les PDFs
    print("\n" + "=" * 70)
    print("📄 GÉNÉRATION DES FICHIERS PDF")
    print("=" * 70)
    
    try:
        print("\n📄 Génération des emplois du temps des classes...")
        lesEmploisDeTpsClasses = LesEmploisDeTpsClasses()
        for classe in emplois_classes:
            lesEmploisDeTpsClasses.rediger_edt(classe, emplois_classes[classe])
        lesEmploisDeTpsClasses.output("lesEmploisDeTpsClasses.pdf")
        print("✅ PDF des classes généré : lesEmploisDeTpsClasses.pdf")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF des classes : {e}")
        import traceback
        traceback.print_exc()
    
    try:
        print("\n📄 Génération des emplois du temps des professeurs...")
        lesEmploisDeTpsProfs = LesEmploisDeTpsProfs()
        for prof_id in emplois_profs:
            # Trouver le nom du professeur
            prof_nom = None
            for matiere in Les_interfaces.noms_professeurs:
                if prof_id in Les_interfaces.noms_professeurs[matiere]:
                    prof_nom = Les_interfaces.noms_professeurs[matiere][prof_id]
                    break
            lesEmploisDeTpsProfs.rediger_edt(prof_id, prof_nom, emplois_profs[prof_id])
        lesEmploisDeTpsProfs.output("lesEmploisDeTpsProfs.pdf")
        print("✅ PDF des professeurs généré : lesEmploisDeTpsProfs.pdf")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF des professeurs : {e}")
        import traceback
        traceback.print_exc()
    
    # Résumé final
    print("\n" + "=" * 70)
    if all_valid:
        print("🎉 SUCCÈS COMPLET ! Tous les emplois du temps respectent les contraintes.")
    else:
        print("⚠️  SUCCÈS PARTIEL : Certaines contraintes ne sont pas respectées.")
    print("=" * 70)
    
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
