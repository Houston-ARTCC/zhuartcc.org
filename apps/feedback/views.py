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
        post = request.POST
        Feedback(
            controller=User.objects.get(cid=post['controller']),
            controller_callsign=post['controller_callsign'],
            rating=int(post['rating']),
            pilot_name=post['pilot_name'] if 'pilot_name' in post else None,
            pilot_email=post['pilot_email'] if 'pilot_email' in post else None,
            event=Event.objects.get(id=post['event']) if 'event' in post else None,
            flight_callsign=post['flight_callsign'] if 'flight_callsign' in post else None,
            comments=post['comments'],
        ).save()

        return redirect('/feedback')
    else:
        return render(request, 'add_feedback.html', {
            'page_title': 'Submit Feedback',
            'controllers': User.objects.filter(status=0),
            'events': Event.objects.filter(start__gte=timezone.now() - timedelta(days=30)),
        })
