from .helpers import get_files_from_location

# Simula a lista que viria do Settings
ignored = ['console_logs','tmp', 'temp']
location = r'C:\Users\dsantos\Desktop\TestingLog'

files = get_files_from_location(location, ignored_dirs=ignored)
print(f'Ficheiros encontrados: {files}')