from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from ..administration.models import Announcement
from ..api.models import Controller
from ..api.views import return_sorted_hours
from ..event.models import Event
from ..training.models import TrainingSession


def view_homepage(request):
    return render(request, 'homepage.html', {
        'online': Controller.objects.all(),
        'events': Event.objects.filter(hidden=False).filter(end__gte=timezone.now()).order_by('start')[:5],
        'announcements': Announcement.objects.all().order_by('-created')[:5],
        'top_controllers': return_sorted_hours()
    })


def view_privacy_policy(request):
    return render(request, 'privacy.html', {'page_title': 'Privacy Policy'})


def view_calendar(request):
    events = Event.objects.all()
    return render(request, 'calendar.html', {
        'page_title': 'Calendar',
        'events': events if request.user_obj and request.user_obj.is_staff else events.filter(hidden=False),
        'sessions': TrainingSession.objects.all()
    })


def error_404(request, exception):
    if request.method == 'POST':
        return HttpResponse('The requested resource or endpoint was not found!', status=404)

    response = render(request, 'errorTemplate.html', {
        'error': 404,
        'title': 'We searched everything!',
        'exception': 'The requested resource or endpoint was not found!'
    })
    response.status_code = 404
    return response


def error_500(request):
    exception = 'The server encountered an error while processing your request. The webmaster has been notified.'
    if request.method == 'POST':
        return HttpResponse(exception, status=500)

    response = render(request, 'errorTemplate.html', {
        'error': 500,
        'title': 'Uh oh!',
        'exception': exception
    })
    response.status_code = 500
    return response


def error_403(request, exception):
    if request.method == 'POST':
        return HttpResponse(exception, status=403)

    response = render(request, 'errorTemplate.html', {
        'error': 403,
        'title': 'Access Denied!',
        'exception': exception
    })
    response.status_code = 403
    return response


def error_400(request, exception):
    if request.method == 'POST':
        return HttpResponse(exception, status=400)

    response = render(request, 'errorTemplate.html', {
        'error': 400,
        'title': 'Well... this is awkward...',
        'exception': exception
    })
    response.status_code = 400
    return response
