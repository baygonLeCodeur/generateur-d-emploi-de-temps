#!/usr/bin/env python3
"""
Script de test rapide pour le moteur de génération.
Version simplifiée pour tests rapides.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mes_dictionnaires import Les_interfaces
from fast_scheduler import generate_fast_schedule
from pdfLibrary import LesEmploisDeTpsClasses, LesEmploisDeTpsProfs


def main():
    """Fonction principale"""
    print("=" * 70)
    print("TEST RAPIDE DU GÉNÉRATEUR D'EMPLOIS DU TEMPS")
    print("=" * 70)
    
    # Vérifier que les données sont chargées
    if not Les_interfaces.niveaux_classes:
        print("❌ Aucune donnée chargée.")
        return 1
    
    total_classes = sum(len(c) for c in Les_interfaces.niveaux_classes.values())
    print(f"\n📚 Configuration: {len(Les_interfaces.niveaux_classes)} niveaux, "
          f"{total_classes} classes, {len(Les_interfaces.salles)} salles")
    
    # Générer les emplois du temps
    print("\n" + "=" * 70)
    result = generate_fast_schedule()
    
    if result is None:
        print("\n❌ La génération a échoué")
        return 1
    
    emplois_classes, emplois_profs, emplois_salles = result
    
    # Statistiques rapides
    print("\n📊 Statistiques:")
    total_heures_classes = 0
    for classe, edt in emplois_classes.items():
        heures = 0
        for jour in edt:
            for moment in edt[jour]:
                heures += sum(1 for c in edt[jour][moment] if c is not None)
        total_heures_classes += heures
    
    print(f"  - Total heures-classe: {total_heures_classes}")
    print(f"  - Classes avec emploi: {len(emplois_classes)}")
    print(f"  - Professeurs: {len(emplois_profs)}")
    
    # Générer les PDFs
    print("\n📄 Génération des PDFs...")
    try:
        lesEmploisDeTpsClasses = LesEmploisDeTpsClasses()
        for classe in emplois_classes:
            lesEmploisDeTpsClasses.rediger_edt(classe, emplois_classes[classe])
        lesEmploisDeTpsClasses.output("lesEmploisDeTpsClasses.pdf")
        print("✅ PDF classes généré")
    except Exception as e:
        print(f"❌ Erreur PDF classes: {e}")
    
    try:
        lesEmploisDeTpsProfs = LesEmploisDeTpsProfs()
        for prof_id in emplois_profs:
            prof_nom = None
            for matiere in Les_interfaces.noms_professeurs:
                if prof_id in Les_interfaces.noms_professeurs[matiere]:
                    prof_nom = Les_interfaces.noms_professeurs[matiere][prof_id]
                    break
            lesEmploisDeTpsProfs.rediger_edt(prof_id, prof_nom, emplois_profs[prof_id])
        lesEmploisDeTpsProfs.output("lesEmploisDeTpsProfs.pdf")
        print("✅ PDF professeurs généré")
    except Exception as e:
        print(f"❌ Erreur PDF profs: {e}")
    
    print("\n🎉 Test terminé !")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
