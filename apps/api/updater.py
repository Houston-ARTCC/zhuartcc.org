from datetime import datetime

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from zhuartcc import settings
from ..api.models import Controller, ControllerSession
from ..user.models import User


def update_scheduler():
    pull_controllers()
    scheduler = BackgroundScheduler()
    scheduler.add_job(pull_controllers, 'interval', minutes=1)
    scheduler.start()


def pull_controllers():
    data = requests.get('http://us.data.vatsim.net/vatsim-data.txt').text
    data_array = [line.split(':') for line in data.split('\n')]
    atc_clients = {client[0]: client for client in data_array if len(client) == 42 and client[3] == 'ATC'}

    for controller in Controller.objects.all():
        if controller.callsign in atc_clients:
            controller.last_update = datetime.now()
            controller.save()
        else:
            ControllerSession(
                user=controller.user,
                callsign=controller.callsign,
                time_logon=controller.online_since,
                duration=controller.last_update - controller.online_since,
            ).save()
            controller.delete()

    for callsign, controller in atc_clients.items():
        if User.objects.filter(cid=controller[1]).exists():
            split = callsign.split('_')
            if split[0] in settings.POSITION_PREFIXES:
                if split[-1] != 'ATIS' and split[-1] != 'OBS' and split[-1] != 'SUP':
                    if not Controller.objects.filter(callsign=callsign).exists():
                        Controller(
                            user=User.objects.get(cid=int(controller[1])),
                            callsign=callsign,
                            frequency=controller[4],
                            online_since=datetime.strptime(controller[36], '%Y%m%d%H%M%S'),
                            last_update=datetime.now(),
                        ).save()
