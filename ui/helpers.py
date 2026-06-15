from PyQt5.QtWidgets import QMessageBox

from version import title


def show_critical_error_message_box(text):
    """
    Displays a critical error message box with a warning icon.

    This function creates a message box using the QMessageBox class to display a
    critical error message to the user. The message box incorporates a warning icon
    and only includes an "Ok" button for user acknowledgment.

    :param text: The error message text to be displayed in the message box.
    :type text: str
    """
    msg_box = QMessageBox(icon=QMessageBox.Warning, text=text)
    msg_box.setWindowTitle(title)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
