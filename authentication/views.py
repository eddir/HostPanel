import hashlib
import hmac
import time
from pprint import pprint

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)

from allauth.socialaccount.providers.telegram.provider import TelegramProvider
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


@csrf_exempt
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def telegram_login(request):
    provider = providers.registry.by_id(TelegramProvider.id, request)
    data = dict(request.data.items())
    hashcode = data.pop("hash")
    payload = "\n".join(sorted(["{}={}".format(k, v) for k, v in data.items()]))
    token = provider.get_settings()["TOKEN"]
    token_sha256 = hashlib.sha256(token.encode()).digest()
    expected_hash = hmac.new(token_sha256, payload.encode(), hashlib.sha256).hexdigest()
    auth_date = int(data.pop("auth_date"))

    if hashcode != expected_hash or time.time() - auth_date > 30:
        return Response({"error": "Хэш не совпал"})

    social_login = provider.sociallogin_from_response(request, data)
    complete_social_login(request, social_login)
    return login(request)


def login(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    res = Response(
        {
            "success": "Авторизация пройдена.",
            "data": {
                "csrf": str(csrf(request)['csrf_token']),
                "jwt": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                }
            }

        }
    )

    res.set_cookie(
        "JWT",
        str(refresh.access_token),
        max_age=3600*24*14,
        httponly=True,
        samesite="None",
        secure=True
    )

    return res
