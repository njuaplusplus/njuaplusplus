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
import json

def index(request):
    return index_page(request, 1)

def get_top_categories(num=None):
    categories = Category.objects.all()
    if num is None:
        return sorted(
                categories,
                cmp=lambda x,y: cmp(x.article_set.count(), y.article_set.count()),
                reverse=True
        )
    else:
        return sorted(
                categories,
                cmp=lambda x,y: cmp(x.article_set.count(), y.article_set.count()),
                reverse=True
        )[:num]

def evenly_divide_list(l, n=2):
    """ Divide the list to n even parts.
    """
    mid = len(l) >> 1
    if mid << 1 == len(l):
        return [l[:mid], l[mid:]]
    else:
        return [l[:mid+1], l[mid+1:]]

def index_page(request, page_num):
    """The news index"""
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
        "blog/default/index.html",
        {
            "articles"      : articles,
            "archive_dates" : evenly_divide_list(Article.objects.datetimes('date_publish','month', order='DESC')),
            "categories"    : evenly_divide_list(get_top_categories(8)),
        }
    )

def single(request, slug) :
    """A single article"""
    article = get_object_or_404(Article, slug=slug)
    return render(
        request,
        "blog/default/post.html",
        {
            "article" : article,
            "archive_dates" : evenly_divide_list(Article.objects.datetimes('date_publish','month', order='DESC')),
            "categories"    : evenly_divide_list(get_top_categories(8)),
        }
    )

def date_archive(request, year, month):
    return date_archive_page(request, year, month, 1)

import pytz

def date_archive_page(request, year, month, page_num):
    """The blog date archive"""
    # this archive pages dates
    year = int(year)
    month = int(month)
    month_range = calendar.monthrange(year, month)
    start = datetime.datetime(year=year, month=month, day=1)#.replace(tzinfo=utc)
    end = datetime.datetime(year=year, month=month, day=month_range[1])#.replace(tzinfo=utc)
    start = pytz.timezone("Asia/Shanghai").localize(start, is_dst=None)
    end = pytz.timezone("Asia/Shanghai").localize(end, is_dst=None)

    # Pagination
    article_queryset = Article.objects.filter(date_publish__range=(start, end))
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
        "blog/default/date_archive.html",
        {
            "start"         : start,
            "end"           : end,
            "articles"      : articles,
            "archive_dates" : evenly_divide_list(Article.objects.datetimes('date_publish','month', order='DESC')),
            "categories"    : evenly_divide_list(get_top_categories(8)),
        }
    )

def category(request):
    categories = get_top_categories()
    category_urls = {}
    for c in categories:
        category_urls[u'%s (%d)' % (c.title, c.article_set.count())] = reverse('blog:category_archive_view', args=(c.slug,))
    category_list = [ [u'%s (%d)' % (c.title, c.article_set.count()), c.article_set.count()+1] for c in categories ]
    return render(
        request,
        'blog/default/category.html',
        {
            'category_list' : json.dumps(category_list, ensure_ascii=False),
            'category_urls' : json.dumps(category_urls, ensure_ascii=False),
            'archive_dates' : evenly_divide_list(Article.objects.datetimes('date_publish','month', order='DESC')),
            'categories'    : get_top_categories(),
        }
    )

def category_archive(request, slug):
    return category_archive_page(request, slug, 1)

def category_archive_page(request, slug, page_num):
    # archive_dates = Article.objects.datetimes('date_publish','month', order='DESC')
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
        "blog/default/category_archive.html",
        {
            "articles"      : articles,
            "archive_dates" : evenly_divide_list(Article.objects.datetimes('date_publish','month', order='DESC')),
            'categories'    : evenly_divide_list(get_top_categories(8)),
            "category"      : category,
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

import re

from django.db.models import Q

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def search(request):
    query_string = request.GET.get('queryString', '')
    found_entries = None
    if query_string:
        entry_query = get_query(query_string, ['title', 'excerpt', 'content_markdown',])
        found_articles = Article.objects.filter(entry_query)

    return render(
        request,
        'blog/default/search_results.html',
        {
            'query_string'   : query_string,
            'found_articles' : found_articles,
            'categories'     : evenly_divide_list(get_top_categories(8)),
            'archive_dates' : evenly_divide_list(Article.objects.datetimes('date_publish','month', order='DESC')),
        }
    )
