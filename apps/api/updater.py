import calendar
from datetime import datetime

import pytz
from django.core.mail import send_mail
from django.db.models import Sum, Q
from django.template.loader import render_to_string
from django.utils import timezone

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.html import strip_tags

from zhuartcc import settings

from .views import return_hour_aggregate
from ..api.models import Controller, ControllerSession
from ..user.models import User


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


def return_inactive_users():
    inactive_users = []
    for user_status in [return_hour_aggregate(user) for user in User.objects.exclude(main_role='MC')]:
        if 'current_status' in user_status and not user_status['current_status']:
            inactive_users.append(user_status['user_obj'])

    return inactive_users


def warn_inactive_users():
    for user in return_inactive_users():
        session_aggregate = ControllerSession.objects.filter(user=user).aggregate(
            current=Sum('duration', filter=Q(time_logon__month=timezone.now().month))
        )
        context = {
            'user': user,
            'hours': round(session_aggregate['current'].total_seconds() / 3600, 1),
            'deadline': f'{calendar.month_name[timezone.now().month + 1]} 5'
        }
        send_mail(
            'Controller Activity Warning',
            render_to_string('emails/activity_warning.txt', context),
            'no-reply@zhuartcc.org',
            [user.email],
            html_message=render_to_string('emails/activity_warning.html', context),
        )
