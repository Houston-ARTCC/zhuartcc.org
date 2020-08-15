import requests

from django.conf import settings
from django.shortcuts import render

from .models import ActionLog
from zhuartcc.decorators import require_staff


@require_staff
def view_admin_panel(request):
    return render(request, 'admin_panel.html', {'page_title': 'Admin Panel'})


@require_staff
def view_action_log(request):
    return render(request, 'action_log.html', {'page_title': 'Action Log', 'actions': ActionLog.objects.all()})


@require_staff
def view_transfers(request):
    transfers = requests.get(
        'https://api.vatusa.net/v2/facility/ZHU/transfers',
        params={'apikey': settings.API_KEY},
    ).json()['transfers']
    return render(request, 'transfers.html', {'page_title': 'Transfers', 'transfers': transfers})
