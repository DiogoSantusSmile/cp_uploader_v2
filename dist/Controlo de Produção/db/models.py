from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship

from .enums import UploadStatus


class Base(DeclarativeBase):
    pass


class Logfile(Base):
    __tablename__ = 'logfile'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    absolute_path = Column(String(250), nullable=False, unique=True)
    filename = Column(String(100), nullable=False)
    is_valid = Column(Boolean, nullable=False, default=True)

    uploads = relationship('LogfileUpload', back_populates='logfile')

    def __str__(self) -> str:
        return str(self.filename)


class LogfileUpload(Base):
    __tablename__ = 'logfile_upload'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(Enum(UploadStatus), nullable=False, default=UploadStatus.FAILED)
    error_message = Column(String(500), nullable=True, default=None)
    operator = Column(String(100), nullable=False)

    logfile_id = Column(Integer, ForeignKey('logfile.id'), nullable=False)
    logfile = relationship('Logfile')

    def __str__(self) -> str:
        return f'Upload {self.created_at} - {self.status}'




