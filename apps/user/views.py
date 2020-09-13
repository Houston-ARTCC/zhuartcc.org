import calendar
import os
from itertools import groupby

import requests
import pytz
from datetime import datetime

from django.core.mail import send_mail
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import User
from ..administration.models import ActionLog
from ..api.models import ControllerSession
from ..api.views import return_inactive_users
from zhuartcc.decorators import require_staff


# Gets all staff members from local database and serves 'staff.html' file
def view_staff(request):
    staff = {
        'ATM': User.objects.filter(staff_role='ATM'),
        'DATM': User.objects.filter(staff_role='DATM'),
        'TA': User.objects.filter(staff_role='TA'),
        'ATA': User.objects.filter(staff_role='ATA'),
        'FE': User.objects.filter(staff_role='FE'),
        'AFE': User.objects.filter(staff_role='AFE'),
        'EC': User.objects.filter(staff_role='EC'),
        'AEC': User.objects.filter(staff_role='AEC'),
        'WM': User.objects.filter(staff_role='WM'),
        'AWM': User.objects.filter(staff_role='AWM'),
        'INS': User.objects.filter(training_role='INS'),
        'MTR': User.objects.filter(training_role='MTR'),
    }

    return render(request, 'staff.html', {'page_title': 'Staff', 'staff': staff})


# Gets all controllers by membership status from local database and serves 'roster.html' file
def view_roster(request):
    active_controllers = User.objects.exclude(status=2)
    home_controllers = active_controllers.filter(main_role='HC').order_by('first_name')
    visiting_controllers = active_controllers.filter(main_role='VC').order_by('first_name')
    mavp_controllers = active_controllers.filter(main_role='MC').order_by('first_name')

    return render(request, 'roster.html', {
        'page_title': 'Roster',
        'home': sort_controllers(home_controllers),
        'visiting': sort_controllers(visiting_controllers),
        'mavp': sort_controllers(mavp_controllers),
    })


# Sorts controllers by certification level
def sort_controllers(query_set):
    controllers = sorted(query_set, key=lambda controller: controller.cert_int)
    controllers_ordered = {k: list(g) for k, g in groupby(controllers, key=lambda controller: controller.cert_int)}
    for i in range(9):
        if i not in controllers_ordered:
            controllers_ordered[i] = []
    return {
        'Oceanic': controllers_ordered[8],
        'Center': controllers_ordered[7],
        'Major Approach': controllers_ordered[6],
        'Minor Approach': controllers_ordered[5],
        'Major Tower': controllers_ordered[4],
        'Minor Tower': controllers_ordered[3],
        'Major Ground': controllers_ordered[2],
        'Minor Ground': controllers_ordered[1],
        'Observer': controllers_ordered[0],
    }


# Gets specified user from local database and serves 'profile.html' file
def view_profile(request, cid):
    user_query = User.objects.filter(cid=cid)
    if user_query.exists():
        user = user_query.first()
    else:
        return HttpResponse('User with specified CID was not found!', status=404)

    connections = ControllerSession.objects.filter(user=user).order_by('-start')
    now = timezone.now()
    stats = connections.aggregate(
        month=Sum('duration', filter=Q(start__month=now.month)),
        year=Sum('duration', filter=Q(start__year=now.year)),
        total=Sum('duration'),
    )

    return render(request, 'profile.html', {
        'page_title': user.full_name,
        'user': user,
        'stats': stats,
        'connections': connections,
    })


# Gets specified user from local database and serves 'editUser.html' file. Overrides user info with form data on POST
@require_staff
def edit_user(request, cid):
    user = User.objects.get(cid=cid)

    if request.method == 'POST':
        post = request.POST
        user.oper_init = post['oper_init']
        user.first_name = post['first_name']
        user.last_name = post['last_name']
        user.email = post['email']
        user.main_role = post['main_role']
        user.home_facility = request.POST.get('home_facility', None)
        user.staff_role = request.POST.get('staff_role', None)
        user.training_role = request.POST.get('training_role', None)
        user.mentor_level = request.POST.get('mentor_level', None)
        user.activity_exempt = True if 'activity_exempt' in post else False
        user.prevent_event_signup = True if 'prevent_event_signup' in post else False
        user.biography = request.POST.get('biography', None)
        user.del_cert = int(post['del_cert'])
        user.gnd_cert = int(post['gnd_cert'])
        user.twr_cert = int(post['twr_cert'])
        user.app_cert = int(post['app_cert'])
        user.ctr_cert = int(post['ctr_cert'])
        user.ocn_cert = int(post['ocn_cert'])
        user.save()

        ActionLog(action=f'User {user.full_name} modified by {request.user_obj}.').save()
        return redirect(reverse('roster'))

    return render(request, 'editUser.html', {'page_title': f'Editing {user.full_name}', 'user': user})


@require_staff
@require_POST
def update_status(request, cid):
    user = User.objects.get(cid=cid)
    user.status = int(request.POST.get('status'))
    if request.POST.get('status') == '1':
        user.loa_until = pytz.utc.localize(datetime.strptime(request.POST.get('loa_until'), '%Y-%m-%d'))
        status = 'LOA until ' + request.POST.get('loa_until')
    if request.POST.get('status') == '2':
        status = 'inactive'
    else:
        status = 'active'
        user.loa_until = None
    user.save()

    ActionLog(action=f'User {user.full_name} set as {status} by {request.user_obj}.').save()

    return HttpResponse(status=200)


@require_staff
def view_inactive_users(request):
    now = timezone.now()
    months = [calendar.month_name[now.month - 2], calendar.month_name[now.month - 1], calendar.month_name[now.month]]
    return render(request, 'roster_tidy.html', {
        'page_title': 'Roster Tidy',
        'months': months,
        'users': return_inactive_users(),
    })


@require_staff
@require_POST
def remove_users(request):
    for id in request.POST.keys():
        if id != 'csrfmiddlewaretoken':
            user = User.objects.get(id=id)
            if user.main_role == 'HC':
                requests.delete(f'https://api.vatusa.net/v2/facility/{os.getenv("ARTCC_ICAO")}/roster/{user.cid}')
            user.status = 2
            user.save()
            send_mail(
                'Roster Removal Notification',
                render_to_string('emails/roster_removal.html', {'user': user}),
                os.getenv('NO_REPLY'),
                [user.email],
                fail_silently=True,
            )

            ActionLog(action=f'User {user.full_name} removed from the ARTCC {request.user_obj}.').save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def add_comment(request, cid):
    user = User.objects.get(cid=cid)
    user.staff_comment = request.POST.get('comment')
    user.staff_comment_author = request.user_obj
    user.save()

    ActionLog(action=f'Staff comment for {user.full_name} added by {request.user_obj}.').save()

    return redirect(reverse('view_user', args=[user.cid]))


@require_staff
@require_POST
def remove_comment(request, cid):
    user = User.objects.get(cid=cid)
    user.staff_comment = None
    user.staff_comment_author = None
    user.save()

    ActionLog(action=f'Staff comment for {user.full_name} removed by {request.user_obj}.').save()

    return redirect(reverse('view_user', args=[user.cid]))
