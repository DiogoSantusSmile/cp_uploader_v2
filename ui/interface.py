from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

import sys

from .components import (
    ConfirmMessageBox,
    ErrorMessageBox,
    MainWindow,
    SelectProductDialog,
    SelectOrderDialog,
    SelectWorkstationDialog
)
from .tasks import AsynchronousTask


class Interface(QApplication):
    user_login_signal = pyqtSignal(object)
    user_logout_signal = pyqtSignal()
    user_login_failed_signal = pyqtSignal(str)
    error_message_signal = pyqtSignal(str, str)
    update_ui_data_signal = pyqtSignal(dict)
    needs_product_signal = pyqtSignal()
    needs_order_signal = pyqtSignal()

    def __init__(self, **kwargs):
        self.on_close = kwargs.pop('on_close')
        self.on_login = kwargs.pop('on_login')
        self.on_sync_user = kwargs.pop('on_sync_user')
        self.on_get_products = kwargs.pop('on_get_products')
        self.on_select_workstation = kwargs.pop('on_select_workstation')
        self.allowed_workstations = kwargs.pop('allowed_workstations')
        self.on_select_product = kwargs.pop('on_select_product')
        self.on_select_order = kwargs.pop('on_select_order')

        super().__init__(sys.argv)

        # Instancia janela principal
        self.__main_window = MainWindow(
            on_login=self.__login_submit_handler,
            on_logout=kwargs.pop('on_logout'),
            on_toggle_worker=kwargs.pop('on_toggle_worker'),
            on_close=self.__close_event_handler,
            on_get_settings=kwargs.pop('on_get_settings'),
            on_save_settings=kwargs.pop('on_save_settings'),
            on_get_workstations=kwargs.pop('on_get_workstations'),
            on_reprocess=kwargs.pop('on_reprocess'),
            on_get_logs=kwargs.pop('on_get_logs'),
            on_sync_user=self.__sync_user_handler,
            logs_location=kwargs.pop('logs_location'),
            logs_extensions=kwargs.pop('logs_extensions'),
            tool=kwargs.pop('tool'),
            show_product_selection_dialog=self.__show_product_selection_dialog,
            show_order_selection_dialog=self.__show_order_selection_dialog,
        )

        # Connect signals
        self.user_login_signal.connect(self.__login_handler)
        self.user_logout_signal.connect(self.__logout_handler)
        self.user_login_failed_signal.connect(self.__main_window.show_login_failed)
        self.error_message_signal.connect(self.show_error_message)
        self.update_ui_data_signal.connect(lambda data: self.__main_window.update_state(data))
        self.needs_product_signal.connect(self.__show_product_selection_dialog)
        self.needs_order_signal.connect(self.__show_order_selection_dialog)

    def show(self):
        """
        Mostra a janela principal e inicia o loop de eventos.

        Esta função é responsável por renderizar a aplicação.
        """
        self.__main_window.show()
        sys.exit(self.exec_())

    def show_error_message(self, title, message):
        """
        Mostra um dialog de erro.

        :param title: Título do dialog.
        :type title: str
        :param message: Texto descritivo do erro.
        :type message: str
        :return: None
        """
        ErrorMessageBox(title, message, parent=self.__main_window).exec_()

    def update_worker_status(self, status: str = 'idle'):
        """
        Atualiza estado do 'Worker' na interface gráfica.

        Possivéis valores: 'idle', 'running'

        :param status: Novo estado do 'Worker', por feito = 'idle'
        :type status: str
        :return: None
        """
        self.__main_window.update_state({'worker_status': status})

    def __login_submit_handler(self, credentials):
        """
        Trata da submissão das credenciais de início de sessão, lançando
        uma tarefa em segundo plano para iniciar processo autenticação
        com o servidor.
        """

        AsynchronousTask(
            target=self.on_login,
            target_kwargs={'credentials': credentials},
            on_progress=self.__main_window.network_progress_signal.emit,
            parent=self
        ).start()

    def __login_handler(self, user):
        """
        Processa o início de sessão do utilizador atualizando os dados
        do mesmo e atualizando a UI.

        :param user: Objeto do utilizador que contém os seus dados.
        :type user: User
        :return: None
        """
        if self.allowed_workstations:
            # calls select workstation dialog
            self.__show_workstation_selection_dialog()

        self.__main_window.update_state({
            'user_name': user.name,
            'user_is_staff': user.is_staff,
        })

    def __logout_handler(self):
        """
        Processa o fim de sessão do utilizador removendo os seus dados
        e atualizando a UI.

        :return: None
        """
        self.__main_window.update_state({
            'user_name': None,
            'user_work_count': 0,
            'user_is_staff': False
        })
        self.__main_window.clear_logs()

    def __close_event_handler(self, event):
        """
        Manipula evento de fecho do programa para questionar o utilizador
        se pretende, efetivamente, encerrar o programa.

        :param event: Evento de fecho.
        :type event: QCloseEvent
        :return: None
        """
        msg_box = ConfirmMessageBox(
            'Encerrar programa',
            'Tem a certeza que pretende encerrar o programa?',
            parent=self.__main_window
        )

        if msg_box.confirm():
            self.on_close()
            event.accept()
        else:
            event.ignore()

    def __sync_user_handler(self):
        """
        Trata da sincronização de trabalhos do utilizador atual com o servidor.
        Lança QThread que envia chama função de sincronização de trabalhos
        registados no servidor.

        :return: None
        """
        AsynchronousTask(
            target=self.on_sync_user,
            parent=self
        ).start()

    def __show_product_selection_dialog(self):
        SelectProductDialog(
            parent=self.__main_window,
            on_get_products=self.on_get_products,
            on_submit=self.on_select_product
        ).exec_()

    def __show_order_selection_dialog(self):
        SelectOrderDialog(
            parent=self.__main_window,
            on_submit=self.on_select_order
        ).exec_()

    def __show_workstation_selection_dialog(self):
        SelectWorkstationDialog(
            parent=self.__main_window,
            allowed_workstations=self.allowed_workstations,
            on_submit=self.on_select_workstation
        ).exec_()
