from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from authentication.views import telegram_login, token_refresh

urlpatterns = [
    path("telegram/login/", telegram_login, name="telegram_login"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/refresh/', token_refresh, name='token_refresh'),
]
