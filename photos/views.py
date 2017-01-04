#!/usr/local/bin/python
# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from qiniu import Auth, urlsafe_base64_encode
from django.utils import timezone

from .models import Photo
import random
import json
import re


# Create your views here.


QINIU_ACCESS_KEY = settings.QINIU_ACCESS_KEY
QINIU_SECRET_KEY = settings.QINIU_SECRET_KEY
QINIU_BUCKET_NAME = settings.QINIU_BUCKET_NAME
QINIU_BUCKET_DOMAIN = settings.QINIU_BUCKET_DOMAIN.rstrip('/')


def index(request):
    return index_page(request, 1)


def index_page(request, page_num):
    template = 'photos/index.html',
    imgs_per_page = 12
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

    background_pattern = "photos/images/patterns/pattern%d.png" % random.randint(1, 34)
    return render(
        request,
        template,
        {
            'photos': photos,
            'background_pattern': background_pattern,
            'qiniu_domain': 'http://%s/'% QINIU_BUCKET_DOMAIN,
        }
    )


@login_required
def upload_photo(request):
    return render(
        request,
        'photos/upload_photo.html',
        {
            'domain':     'http://%s/' % QINIU_BUCKET_DOMAIN,
            'media_root': settings.MEDIA_ROOT,
        }
    )

@login_required
def get_token(request):
    fops = (
        (
            'imageView2/2/w/1920|saveas/',
            '/photos/cache/images/$(x:uploader)/$(x:filename)-1920x.jpg'
        ),
        (
            'imageView2/2/w/512|saveas/',
            '/photos/cache/images/$(x:uploader)/$(x:filename)-512x.jpg'
        ),
    )
    persistent_ops = ';'.join(
        (x[0] + urlsafe_base64_encode('%s:%s%s' % (QINIU_BUCKET_NAME, settings.MEDIA_ROOT, x[1])) for x in fops)
    )
    print(persistent_ops)
    policy = {
        'persistentOps':       persistent_ops,
        'persistentPipeline':  'mytest',
        'persistentNotifyUrl': settings.QINIU_CALLBACK_DOMAIN + 'photos/callback/',
        'mimeLimit':           'image/jpeg',

    }
    qiniu_auth = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    upload_token = qiniu_auth.upload_token(QINIU_BUCKET_NAME, policy=policy)
    return JsonResponse(
        {
            'uptoken': upload_token,
        }
    )


@csrf_exempt
def callback(request):
    print(request.body)
    data = json.loads(request.body.decode("utf-8"))

    if data['code'] == 0 and data['inputBucket'] == QINIU_BUCKET_NAME:
        origin_img_key = data['inputKey']
        match = re.search(r'images/([\w.@+-]+)/.*\.jpg', origin_img_key)
        if match and len(match.groups()) > 0:
            uploader = User.objects.filter(username=match.group(1)).first()
            if uploader is None:
                return HttpResponse('hehe')
            cache_img_keys = {}
            for item in data['items']:
                if item['code'] == 0:
                    img_key = item['key']
                    match = re.search(r'-(\d+)x\.jpg', img_key)
                    if match and len(match.groups()) > 0:
                        img_width = match.group(1)
                        cache_img_keys[img_width] = img_key
            Photo.objects.create(
                title=origin_img_key,
                origin_image=origin_img_key,
                large_image=cache_img_keys['1920'],
                small_image=cache_img_keys['512'],
                uploader=uploader,
                date_upload=timezone.now()
            )
    return HttpResponse('haha')
