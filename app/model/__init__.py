"""Model layer: expose les structures partagées et fonctions d'initialisation.
Ce module wrapper réutilise `mes_dictionnaires.py` et `matieres_seances.json`.
"""
from pathlib import Path
import json
import mes_dictionnaires

# Réexposer la classe Les_interfaces
Les_interfaces = mes_dictionnaires.Les_interfaces

def load_matieres_seances(path: str = None):
    """Charge (ou recharge) le fichier matieres_seances.json dans Les_interfaces."""
    if path is None:
        path = str(Path(__file__).resolve().parents[2] / "matieres_seances.json")
    with open(path, "r", encoding="utf-8") as f:
        Les_interfaces.matieres_seances = json.load(f)
    return Les_interfaces.matieres_seances

def reset_interfaces():
    """Reset rapide des structures partagées (utile pour tests)."""
    Les_interfaces.niveaux_classes = {}
    Les_interfaces.salles = []
    Les_interfaces.devoirs_de_niveaux = {}
    Les_interfaces.salles_devoir_de_niveau = {}
    Les_interfaces.repartition_classes = {}
    Les_interfaces.noms_professeurs = {}
    Les_interfaces.s_v = ""

__all__ = ["Les_interfaces", "load_matieres_seances", "reset_interfaces"]
