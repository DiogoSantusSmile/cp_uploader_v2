def not_empty(value: str, field_name: str):
    if value.strip() == '':
        raise ValueError(f'O campo \'{field_name}\' é de preenchimento obrigatório.')


def valid_choice(
        value: str,
        field_name: str,
        choices: list[str]
):
    if value not in choices:
        raise ValueError(f'O campo \'{field_name}\' não contém uma opção válida.')

