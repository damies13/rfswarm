#!/usr/bin/python
#
# 	Robot Framework Swarm
# 		Manager
#    Version 2.0.0
#

# 	Helpful links
#
#
import multiprocessing
# import queue

import argparse
import base64
import configparser
import csv
import hashlib
import glob
import errno
import importlib.metadata
import ipaddress
import json
import lzma
import os
import platform
import shutil
import signal
import socket
import sqlite3
import sys
import threading
import time
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import matplotlib  # required for matplot graphs
import yaml


class AgentServer(BaseHTTPRequestHandler):

	def do_HEAD(self):
		return

	def do_POST(self):

		self.base = self.server.base
		self.core = self.server.core

		threadstart = time.time()
		httpcode = 200
		try:
			parsed_path = urllib.parse.urlparse(self.path)
			self.base.debugmsg(7, "parsed_path.path", parsed_path.path)
			if (parsed_path.path in ["/AgentStatus", "/Jobs", "/Scripts", "/File", "/Result", "/Metric"]):

				jsonresp = {}
				rawData = (self.rfile.read(int(self.headers['content-length']))).decode('utf-8')
				self.base.debugmsg(7, "rawData: ", rawData)
				self.base.debugmsg(9, "parsed_path.path", parsed_path.path)
				if parsed_path.path == "/AgentStatus":
					jsonreq = json.loads(rawData)

					requiredfields = ["AgentName", "Status", "Robots", "CPU%", "MEM%", "NET%"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							break

					if httpcode == 200:
						self.base.debugmsg(9, "do_POST: jsonreq:", jsonreq)
						self.core.register_agent(jsonreq)
						jsonresp["AgentName"] = jsonreq["AgentName"]
						jsonresp["Status"] = "Updated"

						# job = {
						# 	"job_id": "POST",
						# 	"function": "AgentStatus",
						# 	# "function": self.path[1:],
						# 	"args": jsonreq,
						# }
						# self.base.debugmsg(5, "job:", job)
						# self.base.q_api_resquest.put(job)

				if parsed_path.path == "/Scripts":
					jsonreq = json.loads(rawData)
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

				if parsed_path.path == "/File":
					jsonreq = json.loads(rawData)

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

				if parsed_path.path == "/Jobs":
					jsonreq = json.loads(rawData)

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

				# , "Result"
				if parsed_path.path == "/Result":
					jsonreq = json.loads(rawData)
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

				if parsed_path.path == "/Metric":
					self.base.debugmsg(7, "Metric")
					jsonreq = json.loads(rawData)
					self.base.debugmsg(7, "Metric: jsonreq:", jsonreq)
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

				self.base.debugmsg(7, "jsonresp:", jsonresp)
				message = json.dumps(jsonresp)
			else:
				httpcode = 404
				message = "Unrecognised request: '{}'".format(parsed_path)

		except Exception as e:
			self.base.debugmsg(6, "AgentServer: do_POST:", e)
			httpcode = 500
			message = str(e)
		self.send_response(httpcode)
		try:
			self.end_headers()
			self.wfile.write(bytes(message, "utf-8"))
		except Exception as e:
			self.base.debugmsg(6, "Disconnected before response was sent:", e)
		threadend = time.time()
		# self.base.debugmsg(5, parsed_path.path, "	threadstart:", "%.3f" % threadstart, "threadend:", "%.3f" % threadend, "Time Taken:", "%.3f" % (threadend-threadstart))
		self.base.debugmsg(7, "%.3f" % (threadend - threadstart), "seconds for ", parsed_path.path)

		# job = {
		# 	"job_id": "POST",
		# 	"function": "test",
		# 	# "function": self.path[1:],
		# 	"args": self.path,
		# }
		# self.base.debugmsg(5, "job:", job)
		# self.base.q_api_resquest.put(job)

		return

	def do_GET(self):

		self.base = self.server.base
		self.core = self.server.core

		threadstart = time.time()
		httpcode = 200
		try:
			parsed_path = urllib.parse.urlparse(self.path)
			if parsed_path.path == '/':
				jsonresp = {}

				jsonresp["POST"] = {}
				jsonresp["POST"]["AgentStatus"] = {}
				jsonresp["POST"]["AgentStatus"]["URI"] = "/AgentStatus"
				jsonresp["POST"]["AgentStatus"]["Body"] = {}
				jsonresp["POST"]["AgentStatus"]["Body"]["AgentName"] = "<Agent Host Name>"
				jsonresp["POST"]["AgentStatus"]["Body"]["Status"] = "<Agent Status>"
				jsonresp["POST"]["AgentStatus"]["Body"]["AgentIPs"] = ["<Agent IP Address>", "<Agent IP Address>"]
				jsonresp["POST"]["AgentStatus"]["Body"]["Robots"] = "<sum>"
				jsonresp["POST"]["AgentStatus"]["Body"]["CPU%"] = "0-100"
				jsonresp["POST"]["AgentStatus"]["Body"]["MEM%"] = "0-100"
				jsonresp["POST"]["AgentStatus"]["Body"]["NET%"] = "0-100"

				jsonresp["POST"]["Jobs"] = {}
				jsonresp["POST"]["Jobs"]["URI"] = "/Jobs"
				jsonresp["POST"]["Jobs"]["Body"] = {}
				jsonresp["POST"]["Jobs"]["Body"]["AgentName"] = "<Agent Host Name>"

				jsonresp["POST"]["Scripts"] = {}
				jsonresp["POST"]["Scripts"]["URI"] = "/Scripts"
				jsonresp["POST"]["Scripts"]["Body"] = {}
				jsonresp["POST"]["Scripts"]["Body"]["AgentName"] = "<Agent Host Name>"

				jsonresp["POST"]["File"] = {}
				jsonresp["POST"]["File"]["URI"] = "/File"
				jsonresp["POST"]["File"]["Body"] = {}
				jsonresp["POST"]["File"]["Body"]["AgentName"] = "<Agent Host Name>"
				jsonresp["POST"]["File"]["Body"]["Action"] = "<Upload/Download/Status>"
				jsonresp["POST"]["File"]["Body"]["Hash"] = "<File Hash, provided by /Scripts>"

				jsonresp["POST"]["Result"] = {}
				jsonresp["POST"]["Result"]["URI"] = "/Result"
				jsonresp["POST"]["Result"]["Body"] = {}
				jsonresp["POST"]["Result"]["Body"]["AgentName"] = "<Agent Host Name>"
				jsonresp["POST"]["Result"]["Body"]["ResultName"] = "<A Text String>"
				jsonresp["POST"]["Result"]["Body"]["Result"] = "<PASS | FAIL>"
				jsonresp["POST"]["Result"]["Body"]["ElapsedTime"] = "<seconds as decimal number>"
				jsonresp["POST"]["Result"]["Body"]["StartTime"] = "<epoch seconds as decimal number>"
				jsonresp["POST"]["Result"]["Body"]["EndTime"] = "<epoch seconds as decimal number>"
				jsonresp["POST"]["Result"]["Body"]["ScriptIndex"] = "<Index>"
				jsonresp["POST"]["Result"]["Body"]["Robot"] = "<user number>"
				jsonresp["POST"]["Result"]["Body"]["Iteration"] = "<iteration number>"
				jsonresp["POST"]["Result"]["Body"]["Sequence"] = "<sequence number that ResultName occurred in test case>"

				jsonresp["POST"]["Metric"] = {}
				jsonresp["POST"]["Metric"]["URI"] = "/Metric"
				jsonresp["POST"]["Metric"]["Body"] = {}
				jsonresp["POST"]["Metric"]["Body"]["PrimaryMetric"] = "<Primary Metric Name, e.g. AUT Hostname>"
				jsonresp["POST"]["Metric"]["Body"]["MetricType"] = "<Metric Type, e.g. AUT Web Server>"
				jsonresp["POST"]["Metric"]["Body"]["MetricTime"] = "<Epoch time the metric was recorded>"
				jsonresp["POST"]["Metric"]["Body"]["SecondaryMetrics"] = {}
				jsonresp["POST"]["Metric"]["Body"]["SecondaryMetrics"]["Secondary Metric Name, e.g. CPU%"] = "<Value, e.g. 60>"
				jsonresp["POST"]["Metric"]["Body"]["SecondaryMetrics"]["Secondary Metric Name, e.g. MEMUser"] = "<Value, e.g. 256Mb>"
				jsonresp["POST"]["Metric"]["Body"]["SecondaryMetrics"]["Secondary Metric Name, e.g. MEMSys"] = "<Value, e.g. 1Gb>"
				jsonresp["POST"]["Metric"]["Body"]["SecondaryMetrics"]["Secondary Metric Name, e.g. MEMFree"] = "<Value, e.g. 2Gb>"
				jsonresp["POST"]["Metric"]["Body"]["SecondaryMetrics"]["Secondary Metric Name, e.g. CPUCount"] = "<Value, e.g. 4>"

				message = json.dumps(jsonresp)
			else:
				httpcode = 404
				message = "Unrecognised request: '{}'".format(parsed_path)
		except Exception as e:
			self.base.debugmsg(6, "AgentServer: do_GET:", e)
			httpcode = 500
			message = str(e)

		self.send_response(httpcode)
		try:
			self.end_headers()
			self.wfile.write(bytes(message, "utf-8"))
		except Exception as e:
			self.base.debugmsg(6, "Disconnected before response was sent:", e)
		threadend = time.time()
		# self.base.debugmsg(5, parsed_path.path, "		threadstart:", "%.3f" % threadstart, "threadend:", "%.3f" % threadend, "Time Taken:", "%.3f" % (threadend-threadstart))
		self.base.debugmsg(5, "%.3f" % (threadend - threadstart), "seconds for ", parsed_path.path)
		return

	def handle_http(self):
		return

	def respond(self):
		return

	# 	log_request is here to stop BaseHTTPRequestHandler logging to the console
	# 		https://stackoverflow.com/questions/10651052/how-to-quiet-simplehttpserver/10651257#10651257
	def log_request(self, code='-', size='-'):
		pass

