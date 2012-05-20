from django.conf.urls import patterns, url, include
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    
    url(r'first/$', 'survey.views.survey_first', name="survey-first"),
    url(r'thanks/$', direct_to_template, {'template' : "thanks.html"}, name="survey-thanks"),
    url(r'$', 'survey.views.survey_page', name="survey-page"),
    
)

