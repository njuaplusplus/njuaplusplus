#!/usr/local/bin/python
# coding=utf-8

from photos.models import *
from django.contrib.auth.models import User
from django.core.files import File
import os

def add_photos(root_dir=r'/Users/aplusplus/Downloads/cphotos/'):
    img_extensions = {".jpg", ".png", ".gif"}
    for f in os.listdir(root_dir):
        filename = os.path.join(root_dir, f)
        if os.path.isfile(filename):
            if not f[0] == '.' and any(f.endswith(ext) for ext in img_extensions):
                # print hymn.hymn_name, f
                with open(filename) as inFile:
                    photo = Photo(title=f, uploader=User.objects.get(username='aplusplus'))
                    photo.large_image.save(f, File(inFile))

