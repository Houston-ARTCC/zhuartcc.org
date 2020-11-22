import os
import pytz
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from zhuartcc.overrides import send_mail
from .models import Event, EventPosition, PositionPreset, EventPositionRequest
from ..administration.models import ActionLog
from ..training.models import TrainingSession
from ..user.models import User
from zhuartcc.decorators import require_staff, require_member, require_session


@require_session
def view_event_score(request, cid=None):
    if cid and not request.user_obj.is_staff and cid != request.user_obj.cid:
        return HttpResponse(status=403)

    return render(request, 'event_score.html', {
        'page_title': 'Event Score History',
        'user': User.objects.get(cid=cid) if cid else request.user_obj,
    })


def view_all_events(request):
    return render(request, 'events.html', {
        'page_title': 'Events',
        'events': Event.objects.filter(end__gte=timezone.now()).order_by('start'),
    })


def view_archived_events(request):
    return render(request, 'archived_events.html', {
        'page_title': 'Archived Events',
        'events': Event.objects.filter(start__lte=timezone.now()).order_by('-start'),
    })


def view_event(request, event_id):
    event = Event.objects.get(id=event_id)
    user = request.user_obj
    if event.hidden and user.is_staff or not event.hidden:
        positions = {'center': [], 'tracon': [], 'cab': []}
        for position in event.positions.all():
            positions[position.category] += [position]
        return render(request, 'view_event.html', {
            'page_title': event.name,
            'event': event,
            'positions': positions,
            'available': {k: len(list(filter(lambda pos: pos.user is None, positions[k]))) for k in positions},
            'user': user,
            'allowed_to_signup': user and not user.prevent_event_signup and event.end >= timezone.now(),
            'time_now': timezone.now(),
        })
    else:
        return HttpResponse(status=403)


def send_event_webhook(request, event):
        format = '%b %d, %Y @ %H%Mz'
        url = request.build_absolute_uri(reverse("event", args=[event.id]))
        webhook = DiscordWebhook(url=os.getenv('EVENTS_WEBHOOK_URL'))
        embed = DiscordEmbed(
            title=f':calendar: {event.name}',
            description=event.description + f'\n**[Sign up for the event here!]({url})**',
            color=2966946
        )
        embed.add_embed_field(
            name='Start & End',
            value=f'{event.start.strftime(format)} - {event.end.strftime(format)}',
            inline=False,
        )
        embed.add_embed_field(
            name='Presented by',
            value=event.host,
        )
        embed.set_image(url=request.build_absolute_uri(event.banner))
        webhook.add_embed(embed)
        webhook.execute()


@require_staff
def add_event(request):
    if request.method == 'POST':
        event = Event(
            name=request.POST.get('name'),
            start=pytz.utc.localize(datetime.fromisoformat(request.POST.get('start'))),
            end=pytz.utc.localize(datetime.fromisoformat(request.POST.get('end'))),
            banner=request.POST.get('banner'),
            host=request.POST.get('host'),
            description=request.POST.get('description', None),
            hidden=True if 'hidden' in request.POST else False,
        )
        event.save()
        if not event.hidden:
            send_event_webhook(request, event)

        ActionLog(action=f'Event "{event.name}" created by {request.user_obj}.').save()

        if request.POST.get('preset'):
            PositionPreset.objects.get(id=request.POST.get('preset')).add_to_event(event)

        return redirect(reverse('event', args=[event.id]))
    else:
        return render(request, 'new_event.html', {
            'page_title': 'New Event',
            'position_presets': PositionPreset.objects.all(),
            'events': Event.objects.all(),
            'sessions': TrainingSession.objects.all(),
        })


@require_staff
def edit_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if event.end >= timezone.now():
        if request.method == 'POST':
            event.name = request.POST.get('name')
            event.start = pytz.utc.localize(datetime.fromisoformat(request.POST.get('start')))
            event.end = pytz.utc.localize(datetime.fromisoformat(request.POST.get('end')))
            event.banner = request.POST.get('banner')
            event.host = request.POST.get('host')
            event.description = request.POST.get('description', None)
            if event.hidden and 'hidden' not in request.POST:
                send_event_webhook(request, event)
            event.hidden = True if 'hidden' in request.POST else False
            event.save()

            ActionLog(action=f'Event "{event.name}" modified by {request.user_obj}.').save()

            return redirect(reverse('event', args=[event.id]))
        else:
            positions = {'center': [], 'tracon': [], 'cab': []}
            for position in event.positions.all():
                positions[position.category] += [position]
            return render(request, 'edit_event.html', {
                'page_title': f'Editing {event.name}',
                'positions': positions,
                'controllers': User.objects.exclude(status=2).order_by('first_name'),
                'event': event
            })
    else:
        return HttpResponse(status=403)


@require_staff
@require_POST
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)

    ActionLog(action=f'Event "{event.name}" deleted by {request.user_obj}.').save()

    event.delete()

    return redirect(reverse('events'))


