import requests

from django.conf import settings
from django.shortcuts import render

from zhuartcc.decorators import require_staff


@require_staff
def view_admin_panel(request):
    return render(request, 'admin_panel.html', {'page_title': 'Admin Panel'})
