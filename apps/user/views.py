from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import User


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

    return render(request, 'staff.html', {'staff': staff})


# Gets all controllers by membership status from local database and serves 'roster.html' file
def view_roster(request):
    active_controllers = User.objects.all().exclude(status=2)
    home_controllers = active_controllers.filter(main_role='HC').order_by('first_name')
    visiting_controllers = active_controllers.filter(main_role='VC').order_by('first_name')
    mvap_controllers = active_controllers.filter(main_role='MC').order_by('first_name')

    return render(request, 'roster.html', {
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

    return render(request, 'profile.html', {'user': user})


# Gets specified user from local database and serves 'editUser.html' file. Overrides user info with form data on POST
def edit_user(request, cid):
    if 'staff' in request.session and request.session['staff']:
        user = User.objects.get(cid=cid)

        if request.method == 'POST':
            user.oper_init = request.POST['oper_init']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.staff_role = request.POST['staff_role']
            user.main_role = request.POST['main_role']
            user.home_facility = request.POST['home_facility']
            user.training_role = request.POST['training_role']
            user.del_cert = request.POST['del_cert']
            user.gnd_cert = request.POST['gnd_cert']
            user.twr_cert = request.POST['twr_cert']
            user.app_cert = request.POST['app_cert']
            user.ctr_cert = request.POST['ctr_cert']
            user.ocn_cert = request.POST['ocn_cert']
            user.save()
            return redirect('/roster')

        return render(request, 'editUser.html', {'user': user})
    else:
        return HttpResponse(status=401)
