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
import random
import json


def index(request):
    return index_page(request, 1)


def get_top_categories(num=None):
    categories = Category.objects.all()
    if num is None:
        return sorted(
                categories,
                key=lambda x: x.article_set.count(),
                reverse=True
        )
    else:
        return sorted(
                categories,
                key=lambda x: x.article_set.count(),
                reverse=True
        )[:num]


def evenly_divide_list(l):
    """ Divide the list to 2 even parts.
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
            print('In write_post_view', article.id)
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
        return HttpResponseRedirect(reverse('blog:index'))
    if request.method == 'POST': # 本地用户登录
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        next_url = decide_next_url(request.POST.get('next', ''))
        if user is not None and user.is_active:
            # Correct password, and the user is marked 'active'
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            # Show an error page
            return render(request, 'blog/login.html', {'next': next_url})
    else: # GET method
        code = request.GET.get('code', '')
        next_url = decide_next_url(request.GET.get('next', ''))
        return render(
            request,
            'blog/login.html',
            {
                'next': next_url,
            }
        )

def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('blog:login_view'))

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
    found_articles = None
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
