#!/usr/local/bin/python
# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse

import hashlib, urllib2, json

def index(request):
    if request.method == 'GET':
        return HttpResponse(checkSignature(request))
def checkSignature(request):
    if request.method == 'GET':
        signature=request.GET.get('signature',None)
        timestamp=request.GET.get('timestamp',None)
        nonce=request.GET.get('nonce',None)
        echostr=request.GET.get('echostr',None)
    else:
        signature=request.POST.get('signature',None)
        timestamp=request.POST.get('timestamp',None)
        nonce=request.POST.get('nonce',None)
        echostr=request.POST.get('echostr',None)

    #这里的token我放在setting，可以根据自己需求修改
    token='njuaplusplus'

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return None
