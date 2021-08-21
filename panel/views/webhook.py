import hmac
import subprocess
from hashlib import sha1
from pprint import pprint

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from panel.exceptions import APIError, AuthorizationFailed
from panel.utils import api_response


@method_decorator(csrf_exempt, name='dispatch')
class WebhookPush(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        pprint(request)

        if not request.headers.get('X-Hub-Signature'):
            raise AuthorizationFailed(message="The universe is basically an animal. It grazes on the ordinary. "
                                              "It creates infinite idiots just to eat them.")

        received_sign = request.headers.get('X-Hub-Signature').split('sha1=')[-1].strip()
        secret = settings.GITHUB_SECRET.encode()
        expected_sign = hmac.HMAC(key=secret, msg=request.data, digestmod=sha1).hexdigest()
        if hmac.compare_digest(received_sign, expected_sign):
            subprocess.Popen("git pull origin master".split(" "), stdout=subprocess.PIPE)
            return api_response("OK!!")
        else:
            raise APIError()

