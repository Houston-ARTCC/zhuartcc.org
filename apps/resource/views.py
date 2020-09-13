from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from zhuartcc.decorators import require_staff
from .models import Resource
from ..administration.models import ActionLog


def view_resources(request):
    # resources = Resource.objects.all().order_by('category')
    # resources_sorted = {k: list(g) for k, g in groupby(resources, key=lambda resource: resource.category)}
    # categories = Resource._meta.get_field('category').choices
    # return render(request, 'resources.html', {
    #     'page_title': 'Resources',
    #     'resources': resources_sorted,
    #     'categories': categories
    # })
    return redirect('https://sites.google.com/view/vzhuids/documents-controlling-files')


# Accepts form data and adds database entry
@require_staff
@require_POST
def add_resource(request):
    resource = Resource(
        path=request.FILES.get('file'),
        name=request.POST.get('name'),
        category=request.POST.get('category'),
    )
    resource.save()

    ActionLog(action=f'Resource "{resource}" created by {request.user_obj}.').save()

    return redirect(reverse('resources'))


# Accepts form data and updates database entry
@require_staff
@require_POST
def edit_resource(request, resource_id):
    resource = Resource.objects.get(id=resource_id)
    resource.name = request.POST.get('name')
    resource.category = request.POST.get('category')
    resource.path = request.FILES.get('file', resource.path)
    resource.save()

    ActionLog(action=f'Resource "{resource}" modified by {request.user_obj}.').save()

    return redirect(reverse('resources'))


# Accepts resource ID and deletes database entry
@require_staff
@require_POST
def delete_resource(request, resource_id):
    resource = Resource.objects.get(id=resource_id)

    ActionLog(action=f'Resource "{resource}" deleted by {request.user_obj}.').save()

    resource.delete()

    return HttpResponse(status=200)
