from datetime import datetime, timezone

import json
import os
import xml.etree.ElementTree as ET

from helpers import parse_timestamp

def get_files_from_location(location, ignored_dirs=None):
    """
    Obtém lista de ficheiros num diretório recursivamente.

    Esta função lista todos os ficheiros de um diretório e
    sub-diretórios. Devolve uma lista de caminhos completos
    para cada um dos ficheiros encontrados. Ignora a subpasta
    'processados' e todos os ficheiros no seu interior, uma vez
    que conterá ficheiros que já foram processados.

    :param location: Diretório raíz pelo qual se inicia a procura.
    :type location: str
    :return: Lista de diretórios absolutos dos ficheiros encontrados
        dentro do diretório raíz e respetivos sub-diretórios.
    :rtype: list
    """
    # Regra fixa + Regras dinâmicas do .ini
    base_ignored = {'processed'}
    dynamic_ignored = set(ignored_dirs) if ignored_dirs else set()
    all_ignored = base_ignored.union(dynamic_ignored)

    all_files = []

    for root, dirs, files in os.walk(location):
        # Verifica se alguma parte do caminho faz parte do caminho da lista de ignorados
        if any(part in all_ignored for part in root.split(os.sep)):
            continue

        # if os.path.join(location, 'processed') in root:
        #     continue

        for file in files:
            all_files.append(os.path.join(root, file))

    return all_files


def parse_aleader_aoi(path):
    """
    Função de processamento de logs das AOIs ALeader.

    Analisa ficheiro CSV gerado pela AOI  e extrai dados relativos á inspeção
    do painel.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str
    :raises ValueError: Caso o campo do número de série seja nulo.
    :return: Dicionário que contém lista de números de série, estados, data
             de processamento e outros.
    :rtype: dict
    """
    timestamp = None
    status = None
    machine_id = None
    serial_number = None
    children = []

    with open(path, 'r') as csv_file:
        for i, row in enumerate(csv_file):
            if i == 1:
                splitted_row = row.rstrip('\n').split(',')
                timestamp = datetime.strptime(splitted_row[0], '%Y-%m-%d %H:%M:%S.%f')
                status = 'OK' if splitted_row[3].lower() == 'pass' else 'NG'
                machine_id = splitted_row[4]
                serial_number = splitted_row[5]
                manu_order = splitted_row[16]

                if not serial_number:
                    raise ValueError('serial number is empty')

            if i > 3:
                splitted_row = row.rstrip('\n').split(',')
                unit_result = splitted_row[12]

                if unit_result == 'NG':
                    children.append({'status': unit_result, 'position': int(splitted_row[2].split('_')[1])})

    return {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': timestamp
            }
        },
        'children': children,
        'machine_id': machine_id,
        'order': manu_order
    }


def parse_aoi_mek(path):
    """
    Função de processamento de logs de AOIs MEK.

    Analisa ficheiro XML da AOI MEK para extrair números de série, estados, data
    de inspeção e ordem de fabrico.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados, data
        de processamento e outros.
    :rtype: dict
    """
    serial_numbers = {}
    tree = ET.parse(path)
    root = tree.getroot()

    timestamp = datetime.strptime(root.find('date').text, '%Y%m%d%H%M%S')
    order = root.find('lot_no').text
    serial = root.find('serial').text

    if not serial:
        raise ValueError('serial number is empty')

    status = 'OK' if root.find('status').text.lower() == 'good' else 'NG'
    side = 'TOP' if serial.endswith('1') else 'BOT'

    return {
        'serial_numbers': {
            serial: {
                'status': status,
                'timestamp': timestamp
            }
        },
        'order': order,
        'side': side
    }


def parse_stark_eol(path):
    """
    Função de processamentos de logs dos testes EOL da STARK.

    Analisa ficheiro XML da AOI MEK para extrair números de série, estados, data
    de teste.

    ####### ATENÇÃO #######
        Versão descontinuada pelo cliente.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados, data
        de processamento.
    :rtype: dict
    """
    tree = ET.parse(path)
    root = tree.getroot()

    timestamp = datetime.strptime(root.find('date').text, '%Y%m%d%H%M%S')
    status = 'OK' if root.find('result').text.lower() == 'passed' else 'NG'
    serial_no = root.find('serial_number').text

    if not serial_no:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            serial_no: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }


