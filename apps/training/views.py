from datetime import datetime, timedelta

import pytz
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from zhuartcc.decorators import require_member, require_mentor, require_staff_or_mentor
from .models import TrainingSession, TrainingRequest
from ..administration.models import ActionLog
from ..event.models import Event
from ..user.models import User


@require_member
def view_training_center(request):
    sessions = request.user_obj.student_sessions.all()
    return render(request, 'training_center.html', {
        'page_title': 'Training Center',
        'user': request.user_obj,
        'training_time': sum([session.duration for session in sessions.filter(status=1)], timedelta()),
    })


@require_member
def view_session(request, session_id):
    session = TrainingSession.objects.get(id=session_id)
    if (
            request.user_obj.cid == session.student.cid
            or request.user_obj.is_mentor or request.user_obj.is_staff
    ):
        return render(request, 'session.html', {
            'page_title': 'View Session',
            'session': session,
        })
    else:
        return HttpResponse('You are unauthorized to view somebody else\'s training session!', status=401)


@require_staff_or_mentor
def edit_session(request, session_id):
    session = TrainingSession.objects.get(id=session_id)

    if request.method == 'POST':
        session.instructor = User.objects.get(id=request.POST.get('instructor'))
        session.start = pytz.utc.localize(datetime.fromisoformat(request.POST.get('start')))
        session.end = pytz.utc.localize(datetime.fromisoformat(request.POST.get('end')))
        session.position = request.POST.get('position')
        session.type = request.POST.get('type')
        session.level = request.POST.get('level')
        session.status = request.POST.get('status')
        session.session_notes = request.POST.get('notes')
        session.session_file = request.FILES.get('ots', session.session_file)
        session.save()

        return redirect(reverse('view_session', args=[session.id]))

    return render(request, 'edit_session.html', {
        'page_title': 'Edit Session',
        'session': session,
        'instructors': User.objects.filter(training_role__in=['MTR', 'INS'])
    })


@require_member
def request_training(request):
    if request.method == 'POST':
        start = pytz.utc.localize(datetime.fromisoformat(request.POST['start']))
        end = pytz.utc.localize(datetime.fromisoformat(request.POST['end']))
        if start < end:
            TrainingRequest(
                student=request.user_obj,
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


@require_staff_or_mentor
def view_mentor_history(request):
    mentors = User.objects.filter(training_role__in=['MTR', 'INS'])
    return render(request, 'mentor_history.html', {
        'page_title': 'Mentor History',
        'mentors': [(
            mentor.full_name,
            mentor.instructor_sessions.filter(start__gte=timezone.now() - timedelta(days=30)).filter(status=1)
        ) for mentor in mentors]
    })


@require_staff_or_mentor
def view_scheduled_sessions(request):
    return render(request, 'scheduled_sessions.html', {
        'page_title': 'Scheduled Sessions',
        'sessions': TrainingSession.objects.filter(status=0),
    })


@require_staff_or_mentor
def view_student_profile(request, cid):
    student = User.objects.get(cid=cid)
    sessions = student.student_sessions.all()
    return render(request, 'student_profile.html', {
        'page_title': 'Student Profile',
        'student': student,
        'training_time': sum([session.duration for session in sessions.filter(status=1)], timedelta()),
    })


@require_member
def view_training_requests(request):
    if request.user_obj.is_mentor or request.user_obj.is_staff:
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
    TrainingSession(
        student=training_request.student,
        instructor=request.user_obj,
        start=pytz.utc.localize(datetime.strptime(request.POST['start'], '%Y-%m-%dT%H:%M:%S.%f')),
        end=pytz.utc.localize(datetime.strptime(request.POST['end'], '%Y-%m-%dT%H:%M:%S.%f')),
        type=training_request.type,
        level=training_request.level,
    ).save()

    ActionLog(action=f'{request.user_obj} accepted {training_request.student.full_name}\'s training request.').save()
    training_request.delete()

    return redirect(reverse('training_requests'))


@require_POST
@require_mentor
def reject_training_request(request, request_id):
    training_request = TrainingRequest.objects.get(id=request_id)

    ActionLog(action=f'{request.user_obj} rejected {training_request.student.full_name}\'s training request.').save()
    training_request.delete()

    return redirect(reverse('training_requests'))


@require_POST
def cancel_training_request(request, request_id):
    training_request = TrainingRequest.objects.get(id=request_id)
    if request.user_obj == training_request.student:
        training_request.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse('You are unauthorized to perform this action!', status=403)
