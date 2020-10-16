import os
import pytz
import requests
from datetime import datetime, timedelta
from discord_webhook import DiscordEmbed, DiscordWebhook

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from zhuartcc.decorators import require_member, require_mentor, require_staff_or_mentor
from zhuartcc.overrides import send_mail
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


def modify_session(session, request):
    session.instructor = User.objects.get(id=request.POST.get('instructor'))
    session.start = pytz.utc.localize(datetime.fromisoformat(request.POST.get('start')))
    session.end = pytz.utc.localize(datetime.fromisoformat(request.POST.get('end')))
    session.movements = request.POST.get('movements')
    session.progress = request.POST.get('progress')
    session.position = request.POST.get('position')
    session.type = request.POST.get('type')
    session.level = request.POST.get('level')
    session.status = 1
    session.ots_status = request.POST.get('ots_status')
    session.notes = request.POST.get('notes')
    session.save()

    # Visitors don't get training records posted to VATUSA CTRS
    if session.student.main_role == 'HC':
        hours, remainder = divmod(session.duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        data = {
            'apikey': os.getenv('API_KEY'),
            'instructor_id': session.instructor.cid,
            'session_date': session.start.strftime('%Y-%m-%d %H:%M'),
            'position': session.position,
            'duration': f'{int(hours):02}:{int(minutes):02}',
            'movements': session.movements,
            'score': session.progress,
            'notes': 'No notes provided.' if session.notes == '' else session.notes,
            'location': 1 if session.type == 2 else 2 if session.type == 1 else 0,
            'ots_status': session.ots_status,
        }

        if session.ctrs_id is not None:
            requests.put(f'https://api.vatusa.net/v2/training/record/{session.ctrs_id}', data=data)
        else:
            post_ctrs = requests.post(f'https://api.vatusa.net/v2/user/{session.student.cid}/training/record', data=data)

            if post_ctrs.json()['status'] == 'OK':
                session.ctrs_id = post_ctrs.json()['id']


@require_staff_or_mentor
def file_session(request, session_id):
    session = TrainingSession.objects.get(id=session_id)

    if session.status == 0:
        if request.method == 'POST':
            modify_session(session, request)

            return redirect(reverse('view_session', args=[session.id]))

        return render(request, 'file_session.html', {
            'page_title': 'File Session',
            'session': session,
            'instructors': User.objects.filter(training_role='INS'),
            'mentors': User.objects.filter(training_role='MTR'),
        })
    else:
        return HttpResponse('You cannot file a completed, cancelled, or no-show session!', status=401)


@require_staff_or_mentor
def edit_session(request, session_id):
    session = TrainingSession.objects.get(id=session_id)

    if request.method == 'POST':
        modify_session(session, request)

        return redirect(reverse('view_session', args=[session.id]))

    return render(request, 'edit_session.html', {
        'page_title': 'Edit Session',
        'session': session,
        'instructors': User.objects.filter(training_role='INS'),
        'mentors': User.objects.filter(training_role='MTR'),
    })


@require_member
def request_training(request):
    if request.method == 'POST':
        start = pytz.utc.localize(datetime.fromisoformat(request.POST.get('start')))
        end = pytz.utc.localize(datetime.fromisoformat(request.POST.get('end')))
        if start < end:
            training_request = TrainingRequest(
                student=request.user_obj,
                start=pytz.utc.localize(datetime.fromisoformat(request.POST.get('start'))),
                end=pytz.utc.localize(datetime.fromisoformat(request.POST.get('end'))),
                type=int(request.POST.get('type')),
                level=int(request.POST.get('level')),
                remarks=request.POST.get('remarks', None)
            )
            training_request.save()

            send_mail(
                'Training Request Received',
                render_to_string('emails/request_received.html', {'request': training_request}),
                os.getenv('NO_REPLY'),
                [training_request.student.email],
            )

            format = '%b %d, %Y @ %H%Mz'
            webhook = DiscordWebhook(url=os.getenv('TRAINING_WEBHOOK_URL'))
            embed = DiscordEmbed(
                title=':pencil:  New Training Request!',
                description='See all requests at https://www.zhuartcc.org/training/requests.',
                color=2966946
            )
            embed.add_embed_field(
                name='User',
                value=f'[{request.user_obj.cid}] {request.user_obj.full_name}',
                inline=False,
            )
            embed.add_embed_field(
                name='Availability',
                value=f'{training_request.start.strftime(format)} - {training_request.end.strftime(format)}',
                inline=False,
            )
            embed.add_embed_field(name='Level', value=training_request.get_level_display())
            embed.add_embed_field(name='Type', value=training_request.get_type_display())
            embed.add_embed_field(
                name='Remarks',
                value=training_request.remarks if training_request.remarks != '' else 'No Remarks Provided',
                inline=False,
            )
            webhook.add_embed(embed)
            webhook.execute()
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
    training_session = TrainingSession(
        student=training_request.student,
        instructor=request.user_obj,
        start=pytz.utc.localize(datetime.strptime(request.POST.get('start'), '%Y-%m-%dT%H:%M:%S.%f')),
        end=pytz.utc.localize(datetime.strptime(request.POST.get('end'), '%Y-%m-%dT%H:%M:%S.%f')),
        type=training_request.type,
        level=training_request.level,
    )
    training_session.save()

    send_mail(
        'Training Scheduled!',
        render_to_string('emails/request_accepted.html', {'session': training_session}),
        os.getenv('NO_REPLY'),
        [training_session.student.email, training_session.instructor.email],
    )

    ActionLog(action=f'{request.user_obj} accepted {training_request.student.full_name}\'s training request.').save()
    training_request.delete()

    return redirect(reverse('training_requests'))


@require_POST
@require_mentor
def reject_training_request(request, request_id):
    training_request = TrainingRequest.objects.get(id=request_id)

    send_mail(
        'Training Request Rejected',
        render_to_string('emails/request_rejected.html', {'request': training_request}),
        os.getenv('NO_REPLY'),
        [training_request.student.email],
    )
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
