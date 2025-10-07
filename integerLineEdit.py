from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QFocusEvent

class IntegerLineEdit(QLineEdit):

    def __init__(self, parent=None, width=100, height=30, cas = 1):
        super().__init__(parent)
        self.cas = cas
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignHCenter)
        regex = QRegularExpression("^([0-9]|1[0-9]|2[0-5])$")
        self.setText("0")
        if self.cas == 2:
            regex = QRegularExpression("^([1-9]\d|100)$")
            self.setText("10")
        elif self.cas == 3:
            self.setText("")
            self.setDisabled(True)
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)
        self.editingFinished.connect(self.checkEmpty)
    
    def focusOutEvent(self, event: QFocusEvent) -> None:
        self.checkEmpty()
        super().focusOutEvent(event)
    
    def checkEmpty(self):
        if self.cas == 1 and self.text() == "":
            self.setText("0")
        elif self.cas == 2 and (self.text() == "" or int(self.text()) < 10):
            self.setText("10")
