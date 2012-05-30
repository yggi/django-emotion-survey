import os
import sys

base = os.path.dirname(os.path.dirname(__file__)) 
base_parent = os.path.dirname(base) 
sys.path.append(base)
sys.path.append(base_parent)


sys.path.insert(0, '/srv/www/surveyor/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'surveyor.settings'

from django.core.handlers.wsgi import WSGIHandler

application = WSGIHandler()
