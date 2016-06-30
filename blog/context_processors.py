#!/usr/local/bin/python
# coding=utf-8


def debug_mode(request):
    from django.conf import settings
    return {'debug_mode' : settings.DEBUG}
