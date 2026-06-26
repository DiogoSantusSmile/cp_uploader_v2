from PyQt5.QtCore import pyqtSignal, QDateTime, Qt
from PyQt5.QtWidgets import QDialog, QFileDialog

import os

from ..designer.settings_dialog import Ui_SettingsDialog
from ..mixins import FormMixin
from ..tasks import AsynchronousTask
from ..forms import Form, Field
from ..forms.validators import not_empty


class SettingsDialog(QDialog, FormMixin):
    form_class = Ui_SettingsDialog

    workstation_list_collected_signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        self.task = None
        self.on_save = kwargs.pop('on_save')
        self.on_get_workstations = kwargs.pop('on_get_workstations')
        self.active_workstation = kwargs.pop('active_workstation')
        cp_url = kwargs.pop('cp_url')
        available_tools = kwargs.pop('available_tools')
        active_tool = kwargs.pop('active_tool')
        logs_location = kwargs.pop('logs_location')
        logs_date_start = kwargs.pop('logs_date_start')
        enable_logs_backup = kwargs.pop('enable_logs_backup')
        logs_backup_location = kwargs.pop('logs_backup_location')
        logs_backup_action = kwargs.pop('logs_backup_action')

        super().__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.form.line_cp_url.setText(cp_url)
        self.form.combo_cp_workstation.addItems([self.active_workstation])
        self.form.combo_cp_workstation.setCurrentText(self.active_workstation)
        self.form.combo_logs_tool.addItems(available_tools)
        self.form.combo_logs_tool.setCurrentText(active_tool)
        self.form.line_logs_location.setText(logs_location)
        self.form.line_logs_date_start.setDateTime(
            QDateTime(
                logs_date_start.year,
                logs_date_start.month,
                logs_date_start.day,
                logs_date_start.hour,
                logs_date_start.minute,
                logs_date_start.second,
            )
        )
        if enable_logs_backup:
            self.form.checkbox_activate_backup.setChecked(True)
            self.form.line_backup_location.setText(logs_backup_location)
            self.form.combo_backup_action.setCurrentText(logs_backup_action)

        self.__settings_form = Form(
            fields=(
                Field(name='Endereço URL', widget=self.form.line_cp_url, validators=(not_empty,)),
                Field(name='Posto', widget=self.form.combo_cp_workstation, validators=(not_empty,)),
                Field(name='Diretório', widget=self.form.line_logs_location, validators=(not_empty,)),
                Field(name='Ferramenta', widget=self.form.combo_logs_tool, validators=(not_empty,)),
                Field(name='Apartir de:', widget=self.form.line_logs_date_start),
                # Field(name='Ativar backup automático', widget=self.form.checkbox_activate_backup),
                Field(name='Diretório', widget=self.form.line_backup_location),
                Field(name='Ação', widget=self.form.combo_backup_action)
            ),
            on_submit=self.__save_handler,
            submit_button=self.form.btn_save,
            error_label=self.form.label_form_error
        )

        self.__get_workstation_list()

    def set_bindings(self):
        self.form.btn_dir_explorer.clicked.connect(
            lambda _: self.__open_dir_explorer_handler(self.form.line_logs_location)
        )
        self.form.btn_dir_explorer_backup.clicked.connect(
            lambda _: self.__open_dir_explorer_handler(self.form.line_backup_location),
        )
        self.form.btn_update_workstations.clicked.connect(self.__get_workstation_list)
        self.workstation_list_collected_signal.connect(self.__update_workstation_list_options)

    def closeEvent(self, event):
        if isinstance(self.task, AsynchronousTask) and self.task.isRunning():
            self.task.terminate()

        event.accept()

    def __open_dir_explorer_handler(self, widget):
        dialog = QFileDialog()

        new_path = os.path.normpath(dialog.getExistingDirectory(
            self,
            'Selecionar localização dos logs',
            widget.text()
        ))

        if new_path != '.':
            widget.setText(new_path)

    def __save_handler(self):
        new_settings = {
            'cp_url': self.form.line_cp_url.text(),
            'active_tool': self.form.combo_logs_tool.currentText(),
            'active_workstation': self.form.combo_cp_workstation.currentText(),
            'logs_location': self.form.line_logs_location.text(),
            'logs_date_start': self.form.line_logs_date_start.dateTime().toPyDateTime(),
            'enable_logs_backup': self.form.checkbox_activate_backup.isChecked(),
            'logs_backup_location': self.form.line_backup_location.text(),
            'logs_backup_action': self.form.combo_backup_action.currentText()
        }

        self.on_save(new_settings)
        self.close()

    def __update_workstation_list_options(self, workstation_list: list):
        if workstation_list:
            self.form.combo_cp_workstation.clear()
            self.form.combo_cp_workstation.addItems(workstation_list)
            if self.active_workstation in workstation_list:
                self.form.combo_cp_workstation.setCurrentText(self.active_workstation)

        self.form.combo_cp_workstation.setEnabled(bool(workstation_list))
        self.form.btn_update_workstations.setEnabled(True)

    def __get_workstation_list(self):
        self.task = AsynchronousTask(
            target=self.on_get_workstations,
            on_finish=self.workstation_list_collected_signal.emit,
            parent=self
        )

        self.form.btn_update_workstations.setEnabled(False)
        self.task.start()
