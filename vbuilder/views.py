#!/usr/bin/env python
# coding=utf-8
from django.shortcuts import render
from vbuilder.models import *


def unit_quiz(request, unit):
    closest_def_quizzes = ClosestDefQuiz.objects.filter(unit=unit)
    fillin_blank_quizzes = FillInBlankQuiz.objects.filter(unit=unit)
    match_quizzes = MatchQuiz.objects.filter(unit=unit)
    if closest_def_quizzes:
        closest_def_quizzes = [
            (x.id, x.word, x.quiz.splitlines(), x.answer)
            for x in closest_def_quizzes
        ]
    if fillin_blank_quizzes:
        fillin_blank_quizzes = [
            (x.id, x.words.splitlines(), x.quiz.replace(u'@', u'__').splitlines(), x.answer)
            for x in fillin_blank_quizzes
        ]
    if match_quizzes:
        match_quizzes = [
            (x.id, zip(x.left.splitlines(), x.right.splitlines()), x.answer)
            for x in match_quizzes
        ]
    return render(
        request,
        'vbuilder/unit_quiz.html',
        {
            'closest_def_quizzes' : closest_def_quizzes,
            'fillin_blank_quizzes' : fillin_blank_quizzes,
            'match_quizzes' : match_quizzes,
        }
    )

