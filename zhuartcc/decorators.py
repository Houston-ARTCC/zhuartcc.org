from functools import wraps
from django.http import HttpResponse


def require_staff(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.get('staff'):
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be a staff member to access this endpoint!', status=403)
    return wrap


def require_mentor(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.get('mentor'):
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be a mentor or instructor to access this endpoint!', status=403)
    return wrap


def require_logged_in(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.get('vatsim-data'):
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be logged in to access this endpoint!', status=403)
    return wrap


def require_member(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.session.get('guest'):
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('You must be an active Houston controller to access this endpoint!', status=403)
    return wrap
