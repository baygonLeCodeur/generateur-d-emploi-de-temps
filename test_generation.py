#!/usr/bin/env python3
"""Script de test pour la génération d'emplois du temps"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genere_emploi_du_temps import genere_emploi_du_temps

if __name__ == "__main__":
    print("=" * 60)
    print("Test de génération des emplois du temps")
    print("=" * 60)
    
    try:
        genere_emploi_du_temps()
        print("\n✅ Test terminé avec succès")
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
