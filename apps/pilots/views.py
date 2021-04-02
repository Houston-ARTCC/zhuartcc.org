from itertools import groupby

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.administration.models import ActionLog
from apps.pilots.models import Scenery
from zhuartcc.decorators import require_staff


def view_artcc_map(request):
    return render(request, 'artcc_map.html', {'page_title': 'ARTCC Map'})


def view_scenery(request):
    sceneries = Scenery.objects.all().order_by('simulator')
    scenery_sorted = {k: list(g) for k, g in groupby(sceneries, key=lambda scenery: scenery.get_simulator_display())}
    simulators = Scenery._meta.get_field('simulator').choices
    return render(request, 'scenery.html', {
        'page_title': 'Scenery',
        'sceneries': scenery_sorted,
        'simulators': simulators
    })


@require_staff
@require_POST
def add_scenery(request):
    scenery = Scenery(
        name=request.POST.get('name'),
        simulator=request.POST.get('simulator'),
        link=request.POST.get('link'),
        payware=True if 'payware' in request.POST else False
    )
    scenery.save()

    ActionLog(action=f'Scenery "{scenery.name}" created by {request.user_obj}.').save()

    return redirect(reverse('scenery'))


@require_staff
@require_POST
def edit_scenery(request, scenery_id):
    scenery = Scenery.objects.get(id=scenery_id)
    scenery.name = request.POST.get('name')
    scenery.simulator = request.POST.get('simulator')
    scenery.link = request.POST.get('link')
    scenery.payware = True if 'payware' in request.POST else False
    scenery.save()

    ActionLog(action=f'Scenery "{scenery.name}" modified by {request.user_obj}.').save()

    return redirect(reverse('scenery'))


@require_staff
@require_POST
def delete_scenery(request, scenery_id):
    scenery = Scenery.objects.get(id=scenery_id)

    ActionLog(action=f'Scenery "{scenery.name}" deleted by {request.user_obj}.').save()

    scenery.delete()

    return HttpResponse(status=200)
