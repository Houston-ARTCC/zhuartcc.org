from django.shortcuts import render

from .models import Event


def view_all_events(request):
    return render(request, 'all_events.html', {
        'page_title': 'Events',
        'events': Event.objects.all().order_by('start'),
    })


def view_event(request, id):
    pass


def edit_event(request, id):
    pass


def create_event(request):
    pass
