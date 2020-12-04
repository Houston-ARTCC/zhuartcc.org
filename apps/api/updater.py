import os
import ast
import pytz
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from django.template.loader import render_to_string
from django.utils import timezone

from zhuartcc.overrides import send_mail
from .views import return_inactive_users
from .models import Controller, CurrentAtis
from ..user.models import User


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(pull_controllers, 'interval', minutes=1)
    scheduler.add_job(warn_inactive_users, 'cron', day=23)
    scheduler.start()


def pull_controllers():
    airports = ast.literal_eval(os.getenv('AIRPORT_IATA'))
    data = requests.get('http://us.data.vatsim.net/vatsim-data.txt').text
    data_array = [line.split(':') for line in data.split('\n')]
    atc_clients = {client[0]: client for client in data_array if len(client) == 42 and client[3] == 'ATC'}

    for controller in Controller.objects.all():
        if controller.callsign in atc_clients:
            controller.last_update = timezone.now()
            controller.save()
        else:
            controller.convert_to_session()
            controller.delete()

    for atis in CurrentAtis.objects.all():
        if atis.facility + '_ATIS' not in atc_clients:
            atis.delete()

    for callsign, controller in atc_clients.items():
        if controller[1] and User.objects.filter(cid=controller[1]).exists():
            split = callsign.split('_')
            if split[0] in airports:
                if split[-1] != 'ATIS' and split[-1] != 'OBS' and split[-1] != 'SUP':
                    if not Controller.objects.filter(callsign=callsign).exists():
                        Controller(
                            user=User.objects.get(cid=int(controller[1])),
                            callsign=callsign,
                            frequency=controller[4],
                            online_since=pytz.utc.localize(datetime.strptime(controller[36], '%Y%m%d%H%M%S')),
                            last_update=timezone.now(),
                        ).save()


def warn_inactive_users():
    for aggregate in return_inactive_users():
        context = {
            'user': aggregate['user_obj'],
            'hours': round(aggregate['hours']['current'].total_seconds() / 3600, 1),
        }
        send_mail(
            'Controller Activity Warning',
            render_to_string('emails/activity_warning.html', context),
            os.getenv('NO_REPLY'),
            [aggregate['user_obj'].email],
            fail_silently=True,
        )
