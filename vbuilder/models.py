#!/usr/bin/env python
# coding=utf-8
from django.db import models
from django.utils.translation import ugettext as _


# Create your models here.

class Root(models.Model):
    """ Root of the word
    """
    unit = models.IntegerField(
        verbose_name=_('单元')
    )
    root = models.CharField(
        verbose_name=_('词根'),
        help_text=_(' '),
        max_length=255
    )
    meaning = models.TextField(
        verbose_name=_('意思'),
        help_text=_(' ')
    )
    description = models.TextField(
        verbose_name=_('描述'),
        help_text=_(' '),
        blank=True
    )

    class Meta:
        app_label = _('vbuilder')
        verbose_name = _('Root')
        verbose_name_plural = _('Roots')

    def __str__(self):
        return '%s' % (self.root,)


class NormalWord(models.Model):
    """ Word that has root
    """
    unit = models.IntegerField(
        verbose_name=_('单元')
    )
    word = models.CharField(
        verbose_name=_('单词'),
        help_text=_(' '),
        max_length=255
    )
    root = models.ForeignKey(
        Root,
        verbose_name=_('词根')
    )
    meaning = models.TextField(
        verbose_name=_('意思'),
        help_text=_(' '),
    )
    sentence = models.TextField(
        verbose_name=_('例句'),
        help_text=_(' '),
        blank=True
    )

    description = models.TextField(
        verbose_name=_('描述'),
        help_text=_(' '),
        blank=True
    )

    class Meta:
        app_label = _('vbuilder')
        verbose_name = _('Word')
        verbose_name_plural = _('Words')

    def __str__(self):
        return '%s' % (self.word,)


class ClosestDefQuiz(models.Model):
    """ Quiz to choose the closest definition
    """
    unit = models.IntegerField(
        verbose_name=_('单元')
    )
    word = models.CharField(
        verbose_name=_('单词'),
        help_text=_(' '),
        max_length=255
    )
    quiz = models.TextField(
        verbose_name=_('问题'),
        help_text=_('用换行分隔选项'),
    )
    answer = models.CharField(
        verbose_name=_('答案'),
        help_text=_(' '),
        max_length=255
    )

    class Meta:
        app_label = _('vbuilder')
        verbose_name = _('Closest Defintion Quiz')
        verbose_name_plural = _('Closest Definition Quizzes')

    def __str__(self):
        return '%s %s' % (self.word, self.quiz)


class FillInBlankQuiz(models.Model):
    """ Quiz to fill in each blank with the corredct letter
    """
    unit = models.IntegerField(
        verbose_name=_('单元')
    )
    words = models.TextField(
        verbose_name=_('选项'),
        help_text=_('用换行分隔选项'),
    )
    quiz = models.TextField(
        verbose_name=_('问题'),
        help_text=_('用换行分隔'),
    )
    answer = models.CharField(
        verbose_name=_('答案'),
        help_text=_(' '),
        max_length=255
    )

    class Meta:
        app_label = _('vbuilder')
        verbose_name = _('Fill in Blank Quiz')
        verbose_name_plural = _('Fill in Blank Quizzes')

    def __str__(self):
        return '%s %s' % (self.words, self.quiz)


class MatchQuiz(models.Model):
    """ Quiz to match the definition on the left
    with the correct word on the right
    """
    unit = models.IntegerField(
        verbose_name=_('单元')
    )
    left = models.TextField(
        verbose_name=_('选项'),
        help_text=_('用换行分隔'),
    )
    right = models.TextField(
        verbose_name=_('问题'),
        help_text=_('用换行分隔'),
    )
    answer = models.CharField(
        verbose_name=_('答案'),
        help_text=_(' '),
        max_length=255
    )

    class Meta:
        app_label = _('vbuilder')
        verbose_name = _('Match Quiz')
        verbose_name_plural = _('Match Quizzes')

    def __str__(self):
        return '%s' % (self.left)
