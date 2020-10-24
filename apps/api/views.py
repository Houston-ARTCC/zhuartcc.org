import calendar
import os
from datetime import timedelta

from discord_webhook import DiscordEmbed, DiscordWebhook
from django.db.models import Sum, Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ControllerSession, CurrentAtis
from ..user.models import User


def view_statistics(request):
    now = timezone.now()
    main_stats = ControllerSession.objects.aggregate(
        month=Sum('duration', filter=Q(start__month=now.month) & Q(start__year=now.year)),
        year=Sum('duration', filter=Q(start__year=now.year)),
        total=Sum('duration'),
    )
    main_users = [return_hour_aggregate(user) for user in User.objects.exclude(main_role='MC').order_by('first_name')]
    months = [calendar.month_name[now.month - 2], calendar.month_name[now.month - 1], calendar.month_name[now.month]]

    return render(request, 'statistics.html', {
        'page_title': 'Statistics',
        'main_stats': main_stats,
        'main_users': main_users,
        'months': months,
    })


def return_hour_aggregate(user):
    now = timezone.now()
    prev_filter = (Q(start__month=now.month - 1 if now.month > 1 else 12)
                   & Q(start__year=now.year if now.month > 1 else now.year - 1))
    prev1_filter = (Q(start__month=now.month - 2 if now.month > 2 else 12 if now.month == 2 else 11)
                    & Q(start__year=now.year if now.month > 2 else now.year - 1))
    aggregate = {
        'user_obj': user,
        'hours': ControllerSession.objects.filter(user=user).aggregate(
            current=Sum('duration', filter=Q(start__month=now.month) & Q(start__year=now.year)),
            previous=Sum('duration', filter=prev_filter),
            previous1=Sum('duration', filter=prev1_filter),
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
        now = timezone.now()
        aggregate = {
            'user': user,
            'hours': ControllerSession.objects.filter(user=user).aggregate(
                current=Sum('duration', filter=Q(start__month=now.month) & Q(start__year=now.year))
            )['current']
        }

        if not aggregate['hours']:
            aggregate['hours'] = timedelta()

        aggregates += [aggregate]

    return sorted(aggregates, key=lambda i: i['hours'], reverse=True)


@require_POST
def update_atis(request):
    webhook = DiscordWebhook(url=os.getenv('LOGGING_WEBHOOK_URL'))
    embed = DiscordEmbed(
        title='POST - vATIS',
        description=f'```{request.POST} :: {request.POST.get("facility")}```',
        color=2966946
    )
    webhook.add_embed(embed)
    webhook.execute()
    try:
        CurrentAtis(
            facility=request.POST.get('facility'),
            config_profile=request.POST.get('config_profile'),
            atis_letter=request.POST.get('atis_letter'),
            airport_conditions=request.POST.get('airport_conditions'),
            notams=request.POST.get('notams'),
        ).save()
    except:
        return HttpResponse(status=400)
    return HttpResponse(status=200)


def get_atis(request, icao):
    atis = CurrentAtis.objects.filter(facility=icao.upper()).first()
    if atis:
        return JsonResponse(model_to_dict(atis))
    else:
        return HttpResponse(f'ATIS for facility {icao.upper()} was not found.', status=404)
