import ast
import os
from datetime import timedelta

import requests

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from ..administration.models import ActionLog
from ..user.models import User
from ..user.updater import assign_oper_init


def login(request):
    # Checks if user has a authorization code from VATSIM
    if request.GET.get('code'):
        resp = requests.post('https://auth.vatsim.net/oauth/token/', data={
            'grant_type': 'authorization_code',
            'client_id': os.getenv('VATSIM_CONNECT_ID'),
            'client_secret': os.getenv('VATSIM_CONNECT_SECRET'),
            'redirect_uri': os.getenv('VATSIM_CONNECT_REDIRECT'),
            'code': request.GET.get('code'),
        })

        if resp.status_code == 200:
            auth = resp.json()
        else:
            return

        if 'full_name' not in auth.get('scopes') or 'email' not in auth.get('scopes'):
            return

        data = requests.get('https://auth.vatsim.net/api/user/', headers={
            'Authorization': 'Bearer ' + auth.get('access_token'),
            'Accept': 'application/json'
        }).json().get('data')

        if data['vatsim']['division']['id'] == 'USA':
            resp = requests.get('https://api.vatusa.net/v2/user/' + data.get('cid'))

            if resp.status_code == 200:
                data['vatsim']['subdivision']['id'] = resp.json().get('facility')

        request.session['vatsim_data'] = data
        request.session['cid'] = data.get('cid')

        user = User.objects.filter(cid=data.get('cid')).first()
        if user:
            user.access_token = auth.get('access_token')
            user.refresh_token = auth.get('refresh_token')
            user.token_expires = timezone.now() + timedelta(seconds=auth.get('expires_in'))
            user.save()
        else:
            if data['vatsim']['subdivision']['id'] in ast.literal_eval(os.getenv('MAVP_ARTCCS')):
                new_user = User(
                    first_name=data['personal']['name_first'].capitalize(),
                    last_name=data['personal']['name_last'].capitalize(),
                    cid=int(data['cid']),
                    email=data['personal']['email'],
                    oper_init=assign_oper_init(data['personal']['name_first'][0], data['personal']['name_last'][0]),
                    rating=data['vatsim']['rating']['short'],
                    main_role='MC',
                    home_facility=data['vatsim']['subdivision'].get('id', data['vatsim']['division']['id']),
                )
                new_user.save()
                new_user.assign_initial_cert()

                ActionLog(action=f'User {new_user.full_name} was created by system.').save()

    return redirect(reverse('home'))


def logout(request):
    request.session.flush()

    return redirect(reverse('home'))
