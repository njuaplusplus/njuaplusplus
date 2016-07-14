#!/usr/bin/env python
# coding=utf-8

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .models import Category, Article, ArticleForm, MyImage, MyImageForm, markdown_to_html
import calendar, datetime
from django.conf import settings  # use settings
import datetime
import random
import json
import pytz
import re
from django.db.models import Q
from django.template.loader import render_to_string


def ip(request):
    IPWARE_META_PRECEDENCE_ORDER = (
        'HTTP_X_FORWARDED_FOR', 'X_FORWARDED_FOR',  # client, proxy1, proxy2
        'HTTP_CLIENT_IP',
        'HTTP_X_REAL_IP',
        'HTTP_X_FORWARDED',
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED_FOR',
        'HTTP_FORWARDED',
        'HTTP_VIA',
        'REMOTE_ADDR',
    )
    result = ['%s\t%s' % (k,v) for k,v in request.META.items() if k in IPWARE_META_PRECEDENCE_ORDER]
    return HttpResponse('\n'.join(result))


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
        return [l[:mid + 1], l[mid + 1:]]


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
            "articles":      articles,
            "archive_dates": evenly_divide_list(Article.objects.datetimes('date_publish', 'month', order='DESC')),
            "categories":    evenly_divide_list(get_top_categories(8)),
        }
    )


def single(request, slug):
    """A single article"""
    article = get_object_or_404(Article, slug=slug)
    return render(
        request,
        "blog/default/post.html",
        {
            "article":       article,
            "archive_dates": evenly_divide_list(Article.objects.datetimes('date_publish', 'month', order='DESC')),
            "categories":    evenly_divide_list(get_top_categories(8)),
        }
    )


def date_archive(request, year, month):
    return date_archive_page(request, year, month, 1)


def date_archive_page(request, year, month, page_num):
    """The blog date archive"""
    # this archive pages dates
    year = int(year)
    month = int(month)
    month_range = calendar.monthrange(year, month)
    start = datetime.datetime(year=year, month=month, day=1)  # .replace(tzinfo=utc)
    end = datetime.datetime(year=year, month=month, day=month_range[1])  # .replace(tzinfo=utc)
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
            "start": start,
            "end": end,
            "articles": articles,
            "archive_dates": evenly_divide_list(Article.objects.datetimes('date_publish', 'month', order='DESC')),
            "categories": evenly_divide_list(get_top_categories(8)),
        }
    )


def category(request):
    categories = get_top_categories()
    category_urls = {}
    for c in categories:
        category_urls[u'%s (%d)' % (c.title, c.article_set.count())] = reverse('blog:category_archive_view',
                                                                               args=(c.slug,))
    category_list = [[u'%s (%d)' % (c.title, c.article_set.count()), c.article_set.count() + 1] for c in categories]
    return render(
        request,
        'blog/default/category.html',
        {
            'category_list': json.dumps(category_list, ensure_ascii=False),
            'category_urls': json.dumps(category_urls, ensure_ascii=False),
            'archive_dates': evenly_divide_list(Article.objects.datetimes('date_publish', 'month', order='DESC')),
            'categories': get_top_categories(),
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
            "articles": articles,
            "archive_dates": evenly_divide_list(Article.objects.datetimes('date_publish', 'month', order='DESC')),
            'categories': evenly_divide_list(get_top_categories(8)),
            "category": category,
        }
    )


def author_archive(request, username):
    return author_archive_page(request, username, 1)


def author_archive_page(request, username, page_num):
    author = get_object_or_404(User, username=username)

    # Pagination
    article_queryset = Article.objects.filter(author=author)
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
        'blog/default/author_archive.html',
        {
            'articles': articles,
            'author': author,
            'username': username,
            'archive_dates': evenly_divide_list(Article.objects.datetimes('date_publish', 'month', order='DESC')),
            'categories': evenly_divide_list(get_top_categories(8)),
            'category': category,
        }
    )


