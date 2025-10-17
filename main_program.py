import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QStackedWidget, QVBoxLayout, QHBoxLayout
from main_form_ui import Ui_MainWindow
from saisie_nombres_de_classes import Saisie_nombres_de_classes # Cannot find a Qt installation in "/Users/diabatech/Qt".

class WorkForm(QMainWindow):
    def __init__(self): 
        super().__init__()
        self.ui = Ui_MainWindow() 
        self.ui.setupUi(self)
        self.WFStackedWidget = QStackedWidget()
        self.inner_layout = QVBoxLayout()
        self.inner_layout.addWidget(self.WFStackedWidget)
        self.inner_layout.addStretch() 
        self.main_layout = QHBoxLayout()
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.inner_layout)
        self.main_layout.addStretch()
        self.main_Qwidget = QWidget()
        self.main_Qwidget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_Qwidget)
        
        
        
if __name__ == '__main__':
    try:
        # Preferer le contrôleur MVC si présent
        from app.controller import main as mvc_main
        sys.exit(mvc_main())
    except Exception:
        # fallback : comportement historique
        app = QApplication(sys.argv)
        workForm = WorkForm()
        saisie_nbresClasses = Saisie_nombres_de_classes("RENSEIGNEZ LES NOMBRES DE CLASSES PAR NIVEAU ET LE NOMBRE DE SALLES DE CLASSE", workForm)
        workForm.WFStackedWidget.addWidget(saisie_nbresClasses)
        workForm.WFStackedWidget.setCurrentWidget(saisie_nbresClasses)
        workForm.setFixedHeight(300)
        workForm.show()
        sys.exit(app.exec())