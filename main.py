from configparser import ConfigParser
from datetime import datetime, timedelta
from PyQt5.QtCore import QLockFile

import os
import shutil
import sys

os.environ['DATABASE_URL'] = 'sqlite:///./app.db'

from backup import LogBackupThread
from db import LogfileService
from db.enums import UploadStatus
from helpers import format_evaluation_data, move_logfile, format_evaluation_data_create_evaluation_v1_url
from logger_config import setup_logger
from network import Network
from network.constants import (
    AOI_SMD_URL,
    CREATE_EVALUATION_V2_URL,
    EVALUATIONS_URL,
    GET_WORKSTATIONS_LIST_URL,
    PRODUCTS_LIST_URL,
    UARTRACKER_CREATE_EVALUATION,
    GET_UNIT_URL,
    CREATE_EVALUATION_V1_URL,
    MIL07_URL
)
from settings import Settings
from ui import Interface
from ui.helpers import show_critical_error_message_box
from user import User
from worker import Worker, Parser, TOOLS

logger = setup_logger('root')
lock = QLockFile('app.lock')


class Controller:
    def __init__(self):
        self.__user = None
        self.__worker = None
        self.__product = None
        self.__order = None
        self.__backup_thread = None
        self.__settings = Settings()
        logs_extensions = []

        if self.__settings.tool in TOOLS.keys():
            logs_extensions = TOOLS[self.__settings.tool]['file_extensions']

        self.__interface = Interface(
            on_login=self.__login_handler,
            on_logout=self.__logout_handler,
            on_toggle_worker=self.__toggle_worker,
            on_close=self.__close_handler,
            on_get_settings=self.__get_settings_handler,
            on_save_settings=self.__save_settings_handler,
            on_get_workstations=self.__get_workstations_handler,
            on_reprocess=self.__reprocess_files_handler,
            on_get_logs=self.__get_logs_handler,
            on_sync_user=self.__sync_user_handler,
            on_get_products=self.__get_products_handler,
            on_select_product=self.__set_product,
            on_select_workstation=self.__set_workstation,
            on_select_order=self.__set_order,
            logs_location=self.__settings.logs_location,
            logs_extensions=logs_extensions,
            tool=self.__settings.tool,
            allowed_workstations=self.__settings.allowed_workstations,
        )
        self.__network = Network(url=self.__settings.url)

        if self.__settings.backup_enable:
            self.__backup_thread = LogBackupThread(
                origin=os.path.join(
                    self.__settings.logs_location,
                    'processed'
                ),
                destination=self.__settings.backup_location,
                action=self.__settings.backup_action,
                on_start=self.__backup_job_start_handler,
                on_stop=self.__backup_job_stop_handler,
                on_error=self.__backup_job_error_handler,
                on_movement=self.__backup_job_movement_handler
            )

    def run(self):
        if not lock.tryLock():
            logger.error('Another instance of the app is already running.')
            show_critical_error_message_box('Já existe uma instância do programa em execução.')
            return

        # Inicia backup job se estiver habilitado
        if self.__backup_thread is not None:
            self.__backup_thread.start()

        self.__interface.show()

    def __login_handler(self, credentials: tuple[str, str], **kwargs):
        response = self.__network.check_credentials(credentials, **kwargs)

        if response['status'] == 'success':
            # Atualiza instância do utilizador
            self.__user = User.from_dict({**response['data'], 'password': credentials[1]})

            # Atualiza UI com os dados do utilizador
            self.__interface.user_login_signal.emit(self.__user)

            logger.info('User \'{username}\' logged in.'.format(
                username=credentials[0],
            ))

            return

        if 'status_code' in response.keys():
            logger.info('User \'{username}\' login failed.'.format(
                username=credentials[0],
            ))

            if response['status_code'] == 401:
                msg = 'Nome de utilizador e/ou palavra-passe errados.'
                self.__interface.user_login_failed_signal.emit(msg)
                return

            if response['status_code'] == 500:
                return

        self.__interface.error_message_signal.emit(
            'Erro de rede',
            'Ocorreu um erro!\nPor favor, verifique a sua ligação á rede.'
        )
        return

    def __logout_handler(self):
        if self.__worker is not None:
            self.__worker.stop_signal.emit()

        self.__interface.user_logout_signal.emit()

    def __toggle_worker(self):
        if self.__worker is None:
            self.__worker = Worker(
                location=self.__settings.logs_location,
                parser=Parser(tool=self.__settings.tool),
                on_start=lambda: self.__interface.update_worker_status('running'),
                on_finish=lambda: self.__interface.update_worker_status('idle'),
                on_parse=self.__logfile_parse_handler,
                on_error=self.__worker_error_handler,
                ignored_directories=self.__settings.ignored_directories
            )

        if not self.__worker.isRunning():
            # Verifica se o produto está selecionado quando o posto é AOI ALeader
            if self.__settings.tool in ['AOI ALeader'] and self.__product is None:
                self.__interface.needs_product_signal.emit()
                return

            if self.__settings.tool in ['MIL07']:
                # Verifica se o produto está selecionado quando o posto é MIL07
                if self.__product is None:
                    self.__interface.needs_product_signal.emit()
                    return
                # Verifica se a ordem está selecionada quando o posto é MIL07
                if self.__order is None:
                    self.__interface.needs_order_signal.emit()
                    return

            self.__worker.start()
        else:
            self.__worker.stop_signal.emit()

    def __close_handler(self):
        logger.info('App process terminated by user.')

        # Encerra Backup Thread
        try:
            if self.__backup_thread is not None and self.__backup_thread.isRunning():
                self.__backup_thread.stop()
                # Dá 10 segundos ao backup thread para terminar, caso contrário força encerramento
                finished = self.__backup_thread.wait(10000)
                if not finished:
                    logger.warning('Backup thread did not finish within timeout... proceeding to shutdown.')
        except Exception:
            logger.exception('Error while stopping backup thread')

        lock.unlock()

    def __logfile_parse_handler(self, result):
        move_file = True
        response = None
        error_msg = ''

        if result['status'] == 'error':
            data = {
                'log': {
                    'timestamp': datetime.now(),
                    'path': result['path'],
                    'status': 'error',
                    'message': 'Erro ao processar ficheiro',
                    'data': result['message'],
                }
            }
            upload_details = None
        else:
            if self.__settings.tool == 'AOI ALeader':
                url = AOI_SMD_URL
                result['data'].update({'product_id': self.__product['id']})
            elif self.__settings.tool in ['EOL ZIV', 'FCL0022', 'LVS']:
                url = UARTRACKER_CREATE_EVALUATION
            elif self.__settings.tool in ['BTF1177', 'BTF14']:
                url = CREATE_EVALUATION_V1_URL
            elif self.__settings.tool == 'MIL07':
                url = MIL07_URL
                result['data'].update({'product_id': self.__product['id'], 'order': self.__order})
            else:
                url = CREATE_EVALUATION_V2_URL

            # checks if serial_no finds exactly one serial_no_2 in the database
            if self.__settings.tool in ['ZURC']:
                for serial_number, details in list(result['data']['serial_numbers'].items()):
                    get_data_response = self.__network.get_data(
                        GET_UNIT_URL + f'?serial_no_2__icontains=NS{serial_number} L{details["lot_number"]}')
                    if len(get_data_response['data']['results']) == 0:
                        error_msg = f'Não foi possível encontar uma unidade com o excerto \'{serial_number}\' e lote \'{details["lot_number"]}\'.'
                        break
                    elif len(get_data_response['data']['results']) > 1:
                        error_msg = f'Foi encontrado mais que uma unidade com o excerto \'{serial_number}\' e lote \'{details["lot_number"]}\'.'
                        break
                    else:
                        old_data = result['data']['serial_numbers'].pop(serial_number)
                        new_serial = get_data_response['data']['results'][0]['serial_no']
                        result['data']['serial_numbers'][new_serial] = old_data

            # manage tplaca / fwversion in btf14 logs
            if self.__settings.tool in ['BTF14']:
                for serial_number, details in list(result['data']['serial_numbers'].items()):
                    get_data_response = self.__network.get_data(GET_UNIT_URL + f'?serial_no={serial_number}')
                    if len(get_data_response['data']['results']) == 0:
                        error_msg = f'A unidade: \'{serial_number}\' não existe!'
                        break
                    elif len(get_data_response['data']['results']) > 1:
                        error_msg = f'Foi encontrada mais que uma unidade!'
                        break
                    else:
                        # only UAR260441 registers tplaca and fwversion
                        if get_data_response['data']['results'][0]['product_code'] == 'UAR260441':
                            if not details['tplaca'] or not details['fwversion']:
                                error_msg = 'TPLACA e/ou FWversion vazios!'
                        else:
                            # show error if they exist
                            if details['tplaca'] or details['fwversion']:
                                error_msg = 'Para este produto não é suposto o registo de TPLACA/FWversion!'
                            # if all correct pop them
                            else:
                                result['data']['serial_numbers'][serial_number].pop('tplaca', None)
                                result['data']['serial_numbers'][serial_number].pop('fwversion', None)

            if self.__settings.tool in ['EOL ZIV', 'FCL0022', 'LVS']:
                line_dict = {}
                if self.__settings.line:
                    line_dict['line'] = self.__settings.line

                formatted_data = format_evaluation_data({
                    **result['data'],
                    'user': self.__user.username,
                    'workstation': self.__settings.workstation,
                    **line_dict
                })
            elif self.__settings.tool == 'BTF1177':
                formatted_data = format_evaluation_data_create_evaluation_v1_url({
                    **result['data'],
                    'line': '1',
                    'workstation': self.__settings.workstation,
                    'attributes': {}
                })
            elif self.__settings.tool == 'BTF14':
                first_serial = next(iter(result['data']['serial_numbers']))

                tplaca = result['data']['serial_numbers'][first_serial].pop('tplaca', None)
                fwversion = result['data']['serial_numbers'][first_serial].pop('fwversion', None)

                if tplaca:
                    attributes = {'TPLACA': tplaca, 'FWVersion': fwversion}
                else:
                    attributes = {}

                result['data']['serial_numbers'][first_serial]['serial_no_2'] = ''
                formatted_data = format_evaluation_data_create_evaluation_v1_url({
                    **result['data'],
                    'line': '1',
                    'workstation': self.__settings.workstation,
                    'attributes': attributes
                })
            else:
                formatted_data = format_evaluation_data({
                    **result['data'],
                    'line': '1',
                    'workstation': self.__settings.workstation
                })

            if not error_msg:
                response = self.__network.post_data(url, formatted_data)

                if 'data' in response.keys() and 'message' in response['data']:
                    response['status'] = 'error'

                if response['status'] == 'success':
                    status = 'success'

                    # Se algum número de série estiver NG muda estado para 'warning'
                    for _, sn_data in result['data']['serial_numbers'].items():
                        if sn_data['status'] in ['NG', 'NOK']:
                            status = 'warning'
                            break

                    msg = 'Trabalho registado com sucesso'
                    msg_data = ''
                else:
                    status = 'error'
                    msg = 'Ocorreu um erro ao enviar dados'

                    if 'status_code' in response.keys() and response['status_code'] == 500:
                        msg_data = 'Ocorreu um erro interno no servidor.'
                        self.__toggle_worker()
                        self.__interface.error_message_signal.emit(
                            'Erro de rede',
                            'Ocorreu um erro interno no servidor!\nPor favor, tente mais tarde.'
                        )
                    elif 'status_code' in response.keys():
                        # todo: verificar se mostro a message corretamente (em alguns casos surge detail)
                        msg_data = str(response['data'])
                        status = 'error'
                    else:
                        msg_data = 'Não foi possível comunicar com o servidor.'
                        self.__toggle_worker()
                        self.__interface.error_message_signal.emit(
                            'Erro de rede',
                            'Ocorreu um erro!\nPor favor, verifique a sua ligação á rede.'
                        )

                    if 'status_code' not in response.keys() or response['status_code'] == 500:
                        move_file = False
            else:
                status = 'error'
                msg = 'Ocorreu um erro ao enviar dados'
                msg_data = error_msg

            data = {
                'log': {
                    'timestamp': datetime.now(),
                    'path': result['path'],
                    'status': status,
                    'message': msg,
                    'data': msg_data,
                }
            }
            upload_details = {
                'status': UploadStatus.FAILED if status == 'error' else UploadStatus.SUCCESS,
                'error_message': msg_data,
                'operator': self.__user.name,
            }

        # não move o ficheiro em casos de ocorrer erro interno no servidor
        # ou erro de rede de modo a que volte a tentar processar mais tarde
        if move_file:
            new_log_path = move_logfile(result['path'], self.__settings.logs_location, data['log']['status'])

            data['log']['path'] = new_log_path

            LogfileService().create(
                absolute_path=new_log_path,
                filename=os.path.basename(new_log_path),
                is_valid=True if result['status'] == 'success' else False,
                upload=upload_details
            )

        # verificar se está ok no processamento e no upload
        if response is not None and result['status'] == 'success' and response['status'] == 'success':
            if self.__settings.tool in ['BTF1177', 'BTF14']:
                evaluated_at = datetime.fromisoformat(response['data']['evaluated_at'])
            else:
                evaluated_at = datetime.fromisoformat(response['data'][0]['evaluated_at'])

            self.__user.add_work({
                'path': result['path'],
                'status': 'OK',
                'evaluated_at': evaluated_at,
            })
            self.__interface.update_ui_data_signal.emit({
                'user_work_count': len(self.__user.work_list),
            })

        if not result['ignore']:
            self.__interface.update_ui_data_signal.emit(data)

    def __get_settings_handler(self):
        settings = self.__settings.to_dict()

        return {
            'cp_url': settings['NETWORK']['URL'],
            'active_tool': settings['CORE']['TOOL'],
            'active_workstation': settings['CORE']['WORKSTATION'],
            'logs_location': settings['LOGS']['LOGS_LOCATION'],
            'logs_date_start': settings['LOGS']['DATE_START_LOGS'],
            'available_tools': list(TOOLS.keys()),
            'enable_logs_backup': settings['LOGS_BACKUP']['ENABLE'],
            'logs_backup_location': settings['LOGS_BACKUP']['BACKUP_LOCATION'],
            'logs_backup_action': settings['LOGS_BACKUP']['ACTION'],
        }

    def __save_settings_handler(self, settings):
        """
        como não é possivel atualizar o "line" e o "carrier" pelo menu de definições, para garantir que as alterações
        feitas à mão ao ficheiro "app.ini" se mantêm para estes dois parametros, lê-se o ficheiro e atribui-se as
        respetivas informações.

        Sem isto os valores de "line" e "carrier" mantêm-se sempre os do ficheiro "app.ini" ao momento de início do
        programa.
        """
        config = ConfigParser()
        config.read('app.ini', encoding='utf-8')

        self.__settings.update({
            'NETWORK': {'URL': settings['cp_url']},
            'CORE': {
                'TOOL': settings['active_tool'],
                'WORKSTATION': settings['active_workstation'],
                'ALLOWED_WORKSTATIONS': self.__settings.allowed_workstations
                # TODO: isto deveria passar para a janela dos settings
            },
            'LOGS': {
                'LOGS_LOCATION': settings['logs_location'],
                'DATE_START_LOGS': settings['logs_date_start']
            },
            'LOGS_BACKUP': {
                'ENABLE': settings['enable_logs_backup'],
                'BACKUP_LOCATION': settings['logs_backup_location'],
                'ACTION': settings['logs_backup_action'],
            },
            'UARTRACKER': {
                'LINE': config.get('UARTRACKER', 'LINE')
            }
        })

        # TODO: Este restart é abrupto, futuramente deve esperar que threads terminem antes de
        #   encerrar a app bem como encerrar a app de forma mais elegante.
        # Reinicia app para recarregar configurações.
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    def __get_workstations_handler(self):
        url = GET_WORKSTATIONS_LIST_URL + '?is_active=true&allow_api=true'
        workstation_list = []

        response = self.__network.get_data(url)

        if response['status'] == 'success':
            for item in response['data']['results']:
                workstation_list.append(item['name'])

            return workstation_list

        self.__interface.error_message_signal.emit(
            'Erro de rede',
            'Ocorreu um erro!\nNão foi possível obter a lista de postos.'
        )
        return workstation_list

    def __reprocess_files_handler(self, files):
        for path in files:
            shutil.move(path, self.__settings.logs_location)

    def __get_logs_handler(self, **kwargs):
        return LogfileService().get_all(
            limit=kwargs['limit'],
            offset=kwargs['offset']
        )

    def __sync_user_handler(self):
        start_time = datetime.now() - timedelta(hours=9)

        response = self.__network.get_data(
            EVALUATIONS_URL,
            query={
                'evaluated_at_after': start_time,
                'evaluated_by': self.__user.pk,
                'workstation_name': self.__settings.workstation
            }
        )

        if response['status'] == 'success':
            for result in response['data']['results']:
                self.__user.add_work({
                    'serial_number': result['unit'],
                    'status': result['status'],
                    'evaluated_at': datetime.fromisoformat(result['evaluated_at'].replace('Z', '+00:00')),
                })

            self.__interface.update_ui_data_signal.emit({
                'user_work_count': len(self.__user.work_list),
            })
            return

    def __get_products_handler(self):
        response = self.__network.get_data(PRODUCTS_LIST_URL)

        if response['status'] == 'success':
            return response['data']['results']

        self.__interface.error_message_signal.emit(
            'Erro de rede',
            'Ocorreu um erro!\nNão foi possível obter a lista de produtos.'
        )
        return []

    def __set_product(self, product):
        self.__product = product

        self.__interface.update_ui_data_signal.emit({
            'product_name': self.__product['name'],
        })

        if self.__worker is not None and not self.__worker.isRunning():
            self.__toggle_worker()

    def __set_workstation(self, workstation):
        current = self.__settings.to_dict()
        current['CORE']['WORKSTATION'] = workstation
        # update ini
        self.__settings.update(current)
        # update settings
        self.__settings.load()
        # update state with workstation name
        self.__interface.update_ui_data_signal.emit({
            'workstation_name': workstation,
        })

    def __set_order(self, order):
        self.__order = order

        self.__interface.update_ui_data_signal.emit({
            'order_name': self.__order,
        })

        if self.__worker is not None and not self.__worker.isRunning():
            self.__toggle_worker()

    def __worker_error_handler(self, error):
        self.__interface.error_message_signal.emit(
            'Erro de processamento de ficheiros',
            'Ocorreu um erro ao processar ficheiros de log!\nPor favor, tente novamente.'
        )

    def __backup_job_error_handler(self, error):
        print('[Controller] - backup_job_error_handler called', error)

    def __backup_job_movement_handler(self, movement):
        print('[Controller] - backup_job_movement_handler called', movement)

    def __backup_job_start_handler(self):
        print('[Controller] - backup_job_start_handler called')

    def __backup_job_stop_handler(self):
        print('[Controller] - backup_job_stop_handler called')


if __name__ == '__main__':
    try:
        logger.info('App process is starting...')

        ctrl = Controller()
        ctrl.run()
    except Exception as e:
        logger.error('App shutdown abruptly!', exc_info=True)
