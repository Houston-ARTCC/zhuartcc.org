from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Event, EventPosition
from zhuartcc.decorators import require_staff


def view_all_events(request):
    return render(request, 'all_events.html', {
        'page_title': 'Events',
        'events': Event.objects.all().order_by('start'),
    })


def view_event(request, id):
    event = Event.objects.get(id=id)
    return render(request, 'event.html', {'page_title': event.name, 'event': event})


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
    return redirect(f'/events/{id}')


@require_staff
def add_event(request):
    if request.method == 'POST':
        event = Event(
            name=request.POST['name'],
            banner=request.POST['banner'],
            start=request.POST['start'],
            end=request.POST['end'],
            description=request.POST['description'],
        )
        event.save()
        return redirect(f'/events/{event.id}')
    else:
        return render(request, 'new_event.html', {'page_title': 'New Event'})


@require_staff
@require_POST
def delete_event(request, id):
    Event.objects.get(id=id).delete()
    return redirect('/events')


@require_staff
@require_POST
def add_position(request, id):
    position = EventPosition(
        event=Event.objects.get(id=id),
        position=request.POST['position'],
    )
    position.save()
    return redirect(f'/events/{id}')


@require_staff
@require_POST
def delete_position(request, id):
    EventPosition.objects.get(id=request.POST['position_id']).delete()
    return redirect(f'/events/{id}')


@require_staff
@require_POST
def assign_position(request, id):
    pass


@require_POST
def request_position(request, id):
    pass
