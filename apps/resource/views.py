from itertools import groupby

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Resource
from ..administration.models import ActionLog
from ..user.models import User
from zhuartcc.decorators import require_staff


def view_resources(request):
    resources = Resource.objects.all().order_by('category')
    resources_sorted = {k: list(g) for k, g in groupby(resources, key=lambda resource: resource.category)}
    return render(request, 'resources.html', {'page_title': 'Resources', 'resources': resources_sorted})


# Accepts form data and updates database entry
@require_staff
@require_POST
def edit_resource(request):
    resource = Resource.objects.get(id=request.POST['id'])
    resource.name = request.POST['name']
    resource.category = request.POST['category']
    if 'file' in request.FILES:
        resource.path = request.FILES['file']
    resource.updated = timezone.now()

    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Resource "{resource.name}" edited by {user.return_full_name()}.').save()

    resource.save()
    return redirect('/resources')


# Accepts form data and adds database entry
@require_staff
@require_POST
def add_resource(request):
    resource = Resource(
        path=request.FILES['file'],
        name=request.POST['name'],
        category=request.POST['category'],
        updated=timezone.now(),
    )
    resource.save()
    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Resource "{resource.name}" created by {user.return_full_name()}.').save()
    return redirect('/resources')


# Accepts resource ID and deletes database entry
@require_staff
@require_POST
def delete_resource(request):
    resource = Resource.objects.get(id=request.POST['id'])
    user = User.objects.get(cid=request.session['cid'])
    ActionLog(action=f'Resource "{resource.name}" deleted by {user.return_full_name()}.').save()
    resource.delete()
    return redirect('/resources')
