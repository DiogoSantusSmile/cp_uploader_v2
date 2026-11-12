from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os


def engine_factory():
    return create_engine(os.environ.get('DATABASE_URL'))


def session_factory():
    engine = engine_factory()
    Session = sessionmaker(bind=engine)
    return Session()


@contextmanager
def session_scope():
    session = session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
