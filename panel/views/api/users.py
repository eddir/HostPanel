from django.contrib.auth import get_user_model
from rest_framework.views import APIView

from panel.utils import api_response


class UsersView(APIView):

    @staticmethod
    def get(request):
        """Список текущих пользователей"""
        users = []

        for user in get_user_model().objects.all():
            users.append({
                "username": user.username,
                "name": user.first_name + " " + user.last_name,
                "email": user.email,
                # todo: группа (роль) пользователя - owner, admin
            })

        return api_response(users)
