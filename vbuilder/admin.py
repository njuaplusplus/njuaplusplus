#!/usr/bin/env python
# coding=utf-8
from django.contrib import admin
from vbuilder.models import Root, NormalWord, ClosestDefQuiz, FillInBlankQuiz, MatchQuiz

class RootAdmin(admin.ModelAdmin):
    list_display = ('unit', 'root', 'meaning',)
    search_fields = ('root', )
    fieldsets = (
        (
            None, 
            {
                'fields': ('unit', 'root', 'meaning', 'description',)
            }
        ),
    )

class NormalWordAdmin(admin.ModelAdmin):
    list_display = ('unit', 'word', 'meaning',)
    search_fields = ('word', )
    fieldsets = (
        (
            None, 
            {
                'fields': ('unit', 'word', 'root', 'meaning', 'sentence', 'description',)
            }
        ),
    )

class ClosestDefQuizAdmin(admin.ModelAdmin):
    list_display = ('unit', 'word', 'quiz', 'answer')
    search_fields = ('word', )
    fieldsets = (
        (
            None, 
            {
                'fields': ('unit', 'word', 'quiz', 'answer',)
            }
        ),
    )

class FillInBlankQuizAdmin(admin.ModelAdmin):
    list_display = ('unit', 'words', 'quiz', 'answer')
    search_fields = ('words', )
    fieldsets = (
        (
            None, 
            {
                'fields': ('unit', 'words', 'quiz', 'answer',)
            }
        ),
    )

class MatchQuizAdmin(admin.ModelAdmin):
    list_display = ('unit', 'left', 'right', 'answer')
    search_fields = ('left', )
    fieldsets = (
        (
            None, 
            {
                'fields': ('unit', 'left', 'right', 'answer',)
            }
        ),
    )

admin.site.register(Root, RootAdmin)
admin.site.register(NormalWord, NormalWordAdmin)
admin.site.register(ClosestDefQuiz, ClosestDefQuizAdmin)
admin.site.register(FillInBlankQuiz, FillInBlankQuizAdmin)
admin.site.register(MatchQuiz, MatchQuizAdmin)
