import pytest
from app.model.validation import validate_for_generation, ValidationError
from app.model import reset_interfaces, load_matieres_seances
from mes_dictionnaires import Les_interfaces


def setup_function():
    reset_interfaces()
    load_matieres_seances()


def test_validate_success_minimal():
    # setup minimal valid structures
    Les_interfaces.salles = ["S1"]
    Les_interfaces.niveaux_classes = {"3eme": ["3eme 1"]}
    # creer repartition et noms pour une matiere issue de matieres_seances
    # prendre la première matière disponible
    niveau = next(iter(Les_interfaces.matieres_seances))
    mat = next(iter(Les_interfaces.matieres_seances[niveau]))
    Les_interfaces.repartition_classes[mat] = {mat + "_01": ["3eme 1"]}
    Les_interfaces.noms_professeurs[mat] = {mat + "_01": mat + " Prof"}

    # ne devrait pas lever d'erreur
    validate_for_generation()


def test_validate_missing_salles():
    Les_interfaces.salles = []
    Les_interfaces.niveaux_classes = {"3eme": ["3eme 1"]}
    with pytest.raises(ValidationError):
        validate_for_generation()
