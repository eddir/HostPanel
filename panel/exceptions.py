# Успешный запрос
RESPONSE_OK = 0
# Что-то пошло не так
UNEXPECTED_ERROR = 1
# возникает в том случае, если пользователь не предоставил токен авторизации
UNAUTHORIZED_ERROR = 2
# сообщает о проблемах с предоставленным токеном авторизации. Токен устарел, либо недействительный.
AUTH_FAILED = 100
AUTH_WRONG_REFRESH_TOKEN = 101

class APIError(Exception):
    """
    Ошибка API.
    """
    code = UNEXPECTED_ERROR
    message = None

    def __init__(self, code=None, message=None):
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message


class AuthorizationFailed(APIError):
    """
    Ошибки при авторизации. Её отсутствие, либо неудачная попытка авторизоваться.
    """
    code = UNAUTHORIZED_ERROR


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


class UndefinedCaretakerVersion(Exception):
    """
    Вывзывается при ошибке во время распознавания версии
    скрипта Watchdog.
    """
    pass
