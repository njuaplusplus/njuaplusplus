#!/usr/local/bin/python
# coding=utf-8

from django.conf.urls import patterns, url

from photos import views

urlpatterns = patterns('',
    url('^$', views.index, name="index"),
    url('^page/(?P<page_num>[\d]+)/$', views.index_page, name="index_page"),
)
