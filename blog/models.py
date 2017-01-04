#!/usr/bin/env python
# coding=utf-8
from django.contrib.auth.forms import PasswordChangeForm
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
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User


class Category(models.Model):
    """Category Model"""
    title = models.CharField(
        verbose_name=_('名称'),
        help_text=_(' '),
        max_length=255,
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        help_text=_('Uri identifier.'),
        max_length=255,
        unique=True
    )

    class Meta:
        app_label = _('blog')
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['title', ]

    def save(self, *args, **kwargs):
        if not self.slug.strip():
            # slug is null or empty
            self.slug = uuslug(self.title, instance=self, max_length=32, word_boundary=True)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.title,)


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
        verbose_name=_('图片'),
        help_text=_(' '),
        upload_to='blogs/images/%Y/%m/%d',
        null=True,
        blank=True
    )
    origin_image = models.CharField(
        verbose_name=_('原图的七牛key'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    large_image = models.CharField(
        verbose_name=_('1024x的七牛key'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    small_image = models.CharField(
        verbose_name=_('256x的七牛key'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    title = models.CharField(
        verbose_name=_('标题'),
        help_text=_(' '),
        max_length=100
    )
    description = models.TextField(
        verbose_name=_('描述'),
        help_text=_(' '),
        blank=True
    )
    # Whether this image is visible to others?
    is_public = models.BooleanField(
        verbose_name=_('公共可见'),
        default=False
    )
    date_upload = models.DateTimeField(
        verbose_name=_('上传日期'),
        help_text=_(' ')
    )

    class Meta:
        app_label = _('blog')
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        ordering = ['-date_upload', 'title', ]

    def __str__(self):
        return '%s' % (self.title,)


class Article(models.Model):
    """Article Model"""
    title = models.CharField(
        verbose_name=_('标题'),
        help_text=_(' '),
        max_length=255
    )
    slug = models.SlugField(
        verbose_name=_('固定链接'),
        help_text=_('本文章的短网址(Uri identifier).'),
        max_length=255,
        unique=True
    )
    cover = models.ImageField(
        verbose_name=_('封面'),
        help_text=_('若留空, 则使用默认图片'),
        upload_to='blogs/images/%Y/%m/%d',
        null=True,
        blank=True
    )
    excerpt = models.TextField(
        verbose_name=_('摘要'),
        help_text=_(' '),
        blank=True
    )
    author = models.ForeignKey(User, verbose_name=_('作者'))
    content_markdown = models.TextField(
        verbose_name=_('内容 (Markdown)'),
        help_text=_(' '),
    )
    content_markup = models.TextField(
        verbose_name=_('内容 (Markup)'),
        help_text=_(' '),
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name=_('分类'),
        help_text=_(' '),
        blank=True
    )
    date_publish = models.DateTimeField(
        verbose_name=_('发布日期'),
        help_text=_(' ')
    )
    is_public = models.BooleanField(
        verbose_name=_('公开博客'),
        default=False
    )
    is_approved = models.BooleanField(
        verbose_name=_('通过审核'),
        default=False
    )
    enable_comments = models.BooleanField(
        verbose_name=_('允许评论'),
        default=True
    )

    def get_absolute_url(self):
        return reverse('blog:single_post', kwargs={'slug': self.slug})

    class Meta:
        app_label = _('blog')
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
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
        return '%s' % (self.title,)


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
            'origin_image': forms.HiddenInput(),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        fields = ['origin_image', 'title', 'description', 'is_public', ]


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
        verbose_name=_('本地头像图片'),
        help_text=_('若留空, 则使用默认图片'),
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


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']


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

    def allow(self, comment, content_object, request):
        if comment.ip_address == "b''":
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
            result = ['%s\t%s' % (k, v) for k, v in list(request.META.items()) if k in IPWARE_META_PRECEDENCE_ORDER]
            print('Strange Comment IP:', result)
            return False
        else:
            return super(ArticleModerator, self).allow(comment, content_object, request)

    def email(self, comment, content_object, request):
        """
        Send email notification of a new comment to site staff when email
        notifications have been requested.

        """
        if not self.email_notification:
            return
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        site = get_current_site(request)
        subject = '[%s] New comment posted on "%s"' % (site.name, content_object)
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

        data_tuple = (
            (subject, message, settings.DEFAULT_FROM_EMAIL, [recipient, ]) for recipient in recipient_list
        )

        send_mass_mail(data_tuple, fail_silently=True)


moderator.register(Article, ArticleModerator)


class MyPasswordChangeForm(PasswordChangeForm):
    """
    Just add some class to the widget of default PasswordChangeForm
    """
    def __init__(self, *args, **kwargs):
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'class':'form-control'})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})