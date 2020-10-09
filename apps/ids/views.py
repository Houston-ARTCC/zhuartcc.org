import ast
import os
import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from zhuartcc.decorators import require_member
from .models import EnrouteFlight


@require_member
def view_enroute_strips(request):
    flights = EnrouteFlight.objects.exclude(discarded=True)
    sorted_flights = {
        waypoint: flights.filter(post_fix=waypoint) for waypoint in ast.literal_eval(os.getenv('CROSSING_WAYPOINTS'))
    }
    return render(request, 'enroute_strips.html', {
        'all_flights': sorted_flights
    })


@require_POST
@require_member
def add_flight(request):
    data = requests.get('http://us.data.vatsim.net/vatsim-data.txt').text
    data_array = [line.split(':') for line in data.split('\n')]
    pilot_clients = {client[0]: client for client in data_array if len(client) == 42 and client[3] == 'PILOT'}
    if request.POST['add-callsign'] in pilot_clients:
        flight_query = EnrouteFlight.objects.filter(callsign=request.POST['add-callsign'])
        if not flight_query.exists():
            pilot = pilot_clients[request.POST['add-callsign']]
            EnrouteFlight(
                callsign=pilot[0],
                aircraft=pilot[9],
                tas_filed=pilot[10],
                tas_actual=pilot[8],
                post_fix=request.POST['add-crossing'],
                altitude=pilot[7],
                route=pilot[30],
                transponder=pilot[17],
                arrival=pilot[13][0] == 'K' or pilot[13][0] == 'C'
            ).save()
            return HttpResponse(status=200)
        elif flight_query.first().discarded:
            flight = flight_query.first()
            flight.post_fix = request.POST['add-crossing']
            flight.discarded = False
            flight.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse('That flight strip already exists!', status=400)
    else:
        return HttpResponse('A flight with that callsign was not found!', status=400)