def parse_stark_eol_v2(path):
    """
    Função de processamentos de logs dos testes EOL da STARK versão 2 (formato JSON).

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados, data
        de processamento.
    :rtype: dict
    """
    with open(path, 'r') as file:
        data = json.load(file)

    status = 'OK' if data['testResult'].lower() == 'passed' else 'NG'

    if not data['serialNumber']:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            data['serialNumber']: {
                'status': status,
                'timestamp': datetime.fromisoformat(data['date'])
            }
        }
    }


def parse_ziv_eol(path):
    """
    Função de processamento de logs para registo automático dos testes ZIV no UARTRACKER (old-software).

    Analisa ficheiros CSV gerados, e extrai dados relevantes do ficheiro (serial_number, timestamp, status).

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :raises ValueError:
    - Caso serial_number não exista.
    - Caso o campo timestamp não esteja no formato ISO-8601.

    :return: Dicionário que contém lista de números de série, estado e data de processamento.
    :rtype: dict
    """
    with open(path, 'r') as csv_file:
        for i, row in enumerate(csv_file):
            if i == 0:
                splitted_row = row.rstrip('\n').split(';')
                status = 'OK' if splitted_row[0].lower() == 'passed' else 'NOK'

                timestamp = parse_timestamp(splitted_row[4] + splitted_row[5])

                serial_number = splitted_row[3]

                if not serial_number:
                    raise ValueError('serial number is empty')

                return {
                    'serial_numbers': {
                        serial_number: {
                            'status': status,
                            'timestamp': timestamp
                        }
                    }
                }


def parse_btf13(path):
    """
    Função de processamento de logs da BTF13.

    Analisa ficheiro XML da BTF13 para extrair números de série, estados e data
    de inspeção.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    serial_numbers = {}
    tree = ET.parse(path)
    root = tree.getroot()

    timestamp_str = root.find('endtime').text.strip().replace('_', '')
    timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
    serial = root.find('serialnumber').text
    status = 'OK' if root.find('result').text.lower() == 'pass' else 'NG'

    if not serial:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            serial: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }


def parse_fcl0022(path):
    status = None
    serial_number = None
    timestamp = None

    # get filename
    filename = str(path)
    # ignore files that end in NONE (dummys, etc)
    if filename[-4:] != 'NONE':
        with open(path, 'r') as file:
            for _, row in enumerate(file):
                splitted_row = row.rstrip('\n').split(';')

                if splitted_row[0].lower() == 'boardresult':
                    if splitted_row[1]:
                        status = 'OK' if splitted_row[1].lower() == 'pass' else 'NOK'

                if splitted_row[0].lower() == 'sn':
                    serial_number = splitted_row[1]

                if splitted_row[0].lower() == 'timeend':
                    try:
                        timestamp = datetime.strptime(splitted_row[1] + splitted_row[2], '%m/%d/%Y%H:%M:%S.%f')
                    except (ValueError, TypeError):
                        message = '"timestamp" must be a valid string in ISO-8601 format.'
                        raise ValueError(message)

            if not serial_number:
                raise ValueError('serial number is empty')

            if not status:
                raise ValueError('BOARDRESULT is empty')

            return {
                'serial_numbers': {
                    serial_number: {
                        'status': status,
                        'timestamp': timestamp
                    }
                }
            }


def parse_zurc(path):
    """
    Função de processamento de logs ZURC.

    Analisa o ficheiro log em JSON para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    with open(path, 'r') as file:
        data = json.load(file)

    status = 'OK' if data['result'] == 99 else 'NG'
    serial_number = data['serial_number']
    lot_number = data['lote']

    if not lot_number:
        raise ValueError('lot number is empty')

    if not serial_number:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': datetime.strptime(data['fecha'], "%Y-%m-%d %H:%M:%S"),
                'lot_number': lot_number
            }
        }
    }


