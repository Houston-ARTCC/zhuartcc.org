import threading
from functools import wraps

from django.core.exceptions import PermissionDenied


def require_member(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user_obj:
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied('You must be an active Houston controller to access this endpoint!')
    return inner


def require_session(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user_obj and request.session.get('vatsim_data'):
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied('You must be logged in to access this endpoint!')
    return inner


def require_staff(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user_obj and request.user_obj.is_staff:
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied('You must be a staff member to access this endpoint!')
    return inner


def require_mentor(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user_obj and request.user_obj.is_mentor:
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied('You must be a mentor or instructor to access this endpoint!')
    return inner


def require_staff_or_mentor(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user_obj and (request.user_obj.is_staff or request.user_obj.is_mentor):
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied('You must be staff, mentor, or instructor to access this endpoint!')
    return inner


def require_role(role_list):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.user_obj and request.user_obj.main_role in role_list:
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied('You lack the necessary role to access this endpoint!')
        return inner
    return decorator


def run_async(func):
    @wraps(func)
    def inner(*args, **kwargs):
        threading.Thread(target=func, args=args).start()
    return inner
