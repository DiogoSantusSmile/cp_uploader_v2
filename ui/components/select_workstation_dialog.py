from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QCompleter

from ..designer.select_workstation_dialog import Ui_SelectWorkstationDialog
from ..mixins import FormMixin
from ..forms import Form, Field
from ..forms.validators import not_empty


class SelectWorkstationDialog(QDialog, FormMixin):
    form_class = Ui_SelectWorkstationDialog

    def __init__(self, *args, **kwargs):
        self.allowed_workstations = kwargs.pop('allowed_workstations')
        self.on_submit = kwargs.pop('on_submit')
        self.__chose_a_workstation = False

        super().__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Completer that matches substrings, case-insensitive
        completer = QCompleter(self.form.combobox_workstation.model(), self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.form.combobox_workstation.setCompleter(completer)

        self.form.combobox_workstation.lineEdit().textChanged.connect(self.__on_text_changed)

        self.form.btn_submit.setEnabled(False)
        self.form.combobox_workstation.setEnabled(False)

        self.__workstation_form = Form(
            fields=(
                Field(name='Posto', widget=self.form.combobox_workstation, validators=(not_empty,)),
            ),
            error_label=self.form.label_form_error,
            on_submit=self.__submit_handler,
            submit_button=self.form.btn_submit
        )

        self.__update_allowed_workstations()

    def __update_allowed_workstations(self):
        items = []

        for workstation in self.allowed_workstations.split(','):
            items.append(workstation.strip())

        self.form.combobox_workstation.clear()
        if items:
            self.form.combobox_workstation.addItems(items)
            self.form.combobox_workstation.setCurrentText('')
            self.form.combobox_workstation.lineEdit().setPlaceholderText("Escreva para filtrar...")

            self.form.combobox_workstation.setEnabled(True)

    def __on_text_changed(self, text: str):
        is_valid = self.form.combobox_workstation.findText(text, Qt.MatchExactly) != -1
        self.form.btn_submit.setEnabled(is_valid)

    def __submit_handler(self):
        self.on_submit(self.form.combobox_workstation.currentText())
        self.__chose_a_workstation = True
        self.close()

    def closeEvent(self, event):
        if not self.__chose_a_workstation:
            event.ignore()
            self.form.label_form_error.setText('Selecione um posto primeiro!')
        else:
            super().closeEvent(event)
