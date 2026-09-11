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

if True:  # noqa: E402
	sys.path.append(os.path.abspath(os.path.dirname(__file__)))
	from RFSwarmBase import RFSwarmBase
	from RFSwarmGUItk import RFSwarmGUItk

from APIQHandeler import APIQHandeler
from RFSwarmGUIhtml import RFSwarmGUIhtml
from RFSwarmV2API import RFSwarmV2API

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# required for matplot graphs
from matplotlib.figure import Figure  # required for matplot graphs

matplotlib.use("TkAgg")  # required for matplot graphs

__name__ = "rfswarm"


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


class RFSwarmCore:

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# core application
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def __init__(self, master=None):
		self.base = RFSwarmBase()
		self.base.debugmsg(0, "Robot Framework Swarm: Manager")
		self.base.debugmsg(0, "	Version", self.base.version)
		signal.signal(signal.SIGINT, self.on_closing)

		self.base.debugmsg(9, "ArgumentParser")
		# Check for command line args
		parser = argparse.ArgumentParser()
		parser.add_argument('-g', '--debug', help='Set debug level, default level is 0')
		parser.add_argument('-v', '--version', help='Display the version and exit', action='store_true')
		parser.add_argument('-i', '--ini', help='path to alternate ini file')
		parser.add_argument('-s', '--scenario', help='Load this scenario file')
		parser.add_argument('-r', '--run', help='Run the scenario automatically after loading', action='store_true')
		parser.add_argument('-a', '--agents', help='Wait for this many agents before starting (default 1)')
		parser.add_argument('-n', '--nogui', help='Don\'t display the GUI', action='store_true')
		parser.add_argument('-t', '--starttime', help='Specify the time to start the test HH:MM or HH:MM:SS (ISO 8601)')
		parser.add_argument('-d', '--dir', help='Results directory')
		parser.add_argument('-e', '--ipaddress', help='IP Address to bind the server to')
		parser.add_argument('-p', '--port', help='Port number to bind the server to')
		parser.add_argument('-c', '--create', help='ICON : Create application icon / shortcut')
		# to be deprecated by version 2.1
		parser.add_argument('-u', '--ui', help='[ V1 | V2 ] Specify which version of the GUI you want to use (default: V1)')

		self.base.args = parser.parse_args()
		self.base.core = self

		self.base.debugmsg(6, "self.base.args: ", self.base.args)

		if self.base.args.debug:
			self.base.debuglvl = int(self.base.args.debug)

		if self.base.args.version:
			self.show_additional_versions()
			exit()

		if self.base.args.create:
			if self.base.args.create.upper() in ["ICON", "ICONS"]:
				self.create_icons()
			else:
				self.base.debugmsg(0, "create with option ", self.base.args.create.upper(), "not supported.")
			exit()

		if self.base.args.starttime:
			self.base.run_starttime = self.base.parse_time(self.base.args.starttime)
			self.base.debugmsg(5, "run_starttime:", self.base.run_starttime)

		self.base.debugmsg(6, "ConfigParser")
		self.base.config = configparser.ConfigParser()
		scrdir = os.path.dirname(__file__)
		self.base.debugmsg(6, "scrdir: ", scrdir)
		#
		# 	ensure ini file
		#
		self.base.manager_ini = self.base.findiniloctaion()

		# rename old ini file if it exists
		# 	this section can probably be removed in the future, but will probably need to stay for at least a few releases
		self.base.gui_ini = os.path.join(scrdir, "RFSwarmGUI.ini")
		if os.path.isfile(self.base.gui_ini) and not os.path.isfile(self.base.manager_ini):
			try:
				os.rename(self.base.gui_ini, self.base.manager_ini)
			except Exception:
				pass

		# old ini file

		if self.base.args.ini:
			self.base.save_ini = False
			self.base.debugmsg(5, "self.base.args.ini: ", self.base.args.ini)
			self.base.manager_ini = self.base.args.ini

		if os.path.isfile(self.base.manager_ini):
			self.base.debugmsg(7, "agentini: ", self.base.manager_ini)
			arrconfigfile = os.path.splitext(self.base.manager_ini)
			self.base.debugmsg(5, "arrconfigfile: ", arrconfigfile)
			if len(arrconfigfile) < 2:
				self.base.debugmsg(0, "Configuration file ", self.base.manager_ini, " missing extention, unable to determine supported format. Plesae use extentions .ini, .yaml or .json")
				exit()
			if arrconfigfile[1].lower() not in [".ini", ".yml", ".yaml", ".json"]:
				self.base.debugmsg(0, "Configuration file ", self.base.manager_ini, " has an invalid extention, unable to determine supported format. Plesae use extentions .ini, .yaml or .json")
				exit()
			if arrconfigfile[1].lower() == ".ini":
				self.base.config.read(self.base.manager_ini, encoding="utf8")
			else:
				configdict = {}
				if arrconfigfile[1].lower() in [".yml", ".yaml"]:
					# read yaml file
					self.base.debugmsg(5, "read yaml file")
					with open(self.base.manager_ini, 'r', encoding="utf-8") as f:
						configdict = yaml.safe_load(f)
						configdict = self.base.configparser_safe_dict(configdict)
						self.base.debugmsg(5, "configdict: ", configdict)
				if arrconfigfile[1].lower() == ".json":
					# read json file
					self.base.debugmsg(5, "read json file")
					with open(self.base.manager_ini, 'r', encoding="utf-8") as f:
						configdict = json.load(f)
						configdict = self.base.configparser_safe_dict(configdict)
						self.base.debugmsg(5, "configdict: ", configdict)
				self.base.debugmsg(5, "configdict: ", configdict)
				self.base.config.read_dict(configdict)
		else:
			self.base.saveini()

		self.base.debugmsg(0, "	Configuration File: ", self.base.manager_ini)

		self.base.debugmsg(9, "self.base.config: ", self.base.config._sections)
		if self.base.args.scenario:
			self.base.save_ini = False
			self.base.debugmsg(5, "self.base.args.scenario: ", self.base.args.scenario)
			scenariofile = os.path.abspath(self.base.args.scenario)
			self.base.debugmsg(5, "scenariofile: ", scenariofile)
			if 'Plan' not in self.base.config:
				self.base.config['Plan'] = {}
				self.base.config['Plan']['ScenarioFile'] = ""
			self.base.debugmsg(6, "Plan:scenariofile: ", self.base.config['Plan']['ScenarioFile'])
			self.base.config['Plan']['ScenarioFile'] = self.base.inisafevalue(scenariofile)
			self.base.debugmsg(6, "Plan:scenariofile: ", self.base.config['Plan']['ScenarioFile'])

		if self.base.args.dir:
			self.base.save_ini = False
			self.base.debugmsg(5, "self.base.args.dir: ", self.base.args.dir)
			ResultsDir = os.path.abspath(self.base.args.dir)
			self.base.debugmsg(5, "ResultsDir: ", ResultsDir)
			if 'Run' not in self.base.config:
				self.base.config['Run'] = {}
			self.base.config['Run']['ResultsDir'] = self.base.inisafevalue(ResultsDir)

		if self.base.args.ipaddress:
			self.base.save_ini = False
			self.base.debugmsg(5, "self.base.args.ipaddress: ", self.base.args.ipaddress)
			if 'Server' not in self.base.config:
				self.base.config['Server'] = {}
			self.base.config['Server']['BindIP'] = self.base.inisafevalue(self.base.args.ipaddress)

		if self.base.args.port:
			self.base.save_ini = False
			self.base.debugmsg(5, "self.base.args.port: ", self.base.args.port)
			if 'Server' not in self.base.config:
				self.base.config['Server'] = {}
			self.base.config['Server']['BindPort'] = self.base.inisafevalue(self.base.args.port)

		#
		# GUI
		#

		if 'GUI' not in self.base.config:
			self.base.config['GUI'] = {}
			self.base.saveini()

		if 'win_width' not in self.base.config['GUI']:
			self.base.config['GUI']['win_width'] = "800"
			self.base.saveini()

		if 'win_height' not in self.base.config['GUI']:
			self.base.config['GUI']['win_height'] = "390"
			self.base.saveini()

		if 'graph_list' not in self.base.config['GUI']:
			self.base.config['GUI']['graph_list'] = ""
			self.base.saveini()

		#
		# Plan
		#

		if 'Plan' not in self.base.config:
			self.base.config['Plan'] = {}
			self.base.saveini()

		if 'ScriptDir' not in self.base.config['Plan']:
			self.base.config['Plan']['ScriptDir'] = self.base.inisafedir(self.base.dir_path)
			self.base.debugmsg(5, "ScriptDir: ", self.base.config['Plan']['ScriptDir'])
			self.base.saveini()
		else:
			if not os.path.isdir(self.base.config['Plan']['ScriptDir']):
				self.base.config['Plan']['ScriptDir'] = self.base.inisafedir(self.base.dir_path)
				self.base.debugmsg(5, "ScriptDir: ", self.base.config['Plan']['ScriptDir'])
				self.base.saveini()

		if 'ScenarioDir' not in self.base.config['Plan']:
			self.base.config['Plan']['ScenarioDir'] = self.base.inisafedir(self.base.dir_path)
			self.base.saveini()
		else:
			if not os.path.isdir(self.base.config['Plan']['ScenarioDir']):
				self.base.config['Plan']['ScenarioDir'] = self.base.inisafedir(self.base.dir_path)
				self.base.saveini()

		missing_scenario = False
		if 'ScenarioFile' not in self.base.config['Plan']:
			self.base.config['Plan']['ScenarioFile'] = ""
			self.base.debugmsg(6, "Plan:scenariofile: ", self.base.config['Plan']['ScenarioFile'])
			self.base.saveini()
		else:
			# check file exists - it may have been deleted since rfswarm last ran with this ini file
			self.base.debugmsg(6, "Plan:scenariofile: ", self.base.config['Plan']['ScenarioFile'])
			if not os.path.exists(self.base.config['Plan']['ScenarioFile']):
				if len(self.base.config['Plan']['ScenarioFile']) > 1:
					missing_scenario = True
					msg = "Scenario file Not found:\n" + self.base.config['Plan']['ScenarioFile']
				self.base.config['Plan']['ScenarioFile'] = ""
				self.base.debugmsg(6, "Plan:scenariofile: ", self.base.config['Plan']['ScenarioFile'])
				self.base.config['Plan']['ScriptDir'] = self.base.inisafedir(self.base.dir_path)
				self.base.debugmsg(5, "ScriptDir: ", self.base.config['Plan']['ScriptDir'])
				self.base.config['Plan']['ScenarioDir'] = self.base.inisafedir(self.base.dir_path)
				self.base.saveini()

		#
		# Monitoring
		#

		if 'Monitoring' not in self.base.config:
			self.base.config['Monitoring'] = {}
			self.base.saveini()

		if 'ScriptDir' not in self.base.config['Monitoring']:
			self.base.config['Monitoring']['ScriptDir'] = self.base.config['Plan']['ScriptDir']

		#
		# Run
		#

		if 'Run' not in self.base.config:
			self.base.config['Run'] = {}
			self.base.saveini()

		if 'ResultsDir' not in self.base.config['Run']:
			self.base.config['Run']['ResultsDir'] = self.base.inisafevalue(os.path.join(self.base.dir_path, "results"))
			self.base.saveini()
		else:
			if not os.path.isdir(self.base.config['Run']['ResultsDir']):
				self.base.config['Run']['ResultsDir'] = self.base.inisafevalue(self.base.dir_path)
				self.base.saveini()

		if 'display_index' not in self.base.config['Run']:
			self.base.config['Run']['display_index'] = str(False)
			self.base.saveini()

		if 'display_iteration' not in self.base.config['Run']:
			self.base.config['Run']['display_iteration'] = str(False)
			self.base.saveini()

		if 'display_sequence' not in self.base.config['Run']:
			self.base.config['Run']['display_sequence'] = str(False)
			self.base.saveini()

		if 'display_percentile' not in self.base.config['Run']:
			self.base.config['Run']['display_percentile'] = str(90)
			self.base.saveini()

		#
		# Server
		#

		if 'Server' not in self.base.config:
			self.base.config['Server'] = {}
			self.base.saveini()

		if 'BindIP' not in self.base.config['Server']:
			self.base.config['Server']['BindIP'] = ''
			self.base.saveini()

		if 'Config.Server.BindIP' not in self.base.shared_state:
			self.base.shared_state['Config.Server.BindIP'] = self.base.config['Server']['BindIP']

		if 'BindPort' not in self.base.config['Server']:
			self.base.config['Server']['BindPort'] = "8138"
			self.base.saveini()

		if 'Config.Server.BindPort' not in self.base.shared_state:
			self.base.shared_state['Config.Server.BindPort'] = self.base.config['Server']['BindPort']

		#
		# 	end ensure ini file
		#

		if not self.base.args.create and not self.base.args.nogui:
			self.check_icons("RFSwarm Manager")

		if self.base.args.nogui:
			self.base.save_ini = False
			if not self.base.args.run:
				self.base.args.run = True
		else:
			if self.base.args.ui:
				if self.base.args.ui.upper() in ["V1"]:
					self.base.gui = RFSwarmGUItk(base)

				if self.base.args.ui.upper() in ["V2"]:
					self.base.gui = RFSwarmGUIhtml(self.base, self)

			else:
				# run default
				self.base.gui = RFSwarmGUItk(self.base)
				# self.base.gui = RFSwarmGUIhtml()

		if missing_scenario:
			self.display_warning(msg)

		self.BuildCore()

		self.base.debugmsg(5, "run_agent_server")
		self.base.Agentserver = threading.Thread(target=self.run_agent_server)
		self.base.Agentserver.start()

		self.base.debugmsg(5, "run_v2_server")
		self.base.v2server = threading.Thread(target=self.run_v2_server)
		self.base.v2server.start()

		self.base.debugmsg(5, "run_db_thread")
		self.base.run_dbthread = True
		self.base.dbthread = threading.Thread(target=self.base.run_db_thread)
		self.base.dbthread.start()

		# APIQHandeler
		self.base.debugmsg(5, "run APIQHandeler")
		self.base.qhandler = APIQHandeler(self.base, self)
		self.base.qhthread = threading.Thread(target=self.base.qhandler.worker_loop)
		self.base.qhthread.start()


	def show_additional_versions(self):

		self.base.debugmsg(0, "	Dependancy Versions")
		try:
			self.base.debugmsg(0, "		Python Version", sys.version)
		except Exception as e:
			self.base.debugmsg(3, "error:", e)

		try:
			self.base.debugmsg(0, "		SQLite Version", sqlite3.sqlite_version)
		except Exception as e:
			self.base.debugmsg(3, "error:", e)

		try:
			import tkinter as tk
			self.base.debugmsg(0, "		Tcl/Tk Version", tk.Tcl().call("info", "patchlevel"))
		except Exception as e:
			self.base.debugmsg(3, "error:", e)

	def BuildCore(self):
		self.base.debugmsg(5, "BuildCore")

		self.base.debugmsg(6, "Plan:scenariofile: ", self.base.config['Plan']['ScenarioFile'])
		self.base.debugmsg(5, "BuildCorePlan")
		self.BuildCorePlan()
		self.base.debugmsg(5, "BuildCoreMonitoring")
		self.BuildCoreMonitoring()
		self.base.debugmsg(5, "BuildCoreRun")
		self.BuildCoreRun()

	def scheduled_start(self):
		while self.base.keeprunning:
			if self.base.run_starttime > 0:
				sec2st = self.base.run_starttime - int(time.time())
				if sec2st < 1:
					self.base.run_start = 0
					self.base.run_starttime = 0
					self.base.debugmsg(5, "sec2st:", sec2st)
					autostart = threading.Thread(target=self.autostart)
					autostart.start()
			time.sleep(1)

	def autostart(self):
		self.base.debugmsg(5, "appstarted:", self.base.appstarted)
		# wait for mainloops to finished
		while not self.base.appstarted:
			time.sleep(1)
			self.base.debugmsg(5, "appstarted:", self.base.appstarted)

		if self.base.run_start < 1:
			neededagents = 1
			if self.base.args.agents:
				neededagents = int(self.base.args.agents)

			self.base.debugmsg(5, "len(self.base.Agents):", len(self.base.Agents), "	neededagents:", neededagents)
			# agntlst = list(self.base.Agents.keys())
			# while len(self.base.Agents) < neededagents:
			while self.base.agents_ready() < neededagents and self.base.keeprunning:
				self.base.debugmsg(1, "Waiting for Agents")
				# self.base.debugmsg(3, "Agents:", len(self.base.Agents), "	Agents Needed:", neededagents)
				self.base.debugmsg(3, "Agents:", self.base.agents_ready(), "	Agents Needed:", neededagents)
				time.sleep(10)

			if self.base.keeprunning:
				if self.base.args.nogui:
					self.base.debugmsg(5, "core.ClickPlay")
					self.ClickPlay()
				else:
					self.base.debugmsg(5, "self.base.gui.ClickPlay")
					self.base.gui.ClickPlay()

	def mainloop(self):

		self.base.debugmsg(5, "mainloop start")

		if self.base.args.run and self.base.run_starttime < 1:
			# auto click play ?
			# self.autostart()
			autostart = threading.Thread(target=self.autostart)
			autostart.start()

		autostart = threading.Thread(target=self.scheduled_start)
		autostart.start()

		if not self.base.args.nogui:
			self.base.gui.mainloop()

		while self.base.run_dbthread:
			time.sleep(10)

		self.base.debugmsg(5, "mainloop end")

	def on_closing(self, _event=None, *args):
		# , _event=None is required for any function that has a shortcut key bound to it

		self.base.keeprunning = False
		self.base.shared_state['KeepRunning'] = False
		self.neededagents = 0

		if self.base.appstarted:
			try:
				self.base.debugmsg(0, "Shutdown Agent Manager")
				self.base.agenthttpserver.shutdown()
				self.base.debugmsg(9, "Shutdown Agent Manager after")
			except Exception:
				pass

		try:
			if self.base.Agentserver.is_alive():
				self.base.debugmsg(9, "Join Agent Manager Thread")
				self.base.Agentserver.join(timeout=30)
				self.base.debugmsg(9, "Join Agent Manager Thread after")
		except Exception:
			pass

		try:
			if self.base.qhandler.is_alive():
				self.base.debugmsg(9, "Join APIQHandeler Thread")
				self.base.qhandler.join(timeout=30)
				self.base.debugmsg(9, "Join APIQHandeler Thread after")
		except Exception:
			pass

		try:
			self.base.run_dbthread = False
			if self.base.dbthread.is_alive():
				self.base.debugmsg(9, "Join DB Thread")
				self.base.dbthread.join(timeout=30)
				self.base.debugmsg(9, "Join DB Thread after")
		except Exception:
			pass

		try:
			self.base.debugmsg(3, "Save ini File")
			self.base.saveini()
		except Exception:
			pass

		time.sleep(1)
		self.base.debugmsg(2, "Exit")
		try:
			sys.exit(0)
		except SystemExit as e:
			try:
				remaining_threads = [t for t in threading.enumerate() if t is not threading.main_thread() and t.is_alive()]
				if remaining_threads:
					self.base.debugmsg(5, "Failed to gracefully exit RFSwarm-Manager. Forcing immediate exit.")
					for thread in remaining_threads:
						self.base.debugmsg(9, "Thread name:", thread.name)
					os._exit(0)
				else:
					raise e

			except Exception as e:
				self.base.debugmsg(3, "Failed to exit with error:", e)
				os._exit(1)
		sys.stdout.flush()
		sys.stderr.flush()

	def create_icons(self):
		self.base.debugmsg(0, "Creating application icons for RFSwarm Manager")
		appname = "RFSwarm Manager"
		namelst = appname.split()
		self.base.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		self.base.debugmsg(6, "projname:", projname)
		pipdata = importlib.metadata.distribution(projname)
		# print("files:", pipdata.files)
		# print("file0:", pipdata.files[0])
		manager_executable = os.path.abspath(str(pipdata.locate_file(pipdata.files[0])))
		self.base.debugmsg(5, "manager_executable:", manager_executable)

		script_dir = os.path.dirname(os.path.abspath(__file__))
		self.base.debugmsg(5, "script_dir:", script_dir)
		icon_dir = os.path.join(pipdata.locate_file('rfswarm_manager'), "icons")
		self.base.debugmsg(5, "icon_dir:", icon_dir)

		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				try:
					self.base.ensuredir("/usr/share/applications")
					directoryfilename = os.path.join("/usr/share/applications", "rfswarm.directory")
					directorydata = ["test"]
					with open(directoryfilename, 'w') as df:
						df.writelines(directorydata)
					os.remove(directoryfilename)
					fileprefix = "/usr/share"
				except Exception:
					pass

			fileprefix = os.path.expanduser(fileprefix)

			# self.base.debugmsg(5, "Create .directory file")
			# directorydata = []
			# directorydata.append('[Desktop Entry]\n')
			# directorydata.append('Type=Directory\n')
			# directorydata.append('Name=RFSwarm\n')
			# directorydata.append('Icon=rfswarm-logo\n')
			#
			# directoryfilename = os.path.join(fileprefix, "desktop-directories", "rfswarm.directory")
			# directorydir = os.path.dirname(directoryfilename)
			# self.base.ensuredir(directorydir)
			#
			# self.base.debugmsg(5, "directoryfilename:", directoryfilename)
			# with open(directoryfilename, 'w') as df:
			# 	df.writelines(directorydata)
			#
			# directoryfilename = os.path.join(fileprefix, "applications", "rfswarm.directory")
			# directorydir = os.path.dirname(directoryfilename)
			# self.base.ensuredir(directorydir)
			# self.base.debugmsg(5, "directoryfilename:", directoryfilename)
			# with open(directoryfilename, 'w') as df:
			# 	df.writelines(directorydata)

			self.base.debugmsg(5, "Create .desktop file")
			desktopdata = []
			desktopdata.append('[Desktop Entry]\n')
			desktopdata.append('Name=' + appname + '\n')
			desktopdata.append('Exec=' + manager_executable + '\n')
			desktopdata.append('Terminal=false\n')
			desktopdata.append('Type=Application\n')
			desktopdata.append('Icon=' + projname + '\n')
			desktopdata.append('Categories=RFSwarm;Development;\n')
			desktopdata.append('Keywords=rfswarm;manager;\n')
			# desktopdata.append('\n')

			desktopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
			desktopdir = os.path.dirname(desktopfilename)
			self.base.ensuredir(desktopdir)

			self.base.debugmsg(5, "desktopfilename:", desktopfilename)
			with open(desktopfilename, 'w') as df:
				df.writelines(desktopdata)

			self.base.debugmsg(5, "Copy icons")
			# /usr/share/icons/hicolor/128x128/apps/
			# 	1024x1024  128x128  16x16  192x192  22x22  24x24  256x256  32x32  36x36  42x42  48x48  512x512  64x64  72x72  8x8  96x96
			# or
			#  ~/.local/share/icons/hicolor/256x256/apps/
			src_iconx128 = os.path.join(icon_dir, projname + "-128.png")
			self.base.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", projname + ".png")
			dst_icondir = os.path.dirname(dst_iconx128)
			self.base.ensuredir(dst_icondir)
			self.base.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

			src_iconx128 = os.path.join(icon_dir, "rfswarm-logo-128.png")
			self.base.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", "rfswarm-logo.png")
			self.base.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

		if platform.system() == 'Darwin':
			self.base.debugmsg(5, "Create folder structure in /Applications")

			src_iconx1024 = os.path.join(icon_dir, projname + "-1024.png")

			self.create_macos_app_bundle(appname, pipdata.version, manager_executable, src_iconx1024)

		if platform.system() == 'Windows':
			self.base.debugmsg(5, "Create Startmenu shorcuts")
			roam_appdata = os.environ["APPDATA"]
			scutpath = os.path.join(roam_appdata, "Microsoft", "Windows", "Start Menu", appname + ".lnk")
			# targetpath = "c:\\Users\\Dave\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\rfswarm.exe"
			# iconpath = "c:\\Users\\Dave\\AppData\\Local\\Programs\\Python\\Python311\\Lib\site-packages\\rfswarm_manager\\icons\\rfswarm-manager-128.ico"
			src_iconx128 = os.path.join(icon_dir, projname + "-128.ico")

			self.create_windows_shortcut(scutpath, manager_executable, src_iconx128, "Performance testing with robot test cases", True)

	def create_windows_shortcut(self, scutpath, targetpath, iconpath, desc, minimised=False):
		pslst = []

		directorydir = os.path.dirname(scutpath)
		self.base.ensuredir(directorydir)

		pslst.append("$wshshell = New-Object -COMObject wscript.shell")
		pslst.append('$scut = $wshshell.CreateShortcut("""' + scutpath + '""")')
		pslst.append('$scut.TargetPath = """' + targetpath + '"""')
		pslst.append('$scut.IconLocation = """' + iconpath + '"""')
		if minimised:
			pslst.append("$scut.WindowStyle = 7")
		pslst.append("$scut.Description = '" + desc + "'")
		pslst.append("$scut.Save()")

		# psscript = '\n'.join(pslst)
		psscript = '; '.join(pslst)
		self.base.debugmsg(6, "psscript:", psscript)

		response = os.popen('powershell.exe -command ' + psscript).read()

		self.base.debugmsg(6, "response:", response)

	def create_macos_app_bundle(self, name, version, exesrc, icosrc):

		appspath = "~/Applications"
		if os.access("/Applications", os.W_OK):
			appspath = "/Applications"

		appspath = os.path.expanduser(appspath)

		# https://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

		apppath = os.path.join(appspath, name + ".app")
		MacOSFolder = os.path.join(apppath, "Contents", "MacOS")
		self.base.ensuredir(MacOSFolder)

		# need to create the icon file:
		# https://stackoverflow.com/questions/646671/how-do-i-set-the-icon-for-my-applications-mac-os-x-app-bundle
		namelst = name.split()
		self.base.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		self.base.debugmsg(6, "projname:", projname)
		signature = "RFS{0}".format(namelst[1].upper())
		self.base.debugmsg(6, "signature:", signature)

		ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
		iconset = os.path.join(ResourcesFolder, projname + ".iconset")
		icnsfile = os.path.join(ResourcesFolder, projname + ".icns")
		self.base.ensuredir(iconset)

		# Normal screen icons
		self.base.debugmsg(6, "Normal screen icons")
		for size in [16, 32, 64, 128, 256, 512]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{0}x{0}.png'".format(size, icosrc, iconset)
			self.base.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			self.base.debugmsg(6, "response:", response)

		# Retina display icons
		self.base.debugmsg(6, "Retina display icons")
		for size in [32, 64, 128, 256, 512, 1024]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{3}x{3}x2.png'".format(size, icosrc, iconset, int(size / 2))
			self.base.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			self.base.debugmsg(6, "response:", response)

		# Make a multi-resolution Icon
		self.base.debugmsg(6, "Make a multi-resolution Icon")
		cmd = "iconutil -c icns -o '{0}' '{1}'".format(icnsfile, iconset)
		self.base.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		self.base.debugmsg(6, "response:", response)

		#  create apppath + "/Contents/Info.plist"
		bundleName = name
		bundleIdentifier = "org.rfswarm." + projname

		# https://stackoverflow.com/questions/1596945/building-osx-app-bundle
		# Found 2 issues:
		# 	- <xml and <plist wasn't closed with > and xml was missing encoding
		# 	- APPL???? --> RFS<SIGNATURE_NAME>

		Infoplist = os.path.join(apppath, "Contents", "Info.plist")
		with open(Infoplist, "w") as f:
			f.write("""<?xml version="1.0" encoding="UTF-8"?>
			<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
			<plist version="1.0">
			<dict>
				<key>CFBundleDevelopmentRegion</key>
				<string>English</string>
				<key>CFBundleExecutable</key>
				<string>%s</string>
				<key>CFBundleGetInfoString</key>
				<string>%s</string>
				<key>CFBundleIconFile</key>
				<string>%s.icns</string>
				<key>CFBundleIdentifier</key>
				<string>%s</string>
				<key>CFBundleInfoDictionaryVersion</key>
				<string>6.0</string>
				<key>CFBundleName</key>
				<string>%s</string>
				<key>CFBundlePackageType</key>
				<string>APPL</string>
				<key>CFBundleShortVersionString</key>
				<string>%s</string>
				<key>CFBundleSignature</key>
				<string>%s</string>
				<key>CFBundleVersion</key>
				<string>%s</string>
				<key>NSAppleScriptEnabled</key>
				<string>YES</string>
				<key>NSMainNibFile</key>
				<string>MainMenu</string>
				<key>NSPrincipalClass</key>
				<string>NSApplication</string>
			</dict>
			</plist>
			""" % (projname, bundleName + " " + version, projname, bundleIdentifier, bundleName, version, signature, version))
			f.close()

		# create apppath + "/Contents/PkgInfo"
		PkgInfo = os.path.join(apppath, "Contents", "PkgInfo")
		with open(PkgInfo, "w") as f:
			f.write("APPL%s" % signature)
			f.close()

		# apppath + "/Contents/MacOS/main.py"
		execbundle = os.path.join(apppath, "Contents", "MacOS", projname)
		if os.path.exists(execbundle):
			os.remove(execbundle)
		os.symlink(exesrc, execbundle)

		# touch '/Applications/RFSwarm Manager.app' to update .app icon
		cmd = "touch '{0}'".format(apppath)
		self.base.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		self.base.debugmsg(6, "response:", response)

		# # Try re-registering your application with Launch Services:
		# # /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f /Applications/MyTool.app
		# lsregister = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
		# cmd = "{0} -f '{1}'".format(lsregister, apppath)
		# self.base.debugmsg(6, "cmd:", cmd)
		# response = os.popen(cmd).read()
		# self.base.debugmsg(6, "response:", response)

	def check_icons(self, appname):
		projname = "-".join(appname.split()).lower()
		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				fileprefix = "/usr/share"
			fileprefix = os.path.expanduser(fileprefix)
			desktopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
			if not os.path.exists(desktopfilename):
				self.base.debugmsg(1, f"{appname} icon / shortcut is not installed. You can create it using the -c or --create flags.")

		elif platform.system() == 'Darwin':
			appspath = "~/Applications"
			if os.access("/Applications", os.W_OK):
				appspath = "/Applications"
			appspath = os.path.expanduser(appspath)
			apppath = os.path.join(appspath, appname + ".app")
			ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
			iconset = os.path.join(ResourcesFolder, projname + ".iconset")
			if not os.path.exists(iconset):
				self.base.debugmsg(1, f"{appname} icon / shortcut is not installed. You can create it using the -c or --create flags.")

		elif platform.system() == 'Windows':
			roam_appdata = os.environ["APPDATA"]
			scutpath = os.path.join(roam_appdata, "Microsoft", "Windows", "Start Menu", appname + ".lnk")
			# directorydir = os.path.dirname(scutpath)
			if not os.path.exists(scutpath):
				self.base.debugmsg(1, f"{appname} icon / shortcut is not installed. You can create it using the -c or --create flags.")

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Messages
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def display_warning(self, message):
		if not self.base.args.nogui:
			self.base.debugmsg(0, message)
			self.base.gui.display_warning(message)
		else:
			self.base.debugmsg(0, message)
			self.on_closing(message)

	def display_info(self, message):
		if not self.base.args.nogui:
			self.base.debugmsg(0, message)
			self.base.gui.display_info(message)
		else:
			self.base.debugmsg(0, message)
			self.on_closing(message)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Server
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def run_v2_server(self):

		# self.base.v2startmode = 'chrome'
		# self.base.v2path = "V2UI"
		# self.base.v2starturl = "index.html"
		if len(self.base.config['Server']['BindIP'])>0:
			self.base.v2starthost = self.base.config['Server']['BindIP']
		self.base.v2startport = int(self.base.config['Server']['BindPort']) + 1
		self.base.v2startapp = RFSwarmV2API().api_object()

		v2width = int(self.base.config['GUI']['win_width'])
		v2height = int(self.base.config['GUI']['win_height'])

		# eel.init(self.base.v2path)
		# try:
		# 	self.base.debugmsg(1, "Starting V2 Manager", "http://{}:{}/".format(self.base.v2starthost, self.base.v2startport))
		# 	eel.start(self.base.v2starturl, mode=self.base.v2startmode, host=self.base.v2starthost, port=self.base.v2startport, app=self.base.v2startapp, size=(v2width,v2height))
		# 	self.base.appstarted = True
		# 	self.base.debugmsg(5, "appstarted:", self.base.appstarted)
		# except Exception as e:
		# 	self.base.debugmsg(5, "e:", e)
		# 	self.on_closing()
		# 	return False

	def run_agent_server(self):

		srvip = self.base.config['Server']['BindIP']
		srvport = int(self.base.config['Server']['BindPort'])
		if len(srvip) > 0:
			self.base.srvdisphost = srvip
			ip = ipaddress.ip_address(srvip)
			self.base.debugmsg(5, "ip.version:", ip.version)
			if ip.version == 6 and sys.version_info < (3, 8):
				self.base.debugmsg(0, "Python 3.8 or higher required to bind to IPv6 Addresses")
				pyver = "{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
				self.base.debugmsg(0, "Python Version:", pyver, "	IP Version:", ip.version, "	IP Address:", srvip)
				srvip = ''
				self.base.srvdisphost = socket.gethostname()
		else:
			self.base.srvdisphost = socket.gethostname()

		server_address = (srvip, srvport)
		try:
			self.base.agenthttpserver = ThreadingHTTPServer(server_address, AgentServer)
			self.base.agenthttpserver.base = self.base
			self.base.agenthttpserver.core = self

		except PermissionError:
			self.base.debugmsg(0, "Permission denied when trying :", server_address)
			self.on_closing()
			return False
		except Exception as e:
			self.base.debugmsg(5, "e:", e)
			self.base.debugmsg(0, e, "Shutting down...")
			self.on_closing()
			return False

		self.base.appstarted = True
		self.base.debugmsg(5, "appstarted:", self.base.appstarted)
		self.base.debugmsg(1, "Starting Agent Manager", "http://{}:{}/".format(self.base.srvdisphost, srvport))
		self.base.agenthttpserver.serve_forever()

	def register_agent(self, agentdata):
		self.base.debugmsg(7, "agentdata:", agentdata)
		agentname = agentdata["AgentName"]

		self.base.add_scriptfilter("Agent: {}".format(agentname))

		AssignedRobots = 0
		if agentname in self.base.Agents and "AssignedRobots" in self.base.Agents[agentname]:
			AssignedRobots = self.base.Agents[agentname]["AssignedRobots"]
		agentdata["AssignedRobots"] = AssignedRobots

		AssignedMRobots = 0
		if agentname in self.base.Agents and "AssignedMRobots" in self.base.Agents[agentname]:
			AssignedMRobots = self.base.Agents[agentname]["AssignedMRobots"]
		agentdata["AssignedMRobots"] = AssignedMRobots

		if "Monitor" not in agentdata.keys():
			agentdata["Monitor"] = 0

		agentdata["LastSeen"] = int(time.time())
		if "Status" not in agentdata.keys():
			agentdata["Status"] = "Unknown"
			if agentdata["Robots"] == 0:
				agentdata["Status"] = "Ready"
			if agentdata["Robots"] > 0:
				agentdata["Status"] = "Running"

		load = max([agentdata["CPU%"], agentdata["MEM%"], agentdata["NET%"]])
		agentdata["LOAD%"] = load
		if "Uploading" not in agentdata["Status"]:
			if load > 80:
				agentdata["Status"] = "Warning"
			if load > 95:
				agentdata["Status"] = "Critical"

		self.base.Agents[agentdata["AgentName"]] = agentdata

		self.base.debugmsg(9, "register_agent: agentdata:", agentdata)

		t = threading.Thread(target=self.UpdateAgents, name="UpdateAgents")
		t.start()

		# add filter options to the filter list
		if "Properties" in agentdata:
			filterexclude = ["RobotFramework: Libraries", "RFSwarmAgent: Version"]
			valexclude = [True, False, "", "True", "False"]
			for prop in agentdata["Properties"]:
				self.base.debugmsg(8, "prop:", prop)
				if prop not in filterexclude:
					t = threading.Thread(target=self.base.add_scriptfilter, args=(prop, ))
					t.start()
					if agentdata["Properties"][prop] not in valexclude:
						val = "{}: {}".format(prop, agentdata["Properties"][prop])
						t = threading.Thread(target=self.base.add_scriptfilter, args=(val, ))
						t.start()

			if "RFSwarmAgent: Version" in agentdata["Properties"]:
				prop = "RFSwarmAgent: Version: {}".format(agentdata["Properties"]["RFSwarmAgent: Version"])
				t = threading.Thread(target=self.base.add_scriptfilter, args=(prop, ))
				t.start()

		# save data to db

		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Status", agentdata["Status"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "LastSeen", agentdata["LastSeen"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "AssignedRobots", agentdata["AssignedRobots"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Robots", agentdata["Robots"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Monitor", agentdata["Monitor"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Load", agentdata["LOAD%"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "CPU", agentdata["CPU%"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "MEM", agentdata["MEM%"], agentdata["AgentName"])
		self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "NET", agentdata["NET%"], agentdata["AgentName"])
		# FileCount was added in v1.3.2
		if "FileCount" in agentdata:
			self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "FileCount", agentdata["FileCount"], agentdata["AgentName"])

		if "AgentIPs" in agentdata:
			for ip in agentdata["AgentIPs"]:
				self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "IPAddress", ip, agentdata["AgentName"])
		if "Properties" in agentdata:
			for prop in agentdata["Properties"]:
				self.base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], prop, agentdata["Properties"][prop], agentdata["AgentName"])

	def register_result(self, AgentName, result_name, result, elapsed_time, start_time, end_time, index, robot, iter, sequence):
		self.base.debugmsg(9, "register_result")
		resdata = (index, robot, iter, AgentName, sequence, result_name, result, elapsed_time, start_time, end_time)
		self.base.debugmsg(7, "resdata:", resdata)
		self.base.dbqueue["Results"].append(resdata)
		self.base.debugmsg(9, "dbqueue Results:", self.base.dbqueue["Results"])

		if not self.base.args.nogui:
			ut = threading.Thread(target=self.base.gui.delayed_UpdateRunStats)
			ut.start()

	def register_metric(self, PrimaryMetric, MetricType, MetricTime, SecondaryMetrics, DataSource):
		# core.register_metric(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"], jsonreq["AgentName"])
		self.base.debugmsg(7, "PrimaryMetric:", PrimaryMetric, "	MetricType:", MetricType, "	MetricTime:", MetricTime, "	SecondaryMetrics:", SecondaryMetrics, "	DataSource:", DataSource)

		# Save Metric Data

		for key in SecondaryMetrics:
			self.base.debugmsg(7, PrimaryMetric, MetricType, MetricTime, key, SecondaryMetrics[key], DataSource)
			self.base.save_metrics(PrimaryMetric, MetricType, MetricTime, key, SecondaryMetrics[key], DataSource)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Plan
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildCorePlan(self):
		self.base.debugmsg(5, "BuildCorePlan")

		self.base.debugmsg(6, "Plan:scenariofile: ", self.base.config['Plan']['ScenarioFile'])
		self.base.debugmsg(6, "ScenarioFile: ", len(self.base.config['Plan']['ScenarioFile']), self.base.config['Plan']['ScenarioFile'])
		if len(self.base.config['Plan']['ScenarioFile']) > 0:
			load_result = self.OpenFile(self.base.config['Plan']['ScenarioFile'])
			if not self.base.args.nogui and load_result == 1:
				self.base.gui.OpenINIGraphs()
		else:
			self.base.addScriptRow()

	def OpenFile(self, ScenarioFile):
		fileok = True

		self.base.debugmsg(6, "ScenarioFile: ", ScenarioFile)
		self.base.debugmsg(6, "self.base.config['Plan']['ScenarioFile']: ", self.base.config['Plan']['ScenarioFile'])
		self.base.config['Plan']['ScenarioDir'] = self.base.inisafedir(os.path.dirname(ScenarioFile))
		self.base.debugmsg(6, "self.base.config['Plan']['ScenarioDir']: ", self.base.config['Plan']['ScenarioDir'])

		self.base.debugmsg(6, "Config graph list: ")
		self.base.debugmsg(6, "self.base.config['GUI']['graph_list']: ", self.base.config['GUI']['graph_list'])
		iniglist = list(self.base.config['GUI']['graph_list'].split(","))
		self.base.debugmsg(9, "iniglist: ", iniglist)
		self.base.config['GUI']['graph_list'] = self.base.inisafevalue(",".join(set(iniglist)))
		self.base.debugmsg(6, "self.base.config['GUI']['graph_list']: ", self.base.config['GUI']['graph_list'])

		filedata = configparser.ConfigParser()
		self.base.debugmsg(6, "filedata: ", filedata._sections)

		if os.path.isfile(ScenarioFile):
			self.base.debugmsg(9, "ScenarioFile: ", ScenarioFile)
			try:
				arrfile = os.path.splitext(ScenarioFile)
				self.base.debugmsg(5, "arrfile: ", arrfile)
				if len(arrfile) < 2:
					msg = "Scenario file ", ScenarioFile, " missing extention, unable to determine supported format. Plesae use extentions .rfs, .yaml or .json"
					self.display_warning(msg)
					return 1
				if arrfile[1].lower() not in [".rfs", ".yml", ".yaml", ".json"]:
					msg = "Scenario file ", ScenarioFile, " has an invalid extention, unable to determine supported format. Plesae use extentions .rfs, .yaml or .json"
					self.display_warning(msg)
					return 1
				if arrfile[1].lower() == ".rfs":
					filedata.read(ScenarioFile, encoding="utf8")
				else:
					filedict = {}
					if arrfile[1].lower() in [".yml", ".yaml"]:
						# read yaml file
						self.base.debugmsg(5, "read yaml file")
						with open(ScenarioFile, 'r', encoding="utf-8") as f:
							filedict = yaml.safe_load(f)
						self.base.debugmsg(5, "filedict: ", filedict)
						filedict = self.base.configparser_safe_dict(filedict)
						self.base.debugmsg(5, "filedict: ", filedict)
					if arrfile[1].lower() == ".json":
						# read json file
						self.base.debugmsg(5, "read json file")
						with open(ScenarioFile, 'r', encoding="utf-8") as f:
							filedict = json.load(f)
						self.base.debugmsg(5, "filedict: ", filedict)
						filedict = self.base.configparser_safe_dict(filedict)
						self.base.debugmsg(5, "filedict: ", filedict)
					self.base.debugmsg(5, "filedict: ", filedict)
					filedata.read_dict(filedict)
				if self.base.config['Plan']['ScenarioFile'] != ScenarioFile:
					self.base.debugmsg(6, "ScenarioFile:", ScenarioFile)
					self.base.config['Plan']['ScenarioFile'] = self.base.inisafevalue(ScenarioFile)
					self.base.saveini()
			except Exception:
				self.base.config['Plan']['ScenarioFile'] = ""
		else:
			if len(ScenarioFile) > 1:
				# error file not exist
				msg = "Scenario file Not found:\n" + ScenarioFile
				self.display_warning(msg)
			return 1

		self.base.debugmsg(6, "filedata: ", filedata)

		scriptcount = 0
		monitorcount = 0
		graphlist = []
		if "Scenario" in filedata:
			self.base.debugmsg(6, "Scenario:", filedata["Scenario"])
			if "scriptcount" in filedata["Scenario"]:
				scriptcount = int(filedata["Scenario"]["scriptcount"])
				self.base.debugmsg(8, "scriptcount:", scriptcount)

			if "graphlist" in filedata["Scenario"]:
				graphlist = filedata["Scenario"]["graphlist"].split(",")

			if "uploadmode" in filedata["Scenario"]:
				self.base.uploadmode = filedata['Scenario']['uploadmode']

			if "monitortimebefore" in filedata["Scenario"]:
				self.base.mtimebefore = int(filedata['Scenario']['monitortimebefore'])
				self.base.debugmsg(5, "self.base.mtimebefore:", self.base.mtimebefore)
				self.msr_delayb4_validate("OpenFile", self.base.mtimebefore)

			if "monitortimeafter" in filedata["Scenario"]:
				self.base.mtimeafter = int(filedata['Scenario']['monitortimeafter'])
				self.base.debugmsg(5, "self.base.mtimeafter:", self.base.mtimeafter)
				self.msr_delayaft_validate("OpenFile", self.base.mtimeafter)

			if "monitorcount" in filedata["Scenario"]:
				monitorcount = int(filedata["Scenario"]["monitorcount"])
				self.base.debugmsg(5, "monitorcount:", monitorcount)

		else:
			self.base.debugmsg(1, "File contains no scenario:", ScenarioFile)
			self.base.config['Plan']['ScenarioFile'] = ""
			return 1

		if "Script Defaults" in filedata:
			self.base.scriptdefaults = filedata['Script Defaults']

		# Set self.base.config['Plan']['ScriptDir']
		self.base.debugmsg(5, "scriptcount:", scriptcount)
		filelst = []

		for i in range(scriptcount):
			istr = str(i + 1)
			self.base.debugmsg(5, "istr:", istr)
			if istr in filedata:
				self.base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				if "script" in filedata[istr]:
					self.base.debugmsg(5, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(self.base.config['Plan']['ScenarioDir'], scriptname)
						self.base.debugmsg(5, "combined:", combined)
						scriptname = os.path.abspath(combined)
					self.base.debugmsg(5, "scriptname:", scriptname)

					if scriptname not in filelst:
						filelst.append(scriptname)

		for i in range(monitorcount):
			istr = "m{}".format(i + 1)
			self.base.debugmsg(5, "istr:", istr)
			if istr in filedata:
				self.base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				if "script" in filedata[istr]:
					self.base.debugmsg(5, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(self.base.config['Plan']['ScenarioDir'], scriptname)
						self.base.debugmsg(5, "combined:", combined)
						scriptname = os.path.abspath(combined)
					self.base.debugmsg(5, "scriptname:", scriptname)

					if scriptname not in filelst:
						filelst.append(scriptname)

		if len(filelst) > 0:
			commonpath = os.path.commonpath(filelst)
			self.base.debugmsg(5, "commonpath: ", commonpath)
			self.base.config['Plan']['ScriptDir'] = self.base.inisafedir(commonpath)
			self.base.saveini()
		else:
			self.base.config['Plan']['ScriptDir'] = self.base.inisafedir(self.base.dir_path)
			self.base.debugmsg(5, "ScriptDir: ", self.base.config['Plan']['ScriptDir'])
			self.base.saveini()

		rowcount = 0
		for i in range(scriptcount):
			istr = str(i + 1)
			if istr in filedata:
				self.base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				rowcount += 1

				# if i not in self.base.scriptlist:
				# 	self.base.scriptlist.append({})
				# 	self.base.scriptlist[ii]["Index"] = ii
				if not self.base.args.nogui:
					if rowcount + 1 > self.base.gui.scriptgrid.grid_size()[1]:		# grid_size tupple: (cols, rows)
						self.base.addScriptRow()
				else:
					self.base.addScriptRow()

				# users = 13
				if "robots" in filedata[istr] or "users" in filedata[istr]:
					if "robots" in filedata[istr]:
						self.base.debugmsg(8, "filedata[", istr, "][robots]:", filedata[istr]["robots"])
						self.sr_users_validate(rowcount, int(filedata[istr]["robots"]))
					else:
						self.base.debugmsg(8, "filedata[", istr, "][users]:", filedata[istr]["users"])
						self.sr_users_validate(rowcount, int(filedata[istr]["users"]))
						# delay = 0
				else:
					self.base.debugmsg(3, "robots missing [", istr, "]")
					fileok = False
				if "delay" in filedata[istr]:
					self.base.debugmsg(8, "filedata[", istr, "][delay]:", filedata[istr]["delay"])
					self.sr_delay_validate(rowcount, int(filedata[istr]["delay"]))
					# rampup = 60
				else:
					self.base.debugmsg(3, "delay missing [", istr, "]")
					fileok = False
				if "rampup" in filedata[istr]:
					self.base.debugmsg(8, "filedata[", istr, "][rampup]:", filedata[istr]["rampup"])
					self.sr_rampup_validate(rowcount, int(filedata[istr]["rampup"]))
					# run = 600
				else:
					self.base.debugmsg(3, "rampup missing [", istr, "]")
					fileok = False
				if "run" in filedata[istr]:
					self.base.debugmsg(8, "filedata[", istr, "][run]:", filedata[istr]["run"])
					self.sr_run_validate(rowcount, int(filedata[istr]["run"]))
					# script = /Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot
				else:
					self.base.debugmsg(3, "run missing [", istr, "]")
					fileok = False
				if "script" in filedata[istr]:
					self.base.debugmsg(7, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)

					self.base.debugmsg(7, "scriptname:", scriptname)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(self.base.config['Plan']['ScenarioDir'], scriptname)
						self.base.debugmsg(7, "combined:", combined)
						scriptname = os.path.abspath(combined)
					self.base.debugmsg(7, "scriptname:", scriptname)
					self.sr_file_validate(rowcount, scriptname)
				else:
					self.base.debugmsg(3, "script missing [", istr, "]")
					fileok = False
				if "test" in filedata[istr]:
					self.base.debugmsg(8, "filedata[", istr, "][test]:", filedata[istr]["test"])
					self.sr_test_validate("row{}".format(rowcount), filedata[istr]["test"])
				else:
					self.base.debugmsg(3, "test missing [", istr, "]")
					fileok = False

				if "resultnamemode" in filedata[istr]:
					self.base.debugmsg(8, "resultnamemode:", filedata[istr]["resultnamemode"])
					self.base.scriptlist[rowcount]["resultnamemode"] = filedata[istr]["resultnamemode"]

				if "excludelibraries" in filedata[istr]:
					self.base.debugmsg(8, "excludelibraries:", filedata[istr]["excludelibraries"])
					self.base.scriptlist[rowcount]["excludelibraries"] = filedata[istr]["excludelibraries"]

				if "robotoptions" in filedata[istr]:
					self.base.debugmsg(8, "robotoptions:", filedata[istr]["robotoptions"])
					self.base.scriptlist[rowcount]["robotoptions"] = filedata[istr]["robotoptions"]

				# testrepeater = True
				if "testrepeater" in filedata[istr]:
					self.base.scriptlist[rowcount]["testrepeater"] = self.base.str2bool(filedata[istr]["testrepeater"])
				# includetesttime = True
				if "includetesttime" in filedata[istr]:
					self.base.scriptlist[rowcount]["includetesttime"] = self.base.str2bool(filedata[istr]["includetesttime"])
				# injectsleepenabled = True
				if "injectsleepenabled" in filedata[istr]:
					self.base.scriptlist[rowcount]["injectsleepenabled"] = self.base.str2bool(filedata[istr]["injectsleepenabled"])
				# injectsleepminimum = 18
				if "injectsleepminimum" in filedata[istr] and len(filedata[istr]["injectsleepminimum"]) > 0:
					self.base.scriptlist[rowcount]["injectsleepminimum"] = int(filedata[istr]["injectsleepminimum"])
				# injectsleepmaximum = 33
				if "injectsleepmaximum" in filedata[istr] and len(filedata[istr]["injectsleepmaximum"]) > 0:
					self.base.scriptlist[rowcount]["injectsleepmaximum"] = int(filedata[istr]["injectsleepmaximum"])
				# exclude sleep from time Issue #401
				if "excludesleep" in filedata[istr]:
					self.base.scriptlist[rowcount]["excludesleep"] = filedata[istr]["excludesleep"]
				if "applypacingtime" in filedata[istr]:
					self.base.scriptlist[rowcount]["applypacingtime"] = filedata[istr]["applypacingtime"]
				if "applypacingstart" in filedata[istr]:
					self.base.scriptlist[rowcount]["applypacingstart"] = filedata[istr]["applypacingstart"]
				# disableloglog
				if "disableloglog" in filedata[istr]:
					self.base.scriptlist[rowcount]["disableloglog"] = self.base.str2bool(filedata[istr]["disableloglog"])
				# disablelogreport
				if "disablelogreport" in filedata[istr]:
					self.base.scriptlist[rowcount]["disablelogreport"] = self.base.str2bool(filedata[istr]["disablelogreport"])
				# disablelogoutput
				if "disablelogoutput" in filedata[istr]:
					self.base.scriptlist[rowcount]["disablelogoutput"] = self.base.str2bool(filedata[istr]["disablelogoutput"])

				if "filters" in filedata[istr]:
					self.base.debugmsg(9, "filedata[istr][filters]:", filedata[istr]["filters"], type(filedata[istr]["filters"]))
					filtr = filedata[istr]["filters"].replace("'", '"')
					self.base.debugmsg(9, "filtr:", filtr, type(filtr))
					filtrs = json.loads(filtr)
					self.base.debugmsg(9, "filtrs:", filtrs, type(filtrs))
					self.base.scriptlist[rowcount]["filters"] = filtrs

				if not fileok:
					self.base.debugmsg(1, "Scenario file is damaged:", ScenarioFile)
					return 1

		rowcount = 0
		for i in range(monitorcount):
			istr = "m{}".format(i + 1)
			if istr in filedata:
				self.base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				rowcount += 1

				# if i not in self.base.scriptlist:
				# 	self.base.scriptlist.append({})
				# 	self.base.scriptlist[ii]["Index"] = ii
				# if not self.base.args.nogui:
				# 	if rowcount + 1 > self.base.gui.scriptgrid.grid_size()[1]:		# grid_size tupple: (cols, rows)
				# 		self.base.addMScriptRow()
				# else:
				self.base.addMScriptRow()

				# users = 13
				# if "robots" in filedata[istr] or "users" in filedata[istr]:
				# 	if "robots" in filedata[istr]:
				# 		self.base.debugmsg(8, "filedata[", istr, "][robots]:", filedata[istr]["robots"])
				# 		self.msr_users_validate(rowcount, int(filedata[istr]["robots"]))
				# 	else:
				# 		self.base.debugmsg(8, "filedata[", istr, "][users]:", filedata[istr]["users"])
				# 		self.msr_users_validate(rowcount, int(filedata[istr]["users"]))
				# 		# delay = 0
				# else:
				# 	self.base.debugmsg(3, "robots missing [", istr, "]")
				# 	fileok = False
				# if "delay" in filedata[istr]:
				# 	self.base.debugmsg(8, "filedata[", istr, "][delay]:", filedata[istr]["delay"])
				# 	self.msr_delay_validate(rowcount, int(filedata[istr]["delay"]))
				# 	# rampup = 60
				# else:
				# 	self.base.debugmsg(3, "delay missing [", istr, "]")
				# 	fileok = False
				# if "rampup" in filedata[istr]:
				# 	self.base.debugmsg(8, "filedata[", istr, "][rampup]:", filedata[istr]["rampup"])
				# 	self.msr_rampup_validate(rowcount, int(filedata[istr]["rampup"]))
				# 	# run = 600
				# else:
				# 	self.base.debugmsg(3, "rampup missing [", istr, "]")
				# 	fileok = False
				# if "run" in filedata[istr]:
				# 	self.base.debugmsg(8, "filedata[", istr, "][run]:", filedata[istr]["run"])
				# 	self.msr_run_validate(rowcount, int(filedata[istr]["run"]))
				# 	# script = /Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot
				# else:
				# 	self.base.debugmsg(3, "run missing [", istr, "]")
				# 	fileok = False

				if "script" in filedata[istr]:
					self.base.debugmsg(5, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)

					self.base.debugmsg(5, "scriptname:", scriptname)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(self.base.config['Plan']['ScenarioDir'], scriptname)
						self.base.debugmsg(7, "combined:", combined)
						scriptname = os.path.abspath(combined)
					self.base.debugmsg(7, "scriptname:", scriptname)
					self.msr_file_validate(rowcount, scriptname)
				else:
					self.base.debugmsg(3, "script missing [", istr, "]")
					fileok = False
				if "test" in filedata[istr]:
					self.base.debugmsg(8, "filedata[", istr, "][test]:", filedata[istr]["test"])
					self.msr_test_validate("mrow{}".format(rowcount), filedata[istr]["test"])
				else:
					self.base.debugmsg(3, "test missing [", istr, "]")
					fileok = False

				if "resultnamemode" in filedata[istr]:
					self.base.debugmsg(8, "resultnamemode:", filedata[istr]["resultnamemode"])
					self.base.mscriptlist[rowcount]["resultnamemode"] = filedata[istr]["resultnamemode"]

				if "excludelibraries" in filedata[istr]:
					self.base.debugmsg(8, "excludelibraries:", filedata[istr]["excludelibraries"])
					self.base.mscriptlist[rowcount]["excludelibraries"] = filedata[istr]["excludelibraries"]

				if "robotoptions" in filedata[istr]:
					self.base.debugmsg(8, "robotoptions:", filedata[istr]["robotoptions"])
					self.base.mscriptlist[rowcount]["robotoptions"] = filedata[istr]["robotoptions"]

				# testrepeater = True
				if "testrepeater" in filedata[istr]:
					self.base.mscriptlist[rowcount]["testrepeater"] = self.base.str2bool(filedata[istr]["testrepeater"])
				# includetesttime = True
				if "includetesttime" in filedata[istr]:
					self.base.mscriptlist[rowcount]["includetesttime"] = self.base.str2bool(filedata[istr]["includetesttime"])
				# injectsleepenabled = True
				if "injectsleepenabled" in filedata[istr]:
					self.base.mscriptlist[rowcount]["injectsleepenabled"] = self.base.str2bool(filedata[istr]["injectsleepenabled"])
				# injectsleepminimum = 18
				if "injectsleepminimum" in filedata[istr] and len(filedata[istr]["injectsleepminimum"]) > 0:
					self.base.mscriptlist[rowcount]["injectsleepminimum"] = int(filedata[istr]["injectsleepminimum"])
				# injectsleepmaximum = 33
				if "injectsleepmaximum" in filedata[istr] and len(filedata[istr]["injectsleepmaximum"]) > 0:
					self.base.mscriptlist[rowcount]["injectsleepmaximum"] = int(filedata[istr]["injectsleepmaximum"])
				# exclude sleep from time Issue #401
				if "excludesleep" in filedata[istr]:
					self.base.mscriptlist[rowcount]["excludesleep"] = filedata[istr]["excludesleep"]
				if "applypacingtime" in filedata[istr]:
					self.base.mscriptlist[rowcount]["applypacingtime"] = filedata[istr]["applypacingtime"]
				if "applypacingstart" in filedata[istr]:
					self.base.mscriptlist[rowcount]["applypacingstart"] = filedata[istr]["applypacingstart"]
				# disableloglog
				if "disableloglog" in filedata[istr]:
					self.base.mscriptlist[rowcount]["disableloglog"] = self.base.str2bool(filedata[istr]["disableloglog"])
				# disablelogreport
				if "disablelogreport" in filedata[istr]:
					self.base.mscriptlist[rowcount]["disablelogreport"] = self.base.str2bool(filedata[istr]["disablelogreport"])
				# disablelogoutput
				if "disablelogoutput" in filedata[istr]:
					self.base.mscriptlist[rowcount]["disablelogoutput"] = self.base.str2bool(filedata[istr]["disablelogoutput"])

				if "filters" in filedata[istr]:
					self.base.debugmsg(9, "filedata[istr][filters]:", filedata[istr]["filters"], type(filedata[istr]["filters"]))
					filtr = filedata[istr]["filters"].replace("'", '"')
					self.base.debugmsg(9, "filtr:", filtr, type(filtr))
					filtrs = json.loads(filtr)
					self.base.debugmsg(9, "filtrs:", filtrs, type(filtrs))
					self.base.mscriptlist[rowcount]["filters"] = filtrs

				if not fileok:
					self.base.debugmsg(1, "Scenario file is damaged:", ScenarioFile)
					return 1

		self.base.debugmsg(9, "config graph_list: ", self.base.config['GUI']['graph_list'])

		self.base.debugmsg(9, "graphlist: ", graphlist)
		self.base.debugmsg(9, "iniglist: ", iniglist)
		self.base.config['GUI']['graph_list'] = self.base.inisafevalue(",".join(set(iniglist + graphlist)))

		self.base.debugmsg(9, "config graph_list: ", self.base.config['GUI']['graph_list'])

		if not self.base.args.nogui:
			self.base.gui.ClearScenarioGraphs()

		for iniid in graphlist:
			if iniid in filedata:
				self.base.debugmsg(5, "iniid: ", iniid, " 	filedata[iniid]:", filedata[iniid])
				self.base.config[iniid] = self.base.inisafevalue(filedata[iniid])
				if not self.base.args.nogui:
					self.base.gui.AddScenarioGraph(filedata[iniid]["name"], iniid)

		if not self.base.args.nogui:
			self.base.gui.OpenINIGraphs()
			time.sleep(0.250)

			self.base.debugmsg(5, "Call self.base.gui.pln_update_graph")
			self.base.gui.pln_graph_update = False
			t = threading.Thread(target=self.base.gui.pln_update_graph)
			t.start()

		return 0

	def ClickPlay(self, _event=None):

		self.base.debugmsg(0, "Test Started:	", int(time.time()), "[", datetime.now().isoformat(sep=' ', timespec='seconds'), "]")

		# before we start any robots we need to make sure the assigned robot counts are zero
		for nxtagent in self.base.Agents.keys():
			self.base.Agents[nxtagent]["AssignedRobots"] = 0
			self.base.Agents[nxtagent]["AssignedMRobots"] = 0

		self.base.run_abort = False
		self.base.run_start = 0
		self.base.run_end = 0
		self.base.plan_end = 0
		self.base.mon_end = 0
		self.base.run_finish = 0
		self.base.posttest = False
		self.base.run_paused = False
		self.base.MetricIDs = {}

		self.base.robot_schedule = self.base.robot_schedule_template

		warnings = self.Pre_Run_Checks()
		if len(warnings) > 0:
			# report warnings and stop test from running
			self.base.run_abort = False
			self.base.run_end = int(time.time()) - 1
			self.base.plan_end = int(time.time()) - 1
			self.base.mon_end = int(time.time()) - 1
			self.base.run_finish = int(time.time()) - 1

			for warning in warnings:
				self.base.debugmsg(0, warning)

			return 0

		sec2st = self.base.run_starttime - int(time.time())
		if sec2st < 1:
			mstarttime = int(time.time())
			mendtime = self.base.mon_end - mstarttime
			starttime = mstarttime + self.base.mtimebefore
			datafiletime = datetime.now().strftime("%Y%m%d_%H%M%S")
			if len(self.base.config['Plan']['ScenarioFile']) > 0:
				filename = os.path.basename(self.base.config['Plan']['ScenarioFile'])
				sname = os.path.splitext(filename)[0]
				self.base.run_name = "{}_{}".format(datafiletime, sname)
			else:
				self.base.run_name = "{}_{}".format(datafiletime, "Scenario")
			self.base.debugmsg(5, "self.base.run_name:", self.base.run_name)

			# give some time (10ms) to create the db before starting monitoring
			time.sleep(1)
			self.base.debugmsg(5, "core.run_start_threads")
			t = threading.Thread(target=self.run_start_threads)
			t.start()
			if not self.base.args.nogui:
				time.sleep(0.1)
				self.base.debugmsg(5, "self.base.gui.delayed_UpdateRunStats")
				ut = threading.Thread(target=self.base.gui.delayed_UpdateRunStats)
				ut.start()
				self.base.debugmsg(9, "self.base.gui.tabs.tabs()", self.base.gui.tabs.tabs())
				self.base.debugmsg(8, "self.base.gui.tabids", self.base.gui.tabids)
				self.base.debugmsg(7, "self.base.gui.tabids['Run']", self.base.gui.tabids['Run'])
				# self.tabids['Run']
				# self.base.gui.tabs.select(2)
				self.base.gui.tabs.select(self.base.gui.tabids['Run'])

			# wait till db has been opened
			while self.base.run_name != self.base.run_name_current:
				time.sleep(0.1)
			while not self.base.dbready:
				time.sleep(0.1)

			# self.base.save_metrics(self.base.run_name, "Scenario", int(time.time()), "starttime", self.base.run_starttime, self.base.srvdisphost)
			self.base.save_metrics(self.base.run_name, "Scenario", starttime, "Start", starttime, self.base.srvdisphost)
			self.base.save_metrics("Time", "Scenario", starttime, "Start", starttime, self.base.srvdisphost)

			self.base.save_metrics("Manager", "rfswarm", starttime, "Version", self.base.version, self.base.srvdisphost)

			# collect list of test cases and robot files
			# --- save_metrics(self, PMetricName, MetricType, MetricTime, SMetricName, MetricValue):
			for grp in self.base.scriptlist:
				self.base.debugmsg(5, "grp", grp)
				if "Test" in grp.keys() and len(grp["Test"]) > 0:
					self.base.debugmsg(5, "grp[Index]", grp['Index'])
					self.base.save_metrics("Local_Path_{}".format(grp['Index']), "Scenario", starttime, grp['Script'], grp['Test'], self.base.srvdisphost)

					relpath = self.base.get_relative_path(self.base.config['Plan']['ScenarioFile'], grp['Script'])
					self.base.save_metrics("Test_{}".format(grp['Index']), "Scenario", starttime, relpath, grp['Test'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Test", starttime, relpath, grp['Test'], self.base.srvdisphost)

					self.base.save_metrics("Robots_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['Robots'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Robots", starttime, grp['Test'], grp['Robots'], self.base.srvdisphost)

					self.base.save_metrics("Delay_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['Delay'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Delay", starttime, grp['Test'], grp['Delay'], self.base.srvdisphost)

					self.base.save_metrics("Ramp_Up_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['RampUp'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Ramp_Up", starttime, grp['Test'], grp['RampUp'], self.base.srvdisphost)

					self.base.save_metrics("Run_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['Run'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Run", starttime, grp['Test'], grp['Run'], self.base.srvdisphost)

			for grp in self.base.mscriptlist:
				self.base.debugmsg(5, "grp", grp)
				if "Test" in grp.keys() and len(grp["Test"]) > 0:
					self.base.debugmsg(5, "grp[Index]", grp['Index'])
					self.base.save_metrics("Local_Path_{}".format(grp['Index']), "Scenario", mstarttime, grp['Script'], grp['Test'], self.base.srvdisphost)

					relpath = self.base.get_relative_path(self.base.config['Plan']['ScenarioFile'], grp['Script'])
					self.base.save_metrics("Test_{}".format(grp['Index']), "Scenario", mstarttime, relpath, grp['Test'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Test", mstarttime, relpath, grp['Test'], self.base.srvdisphost)

					self.base.save_metrics("Robots_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], grp['Robots'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Robots", mstarttime, grp['Test'], grp['Robots'], self.base.srvdisphost)

					self.base.save_metrics("Delay_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], grp['Delay'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Delay", mstarttime, grp['Test'], grp['Delay'], self.base.srvdisphost)

					self.base.save_metrics("Ramp_Up_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], grp['RampUp'], self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Ramp_Up", mstarttime, grp['Test'], grp['RampUp'], self.base.srvdisphost)

					self.base.save_metrics("Run_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], mendtime, self.base.srvdisphost)
					self.base.save_metrics(grp['Index'], "Scenario_Run", mstarttime, grp['Test'], mendtime, self.base.srvdisphost)

	def Pre_Run_Checks(self, _event=None):
		warnings = []

		# good
		# grp {'Index': 1, 'Robots': 2, 'Delay': 0, 'RampUp': 45, 'Run': 60, 'Test': 'RFSwarm Demo Test', 'TestVar': <tkinter.StringVar object at 0x7f6a4b911ea0>, 'Script': '/home/dave/Documents/Github/rfswarm/Tests/Demo/rfswarm_demo.robot', 'ScriptHash': '03ad3be39fcfd8f37dfe1db445192728'}
		# bad
		# grp {'Index': 1, 'Robots': 10, 'Delay': 0, 'RampUp': 1800, 'Run': 7200, 'Test': '', 'TestVar': <tkinter.StringVar object at 0x7f7fe07dfe50>}

		self.base.debugmsg(5, "scriptlist:", self.base.scriptlist)
		for grp in self.base.scriptlist:
			self.base.debugmsg(5, "grp", grp)
			if "Index" in grp.keys():
				if "Robots" not in grp.keys() or grp["Robots"] < 1:
					warnings.append("Plan Index {} has no Robots.".format(grp["Index"]))

				# RampUp	< 10
				if "RampUp" not in grp.keys() or grp["RampUp"] < 10:
					warnings.append("Plan Index {} Ramp Up is < 10 sec.".format(grp["Index"]))

				if "Run" not in grp.keys() or grp["Run"] < 10:
					warnings.append("Plan Index {} Run is < 10 sec.".format(grp["Index"]))

				if "Script" not in grp.keys() or len(grp["Script"]) < 1:
					warnings.append("Plan Index {} has no Script.".format(grp["Index"]))
				else:
					# ScriptHash
					if "ScriptHash" not in grp.keys() or len(grp["ScriptHash"]) < 1:
						warnings.append("Plan Index {} Agents don't have Script yet.".format(grp["Index"]))

				if "Test" not in grp.keys() or len(grp["Test"]) < 1:
					warnings.append("Plan Index {} has no Test.".format(grp["Index"]))

				grp_plan_end = int(time.time()) + self.base.mtimebefore + grp['Delay'] + grp["RampUp"] + grp['Run'] + grp["RampUp"]
				# mtimebefore = 0
				# mtimeafter = 0
				if grp_plan_end > self.base.plan_end:
					self.base.plan_end = grp_plan_end
					self.base.debugmsg(5, "self.base.plan_end:", self.base.plan_end)
					self.base.mon_end = self.base.plan_end + self.base.mtimeafter

		self.base.debugmsg(5, "mscriptlist:", self.base.mscriptlist)
		for grp in self.base.mscriptlist:
			self.base.debugmsg(5, "grp", grp)
			if "Index" in grp.keys():
				if "Robots" not in grp.keys() or grp["Robots"] < 1:
					warnings.append("Monitoring Index {} has no Robots.".format(grp["Index"]))

				if "Script" not in grp.keys() or len(grp["Script"]) < 1:
					warnings.append("Monitoring Index {} has no Script.".format(grp["Index"]))
				else:
					# ScriptHash
					if "ScriptHash" not in grp.keys() or len(grp["ScriptHash"]) < 1:
						warnings.append("Monitoring Index {} Agents don't have Script yet.".format(grp["Index"]))

				if "Test" not in grp.keys() or len(grp["Test"]) < 1:
					warnings.append("Monitoring Index {} has no Test.".format(grp["Index"]))

		# warnings.append("Debuging : Don't Run")
		return warnings

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Monitoring
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildCoreMonitoring(self):
		self.base.debugmsg(5, "RFSwarmCore: BuildCoreMonitoring")

	def msr_delayb4_validate(self, *args):
		self.base.debugmsg(5, "args", args)
		if not self.base.args.nogui:
			self.base.gui.msr_delayb4_validate(*args)
		return True

	def msr_delayaft_validate(self, *args):
		self.base.debugmsg(5, "args", args)
		if not self.base.args.nogui:
			self.base.gui.msr_delayaft_validate(*args)
		return True

	def msr_file_validate(self, r, *args):
		self.base.debugmsg(5, "r:", r, "	args:", args)
		if args:
			scriptfile = args[0]
		else:
			scriptfile = ""

		if not os.path.exists(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\ncannot be found by RFSwarm Manager."
			if not self.base.args.nogui:
				self.display_warning(msg)
			else:
				self.base.debugmsg(0, msg)
			return False
		elif not os.path.isfile(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\nis a directory, not a file."
			if not self.base.args.nogui:
				self.display_warning(msg)
			else:
				self.base.debugmsg(0, msg)
			return False

		self.base.debugmsg(5, "scriptfile:", scriptfile)
		if len(scriptfile) > 0:
			self.base.mscriptlist[r]["Script"] = scriptfile
			relpath = self.base.get_relative_path(self.base.config['Plan']['ScriptDir'], scriptfile)
			script_hash = self.base.hash_file(scriptfile, relpath)
			self.base.mscriptlist[r]["ScriptHash"] = script_hash

			if script_hash not in self.base.scriptfiles:
				self.base.scriptfiles[script_hash] = {
					"id": script_hash,
					"localpath": scriptfile,
					"relpath": relpath,
					"type": "script"
				}

				t = threading.Thread(target=self.base.find_dependancies, args=(script_hash, ))
				t.start()

		else:
			if "ScriptHash" in self.base.mscriptlist[r]:
				oldhash = self.base.mscriptlist[r]["ScriptHash"]
				t = threading.Thread(target=self.base.remove_hash, args=(oldhash, ))
				t.start()

			self.base.mscriptlist[r]["Script"] = ''
			self.base.mscriptlist[r]["ScriptHash"] = ''

		self.plan_scnro_chngd = True
		if not self.base.args.nogui:
			self.base.gui.msr_file_validate(r, *args)
		return True

	def msr_test_validate(self, *args):
		self.base.debugmsg(5, "args:", args)
		# r = int(args[0][-1:])+1
		r = int(args[0][4:])
		self.base.debugmsg(5, "r:", r)

		v = None
		if len(args) > 1 and len(args[1]) > 1:
			v = args[1]
			self.base.debugmsg(5, "v:", v)
			self.base.mscriptlist[r]["Test"] = v

		self.base.debugmsg(5, "mscriptlist[r]:", self.base.mscriptlist[r])

		if not self.base.args.nogui:
			self.base.gui.msr_test_validate(*args)
		return True

	def update_monitoring_jobs_mon_end(self, *args):
		self.base.debugmsg(5, "args:", args)
		for agnt in self.base.robot_schedule["Agents"].keys():
			for grurid in self.base.robot_schedule["Agents"][agnt].keys():
				self.base.debugmsg(5, "grurid:", grurid)
				if grurid[0] == "m":
					self.base.debugmsg(5, "grurid:", grurid, "New EndTime", self.base.mon_end)
					self.base.robot_schedule["Agents"][agnt][grurid]["EndTime"] = self.base.mon_end

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Run
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildCoreRun(self):
		self.base.debugmsg(5, "RFSwarmCore: BuildCoreRun")

	def ClickStop(self, _event=None):

		if self.base.run_end < int(time.time()):
			# abort run?
			self.base.run_abort = True
			self.base.debugmsg(5, "self.base.run_abort:", self.base.run_abort)
		else:
			self.base.run_end = int(time.time())  # time now
			self.base.debugmsg(0, "Run Stopped:", self.base.run_end, "[", datetime.now().isoformat(sep=' ', timespec='seconds'), "]")
			self.base.robot_schedule["End"] = self.base.run_end

			for agnt in self.base.robot_schedule["Agents"].keys():
				for grurid in self.base.robot_schedule["Agents"][agnt].keys():
					self.base.robot_schedule["Agents"][agnt][grurid]["EndTime"] = self.base.run_end
			self.base.mon_end = self.base.run_end

	def run_start_threads(self):

		if self.base.run_end > 0 and int(time.time()) > self.base.run_end:
			self.base.run_paused = True

		totrbts = 0
		currbts = 0

		# Start Monitoring robots
		self.base.debugmsg(5, "self.base.mscriptlist:", self.base.mscriptlist)
		for grp in self.base.mscriptlist:
			if "Test" in grp.keys() and len(grp["Test"]) > 0:
				self.base.debugmsg(5, "grp:", grp)
				nxtagent = None
				agentwarn = False
				while nxtagent is None:
					if 'filters' in grp:
						nxtagent = self.base.get_next_agent(grp['filters'])
						self.base.debugmsg(7, '(filters) next_agent:', nxtagent)
					else:
						nxtagent = self.base.get_next_agent([])
						self.base.debugmsg(9, '(filters else) next_agent:', nxtagent)
					self.base.debugmsg(5, '(Monitoring) next_agent:', nxtagent)
					if nxtagent is None:
						self.base.debugmsg(7, 'next_agent is None !!!')
						agentwarn = True
						if not self.base.args.nogui and not self.base.run_paused:
							self.base.debugmsg(7, 'self.base.args.nogui:', self.base.args.nogui, "self.base.run_paused:", self.base.run_paused)
							self.display_warning("Not enough Agents available to run Monitoring Robots!\n\nTest run is paused, please add agents to continue or click stop to abort.")
							self.base.debugmsg(7, 'self.base.args.nogui:', self.base.args.nogui, "self.base.run_paused:", self.base.run_paused)

						self.base.debugmsg(5, 'Not enough Agents available to run Robots! (Monitoring)')
						self.base.debugmsg(0, 'Not enough Agents available to run Monitoring Robots!')
						time.sleep(10)
					elif agentwarn:
						agentwarn = False
						if not self.base.args.nogui:
							self.display_info("Enough Agents available to run Monitoring Robots, test will now resume.")
						self.base.debugmsg(0, 'Enough Agents available to run Monitoring Robots, resuming.')
				# now we have agent for monitoring rorbot assign robobt

				if self.base.run_start < 1:
					self.base.run_start = int(time.time())  # time now
					self.base.robot_schedule = self.base.robot_schedule_template
					self.base.robot_schedule["RunName"] = self.base.run_name
					self.base.robot_schedule["Agents"] = {}
					self.base.robot_schedule["Scripts"] = {}
					self.base.robot_schedule["Start"] = self.base.run_start

					if not self.base.args.nogui:
						stm = time.localtime(self.base.robot_schedule["Start"])
						self.base.gui.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))

				gid = grp["Index"]
				self.base.debugmsg(5, "gid", gid, " 	robot_schedule[Scripts].keys()", self.base.robot_schedule["Scripts"].keys())
				if gid not in self.base.robot_schedule["Scripts"].keys():
					self.base.robot_schedule["Scripts"][gid] = {}

				nxtuid = 1
				uid = nxtuid
				grurid = "{}_{}_{}".format(gid, uid, int(time.time()))
				self.base.debugmsg(9, 'uid', uid)
				self.base.robot_schedule["Scripts"][gid][uid] = grurid

				if nxtagent not in self.base.robot_schedule["Agents"].keys():
					self.base.robot_schedule["Agents"][nxtagent] = {}

				self.base.robot_schedule["Agents"][nxtagent][grurid] = {
					"ScriptHash": grp["ScriptHash"],
					"Test": grp["Test"],
					"StartTime": int(time.time()),
					"EndTime": self.base.mon_end,
					"id": grurid
				}

				if "resultnamemode" in grp:
					self.base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = grp["resultnamemode"]
				else:
					if "resultnamemode" in self.base.scriptdefaults:
						self.base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = self.base.scriptdefaults["resultnamemode"]
					else:
						self.base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = self.base.resultnamemodedefault

				if "excludelibraries" in grp:
					self.base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = grp["excludelibraries"]
				else:
					if "excludelibraries" in self.base.scriptdefaults:
						self.base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = self.base.scriptdefaults["excludelibraries"]
					else:
						self.base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = self.base.excludelibrariesdefault

				if "robotoptions" in grp:
					self.base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = grp["robotoptions"]
				else:
					if "robotoptions" in self.base.scriptdefaults:
						self.base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = self.base.scriptdefaults["robotoptions"]

				tt = self.base.includetesttimedefault
				if "includetesttime" in self.base.scriptdefaults:
					tt = self.base.scriptdefaults["includetesttime"]
				if "includetesttime" in grp:
					tt = grp["includetesttime"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["includetesttime"] = str(tt)

				tr = self.base.testrepeaterdefault
				if "testrepeater" in self.base.scriptdefaults:
					tr = self.base.scriptdefaults["testrepeater"]
				if "testrepeater" in grp:
					tr = grp["testrepeater"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["testrepeater"] = str(tr)

				# injectsleepenableddefault = False
				ise = self.base.injectsleepenableddefault
				if "injectsleepenabled" in self.base.scriptdefaults:
					ise = self.base.scriptdefaults["injectsleepenabled"]
				if "injectsleepenabled" in grp:
					ise = grp["injectsleepenabled"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepenabled"] = str(ise)
				if self.base.str2bool(ise):
					# injectsleepminimumdefault = 15
					ismn = self.base.injectsleepminimumdefault
					if "injectsleepminimum" in self.base.scriptdefaults:
						ismn = self.base.scriptdefaults["injectsleepminimum"]
					if "injectsleepminimum" in grp:
						ismn = grp["injectsleepminimum"]
					self.base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepminimum"] = str(ismn)
					# injectsleepmaximumdefault = 45
					ismx = self.base.injectsleepmaximumdefault
					if "injectsleepmaximum" in self.base.scriptdefaults:
						ismx = self.base.scriptdefaults["injectsleepmaximum"]
					if "injectsleepmaximum" in grp:
						ismx = grp["injectsleepmaximum"]
					self.base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepmaximum"] = str(ismx)

				# excludesleep = False
				xs = self.base.excludesleepdefault
				if "excludesleep" in self.base.scriptdefaults:
					xs = self.base.scriptdefaults["excludesleep"]
				if "excludesleep" in grp:
					xs = grp["excludesleep"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["excludesleep"] = str(xs)

				# applypacingtime
				apt = self.base.applypacingtimedefault
				if "applypacingtime" in self.base.scriptdefaults:
					apt = self.base.scriptdefaults["applypacingtime"]
				if "applypacingtime" in grp:
					apt = grp["applypacingtime"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["applypacingtime"] = str(apt)

				# applypacingstart
				aps = self.base.applypacingstartdefault
				if "applypacingstart" in self.base.scriptdefaults:
					aps = self.base.scriptdefaults["applypacingstart"]
				if "applypacingstart" in grp:
					aps = grp["applypacingstart"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["applypacingstart"] = str(aps)

				# disableloglogdefault = False
				dll = self.base.disableloglogdefault
				if "disableloglog" in self.base.scriptdefaults:
					dll = self.base.scriptdefaults["disableloglog"]
				if "disableloglog" in grp:
					dll = grp["disableloglog"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["disableloglog"] = str(dll)
				# disablelogreportdefault = False
				dlr = self.base.disablelogreportdefault
				if "disablelogreport" in self.base.scriptdefaults:
					dlr = self.base.scriptdefaults["disablelogreport"]
				if "disablelogreport" in grp:
					dlr = grp["disablelogreport"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["disablelogreport"] = str(dlr)
				# disablelogoutputdefault = False
				dlo = self.base.disablelogoutputdefault
				if "disablelogoutput" in self.base.scriptdefaults:
					dlo = self.base.scriptdefaults["disablelogoutput"]
				if "disablelogoutput" in grp:
					dlo = grp["disablelogoutput"]
				self.base.robot_schedule["Agents"][nxtagent][grurid]["disablelogoutput"] = str(dlo)

				self.base.Agents[nxtagent]["AssignedMRobots"] += 1
				self.base.debugmsg(5, "self.base.Agents[", nxtagent, "][AssignedMRobots]:", self.base.Agents[nxtagent]["AssignedMRobots"])

				# currbts += 1
				# self.base.debugmsg(2, "Robot:", currbts, "	Test:", grp["Test"], "	Assigned to:", nxtagent)
				self.base.debugmsg(2, "Monitoring Robot:", " Test:", grp["Test"], "	Assigned to:", nxtagent)

				# self.base.debugmsg(9, "robot_schedule", self.base.robot_schedule)

		# Start Plan robots
		self.base.debugmsg(8, "self.base.scriptlist:", self.base.scriptlist)
		for grp in self.base.scriptlist:
			if "Robots" in grp:
				self.base.debugmsg(9, "run_start_threads: totrbts", totrbts, " 	grp:", grp)
				totrbts += int(grp["Robots"])
				self.base.debugmsg(8, "run_start_threads: totrbts", totrbts)

		self.base.debugmsg(8, 'currbts:', currbts, "	totrbts:", totrbts, "	run_paused:", self.base.run_paused)
		while currbts < totrbts:
			self.base.debugmsg(6, "while totrbts", totrbts, " 	currbts:", currbts)
			# totrbts = 0

			if "Start" not in self.base.robot_schedule:
				self.base.robot_schedule["Start"] = 0

			if self.base.run_end > 0 and int(time.time()) > self.base.run_end:
				break

			if self.base.run_paused and int(time.time()) < self.base.run_end:
				nxtagent = self.base.get_next_agent([])
				self.base.debugmsg(6, '(if) next_agent:', nxtagent)
				if nxtagent is None:
					self.base.run_paused = True
					self.base.debugmsg(5, 'Not enough Agents available to run Robots! (if)')
					self.base.debugmsg(3, 'Not enough Agents available to run Robots!')
					time.sleep(10)
				else:
					self.base.run_paused = False
					if not self.base.args.nogui:
						self.display_info("Enough Agents available to run Robots, test will now resume.")
					self.base.debugmsg(0, 'Enough Agents available to run Robots, resuming.')
			else:
				for grp in self.base.scriptlist:
					self.base.debugmsg(9, "grp", grp)
					if "Test" in grp.keys() and len(grp["Test"]) > 0:
						self.base.debugmsg(6, "while totrbts", totrbts, " 	currbts:", currbts)
						self.base.debugmsg(9, "grp[Index]", grp['Index'])

						if 'filters' in grp:
							nxtagent = self.base.get_next_agent(grp['filters'])
							self.base.debugmsg(7, '(filters) next_agent:', nxtagent)
						else:
							nxtagent = self.base.get_next_agent([])
							self.base.debugmsg(9, '(filters else) next_agent:', nxtagent)
						self.base.debugmsg(7, '(else) next_agent:', nxtagent)

						if nxtagent is None:
							self.base.debugmsg(7, 'next_agent is None !!!')
							if not self.base.args.nogui and not self.base.run_paused:
								self.base.debugmsg(7, 'self.base.args.nogui:', self.base.args.nogui, "self.base.run_paused:", self.base.run_paused)
								self.display_warning("Not enough Agents available to run Robots!\n\nTest run is paused, please add agents to continue or click stop to abort.")
								self.base.debugmsg(7, 'self.base.args.nogui:', self.base.args.nogui, "self.base.run_paused:", self.base.run_paused)
							self.base.run_paused = True

							self.base.debugmsg(5, 'Not enough Agents available to run Robots! (else)')
							self.base.debugmsg(0, 'Not enough Agents available to run Robots!')
							time.sleep(10)
							break
						else:
							colour = self.base.line_colour(grp["Index"])
							self.base.debugmsg(9, "Line colour", colour)

							if self.base.run_start < 1:
								self.base.run_start = int(time.time())  # time now
								self.base.robot_schedule = self.base.robot_schedule_template
								self.base.robot_schedule["RunName"] = self.base.run_name
								self.base.robot_schedule["Agents"] = {}
								self.base.robot_schedule["Scripts"] = {}
								self.base.robot_schedule["Start"] = self.base.run_start

								if not self.base.args.nogui:
									stm = time.localtime(self.base.robot_schedule["Start"])
									self.base.gui.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))

								self.base.run_end = self.base.run_start + self.base.mtimebefore + grp["Delay"] + grp["RampUp"] + grp["Run"]
								self.base.debugmsg(9, grp['Index'], " 	run_start:", self.base.run_start, " 	Delay:", grp["Delay"], " 	RampUp:", grp["RampUp"], " 	Run:", grp["Run"], " 	run_end:", self.base.run_end)
								self.base.robot_schedule["End"] = self.base.run_end

								# totrbts = 0

							gid = grp["Index"]
							self.base.debugmsg(9, "gid", gid, " 	robot_schedule[Scripts].keys()", self.base.robot_schedule["Scripts"].keys())
							if gid not in self.base.robot_schedule["Scripts"].keys():
								self.base.robot_schedule["Scripts"][gid] = {}
								self.base.debugmsg(9, "totrbts", totrbts)
								# totrbts += int(grp["Robots"])
								self.base.debugmsg(9, "totrbts", totrbts)

							if gid not in self.base.scriptgrpend.keys() or self.base.scriptgrpend[gid] < self.base.run_start:
								self.base.scriptgrpend[gid] = self.base.run_start + self.base.mtimebefore + grp["Delay"] + grp["RampUp"] + grp["Run"]
								self.base.debugmsg(9, "gid:", gid, " 	run_start:", self.base.run_start, "	self.base.mtimebefore:", self.base.mtimebefore, " 	Delay:", grp["Delay"], " 	RampUp:", grp["RampUp"], " 	Run:", grp["Run"], " 	run_end:", self.base.run_end)
								if self.base.scriptgrpend[gid] > self.base.run_end:
									self.base.run_end = self.base.scriptgrpend[gid]

							time_elapsed = int(time.time()) - self.base.run_start
							self.base.debugmsg(9, 'time_elapsed', time_elapsed, " Monitoring Delay", self.base.mtimebefore, " Delay", grp["Delay"])
							if time_elapsed > (self.base.mtimebefore + grp["Delay"]) - 1:
								uid = 0
								nxtuid = len(self.base.robot_schedule["Scripts"][gid]) + 1
								self.base.debugmsg(9, 'nxtuid', nxtuid)
								# Determine if we should start another user?
								if nxtuid < grp["Robots"] + 1:
									if grp["RampUp"] > 0:
										rupct = (time_elapsed - (self.base.mtimebefore + grp["Delay"])) / grp["RampUp"]
										# self.base.mtimebefore
										# rupct - Ramp-up percent
									else:
										rupct = 1
									self.base.debugmsg(9, 'rupct', rupct)
									# ruusr - Ramp-up user
									ruusr = int(grp["Robots"] * rupct) + 1
									self.base.debugmsg(9, 'nxtuid', nxtuid, 'ruusr', ruusr)
									if nxtuid < ruusr + 1:
										uid = nxtuid
										grurid = "{}_{}_{}".format(gid, uid, int(time.time()))
										self.base.debugmsg(9, 'uid', uid)
										self.base.robot_schedule["Scripts"][gid][uid] = grurid

										if nxtagent not in self.base.robot_schedule["Agents"].keys():
											self.base.robot_schedule["Agents"][nxtagent] = {}

										self.base.robot_schedule["Agents"][nxtagent][grurid] = {
											"ScriptHash": grp["ScriptHash"],
											"Test": grp["Test"],
											"StartTime": int(time.time()),
											"EndTime": self.base.scriptgrpend[gid],
											"id": grurid
										}

										if "resultnamemode" in grp:
											self.base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = grp["resultnamemode"]
										else:
											if "resultnamemode" in self.base.scriptdefaults:
												self.base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = self.base.scriptdefaults["resultnamemode"]
											else:
												self.base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = self.base.resultnamemodedefault

										if "excludelibraries" in grp:
											self.base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = grp["excludelibraries"]
										else:
											if "excludelibraries" in self.base.scriptdefaults:
												self.base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = self.base.scriptdefaults["excludelibraries"]
											else:
												self.base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = self.base.excludelibrariesdefault

										if "robotoptions" in grp:
											self.base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = grp["robotoptions"]
										else:
											if "robotoptions" in self.base.scriptdefaults:
												self.base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = self.base.scriptdefaults["robotoptions"]

										tt = self.base.includetesttimedefault
										if "includetesttime" in self.base.scriptdefaults:
											tt = self.base.scriptdefaults["includetesttime"]
										if "includetesttime" in grp:
											tt = grp["includetesttime"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["includetesttime"] = str(tt)

										tr = self.base.testrepeaterdefault
										if "testrepeater" in self.base.scriptdefaults:
											tr = self.base.scriptdefaults["testrepeater"]
										if "testrepeater" in grp:
											tr = grp["testrepeater"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["testrepeater"] = str(tr)

										# injectsleepenableddefault = False
										ise = self.base.injectsleepenableddefault
										if "injectsleepenabled" in self.base.scriptdefaults:
											ise = self.base.scriptdefaults["injectsleepenabled"]
										if "injectsleepenabled" in grp:
											ise = grp["injectsleepenabled"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepenabled"] = str(ise)
										if self.base.str2bool(ise):
											# injectsleepminimumdefault = 15
											ismn = self.base.injectsleepminimumdefault
											if "injectsleepminimum" in self.base.scriptdefaults:
												ismn = self.base.scriptdefaults["injectsleepminimum"]
											if "injectsleepminimum" in grp:
												ismn = grp["injectsleepminimum"]
											self.base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepminimum"] = str(ismn)
											# injectsleepmaximumdefault = 45
											ismx = self.base.injectsleepmaximumdefault
											if "injectsleepmaximum" in self.base.scriptdefaults:
												ismx = self.base.scriptdefaults["injectsleepmaximum"]
											if "injectsleepmaximum" in grp:
												ismx = grp["injectsleepmaximum"]
											self.base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepmaximum"] = str(ismx)

										# excludesleep = False
										xs = self.base.excludesleepdefault
										if "excludesleep" in self.base.scriptdefaults:
											xs = self.base.scriptdefaults["excludesleep"]
										if "excludesleep" in grp:
											xs = grp["excludesleep"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["excludesleep"] = str(xs)

										# applypacingtime
										apt = self.base.applypacingtimedefault
										if "applypacingtime" in self.base.scriptdefaults:
											apt = self.base.scriptdefaults["applypacingtime"]
										if "applypacingtime" in grp:
											apt = grp["applypacingtime"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["applypacingtime"] = str(apt)

										# applypacingstart
										aps = self.base.applypacingstartdefault
										if "applypacingstart" in self.base.scriptdefaults:
											aps = self.base.scriptdefaults["applypacingstart"]
										if "applypacingstart" in grp:
											aps = grp["applypacingstart"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["applypacingstart"] = str(aps)

										# disableloglogdefault = False
										dll = self.base.disableloglogdefault
										if "disableloglog" in self.base.scriptdefaults:
											dll = self.base.scriptdefaults["disableloglog"]
										if "disableloglog" in grp:
											dll = grp["disableloglog"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["disableloglog"] = str(dll)
										# disablelogreportdefault = False
										dlr = self.base.disablelogreportdefault
										if "disablelogreport" in self.base.scriptdefaults:
											dlr = self.base.scriptdefaults["disablelogreport"]
										if "disablelogreport" in grp:
											dlr = grp["disablelogreport"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["disablelogreport"] = str(dlr)
										# disablelogoutputdefault = False
										dlo = self.base.disablelogoutputdefault
										if "disablelogoutput" in self.base.scriptdefaults:
											dlo = self.base.scriptdefaults["disablelogoutput"]
										if "disablelogoutput" in grp:
											dlo = grp["disablelogoutput"]
										self.base.robot_schedule["Agents"][nxtagent][grurid]["disablelogoutput"] = str(dlo)

										self.base.Agents[nxtagent]["AssignedRobots"] += 1
										self.base.debugmsg(5, "self.base.Agents[", nxtagent, "][AssignedRobots]:", self.base.Agents[nxtagent]["AssignedRobots"])

										currbts += 1
										self.base.debugmsg(2, "Robot:", currbts, "	Test:", grp["Test"], "	Assigned to:", nxtagent)

										self.base.debugmsg(9, "robot_schedule", self.base.robot_schedule)

						if self.base.run_end > 0 and int(time.time()) > self.base.run_end:
							self.base.debugmsg(6, "Test Paused: run_end:", self.base.run_end, "	time:", int(time.time()))
							self.base.run_paused = True
							break

						time.sleep(0.1)
						if not self.base.args.nogui:
							etm = time.gmtime(int(time.time()) - self.base.robot_schedule["Start"])
							self.base.gui.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))

		self.base.debugmsg(2, "Robot Ramp Up Completed")

	def sr_users_validate(self, *args):
		self.base.debugmsg(5, "args:", args)
		usrs = 0
		if args:
			r = args[0]
			if len(args) > 1:
				usrs = args[1]
			self.base.debugmsg(6, "Row:", r, "Robots:", usrs)
			self.base.debugmsg(8, "self.base.scriptlist:", self.base.scriptlist)
			self.base.scriptlist[r]["Robots"] = int(usrs)

		if not self.base.args.nogui:
			self.base.gui.sr_users_validate(*args)
		return True

	def sr_delay_validate(self, *args):
		self.base.debugmsg(5, "args:", args)
		if args:
			r = args[0]
			dly = 0
			if len(args) > 1:
				dly = str(args[1])
			self.base.debugmsg(6, "Row:", r, "Delay:", dly)
			self.base.scriptlist[r]["Delay"] = int(dly)

		if not self.base.args.nogui:
			self.base.gui.sr_delay_validate(*args)
		return True

	def sr_rampup_validate(self, *args):
		self.base.debugmsg(5, "args:", args)
		if args:
			r = args[0]
			rmp = None
			if len(args) > 1:
				rmp = str(args[1])
			self.base.debugmsg(6, "Row:", r, "RampUp:", rmp)
			self.base.scriptlist[r]["RampUp"] = int(rmp)

		if not self.base.args.nogui:
			self.base.gui.sr_rampup_validate(*args)
		return True

	def sr_run_validate(self, *args):
		self.base.debugmsg(5, "args:", args)
		if args:
			r = args[0]
			run = None
			if len(args) > 1:
				run = str(args[1])
			self.base.debugmsg(6, "Row:", r, "Run:", run)
			self.base.scriptlist[r]["Run"] = int(run)

		if not self.base.args.nogui:
			self.base.gui.sr_run_validate(*args)
		return True

	def sr_file_validate(self, r, *args):
		self.base.debugmsg(9, "r:", r, "	args:", args)
		if args:
			scriptfile = args[0]
		else:
			scriptfile = ""

		if not os.path.exists(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\ncannot be found by RFSwarm Manager."
			if not self.base.args.nogui:
				self.display_warning(msg)
			else:
				self.base.debugmsg(0, msg)
			return False
		elif not os.path.isfile(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\nis a directory, not a file."
			if not self.base.args.nogui:
				self.display_warning(msg)
			else:
				self.base.debugmsg(0, msg)
			return False

		self.base.debugmsg(7, "scriptfile:", scriptfile)
		if len(scriptfile) > 0:
			self.base.scriptlist[r]["Script"] = scriptfile
			relpath = self.base.get_relative_path(self.base.config['Plan']['ScriptDir'], scriptfile)
			script_hash = self.base.hash_file(scriptfile, relpath)
			self.base.scriptlist[r]["ScriptHash"] = script_hash

			if script_hash not in self.base.scriptfiles:
				self.base.scriptfiles[script_hash] = {
					"id": script_hash,
					"localpath": scriptfile,
					"relpath": relpath,
					"type": "script"
				}

				t = threading.Thread(target=self.base.find_dependancies, args=(script_hash, ))
				t.start()

		else:
			if "ScriptHash" in self.base.scriptlist[r]:
				oldhash = self.base.scriptlist[r]["ScriptHash"]
				t = threading.Thread(target=self.base.remove_hash, args=(oldhash, ))
				t.start()

			self.base.scriptlist[r]["Script"] = ''
			self.base.scriptlist[r]["ScriptHash"] = ''

		self.plan_scnro_chngd = True
		if not self.base.args.nogui:
			self.base.gui.sr_file_validate(r, *args)
		return True

	def sr_test_validate(self, *args):
		self.base.debugmsg(5, "args:", args)
		# r = int(args[0][-1:])+1
		r = int(args[0][3:])
		self.base.debugmsg(9, "r:", r)

		v = None
		if len(args) > 1 and len(args[1]) > 1:
			v = args[1]
			self.base.debugmsg(9, "v:", v)
			self.base.scriptlist[r]["Test"] = v

		self.base.debugmsg(9, "scriptlist[r]:", self.base.scriptlist[r])

		if not self.base.args.nogui:
			self.base.gui.sr_test_validate(*args)
		return True

	def UpdateAgents(self):

		uploadcount = 0
		removeagents = []
		robot_count = 0
		monitor_count = 0
		time_elapsed = int(time.time()) - self.base.agenttgridupdate
		if time_elapsed >= 5:
			self.base.debugmsg(6, "time_elapsed:", time_elapsed)

			self.base.agenttgridupdate = int(time.time())
			agntlst = list(self.base.Agents.keys())
			self.base.debugmsg(6, "agntlst:", agntlst)
			for agnt in agntlst:

				includerobots = True

				if "Uploading" in self.base.Agents[agnt]["Status"]:
					uploadcount += 1

				tm = self.base.Agents[agnt]["LastSeen"]
				agnt_elapsed = int(time.time()) - tm
				if agnt_elapsed > 30:
					self.base.Agents[agnt]["Status"] = "Offline?"
					includerobots = False
				if agnt_elapsed > 300:
					removeagents.append(agnt)
					includerobots = False

				if includerobots:
					robot_count += self.base.Agents[agnt]["Robots"]
					monitor_count += self.base.Agents[agnt]["Monitor"]

			if self.base.total_robots > 0 and robot_count < 1 and self.base.total_monitor > 0 and monitor_count < 1:
				# run finished so clear run name
				self.base.save_metrics(self.base.run_name, "Scenario", int(time.time()), "total_robots", robot_count, self.base.srvdisphost)
				self.base.save_metrics(self.base.run_name, "Scenario", int(time.time()), "monitor_robots", monitor_count, self.base.srvdisphost)
				self.base.save_metrics(self.base.run_name, "Scenario", int(time.time()), "End_Time", int(time.time()), self.base.srvdisphost)
				self.base.save_metrics("Time", "Scenario", int(time.time()), "End", int(time.time()), self.base.srvdisphost)
				self.base.run_name = ""
				self.base.robot_schedule["RunName"] = self.base.run_name

			# Update self.base.mon_end time on monitoring robot's jobs in the situations where:
			# self.base.total_robots > 0 and time now + self.base.mtimeafter is greater than self.base.mon_end
			# (Ensure we monitor long enough)
			if self.base.total_robots > 0:
				new_mon_end = int(time.time()) + self.base.mtimeafter
				if new_mon_end > self.base.mon_end:
					self.base.mon_end = new_mon_end
					self.update_monitoring_jobs_mon_end()

			# self.base.total_robots > 0 and robot_count < 1 and time now + self.base.mtimeafter is less than self.base.mon_end
			# (Ensure we don't monitor too long)
			if self.base.total_robots > 0 and robot_count < 1:
				new_mon_end = int(time.time()) + self.base.mtimeafter
				if new_mon_end < self.base.mon_end:
					self.base.mon_end = new_mon_end
					self.update_monitoring_jobs_mon_end()

			self.base.total_robots = robot_count
			self.base.total_monitor = monitor_count

			for agnt in removeagents:
				# this should prevent issue RuntimeError: dictionary changed size during iteration
				del self.base.Agents[agnt]

			# temp. fix for disconnecting agent when inactive:
			self.updatethread = threading.Thread(target=self.delayed_UpdateAgents)
			self.updatethread.start()

			if not self.base.args.nogui:
				self.base.debugmsg(6, "nogui:", self.base.args.nogui)
				try:
					self.base.gui.UpdateAgents()
				except Exception:
					pass

			# Save Total Robots Metric
			if len(self.base.run_name) > 0:
				self.base.save_metrics(self.base.run_name, "Scenario", int(time.time()), "total_robots", self.base.total_robots, self.base.srvdisphost)
				self.base.save_metrics(self.base.run_name, "Scenario", int(time.time()), "monitor_robots", self.base.total_monitor, self.base.srvdisphost)
			else:
				self.base.save_metrics("PreRun", "Scenario", int(time.time()), "total_robots", self.base.total_robots, self.base.srvdisphost)
				self.base.save_metrics("PreRun", "Scenario", int(time.time()), "monitor_robots", self.base.total_monitor, self.base.srvdisphost)

			# if self.base.args.run:
			self.base.debugmsg(5, "self.base.args.run:", self.base.args.run, "	self.base.args.nogui:", self.base.args.nogui, "	run_end:", self.base.run_end, "	time:", int(time.time()))
			self.base.debugmsg(5, "self.base.posttest:", self.base.posttest, "	total_robots:", self.base.total_robots)
			self.base.debugmsg(5, "self.base.posttest:", self.base.posttest, "	total_monitor:", self.base.total_monitor)
			self.base.debugmsg(5, "run_finish:", self.base.run_finish, "	time:", int(time.time()), "uploadcount:", uploadcount)
			if self.base.run_end > 0\
				and self.base.run_end < int(time.time())\
				and self.base.total_robots < 1\
				and self.base.total_monitor < 1\
				and not self.base.posttest\
				and self.base.run_finish < 1\
				and uploadcount < 1:

				self.base.run_finish = int(time.time())
				self.base.debugmsg(5, "run_end:", self.base.run_end, "	time:", int(time.time()), "	total_robots:", self.base.total_robots, "	total_monitor", self.base.total_monitor)
				# self.base.save_metrics(self.base.run_name, "Scenario", self.base.run_finish, "End_Time", self.base.run_finish, self.base.srvdisphost)
				self.base.save_metrics("Time", "Scenario", self.base.run_finish, "Upload_Finished", self.base.run_finish, self.base.srvdisphost)

				if not self.base.args.nogui:
					time.sleep(1)
					self.base.gui.delayed_UpdateRunStats()

			if self.base.run_finish > 0 and self.base.run_finish + 60 < int(time.time()) and not self.base.posttest:
				self.base.debugmsg(0, "Test Completed:	", self.base.run_finish, "[", datetime.now().isoformat(sep=' ', timespec='seconds'), "]")
				self.base.posttest = True
				if self.base.args.nogui:
					self.base.debugmsg(9, "report_text")
					self.base.report_text()
					self.base.debugmsg(6, "on_closing")
					self.on_closing()
				else:
					time.sleep(1)
					self.base.gui.delayed_UpdateRunStats()

	def delayed_UpdateAgents(self):
		time.sleep(10)
		self.UpdateAgents()

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# End class RFSwarmCore
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class RFSwarm():
	def __init__(self):

		multiprocessing.freeze_support()
		# base = RFSwarmBase()

		core = RFSwarmCore()
		# core = rfswarm()

		try:
			core.mainloop()

			# while core.base.run_dbthread:
			# 	time.sleep(300)

		except KeyboardInterrupt:
			core.on_closing()
		except Exception as e:
			core.base.debugmsg(1, "core.Exception:", e)
			core.on_closing()

def main():
	rfs = RFSwarm()

if __name__ == '__main__':
	main()

if __name__ == 'rfswarm':
	main()
