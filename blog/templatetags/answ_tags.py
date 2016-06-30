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


@register.filter(name='add_str')
def add_str(s1, s2):
    """
    Concatenate s1 and s2
    """
    return str(s1).strip().replace('"', '-') + str(s2).strip().replace('"', '-')
