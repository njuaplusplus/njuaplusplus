#!/usr/bin/env python
# coding=utf-8

from django.conf.urls import url

from atimelogger import views

urlpatterns = [
    url(r'^intervals/$', views.intervals, name="intervals"),
]
