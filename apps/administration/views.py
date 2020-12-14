import os
import requests
import timezone

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from zhuartcc.overrides import send_mass_mail
from zhuartcc.decorators import require_staff, require_staff_or_mentor
from .models import ActionLog, Announcement
from ..feedback.models import Feedback
from ..training.models import TrainingRequest
from ..user.models import User
from ..visit.models import Visit


@require_staff_or_mentor
def view_admin_panel(request):
    return render(request, 'admin_panel.html', {
        'page_title': 'Admin Panel',
        'controllers': User.objects.all().order_by('first_name'),
        'notifications': {
            'visit': Visit.objects.count(),
            'training': TrainingRequest.objects.filter(end__gt=timezone.now()).count(),
            'feedback': Feedback.objects.filter(approved=False).count(),
        }
    })


@require_staff
def view_action_log(request):
    return render(request, 'action_log.html', {
        'page_title': 'Action Log',
        'actions': ActionLog.objects.all(),
    })


@require_staff
def view_transfers(request):
    transfers = requests.get(
        f'https://api.vatusa.net/v2/facility/{os.getenv("ARTCC_ICAO")}/transfers',
        params={'apikey': os.getenv('API_KEY')},
    ).json()

    return render(request, 'transfers.html', {
        'page_title': 'Transfer Requests',
        'transfers': transfers['transfers'],
    })


@require_staff
def view_announcement(request):
    if request.method == 'POST':
        announcement = Announcement(
            author=request.user_obj,
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        announcement.save()

        ActionLog(action=f'User {request.user_obj} created announcement "{announcement.subject}".').save()

        return redirect(reverse('home'))

    return render(request, 'announcement.html', {'page_title': 'Announcement'})


@require_staff
def view_broadcast(request):
    if request.method == 'POST':
        recipients = User.objects.filter(rating__in=request.POST)

        if request.POST.get('main_role') != 'AC':
            recipients = recipients.filter(main_role=request.POST.get('main_role'))

        context = {
            'message': request.POST.get('message'),
            'sender': request.user_obj
        }
        send_mass_mail(
            (
                (
                    request.POST.get('subject'),
                    render_to_string('emails/broadcast.html', context),
                    os.getenv('NO_REPLY'),
                    [recipient.email],
                ) for recipient in recipients
            ), fail_silently=False
        )

        ActionLog(action=f'User {request.user_obj} sent broadcast "{request.POST.get("subject")}".').save()

        return HttpResponse(status=200)

    return render(request, 'broadcast.html', {'page_title': 'Broadcast'})
