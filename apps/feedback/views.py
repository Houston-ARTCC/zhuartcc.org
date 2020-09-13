from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from zhuartcc.decorators import require_staff, require_session
from .models import Feedback
from ..event.models import Event
from ..user.models import User


def view_all_feedback(request):
    return render(request, 'all_feedback.html', {
        'page_title': 'Feedback',
        'all_feedback': Feedback.objects.filter(approved=True),
    })


@require_session
def add_feedback(request):
    if request.method == 'POST':
        Feedback(
            controller=User.objects.get(cid=request.POST.get('controller')),
            controller_callsign=request.POST.get('controller_callsign'),
            rating=int(request.POST.get('rating')),
            pilot_name=request.POST.get('pilot_name', None),
            pilot_email=request.POST.get('pilot_email', None),
            event=Event.objects.get(id=request.POST.get('event')) if request.POST.get('event') != '' else None,
            flight_callsign=request.POST.get('flight_callsign', None),
            comments=request.POST.get('comments'),
        ).save()

        return redirect(reverse('feedback'))
    else:
        return render(request, 'add_feedback.html', {
            'page_title': 'Submit Feedback',
            'controllers': User.objects.filter(status=0),
            'events': Event.objects.filter(start__gte=timezone.now() - timedelta(days=30))
                      .filter(start__lte=timezone.now()).filter(hidden=False),
        })


@require_staff
def view_feedback_approval(request):
    return render(request, 'feedback_approval.html', {
        'page_title': 'Feedback Approval',
        'unapproved_feedback': Feedback.objects.filter(approved=False)
    })


@require_staff
@require_POST
def approve_feedback(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    feedback.approved = True
    feedback.save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def reject_feedback(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    feedback.delete()

    return HttpResponse(status=200)
