from datetime import datetime

import os
import shutil


def format_evaluation_data(data):
    for _, details in data['serial_numbers'].items():
        if 'timestamp' in details.keys():
            details['evaluated_at'] = details.pop('timestamp').isoformat()

    return data

def format_evaluation_data_create_evaluation_v1_url(data):
    new_data = dict()

    new_data['unit'] = list(data['serial_numbers'].keys())[0]
    new_data['status'] = data['serial_numbers'][new_data['unit']]['status']
    new_data['evaluated_at'] = data['serial_numbers'][new_data['unit']]['timestamp'].isoformat()
    new_data['serial_no_2'] = data['serial_numbers'][new_data['unit']]['serial_no_2']
    new_data['line'] = data['line']
    new_data['workstation'] = data['workstation']
    new_data['attributes'] = data['attributes']

    return new_data

def move_logfile(origin, destination, status):
    if status == 'success':
        subfolder = os.path.join(destination, "processed", "OK")
    else:
        subfolder = os.path.join(destination, "processed", "NOK")

    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    new_path = os.path.join(subfolder, os.path.basename(origin))

    shutil.move(origin, new_path)

    return new_path


def parse_timestamp(timestamp):
    try:
        return datetime.strptime(timestamp, '%d/%m/%Y%H:%M:%S')
    except (ValueError, TypeError):
        try:
            return datetime.strptime(timestamp, '%Y-%m-%d%H:%M:%S')
        except (ValueError, TypeError):
            message = '"timestamp" must be a valid string in ISO-8601 format.'
            raise ValueError(message)
