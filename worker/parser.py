from .helpers import (
    parse_aleader_aoi,
    parse_aoi_mek,
    parse_stark_eol_v2,
    parse_schreder,
    parse_ziv_eol,
    parse_btf13,
    parse_fcl0022,
    parse_zurc,
    parse_btf_1177,
    parse_btf14,
    parse_bt81,
    parse_mil07,
    parse_dboard_r5,
    parse_lvs,
    parse_starktest_pc2,
    parse_automatic_label_check_01,
    parse_altra_air_lateral_uar260441,
    parse_btf06,
    parse_leak_test_1,
    parse_leak_test_2,
    parse_sram_mainboard_11
)
from logger_config import setup_logger

logger = setup_logger('parser')

TOOLS = {
    'AOI ALeader': {
        'file_extensions': ['.csv'],
        'parser': parse_aleader_aoi
    },
    'AOI MEK': {
        'file_extensions': ['.xml'],
        'parser': parse_aoi_mek
    },
    'EOL STARK': {
        'file_extensions': ['.json'],
        'parser': parse_stark_eol_v2
    },
    'SCHREDER': {
        'file_extensions': ['.json'],
        'parser': parse_schreder,
    },
    'EOL ZIV': {
        'file_extensions': ['.csv'],
        'parser': parse_ziv_eol
    },
    'BTF13': {
        'file_extensions': ['.xml'],
        'parser': parse_btf13
    },
    'FCL0022': {
        'file_extensions': [''],
        'parser': parse_fcl0022,
        'exclude_if_filename_contains': ['NONE'],
    },
    'ZURC': {
        'file_extensions': ['.json'],
        'parser': parse_zurc,
    },
    'BTF1177': {
        'file_extensions': ['.json'],
        'parser': parse_btf_1177,
    },
    'BTF14': {
        'file_extensions': ['.xml'],
        'parser': parse_btf14,
    },
    'MIL07': {
        'file_extensions': ['.txt'],
        'parser': parse_mil07,
    },
    'BT81': {
        'file_extensions': ['.xml'],
        'parser': parse_bt81,
    },
    'DBOARD_R5': {
        'file_extensions': ['.xml'],
        'parser': parse_dboard_r5,
    },
    'LVS': {
        'file_extensions': ['.csv'],
        'parser': parse_lvs,
    },
    'STARKTEST_PC2': {
        'file_extensions': ['.json'],
        'parser': parse_starktest_pc2,
    },
    'AUTOMATIC_LABEL_CHECK_01': {
        'file_extensions': ['.xml'],
        'parser': parse_automatic_label_check_01,
    },
    'ALTRA_air_lateral_UAR260441': {
        'file_extensions': ['.xml'],
        'parser': parse_altra_air_lateral_uar260441,
    },
    'BTF06': {
        'file_extensions': ['.json'],
        'parser': parse_btf06,
    },
    'LEAK_TEST_1': {
        'file_extensions': ['.csv'],
        'parser': parse_leak_test_1,
    },
    'LEAK_TEST_2': {
        'file_extensions': ['.csv'],
        'parser': parse_leak_test_2,
    },
    'SRAM_MAINBOARD_11': {
        'file_extensions': ['.csv'],
        'parser': parse_sram_mainboard_11
    },
}


class Parser:
    __tool = None
    __parser = None
    __extensions = None
    __excluded_strings = None

    def __init__(self, tool):
        self.tool = tool

    def parse(self, path):
        if self.__extensions and not path.lower().endswith(tuple(self.__extensions)):
            return {
                'status': 'error',
                'path': path,
                'message': 'Extensão de ficheiro não suportada.',
                'ignore': True
            }
        if self.__excluded_strings and any(excl_string in path for excl_string in self.__excluded_strings):
            return {
                'status': 'error',
                'path': path,
                'message': f'Ficheiro contêm uma das seguintes palavras proibidas no seu nome: '
                           f'{self.__excluded_strings}',
                'ignore': True
            }

        try:
            return {
                'status': 'success',
                'path': path,
                'data': self.__parser(path),
                'ignore': False
            }
        except Exception as e:
            logger.exception(e)
            return {
                'status': 'error',
                'path': path,
                'message': str(e),
                'ignore': False
            }

    @property
    def tool(self):
        return self.__tool

    @tool.setter
    def tool(self, value):
        if value not in TOOLS:
            raise ValueError(f'Ferramenta \'{value}\' não está na lista de ferramentas permitidas.')

        self.__tool = value
        self.__parser = TOOLS[value]['parser']
        self.__extensions = TOOLS[value]['file_extensions']
        self.__excluded_strings = TOOLS[value].get('exclude_if_filename_contains', [])
