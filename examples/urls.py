"""njuaplusplus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('blog.urls', namespace='blog')),
    url(r'^photos/', include('photos.urls', namespace='photos')),
    url(r'^wechat/', include('wechat.urls', namespace='wechat')),
    url(r'^vbuilder/', include('vbuilder.urls', namespace='vbuilder')),
    url(r'^atimelogger/', include('atimelogger.urls', namespace='atimelogger')),
    # url(r'^comments/', include('fluent_comments.urls')),
    url(r'^comments/', include('mycomments.urls')),
    url(r'^admin/', admin.site.urls),
]

# Warning! Just use during development! Remove this for production use.
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
