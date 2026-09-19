import os
from django.core.wsgi import get_wsgi_application

# This sets the settings module used by the WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RFSwarmDjango.django_project.settings')

# This is the standard WSGI application
application = get_wsgi_application()
