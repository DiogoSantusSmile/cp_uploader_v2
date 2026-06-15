class FormMixin(object):
    form_class = None

    def __init__(self):
        if self.form_class is None:
            raise Exception("Form not defined.")

        # Instancia formulário
        self.form = self.form_class()
        self.form.setupUi(self)

        self.set_bindings()

    def set_bindings(self):
        """Define eventos dos componentes."""
        pass
