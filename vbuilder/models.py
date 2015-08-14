#!/usr/bin/env python
# coding=utf-8
from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.

class Root(models.Model):
    ''' Root of the word
    '''
    unit = models.IntegerField(
        verbose_name = _(u'单元')
    )
    root = models.CharField(
        verbose_name = _(u'词根'),
        help_text = _(u' '),
        max_length = 255
    )
    meaning = models.TextField(
        verbose_name = _(u'意思'),
        help_text = _(u' ')
    )
    description = models.TextField(
        verbose_name = _(u'描述'),
        help_text = _(u' '),
        blank = True
    )
    class Meta:
        app_label = _(u'vbuilder')
        verbose_name = _(u'Root')
        verbose_name_plural = _(u'Roots')
    def __unicode__(self):
        return u'%s' % (self.root,)

class NormalWord(models.Model):
    ''' Word that has root
    '''
    unit = models.IntegerField(
        verbose_name = _(u'单元')
    )
    word = models.CharField(
        verbose_name = _(u'单词'),
        help_text = _(u' '),
        max_length = 255
    )
    root = models.ForeignKey(
        Root,
        verbose_name = _(u'词根')
    )
    meaning = models.TextField(
        verbose_name = _(u'意思'),
        help_text = _(u' '),
    )
    sentence = models.TextField(
        verbose_name = _(u'例句'),
        help_text = _(u' '),
        blank = True
    )

    description = models.TextField(
        verbose_name = _(u'描述'),
        help_text = _(u' '),
        blank = True
    )
    class Meta:
        app_label = _(u'vbuilder')
        verbose_name = _(u'Word')
        verbose_name_plural = _(u'Words')
    def __unicode__(self):
        return u'%s' % (self.word,)

class ClosestDefQuiz(models.Model):
    ''' Quizze to choose the closest definition
    '''
    unit = models.IntegerField(
        verbose_name = _(u'单元')
    )
    word = models.CharField(
        verbose_name = _(u'单词'),
        help_text = _(u' '),
        max_length = 255
    )
    quiz = models.TextField(
        verbose_name = _(u'问题'),
        help_text = _(u'用换行分隔选项'),
    )
    answer = models.CharField(
        verbose_name = _(u'答案'),
        help_text = _(u' '),
        max_length = 255
    )
    class Meta:
        app_label = _(u'vbuilder')
        verbose_name = _(u'Closest Defintion Quiz')
        verbose_name_plural = _(u'Closest Definition Quizzes')
    def __unicode__(self):
        return u'%s %s' % (self.word, self.quiz)

class FillInBlankQuiz(models.Model):
    ''' Quizze to fill in each blank with the corredct letter
    '''
    unit = models.IntegerField(
        verbose_name = _(u'单元')
    )
    words = models.TextField(
        verbose_name = _(u'选项'),
        help_text = _(u'用换行分隔选项'),
    )
    quiz = models.TextField(
        verbose_name = _(u'问题'),
        help_text = _(u'用换行分隔'),
    )
    answer = models.CharField(
        verbose_name = _(u'答案'),
        help_text = _(u' '),
        max_length = 255
    )
    class Meta:
        app_label = _(u'vbuilder')
        verbose_name = _(u'Fill in Blank Quiz')
        verbose_name_plural = _(u'Fill in Blank Quizzes')
    def __unicode__(self):
        return u'%s %s' % (self.words, self.quiz)

class MatchQuiz(models.Model):
    ''' Quizze to match the definition on the left
    with the correct word on the right
    '''
    unit = models.IntegerField(
        verbose_name = _(u'单元')
    )
    left = models.TextField(
        verbose_name = _(u'选项'),
        help_text = _(u'用换行分隔'),
    )
    right = models.TextField(
        verbose_name = _(u'问题'),
        help_text = _(u'用换行分隔'),
    )
    answer = models.CharField(
        verbose_name = _(u'答案'),
        help_text = _(u' '),
        max_length = 255
    )
    class Meta:
        app_label = _(u'vbuilder')
        verbose_name = _(u'Match Quiz')
        verbose_name_plural = _(u'Match Quizzes')
    def __unicode__(self):
        return u'%s' % (self.left)
