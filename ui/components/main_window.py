from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QMainWindow

from .about_dialog import AboutDialog
from .history_dialog import HistoryDialog
from .log_detail_dialog import LogDetailDialog
from .message_box import MessageBox
from .settings_dialog import SettingsDialog
from ..mixins import FormMixin
from ..designer.main_window import Ui_MainWindow
from ..forms import Form, Field
from ..forms.validators import not_empty


class MainWindow(QMainWindow, FormMixin):
    form_class = Ui_MainWindow
    __state = {
        'worker_status': 'idle',
        'tool': '',
        'user_name': '',
        'user_work_count': 0,
        'user_is_staff': False,
        'logs': [],
        'logs_location': None,
        'logs_extensions': None,
        'product_name': '',
        'order_name': '',
        'workstation_name': '',
    }

    network_progress_signal = pyqtSignal(int)

    # Indices das páginas do stacked widget
    __DASHBOARD_INDEX = 1
    __LOGIN_INDEX = 0

    def __init__(self, *args, **kwargs):
        self.on_login = kwargs.pop('on_login')
        self.on_logout = kwargs.pop('on_logout')
        self.on_toggle_worker = kwargs.pop('on_toggle_worker')
        self.on_close = kwargs.pop('on_close')
        self.on_get_settings = kwargs.pop('on_get_settings')
        self.on_save_settings = kwargs.pop('on_save_settings')
        self.on_get_workstations = kwargs.pop('on_get_workstations')
        self.on_reprocess = kwargs.pop('on_reprocess')
        self.on_get_logs = kwargs.pop('on_get_logs')
        self.on_sync_user = kwargs.pop('on_sync_user')
        self.show_product_selection_dialog = kwargs.pop('show_product_selection_dialog')
        self.show_order_selection_dialog = kwargs.pop('show_order_selection_dialog')
        self.__state['tool'] = kwargs.pop('tool')
        self.__state['logs_location'] = kwargs.pop('logs_location')
        self.__state['logs_extensions'] = kwargs.pop('logs_extensions')

        super().__init__(*args, **kwargs)

        self.update_state()
        self.form.line_username.setFocus()
        self.form.network_progressbar.hide()

        self.__login_form = Form(
            fields=(
                Field(name='Utilizador', widget=self.form.line_username, validators=(not_empty,)),
                Field(name='Palavra-passe', widget=self.form.line_password, validators=(not_empty,))
            ),
            on_submit=self.__login_handler,
            submit_button=self.form.btn_login,
            error_label=self.form.label_login_failed
        )

    def set_bindings(self):
        self.form.action_terminate.triggered.connect(self.close)
        self.form.action_settings.triggered.connect(self.__show_settings_handler)
        self.form.action_about.triggered.connect(self.__show_about_handler)
        self.form.action_history.triggered.connect(self.__show_history_handler)
        self.form.btn_logout.clicked.connect(self.on_logout)
        self.form.btn_toggle_job.clicked.connect(self.on_toggle_worker)
        self.form.btn_reprocess.clicked.connect(self.__reprocess_handler)
        self.form.btn_clear_logs.clicked.connect(self.clear_logs)
        self.form.list_logs.itemDoubleClicked.connect(self.__show_details_handler)
        self.network_progress_signal.connect(self.__update_network_progress)
        self.form.btn_change_product.clicked.connect(self.show_product_selection_dialog)
        self.form.btn_change_order.clicked.connect(self.show_order_selection_dialog)

    def lock_window(self):
        self.form.stacked_content.setCurrentIndex(self.__LOGIN_INDEX)
        self.form.frame_user_details.hide()

    def show_login_failed(self, message):
        # todo: esta função devia ser repensada
        self.__login_form.set_error(message)

    def update_state(self, new_state: dict = None):
        """
        Atualiza estado interno e refresca os componentes gráficos com base no
        novo estado. Esta função certifica que a interface gráfica reflete as
        alterações do estado da aplicação, incluindo os detalhes do utilizador,
        detalhes da ferramenta, estado do worker, logs e dados do produto.

        :param new_state: Dicionário que contém novos valores do estado da
            aplicação. Se o dicionário contiver um 'log' este será adicionado
            à lista de logs do estado atual. Se nenhum estado for fornecido,
            o estado permanece inalterado.
        :type new_state: dict, opcional
        :return: None
        """

        if new_state is not None:
            if 'log' in new_state:
                self.__state['logs'].append(new_state.pop('log'))

            self.__state = {**self.__state, **new_state}

        # Atualiza estado da UI dos componentes relativos ao utilizador
        if self.__state['user_name']:
            # Sincroniza trabalhos com o Controlo de Produção
            if self.form.stacked_content.currentIndex() == self.__LOGIN_INDEX:
                self.on_sync_user()

            self.form.stacked_content.setCurrentIndex(self.__DASHBOARD_INDEX)
            self.form.label_user.setText(self.__state['user_name'])
            self.form.frame_user_details.show()
        else:
            self.lock_window()

        self.form.label_processed_amount.setText('Qtd. processada: ' + str(self.__state['user_work_count']))

        if self.__state['workstation_name']:
            self.form.label_workstation.setText(self.__state['workstation_name'])

        # Atualiza estado da UI dos componentes relativos à ferramenta
        if self.__state['tool'] and self.__state['user_name']:
            self.form.label_tool.setText(self.__state['tool'])
            self.form.label_tool.show()
            self.form.btn_toggle_job.setEnabled(True)
            self.form.btn_toggle_job.setToolTip('')
            self.form.btn_reprocess.setEnabled(True)
            self.form.btn_reprocess.setToolTip('')
        else:
            self.form.label_tool.hide()
            self.form.btn_toggle_job.setEnabled(False)
            self.form.btn_toggle_job.setToolTip('Não pode iniciar enquanto não escolher uma ferramenta.')
            self.form.btn_reprocess.setEnabled(False)
            self.form.btn_reprocess.setToolTip('Não pode reprocessar enquanto não escolher uma ferramenta.')

        # Atualiza estado da UI dos componentes relativos ao estado do "Worker"
        if self.__state['worker_status'].lower() == 'running':
            self.form.btn_toggle_job.setText('  Parar')
            self.form.label_status_text.setText('A processar...')
            self.form.label_status_icon.setPixmap(QPixmap(':/images/images/green-circle.png'))
            self.form.btn_toggle_job.setIcon(QIcon(':/images/images/pause-button.png'))
        else:
            self.form.btn_toggle_job.setText('  Iniciar')
            self.form.label_status_text.setText('Parado.')
            self.form.label_status_icon.setPixmap(QPixmap(':/images/images/red-circle.png'))
            self.form.btn_toggle_job.setIcon(QIcon(':/images/images/play-button.png'))

        # Atualiza lista de logs
        if self.__state['logs']:
            self.form.list_logs.clear()
            if len(self.__state['logs']) > 100:
                self.__state['logs'].pop(0)

            for log in reversed(self.__state['logs']):
                item_text = ' - '.join([
                    log['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    log['message'],
                    log['path']
                ])
                item = QListWidgetItem(parent=self.form.list_logs)
                item.setText(item_text)
                item.log = log

                if log['status'] == 'error':
                    item.setBackground(QColor('#f3bcbc'))
                elif log['status'] == 'warning':
                    item.setBackground(QColor('#fcc571'))
                elif log['status'] == 'success':
                    item.setBackground(QColor('#a2f3b2'))

        # Atualiza produto
        if self.__state['product_name']:
            self.form.label_product_name.setText(self.__state['product_name'])
            self.form.label_product_name.show()
            self.form.label_tool.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
            self.form.btn_change_product.show()
        else:
            self.form.label_product_name.hide()
            self.form.label_tool.setAlignment(Qt.AlignCenter)
            self.form.btn_change_product.hide()

        # Atualiza a ordem
        if self.__state['order_name']:
            self.form.label_order_name.setText(self.__state['order_name'])
            self.form.label_order_name.show()
            self.form.label_tool.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
            self.form.btn_change_order.show()
        else:
            self.form.label_order_name.hide()
            self.form.label_tool.setAlignment(Qt.AlignCenter)
            self.form.btn_change_order.hide()

    def closeEvent(self, event):
        self.on_close(event)

    def clear_logs(self):
        """
        Limpa lista de logs do estado atual da aplicação.

        :return: None
        """
        self.__state['logs'] = []
        self.form.list_logs.clear()

    def __login_handler(self):
        """
        Trata a operação de início de sessão quando o utilizador submete os
        dados de login. Esta função recolhe os dados do formulário e invoca
        a respetiva função de callback para processar a autenticação.

        :return: None
        """
        if self.form.network_progressbar.isVisible():
            return

        username = self.form.line_username.text()
        password = self.form.line_password.text()

        self.on_login((username, password))

    def __update_network_progress(self, progress):
        """
        Atualiza barra de progresso para pedidos de rede na interface gráfica.

        Quando progresso chegar a 100% a barra é escondida.

        :param progress: Percentagem do progresso
        :type progress: int
        """
        if progress == 100:
            self.form.network_progressbar.hide()
        else:
            self.form.network_progressbar.show()

        self.form.network_progressbar.setValue(progress)

    def __show_details_handler(self, selected_item):
        """
        Mostra janela de detalhes do log selecionado.

        :param selected_item: Item selecionado pelo utilizador que contém
                              informações do log.
        :type selected_item: QListWidgetItem
        :return: None
        """
        LogDetailDialog(selected_item.log, parent=self).exec_()

    def __show_settings_handler(self):
        """
        Mostra janela de definições da aplicação.

        Esta função verifica se o utilizador tem permissões de staff para
        poder aceder ao menu das definições.

        :return: None
        """
        if not self.__state['user_is_staff']:
            MessageBox(
                'Sem permissão',
                'Não tem permissão para alterar definições do programa',
                parent=self
            ).exec_()
            return

        SettingsDialog(
            self,
            **self.on_get_settings(),
            on_save=self.on_save_settings,
            on_get_workstations=self.on_get_workstations
        ).exec_()

    def __show_about_handler(self):
        """
        Mostra janela de detalhes da aplicação, como nome do programa,
        versão da aplicação e copyright.

        :return: None
        """
        AboutDialog(self).exec_()

    def __reprocess_handler(self):
        """
        Esta função seleciona, através de um file dialog, um ou mais ficherios log
        para reprocessamento.

        :return: None
        """
        selected_files, _ = QFileDialog().getOpenFileNames(
            parent=self,
            caption='Selecionar ficheiro',
            directory=self.__state['logs_location'],
            filter='Log Files ({})'.format(' '.join('*' + ext for ext in self.__state['logs_extensions']))
        )

        self.on_reprocess(selected_files)

    def __show_history_handler(self):
        """
        Mostra janela de histórico de trabalhos. Bloqueia o acesso à janela
        caso o utilizador não esteja autenticado.

        :return: None
        """
        if not self.__state['user_name']:
            MessageBox(
                'Autenticação requerida',
                'Autentique-se para aceder a este conteúdo.',
                parent=self
            ).exec_()
            return

        HistoryDialog(
            parent=self,
            on_get_logs=self.on_get_logs
        ).exec_()
