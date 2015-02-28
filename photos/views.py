#!/usr/local/bin/python
# coding=utf-8
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from photos.models import Photo

# Create your views here.

def index(request):
    return index_page(request, 1)

def index_page(request, page_num):
    template = 'photos/index.html',
    imgs_per_page = 20
    if request.user_agent.is_mobile:
        template = 'photos/mobile/index.html'
        imgs_per_page = 6

    photo_queryset = Photo.objects.all().order_by('-date_upload')
    paginator = Paginator(photo_queryset, imgs_per_page)
    try:
        photos = paginator.page(page_num)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        photos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        # photos = paginator.page(paginator.num_pages)
        photos = None
    return render(
        request,
        template,
        {
            'photos' : photos,
        }
    )
