from django.conf.urls import patterns, url, include
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    
    url(r'first/$', 'survey.views.survey_first', name="survey-first"),
    url(r'reset/$', 'survey.views.survey_reset', name="survey-reset"),
    url(r'check/$', direct_to_template, {'template' : "reset.html"}, name="survey-reset-check"),
    url(r'thanks/$', direct_to_template, {'template' : "thanks.html"}, name="survey-thanks"),
    url(r'$', 'survey.views.survey_page', name="survey-page"),
    
)

