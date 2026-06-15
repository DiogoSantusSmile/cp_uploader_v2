# from datetime import datetime
#
# import os
# import pytest
#
# from db.enums import UploadStatus
# from db.models import Base, Logfile, LogfileUpload
# from db.services import Service, LogfileService
# from db.session import engine_factory, session_scope
#
#
# class TestService:
#     def setup_class(self):
#         os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
#
#         if os.path.exists('test.db'):
#             os.remove('test.db')
#
#         self.db_engine = engine_factory()
#
#         Base.metadata.create_all(self.db_engine)
#
#     def teardown_class(self):
#         Base.metadata.drop_all(self.db_engine)
#         self.db_engine.dispose()
#         del os.environ['DATABASE_URL']
#
#     def test_model_setter(self):
#         valid_models = [
#             Logfile,
#             LogfileUpload
#         ]
#
#         with pytest.raises(ValueError):
#             Service(model=str)
#
#         for model in valid_models:
#             Service(model=model)
#
#     def test_model_getter(self):
#         obj = Service(model=Logfile)
#
#         assert obj.model == Logfile
#
#     def test_create(self):
#         service = Service(model=Logfile)
#
#         data = service.create(
#             absolute_path='C:\\Path\\to\\file.txt',
#             filename='file.txt'
#         )
#
#         assert isinstance(data['id'], int)
#         assert isinstance(data['created_at'], datetime)
#         assert data['absolute_path'] == 'C:\\Path\\to\\file.txt'
#         assert data['filename'] == 'file.txt'
#         assert data['uploads'] == []
#
#     def test_filter_by_field_value(self):
#         service = Service(model=Logfile)
#
#         with session_scope() as session:
#             session.add_all([
#                 Logfile(absolute_path='C:\\Path\\to\\file.txt', filename='file.txt'),
#                 Logfile(absolute_path='C:\\Path\\to\\file2.txt', filename='file.txt'),
#                 Logfile(absolute_path='C:\\Path\\to\\file3.txt', filename='file2.txt'),
#             ])
#             session.commit()
#
#         data = service.filter_by(filename='file.txt')
#
#         assert len(data) == 2
#         assert data[0]['absolute_path'] == 'C:\\Path\\to\\file.txt'
#         assert data[1]['absolute_path'] == 'C:\\Path\\to\\file2.txt'
#
#     def test_filter_by_ordered(self):
#         service = Service(model=Logfile)
#
#         with session_scope() as session:
#             session.add_all([
#                 Logfile(absolute_path='C:\\Path\\to\\file.txt', filename='BFile.txt'),
#                 Logfile(absolute_path='C:\\Path\\to\\file2.txt', filename='CFile.txt'),
#                 Logfile(absolute_path='C:\\Path\\to\\file3.txt', filename='AFile.txt'),
#             ])
#             session.commit()
#
#         data = service.filter_by(order_by='filename')
#
#         assert len(data) == 3
#         assert data[0]['filename'] == 'AFile.txt'
#         assert data[1]['filename'] == 'BFile.txt'
#         assert data[2]['filename'] == 'CFile.txt'
#
#     def test_filter_by_limited(self):
#         service = Service(model=Logfile)
#
#         with session_scope() as session:
#             session.add_all([
#                 Logfile(absolute_path='C:\\Path\\to\\file.txt', filename='file.txt'),
#                 Logfile(absolute_path='C:\\Path\\to\\file2.txt', filename='file.txt'),
#             ])
#             session.commit()
#
#         data = service.filter_by(limit=1)
#
#         assert len(data) == 1
#         assert data[0]['absolute_path'] == 'C:\\Path\\to\\file.txt'
#
#
# class TestLogfileService:
#     def setup_class(self):
#         os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
#
#         if os.path.exists('test.db'):
#             os.remove('test.db')
#
#         self.db_engine = engine_factory()
#
#         Base.metadata.create_all(self.db_engine)
#
#     def teardown_class(self):
#         Base.metadata.drop_all(self.db_engine)
#         self.db_engine.dispose()
#         del os.environ['DATABASE_URL']
#
#     def test_create(self):
#         data = LogfileService().create(
#             absolute_path='C:\\Path\\to\\file.txt',
#             filename='file.txt'
#         )
#
#         assert isinstance(data['id'], int)
#         assert isinstance(data['created_at'], datetime)
#         assert data['absolute_path'] == 'C:\\Path\\to\\file.txt'
#         assert data['filename'] == 'file.txt'
#         assert len(data['uploads']) == 0
#
#     def test_create_with_upload(self):
#         data = LogfileService().create(
#             absolute_path='C:\\Path\\to\\file.txt',
#             filename='file.txt',
#             upload={
#                 'status': UploadStatus.FAILED,
#                 'error_message': 'Failure message',
#                 'operator': 'John Doe'
#             }
#         )
#
#         assert isinstance(data['id'], int)
#         assert isinstance(data['created_at'], datetime)
#         assert data['absolute_path'] == 'C:\\Path\\to\\file.txt'
#         assert data['filename'] == 'file.txt'
#         assert len(data['uploads']) == 1
#         assert data['uploads'][0]['status'] == UploadStatus.FAILED
#         assert data['uploads'][0]['error_message'] == 'Failure message'
#         assert data['uploads'][0]['operator'] == 'John Doe'
#         assert isinstance(data['uploads'][0]['created_at'], datetime)
#         assert isinstance(data['uploads'][0]['id'], int)
#         assert data['uploads'][0]['logfile_id'] == data['id']
#
#     def test_get_all(self):
#         with session_scope() as session:
#             for i in range(1, 11):
#                 logfile = Logfile(
#                     absolute_path=f'C:\\Path\\to\\file{i}.txt',
#                     filename=f'file{i}.txt'
#                 )
#                 upload = LogfileUpload(
#                     logfile=logfile,
#                     status=UploadStatus.SUCCESS,
#                     error_message='',
#                     operator='John Doe'
#                 )
#                 logfile.uploads.append(upload)
#                 session.add_all([logfile, upload])
#
#             session.commit()
#
#         data = LogfileService().get_all()
#
#         assert len(data) == 10
#
#     def test_get_all_limit(self):
#         with session_scope() as session:
#             for i in range(1, 11):
#                 logfile = Logfile(
#                     absolute_path=f'C:\\Path\\to\\file{i}.txt',
#                     filename=f'file{i}.txt'
#                 )
#                 upload = LogfileUpload(
#                     logfile=logfile,
#                     status=UploadStatus.SUCCESS,
#                     error_message='',
#                     operator='John Doe'
#                 )
#                 logfile.uploads.append(upload)
#                 session.add_all([logfile, upload])
#
#             session.commit()
#
#         data = LogfileService().get_all(limit=5)
#
#         assert len(data) == 5
#         assert data[0]['filename'] == 'file1.txt'
#         assert data[1]['filename'] == 'file2.txt'
#         assert data[2]['filename'] == 'file3.txt'
#         assert data[3]['filename'] == 'file4.txt'
#         assert data[4]['filename'] == 'file5.txt'
#
#     def test_get_all_offset(self):
#         with session_scope() as session:
#             for i in range(1, 11):
#                 logfile = Logfile(
#                     absolute_path=f'C:\\Path\\to\\file{i}.txt',
#                     filename=f'file{i}.txt'
#                 )
#                 upload = LogfileUpload(
#                     logfile=logfile,
#                     status=UploadStatus.SUCCESS,
#                     error_message='',
#                     operator='John Doe'
#                 )
#                 logfile.uploads.append(upload)
#                 session.add_all([logfile, upload])
#
#             session.commit()
#
#         data = LogfileService().get_all(offset=5, limit=5)
#
#         assert len(data) == 5
#         assert data[0]['filename'] == 'file6.txt'
#         assert data[1]['filename'] == 'file7.txt'
#         assert data[2]['filename'] == 'file8.txt'
#         assert data[3]['filename'] == 'file9.txt'
#         assert data[4]['filename'] == 'file10.txt'
