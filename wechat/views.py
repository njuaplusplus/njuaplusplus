#!/usr/local/bin/python
# coding=utf-8
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt

import hashlib

@csrf_exempt
def index(request):
    if request.method == 'GET':
        print('Wechat receive GET request')
        if checkSignature(request):
            echostr=request.GET.get('echostr',None)
            return HttpResponse(echostr)
    else:
        print('Wechat receive POST request')
        if checkSignature(request):
            import xml.etree.ElementTree as ET
            import time
            rawStr = smart_str(request.body)
            msg = paraseMsgXml(ET.fromstring(rawStr))
            toUser = msg.get('FromUserName','')
            fromUser = msg.get('ToUserName','')
            createTime = str(int(time.time()))
            #msgType = ''.join(msg.get('MsgType', '').split()) # QQ 居然返回的 text 前后有空白符..
            msgType = msg.get('MsgType', '')

            if msgType == 'event':
                event = msg['Event']
                if event == 'subscribe':
                    print('Event - subscribe')
                    content = '就接收小视频而已..'
                    context = { 'toUser': toUser, 'fromUser': fromUser, 'createTime': createTime, 'content': content}
                    return render_to_response('wechat/reply_text.xml', context, content_type="application/xml")
                elif event == 'unsubscribe':
                    content = '......'
                    context = { 'toUser': toUser, 'fromUser': fromUser, 'createTime': createTime, 'content': content}
                    return render_to_response('wechat/reply_text.xml', context, content_type="application/xml")
            elif msgType == 'text':
                print('Receive text')
                content = 'Contact me'
                context = { 'toUser': toUser, 'fromUser': fromUser, 'createTime': createTime, 'content': content}
                return render_to_response('wechat/reply_text.xml', context, content_type="application/xml")

    return HttpResponse('Hello World')

def checkSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)

    #这里的token我放在setting，可以根据自己需求修改
    token='njuaplusplus'

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        print('Check Signature Success')
        return True
    else:
        print('Check Signature Fail')
        return False

def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text).strip()
    return msg
