from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime

from django.views.decorators.http import require_POST

from .models import Visit
from ..user.updater import assign_oper_init


# Serves 'visit.html' file. Saves request from form data on POST
def submit_visiting_request(request):
    if request.method == 'POST':
        form_data = request.POST
        visiting_request = Visit(
            cid=form_data['cid'],
            rating=form_data['rating'],
            home_facility=form_data['home_facility'],
            first_name=form_data['first_name'],
            last_name=form_data['last_name'],
            email=form_data['email'],
            reason=form_data['reason'],
            submitted=datetime.now(),
        )
        visiting_request.save()
        return redirect('/')

    # Ensures that user is eligible to visit
    if 'vatsim_data' not in request.session:
        status = {
            'eligible': False,
            'reason': 'You must be logged in to submit a request. Please log in with your VATSIM account and try again.'
        }
    elif User.objects.filter(cid=request.session['vatsim_data']['cid']).exists():
        status = {
            'eligible': False,
            'reason': 'You are already a member of the ZHU ARTCC, go control a position silly!'
        }
    elif request.session['vatsim_data']['rating'] == 'OBS':
        status = {
            'eligible': False,
            'reason': 'Unfortunately, you must be an S1 or above to visit the Houston ARTCC. Feel free to submit a '
                      'request once you meet the requirements.'
        }
    else:
        status = {'eligible': True}

    return render(request, 'visit.html', {'status': status})


# Gets all visiting requests from local database and serves 'visitRequests.html' file
def view_visiting_requests(request):
    if 'staff' in request.session and request.session['staff']:
        visiting_requests = Visit.objects.all()
        return render(request, 'visitRequests.html', {'visiting_requests': visiting_requests})
    else:
        return HttpResponse(status=401)


# Creates User object from visiting request with CID specified in POST
@require_POST
def accept_visiting_request(request):
    if 'staff' in request.session and request.session['staff']:
        visiting_request = Visit.objects.get(cid=request.POST['cid'])

        new_user = User(
            first_name=visiting_request.first_name.capitalize(),
            last_name=visiting_request.last_name.capitalize(),
            cid=visiting_request.cid,
            email=visiting_request.email,
            oper_init=assign_oper_init(visiting_request.first_name[0], visiting_request.last_name[0]),
            home_facility=visiting_request.home_facility,
            rating=visiting_request.rating,
            main_role='VC',
        )
        new_user.assign_initial_cert()
        new_user.save()

        message = {
            'recipient_name': visiting_request.first_name,
            'text': 'Your visiting request has been accepted.',
            'sender': 'Marcus Miller',
            'sender_role': 'Air Traffic Manager'
        }
        send_mail(
            'Welcome to ZHU!',
            render_to_string('emailTemplate.txt', {'message': message}),
            'no-reply@zhuartcc.org',
            [visiting_request.email],
            html_message=render_to_string('emailTemplate.html', {'message': message}),
        )

        visiting_request.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=401)


# Deletes visiting request with CID specified in POST
@require_POST
def reject_visiting_request(request):
    if 'staff' in request.session and request.session['staff']:
        visiting_request = Visit.objects.get(cid=request.POST['cid'])

        message = {
            'recipient_name': visiting_request.first_name,
            'text': 'Your visiting request has been rejected for the following reason: ' + request.POST['reason'],
            'sender': 'Marcus Miller',
            'sender_role': 'Air Traffic Manager'
        }
        send_mail(
            'Your ZHU Visting Request...',
            render_to_string('emailTemplate.txt', {'message': message}),
            'no-reply@zhuartcc.org',
            [visiting_request.email],
            html_message=render_to_string('emailTemplate.html', {'message': message}),
        )

        visiting_request.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=401)