def parse_btf_1177(path):
    """
    Função de processamento de logs BTF 1177.

    Analisa ficheiro JSON da BTF 1177 para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    with open(path, 'r') as file:
        data = json.load(file)

    status = 'OK' if data['result'].lower() == 'ok' else 'NG'
    serial_number = data['serial_number']
    serial_number_2 = data['serial_number_2']

    if not serial_number:
        raise ValueError('serial number is empty')

    if not serial_number_2:
        raise ValueError('serial_number_2 is empty')

    return {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S"),
                'serial_no_2': serial_number_2
            }
        }
    }


def parse_btf14(path):
    """
    Função de processamento de logs BTF14.

    Analisa ficheiro XML da BTF14 para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    tree = ET.parse(path)
    root = tree.getroot()

    serial_no = root.find('serialnumber').text

    if not serial_no:
        raise ValueError('serial number is empty')

    date = datetime.strptime(root.find('date').text, '%d%m%Y_%H%M%S')

    endtime = datetime.strptime(root.find('endtime').text, '%H:%M:%S')

    timestamp = date.replace(
        hour=endtime.hour,
        minute=endtime.minute,
        second=endtime.second
    )

    status = 'OK' if root.find('result').text.lower() == 'passed' else 'NG'

    tplaca = root.find('TPLACA').text
    fwversion = root.find('FWVersion').text

    return {
        'serial_numbers': {
            serial_no: {
                'status': status,
                'timestamp': timestamp,
                'tplaca': tplaca,
                'fwversion': fwversion
            }
        }
    }


def parse_bt81(path):
    """
    Função de processamento de logs da BT81.

    Analisa ficheiro TXT da BT81 para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    tree = ET.parse(path)
    root = tree.getroot()

    timestamp = datetime.strptime(root.find('endtime').text, '%Y%m%d%H%M%S')
    status = 'OK' if root.find('result').text.lower() == 'passed' else 'NG'
    serial_number = root.find('serial_number').text

    if not serial_number:
        raise ValueError('serial number is empty')

    # try to collect serial_no_2 (only for bt81 logs) wich has the name of serial_number_gbt
    try:
        serial_no_2 = root.find('serial_number_gbt').text
        # adds static digits to start of serial_no_2
        if serial_no_2:
            serial_no_2 = '020215102523' + serial_no_2
        # raises error if log has serial_no_2 attr but it is empty
        if status == 'OK' and not serial_no_2:
            raise ValueError('serial number gbt is empty')
    except AttributeError:
        serial_no_2 = None

    return_dict = {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }

    if serial_no_2:
        return_dict['serial_numbers'][serial_number]['serial_no_2'] = serial_no_2

    return return_dict


def parse_mil07(path):
    """
    Função de processamento de logs da MIL07.

    Analisa ficheiro TXT da MIL07 para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    tree = ET.parse(path)
    root = tree.getroot()

    timestamp = datetime.strptime(root.find('date').text, '%Y%m%d%H%M%S')
    status = 'OK' if root.find('result').text.lower() == 'passed' else 'NG'
    serial_number = root.find('serial_number').text

    if not serial_number:
        raise ValueError('serial number is empty')

    return_dict = {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }

    return return_dict


def parse_dboard_r5(path):
    """
    Função de processamentos de logs dos testes da "DBOARD R5 FT30 Tester".

    Analisa ficheiro XML para extrair números de série, estados, data
    de teste.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados, data
        de processamento.
    :rtype: dict
    """
    tree = ET.parse(path)
    root = tree.getroot()

    timestamp = datetime.strptime(root.find('endtime').text, '%d-%m-%Y %H:%M:%S')
    status = 'OK' if root.find('result').text.lower() == 'pass' else 'NG'
    serial_no = root.find('serial_number').text

    if not serial_no:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            serial_no: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }


