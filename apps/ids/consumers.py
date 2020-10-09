from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from django.forms import model_to_dict

from .models import EnrouteFlight


class FlightConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)('ids', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)('ids', self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if action == 'update':
            flight_id = text_data_json['flight_id']
            flight_data = text_data_json['flight_data']

            new_data = {field['name']: field['value'] if field['value'] != '' else None for field in flight_data}
            flight = EnrouteFlight.objects.filter(id=flight_id)
            flight.update(**new_data)

            async_to_sync(self.channel_layer.group_send)(
                'ids',
                {
                    'type': 'update_flight',
                    'flight_id': flight_id,
                    'flight_data': model_to_dict(flight.first()),
                })
        elif action == 'delete':
            flight_id = text_data_json['flight_id']

            flight = EnrouteFlight.objects.get(id=flight_id)
            flight.discarded = True
            flight.save()

            async_to_sync(self.channel_layer.group_send)(
                'ids',
                {
                    'type': 'delete_flight',
                    'flight_id': flight_id,
                })

    def update_flight(self, event):
        self.send(text_data=json.dumps({
            'action': 'update',
            'flight_id': event['flight_id'],
            'flight_data': event['flight_data'],
        }))

    def new_flight(self, event):
        self.send(text_data=json.dumps({
            'action': 'new',
            'flight_id': event['flight_id'],
            'flight_data': event['flight_data'],
        }))

    def delete_flight(self, event):
        self.send(text_data=json.dumps({
            'action': 'delete',
            'flight_id': event['flight_id'],
        }))
