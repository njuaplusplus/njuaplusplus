#!/usr/bin/env python
# coding=utf-8

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth
from django.contrib.auth.models import User
from blog.models import Category, Article, ArticleForm, User_Profile
import calendar, datetime
from django.conf import settings # use settings
import datetime
import jwt
import random
from duoshuo import DuoshuoAPI

def index(request):
    return index_page(request, 1)

def index_page(request, page_num):
    """The news index"""
    # archive_dates = Article.objects.datetimes('date_publish','month', order='DESC')
    # categories = Category.objects.all()

    article_queryset = Article.objects.all()
    paginator = Paginator(article_queryset, 5)

    try:
        articles = paginator.page(page_num)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/index.html",
        {
            "articles" : articles,
            # "archive_dates" : archive_dates,
            # "categories" : categories
        }
    )

def single(request, slug) :
    """A single article"""
    article = get_object_or_404(Article, slug=slug)
    # archive_dates = Article.objects.datetimes('date_publish','month', order='DESC')
    # categories = Category.objects.all()
    return render(
        request,
        "blog/post.html",
        {
            "article" : article,
            # "archive_dates" : archive_dates,
            # "categories" : categories
        }
    )

def date_archive(request, year, month) :
    """The blog date archive"""
    # this archive pages dates
    year = int(year)
    month = int(month)
    month_range = calendar.monthrange(year, month)
    start = datetime.datetime(year=year, month=month, day=1)#.replace(tzinfo=utc)
    end = datetime.datetime(year=year, month=month, day=month_range[1])#.replace(tzinfo=utc)
    archive_dates = Article.objects.datetimes('date_publish','month', order='DESC')
    categories = Category.objects.all()

    # Pagination
    page = request.GET.get('page')
    article_queryset = Article.objects.filter(date_publish__range=(start.date(), end.date()))
    paginator = Paginator(article_queryset, 5)

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/article/date_archive.html",
        {
            "start" : start,
            "end" : end,
            "articles" : articles,
            "archive_dates" : archive_dates,
            "categories" : categories
        }
    )

def category_archive(request, slug):
    return category_archive_page(request, slug, 1)

def category_archive_page(request, slug, page_num):
    # archive_dates = Article.objects.datetimes('date_publish','month', order='DESC')
    # categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)

    # Pagination
    article_queryset = Article.objects.filter(categories=category)
    paginator = Paginator(article_queryset, 5)

    try:
        articles = paginator.page(page_num)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles = paginator.page(paginator.num_pages)
    return render(
        request,
        "blog/category_archive.html",
        {
            "articles" : articles,
            # "archive_dates" : archive_dates,
            # "categories" : categories,
            "category" : category
        }
    )

@login_required
def write_post_view(request):
    if not request.user.groups.filter(name='authors'):
        return render(request, 'blog/error.html', {'error': '权限不够', 'message': '权限不够, 请联系管理员!', })
    if request.method == 'POST':
        article_form = ArticleForm(request.POST, request.FILES)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.author = request.user
            print 'In write_post_view', article.id
            article.save()
            article_form.save_m2m()
            return HttpResponseRedirect(reverse('blog:single_post', args=(article.slug,)))
    else:
        article_form = ArticleForm()
    return render(request, 'blog/write_post.html', {'article_form': article_form, })

@login_required
def edit_post_view(request, post_id):
    article = get_object_or_404(Article, pk=post_id)
    if not request.user.groups.filter(name='admins') and not (request.user.groups.filter(name='authors') and request.user == article.author):
        return render(request, 'blog/error.html', {'error': '权限不够', 'message': '权限不够, 请联系管理员!', })
    if request.method == 'POST':
        article_form = ArticleForm(request.POST, request.FILES, instance=article)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.is_markuped = False
            article.save()
            article_form.save_m2m()
            return HttpResponseRedirect(reverse('blog:single_post', args=(article.slug,)))
    else:
        article_form = ArticleForm(instance=article)
    return render(request, 'blog/write_post.html', {'article_form': article_form, })

def decide_next_url(next_url):
    if next_url is None or len(next_url) == 0 or next_url == reverse('blog:login_view'):
        next_url = reverse('blog:index')
    return next_url