def parse_lvs(path):
    with open(path, 'r') as file:
        first_line = file.readline().rstrip('\n')

    splitted = first_line.split(';')

    if not splitted[1][4:] or not splitted[2] or not splitted[3]:
        raise ValueError('serial number is empty')

    serial_no = splitted[1][4:] + 'R' + splitted[2] + splitted[3]

    timestamp = datetime.strptime(splitted[4] + splitted[5], '%d/%m/%Y%H:%M:%S')
    status = 'OK' if splitted[0].lower() == 'passed' else 'NOK'

    return {
        'serial_numbers': {
            serial_no: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }


def parse_starktest_pc2(path):
    """
    Função de processamento de logs StarkTest PC2.

    Analisa ficheiro JSON do StarkTest PC2 para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    with open(path, 'r') as file:
        data = json.load(file)

    status = 'OK' if data['testResult'].lower() == 'passed' else 'NG'
    serial_number = data['serialNumber']

    if not serial_number:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': datetime.fromisoformat(data['date'])
            }
        }
    }


def parse_automatic_label_check_01(path):
    """
    Função de processamentos de logs dos testes da "AUTOMATIC_LABEL_CHECK_01".

    Analisa ficheiro XML para extrair números de série, estados, data
    de teste.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados, data
        de processamento.
    :rtype: dict
    """
    tree = ET.parse(path)
    root = tree.getroot()

    timestamp = datetime.strptime(root.find('endtime').text, '%d-%m-%Y %H:%M:%S')
    status = 'OK' if root.find('result').text.lower() == 'pass' else 'NG'
    serial_no = root.find('serial_number').text

    if not serial_no:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            serial_no: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }


def parse_altra_air_lateral_uar260441(path):
    """
    Função de processamento de logs ALTRA air lateral UAR260441.

    Analisa ficheiro XML da ALTRA air lateral UAR260441 para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    tree = ET.parse(path)
    root = tree.getroot()

    serial_no = root.find('serialnumber').text

    if not serial_no:
        raise ValueError('serial number is empty')

    date = datetime.strptime(root.find('date').text, '%d%m%Y_%H%M%S')

    endtime = datetime.strptime(root.find('endtime').text, '%H:%M:%S')

    timestamp = date.replace(
        hour=endtime.hour,
        minute=endtime.minute,
        second=endtime.second
    )

    status = 'OK' if root.find('result').text.lower() == 'passed' else 'NG'

    return {
        'serial_numbers': {
            serial_no: {
                'status': status,
                'timestamp': timestamp
            }
        }
    }


def parse_btf06(path):
    """
    Função de processamento de logs BTF06.

    Analisa ficheiro JSON da BTF BTF06 para extrair números de série, estados e data
    de processamento.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str
    :return: Dicionário que contém lista de números de série, estados e data
        de processamento.
    :rtype: dict
    """
    with open(path, 'r') as file:
        data = json.load(file)

    status = 'OK' if data['ResultadoFinal'].lower() == 'pass' else 'NG'
    serial_number = data['CodUnico']

    if not serial_number:
        raise ValueError('serial number is empty')

    return {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': datetime.strptime(data['task_ended_at'], "%d-%m-%Y %H:%M:%S")
            }
        }
    }

def parse_leak_test_1(path):
    """
    Função de processamento de logs de teste de fugas (IGBT Leak Test 1).

    Analisa ficheiro CSV com resultados de Leak1, extrai número de série,
    estado e timestamp. O timestamp é fornecido em UTC e convertido para hora local.

    Apenas leak1 deve ser considerado na avaliação do estado.
    Se leak1 ≤ 9 → OK, caso contrário → NG.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :raises: ValueError: Caso o número de série seja nulo.

    :return: Dicionário com números de série, estados e timestamps.
    :rtype: dict
    """
    serial_numbers = {}

    with open(path, 'r') as csv_file:
        for i, row in enumerate(csv_file):
            if i == 0:
                continue # cabeçalho

            cols = [c.strip().strip('"') for c in row.rstrip('\n').split(',')]
            if len(cols) < 6 or not cols[1]:
                continue

            serial_number = cols[3]
            if not serial_number:
                raise ValueError('serial number is empty')

            timestamp_utc = datetime.strptime(
                f'{cols[1]} {cols[2]}', '%Y-%m-%d %H:%M:%S'
            ).replace(tzinfo=timezone.utc)

            timestamp_local = timestamp_utc.astimezone()

            status = 'OK' if int(cols[4]) <= 9 else 'NG'

            serial_numbers[serial_number] = {
                'status': status,
                'timestamp': timestamp_local,
            }

    if not serial_numbers:
        raise ValueError('log file contains no measurements')

    return {'serial_numbers': serial_numbers}


