import hmac
import requests
from base64 import urlsafe_b64encode, urlsafe_b64decode

from django.conf import settings
from django.shortcuts import redirect
from ..user.models import User


def login(request):
    # Checks if user has a token from VATUSA
    if request.GET.get('token'):
        jwk = settings.ULS_KEY

        algorithms = {
            'HS256': 'sha256',
            'HS384': 'sha384',
            'HS512': 'sha512',
        }

        raw_token = request.GET['token']
        token = raw_token.split('.')

        token_sig = token[2]

        jwk_sig = urlsafe_b64encode(
            hmac.digest(
                urlsafe_b64decode(jwk['k'] + '=='),
                f'{token[0]}.{token[1]}'.encode(),
                algorithms[jwk['alg']],
            ))[:-1].decode()

        if token_sig == jwk_sig:
            data = requests.get(f'https://login.vatusa.net/uls/v2/info?token={token[1]}').json()
            
            request.session['vatsim_data'] = data
            
            if User.objects.filter(cid=data['cid']).exists():
                user = User.objects.get(cid=data['cid'])
                request.session['guest'] = False
                request.session['staff'] = user.is_staff()
                request.session['mentor'] = user.is_mentor()
            else:
                request.session['guest'] = True
                request.session['staff'] = False
                request.session['mentor'] = False

    return redirect('/')


def logout(request):
    request.session.flush()

    return redirect('/')
