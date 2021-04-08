import logging
import re
import traceback
from pprint import pprint

from rest_framework.views import exception_handler
from django.http import JsonResponse

from HostPanel.settings import MEDIA_ROOT
from panel.exceptions import UndefinedCaretakerVersion


def custom_exception_handler(exc, context):
    pprint(''.join(traceback.format_tb(exc.__traceback__)))
    pprint(exc)
    return JsonResponse({
        "code": 500,
        "message": str(exc)
    }, safe=False, status=500)


def get_caretaker_version():
    try:
        with open(MEDIA_ROOT + "Caretaker/client.py", 'r') as infile:
            file = infile.read()
            version = re.search(r'VERSION = \"(.*)\"(.*)', file).group(1)
            return version

    except (AttributeError, Exception):
        raise UndefinedCaretakerVersion()