def parse_leak_test_2(path):
    """
    Função de processamento de logs de teste de fugas (IGBT Leak Test 2).

    Analisa ficheiro CSV com resultados de Leak2, extrai número de série,
    estado e timestamp. O timestamp é fornecido em UTC e convertido para hora local.

    Apenas leak2 deve ser considerado na avaliação do estado.
    Se leak2 ≤ 9 → OK, caso contrário → NG.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str

    :raises: ValueError: Caso o número de série seja nulo.

    :return: Dicionário com números de série, estados e timestamps.
    :rtype: dict
    """
    serial_numbers = {}

    with open(path, 'r') as csv_file:
        for i, row in enumerate(csv_file):
            if i == 0:
                continue # cabeçalho

            cols = [c.strip().strip('"') for c in row.rstrip('\n').split(',')]
            if len(cols) < 6 or not cols[1]:
                continue

            serial_number = cols[3]
            if not serial_number:
                raise ValueError('serial number is empty')

            timestamp_utc = datetime.strptime(
                f'{cols[1]} {cols[2]}', '%Y-%m-%d %H:%M:%S'
            ).replace(tzinfo=timezone.utc)

            timestamp_local = timestamp_utc.astimezone()

            status = 'OK' if int(cols[5]) <= 9 else 'NG'

            serial_numbers[serial_number] = {
                'status': status,
                'timestamp': timestamp_local,
            }

    if not serial_numbers:
        raise ValueError('log file contains no measurements')

    return {'serial_numbers': serial_numbers}

def parse_sram_mainboard_11(path):
    """
    Analisa ficheiro CSV com resultados da SRAM MAINBOARD 11.

    Extrai o número de série, data e hora de início a partir do cabeçalho fixo,
    e localiza dinamicamente a linha do 'FinalResult' para definir o estado.
    Se o resultado for PASS → OK, caso contrário → NG.

    :param path: Endereço absoluto do ficheiro a ser processado.
    :type path: str
    :raises ValueError: Caso o número de série seja nulo.
    :return: Dicionário com números de série, estados e timestamps.
    :rtype: dict
    """
    test_date = None
    test_time = None
    serial_number = None
    status = 'NG'

    with open(path, 'r', encoding='utf-8') as csv_file:
        for i, row in enumerate(csv_file, start=1):
            cols = [c.strip().strip('"') for c in row.rstrip('\n').split(',')]
            if not cols or len(cols) < 2:
                continue

            # Metadados do cabeçalho (linhas fixas)
            if i == 4:
                test_date = cols[1]
            elif i == 6:
                test_time = cols[1]
            elif i == 9:
                serial_number = cols[1]

            # Localização dinâmica do resultado final
            if cols[1] == 'FinalResult':
                if len(cols) >= 8 and cols[7] == 'PASS':
                    status = 'OK'
                else:
                    status = 'NG'

                # Garante que já passámos o cabeçalho antes de interromper o loop
                if i > 9:
                    break

    if not serial_number:
        raise ValueError('serial number is empty')

    if test_date and test_time:
        # Formato da data no ficheiro: DD/MM/YYYY hh:mm:ss
        timestamp_utc = datetime.strptime(
            f'{test_date} {test_time}', '%d/%m/%Y %H:%M:%S'
        ).replace(tzinfo=timezone.utc)
        timestamp_local = timestamp_utc.astimezone()
    else:
        timestamp_local = datetime.now().astimezone()

    return {
        'serial_numbers': {
            serial_number: {
                'status': status,
                'timestamp': timestamp_local
            }
        }
    }