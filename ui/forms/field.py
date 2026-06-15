from PyQt5.QtWidgets import QComboBox
from .validators import valid_choice


class Field:
    def __init__(self, name, widget, validators=None):
        if validators is None:
            validators = []

        self.widget = widget
        self.validators = validators
        self.name = name

        if isinstance(self.widget, QComboBox):
            self.validators += (valid_choice,)

    def __get_current_value(self):
        if isinstance(self.widget, QComboBox):
            return self.widget.currentText()
        else:
            return self.widget.text()

    def validate(self):
        value = self.__get_current_value()

        for validator in self.validators:
            kwargs = {
                'value': value,
                'field_name': self.name,
            }

            if validator.__name__ == 'valid_choice':
                kwargs.update({
                    'choices': [self.widget.itemText(i) for i in range(self.widget.count())]
                })

            validator(**kwargs)

        return value
