from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model


class UsersView(APIView):

    @staticmethod
    def get(request):
        users = []

        for user in get_user_model().objects.all():
            users.append({
                "username": user.username,
                "name": user.first_name + " " + user.last_name,
                "email": user.email,
                # todo: группа (роль) пользователя - owner, admin
            })

        return Response({
            "ok": True,
            "response": users
        })