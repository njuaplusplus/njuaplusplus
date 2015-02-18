#!/usr/local/bin/python
# coding=utf-8

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    if user.groups.filter(name=group_name):
        return True
    else:
        return False
