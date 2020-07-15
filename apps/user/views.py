import pytz
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.http import require_POST

from .models import User
from zhuartcc.decorators import require_staff


# Gets all staff members from local database and serves 'staff.html' file
def view_staff(request):
    staff = {
        'ATM': User.objects.filter(staff_role='ATM').first(),
        'DATM': User.objects.filter(staff_role='DATM').first(),
        'TA': User.objects.filter(staff_role='TA').first(),
        'ATA': User.objects.filter(staff_role='ATA').first(),
        'FE': User.objects.filter(staff_role='FE').first(),
        'AFE': User.objects.filter(staff_role='AFE').first(),
        'EC': User.objects.filter(staff_role='EC').first(),
        'AEC': User.objects.filter(staff_role='AEC').first(),
        'WM': User.objects.filter(staff_role='WM').first(),
        'AWM': User.objects.filter(staff_role='AWM').first(),
        'INS': User.objects.filter(training_role='INS'),
        'MTR': User.objects.filter(training_role='MTR'),
    }

    return render(request, 'staff.html', {'page_title': 'Staff', 'staff': staff})


# Gets all controllers by membership status from local database and serves 'roster.html' file
def view_roster(request):
    active_controllers = User.objects.all().exclude(status=2)
    home_controllers = active_controllers.filter(main_role='HC').order_by('first_name')
    visiting_controllers = active_controllers.filter(main_role='VC').order_by('first_name')
    mvap_controllers = active_controllers.filter(main_role='MC').order_by('first_name')

    return render(request, 'roster.html', {
        'page_title': 'Roster',
        'home': sort_controllers(home_controllers),
        'visiting': sort_controllers(visiting_controllers),
        'mvap': sort_controllers(mvap_controllers),
    })


# Sorts controllers by certification level
def sort_controllers(query_set):
    return {
        'Oceanic': query_set.filter(cert_int=8),
        'Center': query_set.filter(cert_int=7),
        'Major Approach': query_set.filter(cert_int=6),
        'Minor Approach': query_set.filter(cert_int=5),
        'Major Tower': query_set.filter(cert_int=4),
        'Minor Tower': query_set.filter(cert_int=3),
        'Major Ground': query_set.filter(cert_int=2),
        'Minor Ground': query_set.filter(cert_int=1),
        'Observer': query_set.filter(cert_int=0),
    }


# Gets specified user from local database and serves 'profile.html' file
def view_user_profile(request, cid):
    user = User.objects.get(cid=cid)

    return render(request, 'profile.html', {'page_title': user.return_full_name(), 'user': user})


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
        user.home_facility = post['home_facility'] if 'home_facility' in post else None
        user.staff_role = post['staff_role'] if post['staff_role'] in settings.STAFF_ROLES else None
        user.training_role = post['training_role'] if post['training_role'] in settings.TRAINING_ROLES else None
        user.activity_exempt = True if 'activity_exempt' in post else False
        user.biography = post['biography'] if 'biography' in post else ''
        user.del_cert = int(post['del_cert'])
        user.gnd_cert = int(post['gnd_cert'])
        user.twr_cert = int(post['twr_cert'])
        user.app_cert = int(post['app_cert'])
        user.ctr_cert = int(post['ctr_cert'])
        user.ocn_cert = int(post['ocn_cert'])
        user.cert_int = user.return_cert_int()
        user.save()
        return redirect('/roster')

    return render(request, 'editUser.html', {'page_title': f'Editing {user.return_full_name()}', 'user': user})


@require_staff
@require_POST
def update_status(request):
    try:
        user = User.objects.get(id=request.POST['id'])
        user.status = int(request.POST['status'])
        if request.POST['status'] == '1':
            user.loa_until = pytz.utc.localize(datetime.strptime(request.POST['loa_until'], '%Y-%m-%d'))
        else:
            user.loa_until = None
        user.save()

        return HttpResponse(status=200)
    except:
        return HttpResponse('Something was wrong your request!', status=400)
