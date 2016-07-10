#!/usr/bin/env python
# coding=utf-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^page/(?P<page_num>[\d]+)/$', views.index_page, name="index_page"),
    url(r'^category/$', views.category, name="category_view"),
    url(r'^category/(?P<slug>[-\w]+)/$', views.category_archive, name="category_archive_view"),
    url(r'^category/(?P<slug>[-\w]+)/page/(?P<page_num>[\d]+)/$', views.category_archive_page, name="category_archive_page_view"),
    url(r'^archive/(?P<year>[\d]+)/(?P<month>[\d]+)/$', views.date_archive, name="date_archive_view"),
    url(r'^archive/(?P<year>[\d]+)/(?P<month>[\d]+)/page/(?P<page_num>[\d]+)/$', views.date_archive_page, name="date_archive_page_view"),
    url(r'^post/(?P<slug>[-\w]+)/$', views.single, name="single_post"),
    url(r'^write-post/$', views.write_post_view, name="write_post_view"),
    url(r'^preview-post/$', views.preview_post_view, name="preview_post_view"),
    url(r'^edit-post/(?P<post_id>\d+)/$', views.edit_post_view, name='edit_post_view'),
    url(r'^search/$', views.search, name='search'),
    url(r'^accounts/login/$', views.login_view, name='login_view'),
    url(r'^accounts/logout/$', views.logout_view, name='logout_view'),
    # url(r'^ip/$', views.ip),
]
