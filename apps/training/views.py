from datetime import datetime

import pytz
from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.shortcuts import render, redirect

from zhuartcc.decorators import require_member
from .models import TrainingSession, TrainingRequest
from ..event.models import Event
from ..user.models import User


@require_member
def view_training_center(request):
    user = User.objects.get(cid=request.session['cid'])
    sessions = TrainingSession.objects.filter(student=user)
    statistics = {
        'training_time': sessions.filter(status=1).aggregate(Sum('duration'))['duration__sum'],
    }
    return render(request, 'training_center.html', {
        'page_title': 'Training Center',
        'user': user,
        'statistics': statistics,
        'sessions': sessions,
    })


@require_member
def view_session(request, id):
    session = TrainingSession.objects.get(id=id)
    if (
            request.session['cid'] == session.student.cid
            or request.session['mentor'] or request.session['staff']
    ):
        return render(request, 'session.html', {'session': session})
    else:
        return HttpResponse('You are unauthorized to view somebody else\'s training session!', status=401)


@require_member
def request_training(request):
    if request.method == 'POST':
        TrainingRequest(
            student=User.objects.get(cid=request.session['cid']),
            start=pytz.utc.localize(datetime.fromisoformat(request.POST['start'])),
            end=pytz.utc.localize(datetime.fromisoformat(request.POST['end'])),
            type=request.POST['type'],
            level=request.POST['level'],
            remarks=request.POST.get('remarks', None)
        ).save()

        return redirect(f'/training/')
    else:
        return render(request, 'request_training.html', {
            'page_title': 'Request Training',
            'events': Event.objects.all(),
            'sessions': TrainingSession.objects.all(),
            'types': TrainingRequest._meta.get_field('type').choices,
            'levels': TrainingRequest._meta.get_field('level').choices,
        })
