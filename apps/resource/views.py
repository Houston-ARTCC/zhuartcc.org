from itertools import groupby

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Resource
from ..administration.models import ActionLog
from ..user.models import User
from zhuartcc.decorators import require_staff


def view_resources(request):
    resources = Resource.objects.all().order_by('category')
    resources_sorted = {k: list(g) for k, g in groupby(resources, key=lambda resource: resource.category)}
    categories = Resource._meta.get_field('category').choices
    return render(request, 'resources.html', {
        'page_title': 'Resources',
        'resources': resources_sorted,
        'categories': categories
    })


# Accepts form data and adds database entry
@require_staff
@require_POST
def add_resource(request):
    resource = Resource(
        path=request.FILES['file'],
        name=request.POST['name'],
        category=request.POST['category'],
    )
    resource.save()

    user = User.objects.get(cid=request.session.get('cid'))
    ActionLog(action=f'Resource "{resource.name}" created by {user.full_name}.').save()

    return redirect(reverse('resources'))


# Accepts form data and updates database entry
@require_staff
@require_POST
def edit_resource(request, resource_id):
    resource = Resource.objects.get(id=resource_id)
    resource.name = request.POST['name']
    resource.category = request.POST['category']
    if 'file' in request.FILES:
        resource.path = request.FILES['file']
    resource.save()

    user = User.objects.get(cid=request.session.get('cid'))
    ActionLog(action=f'Resource "{resource.name}" modified by {user.full_name}.').save()

    return redirect(reverse('resources'))


# Accepts resource ID and deletes database entry
@require_staff
@require_POST
def delete_resource(request, resource_id):
    resource = Resource.objects.get(id=resource_id)

    user = User.objects.get(cid=request.session.get('cid'))
    ActionLog(action=f'Resource "{resource.name}" deleted by {user.full_name}.').save()

    resource.delete()

    return HttpResponse(status=200)
