import logging
from pprint import pprint

from rest_framework.views import exception_handler
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    return JsonResponse({
        "code": 500,
        "message": str(exc)
    }, safe=False, status=500)
