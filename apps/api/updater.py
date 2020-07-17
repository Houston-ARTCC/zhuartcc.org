import calendar
import pytz
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from django.core.mail import send_mail
from django.db.models import Sum, Q
from django.template.loader import render_to_string
from django.utils import timezone

from .views import return_inactive_users
from .models import Controller, ControllerSession
from ..user.models import User
from zhuartcc import settings


def update_scheduler():
    pull_controllers()
    scheduler = BackgroundScheduler()
    scheduler.add_job(pull_controllers, 'interval', minutes=1)
    scheduler.add_job(warn_inactive_users, 'cron', day=23)
    scheduler.start()


def pull_controllers():
    data = requests.get('http://us.data.vatsim.net/vatsim-data.txt').text
    data_array = [line.split(':') for line in data.split('\n')]
    atc_clients = {client[0]: client for client in data_array if len(client) == 42 and client[3] == 'ATC'}

    for controller in Controller.objects.all():
        if controller.callsign in atc_clients:
            controller.last_update = timezone.now()
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
                            online_since=pytz.utc.localize(datetime.strptime(controller[36], '%Y%m%d%H%M%S')),
                            last_update=timezone.now(),
                        ).save()


def warn_inactive_users():
    for aggregate in return_inactive_users():
        context = {
            'user': aggregate['user_obj'],
            'hours': round(aggregate['current'].total_seconds() / 3600, 1),
            'deadline': f'{calendar.month_name[timezone.now().month + 1]} 5'
        }
        send_mail(
            'Controller Activity Warning',
            render_to_string('emails/activity_warning.txt', context),
            'no-reply@zhuartcc.org',
            [aggregate['user_obj'].email],
            html_message=render_to_string('emails/activity_warning.html', context),
        )
