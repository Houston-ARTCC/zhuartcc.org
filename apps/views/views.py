import requests
from django.shortcuts import render

from ..api.models import Controller


def view_homepage(request):
    return render(request, 'homepage.html', {
        'online': Controller.objects.all(),
        'pilots': requests.get('https://api.denartcc.org/live/ZHU').json,
    })


def view_privacy_policy(request):
    return render(request, 'privacy.html', {'page_title': 'Privacy Policy'})