@require_staff
@require_POST
def add_position(request, event_id):
    EventPosition(
        event=Event.objects.get(id=event_id),
        name=request.POST.get('position'),
    ).save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def delete_position(request, position_id):
    EventPosition.objects.get(id=position_id).delete()

    return HttpResponse(status=200)


@require_member
@require_POST
@csrf_exempt
def request_position(request, position_id):
    position = EventPosition.objects.get(id=position_id)

    if request.user_obj.prevent_event_signup:
        return HttpResponse('You are not allowed to sign up for events!', status=403)

    if position.is_cic and not position.is_cic_eligible(request.user_obj):
        return HttpResponse('You are not eligible for this CIC position!', status=403)

    if EventPositionRequest.objects.filter(user=request.user_obj).filter(position_id=position_id).exists():
        return HttpResponse('You already requested this position!', status=403)

    EventPositionRequest(
        position=position,
        user=request.user_obj,
    ).save()

    return HttpResponse(status=200)


@require_member
@require_POST
@csrf_exempt
def unrequest_position(request, request_id):
    position_request = EventPositionRequest.objects.get(id=request_id)
    if position_request.user.id == request.user_obj.id:
        position_request.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse('You are unauthorized to complete this action!', status=401)


@require_staff
@require_POST
def assign_position(request, request_id):
    position_request = EventPositionRequest.objects.get(id=request_id)
    if position_request.position.user != position_request.user:
        if position_request.position.user is not None:
            send_mail(
                'Event Position Unassigned',
                render_to_string('emails/position_unassigned.html', {'position': position_request.position}),
                os.getenv('NO_REPLY'),
                [position_request.position.user.email],
            )
        position_request.assign()

        send_mail(
            'Event Position Assigned!',
            render_to_string('emails/position_assigned.html', {'position': position_request.position}),
            os.getenv('NO_REPLY'),
            [position_request.user.email],
        )

        position_request.user.event_requests.filter(position__event=position_request.position.event).delete()

        return HttpResponse(status=200)
    return HttpResponse('Position is already assigned to selected user.', status=403)


@require_staff
@require_POST
def unassign_position(request, position_id):
    position = EventPosition.objects.get(id=position_id)

    send_mail(
        'Event Position Unassigned',
        render_to_string('emails/position_unassigned.html', {'position': position}),
        os.getenv('NO_REPLY'),
        [position.user.email],
    )

    position.user = None
    position.save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def manual_assign(request, position_id, cid):
    position = EventPosition.objects.get(id=position_id)
    controller = User.objects.get(cid=cid)

    if position.user != controller:
        if position.user is not None:
            send_mail(
                'Event Position Unassigned',
                render_to_string('emails/position_unassigned.html', {'position': position}),
                os.getenv('NO_REPLY'),
                [position.user.email],
            )

        position.user = controller
        position.save()

        send_mail(
            'Event Position Assigned!',
            render_to_string('emails/position_assigned.html', {'position': position}),
            os.getenv('NO_REPLY'),
            [controller.email],
        )

        return HttpResponse(status=200)
    return HttpResponse('Position is already assigned to selected user.', status=403)


@require_staff
@require_POST
def embed_positions(request, event_id):
    event = Event.objects.get(id=event_id)
    url = request.build_absolute_uri(reverse("event", args=[event.id]))
    webhook = DiscordWebhook(url=os.getenv('EVENTS_WEBHOOK_URL'))
    embed = DiscordEmbed(
        title=f':calendar: "{event.name}"',
        description=f'Below are the event position assignments as they currently stand. Assignments are subject to '
                    f'change on the day of the event so you should always double check the event page before logging '
                    f'on to control.\n**[View the event page here!]({url})**',
        color=2966946
    )
    for position in event.positions.all():
        embed.add_embed_field(
            name=position.name,
            value=position.user.full_name if position.user is not None else 'Unassigned',
        )
    embed.set_image(url=request.build_absolute_uri(event.banner))
    webhook.add_embed(embed)
    webhook.execute()

    return HttpResponse(status=200)


@require_staff
def view_presets(request):
    return render(request, 'presets.html', {
        'page_title': 'Position Presets',
        'position_presets': PositionPreset.objects.all(),
    })


@require_staff
@require_POST
def add_preset(request):
    preset = PositionPreset(
        name=request.POST.get('name')
    )
    preset.save()

    ActionLog(action=f'Position preset "{preset}" created by {request.user_obj}.').save()

    return redirect(reverse('presets'))


@require_staff
@require_POST
def edit_preset(request, preset_id):
    preset = PositionPreset.objects.get(id=preset_id)
    preset.positions_json = request.POST.get('positions')
    preset.save()

    ActionLog(action=f'Position preset "{preset}" modified by {request.user_obj}.').save()

    return HttpResponse(status=200)


@require_staff
@require_POST
def delete_preset(request, preset_id):
    preset = PositionPreset.objects.get(id=preset_id)

    ActionLog(action=f'Position preset "{preset}" deleted by {request.user_obj}.').save()

    preset.delete()

    return HttpResponse(status=200)
