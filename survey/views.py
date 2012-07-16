# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from models import ParticipantForm, AnswerFormSet, Participant, Question, Answer, CATEGORIES, Result
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from random import choice
from django.db.models import Avg

#def survey_redirect(request):
#    if request.session.get('participant_id', False) and Participant.objects.filter(pk = request.session.get('participant_id')):
#        return HttpResponseRedirect(reverse('survey-page'))
#    else:
#        return HttpResponseRedirect(reverse('survey-first'))

def survey_eval(request):
    ev = []
    
    genders = [{'title':"Alle", 'query':["m","f"]},{'title':u"Männlich", 'query':["m"],},{'title':"Weiblich", 'query':["f"]}]
    
    for g in genders:
        ps = Participant.objects.filter(done=True, gender__in=g['query'])
        psa = ps.aggregate(age = Avg('age'), edu = Avg('education'), degree = Avg('degree'))
        psa['count'] = ps.count()
        
        qs = Question.objects.filter(answer__participant__done=True, answer__participant__gender__in=g['query']).annotate(fear__avg=Avg('answer__fear'), anger__avg=Avg('answer__anger'), shame__avg=Avg('answer__shame'), guilt__avg=Avg('answer__guilt'), neutral__avg=Avg('answer__neutral'))
        
        qsv = qs.values()
        for q in qsv:
            q['fear']=q['fear__avg']-(q['anger__avg']+q['shame__avg']+q['guilt__avg']+q['neutral__avg'])
            q['anger']=q['anger__avg']-(q['fear__avg']+q['shame__avg']+q['guilt__avg']+q['neutral__avg'])
            q['shame']=q['shame__avg']-(q['fear__avg']+q['anger__avg']+q['guilt__avg']+q['neutral__avg'])
            q['guilt']=q['guilt__avg']-(q['anger__avg']+q['shame__avg']+q['fear__avg']+q['neutral__avg'])
            q['neutral']=q['neutral__avg']-(q['anger__avg']+q['shame__avg']+q['guilt__avg']+q['fear__avg'])
        
        
        ev.append({'title':g['title'], 'ps':psa, 'qs':qsv})
        
    return render_to_response("eval.html",{'ev':ev, 'cat':CATEGORIES} ,context_instance=RequestContext(request))
    

def survey_reset(request):
    if not request.session.session_key:
        return HttpResponseRedirect(reverse('survey-page'))
    try:
        participant = Participant.objects.get(session = request.session.session_key)
    except Participant.DoesNotExist:
        return HttpResponseRedirect(reverse('survey-page'))
    
    participant.session = "aborted"
    participant.save()
    return HttpResponseRedirect(reverse('survey-page'))
    
def survey_first(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            try:
                participant = Participant.objects.get(session = request.session.session_key)
            except Participant.DoesNotExist:
                participant = form.save(commit=False)
                participant.session = request.session.session_key
                participant.save()
                #request.session['participant_id'] = participant.pk
            return HttpResponseRedirect(reverse('survey-page'))
    else:
        form = ParticipantForm()
    
    return render_to_response('first.html', {
                                             'form': form,
                                             },
                                             context_instance=RequestContext(request))

def survey_page(request):
    request.session['foo'] = "bar"
    if not request.session.session_key:
        return HttpResponseRedirect(reverse('survey-first'))
    try:
        participant = Participant.objects.get(session = request.session.session_key)
    except Participant.DoesNotExist:
        return HttpResponseRedirect(reverse('survey-first'))
    #participant = get_object_or_404(Participant, pk = request.session.get('participant_id'))
    answered = Answer.objects.filter(participant = participant)
    unanswered = Question.objects.exclude(pk__in = answered.values_list('question', flat=True))
    unfinished = Answer.objects.filter(participant = participant, done=False)
    
    if not unanswered and not unfinished:
        participant.done = True
        participant.save()
        return HttpResponseRedirect(reverse('survey-thanks'))
    
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.instance.done = True
            formset.save(commit=True)
            for form in formset:
                obj, created = Result.objects.get_or_create(question = form.instance.question)
                obj.save()
            return HttpResponseRedirect(reverse('survey-page'))
    else:
        answers = []
    
        if not unfinished:
            for cat in CATEGORIES:
                try:
                    question = choice(unanswered.filter(category = cat))
                    Answer(question=question, participant=participant).save()
                except (IndexError):
                    pass
        formset = AnswerFormSet(queryset=unfinished.order_by('?') )
    sentences = []
    for form in formset:
        form.fields['question'].widget = forms.HiddenInput()
        form.fields['participant'].widget = forms.HiddenInput()
    
    return render_to_response('page.html', {
                                             'formset': formset,
                                             'sentences': sentences,
                                             'allpage' : Question.objects.count()/5+1,
                                             'thispage': answered.filter(done=True).count()/5+1,
                                             },
                                             context_instance=RequestContext(request))
