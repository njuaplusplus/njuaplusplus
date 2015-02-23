#!/usr/local/bin/python
# coding=utf-8
from django.shortcuts import render

# Create your views here.

def index(request):
    return index_page(request, 1)

def index_page(request, page_num):
    return render(
        request,
        'photos/index.html',
        {
            'next_page_num' : str(int(page_num) + 1),
        }
    )
