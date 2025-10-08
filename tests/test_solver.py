from app.model import reset_interfaces, load_matieres_seances
from mes_dictionnaires import Les_interfaces
from app.solver.csp_solver import solve_emplois


def setup_module():
    reset_interfaces()
    load_matieres_seances()


def test_solver_minimal():
    # configuration minimale
    Les_interfaces.salles = ["S1", "S2"]
    Les_interfaces.niveaux_classes = {"3eme": ["3eme 1"]}
    Les_interfaces.devoirs_de_niveaux = {"Lundi": [], "Mardi": [], "Mercredi": [], "Jeudi": [], "Vendredi": []}
    # peupler repartition et noms
    niveau = next(iter(Les_interfaces.matieres_seances))
    mat = next(iter(Les_interfaces.matieres_seances[niveau]))
    Les_interfaces.repartition_classes[mat] = {mat + "_01": ["3eme 1"]}
    Les_interfaces.noms_professeurs[mat] = {mat + "_01": mat + " Prof"}

    from les_dependances import emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or
    res = solve_emplois(emplois_du_temps_classes_or, emplois_du_temps_profs_or, emplois_du_temps_salles_or)
    assert res is not None
