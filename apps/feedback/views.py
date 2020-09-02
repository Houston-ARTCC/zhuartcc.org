from datetime import datetime, timedelta

import pytz
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Feedback
from ..event.models import Event
from ..user.models import User


def view_all_feedback(request):
    return render(request, 'all_feedback.html', {
        'page_title': 'Feedback',
        'all_feedback': Feedback.objects.all(),
    })


def add_feedback(request):
    if request.method == 'POST':
        Feedback(
            controller=User.objects.get(cid=request.POST['controller']),
            controller_callsign=request.POST['controller_callsign'],
            rating=int(request.POST['rating']),
            pilot_name=request.POST.get('pilot_name', None),
            pilot_email=request.POST.get('pilot_email', None),
            event=Event.objects.get(id=request.POST['event']) if 'event' in request.POST else None,
            flight_callsign=request.POST.get('flight_callsign', None),
            comments=request.POST['comments'],
        ).save()

        return redirect('/feedback')
    else:
        return render(request, 'add_feedback.html', {
            'page_title': 'Submit Feedback',
            'controllers': User.objects.filter(status=0),
            'events': Event.objects.filter(start__gte=timezone.now() - timedelta(days=30)),
        })
