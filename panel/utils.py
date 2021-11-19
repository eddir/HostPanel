import re
import traceback
from pprint import pprint

from django.http import JsonResponse
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed, TokenError

from HostPanel.settings import BASE_DIR
from panel.exceptions import UndefinedCaretakerVersion, AUTH_FAILED, UNEXPECTED_ERROR, APIError, AuthorizationFailed, \
    RESPONSE_OK


def api_response(response):
    return JsonResponse({
        "code": RESPONSE_OK,
        "response": response
    })


def custom_exception_handler(exc, context):

    http_code = HTTP_500_INTERNAL_SERVER_ERROR
    api_code = UNEXPECTED_ERROR

    if isinstance(exc, (AuthorizationFailed, AuthenticationFailed, TokenError, NotAuthenticated, APIError)):
        http_code = HTTP_200_OK

    if http_code == HTTP_500_INTERNAL_SERVER_ERROR:
        pprint(''.join(traceback.format_tb(exc.__traceback__)))
        pprint(exc)

    if isinstance(exc, APIError):
        message = exc.message
        api_code = exc.code
    elif isinstance(exc, (InvalidToken, TokenError, NotAuthenticated)):
        message = "Authorization failed"
        api_code = AUTH_FAILED
    elif isinstance(exc, ValidationError):
        message = exc.detail
    else:
        message = [str(exc)]

    return JsonResponse({
        "code": api_code,
        "response": message
    }, safe=False, status=http_code)


def get_caretaker_version():
    try:
        with open(str(BASE_DIR) + "/watchdog/client.py", 'r') as infile:
            file = infile.read()
            version = re.search(r'VERSION = \"(.*)\"(.*)', file).group(1)
            return version

    except (AttributeError, Exception):
        raise UndefinedCaretakerVersion("Не удлаось проверить версию Caretaker. Проверьте всё ли на месте.")
