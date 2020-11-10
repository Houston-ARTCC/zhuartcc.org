from django import template

from apps.event.models import EventPosition
from apps.user.models import User

register = template.Library()


@register.filter
def duration(timedelta):
    if timedelta is not None:
        total_seconds = int(timedelta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f'{hours}h {minutes}m'
    else:
        return None


@register.filter
def duration_minutes(timedelta):
    return timedelta.total_seconds() // 60


@register.filter
def as_range(int):
    return range(int)


@register.filter
def get_value_from_dict(dict, key):
    return dict[str(key)] if str(key) in dict else None


@register.filter
def id_from_user(queryset, user_id):
    for object in queryset:
        if object.user_id == user_id:
            return object.id
    return None


@register.filter
def to_iso_format(dt):
    return dt.isoformat().replace('+00:00', '')


@register.filter
def is_cic_eligible(position, user):
    if isinstance(position, EventPosition) and isinstance(user, User):
        return position.is_cic_eligible(user)
