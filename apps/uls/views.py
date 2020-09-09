import ast
import os
import hmac
import requests
from base64 import urlsafe_b64encode, urlsafe_b64decode

from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.urls import reverse

from ..administration.models import ActionLog
from ..user.models import User
from ..user.updater import assign_oper_init


def login(request):
    # Checks if user has a token from VATUSA
    if request.GET.get('token'):
        raw_token = request.GET.get('token')
        token = raw_token.split('.')

        token_sig = token[2]

        jwk_sig = urlsafe_b64encode(
            hmac.digest(
                urlsafe_b64decode(os.getenv('ULS_K_VALUE') + '=='),
                f'{token[0]}.{token[1]}'.encode(),
                'sha256',
            ))[:-1].decode()

        if token_sig == jwk_sig:
            data = requests.get(f'https://login.vatusa.net/uls/v2/info?token={token[1]}').json()

            request.session['vatsim_data'] = data
            request.session['cid'] = data['cid']

            user_query = User.objects.filter(cid=data['cid'])

            if user_query.exists() and user_query[0].status != 2:
                user = User.objects.get(cid=data['cid'])
                request.session['member'] = True
                request.session['staff'] = user.is_staff
                request.session['mentor'] = user.is_mentor
            elif data['facility']['id'] in ast.literal_eval(os.getenv('MAVP_ARTCCS')):
                request.session['member'] = True

                new_user = User(
                    first_name=data['fname'].capitalize(),
                    last_name=data['lname'].capitalize(),
                    cid=int(data['cid']),
                    email=data['email'],
                    oper_init=assign_oper_init(data['fname'][0], data['lname'][0]),
                    rating=data['rating_short'],
                    main_role='MC',
                    home_facility=data['facility']['id'],
                )
                new_user.save()
                new_user.assign_initial_cert()

                ActionLog(action=f'User {new_user.full_name} was created by system.').save()
        else:
            return HttpResponseServerError()

    return redirect(reverse('home'))


def logout(request):
    request.session.flush()

    return redirect(reverse('home'))
