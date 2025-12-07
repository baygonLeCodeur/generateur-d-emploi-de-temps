#!/usr/bin/env python3
"""
Script de test pour le générateur amélioré.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mes_dictionnaires import Les_interfaces
from improved_genere import genere_emploi_du_temps_ameliore
from pdfLibrary import LesEmploisDeTpsClasses, LesEmploisDeTpsProfs


def main():
    print("=" * 70)
    print("TEST DU GÉNÉRATEUR AMÉLIORÉ")
    print("=" * 70)
    
    if not Les_interfaces.niveaux_classes:
        print("❌ Aucune donnée chargée.")
        return 1
    
    total_classes = sum(len(c) for c in Les_interfaces.niveaux_classes.values())
    print(f"\n📚 Configuration: {len(Les_interfaces.niveaux_classes)} niveaux, "
          f"{total_classes} classes, {len(Les_interfaces.salles)} salles")
    
    # Générer
    result = genere_emploi_du_temps_ameliore()
    
    if result is None or result[0] is None:
        print("\n❌ Échec de la génération")
        return 1
    
    emplois_classes, emplois_profs, emplois_salles = result
    
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
    
    print("\n🎉 Test terminé!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
