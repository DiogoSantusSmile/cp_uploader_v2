import logging
import os
import sys


def setup_logger(name='application'):
    def handle_exception(exc_type, exc_value, exc_traceback):
        """
        Função encarregada de logar exceções não capturadas no programa.

        1. Regista o erro usando o logger configurado:
            - Mensagem "Uncaught exception"
            - Inclui informação completa da exceção (tipo, valor e traceback)
        2. Termina o processo imediatamente com código de saída 1: sys.exit(1).

        Parâmetros:
        - exc_type (Type[BaseException]): Tipo (classe) da exceção que foi levantada. Exs: ValueError, KeyError, etc.
        - exc_value (BaseException): Objeto da exceção em si, que contém a mensagem de erro e possivelmente outros
        atributos (por exemplo, args, etc).
        - exc_traceback (traceback): Objeto traceback que representa a "pilha" de chamadas no ponto em que a exceção
        ocorreu.
        """
        # Log error
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        # force the process to terminate
        sys.exit(1) # todo: mostrar pop-up erro

    logs_location = 'logs/'
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not os.path.exists(logs_location):
        os.mkdir(logs_location)

    # Console handler (outputs logs to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(os.path.join(logs_location, 'application.log'))
    file_handler.setLevel(logging.DEBUG)

    # Add consistent formatting for logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Prevent duplicate logs by removing handlers if already defined
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    sys.excepthook = handle_exception

    return logger
