from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

import os
import platform
import subprocess

from ..designer.log_detail_dialog import Ui_LogDetailDialog
from ..mixins import FormMixin


class LogDetailDialog(QDialog, FormMixin):
    form_class = Ui_LogDetailDialog

    def __init__(self, log, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.form.label_timestamp.setText(log['timestamp'].strftime('%Y-%m-%d %H:%M:%S'))
        self.form.label_logfile.setText(log['path'])

        if log['status'] == 'error':
            self.form.label_status_message.setStyleSheet(
                'background-color: red; color: white; font: 75 20pt "MS Shell Dlg 2";'
            )
            self.form.label_status_message.setText('Erro! - {}'.format(log['message']))
            self.form.label_status.setText('Erro')
            self.form.text_edit_log.setText(log['data'])
        elif log['status'] == 'warning':
            self.form.label_status_message.setStyleSheet(
                'background-color: red; color: white; font: 75 20pt "MS Shell Dlg 2";'
            )
            self.form.label_status_message.setText('Unidade(s) NOK')
            self.form.label_status.setText('OK')
            self.form.label_edit_log.hide()
            self.form.text_edit_log.hide()
        else:
            self.form.label_status_message.setStyleSheet(
                'background-color: green; color: white; font: 75 20pt "MS Shell Dlg 2";'
            )
            self.form.label_status_message.setText('OK')
            self.form.label_status.setText('OK')
            self.form.label_edit_log.hide()
            self.form.text_edit_log.hide()

    def set_bindings(self):
        self.form.btn_log_path.clicked.connect(self.__open_log_path_handler)

    def __open_log_path_handler(self):
        path=self.form.label_logfile.text()

        system = platform.system()

        if system == 'Windows':
            subprocess.Popen(r'explorer /select,"{}"'.format(path))
        elif system == 'Linux':
            subprocess.Popen(['pcmanfm', os.path.dirname(path)])
