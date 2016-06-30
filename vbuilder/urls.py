#!/usr/bin/env python
# coding=utf-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^quiz/(?P<unit>[\d]+)/$', views.unit_quiz, name='unit_quiz'),
]
