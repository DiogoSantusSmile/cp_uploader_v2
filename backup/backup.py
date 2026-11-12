from PyQt5.QtCore import QThread, pyqtSignal

from logger_config import setup_logger
from enum import Enum
import os
import shutil
import time
import hashlib

logger = setup_logger('backup')


def copy_job(origin, destination):

    os.makedirs(destination, exist_ok=True)

    for directory_name in os.listdir(origin):

        source_directory = os.path.join(
            origin,
            directory_name
        )

        if not os.path.isdir(source_directory):
            continue

        destination_directory = os.path.join(
            destination,
            directory_name
        )

        if os.path.exists(destination_directory):
            continue

        logger.info(
            'Starting backup of directory: %s',
            source_directory
        )

        source_checksum = calculate_directory_checksum(
            source_directory
        )

        shutil.copytree(
            source_directory,
            destination_directory
        )

        destination_checksum = calculate_directory_checksum(
            destination_directory
        )

        if source_checksum != destination_checksum:

            shutil.rmtree(
                destination_directory,
                ignore_errors=True
            )

            raise RuntimeError(
                f'Directory checksum mismatch: '
                f'{directory_name}'
            )

        logger.info(
            'COPY OK | Directory=%s | SHA256=%s',
            directory_name,
            source_checksum
        )

        yield directory_name


def move_job(origin, destination):

    os.makedirs(destination, exist_ok=True)

    for directory_name in os.listdir(origin):

        source_directory = os.path.join(
            origin,
            directory_name
        )

        if not os.path.isdir(source_directory):
            continue

        destination_directory = os.path.join(
            destination,
            directory_name
        )

        if os.path.exists(destination_directory):
            continue

        logger.info(
            'Starting move of directory: %s',
            source_directory
        )

        source_checksum = calculate_directory_checksum(
            source_directory
        )

        shutil.copytree(
            source_directory,
            destination_directory
        )

        destination_checksum = calculate_directory_checksum(
            destination_directory
        )

        if source_checksum != destination_checksum:

            shutil.rmtree(
                destination_directory,
                ignore_errors=True
            )

            raise RuntimeError(
                f'Directory checksum mismatch: '
                f'{directory_name}'
            )

        shutil.rmtree(
            source_directory
        )

        logger.info(
            'MOVE OK | Directory=%s | SHA256=%s',
            directory_name,
            source_checksum
        )

        yield directory_name

def calculate_directory_checksum(directory):
    """
    Calcula um checksum SHA256 de todos os ficheiros
    existentes no diretório e subdiretórios.
    """

    sha256 = hashlib.sha256()

    for root, _, files in os.walk(directory):
        for file in sorted(files):
            file_path = os.path.join(root, file)

            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)

    return sha256.hexdigest()


class Action(Enum):
    # store a (label, function) tuple as the value so the enum member
    # carries its associated job directly
    COPY = ('COPY', copy_job)
    MOVE = ('MOVE', move_job)

    def __init__(self, label, func):
        self._label = label
        # expose the function as an attribute on the enum member
        self.job = func

    def __str__(self):
        return self._label


class LogBackupThread(QThread):
    """
    Thread para mover logs que já foram carregados para o Controlo de Produção.

    Este job tem 2 ações possíveis:
        'COPY' e 'MOVE'. A ação 'COPY' irá copiar os logs para a pasta de destino,
        mantendo os arquivos originais na dentro duma pasta de arquivo.
        A ação 'MOVE' irá mover os logs para a pasta de destino, removendo os arquivos
        originais da pasta de origem.

    Signals:
        start_signal: Emite quando a thread é iniciada.
        stop_signal: Emite quando a thread é parada, seja por conclusão ou por
                     pedido de paragem.
        movement_signal: Emite o nome do ficheiro que foi movido ou copiado.
        error_signal: Emite uma mensagem de erro caso ocorra algum problema
                        durante a execução da tarefa
    """

    # Defina as ações permitidas como Enum; ACTION_MAP contém as funções
    ACTIONS = Action

    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    movement_signal = pyqtSignal(str)

    def __init__(self, action=ACTIONS.COPY, *args, **kwargs):
        self.__origin = kwargs.pop('origin')
        self.__destination = kwargs.pop('destination')

        self.on_start = kwargs.pop('on_start')
        self.on_stop = kwargs.pop('on_stop')

        self.action = action
        self.__wants_to_stop = False

        on_error = kwargs.pop('on_error')
        on_movement = kwargs.pop('on_movement')

        super().__init__(*args, **kwargs)

        self.started.connect(self.start_handler)
        self.finished.connect(self.finish_handler)
        self.movement_signal.connect(on_movement)
        self.error_signal.connect(on_error)

    def start_handler(self):
        logger.info('Worker job started.')
        self.on_start()

    def finish_handler(self):
        logger.info('Worker job finished.')
        self.on_stop()

    def run(self):
        self.__wants_to_stop = False

        logger.info(
            'Backup thread started. Origin=%s, Destination=%s, Action=%s',
            self.__origin,
            self.__destination,
            self.action.name
        )

        while not self.__wants_to_stop:

            try:

                for directory_name in self.action.job(
                    self.__origin,
                    self.__destination,
                ):

                    self.movement_signal.emit(
                        directory_name
                    )

                time.sleep(1)

            except Exception as e:

                logger.exception(e)

                self.error_signal.emit(
                    str(e)
                )

                break

        logger.info('Backup thread finished')

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, value):
        # Accept either an Action enum member or a string with the member name
        try:
            if isinstance(value, Action):
                action_member = value
            elif isinstance(value, str):
                action_member = Action[value]
            else:
                action_member = Action(value)
        except Exception:
            allowed = [a.name for a in Action]
            logger.error(
                'Invalid action provided for LogBackupThread: %s. Allowed: %s',
                value,
                allowed,
            )
            raise ValueError('Invalid action. Must be one of {}'.format(allowed))

        self.__action = action_member

    def stop(self):
        self.__wants_to_stop = True