@login_required
def write_post_view(request):
    if not request.user.groups.filter(name='authors'):
        return render(request, 'blog/error.html', {'error': '权限不够', 'message': '权限不够, 请联系管理员!',})
    if request.method == 'POST':
        article_form = ArticleForm(request.POST, request.FILES)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.author = request.user
            article.for_preview = False
            article.save()
            article_form.save_m2m()
            return HttpResponseRedirect(reverse('blog:single_post', args=(article.slug,)))
    else:
        article_form = ArticleForm()
        my_image_form = MyImageForm()
    return render(
        request,
        'blog/write_post.html',
        {
            'article_form': article_form,
            'my_images': MyImage.objects.all(),
            'my_image_form': my_image_form,
         }
    )


@login_required
def preview_post_view(request):
    if request.method == 'POST' and request.is_ajax():
        try:
            article_id = int(request.POST.get('article-id', '-1'))
        except ValueError:
            article_id = -1

        article_form = ArticleForm(request.POST, request.FILES,
                                   instance=Article.objects.filter(pk=article_id).first())
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.author = request.user
            article.content_markup = markdown_to_html(article.content_markdown)
            request.session['preview_article_html'] = render_to_string(
                'blog/default/post.html',
                {
                    'article': article,
                    'article_categories': [
                        {
                            'slug': x.slug,
                            'title': x.title,
                        }
                        for x in article_form.cleaned_data['categories']
                    ],
                    'preview_post': True,
                },
                request=request
            )
        return _ajax_result(request, article_form)
    elif request.method == 'GET':
        article_html = request.session.get('preview_article_html', None)
        if article_html:
            return HttpResponse(article_html)
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')


@login_required
@require_POST
def upload_image_ajax(request):
    if not request.is_ajax():
        return HttpResponseBadRequest("Expecting Ajax call")

    my_image_form = MyImageForm(request.POST, request.FILES)
    if my_image_form.is_valid():
        my_image = my_image_form.save(commit=False)
        print(my_image.image)
        my_image.user = request.user
        my_image.save()
        return _ajax_result(request, my_image_form, my_image)
    else:
        return _ajax_result(request, my_image_form)


def _ajax_result(request, form, image=None):
    success = True
    json_errors = {}

    if form.errors:
        for field_name in form.errors:
            json_errors[field_name] = str(form[field_name].errors)
        success = False

    json_return = {
        'success': success,
        'errors': json_errors,
    }

    if image is not None:
        json_return.update({
            'image_url': image.image.url,
            'image_title': image.title,
        })

    return JsonResponse(json_return)


@login_required
def edit_post_view(request, post_id):
    article = get_object_or_404(Article, pk=post_id)
    if not request.user.groups.filter(name='admins') and not (
                request.user.groups.filter(name='authors') and request.user == article.author
    ):
        return render(request, 'blog/error.html', {'error': '权限不够', 'message': '权限不够, 请联系管理员!',})
    if request.method == 'POST':
        article_form = ArticleForm(request.POST, request.FILES, instance=article)
        if article_form.is_valid():
            article = article_form.save()
            return HttpResponseRedirect(reverse('blog:single_post', args=(article.slug,)))
    else:
        article_form = ArticleForm(instance=article)
        my_image_form = MyImageForm()
    return render(
        request,
        'blog/write_post.html',
        {
            'article_form': article_form,
            'article_id': post_id,
            'my_images': MyImage.objects.all(),
            'my_image_form': my_image_form,
        }
    )


def decide_next_url(next_url):
    if next_url is None or len(next_url) == 0 or next_url == reverse('blog:login_view'):
        next_url = reverse('blog:index')
    return next_url


def login_view(request):
    if request.user is not None and request.user.is_active:
        return HttpResponseRedirect(reverse('blog:index'))
    if request.method == 'POST':  # 本地用户登录
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
    else:  # GET method
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
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
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
        entry_query = get_query(query_string, ['title', 'excerpt', 'content_markdown', ])
        found_articles = Article.objects.filter(entry_query)

    return render(
        request,
        'blog/default/search_results.html',
        {
            'query_string': query_string,
            'found_articles': found_articles,
            'categories': evenly_divide_list(get_top_categories(8)),
            'archive_dates': evenly_divide_list(Article.objects.datetimes('date_publish', 'month', order='DESC')),
        }
    )
