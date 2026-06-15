from PyQt5.QtCore import QThread, pyqtSignal

import time

from .helpers import get_files_from_location
from logger_config import setup_logger

logger = setup_logger('worker')


class Worker(QThread):
    stop_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, settings_instance, *args, **kwargs):
        self.location = kwargs.pop('location')
        self.parser = kwargs.pop('parser')
        self.on_start = kwargs.pop('on_start')
        self.on_finish = kwargs.pop('on_finish')
        self.on_parse = kwargs.pop('on_parse')
        self.on_error = kwargs.pop('on_error')
        self.__wants_to_stop = False

        super().__init__(*args, **kwargs)
        self.settings = settings_instance # Armazena para usar no run()
        self.started.connect(self.start_handler)
        self.finished.connect(self.finish_handler)
        self.stop_signal.connect(self.stop)
        self.error_signal.connect(self.on_error)

    def start_handler(self):
        logger.info('Worker job started.')
        self.on_start()

    def finish_handler(self):
        logger.info('Worker job finished.')
        self.on_finish()

    def run(self):
        # acesso à instância, não ao módulo
        ignored = self.settings.ignored_directories

        self.__wants_to_stop = False

        while not self.__wants_to_stop:
            try:
                # Passa os diretórios ignorados para a função
                for file in get_files_from_location(self.location, ignored_dirs=ignored):
                    if self.__wants_to_stop:
                        break

                    logger.info(f'Parsing {file}.')
                    result = self.parser.parse(file)
                    logger.info(f'Parsing {file} done.\n\t{result}')
                    self.on_parse(result)

                time.sleep(1)
            except Exception as e:
                logger.exception(e)
                self.error_signal.emit(str(e))
                break

    def stop(self):
        self.__wants_to_stop = True