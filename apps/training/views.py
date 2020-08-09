import json

from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from zhuartcc.decorators import require_member
from .models import TrainingSession, Exam
from ..user.models import User


@require_member
def view_training_center(request):
    user = User.objects.get(cid=request.session['cid'])
    statistics = {
        'avg_exam_score': Exam.objects.filter(student=user).aggregate(Avg('score'))['score__avg'],
        'training_time': TrainingSession.objects.filter(student=user).aggregate(Sum('duration'))['duration__sum'],
    }
    statistics['avg_exam_score'] = int(statistics['avg_exam_score']) if statistics['avg_exam_score'] else None
    return render(request, 'training_center.html', {
        'page_title': 'Training Center',
        'user': user,
        'statistics': statistics,
        'sessions': TrainingSession.objects.filter(student=user),
        'exams': Exam.objects.filter(student=user),
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


@require_member
def view_exam(request, id):
    exam = Exam.objects.get(id=id)
    if exam.completed:
        if request.session['cid'] == exam.student.cid or request.session['mentor'] or request.session['staff']:
            return render(request, 'review_exam.html', {'exam': exam, 'answers': exam.get_answers()})
        else:
            return HttpResponse('You are unauthorized to view somebody else\'s exam!', status=401)
    else:
        if request.method == 'POST':
            answers = {question.id: request.POST[f'question_{question.id}'] for question in exam.questions.all()}
            exam.answers = json.dumps(answers)
            exam.submitted = timezone.now()
            exam.save()
            exam.score_exam()

            return HttpResponse(status=200)

        return render(request, 'take_exam.html', {'exam': exam})
