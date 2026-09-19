import multiprocessing
import os
import sys
from django.core.management import execute_from_command_line

# class TerminateException(Exception):
# 	pass

def run_django(q_api_resquest: multiprocessing.Queue, q_api_result: multiprocessing.Queue, shared_state: dict):
	"""Worker function to initialize and start Django."""
	# 1. Set the settings module
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RFSwarmDjango.django_project.settings")

	# 2. Inject the queue into a shared module or django.conf.settings 
	# so views can access it later.
	from django.conf import settings
	import django
	django.setup()

	# Attach the live queue to settings dynamically
	settings.Q_API_RESQUEST = q_api_resquest
	settings.Q_API_RESULT = q_api_result
	settings.SHARED_STATE = shared_state

	# 3. Start the development server (or uwsgi/gunicorn)
	# Using --noreload is CRITICAL to prevent Django from spawning its own subprocesses
	# sys.argv = ['manage.py', 'runserver', str(shared_state["Server_BindPort"]), '--noreload']
	arrcmd = ['manage.py', 'runserver', str(shared_state["Server_BindPort"]), '--noreload']
	execute_from_command_line(arrcmd)
	# try:
	# 	execute_from_command_line(sys.argv)
	# except Exception as e:
	# 	# catch errors when we terminate the process, 
	# 	# TODO: need to find a way to stop the process cleanly
	# 	print(f"Exception: {e}")
	# 	pass



	# 