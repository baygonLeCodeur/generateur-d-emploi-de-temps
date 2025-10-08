"""View layer: fabrique les composants UI en s'appuyant sur les widgets existants.
Ce wrapper permet d'importer les composants UI depuis l'ancien code sans modification lourde.
"""
from ...main_form_ui import Ui_MainWindow
from ...saisie_nombres_de_classes import Saisie_nombres_de_classes
from ...saisie_nbres_de_profs import Saisie_nbres_de_profs
from ...nommage_profs import Nommage_profs
from ...nommer_profs_edhc import Nommer_profs_edhc
from ...affect_class_a_prof import Affect_class_a_prof

__all__ = [
    "Ui_MainWindow",
    "Saisie_nombres_de_classes",
    "Saisie_nbres_de_profs",
    "Nommage_profs",
    "Nommer_profs_edhc",
    "Affect_class_a_prof",
]
