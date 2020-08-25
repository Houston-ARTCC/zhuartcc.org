import pytz
from datetime import datetime
from itertools import groupby

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Event, EventPosition, PositionPreset, EventPositionRequest
from ..administration.models import ActionLog
from ..user.models import User
from zhuartcc.decorators import require_staff, require_member


def view_all_events(request):
    return render(request, 'events.html', {
        'page_title': 'Events',
        'events': Event.objects.filter(end__gte=timezone.now()).order_by('start'),
    })


def view_event(request, id):
    event = Event.objects.get(id=id)
    positions = {k: list(g) for k, g in groupby(event.positions.all(), key=lambda position: position.category)}
    available = {k: len(list(filter(lambda pos: pos.user is None, positions[k]))) for k in positions}
    user = User.objects.get(cid=request.session['cid'])
    requests = {str(pos.id): pos.requests.values_list('user', flat=True) for pos in event.positions.all()}
    return render(request, 'view_event.html', {
        'page_title': event.name,
        'event': event,
        'positions': positions,
        'available': available,
        'user': user,
        'requests': requests,
    })


@require_staff
def add_event(request):
    if request.method == 'POST':
        event = Event(
            name=request.POST['name'],
            start=pytz.utc.localize(datetime.fromisoformat(request.POST['start'])),
            end=pytz.utc.localize(datetime.fromisoformat(request.POST['end'])),
            banner=request.POST['banner'],
            host=request.POST['host'],
            description=request.POST['description'] if 'description' in request.POST else None,
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
        })


@require_staff
@require_POST
def edit_event(request, id):
    event = Event.objects.get(id=id)
    event.name = request.POST['name']
    event.banner = request.POST['banner']
    event.start = request.POST['start']
    event.end = request.POST['end']
    event.description = request.POST['description']
    event.save()

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Event "{event.name}" modified by {user.full_name}.').save()

    return redirect(f'/events/{id}')


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
    position = EventPosition(
        event=Event.objects.get(id=id),
        position=request.POST['position'],
    )
    position.save()

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Position "{position.name}" for "{position.event.name}" created by {user.full_name}.').save()

    return redirect(f'/events/{id}')


@require_staff
@require_POST
def delete_position(request, id):
    position = EventPosition.objects.get(id=id)

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Position "{position.name}" for "{position.event.name}" deleted by {user.full_name}.').save()

    position.delete()

    return redirect(f'/events/{id}')


@require_member
@require_POST
def request_position(request, id):
    EventPositionRequest(
        position=EventPosition.objects.get(id=id),
        user=User.objects.get(cid=request.session['cid']),
    ).save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def approve_position_request(request, id):
    position_request = EventPositionRequest.objects.get(id=id)
    position_request.position.user = position_request.user
    position_request.delete()

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
