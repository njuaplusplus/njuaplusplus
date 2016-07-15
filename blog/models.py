#!/usr/bin/env python
# coding=utf-8

from django.db import models
from django.utils.translation import ugettext as _
# from markdown import markdown
import markdown
from django.contrib.auth.models import User
from uuslug import uuslug
from django import forms
from pagedown.widgets import PagedownWidget
# from bootstrap3_datetime.widgets import DateTimePicker
from datetimewidget.widgets import DateTimeWidget
from django.core.urlresolvers import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django_comments.moderation import CommentModerator, moderator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User


class Category(models.Model):
    """Category Model"""
    title = models.CharField(
        verbose_name=_(u'名称'),
        help_text=_(u' '),
        max_length=255,
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_(u'Slug'),
        help_text=_(u'Uri identifier.'),
        max_length=255,
        unique=True
    )

    class Meta:
        app_label = _(u'blog')
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')
        ordering = ['title', ]

    def save(self, *args, **kwargs):
        if not self.slug.strip():
            # slug is null or empty
            self.slug = uuslug(self.title, instance=self, max_length=32, word_boundary=True)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return u'%s' % (self.title,)


class MyImage(models.Model):
    """ Image storage for the post"""
    # Who uploaded this image.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        blank=True,
        null=True,
        related_name="%(class)s_image",
        on_delete=models.SET_NULL
    )
    image = models.ImageField(
        verbose_name=_(u'图片'),
        help_text=_(u' '),
        upload_to='blogs/images/%Y/%m/%d',
    )
    title = models.CharField(
        verbose_name=_(u'标题'),
        help_text=_(u' '),
        max_length=100
    )
    description = models.TextField(
        verbose_name=_(u'描述'),
        help_text=_(u' '),
        blank=True
    )
    # Whether this image is visible to others?
    is_public = models.BooleanField(
        verbose_name=_(u'公共可见'),
        default=False
    )

    class Meta:
        app_label = _(u'blog')
        verbose_name = _(u'Image')
        verbose_name_plural = _(u'Images')
        ordering = ['title', ]

    def __str__(self):
        return u'%s' % (self.title,)


class Article(models.Model):
    """Article Model"""
    title = models.CharField(
        verbose_name=_(u'标题'),
        help_text=_(u' '),
        max_length=255
    )
    slug = models.SlugField(
        verbose_name=_(u'固定链接'),
        help_text=_(u'本文章的短网址(Uri identifier).'),
        max_length=255,
        unique=True
    )
    cover = models.ImageField(
        verbose_name=_(u'封面'),
        help_text=_(u'若留空, 则使用默认图片'),
        upload_to='blogs/images/%Y/%m/%d',
        null=True,
        blank=True
    )
    excerpt = models.TextField(
        verbose_name=_(u'摘要'),
        help_text=_(u' '),
        blank=True
    )
    author = models.ForeignKey(User, verbose_name=_(u'作者'))
    content_markdown = models.TextField(
        verbose_name=_(u'内容 (Markdown)'),
        help_text=_(u' '),
    )
    content_markup = models.TextField(
        verbose_name=_(u'内容 (Markup)'),
        help_text=_(u' '),
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name=_(u'分类'),
        help_text=_(u' '),
        blank=True
    )
    date_publish = models.DateTimeField(
        verbose_name=_(u'发布日期'),
        help_text=_(u' ')
    )
    is_public = models.BooleanField(
        verbose_name=_(u'公开博客'),
        default=False
    )
    is_approved = models.BooleanField(
        verbose_name=_(u'通过审核'),
        default=False
    )
    enable_comments = models.BooleanField(
        verbose_name=_(u'允许评论'),
        default=True
    )

    def get_absolute_url(self):
        return reverse('blog:single_post', kwargs={'slug': self.slug})

    class Meta:
        app_label = _(u'blog')
        verbose_name = _(u'Article')
        verbose_name_plural = _(u'Articles')
        ordering = ['-date_publish']

    def save(self, *args, **kwargs):
        if not self.slug.strip():
            # slug is null or empty
            self.slug = uuslug(self.title, instance=self, max_length=32, word_boundary=True)
        if self.is_approved is None:
            self.is_approved = False
        if self.is_public is None:
            self.is_public = False
        self.content_markup = markdown_to_html(self.content_markdown)
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return u'%s' % (self.title,)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        dateTimeOptions = {
            'todayBtn': 'true',
        }
        widgets = {
            # 'content_markdown' : PagedownWidget(),
            # 'date_publish' : DateTimePicker(options={"format": "YYYY-MM-DD HH:mm", "pickSeconds": False, "language": 'zh-cn', }),
            'date_publish': DateTimeWidget(usel10n=True, bootstrap_version=3, options=dateTimeOptions),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'content_markdown': forms.Textarea(attrs={'class': 'form-control', 'rows': 20}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        exclude = ['content_markup', 'author', 'is_approved', ]


class MyImageForm(forms.ModelForm):
    class Meta:
        model = MyImage
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        exclude = ['user', ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        fields = '__all__'


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    token = models.IntegerField(default=0)
    avatar = models.ImageField(
        verbose_name=_(u'本地头像图片'),
        help_text=_(u'若留空, 则使用默认图片'),
        upload_to='avatars/%Y/%m/%d',
        null=True,
        blank=True
    )
    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(64, 64)],
        format='JPEG',
        options={'quality': 80}
    )

    def __str__(self):
        return self.user.username


def markdown_to_html(text):
    """Compile the text into html
    """
    md = markdown.Markdown(
        extensions=['codehilite', 'attr_list'],
        extension_configs={
            'codehilite': {
                'linenums': True,
                # 'noclasses': True,
            }
        }
    )
    return md.convert(text)


class ArticleModerator(CommentModerator):
    email_notification = True
    enable_field = 'enable_comments'

    def email(self, comment, content_object, request):
        """
        Send email notification of a new comment to site staff when email
        notifications have been requested.

        """
        if not self.email_notification:
            return
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        site = get_current_site(request)
        subject = u'[%s] New comment posted on "%s"' % (site.name, content_object)
        message = render_to_string(
            'comments/comment_notification_email.txt',
            {
                'site': site,
                'comment': comment,
                'content_object': content_object,
            }
        )
        # Add the users of the parent comments
        pp = comment.parent
        while pp:
            mail_addr = pp.user_email
            if not mail_addr and pp.user and pp.user.email:
                mail_addr = pp.user.email
            if mail_addr and mail_addr != 'user@example.com':
                if not mail_addr in recipient_list:
                    recipient_list.append(mail_addr)
            pp = pp.parent

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)


moderator.register(Article, ArticleModerator)
