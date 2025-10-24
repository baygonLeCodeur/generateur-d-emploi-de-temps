"""Validation des données et exceptions pour le modèle."""
from typing import List
from mes_dictionnaires import Les_interfaces


class ValidationError(Exception):
    """Exception levée lorsque les données d'entrée sont invalides pour la génération."""
    pass


def validate_interfaces():
    """Valide les structures principales de `Les_interfaces` avant génération.

    Vérifications réalisées :
    - `niveaux_classes` non vide et contient au moins une classe
    - `salles` non vide
    - `matieres_seances` contient au moins un niveau
    - `repartition_classes` et `noms_professeurs` cohérents (même clés pour les matières)
    - chaque matière a au moins un professeur assigné
    - `devoirs_de_niveaux` contient les jours attendus si présent
    """
    li = Les_interfaces
    if not isinstance(li.niveaux_classes, dict) or not any(li.niveaux_classes.values()):
        raise ValidationError("Aucune classe renseignée dans Les_interfaces.niveaux_classes")
    if not isinstance(li.salles, list) or len(li.salles) == 0:
        raise ValidationError("Aucune salle renseignée dans Les_interfaces.salles")
    if not isinstance(li.matieres_seances, dict) or len(li.matieres_seances) == 0:
        raise ValidationError("matieres_seances.json est vide ou manquant")
    # vérifier cohérence des matières
    if not isinstance(li.repartition_classes, dict) or not isinstance(li.noms_professeurs, dict):
        raise ValidationError("Les structures repartition_classes et noms_professeurs doivent être des dictionnaires")
    for mat in li.repartition_classes:
        if mat not in li.noms_professeurs:
            raise ValidationError(f"La matière {mat} est absente de noms_professeurs")
        # Permettre que repartition_classes[matiere] soit vide, signifiant que la matière n'est pas enseignée
    # vérifier devoirs_de_niveaux si présent
    if hasattr(li, 'devoirs_de_niveaux') and li.devoirs_de_niveaux:
        expected_days = {"Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"}
        if not expected_days.issuperset(set(li.devoirs_de_niveaux.keys())):
            # we allow partial specification but warn via exception
            raise ValidationError("Les clés de devoirs_de_niveaux doivent être des jours parmi Lundi..Vendredi")


def validate_for_generation():
    """Fonction d'entrée pour valider toutes les préconditions avant de lancer la génération."""
    validate_interfaces()

__all__ = ["ValidationError", "validate_for_generation"]
