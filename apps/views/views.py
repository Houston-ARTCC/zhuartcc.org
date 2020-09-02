import requests
from django.shortcuts import render
from django.utils import timezone

from ..administration.models import Announcement
from ..api.models import Controller
from ..api.views import return_sorted_hours
from ..event.models import Event


def view_homepage(request):
    return render(request, 'homepage.html', {
        'online': Controller.objects.all(),
        'events': Event.objects.filter(hidden=False).filter(end__gte=timezone.now()).order_by('start')[:3],
        'announcements': Announcement.objects.all().order_by('-created')[:5],
        'top_controllers': return_sorted_hours()
    })


def view_privacy_policy(request):
    return render(request, 'privacy.html', {'page_title': 'Privacy Policy'})
