"""Controller léger: orchestration entre model et view et point d'entrée applicatif MVC."""
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget
import sys
from ..model import Les_interfaces, load_matieres_seances
from ..view import Ui_MainWindow, Saisie_nombres_de_classes
from ..model.validation import validate_for_generation, ValidationError
from PySide6.QtWidgets import QMessageBox


class AppController:
    def __init__(self):
        # chargement des données de matières
        load_matieres_seances()

    def run(self):
        app = QApplication(sys.argv)
        main_window = QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(main_window)

        # Appliquer feuille de style si disponible
        try:
            import os
            qss_path = os.path.join(os.path.dirname(__file__), '..', 'view', 'style.qss')
            qss_path = os.path.normpath(qss_path)
            if os.path.exists(qss_path):
                with open(qss_path, 'r', encoding='utf-8') as f:
                    app.setStyleSheet(f.read())
        except Exception:
            pass

        WFStackedWidget = QStackedWidget()
        inner_layout = QVBoxLayout()
        inner_layout.addWidget(WFStackedWidget)
        inner_layout.addStretch()
        main_layout = QHBoxLayout()
        main_layout.addStretch()
        main_layout.addLayout(inner_layout)
        main_layout.addStretch()
        main_Qwidget = QWidget()
        main_Qwidget.setLayout(main_layout)
        main_window.setCentralWidget(main_Qwidget)

        # première page: saisie des nombres de classes
        try:
            # on tente une validation rapide (si insuffisant, l'utilisateur remplira les champs)
            validate_for_generation()
        except ValidationError:
            # pas de panique : on laisse l'utilisateur remplir l'UI ; mais on peut informer
            pass
        saisie_nbresClasses = Saisie_nombres_de_classes("RENSEIGNEZ LES NOMBRES DE CLASSES PAR NIVEAU ET LE NOMBRE DE SALLES DE CLASSE", main_window)
        WFStackedWidget.addWidget(saisie_nbresClasses)
        WFStackedWidget.setCurrentWidget(saisie_nbresClasses)

        main_window.setFixedHeight(300)
        main_window.show()
        return app.exec()


def main():
    controller = AppController()
    return controller.run()

if __name__ == '__main__':
    sys.exit(main())
