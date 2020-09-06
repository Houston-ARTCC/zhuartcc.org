import pytz
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Event, EventPosition, PositionPreset, EventPositionRequest
from ..administration.models import ActionLog
from ..training.models import TrainingSession
from ..user.models import User
from zhuartcc.decorators import require_staff, require_member, require_logged_in


@require_logged_in
def view_event_score(request, cid=None):
    user_cid = cid or request.session['cid']

    if cid and not request.session['staff'] and cid != request.session['cid']:
        return HttpResponse(status=403)

    return render(request, 'event_score.html', {
        'page_title': 'Event Score History',
        'user': User.objects.get(cid=user_cid),
    })


def view_all_events(request):
    return render(request, 'events.html', {
        'page_title': 'Events',
        'events': Event.objects.filter(end__gte=timezone.now()).order_by('start'),
    })


def view_archived_events(request):
    return render(request, 'archived_events.html', {
        'page_title': 'Archived Events',
        'events': Event.objects.filter(start__lte=timezone.now()).order_by('-start'),
    })


def view_event(request, id):
    event = Event.objects.get(id=id)
    if event.hidden and request.session['staff'] or not event.hidden:
        positions = {'center': [], 'tracon': [], 'cab': []}
        for position in event.positions.all():
            positions[position.category] += [position]
        user = User.objects.get(cid=request.session['cid']) if 'cid' in request.session else None
        return render(request, 'view_event.html', {
            'page_title': event.name,
            'event': event,
            'positions': positions,
            'available': {k: len(list(filter(lambda pos: pos.user is None, positions[k]))) for k in positions},
            'user': user,
            'allowed_to_signup': user and not user.prevent_event_signup and event.end >= timezone.now(),
            'time_now': timezone.now(),
        })
    else:
        return HttpResponse(status=403)


@require_staff
def add_event(request):
    if request.method == 'POST':
        event = Event(
            name=request.POST['name'],
            start=pytz.utc.localize(datetime.fromisoformat(request.POST['start'])),
            end=pytz.utc.localize(datetime.fromisoformat(request.POST['end'])),
            banner=request.POST['banner'],
            host=request.POST['host'],
            description=request.POST.get('description', None),
            hidden=True if 'hidden' in request.POST else False,
        )
        event.save()

        user = User.objects.get(cid=request.session['cid'])
        ActionLog(action=f'Event "{event.name}" created by {user.full_name}.').save()

        if request.POST['preset']:
            PositionPreset.objects.get(id=request.POST['preset']).add_to_event(event)

        return redirect(f'/events/{event.id}')
    else:
        return render(request, 'new_event.html', {
            'page_title': 'New Event',
            'position_presets': PositionPreset.objects.all(),
            'events': Event.objects.all(),
            'sessions': TrainingSession.objects.all(),
        })


@require_staff
def edit_event(request, id):
    event = Event.objects.get(id=id)
    if event.end >= timezone.now():
        if request.method == 'POST':
            event.name = request.POST['name']
            event.start = pytz.utc.localize(datetime.fromisoformat(request.POST['start']))
            event.end = pytz.utc.localize(datetime.fromisoformat(request.POST['end']))
            event.banner = request.POST['banner']
            event.host = request.POST['host']
            event.description = request.POST.get('description', None)
            event.hidden = True if 'hidden' in request.POST else False
            event.save()

            user = User.objects.get(cid=request.session['cid'])
            ActionLog(action=f'Event "{event.name}" modified by {user.full_name}.').save()

            return redirect(f'/events/{id}/')
        else:
            positions = {'center': [], 'tracon': [], 'cab': []}
            for position in event.positions.all():
                positions[position.category] += [position]
            return render(request, 'edit_event.html', {
                'page_title': f'Editing {event.name}',
                'positions': positions,
                'event': event
            })
    else:
        return HttpResponse(status=403)


@require_staff
@require_POST
def delete_event(request, id):
    event = Event.objects.get(id=id)

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Event "{event.name}" deleted by {user.full_name}.').save()

    event.delete()

    return redirect('/events')


@require_staff
@require_POST
def add_position(request, id):
    EventPosition(
        event=Event.objects.get(id=id),
        name=request.POST['position'],
    ).save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def delete_position(request, id):
    EventPosition.objects.get(id=id).delete()

    return HttpResponse(status=200)


@require_member
@require_POST
@csrf_exempt
def request_position(request, id):
    user = User.objects.get(cid=request.session['cid'])
    if user.prevent_event_signup:
        return HttpResponse('You are not allowed to sign up for events!', status=403)
    else:
        EventPositionRequest(
            position=EventPosition.objects.get(id=id),
            user=user,
        ).save()

        return HttpResponse(status=200)


@require_member
@require_POST
@csrf_exempt
def unrequest_position(request, id):
    position_request = EventPositionRequest.objects.get(id=id)
    if position_request.user.id == User.objects.get(cid=request.session['cid']).id:
        position_request.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse('You are unauthorized to complete this action!', status=401)


@require_staff
@require_POST
def assign_position(request, id):
    EventPositionRequest.objects.get(id=id).assign()

    return HttpResponse(status=200)


@require_staff
@require_POST
def unassign_position(request, id):
    position = EventPosition.objects.get(id=id)
    position.user = None
    position.save()

    return HttpResponse(status=200)


@require_staff
def view_presets(request):
    return render(request, 'presets.html', {
        'page_title': 'Position Presets',
        'position_presets': PositionPreset.objects.all(),
    })


@require_staff
@require_POST
def add_preset(request):
    preset = PositionPreset(
        name=request.POST['name']
    )
    preset.save()

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Position preset "{preset.name}" created by {user.full_name}.').save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def edit_preset(request, id):
    preset = PositionPreset.objects.get(id=id)
    preset.positions_json = request.POST['positions']
    preset.save()

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Position preset "{preset.name}" modified by {user.full_name}.').save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def delete_preset(request, id):
    preset = PositionPreset.objects.get(id=id)

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Position preset "{preset.name}" deleted by {user.full_name}.').save()

    preset.delete()

    return HttpResponse(status=200)
