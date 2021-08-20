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
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from panel.exceptions import AUTH_FAILED


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


@csrf_exempt
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def token_refresh(request):
    print("token refresh")
    serializer = TokenRefreshSerializer(data={"refresh": request.COOKIES["JWT-REFRESH"]})

    try:
        serializer.is_valid(raise_exception=True)
    except TokenError:
        return Response({
            "code": AUTH_FAILED,
            "message": "Authorization failed"
        }, status=status.HTTP_401_UNAUTHORIZED)

    res = Response({
        "success": "Авторизация пройдена.",
        "data": {
            "csrf": str(csrf(request)['csrf_token'])
        }
    })

    res.set_cookie("JWT", str(serializer.validated_data['access']), max_age=3600 * 24 * 14, httponly=True,
                   samesite="None", secure=True)
    res.set_cookie("JWT-REFRESH", str(serializer.validated_data['refresh']), max_age=3600 * 24 * 14, httponly=True,
                   samesite="None", secure=True, path="/auth")

    return res


def login(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    res = Response(
        {
            "success": "Авторизация пройдена.",
            "data": {
                "csrf": str(csrf(request)['csrf_token'])
            }

        }
    )

    res.set_cookie("JWT", str(refresh.access_token), max_age=3600 * 24 * 14, httponly=True, samesite="None",
                   secure=True)
    res.set_cookie("JWT-REFRESH", str(refresh), max_age=3600 * 24 * 14, httponly=True, samesite="None", secure=True,
                   path="/auth")
    return res
