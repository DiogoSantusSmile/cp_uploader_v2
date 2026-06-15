from datetime import datetime
from urllib.parse import quote

import json
import requests

from .constants import LOGIN_URL
from logger_config import setup_logger

logger = setup_logger('network')


class Network:
    def __init__(self, url, basic_authentication=None):
        self.__url = url
        self.__basic_authentication = basic_authentication

    def __send_request(self, url, data=None, method='GET', on_progress=None):
        # Garante o uso dos method
        if method not in ['GET', 'POST']:
            raise ValueError(f"HTTP method '{method}' is not supported. Use 'GET' or 'POST'.")

        request_kwargs = {'url': url, 'method': method.upper()}

        # Adiciona dados do POST se aplicável
        if method == 'POST':
            request_kwargs.update({
                'headers': {'Content-Type': 'application/json'},
                'data': data
            })

            if on_progress:
                on_progress(10)

        # Adiciona autenticação se fornecida
        if self.__basic_authentication is not None:
            request_kwargs['auth'] = self.__basic_authentication

        # Envia pedido http
        try:
            logger.info(f'Sending {method} request to {url}'.format(
                method=request_kwargs['method'],
                url=request_kwargs['url']
            ))

            if on_progress:
                on_progress(33)

            response = requests.request(**request_kwargs)

            if on_progress:
                on_progress(66)

            logger.info(f'Server responded with a {response.status_code} status code.')

            if response.status_code == 200 or response.status_code == 201:
                if on_progress:
                    on_progress(100)

                return {
                    'status': 'success',
                    'status_code': response.status_code,
                    'data': response.json(),
                }
            else:
                try:
                    data = json.loads(response.content)
                except json.JSONDecodeError:
                    data = None
                msg = f'Server responded with a {response.status_code} status code.'
                logger.info(f'{msg}: {data}')

                if on_progress:
                    on_progress(100)

                return {
                    'status': 'error',
                    'status_code': response.status_code,
                    'message': msg,
                    'data': data,
                }
        except Exception as e:
            if on_progress:
                on_progress(100)

            logger.exception(e)
            return {
                'status': 'error',
                'message': str(e),
            }

    def get_data(self, path, query: dict = None, **kwargs):
        query_items = []
        query_string = ''

        if query is not None:
            for key, value in query.items():
                if isinstance(value, datetime):
                    formatted_value = quote(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    formatted_value = value

                query_items.append('{key}={value}'.format(key=key, value=formatted_value))

            if query_items:
                query_string = '&'.join(query_items)

        full_url = self.__url + path + ('?' + query_string if query is not None else '')

        response = self.__send_request(full_url, **kwargs)

        if response['status'] == 'success':
            next_url = response['data'].get('next')

            if next_url:
                response = self.__get_all_pages_data(response=response)

        return response

    def __get_all_pages_data(self, **kwargs):
        response = kwargs.pop('response')

        items_list = []
        next_page = response['data']['next']

        # save first page items
        for item in response['data']['results']:
            items_list.append(item)

        while next_page:
            # send request
            url = next_page
            response = self.__send_request(url)

            for item in response['data']['results']:
                items_list.append(item)

            # get next page if exists
            try:
                next_page = response['data']['next']
            except TypeError:
                next_page = None

        return {
            "status": "success",
            "data": {
                "results": items_list
            }
        }

    def post_data(self, path, data, **kwargs):
        full_url = self.__url + path

        return self.__send_request(full_url, json.dumps(data), method='POST', **kwargs)

    def check_credentials(self, credentials, **kwargs):
        self.__basic_authentication = credentials

        return self.get_data(LOGIN_URL, **kwargs)
