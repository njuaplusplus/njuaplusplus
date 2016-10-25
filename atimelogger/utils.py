#!/usr/bin/env python
# coding=utf-8

import datetime
import requests
from requests.auth import HTTPBasicAuth
import pytz
from django.conf import settings

types = {}
activites = {}


class Type:
    def __init__(self, guid, name):
        self.guid = guid
        self.name = name

    def __str__(self):
        return '%s %s' % (self.name, self.guid)

    def __unicode__(self):
        return '%s %s' % (self.name, self.guid)


class Activity:
    def __init__(self, guid):
        self.guid = guid


class Interval:
    def __init__(self, guid, type, start, end):
        """

        :param guid:
        :param type:
        :param start:
        :param end:
        :return:
        """
        self.guid = guid
        self.type = type
        self.start = start
        self.end = end

    def __str__(self):
        return '%s from %s to %s %s' % (self.guid, self.start, self.end, self.type)

    def __unicode__(self):
        return '%s from %s to %s %s' % (self.guid, self.start, self.end, str(self.type))


def init_types():
    auth = HTTPBasicAuth(settings.ATIMELOGGER['username'], settings.ATIMELOGGER['password'])
    url = 'https://app.atimelogger.com/api/v2/types'
    result = get_json(url, auth)
    if result:
        for t in result['types']:
            guid = t['guid']
            if guid not in types:
                types[guid] = Type(guid=guid, name=t['name'])

    # for t in types.values():
    #     print(unicode(t))


def get_today_intervals():
    today = datetime.date.today()
    today_datetime = datetime.datetime(year=today.year, month=today.month, day=today.day)
    start = int((today_datetime - datetime.datetime(1970, 1, 1)).total_seconds())
    params = {
        'from': start,
    }
    auth = HTTPBasicAuth(settings.ATIMELOGGER['username'], settings.ATIMELOGGER['password'])
    url = 'https://app.atimelogger.com/api/v2/intervals'
    result = get_json(url, auth, params)
    intervals = []
    if result:
        for interval in result['intervals']:
            interval_type = types[interval['type']['guid']]
            intervals.append(Interval(
                    guid=interval['guid'],
                    type=interval_type,
                    # start=pytz.timezone("Asia/Shanghai").localize(
                    #         datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=interval['from']),
                    #         is_dst=False
                    # ),
                    # end=pytz.timezone("Asia/Shanghai").localize(
                    #         datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=interval['to']),
                    #         is_dst=False
                    # )
                    start=pytz.timezone('utc').localize(
                            datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=interval['from']),
                            is_dst=False
                    ),
                    end=pytz.timezone('utc').localize(
                            datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=interval['to']),
                            is_dst=False
                    )
            ))
    for interval in intervals:
        print((str(interval)))
    return intervals


def get_json(url, auth, params=None):
    r = requests.get(url, auth=auth, params=params)
    if r.status_code == 200:
        print('get_json Success!')
        return r.json()
    return None


if __name__ == '__main__':
    init_types()
    get_today_intervals()
