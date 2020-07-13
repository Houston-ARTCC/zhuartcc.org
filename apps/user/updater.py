from apscheduler.schedulers.background import BackgroundScheduler
import requests

from .models import User
from django.conf import settings


# Schedules a task to update the roster every 30 minutes
def update_scheduler():
    update_roster()
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_roster, 'interval', minutes=30)
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
            new_user.assign_initial_cert()
            new_user.save()
        else:
            edit_user = User.objects.get(cid=user_details['cid'])
            edit_user.rating = user_details['rating_short']
            edit_user.save()

    # Cycles through visiting controllers separately since they are not on main roster
    for edit_user in User.objects.filter(main_role='VC'):
        user_details = requests.get(
            f'https://api.vatusa.net/v2/user/{edit_user.cid}',
            params={'apikey': settings.API_KEY},
        ).json()
        edit_user.rating = user_details['rating_short']
        edit_user.save()


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
