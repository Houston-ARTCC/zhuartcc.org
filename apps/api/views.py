from django.db.models import Sum, Q
from django.shortcuts import render
from django.utils import timezone

from .models import ControllerSession


def view_statistics(request):
    hours = ControllerSession.objects.aggregate(
        month=Sum('duration', filter=Q(time_logon__month=timezone.now().month)),
        year=Sum('duration', filter=Q(time_logon__year=timezone.now().year)),
        total=Sum('duration'),
    )
    return render(request, 'statistics.html', {'page_title': 'Statistics', 'hours': hours})
