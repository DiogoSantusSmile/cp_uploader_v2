from PyQt5.QtCore import QThread

from logger_config import setup_logger

logger = setup_logger('tasks')


class AsynchronousTask(QThread):
    def __init__(self, *args, **kwargs):
        self.result = None
        self.target = kwargs.pop('target')
        self.target_kwargs = kwargs.pop('target_kwargs', {})
        self.on_finish = kwargs.pop('on_finish', None)
        on_progress = kwargs.pop('on_progress', None)

        super().__init__(*args, **kwargs)

        if self.on_finish is not None:
            self.finished.connect(self.finished_handler)

        if on_progress is not None:
            self.target_kwargs.update({'on_progress': on_progress})

    def run(self):
        self.result = self.target(**self.target_kwargs)
        self.finished.emit()

    def finished_handler(self):
        try:
            self.on_finish(self.result)
        except TypeError as e:
            logger.exception(e)
