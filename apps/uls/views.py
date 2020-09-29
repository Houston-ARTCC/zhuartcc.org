import ast
import os
import hmac
import urllib.parse

import requests
from base64 import urlsafe_b64encode, urlsafe_b64decode

from django.http import HttpResponse
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
            if not User.objects.filter(cid=data['cid']).exists():
                if data['facility']['id'] in ast.literal_eval(os.getenv('MAVP_ARTCCS')):
                    new_user = User(
                        first_name=data['firstname'].capitalize(),
                        last_name=data['lastname'].capitalize(),
                        cid=int(data['cid']),
                        email=data['email'],
                        oper_init=assign_oper_init(data['firstname'][0], data['lastname'][0]),
                        rating=data['rating'],
                        main_role='MC',
                        home_facility=data['facility']['id'],
                    )
                    new_user.save()
                    new_user.assign_initial_cert()

                    ActionLog(action=f'User {new_user.full_name} was created by system.').save()
        else:
            return HttpResponse('Something was wrong with the token we got from VATUSA!', status=500)

    return redirect(reverse('home'))


def dev_login(request):
    if not request.GET:
        return redirect(f'https://auth.vatsim.net/oauth/authorize?client_id={os.getenv("VATSIM_CLIENT")}'
                        f'&redirect_uri={urllib.parse.quote(request.build_absolute_uri(reverse("dev_login")), safe="")}'
                        f'&response_type=code&scope=full_name+vatsim_details+email')
    req = requests.post('https://auth.vatsim.net/oauth/token', data={
        'grant_type': 'authorization_code',
        'client_id': os.getenv('VATSIM_CLIENT'),
        'client_secret': os.getenv('VATSIM_SECRET'),
        'redirect_uri': 'http://localhost/devlogin/',
        'code': request.GET.get('code'),
    })
    data = requests.get('https://auth.vatsim.net/api/user', headers={
        'Authorization': 'Bearer ' + req.json()['access_token']
    })
    return HttpResponse(data.json(), status=400)


def logout(request):
    request.session.flush()

    return redirect(reverse('home'))
