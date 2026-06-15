from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from ..designer.about_dialog import Ui_AboutDialog
from ..mixins import FormMixin
from version import version, title, copyright, release_date


class AboutDialog(QDialog, FormMixin):
    form_class = Ui_AboutDialog

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.form.label_app_title.setText(title)
        self.form.label_app_version.setText(f'Versão {version}')
        self.form.label_released_at.setText('Data de lançamento: {}'.format(release_date))
        self.form.label_copyright.setText(copyright)
