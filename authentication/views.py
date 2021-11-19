import hashlib
import hmac
import time

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
)
from allauth.socialaccount.providers.telegram.provider import TelegramProvider
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from panel.exceptions import AUTH_FAILED, APIError, RESPONSE_OK, AUTH_WRONG_REFRESH_TOKEN


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
        raise APIError(AUTH_FAILED, "Хэш не совпал")

    social_login = provider.sociallogin_from_response(request, data)
    complete_social_login(request, social_login)
    return login(request)


@csrf_exempt
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def token_refresh(request):
    if "JWT-REFRESH" not in request.COOKIES:
        raise APIError(AUTH_WRONG_REFRESH_TOKEN, "Токен просрочен")

    serializer = TokenRefreshSerializer(data={"refresh": request.COOKIES["JWT-REFRESH"]})
    serializer.is_valid(raise_exception=True)
    return jwt(request, serializer.validated_data['access'], serializer.validated_data['refresh'])


def login(request):
    token = RefreshToken.for_user(request.user)
    return jwt(request, token.access_token, token)


def jwt(request, access_token, refresh_token):
    response = Response(
        {
            "code": RESPONSE_OK,
            "response": {
                "message": "Авторизация пройдена.",
                "csrf": str(csrf(request)['csrf_token'])
            }
        }
    )

    response.set_cookie("JWT", str(access_token), max_age=3600 * 24 * 14, httponly=True, samesite="None",
                        secure=True)
    response.set_cookie("JWT-REFRESH", str(refresh_token), max_age=3600 * 24 * 14, httponly=True, samesite="None",
                        secure=True, path="/auth")
    return response
