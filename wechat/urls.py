#!/usr/local/bin/python
# coding=utf-8

from django.conf.urls import url

from wechat import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]