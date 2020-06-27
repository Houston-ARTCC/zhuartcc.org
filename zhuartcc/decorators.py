from functools import wraps
from django.http import HttpResponse


# View decorator that checks session to see if user is staff
def require_staff(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session['staff']:
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be a staff member to complete this action!', status=401)
    return wrap


# View decorator that checks session to see if user is a mentor
def require_mentor(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session['mentor']:
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be a training staff member to complete this action!', status=401)
    return wrap


# View decorator that checks session to see if user is logged in
def require_logged_in(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if 'vatsim_data' in request.session:
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be logged in to complete this action!', status=401)
    return wrap


# View decorator that checks session to see if user is a member of the ARTCC
def require_member(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.session['guest']:
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be a member to complete this action!', status=401)
    return wrap
