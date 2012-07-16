# -*- coding: utf-8 -*-

from survey.models import *
from django.contrib import admin

def answers_by_participant(obj):
    return Answer.objects.filter(participant = obj, done = True).count()
answers_by_participant.short_description = 'Beantwortet'

def is_participant_done(obj):
    return answers_by_participant(obj) == Question.objects.all().count()
is_participant_done.short_description = 'Fertig?'

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('pk', 'age', 'gender', 'degree',answers_by_participant, 'done', 'date_start', 'session')
    list_filter = ('done',)
    
def answers_by_question(obj):
    return Answer.objects.filter(question = obj, done = True).count()
answers_by_question.short_description = 'Antworten'

def avg_cat(obj, cat):
    q = Answer.objects.filter(question = obj, done = True).values_list(cat, flat=True)
    if len(q):
        return sum(q)/len(q)
    else:
        return "-"

def avg_fear(obj):
    return avg_cat(obj, 'fear')
avg_fear.short_description = 'avg(Angst)'

def avg_anger(obj):
    return avg_cat(obj, 'anger')
avg_anger.short_description = u'avg(Ärger)'

def avg_shame(obj):
    return avg_cat(obj, 'shame')
avg_shame.short_description = u'avg(Scham)'

def avg_guilt(obj):
    return avg_cat(obj, 'guilt')
avg_guilt.short_description = u'avg(Schuld)'

def avg_neutral(obj):
    return avg_cat(obj, 'anger')
avg_neutral.short_description = u'avg(Neutral)'

def d_cat(obj, cat):
    if avg_cat(obj,cat) != "-":
        return 2*avg_cat(obj,cat)-sum([avg_fear(obj),avg_anger(obj),avg_shame(obj),avg_guilt(obj),avg_neutral(obj)])
    else:
        return "-"
def d_fear(obj):
    return d_cat(obj, 'fear')
d_fear.short_description = 'd(Angst)'

def d_anger(obj):
    return d_cat(obj, 'anger')
d_anger.short_description = u'd(Ärger)'

def d_shame(obj):
    return d_cat(obj, 'shame')
d_shame.short_description = u'd(Scham)'

def d_guilt(obj):
    return d_cat(obj, 'guilt')
d_guilt.short_description = u'd(Schuld)'

def d_neutral(obj):
    return d_cat(obj, 'anger')
d_neutral.short_description = u'd(Neutral)'


class QuestionAdmin(admin.ModelAdmin):
    #list_display = ('pk', 'category', 'sentence', answers_by_question, avg_fear, avg_anger, avg_shame, avg_guilt, avg_neutral, d_fear, d_anger, d_shame, d_guilt, d_neutral)
    list_display = ('pk', 'category', 'sentence')
    
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question','participant', 'fear', 'anger', 'shame', 'guilt', 'neutral', 'autobiographic', 'done')
    
class ResultAdmin(admin.ModelAdmin):
    list_display = ('question', 'count', 'avg_fear', 'avg_anger', 'avg_shame', 'avg_guilt', 'avg_neutral','d_fear', 'd_anger', 'd_shame', 'd_guilt', 'd_neutral')
    list_display_links = ('count',)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Result, ResultAdmin)

