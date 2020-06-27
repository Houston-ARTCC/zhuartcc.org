from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from datetime import datetime

from .models import Resource
from zhuartcc.decorators import require_staff


def view_resources(request):
    resources = {category: Resource.objects.filter(category=category) for category in settings.RESOURCE_CATEGORIES}
    return render(request, 'resources.html', {'resources': resources})


# Accepts form data and updates database entry
@require_staff
@require_POST
def edit_resource(request):
    resource = Resource.objects.get(id=request.POST['id'])
    resource.name = request.POST['name']
    resource.category = request.POST['category']
    if 'file' in request.FILES:
        resource.path = request.FILES['file']
    resource.updated = datetime.now()
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
        updated=datetime.now(),
    )
    resource.save()
    return redirect('/resources')


# Accepts resource ID and deletes database entry
@require_staff
@require_POST
def delete_resource(request):
    Resource.objects.get(id=request.POST['id']).delete()
    return redirect('/resources')
