class ServerAuthenticationFailed(Exception):
    """
    Создаётся при неудачной попытке авторизоваться на VPS,
    используя предоставленные данные для входа.
    """
    pass


class ServerBadCommand(Exception):
    """
    Вывзывается при возникновении ошибок во время выполнения
    команды на VPS.
    """
    pass
