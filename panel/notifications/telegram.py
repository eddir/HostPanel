import urllib.parse

import requests
from requests import RequestException

from HostPanel.settings import TELEGRAM_TOKEN
from panel.models import Subscriber


def send_telegram_alert(message):
    for sub in Subscriber.objects.all():
        try:
            requests.get('https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&parse_mode=Markdown&text={2}'.format(
                TELEGRAM_TOKEN,
                sub.telegram_id,
                urllib.parse.quote(message, safe="")
            ))
        except RequestException as e:
            print(str(e))
