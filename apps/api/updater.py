import requests
from apscheduler.schedulers.background import BackgroundScheduler

from zhuartcc import settings


def update_scheduler():
    api_update()
    scheduler = BackgroundScheduler()
    scheduler.add_job(api_update, 'interval', minutes=5)
    scheduler.start()


def api_update():
    data = requests.get('http://us.data.vatsim.net/vatsim-data.txt').text.split('\n')
    data_array = [line.split(':') for line in data]

    all_clients = [line for line in data_array if len(line) == 42]
    atc_clients = [client for client in all_clients if client[3] == 'ATC']
    pilot_clients = [client for client in all_clients if client[3] == 'PILOT']

    pull_controllers(atc_clients)
    pull_pilots(pilot_clients)


def pull_controllers(data):
    for controller in data:
        callsign = controller[0].split('_')
        if callsign[0] in settings.POSITION_PREFIXES and callsign[-1] != 'OBS' and callsign[-1] != 'SUP':
            print(controller)


def pull_pilots(data):
    for pilot in data:
        pass