def login_view(request):
    if request.user is not None and request.user.is_active:
        response = HttpResponseRedirect(reverse('blog:index'))
        return set_jwt_and_response(request.user, response)
    if request.method == 'POST': # 本地用户登录
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        next_url = decide_next_url(request.POST.get('next', ''))
        if user is not None and user.is_active:
            # Correct password, and the user is marked 'active'
            auth.login(request, user)
            response = HttpResponseRedirect(next_url)
            return set_jwt_and_response(request.user, response)
        else:
            # Show an error page
            return render(request, 'blog/login.html', {'next': next_url})
    else: # GET method
        code = request.GET.get('code', '')
        next_url = decide_next_url(request.GET.get('next', ''))
        if len(code) > 0: # 多说登录
            api = DuoshuoAPI(settings.DUOSHUO_SHORT_NAME, settings.DUOSHUO_SECRET)
            response = api.get_token(code=code)
            print 'api.get_token %s' % code
            print response
            if response.has_key('user_key'): # 这个多说账号已经绑定过本地账户了
                user = User.objects.get(pk=int(response['user_key']))
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
                user_profile = User_Profile.objects.filter(user=user)
                if not user_profile: # 手动绑定了多说账号和本地账号, 但是本地没有对应的 user_profile
                    user_profile = User_Profile(user=user,duoshuo_id=int(response['user_id']), avatar=response['avatar_url'])
                    user_profile.save()
            else: # 这个多说账户还没有绑定
                access_token = response['access_token']
                user_profile = User_Profile.objects.filter(duoshuo_id=int(response['user_id']))
                if user_profile: #此多说账号在本站已经注册过了, 但是没有绑定, 则先绑定, 然后直接登录
                    user = user_profile.first().user
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth.login(request, user)
                else: # 此多说账号在本站未注册, 添加一个用户
                    print 'api.users.profile user_id %s' % response['user_id']
                    response = api.users.profile(user_id=response['user_id'])['response']
                    print response
                    username = 'duoshuo_%s' % response['user_id']
                    while User.objects.filter(username=username).count():
                        username = username + str(random.randrange(1,9)) #如果多说账号用户名和本站用户名重复，就加上随机数字
                    tmp_password = ''.join([random.choice('abcdefg&#%^*f') for i in range(8)]) #随机长度8字符做密码
                    new_user = User.objects.create_user(username=username, email='user@example.com', password=tmp_password, first_name=response['name']) #默认密码和邮箱，之后让用户修改
                    user_profile = User_Profile.objects.get_or_create(user=new_user)[0]
                    user_profile.duoshuo_id = int(response['user_id']) #把返回的多说ID存到profile
                    user_profile.avatar = response['avatar_url']
                    user_profile.save()

                    user = auth.authenticate(username=username, password=tmp_password)
                    auth.login(request, user)
                # SSO 同步多说账户
                sync_sso_duoshuo(access_token, request.user)
            response = HttpResponseRedirect(next_url)
            return set_jwt_and_response(request.user, response)
        # absolute_next_url = request.build_absolute_uri(next_url)
        sso_login_url = '%s?next=%s' % (request.build_absolute_uri(reverse('blog:login_view')), next_url)
        sso_logout_url = request.build_absolute_uri(reverse('blog:logout_view'))
        context = {'next': next_url, 'sso_login_url': sso_login_url, 'sso_logout_url': sso_logout_url, }
        return render(request, 'blog/login.html', context)

def logout_view(request):
    print 'logout_view'
    auth.logout(request)
    response = HttpResponseRedirect(reverse('blog:login_view'))
    response.delete_cookie('duoshuo_token')
    print 'return logout_view'
    return response

def set_jwt_and_response(user, response):
    # For duoshuo jwt login
    if user is not None and user.is_authenticated() and user.is_active:
        user_profile = User_Profile.objects.filter(user=user)
        if not user_profile: # 本地的没有 多说 User_Profile
            # 则使用 jwt 来创建一个多说账户
            # For duoshuo jwt login
            duoshuo_jwt_token = None
            username = user.get_full_name()
            if not username:
                username = user.username
            token = {
                "short_name": settings.DUOSHUO_SHORT_NAME,
                "user_key": user.id,
                "name": username
            }
            duoshuo_jwt_token = jwt.encode(token, settings.DUOSHUO_SECRET)
            response.set_cookie('duoshuo_token', duoshuo_jwt_token)
    return response

import urllib
import urllib2

def sync_sso_duoshuo(access_token, user):
    '''将SSO本地用户同步到已有多说账户中
    '''
    url = 'http://api.duoshuo.com/sites/join.json'
    username = user.get_full_name()
    if not username:
        username = user.username
    email = user.email
    if not email:
        email = 'user@example.com'
    params = {
        'short_name': settings.DUOSHUO_SHORT_NAME,
        'secret': settings.DUOSHUO_SECRET,
        'access_token': access_token,
        'user[user_key]': user.id,
        'user[name]': username,
        'user[email]': user.email,
    }
    print 'sync_sso_duoshuo'
    print params
    data = urllib.urlencode(params)
    request = urllib2.Request(url, data=data)
    response = urllib2.urlopen(request)
    result = response.read()
    print result
