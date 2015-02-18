#!/usr/local/bin/python
# coding=utf-8

from django.conf.urls import patterns, url

from blog import views

urlpatterns = patterns('',
    url('^$', views.index, name="index"),
    url('^page/(?P<page_num>[\d]+)/$', views.index_page, name="index_page"),
    url('^category/(?P<slug>[-\w]+)/$', views.category_archive, name="category_archive_view"),
    url('^category/(?P<slug>[-\w]+)/page/(?P<page_num>[\d]+)/$', views.category_archive_page, name="category_archive_page_view"),
    url('^archive/(?P<year>[\d]+)/(?P<month>[\d]+)/$', views.date_archive, name="blog-date-archive"),
    url('^post/(?P<slug>[-\w]+)/$', views.single, name="single_post"),
    url('^write-post/$', views.write_post_view, name="write_post_view"),
    url(r'^edit-post/(?P<post_id>\d+)/$', views.edit_post_view, name='edit_post_view'),
    url(r'^accounts/login/$', views.login_view, name='login_view'),
    url(r'^accounts/logout/$', views.logout_view, name='logout_view'),
)
