import calendar
from datetime import timedelta

from django.db.models import Sum, Q
from django.shortcuts import render
from django.utils import timezone

from .models import ControllerSession
from ..training.models import TrainingSession
from ..user.models import User


def view_statistics(request):
    now = timezone.now()
    main_stats = ControllerSession.objects.aggregate(
        month=Sum('duration', filter=Q(time_logon__month=now.month)),
        year=Sum('duration', filter=Q(time_logon__year=now.year)),
        total=Sum('duration'),
    )
    main_users = [return_hour_aggregate(user) for user in User.objects.exclude(main_role='MC').order_by('first_name')]
    mvap_users = [return_hour_aggregate(user) for user in User.objects.filter(main_role='MC').order_by('first_name')]
    months = [calendar.month_name[now.month - 2], calendar.month_name[now.month - 1], calendar.month_name[now.month]]

    return render(request, 'statistics.html', {
        'page_title': 'Statistics',
        'main_stats': main_stats,
        'main_users': main_users,
        'mvap_users': mvap_users,
        'months': months,
    })


def return_hour_aggregate(user):
    now = timezone.now()
    aggregate = {
        'user_obj': user,
        'hours': ControllerSession.objects.filter(user=user).aggregate(
            current=Sum('duration', filter=Q(time_logon__month=now.month)),
            previous=Sum('duration', filter=Q(time_logon__month=now.month - 1)),
            previous1=Sum('duration', filter=Q(time_logon__month=now.month - 2)),
        )
    }
    if aggregate['user_obj'].is_staff:
        requirement = timedelta(hours=5)
    elif aggregate['user_obj'].cert_int > 0:
        requirement = timedelta(hours=2)
    else:
        requirement = timedelta()

    hours = aggregate['hours']
    aggregate['current_status'] = hours['current'] >= requirement if hours['current'] is not None else False
    aggregate['previous_status'] = hours['previous'] >= requirement if hours['previous'] is not None else False
    aggregate['previous1_status'] = hours['previous1'] >= requirement if hours['previous1'] is not None else False
    return aggregate


def return_inactive_users():
    inactive_users = []
    for user_status in [return_hour_aggregate(user) for user in User.objects.exclude(main_role='MC')]:
        if 'current_status' in user_status and not user_status['current_status']:
            inactive_users.append(user_status)

    return inactive_users


def return_sorted_hours():
    aggregates = []
    for user in User.objects.all():
        aggregate = {
            'user': user,
            'hours': ControllerSession.objects.filter(user=user).aggregate(
                current=Sum('duration', filter=Q(time_logon__month=timezone.now().month))
            )['current']
        }

        if not aggregate['hours']:
            aggregate['hours'] = timedelta()

        aggregates += [aggregate]

    return sorted(aggregates, key=lambda i: i['hours'], reverse=True)
