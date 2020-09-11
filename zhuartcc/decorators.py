from functools import wraps
from django.http import HttpResponse

from apps.user.models import User


def require_staff(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.session.get('staff'):
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('You must be a staff member to access this endpoint!', status=403)
    return inner


def require_mentor(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.session.get('mentor'):
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('You must be a mentor or instructor to access this endpoint!', status=403)
    return inner


def require_staff_or_mentor(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.session.get('staff') or request.session.get('mentor'):
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('You must be staff, mentor, or instructor to access this endpoint!', status=403)
    return inner


def require_session(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.session.get('vatsim_data'):
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('You must be logged in to access this endpoint!', status=403)
    return inner


def require_member(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.session.get('member'):
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('You must be an active Houston controller to access this endpoint!', status=403)
    return inner


def require_role(role_list):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if User.objects.get(cid=request.session.get('cid')).main_role in role_list:
                return func(request, *args, **kwargs)
            else:
                return HttpResponse('You lack the necessary role to access this endpoint!', status=403)
        return inner
    return decorator
