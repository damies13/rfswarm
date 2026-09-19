# RFSwarmDjango/api_v1/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Matches GET requests to http://localhost:8000/api/time
    # path('time', views.time_view, name='api_time'), 
    # path('getid', views.get_id_view, name='get_id'), 
	# "/AgentStatus", 
    path('AgentStatus', views.post_agent_status, name='AgentStatus'), 
	# "/Jobs", 
    path('Jobs', views.post_jobs, name='Jobs'), 
	# "/Scripts", 
    path('Scripts', views.post_scripts, name='Scripts'), 
	# "/File", 
    path('File', views.post_file, name='File'), 
	# "/Result", 
    path('Result', views.post_result, name='Result'), 
	# "/Metric"
    path('Metric', views.post_metric, name='Metric'), 

	path('', views.get_index, name='index'), 
]


