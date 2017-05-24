# coding=utf-8
from .models import Interval, ActivityType, ATimeLoggerProfile
from django.utils import timezone
import datetime
import requests

__author__ = 'Shengwei An'

BASE_URL = 'https://app.atimelogger.com'
API_URL = BASE_URL + '/api/v2'


def update_intervals():
    url = API_URL + '/intervals'
    profiles = ATimeLoggerProfile.objects.all()
    base_datetime = timezone.make_aware(datetime.datetime(1970, 1, 1), timezone=timezone.utc)
    for profile in profiles:
        get_or_refresh_token(profile)
        params = {
            'from':  int(profile.update_time.timestamp())-600,
            'limit': 10000,
            'order': 'asc',
        }
        res = requests.get(url, params=params, headers={'Authorization': 'bearer ' + profile.access_token})
        if res.status_code == 200:
            res = res.json()
            created = False
            for interval in res['intervals']:
                interval_type = ActivityType.objects.filter(profile=profile, guid=interval['type']['guid']).first()
                if interval_type is None:
                    update_types(profile)
                    interval_type = ActivityType.objects.filter(profile=profile,
                                                                guid=interval['type']['guid']).first()
                start_time = base_datetime + datetime.timedelta(seconds=interval['from'])
                created = Interval.objects.update_or_create(
                    {
                        'type':       interval_type,
                        'comment':    interval['comment'],
                        'start_time': start_time,
                        'end_time':   base_datetime + datetime.timedelta(seconds=interval['to']),
                    },
                    profile=profile,
                    guid=interval['guid']
                )[1] or created
            if created:
                profile.update_time = start_time
                profile.save()


def update_types(profile=None):
    """ Update the types. Now is only called from the update_intervals.

    Args:
        profile: if not None, just update this profile's types; o.t., update all's

    """
    url = API_URL + '/types'
    if profile is None:
        profiles = ATimeLoggerProfile.objects.all()
    else:
        profiles = [profile]
    for profile in profiles:
        params = {
            'limit': 10000,
        }
        res = requests.get(url, params=params, headers={'Authorization': 'bearer ' + profile.access_token})
        if res.status_code == 200:
            res = res.json()
            for t in res['types']:
                ActivityType.objects.update_or_create(
                    {
                        'color':    t['color'],
                        'name':     t['name'],
                        'image_id': t['imageId'],
                    },
                    profile=profile,
                    guid=t['guid']
                )


def get_or_refresh_token(profile=None):
    """

    Args:
        profile: if not None, just update this profile's token; o.t., update all's

    """
    profiles = [profile]
    if profile is None:
        profiles = ATimeLoggerProfile.objects.all()
    client_id = "androidClient"
    client_secret = "secret"
    for profile in profiles:
        if profile.token_time > timezone.now() - datetime.timedelta(hours=21):  # no need to refresh
            continue
        if not profile.access_token:  # get the new token
            url = BASE_URL + '/oauth/token?username=%s&password=%s&grant_type=password' % (profile.username, profile.password)
        else:  # refresh the token
            url = BASE_URL + '/oauth/token?refresh_token=%s&grant_type=refresh_token' % profile.refresh_token
        res = requests.post(url, auth=(client_id, client_secret))
        if res.status_code == 400:
            # refresh token has expired
            url = BASE_URL + '/oauth/token?username=%s&password=%s&grant_type=password' % (profile.username, profile.password)
            res = requests.post(url, auth=(client_id, client_secret))
        if res.status_code == 200:
            res = res.json()
            profile.access_token = res['access_token']
            profile.refresh_token = res['refresh_token']
            profile.token_time = timezone.now()
            profile.save()
