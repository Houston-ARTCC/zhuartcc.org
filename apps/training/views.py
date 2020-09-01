from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.shortcuts import render

from zhuartcc.decorators import require_member
from .models import TrainingSession
from ..user.models import User


@require_member
def view_training_center(request):
    user = User.objects.get(cid=request.session['cid'])
    sessions = TrainingSession.objects.filter(student=user)
    statistics = {
        'training_time': sessions.filter(status=1).aggregate(Sum('duration'))['duration__sum'],
    }
    return render(request, 'training_center.html', {
        'page_title': 'Training Center',
        'user': user,
        'statistics': statistics,
        'sessions': sessions,
    })


@require_member
def view_session(request, id):
    session = TrainingSession.objects.get(id=id)
    if (
            request.session['cid'] == session.student.cid
            or request.session['mentor'] or request.session['staff']
    ):
        return render(request, 'session.html', {'session': session})
    else:
        return HttpResponse('You are unauthorized to view somebody else\'s training session!', status=401)
