from configparser import ConfigParser, NoSectionError
from datetime import datetime


class Settings:
    __settings_file = 'app.ini'
    url = 'http://192.168.1.222:8600/api/'
    tool = ''
    allowed_workstations = ''
    workstation = ''
    logs_location = ''
    ignored_directories = [] # Lista base, incluindo o default atual
    date_start_logs = datetime.now()
    line = ''

    def __init__(self):
        try:
            self.load()
        except NoSectionError:
            self.save()

    def load(self):
        """
        Carrega o conteúdo do ficheiro `app.ini` e atualiza o objeto.
        """
        config = ConfigParser()
        config.read(self.__settings_file, encoding='utf-8')

        self.url = config.get('NETWORK', 'URL')
        self.tool = config.get('CORE', 'TOOL')
        self.workstation = config.get('CORE', 'WORKSTATION')
        self.allowed_workstations = config.get('CORE', 'ALLOWED_WORKSTATIONS')
        self.logs_location = config.get('LOGS', 'LOGS_LOCATION')
        # Ler lista do .ini (converter de string separada por vírgulas para lista)
        ignored = config.get('LOGS', 'IGNORED_DIRECTORIES')
        self.ignored_directories = [d.strip() for d in ignored.split(',')]
        self.date_start_logs = datetime.strptime(
            config.get('LOGS', 'DATE_START_LOGS'),
            '%Y-%m-%d %H:%M:%S'
        )
        self.line = config.get('UARTRACKER', 'LINE')

    def save(self):
        """
        Guarda configurações no ficheiro `app.ini`.

        :return: None
        """
        config = ConfigParser()
        config.update({
            'CORE': {
                'TOOL': self.tool,
                'ALLOWED_WORKSTATIONS': self.allowed_workstations,
                'WORKSTATION': self.workstation
            },
            'NETWORK': {
                'URL': self.url
            },
            'LOGS': {
                'LOGS_LOCATION': self.logs_location,
                'DATE_START_LOGS': self.date_start_logs.strftime('%Y-%m-%d %H:%M:%S'),
                'IGNORED_DIRECTORIES': ','.join(self.ignored_directories)
            },
            'UARTRACKER': {
                'LINE': self.line
            },
        })

        with open(self.__settings_file, 'w', encoding='utf-8') as config_file:
            config.write(config_file)

    def to_dict(self):
        """
        Devolve propriedades da instância organizadas num dicionário.

        :return: Dicionário com os atributos da instância.
        :rtype: dict
        """
        dict_data = {
            'CORE': {
                'TOOL': self.tool,
                'ALLOWED_WORKSTATIONS': self.allowed_workstations,
                'WORKSTATION': self.workstation,
            },
            'NETWORK': {
                'URL': self.url
            },
            'LOGS': {
                'LOGS_LOCATION': self.logs_location,
                'DATE_START_LOGS': self.date_start_logs,
            },
            'UARTRACKER': {
                'LINE': self.line
            },
        }
        return dict_data

    def update(self, settings: dict, save=True):
        """
        Atualiza a instância com as novas definições. Opcionalmente pode guardar
        as novas definições no ficheiro `app.ini`.

        :param settings: Dicionário que contém as novas configurações
        :type settings: dict
        :param save: Indica se deve guardar as definições de forma persistente.
        É True por defeito.
        :type save: bool, opcional
        :return: None
        """
        self.url = settings['NETWORK']['URL']
        self.tool = settings['CORE']['TOOL']
        self.allowed_workstations = settings['CORE']['ALLOWED_WORKSTATIONS']
        self.workstation = settings['CORE']['WORKSTATION']
        self.logs_location = settings['LOGS']['LOGS_LOCATION']
        self.date_start_logs = settings['LOGS']['DATE_START_LOGS']
        self.line = settings['UARTRACKER']['LINE']

        if save:
            self.save()
