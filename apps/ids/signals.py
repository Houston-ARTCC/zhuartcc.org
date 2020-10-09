from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict

from .models import EnrouteFlight


@receiver(post_save, sender=EnrouteFlight)
def new_flight(sender, instance, created, **kwargs):
    if not created and instance.discarded:
        async_to_sync(get_channel_layer().group_send)(
            'ids',
            {
                'type': 'delete_flight',
                'flight_id': instance.id,
            })
    else:
        async_to_sync(get_channel_layer().group_send)(
            'ids',
            {
                'type': 'new_flight' if created else 'update_flight',
                'flight_id': instance.id,
                'flight_data': model_to_dict(instance),
            })