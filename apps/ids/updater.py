import ast
import os

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from .models import EnrouteFlight


# Schedules a task to update the flights every 5 minutes
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_pilots, 'interval', minutes=5)
    scheduler.start()


def get_pilots():
    data = requests.get('http://us.data.vatsim.net/vatsim-data.txt').text
    data_array = [line.split(':') for line in data.split('\n')]
    pilot_clients = {client[0]: client for client in data_array if len(client) == 42 and client[3] == 'PILOT'}

    for waypoint in ast.literal_eval(os.getenv('CROSSING_WAYPOINTS')):
        for pilot in pilot_clients.values():
            if waypoint in pilot[30]:
                if not EnrouteFlight.objects.filter(callsign=pilot[0]).exists():
                    EnrouteFlight(
                        callsign=pilot[0],
                        aircraft=pilot[9],
                        tas_filed=pilot[10],
                        tas_actual=pilot[8],
                        post_fix=waypoint,
                        altitude=pilot[7],
                        route=pilot[30],
                        transponder=pilot[17],
                        arrival=pilot[13][0] == 'K' or pilot[13][0] == 'C'
                    ).save()

    for flight in EnrouteFlight.objects.all():
        if flight.callsign in pilot_clients:
            flight.tas_actual = pilot_clients[flight.callsign][8]
            flight.altitude = pilot_clients[flight.callsign][7]
            flight.transponder = pilot_clients[flight.callsign][17]
            flight.coast = False
            flight.save()
        elif flight.discarded:
            flight.delete()
        else:
            flight.coast = True
            flight.save()
