#!/usr/local/bin/python
# coding=utf-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^page/(?P<page_num>[\d]+)/$', views.index_page, name='index_page'),
    url(r'^upload/$', views.upload_photo, name='upload_photo'),
    url(r'^get-token/$', views.get_token, name='get_token'),
]