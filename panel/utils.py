import re
import traceback
from pprint import pprint

from django.http import JsonResponse
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken

from HostPanel.settings import MEDIA_ROOT
from panel.exceptions import UndefinedCaretakerVersion, AUTH_FAILED, UNEXPECTED_ERROR


def custom_exception_handler(exc, context):
    if isinstance(exc, InvalidToken):
        return JsonResponse({
            "code": AUTH_FAILED,
            "message": "Authorization failed"
        }, status=401)

    pprint(''.join(traceback.format_tb(exc.__traceback__)))
    pprint(exc)

    if isinstance(exc, ValidationError):
        message = exc.detail
    else:
        message = str(exc)

    return JsonResponse({
        "code": UNEXPECTED_ERROR,
        "message": message
    }, safe=False, status=500)


def get_caretaker_version():
    try:
        with open(MEDIA_ROOT + "Caretaker/client.py", 'r') as infile:
            file = infile.read()
            version = re.search(r'VERSION = \"(.*)\"(.*)', file).group(1)
            return version

    except (AttributeError, Exception):
        raise UndefinedCaretakerVersion()
