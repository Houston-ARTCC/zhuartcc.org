import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from zhuartcc.overrides import send_mass_html_mail
from .models import ActionLog
from ..user.models import User
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
    return render(request, 'transfers.html', {'page_title': 'Transfer Requests', 'transfers': transfers})


@require_staff
def view_broadcast(request):
    return render(request, 'broadcast.html', {'page_title': 'Broadcast'})


@require_staff
@require_POST
def send_broadcast(request):
    try:
        admin = User.objects.get(cid=request.session['cid'])
        recipients = User.objects.filter(rating__in=request.POST)

        if request.POST['main_role'] != 'AC':
            recipients = recipients.filter(main_role=request.POST['main_role'])

        mail_tuple = (
            (
                request.POST['subject'],
                render_to_string('emails/broadcast.txt', {
                    'user': recipient,
                    'message': request.POST['message'],
                    'sender': admin.full_name
                }),
                render_to_string('emails/broadcast.html', {
                    'user': recipient,
                    'message': request.POST['message'],
                    'sender': admin.full_name
                }),
                'no-reply@zhuartcc.org',
                [recipient.email],
            ) for recipient in recipients
        )
        send_mass_html_mail(mail_tuple)

        ActionLog(action=f'User {admin.full_name} sent broadcast "{request.post["subject"]}".').save()

        return HttpResponse(status=200)
    except:
        return HttpResponse('Something was wrong your request!', status=400)