from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from ..designer.select_order_dialog import Ui_SelectOrderDialog
from ..mixins import FormMixin


class SelectOrderDialog(QDialog, FormMixin):
    form_class = Ui_SelectOrderDialog

    def __init__(self, *args, **kwargs):
        self.on_submit = kwargs.pop('on_submit')

        super().__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.form.btn_submit.clicked.connect(self.__submit_handler)

    def __submit_handler(self):
        order = self.form.order_line_edit.text()

        # ordem de fabrico não pode estar vazia
        if not order:
            self.form.label_form_error.setText("Introduza uma ordem de fabrico!")
            return

        # ordem de fabrico deve ter 10 caracteres
        if len(order) != 10:
            self.form.label_form_error.setText("Ordem de fabrico deve ter 10 caracteres!")
            return

        # ordem de fabrico deve ser apenas digitos
        if not order.isdigit() or not order.isascii():
            self.form.label_form_error.setText("Ordem de fabrico deve conter apenas digitos!")
            return

        current_year_prefix = datetime.now().strftime("%y")
        current_month = datetime.now().strftime("%m")
        # os primeiros dois caracteres da ordem de fabrico devem ser refentes ao ano atual. Ex: Em 2025 devem ser 25.
        valid_years = [current_year_prefix]

        # se o mês for janeiro ou fevereiro, é permitido que sejam processadas OFs do ano anterior, desde que a OF seja
        # maior que 50, isto para tentar evitar casos em que o utilizador se engane na introdução da OF.
        if current_month in ['01', '02'] and int(order[2:]) > 50:
            valid_years.insert(0, str(int(current_year_prefix) - 1))

        if order[:2] not in valid_years:
            self.form.label_form_error.setText(
                f"Os primeiros dois caracteres devem ser referentes a um dos\nseguintes anos válidos:"
                f" {', '.join(valid_years)}!"
            )
            return

        # atualiza ordem de fabrico
        self.on_submit(order)
        self.close()
