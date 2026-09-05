
import multiprocessing
import queue

import base64
import json
import lzma
import os
import sys
import threading
import time



class APIQHandeler():

	base = None
	core = None

	worker_functions = {}


	def __init__(self, base, core):
		self.base = base
		self.core = core
		self.base.debugmsg(5, "init APIQHandeler")

		self.register_worker_functions()

	def register_worker_functions(self):
		self.worker_functions["test"] = self._test

		# V1 API
		# GET
		# "/", 
		self.worker_functions["index"] = self._index

		# POST
		# "/AgentStatus", 
		self.worker_functions["AgentStatus"] = self._AgentStatus
		# "/Jobs", 
		self.worker_functions["Jobs"] = self._Jobs
		# "/Scripts", 
		self.worker_functions["Scripts"] = self._Scripts
		# "/File", 
		self.worker_functions["File"] = self._File
		# "/Result", 
		self.worker_functions["Result"] = self._Result
		# "/Metric"
		self.worker_functions["Metric"] = self._Metric

		# V2 API

		# 

	def worker_loop(self):
		"""
		Each process receives a proxy to the shared_state 
		and a reference to the shared task queue.
		"""
		self.base.debugmsg(5, f"Starting")

		# task_queue = self.base.q_api_resquest
		# result_queue = self.base.q_api_ressult

		while self.base.q_api_resquest.empty() and self.base.keeprunning:
			self.base.debugmsg(9, f"q_api_resquest empty: {self.base.q_api_resquest.empty()}, keeprunning: {self.base.keeprunning}")
			time.sleep(0.1)

		# logger = self.core.logger.Logger(shared_state["config_log_level"])
		while self.base.q_api_resquest.empty() == False or self.base.keeprunning:
			self.base.debugmsg(9, f"q_api_resquest empty: {self.base.q_api_resquest.empty()}, keeprunning: {self.base.keeprunning}")

			status = "200"
			message = ""

			task_data = None

			try:
				task_data = self.base.q_api_resquest.get(timeout=1)
				self.base.debugmsg(5, f"Processing: {task_data}")
				# time.sleep(1) 

				# confirm if the taskdata is formatted correctly

				if "job_id" not in task_data.keys():
					message = "Missing job_id"
					status = "404"

				if "function" not in task_data.keys():
					message = "Missing function"
					status = "404"

				if "args" not in task_data.keys():
					message = "Missing job_id"
					status = "404"

				if task_data["function"] not in self.worker_functions:
					message = f"Function {task_data["function"]} not supported"
					status = "404"

				try:
					result = self.worker_functions[task_data["function"]](task_data["args"])

					message = result["message"]
					status = result["status"]

				except Exception as e:
					message = f"Exception: {e}"
					status = "500"
					self.base.debugmsg(5, f"Exception: {e}")


			except Exception as e:
				message = f"queue empty: {e}"
				status = "500"
				self.base.debugmsg(9, f"queue empty: {e}")

			if task_data:
				result = {
					"job_id" : task_data["job_id"],
					"status" : status,
					"result" : message,
				}
				self.base.debugmsg(5, f"result: {result}")
				self.base.q_api_ressult.put(result)

			# time.sleep(0.1)

			# if task_data is None:  # Sentinel to stop
			# 	break
				
			# Perform CPU-intensive work here
			# print(f"Processing: {task_data}")
			# self.base.debugmsg(5, f"Processing: {task_data}")
			# time.sleep(1) 
			
			# Update the shared manager dictionary
			# Because it's a Manager.dict(), this update 
			# is reflected across all processes.
			# shared_state[f"result_{task_data}"] = "Success"
			# shared_dict["results"][f"result_{task_data}"] = "Success"
			# shared_dict.results[f"result_{task_data}"] = "Success"
			# results = shared_dict["results"]
			# results[f"result_{task_data}"] = "Success"

			# config = shared_state["config"]
			# config["curriter"] += 1
			# shared_state["curriter"] += 1
			
			# self.base.q_api_resquest.task_done()
		self.base.debugmsg(5, f"Finished")

	def _test(self, *args):
		self.base.debugmsg(5, f"test: {args}")
		return {
			"status": "200",
			"message": f"test: {args}"
		}
		

	def _index(self, *args):
		indexdata = """
		{
			"POST": {
				"AgentStatus": {
					"URI": "/AgentStatus",
					"Body": {
						"AgentName": "<Agent Host Name>",
						"Status": "<Agent Status>",
						"AgentIPs": [
							"<Agent IP Address>",
							"<Agent IP Address>"
						],
						"Robots": "<sum>",
						"CPU%": "0-100",
						"MEM%": "0-100",
						"NET%": "0-100"
					}
				},
				"Jobs": {
					"URI": "/Jobs",
					"Body": {
						"AgentName": "<Agent Host Name>"
					}
				},
				"Scripts": {
					"URI": "/Scripts",
					"Body": {
						"AgentName": "<Agent Host Name>"
					}
				},
				"File": {
					"URI": "/File",
					"Body": {
						"AgentName": "<Agent Host Name>",
						"Action": "<Upload/Download/Status>",
						"Hash": "<File Hash, provided by /Scripts>"
					}
				},
				"Result": {
					"URI": "/Result",
					"Body": {
						"AgentName": "<Agent Host Name>",
						"ResultName": "<A Text String>",
						"Result": "<PASS | FAIL>",
						"ElapsedTime": "<seconds as decimal number>",
						"StartTime": "<epoch seconds as decimal number>",
						"EndTime": "<epoch seconds as decimal number>",
						"ScriptIndex": "<Index>",
						"Robot": "<user number>",
						"Iteration": "<iteration number>",
						"Sequence": "<sequence number that ResultName occurred in test case>"
					}
				},
				"Metric": {
					"URI": "/Metric",
					"Body": {
						"PrimaryMetric": "<primary metric name, e.g. AUT Hostname>",
						"MetricType": "<metric type, e.g. AUT Web Server>",
						"MetricTime": "<epoch time the metric was recorded>",
						"SecondaryMetrics": {
							"Secondary Metric Name, e.g. CPU%": "<value, e.g. 60>",
							"Secondary Metric Name, e.g. MEMUser": "<value, e.g. 256Mb>",
							"Secondary Metric Name, e.g. MEMSys": "<value, e.g. 1Gb>",
							"Secondary Metric Name, e.g. MEMFree": "<value, e.g. 2Gb>",
							"Secondary Metric Name, e.g. CPUCount": "<value, e.g. 4>"
						}
					}
				}
			}
		}
		"""
		return indexdata
	
	# "/AgentStatus", 
	def _AgentStatus(self, *args):

		jsonresp = {}
		httpcode = 200
		message = ""
		self.base.debugmsg(5, f"args: {args}")
		jsonreq = args[0]

		requiredfields = ["AgentName", "Status", "Robots", "CPU%", "MEM%", "NET%"]
		for field in requiredfields:
			if field not in jsonreq:
				httpcode = 422
				message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
				break

		if httpcode == 200:
			self.base.debugmsg(9, "jsonreq:", jsonreq)
			self.core.register_agent(jsonreq)
			jsonresp["AgentName"] = jsonreq["AgentName"]
			jsonresp["Status"] = "Updated"
			message = json.dumps(jsonresp)

		self.base.debugmsg(5, "httpcode:", httpcode, "	message:", message)
		return {
			"status": httpcode,
			"message": message
		}

	# "/Jobs", 
	def _Jobs(self, *args):

		jsonresp = {}
		httpcode = 200
		message = ""
		self.base.debugmsg(5, f"args: {args}")
		jsonreq = args[0]

		requiredfields = ["AgentName"]
		for field in requiredfields:
			if field not in jsonreq:
				httpcode = 422
				message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
				break

		if httpcode == 200:

			jsonresp["AgentName"] = jsonreq["AgentName"]
			jsonresp["StartTime"] = self.base.run_start
			jsonresp["EndTime"] = self.base.run_end
			jsonresp["RunName"] = self.base.robot_schedule["RunName"]
			jsonresp["Abort"] = self.base.run_abort
			jsonresp["UploadMode"] = self.base.uploadmode
			jsonresp["EnvironmentVariables"] = self.base.envvars

			# self.base.robot_schedule["Agents"]
			if jsonresp["AgentName"] in self.base.robot_schedule["Agents"].keys():
				jsonresp["Schedule"] = self.base.robot_schedule["Agents"][jsonresp["AgentName"]]
			else:
				jsonresp["Schedule"] = {}

			message = json.dumps(jsonresp)

		self.base.debugmsg(5, "httpcode:", httpcode, "	message:", message)
		return {
			"status": httpcode,
			"message": message
		}

	# "/Scripts", 
	def _Scripts(self, *args):

		jsonresp = {}
		httpcode = 200
		message = ""
		self.base.debugmsg(5, f"args: {args}")
		jsonreq = args[0]

		requiredfields = ["AgentName"]
		for field in requiredfields:
			if field not in jsonreq:
				httpcode = 422
				message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
				break

		if httpcode == 200:
			jsonresp["AgentName"] = jsonreq["AgentName"]
			self.base.debugmsg(9, "self.base.scriptlist:", self.base.scriptlist)

			scripts = []
			self.base.debugmsg(9, "self.base.scriptfiles:", self.base.scriptfiles)
			for hash in self.base.scriptfiles:
				self.base.debugmsg(9, "hash:", hash, self.base.scriptfiles[hash])
				scripts.append({'File': self.base.scriptfiles[hash]['relpath'], "Hash": hash})
			self.base.debugmsg(9, "scripts:", scripts)
			jsonresp["Scripts"] = scripts

			t = threading.Thread(target=self.base.check_files_changed)
			t.start()

			message = json.dumps(jsonresp)

		self.base.debugmsg(5, "httpcode:", httpcode, "	message:", message)
		return {
			"status": httpcode,
			"message": message
		}

	# "/File", 
	def _File(self, *args):

		jsonresp = {}
		httpcode = 200
		message = ""
		self.base.debugmsg(5, f"args: {args}")
		jsonreq = args[0]

		requiredfields = ["AgentName", "Hash"]
		# requiredfields = ["AgentName", "Action", "Hash"]
		for field in requiredfields:
			if field not in jsonreq:
				httpcode = 422
				message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
				break

		if httpcode == 200:

			jsonresp["AgentName"] = jsonreq["AgentName"]
			if "Action" in jsonreq and len(jsonreq["Action"]) > 0 and jsonreq["Action"] in ["Upload", "Download", "Status"]:
				if jsonreq["Action"] == "Download":
					if "Hash" in jsonreq and len(jsonreq["Hash"]) > 0 and jsonreq["Hash"] in self.base.scriptfiles:
						hash = jsonreq["Hash"]
						jsonresp["Hash"] = jsonreq["Hash"]
						jsonresp["File"] = self.base.scriptfiles[hash]['relpath']
						localpath = self.base.scriptfiles[hash]['localpath']
						buf = "\n"
						with open(localpath, 'rb') as afile:
							buf = afile.read()
						self.base.debugmsg(9, "buf:", buf)
						compressed = lzma.compress(buf)
						self.base.debugmsg(9, "compressed:", compressed)
						encoded = base64.b64encode(compressed)
						self.base.debugmsg(9, "encoded:", encoded)

						jsonresp["FileData"] = encoded.decode('ASCII')

					else:
						httpcode = 404
						jsonresp["Message"] = "Known File Hash required to download a file"

				if jsonreq["Action"] == "Status":
					if "Hash" in jsonreq and len(jsonreq["Hash"]) > 0:
						jsonresp["Hash"] = jsonreq["Hash"]
						if jsonreq["Hash"] in self.base.scriptfiles or jsonreq["Hash"] in self.base.uploadfiles:
							jsonresp["Exists"] = "True"
						else:
							jsonresp["Exists"] = "False"
					else:
						httpcode = 404
						jsonresp["Message"] = "File Hash required to check file status"

				if jsonreq["Action"] == "Upload":
					#
					# 	TODO: Receive Upload file
					#
					if "Hash" in jsonreq and len(jsonreq["Hash"]) > 0:
						jsonresp["Hash"] = jsonreq["Hash"]
						if jsonreq["Hash"] in self.base.uploadfiles:
							jsonresp["Result"] = "Exists"
						else:
							# self.base.debugmsg(5, "jsonreq:", jsonreq)
							# jsonreq: {
							# 		'AgentName': 'DavesMBP',
							# 		'Action': 'Upload',
							# 		'Hash': 'e7b73742ee1c3d558c4d20adf639d8d8',
							# 		'File': 'OC_Demo_2_1_3_1608352678_1_1608352681/Browse_Store_Product_1.log',
							# 		'FileData': <filedata>
							# 	}
							logdir = os.path.join(self.base.datapath, "logs")
							if os.path.exists(logdir) and os.path.isfile(logdir):
								logdir = os.path.join(self.base.datapath, "logs" + str(int(time.time())))

							self.base.debugmsg(7, "logdir:", logdir)
							relpath = jsonreq['File']
							if '\\' in relpath:
								relpatharr = relpath.split('\\')
							else:
								relpatharr = relpath.split('/')
							localpath = os.path.join(logdir, *relpatharr)
							self.base.debugmsg(7, "localpath:", localpath)
							jsonreq['LocalFile'] = localpath
							self.base.uploadfiles[jsonreq["Hash"]] = jsonreq

							t = threading.Thread(target=self.base.save_upload_file, args=(jsonreq["Hash"],))
							t.start()

							jsonresp["Result"] = "Saved"

			else:
				httpcode = 404
				jsonresp["Message"] = "Unknown Action"


		self.base.debugmsg(5, f"Not Implimented: {args}")
		return {
			"status": "500",
			"message": f"Not Implimented: {args}"
		}

	# "/Result", 
	def _Result(self, *args):

		jsonresp = {}
		httpcode = 200
		message = ""
		self.base.debugmsg(5, f"args: {args}")
		jsonreq = args[0]

		self.base.debugmsg(6, "Result: jsonreq:", jsonreq)
		requiredfields = ["AgentName", "ResultName", "Result", "ElapsedTime", "StartTime", "EndTime", "ScriptIndex", "Iteration", "Sequence"]
		for field in requiredfields:
			if field not in jsonreq:
				httpcode = 422
				message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
				self.base.debugmsg(5, httpcode, ":", message)
				break

		if "Robot" not in jsonreq:
			jsonreq["Robot"] = 0
			if "VUser" in jsonreq:
				jsonreq["Robot"] = jsonreq["VUser"]

		if httpcode == 200:
			self.base.debugmsg(7, "Result: httpcode:", httpcode)
			jsonresp["AgentName"] = jsonreq["AgentName"]

			self.core.register_result(
				jsonreq["AgentName"], jsonreq["ResultName"], jsonreq["Result"],
				jsonreq["ElapsedTime"], jsonreq["StartTime"], jsonreq["EndTime"],
				jsonreq["ScriptIndex"], jsonreq["Robot"], jsonreq["Iteration"],
				jsonreq["Sequence"]
			)

			jsonresp["Result"] = "Queued"
			self.base.debugmsg(7, "Result: jsonresp[\"Result\"]:", jsonresp["Result"])

			message = json.dumps(jsonresp)

		self.base.debugmsg(5, "httpcode:", httpcode, "	message:", message)
		return {
			"status": httpcode,
			"message": message
		}

	# "/Metric"
	def _Metric(self, *args):

		jsonresp = {}
		httpcode = 200
		message = ""
		self.base.debugmsg(5, f"args: {args}")
		jsonreq = args[0]

		self.base.debugmsg(7, "_Metric: jsonreq:", jsonreq)
		requiredfields = ["AgentName", "PrimaryMetric", "MetricType", "MetricTime", "SecondaryMetrics"]
		for field in requiredfields:
			if field not in jsonreq:
				httpcode = 422
				message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
				self.base.debugmsg(9, httpcode, ":", message)
				break

		if httpcode == 200:
			self.base.debugmsg(7, "Result: httpcode:", httpcode)
			jsonresp["Metric"] = jsonreq["PrimaryMetric"]

			# self.core.register_metric(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"], jsonreq["AgentName"])
			t = threading.Thread(target=self.core.register_metric, args=(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"], jsonreq["AgentName"]))
			t.start()

			jsonresp["Result"] = "Queued"
			self.base.debugmsg(7, "Metric: jsonresp[\"Metric\"]:", jsonresp["Metric"])

			message = json.dumps(jsonresp)

		self.base.debugmsg(5, "httpcode:", httpcode, "	message:", message)
		return {
			"status": httpcode,
			"message": message
		}





# 
