#!/usr/bin/env python
# coding=utf-8

from django.shortcuts import render
from atimelogger import utils

# Create your views here.


def intervals(request):
    utils.init_types()
    intervals = utils.get_today_intervals()
    return render(
        request,
        'atimelogger/intervals.html',
        {
            'intervals' : intervals,
        }
    )
