from apscheduler.schedulers.background import BackgroundScheduler
import requests

from .models import User
from django.utils import timezone
from django.conf import settings

from ..administration.models import ActionLog


# Schedules a task to update the roster every 30 minutes
def update_scheduler():
    update_roster()
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_roster, 'interval', minutes=30)
    scheduler.add_job(update_loa, 'cron', hour=0)
    scheduler.start()


# Pulls the roster from VATUSA API and adds new members to local database. Updates emails and ratings of existing users
def update_roster():
    roster = requests.get(
        'https://api.vatusa.net/v2/facility/ZHU/roster',
        params={'apikey': settings.API_KEY},
    ).json()
    del roster['testing']

    for user in roster:
        user_details = roster[user]
        if not User.objects.filter(cid=user_details['cid']).exists():
            new_user = User(
                first_name=user_details['fname'].capitalize(),
                last_name=user_details['lname'].capitalize(),
                cid=int(user_details['cid']),
                email=user_details['email'],
                oper_init=assign_oper_init(user_details['fname'][0], user_details['lname'][0]),
                rating=user_details['rating_short'],
                main_role='HC',
            )
            new_user.save()
            new_user.assign_initial_cert()
            ActionLog(action=f'User {new_user.full_name} was created by system.').save()
        else:
            edit_user = User.objects.get(cid=user_details['cid'])
            edit_user.rating = user_details['rating_short']

            # If user is rejoining the ARTCC after being marked inactive
            if edit_user.status == 2:
                edit_user.status = 1
                edit_user.email = user_details['email'],
                edit_user.oper_init = assign_oper_init(user_details['fname'][0], user_details['lname'][0])
                edit_user.main_role = 'HC'
                edit_user.save()
                edit_user.assign_initial_cert()
                ActionLog(action=f'User {edit_user.full_name} was set as active by system.').save()

            edit_user.save()

    # Removes people if they are no longer on the VATUSA roster
    cids = [roster[user]['cid'] for user in roster]
    for user in User.objects.filter(main_role='HC').exclude(status=2):
        if user.cid not in cids:
            user.status = 2
            user.save()
            ActionLog(action=f'User {user.full_name} was set as inactive by system.').save()

    # Cycles through visiting controllers separately since they are not on main roster
    for edit_user in User.objects.filter(main_role='VC'):
        user_details = requests.get(
            f'https://api.vatusa.net/v2/user/{edit_user.cid}',
            params={'apikey': settings.API_KEY},
        ).json()
        edit_user.rating = user_details['rating_short']
        edit_user.save()


def update_loa():
    for user in User.objects.filter(status=1):
        if user.loa_until is None or user.loa_until <= timezone.now().date():
            user.status = 0
            user.loa_last_month = True
            ActionLog(action=f'User {user.full_name} was set as active by system.').save()


# Decodes a string into a base 26 (A -> Z) integer
def base26decode(str_n):
    int_n = 0
    for pos, char in enumerate(str_n):
        int_n += (ord(char) - 65) * (26 ** (len(str_n) - pos - 1))
    return int_n


# Encodes a base 26 (A -> Z) integer into a string
def base26encode(int_n):
    str_n = ''
    while int_n > 25:
        q, r = divmod(int_n, 26)
        str_n = chr(r + 65) + str_n
        int_n = q
    str_n = chr(int_n + 65) + str_n
    return str_n


# Assigns operating initials to a user based on their initials. Cycles to the next letter if the initials are taken
def assign_oper_init(f_init, l_init):
    oi = (f_init + l_init).upper()
    while User.objects.filter(oper_init=oi).exists():
        new_oi = base26decode(oi) + 1
        oi = base26encode(new_oi if new_oi <= 675 else 0)
    if len(oi) < 2:
        oi = 'A' + oi
    return oi
