from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox


class MessageBox(QMessageBox):
    def __init__(self, title, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(title)
        self.setText(message)
        self.setWindowIcon(QIcon(':/images/images/logo-uartronica-final-mini.png'))
        self.setIcon(QMessageBox.Information)


class ErrorMessageBox(MessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIcon(QMessageBox.Critical)


class ConfirmMessageBox(MessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    def confirm(self):
        result = self.exec_()
        return result == QMessageBox.Yes
