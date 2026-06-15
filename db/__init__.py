from alembic.config import Config
from alembic import command

import os

from .services import LogfileService, LogfileUploadService
from logger_config import setup_logger

__all__ = [
    'LogfileService',
    'LogfileUploadService'
]

DATABASE_URL = os.environ.get('DATABASE_URL')

logger = setup_logger('db')

if not os.path.exists('./app.db'):
    logger.info('Database does not exist, creating a new one...')

    try:
        alembic_cfg = Config('alembic.ini')
        alembic_cfg.set_main_option('sqlalchemy.url', DATABASE_URL)
        command.upgrade(alembic_cfg, 'head')

        logger.info('Database created successfully.')
    except Exception as e:
        logger.exception(e)
