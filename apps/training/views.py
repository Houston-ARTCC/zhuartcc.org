from datetime import datetime, timedelta

import pytz
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from zhuartcc.decorators import require_member, require_mentor
from .models import TrainingSession, TrainingRequest
from ..administration.models import ActionLog
from ..event.models import Event
from ..user.models import User


@require_member
def view_training_center(request):
    user = User.objects.get(cid=request.session.get('cid'))
    sessions = user.student_sessions.all()
    return render(request, 'training_center.html', {
        'page_title': 'Training Center',
        'user': user,
        'training_time': sum([session.duration for session in sessions.filter(status=1)], timedelta()),
        'sessions': sessions,
        'requests': user.training_requests.all(),
    })


@require_member
def view_session(request, session_id):
    session = TrainingSession.objects.get(id=session_id)
    if (
            request.session.get('cid') == session.student.cid
            or request.session.get('mentor') or request.session.get('staff')
    ):
        return render(request, 'session.html', {'session': session})
    else:
        return HttpResponse('You are unauthorized to view somebody else\'s training session!', status=401)


@require_member
def request_training(request):
    if request.method == 'POST':
        start = pytz.utc.localize(datetime.fromisoformat(request.POST['start']))
        end = pytz.utc.localize(datetime.fromisoformat(request.POST['end']))
        if start < end:
            TrainingRequest(
                student=User.objects.get(cid=request.session.get('cid')),
                start=pytz.utc.localize(datetime.fromisoformat(request.POST['start'])),
                end=pytz.utc.localize(datetime.fromisoformat(request.POST['end'])),
                type=request.POST['type'],
                level=request.POST['level'],
                remarks=request.POST.get('remarks', None)
            ).save()
        else:
            return HttpResponse('The start time must be before the end time.', status=400)

        return redirect(reverse('training'))
    else:
        return render(request, 'request_training.html', {
            'page_title': 'Request Training',
            'events': Event.objects.all().filter(hidden=False),
            'sessions': TrainingSession.objects.all(),
            'types': TrainingRequest._meta.get_field('type').choices,
            'levels': TrainingRequest._meta.get_field('level').choices,
        })


@require_mentor
def view_mentor_history(request):
    mentors = User.objects.filter(training_role__in=['MTR', 'INS'])
    return render(request, 'mentor_history.html', {
        'page_title': 'Mentor History',
        'mentors': [(
            mentor.full_name,
            mentor.instructor_sessions.filter(start__gte=timezone.now() - timedelta(days=30)).filter(status=1)
        ) for mentor in mentors]
    })


@require_member
def view_training_requests(request):
    if request.session.get('mentor') or request.session.get('staff'):
        return render(request, 'training_requests.html', {
            'page_title': 'Training Requests',
            'requests': TrainingRequest.objects.all().order_by('start'),
        })
    else:
        return HttpResponse(status=403)


@require_POST
@require_mentor
def accept_training_request(request, request_id):
    training_request = TrainingRequest.objects.get(id=request_id)
    admin = User.objects.get(cid=request.session.get('cid'))
    TrainingSession(
        student=training_request.student,
        instructor=admin,
        start=pytz.utc.localize(datetime.strptime(request.POST['start'], '%Y-%m-%dT%H:%M:%S.%f')),
        end=pytz.utc.localize(datetime.strptime(request.POST['end'], '%Y-%m-%dT%H:%M:%S.%f')),
        type=training_request.type,
        level=training_request.level,
    ).save()

    ActionLog(action=f'{admin.full_name} accepted {training_request.student.full_name}\'s training request.').save()
    training_request.delete()

    return redirect(reverse('training_requests'))


@require_POST
@require_mentor
def reject_training_request(request, request_id):
    training_request = TrainingRequest.objects.get(id=request_id)
    admin = User.objects.get(cid=request.session.get('cid'))

    ActionLog(action=f'{admin.full_name} rejected {training_request.student.full_name}\'s training request.').save()
    training_request.delete()

    return redirect(reverse('training_requests'))


@require_POST
def cancel_training_request(request, request_id):
    training_request = TrainingRequest.objects.get(id=request_id)
    user = User.objects.get(cid=request.session.get('cid'))
    if user == training_request.student:
        training_request.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse('You are unauthorized to perform this action!', status=403)
