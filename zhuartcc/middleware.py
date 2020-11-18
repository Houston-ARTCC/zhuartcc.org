from apps.user.models import User


class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_obj = User.objects.filter(cid=request.session.get('cid')).first()

        return self.get_response(request)
