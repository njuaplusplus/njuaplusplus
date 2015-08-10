#!/usr/local/bin/python
# coding=utf-8

from django.conf.urls import url

from photos import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^page/(?P<page_num>[\d]+)/$', views.index_page, name="index_page"),
]