# coding=utf-8

from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^post/ajax/$', views.post_comment_ajax, name='comments-post-comment-ajax'),
    url(r'^comments/', include('django_comments.urls')),
]
