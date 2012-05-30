from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
# Create your views here.
from models import ParticipantForm, AnswerFormSet, Participant, Question, Answer, CATEGORIES, Result
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from random import choice

def survey_redirect(request):
    if request.session.get('participant_id', False) and Participant.objects.filter(pk = request.session.get('participant_id')):
        return HttpResponseRedirect(reverse('survey-page'))
    else:
        return HttpResponseRedirect(reverse('survey-first'))

def survey_first(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.session_key = "foo" #request.session.session_key.lower()
            participant.save()
            request.session['participant_id'] = participant.pk
            return HttpResponseRedirect(reverse('survey-page'))
    else:
        form = ParticipantForm()
    
    return render_to_response('first.html', {
                                             'form': form,
                                             },
                                             context_instance=RequestContext(request))

def survey_page(request):
    try:
        participant = Participant.objects.get(pk = request.session.get('participant_id',False))
    except Participant.DoesNotExist:
        return HttpResponseRedirect(reverse('survey-first'))
    #participant = get_object_or_404(Participant, pk = request.session.get('participant_id'))
    answered = Answer.objects.filter(participant = participant)
    unanswered = Question.objects.exclude(pk__in = answered.values_list('question', flat=True))
    unfinished = Answer.objects.filter(participant = participant, done=False)
    
    if not unanswered and not unfinished:
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
