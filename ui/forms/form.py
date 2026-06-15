class Form:
    def __init__(self, fields, on_submit, error_label=None, submit_button=None, clear_on_submit=True):
        self.fields = fields
        self.on_submit = on_submit
        self.clear_on_submit = clear_on_submit
        self.error_label = error_label

        try:
            self.fields[-1].widget.returnPressed.connect(self.__submit)
        except AttributeError:
            pass

        if submit_button is not None:
            submit_button.clicked.connect(self.__submit)


    def __submit(self):
        # valida campos do formulário
        if not self.validate():
            return

        # submete formulário
        self.on_submit()

        if self.clear_on_submit:
            self.clear()

    def clear(self):
        for field in self.fields:
            field.widget.clear()

        self.fields[0].widget.setFocus()

        if self.error_label is not None:
            self.error_label.setText('')

    def validate(self):
        for field in self.fields:
            try:
                field.validate()
            except ValueError as e:
                self.set_error(str(e))
                return False
        return True

    def set_error(self, text):
        if self.error_label is not None:
            self.error_label.setText(text)
