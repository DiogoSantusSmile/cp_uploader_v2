from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem

from ..designer.history_dialog import Ui_HistoryDialog
from ..mixins import FormMixin


class HistoryDialog(QDialog, FormMixin):
    form_class = Ui_HistoryDialog

    def __init__(self, *args, **kwargs):
        self.on_get_logs = kwargs.pop('on_get_logs')
        self.__page_offset = 0
        self.__page_size = 20

        super().__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.update_logs_list()

    def set_bindings(self):
        self.form.btn_next_page.clicked.connect(self.next_page_handler)
        self.form.btn_previous_page.clicked.connect(self.previous_page_handler)

    def update_logs_list(self):
        log_list = self.on_get_logs(limit=self.__page_size, offset=self.__page_offset)
        self.form.tree_widget_logs.clear()

        for log in log_list:
            upload_status = ''

            if log['uploads']:
                if log['uploads'][-1]['status'] == 'success':
                    upload_status = 'OK'
                else:
                    upload_status = 'NOK'

            self.form.tree_widget_logs.addTopLevelItem(QTreeWidgetItem([
                log['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                log['filename'],
                log['absolute_path'],
                'OK' if log['is_valid'] else 'NOK',
                upload_status
            ]))

        if self.__page_offset < self.__page_size:
            self.form.btn_previous_page.setEnabled(False)
        else:
            self.form.btn_previous_page.setEnabled(True)

        if len(log_list) < self.__page_size:
            self.form.btn_next_page.setEnabled(False)
        else:
            self.form.btn_next_page.setEnabled(True)

    def next_page_handler(self):
        self.__page_offset += self.__page_size
        self.update_logs_list()

    def previous_page_handler(self):
        self.__page_offset -= self.__page_size

        if self.__page_offset <= 0:
            self.__page_offset = 0

        self.update_logs_list()
