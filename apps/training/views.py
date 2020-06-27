from django.http import HttpResponse
from django.shortcuts import render

from ..user.models import User
from .models import TrainingSession


def view_training_center(request):
    if 'vatsim_data' in request.session:
        user = User.objects.get(cid=request.session['vatsim_data']['cid'])
        scheduled_sessions = TrainingSession.objects.filter(student_id=user.id).filter(status=0)
        return render(request, 'trainingCenter.html', {'user': user, 'sessions': scheduled_sessions})
    return HttpResponse(status=401)


def view_history(request, cid):
    if 'vatsim_data' in request.session:
        user = User.objects.get(cid=cid)
        sessions = TrainingSession.objects.filter(student_id=user.id).order_by('-start')
        if request.session['mentor'] or request.session['staff'] or request.session['vatsim_data']['cid'] == user.cid:
            return render(request, 'viewHistory.html', {'user': user, 'sessions': sessions})
    return HttpResponse(status=401)


def schedule(request):
    if 'vatsim_data' in request.session:
        user = User.objects.get(cid=request.session['vatsim_data']['cid'])
        return render(request, 'schedule.html', {'user': user})
    return HttpResponse(status=401)


def submit_training_request(request):
    pass


def delete_training_request(request):
    pass


def accept_training_request(request):
    if 'mentor' in request.session and request.session['mentor']:
        if request.method == 'POST':
            pass
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=401)
