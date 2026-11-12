from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.collections import InstrumentedList

from .models import Base, Logfile, LogfileUpload
from .session import session_scope


class Service:
    __model = None

    def __init__(self, model):
        self.model = model

    def create(self, **kwargs) -> dict:
        obj = self.__model(**kwargs)

        with session_scope() as session:
            session.add(obj)
            session.commit()
            data = self._to_dict(obj)

        return data

    def filter_by(self, order_by=None, limit=None, null_fields=None, **kwargs) -> list[dict]:
        data = []

        with session_scope() as session:
            queryset = session.query(self.model)

            for key, value in kwargs.items():
                queryset = queryset.filter(self.model.__getattribute__(self.model, key) == value)

            if null_fields is not None:
                for field in null_fields:
                    queryset = queryset.filter(field != None)

            if order_by is not None:
                queryset = queryset.order_by(order_by)

            if limit is not None:
                queryset = queryset.limit(limit)

            for obj in queryset.all():
                data.append(self._to_dict(obj))

        return data

    def _to_dict(self, instance) -> dict:
        serialized = {}

        for attr in inspect(self.model).attrs:
            serialized[attr.key] = getattr(instance, attr.key)
            if isinstance(serialized[attr.key], InstrumentedList):
                serialized[attr.key] = [o.id for o in serialized[attr.key]]

        return serialized

    @property
    def model(self):
        return self.__model

    @model.setter
    def model(self, obj):
        model_classes = [mapper.class_.__name__ for mapper in Base.registry.mappers]

        if obj.__name__ not in model_classes:
            raise ValueError('model is not a valid Model choice.')

        self.__model = obj


class LogfileService(Service):
    def __init__(self):
        super().__init__(model=Logfile)

    def create(self, **kwargs):
        upload = None

        if 'upload' in kwargs.keys():
            upload = kwargs.pop('upload')

        try:
            logfile_data = super().create(**kwargs)
        except IntegrityError:
            logfile_data = self.filter_by(absolute_path=kwargs['absolute_path'])[0]

        if upload is not None:
            upload.update({'logfile_id': logfile_data['id']})

            logfile_data['uploads'].append(
                LogfileUploadService().create(**upload)
            )

        return logfile_data

    def get_all(self, limit=100, offset=0):
        data = []

        with session_scope() as session:
            obj_list = session.query(self.model) \
                .options(joinedload(self.model.uploads)) \
                .offset(offset) \
                .limit(limit) \
                .all()

            for obj in obj_list:
                serialized_data = self._to_dict(obj)
                uploads = serialized_data.pop('uploads')
                serialized_data['uploads'] = []

                for upload_id in uploads:
                    serialized_data['uploads'].append(
                        LogfileUploadService().filter_by(id=upload_id)[0]
                    )

                data.append(serialized_data)

        return data


class LogfileUploadService(Service):
    def __init__(self):
        super().__init__(model=LogfileUpload)
