from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.shortcuts import render

from zhuartcc.decorators import require_member, require_logged_in
from .models import TrainingSession, Exam
from ..user.models import User


@require_member
def view_training_center(request):
    user = User.objects.get(cid=request.session['vatsim_data']['cid'])
    statistics = {
        'avg_exam_score': int(Exam.objects.filter(student=user).aggregate(Avg('score'))['score__avg']),
        'training_time': TrainingSession.objects.filter(student=user).aggregate(Sum('duration'))['duration__sum'],
    }
    return render(request, 'training_center.html', {
        'page_title': 'Training Center',
        'user': user,
        'statistics': statistics,
        'sessions': TrainingSession.objects.filter(student=user),
        'exams': Exam.objects.filter(student=user),
    })


@require_logged_in
def view_session(request, id):
    session = TrainingSession.objects.get(id=id)
    if (
        request.session['vatsim_data']['cid'] == session.student.cid
        or request.session['mentor'] or request.session['staff']
    ):
        return render(request, 'session.html', {'session': session})
    else:
        return HttpResponse('You are unauthorized to view somebody else\'s training session!', status=401)


def view_exam(request, id):
    exam = Exam.objects.get(id=id)
    if (
        request.session['vatsim_data']['cid'] == exam.student.cid
        or request.session['mentor'] or request.session['staff']
    ):
        return render(request, 'exam.html', {'exam': exam})
    else:
        return HttpResponse('You are unauthorized to view somebody else\'s exam!', status=401)
