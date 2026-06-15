from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QDialog, QCompleter

from ..designer.select_product_dialog import Ui_SelectProductDialog
from ..mixins import FormMixin
from ..tasks import AsynchronousTask
from ..forms import Form, Field
from ..forms.validators import not_empty


class SelectProductDialog(QDialog, FormMixin):
    form_class = Ui_SelectProductDialog

    def __init__(self, *args, **kwargs):
        self.on_get_products = kwargs.pop('on_get_products')
        self.on_submit = kwargs.pop('on_submit')
        self.__products = None

        super().__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Completer that matches substrings, case-insensitive
        completer = QCompleter(self.form.combobox_product.model(), self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.form.combobox_product.setCompleter(completer)

        self.form.combobox_product.lineEdit().textChanged.connect(self.__on_text_changed)

        self.form.btn_submit.setEnabled(False)
        self.form.combobox_product.setEnabled(False)
        # save default error style
        self.__label_form_error_default_style = self.form.label_form_error.styleSheet()
        self.form.label_form_error.setStyleSheet('color: orange;')
        self.form.label_form_error.setText('A carregar lista de produtos!')

        self.__product_form = Form(
            fields=(
                Field(name='Produto', widget=self.form.combobox_product, validators=(not_empty,)),
            ),
            error_label=self.form.label_form_error,
            on_submit=self.__submit_handler,
            submit_button=self.form.btn_submit
        )

        QTimer.singleShot(0, self.__start_loading_products)

    def __start_loading_products(self):
        AsynchronousTask(
            target=self.on_get_products,
            on_finish=self.__update_product_choices,
            parent=self
        ).start()

    def __update_product_choices(self, choices: list):
        items = []
        self.__products = choices

        for choice in choices:
            if choice['code']:
                item = choice['code'] + ' | ' + choice['name']
            else:
                item = choice['name']

            items.append(item)

        self.form.combobox_product.clear()
        if items:
            self.form.combobox_product.addItems(items)
            self.form.combobox_product.setCurrentText('')
            # line placeholder
            self.form.combobox_product.lineEdit().setPlaceholderText("Escreva para filtrar...")
            self.form.label_form_error.clear()
            self.form.label_form_error.setStyleSheet(self.__label_form_error_default_style)

            self.form.combobox_product.setEnabled(True)

    def __on_text_changed(self, text: str):
        is_valid = self.form.combobox_product.findText(text, Qt.MatchExactly) != -1
        self.form.btn_submit.setEnabled(is_valid)

    def __submit_handler(self):
        choice = self.form.combobox_product.currentText()
        product_found = None

        for product in self.__products:
            if product['code'] == choice.split(' | ')[0]:
                product_found = product
                break

        self.on_submit(product_found)
        self.close()
