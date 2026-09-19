
import uuid
import json

from django.http import JsonResponse
from datetime import datetime
from django.conf import settings  # <--- Add this import

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

# @ensure_csrf_cookie
@csrf_exempt
def get_index(request):
	myid = uuid.uuid4()

	print(f"get_index: request: {request}")

	myid_str = str(myid)
	print(f"post_scripts: myid_str: {myid_str}")


	job = {
		"job_id": myid_str,
		"function": "index",
		"args": ""
	}

	settings.Q_API_RESQUEST.put(job)
	

	rid = ""
	rjob = {'result': ""}
	while settings.SHARED_STATE['KeepRunning'] and rid != myid_str:
		try:
			rjob = settings.Q_API_RESULT.get(block=True, timeout=1)
			rid = rjob["job_id"]
			if rid != myid_str:
				Q_API_RESULT.put(rjob)
				# time.sleep(1)
		except:
			pass

	print(f"get_index: {rjob}")

	return JsonResponse(rjob)


	# # "/AgentStatus", 
    # path('AgentStatus', views.get_agent_status, name='AgentStatus'), 
@csrf_exempt
def post_agent_status(request):

	print(f"post_agent_status: request: {request}")
	if request.method == 'POST':
		myid = uuid.uuid4()

		myid_str = str(myid)
		print(f"post_scripts: myid_str: {myid_str}")

		jbody = json.loads(request.body)
		print(f"post_scripts: jbody: {jbody}")

		job = {
			"job_id": myid_str,
			"function": "AgentStatus",
			"args": jbody
		}

		settings.Q_API_RESQUEST.put(job)

		rid = ""
		rjob = {'result': ""}
		while settings.SHARED_STATE['KeepRunning'] and rid != myid_str:
			try:
				rjob = settings.Q_API_RESULT.get(block=True, timeout=1)
				rid = rjob["job_id"]
				if rid != myid_str:
					Q_API_RESULT.put(rjob)
					# time.sleep(1)
			except:
				pass

		print(f"post_agent_status: {rjob}")
		# return JsonResponse({
		# 	"id": rjob["result"],
		# 	"job": rjob,
		# 	"status": "success"
		# })
		return JsonResponse(rjob['result'])

	# # "/Jobs", 
    # path('Jobs', views.get_jobs, name='Jobs'), 
@csrf_exempt
def post_jobs(request):

	print(f"post_jobs: request: {request}")
	if request.method == 'POST':
		myid = uuid.uuid4()

		myid_str = str(myid)
		print(f"post_scripts: myid_str: {myid_str}")

		jbody = json.loads(request.body)
		print(f"post_scripts: jbody: {jbody}")

		job = {
			"job_id": myid_str,
			"function": "Jobs",
			"args": jbody
		}

		settings.Q_API_RESQUEST.put(job)

		rid = ""
		rjob = {'result': ""}
		while settings.SHARED_STATE['KeepRunning'] and rid != myid_str:
			try:
				rjob = settings.Q_API_RESULT.get(block=True, timeout=1)
				rid = rjob["job_id"]
				if rid != myid_str:
					Q_API_RESULT.put(rjob)
					# time.sleep(1)
			except:
				pass

		print(f"post_jobs: {rjob}")
		# return JsonResponse({
		# 	"id": rjob["result"],
		# 	"job": rjob,
		# 	"status": "success"
		# })
		return JsonResponse(rjob['result'])

	# pass

	# # "/Scripts", 
    # path('Scripts', views.get_scripts, name='Scripts'), 
@csrf_exempt
def post_scripts(request):

	print(f"post_scripts: request: {request}")
	if request.method == 'POST':
		myid = uuid.uuid4()

		myid_str = str(myid)
		print(f"post_scripts: myid_str: {myid_str}")

		jbody = json.loads(request.body)
		print(f"post_scripts: jbody: {jbody}")

		job = {
			"job_id": myid_str,
			"function": "Scripts",
			"args": jbody
		}

		settings.Q_API_RESQUEST.put(job)

		rid = ""
		rjob = {'result': ""}
		while settings.SHARED_STATE['KeepRunning'] and rid != myid_str:
			try:
				rjob = settings.Q_API_RESULT.get(block=True, timeout=1)
				rid = rjob["job_id"]
				if rid != myid_str:
					Q_API_RESULT.put(rjob)
					# time.sleep(1)
			except:
				pass

		print(f"post_scripts: {rjob}")
		# return JsonResponse({
		# 	"id": rjob["result"],
		# 	"job": rjob,
		# 	"status": "success"
		# })
		return JsonResponse(rjob['result'])

	# pass

	# # "/File", 
    # path('File', views.get_file, name='File'), 
