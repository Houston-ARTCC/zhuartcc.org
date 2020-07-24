from django import template


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
def as_range(int):
    return range(int)
