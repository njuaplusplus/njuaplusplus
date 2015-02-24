#!/usr/local/bin/python
# coding=utf-8
from django.shortcuts import render
import random

# Create your views here.

def index(request):
    return index_page(request, 1)

def index_page(request, page_num):
    holderjs_theme = random.choice(['sky', 'lava', 'social', 'vine', 'gray', 'industrial'])
    num_of_img = xrange(random.randrange(1,9))
    num_of_img = [ "%dx%d" % (random.randrange(200, 600), random.randrange(200, 600)) for i in num_of_img ]
    template = 'photos/index.html',
    if request.user_agent.is_mobile:
        template = 'photos/mobile/index.html'
    return render(
        request,
        template,
        {
            'holderjs_theme' : holderjs_theme,
            'num_of_img' : num_of_img,
            'next_page_num' : str(int(page_num) + 1),
        }
    )