@csrf_exempt
def post_file(request):

	print(f"post_file: request: {request}")
	if request.method == 'POST':
		myid = uuid.uuid4()

		myid_str = str(myid)
		print(f"post_scripts: myid_str: {myid_str}")

		jbody = json.loads(request.body)
		print(f"post_scripts: jbody: {jbody}")

		job = {
			"job_id": myid_str,
			"function": "File",
			"args": jbody
		}

		settings.Q_API_RESQUEST.put(job)

		rid = ""
		rjob = {'result': ""}
		while settings.SHARED_STATE['KeepRunning'] and rid != myid_str:
			try:
				rjob = settings.Q_API_RESULT.get(block=True, timeout=1)
				rid = rjob["job_id"]
				if rid != myid_str:
					Q_API_RESULT.put(rjob)
					# time.sleep(1)
			except:
				pass

		print(f"post_file: {rjob}")
		# return JsonResponse({
		# 	"id": rjob["result"],
		# 	"job": rjob,
		# 	"status": "success"
		# })
		return JsonResponse(rjob['result'])

	# pass

	# # "/Result", 
    # path('Result', views.get_result, name='Result'), 
@csrf_exempt
def post_result(request):

	print(f"post_result: request: {request}")
	if request.method == 'POST':
		myid = uuid.uuid4()

		myid_str = str(myid)
		print(f"post_scripts: myid_str: {myid_str}")

		jbody = json.loads(request.body)
		print(f"post_scripts: jbody: {jbody}")

		job = {
			"job_id": myid_str,
			"function": "Result",
			"args": jbody
		}

		settings.Q_API_RESQUEST.put(job)

		rid = ""
		rjob = {'result': ""}
		while settings.SHARED_STATE['KeepRunning'] and rid != myid_str:
			try:
				rjob = settings.Q_API_RESULT.get(block=True, timeout=1)
				rid = rjob["job_id"]
				if rid != myid_str:
					Q_API_RESULT.put(rjob)
					# time.sleep(1)
			except:
				pass

		print(f"post_result: {rjob}")
		# return JsonResponse({
		# 	"id": rjob["result"],
		# 	"job": rjob,
		# 	"status": "success"
		# })
		return JsonResponse(rjob['result'])

	# pass
	
	# # "/Metric"
    # path('Metric', views.get_metric, name='Metric'), 
@csrf_exempt
def post_metric(request):

	print(f"post_metric: request: {request}")
	if request.method == 'POST':
		myid = uuid.uuid4()

		myid_str = str(myid)
		print(f"post_scripts: myid_str: {myid_str}")

		jbody = json.loads(request.body)
		print(f"post_scripts: jbody: {jbody}")

		job = {
			"job_id": myid_str,
			"function": "Metric",
			"args": jbody
		}

		settings.Q_API_RESQUEST.put(job)

		rid = ""
		rjob = {'result': ""}
		while settings.SHARED_STATE['KeepRunning'] and rid != myid_str:
			try:
				rjob = settings.Q_API_RESULT.get(block=True, timeout=1)
				rid = rjob["job_id"]
				if rid != myid_str:
					Q_API_RESULT.put(rjob)
					# time.sleep(1)
			except:
				pass

		print(f"post_metric: {rjob}")
		# return JsonResponse({
		# 	"id": rjob["result"],
		# 	"job": rjob,
		# 	"status": "success"
		# })
		return JsonResponse(rjob['result'])

	# pass
	






# def get_id_view(request):
# 	"""
# 	Example: Returns time and interacts with the shared queue.
# 	"""
# 	myid = uuid.uuid4()

# 	myid_str = str(myid)

# 	job = {
# 		"job_id": myid_str,
# 		"data": myid_str,
# 		"result": ""
# 	}

# 	# Push the ID onto the task queue for the workers to process
# 	# We use .put() which is the standard method for multiprocessing.Queue
# 	settings.Q_API_RESQUEST.put(job)

# 	rid = ""
# 	while rid != myid_str:
# 		rjob = settings.Q_API_RESULT.get(block=True)
# 		rid = rjob["job_id"]
# 		if rid != myid_str:
# 			Q_API_RESULT.put(rjob)
# 			# time.sleep(1)

# 	return JsonResponse({
# 		"id": rjob["result"],
# 		"job": rjob,
# 		"status": "success"
# 	})



# def time_view(request):
#     """
#     Example: Returns time and interacts with the shared queue.
#     """
#     # 1. Perform an action with the shared queue
#     # (e.g., log that the API was hit)
#     # push_to_queue(f"API hit at {datetime.now()}")

#     # 2. Get the current time
#     now = datetime.utcnow().isoformat()

#     # 3. Return response
#     return JsonResponse({
#         "current_time": now,
#         "status": "success"
#     })

# def process_data_view(request):
#     """
#     Example: A view that triggers a core logic function.
#     """
#     # Call a function from your core application
#     # result = core_logic.some_function()
    
#     # Or interact with the queue
#     # item = get_from_queue()
#     item = "None"
    
#     return JsonResponse({"received_from_queue": item})
