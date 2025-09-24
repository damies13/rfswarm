#!/usr/bin/python
#
# 	Robot Framework Swarm
# 		Manager
#    Version 1.6.0
#

# 	Helpful links
#
#

import argparse
import base64
import configparser
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


matplotlib.use("TkAgg")  # required for matplot graphs

__name__ = "rfswarm"


class AgentServer(BaseHTTPRequestHandler):

	def do_HEAD(self):
		return

	def do_POST(self):
		threadstart = time.time()
		httpcode = 200
		try:
			parsed_path = urllib.parse.urlparse(self.path)
			base.debugmsg(7, "parsed_path.path", parsed_path.path)
			if (parsed_path.path in ["/AgentStatus", "/Jobs", "/Scripts", "/File", "/Result", "/Metric"]):

				jsonresp = {}
				rawData = (self.rfile.read(int(self.headers['content-length']))).decode('utf-8')
				base.debugmsg(7, "rawData: ", rawData)
				base.debugmsg(9, "parsed_path.path", parsed_path.path)
				if parsed_path.path == "/AgentStatus":
					jsonreq = json.loads(rawData)

					requiredfields = ["AgentName", "Status", "Robots", "CPU%", "MEM%", "NET%"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							break

					if httpcode == 200:
						base.debugmsg(9, "do_POST: jsonreq:", jsonreq)
						core.register_agent(jsonreq)
						jsonresp["AgentName"] = jsonreq["AgentName"]
						jsonresp["Status"] = "Updated"

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
						base.debugmsg(9, "base.scriptlist:", base.scriptlist)

						scripts = []
						base.debugmsg(9, "base.scriptfiles:", base.scriptfiles)
						for hash in base.scriptfiles:
							base.debugmsg(9, "hash:", hash, base.scriptfiles[hash])
							scripts.append({'File': base.scriptfiles[hash]['relpath'], "Hash": hash})
						base.debugmsg(9, "scripts:", scripts)
						jsonresp["Scripts"] = scripts

						t = threading.Thread(target=base.check_files_changed)
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
								if "Hash" in jsonreq and len(jsonreq["Hash"]) > 0 and jsonreq["Hash"] in base.scriptfiles:
									hash = jsonreq["Hash"]
									jsonresp["Hash"] = jsonreq["Hash"]
									jsonresp["File"] = base.scriptfiles[hash]['relpath']
									localpath = base.scriptfiles[hash]['localpath']
									buf = "\n"
									with open(localpath, 'rb') as afile:
										buf = afile.read()
									base.debugmsg(9, "buf:", buf)
									compressed = lzma.compress(buf)
									base.debugmsg(9, "compressed:", compressed)
									encoded = base64.b64encode(compressed)
									base.debugmsg(9, "encoded:", encoded)

									jsonresp["FileData"] = encoded.decode('ASCII')

								else:
									httpcode = 404
									jsonresp["Message"] = "Known File Hash required to download a file"

							if jsonreq["Action"] == "Status":
								if "Hash" in jsonreq and len(jsonreq["Hash"]) > 0:
									jsonresp["Hash"] = jsonreq["Hash"]
									if jsonreq["Hash"] in base.scriptfiles or jsonreq["Hash"] in base.uploadfiles:
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
									if jsonreq["Hash"] in base.uploadfiles:
										jsonresp["Result"] = "Exists"
									else:
										# base.debugmsg(5, "jsonreq:", jsonreq)
										# jsonreq: {
										# 		'AgentName': 'DavesMBP',
										# 		'Action': 'Upload',
										# 		'Hash': 'e7b73742ee1c3d558c4d20adf639d8d8',
										# 		'File': 'OC_Demo_2_1_3_1608352678_1_1608352681/Browse_Store_Product_1.log',
										# 		'FileData': <filedata>
										# 	}
										logdir = os.path.join(base.datapath, "logs")
										if os.path.exists(logdir) and os.path.isfile(logdir):
											logdir = os.path.join(base.datapath, "logs" + str(int(time.time())))

										base.debugmsg(7, "logdir:", logdir)
										localpath = os.path.join(logdir, jsonreq['File'])
										base.debugmsg(7, "localpath:", localpath)
										jsonreq['LocalFile'] = localpath
										base.uploadfiles[jsonreq["Hash"]] = jsonreq

										t = threading.Thread(target=base.save_upload_file, args=(jsonreq["Hash"],))
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
						jsonresp["StartTime"] = base.run_start
						jsonresp["EndTime"] = base.run_end
						jsonresp["RunName"] = base.robot_schedule["RunName"]
						jsonresp["Abort"] = base.run_abort
						jsonresp["UploadMode"] = base.uploadmode
						jsonresp["EnvironmentVariables"] = base.envvars

						# base.robot_schedule["Agents"]
						if jsonresp["AgentName"] in base.robot_schedule["Agents"].keys():
							jsonresp["Schedule"] = base.robot_schedule["Agents"][jsonresp["AgentName"]]
						else:
							jsonresp["Schedule"] = {}

				# , "Result"
				if parsed_path.path == "/Result":
					jsonreq = json.loads(rawData)
					base.debugmsg(6, "Result: jsonreq:", jsonreq)
					requiredfields = ["AgentName", "ResultName", "Result", "ElapsedTime", "StartTime", "EndTime", "ScriptIndex", "Iteration", "Sequence"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							base.debugmsg(5, httpcode, ":", message)
							break

					if "Robot" not in jsonreq:
						jsonreq["Robot"] = 0
						if "VUser" in jsonreq:
							jsonreq["Robot"] = jsonreq["VUser"]

					if httpcode == 200:
						base.debugmsg(7, "Result: httpcode:", httpcode)
						jsonresp["AgentName"] = jsonreq["AgentName"]

						core.register_result(
							jsonreq["AgentName"], jsonreq["ResultName"], jsonreq["Result"],
							jsonreq["ElapsedTime"], jsonreq["StartTime"], jsonreq["EndTime"],
							jsonreq["ScriptIndex"], jsonreq["Robot"], jsonreq["Iteration"],
							jsonreq["Sequence"]
						)

						jsonresp["Result"] = "Queued"
						base.debugmsg(7, "Result: jsonresp[\"Result\"]:", jsonresp["Result"])

				if parsed_path.path == "/Metric":
					base.debugmsg(7, "Metric")
					jsonreq = json.loads(rawData)
					base.debugmsg(7, "Metric: jsonreq:", jsonreq)
					requiredfields = ["AgentName", "PrimaryMetric", "MetricType", "MetricTime", "SecondaryMetrics"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							base.debugmsg(9, httpcode, ":", message)
							break

					if httpcode == 200:
						base.debugmsg(7, "Result: httpcode:", httpcode)
						jsonresp["Metric"] = jsonreq["PrimaryMetric"]

						# core.register_metric(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"], jsonreq["AgentName"])
						t = threading.Thread(target=core.register_metric, args=(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"], jsonreq["AgentName"]))
						t.start()

						jsonresp["Result"] = "Queued"
						base.debugmsg(7, "Metric: jsonresp[\"Metric\"]:", jsonresp["Metric"])

				base.debugmsg(7, "jsonresp:", jsonresp)
				message = json.dumps(jsonresp)
			else:
				httpcode = 404
				message = "Unrecognised request: '{}'".format(parsed_path)

		except Exception as e:
			base.debugmsg(6, "AgentServer: do_POST:", e)
			httpcode = 500
			message = str(e)
		self.send_response(httpcode)
		try:
			self.end_headers()
			self.wfile.write(bytes(message, "utf-8"))
		except Exception as e:
			base.debugmsg(6, "Disconnected before response was sent:", e)
		threadend = time.time()
		# base.debugmsg(5, parsed_path.path, "	threadstart:", "%.3f" % threadstart, "threadend:", "%.3f" % threadend, "Time Taken:", "%.3f" % (threadend-threadstart))
		base.debugmsg(7, "%.3f" % (threadend - threadstart), "seconds for ", parsed_path.path)
		return

	def do_GET(self):
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
			base.debugmsg(6, "AgentServer: do_GET:", e)
			httpcode = 500
			message = str(e)

		self.send_response(httpcode)
		try:
			self.end_headers()
			self.wfile.write(bytes(message, "utf-8"))
		except Exception as e:
			base.debugmsg(6, "Disconnected before response was sent:", e)
		threadend = time.time()
		# base.debugmsg(5, parsed_path.path, "		threadstart:", "%.3f" % threadstart, "threadend:", "%.3f" % threadend, "Time Taken:", "%.3f" % (threadend-threadstart))
		base.debugmsg(5, "%.3f" % (threadend - threadstart), "seconds for ", parsed_path.path)
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
		base.debugmsg(0, "Robot Framework Swarm: Manager")
		base.debugmsg(0, "	Version", base.version)
		signal.signal(signal.SIGINT, self.on_closing)

		base.debugmsg(9, "ArgumentParser")
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
		base.args = parser.parse_args()
		base.core = self

		base.debugmsg(6, "base.args: ", base.args)

		if base.args.debug:
			base.debuglvl = int(base.args.debug)

		if base.args.version:
			self.show_additional_versions()
			exit()

		if base.args.create:
			if base.args.create.upper() in ["ICON", "ICONS"]:
				self.create_icons()
			else:
				base.debugmsg(0, "create with option ", base.args.create.upper(), "not supported.")
			exit()

		if base.args.starttime:
			base.run_starttime = base.parse_time(base.args.starttime)
			base.debugmsg(5, "run_starttime:", base.run_starttime)

		base.debugmsg(6, "ConfigParser")
		base.config = configparser.ConfigParser()
		scrdir = os.path.dirname(__file__)
		base.debugmsg(6, "scrdir: ", scrdir)
		#
		# 	ensure ini file
		#
		base.manager_ini = base.findiniloctaion()

		# rename old ini file if it exists
		# 	this section can probably be removed in the future, but will probably need to stay for at least a few releases
		base.gui_ini = os.path.join(scrdir, "RFSwarmGUI.ini")
		if os.path.isfile(base.gui_ini) and not os.path.isfile(base.manager_ini):
			try:
				os.rename(base.gui_ini, base.manager_ini)
			except Exception:
				pass

		# old ini file

		if base.args.ini:
			base.save_ini = False
			base.debugmsg(5, "base.args.ini: ", base.args.ini)
			base.manager_ini = base.args.ini

		if os.path.isfile(base.manager_ini):
			base.debugmsg(7, "agentini: ", base.manager_ini)
			arrconfigfile = os.path.splitext(base.manager_ini)
			base.debugmsg(5, "arrconfigfile: ", arrconfigfile)
			if len(arrconfigfile) < 2:
				base.debugmsg(0, "Configuration file ", base.manager_ini, " missing extention, unable to determine supported format. Plesae use extentions .ini, .yaml or .json")
				exit()
			if arrconfigfile[1].lower() not in [".ini", ".yml", ".yaml", ".json"]:
				base.debugmsg(0, "Configuration file ", base.manager_ini, " has an invalid extention, unable to determine supported format. Plesae use extentions .ini, .yaml or .json")
				exit()
			if arrconfigfile[1].lower() == ".ini":
				base.config.read(base.manager_ini, encoding="utf8")
			else:
				configdict = {}
				if arrconfigfile[1].lower() in [".yml", ".yaml"]:
					# read yaml file
					base.debugmsg(5, "read yaml file")
					with open(base.manager_ini, 'r', encoding="utf-8") as f:
						configdict = yaml.safe_load(f)
						configdict = base.configparser_safe_dict(configdict)
						base.debugmsg(5, "configdict: ", configdict)
				if arrconfigfile[1].lower() == ".json":
					# read json file
					base.debugmsg(5, "read json file")
					with open(base.manager_ini, 'r', encoding="utf-8") as f:
						configdict = json.load(f)
						configdict = base.configparser_safe_dict(configdict)
						base.debugmsg(5, "configdict: ", configdict)
				base.debugmsg(5, "configdict: ", configdict)
				base.config.read_dict(configdict)
		else:
			base.saveini()

		base.debugmsg(0, "	Configuration File: ", base.manager_ini)

		base.debugmsg(9, "base.config: ", base.config._sections)
		if base.args.scenario:
			base.save_ini = False
			base.debugmsg(5, "base.args.scenario: ", base.args.scenario)
			scenariofile = os.path.abspath(base.args.scenario)
			base.debugmsg(5, "scenariofile: ", scenariofile)
			if 'Plan' not in base.config:
				base.config['Plan'] = {}
				base.config['Plan']['ScenarioFile'] = ""
			base.debugmsg(6, "Plan:scenariofile: ", base.config['Plan']['ScenarioFile'])
			base.config['Plan']['ScenarioFile'] = base.inisafevalue(scenariofile)
			base.debugmsg(6, "Plan:scenariofile: ", base.config['Plan']['ScenarioFile'])

		if base.args.dir:
			base.save_ini = False
			base.debugmsg(5, "base.args.dir: ", base.args.dir)
			ResultsDir = os.path.abspath(base.args.dir)
			base.debugmsg(5, "ResultsDir: ", ResultsDir)
			if 'Run' not in base.config:
				base.config['Run'] = {}
			base.config['Run']['ResultsDir'] = base.inisafevalue(ResultsDir)

		if base.args.ipaddress:
			base.save_ini = False
			base.debugmsg(5, "base.args.ipaddress: ", base.args.ipaddress)
			if 'Server' not in base.config:
				base.config['Server'] = {}
			base.config['Server']['BindIP'] = base.inisafevalue(base.args.ipaddress)

		if base.args.port:
			base.save_ini = False
			base.debugmsg(5, "base.args.port: ", base.args.port)
			if 'Server' not in base.config:
				base.config['Server'] = {}
			base.config['Server']['BindPort'] = base.inisafevalue(base.args.port)

		#
		# GUI
		#

		if 'GUI' not in base.config:
			base.config['GUI'] = {}
			base.saveini()

		if 'win_width' not in base.config['GUI']:
			base.config['GUI']['win_width'] = "800"
			base.saveini()

		if 'win_height' not in base.config['GUI']:
			base.config['GUI']['win_height'] = "390"
			base.saveini()

		if 'graph_list' not in base.config['GUI']:
			base.config['GUI']['graph_list'] = ""
			base.saveini()

		#
		# Plan
		#

		if 'Plan' not in base.config:
			base.config['Plan'] = {}
			base.saveini()

		if 'ScriptDir' not in base.config['Plan']:
			base.config['Plan']['ScriptDir'] = base.inisafedir(base.dir_path)
			base.debugmsg(5, "ScriptDir: ", base.config['Plan']['ScriptDir'])
			base.saveini()
		else:
			if not os.path.isdir(base.config['Plan']['ScriptDir']):
				base.config['Plan']['ScriptDir'] = base.inisafedir(base.dir_path)
				base.debugmsg(5, "ScriptDir: ", base.config['Plan']['ScriptDir'])
				base.saveini()

		if 'ScenarioDir' not in base.config['Plan']:
			base.config['Plan']['ScenarioDir'] = base.inisafedir(base.dir_path)
			base.saveini()
		else:
			if not os.path.isdir(base.config['Plan']['ScenarioDir']):
				base.config['Plan']['ScenarioDir'] = base.inisafedir(base.dir_path)
				base.saveini()

		missing_scenario = False
		if 'ScenarioFile' not in base.config['Plan']:
			base.config['Plan']['ScenarioFile'] = ""
			base.debugmsg(6, "Plan:scenariofile: ", base.config['Plan']['ScenarioFile'])
			base.saveini()
		else:
			# check file exists - it may have been deleted since rfswarm last ran with this ini file
			base.debugmsg(6, "Plan:scenariofile: ", base.config['Plan']['ScenarioFile'])
			if not os.path.exists(base.config['Plan']['ScenarioFile']):
				if len(base.config['Plan']['ScenarioFile']) > 1:
					missing_scenario = True
					msg = "Scenario file Not found:\n" + base.config['Plan']['ScenarioFile']
				base.config['Plan']['ScenarioFile'] = ""
				base.debugmsg(6, "Plan:scenariofile: ", base.config['Plan']['ScenarioFile'])
				base.config['Plan']['ScriptDir'] = base.inisafedir(base.dir_path)
				base.debugmsg(5, "ScriptDir: ", base.config['Plan']['ScriptDir'])
				base.config['Plan']['ScenarioDir'] = base.inisafedir(base.dir_path)
				base.saveini()

		#
		# Monitoring
		#

		if 'Monitoring' not in base.config:
			base.config['Monitoring'] = {}
			base.saveini()

		if 'ScriptDir' not in base.config['Monitoring']:
			base.config['Monitoring']['ScriptDir'] = base.config['Plan']['ScriptDir']

		#
		# Run
		#

		if 'Run' not in base.config:
			base.config['Run'] = {}
			base.saveini()

		if 'ResultsDir' not in base.config['Run']:
			base.config['Run']['ResultsDir'] = base.inisafevalue(os.path.join(base.dir_path, "results"))
			base.saveini()
		else:
			if not os.path.isdir(base.config['Run']['ResultsDir']):
				base.config['Run']['ResultsDir'] = base.inisafevalue(base.dir_path)
				base.saveini()

		if 'display_index' not in base.config['Run']:
			base.config['Run']['display_index'] = str(False)
			base.saveini()

		if 'display_iteration' not in base.config['Run']:
			base.config['Run']['display_iteration'] = str(False)
			base.saveini()

		if 'display_sequence' not in base.config['Run']:
			base.config['Run']['display_sequence'] = str(False)
			base.saveini()

		if 'display_percentile' not in base.config['Run']:
			base.config['Run']['display_percentile'] = str(90)
			base.saveini()

		#
		# Server
		#

		if 'Server' not in base.config:
			base.config['Server'] = {}
			base.saveini()

		if 'BindIP' not in base.config['Server']:
			base.config['Server']['BindIP'] = ''
			base.saveini()

		if 'BindPort' not in base.config['Server']:
			base.config['Server']['BindPort'] = "8138"
			base.saveini()

		#
		# 	end ensure ini file
		#

		if base.args.nogui:
			base.save_ini = False
			if not base.args.run:
				base.args.run = True
		else:
			base.gui = RFSwarmGUItk(base)

		if missing_scenario:
			self.display_warning(msg)

		self.BuildCore()

		base.debugmsg(5, "run_agent_server")
		base.Agentserver = threading.Thread(target=self.run_agent_server)
		base.Agentserver.start()
		base.debugmsg(5, "run_db_thread")
		base.run_dbthread = True
		base.dbthread = threading.Thread(target=base.run_db_thread)
		base.dbthread.start()

	def show_additional_versions(self):

		base.debugmsg(0, "	Dependancy Versions")
		try:
			base.debugmsg(0, "		Python Version", sys.version)
		except Exception as e:
			base.debugmsg(3, "error:", e)

		try:
			base.debugmsg(0, "		SQLite Version", sqlite3.sqlite_version)
		except Exception as e:
			base.debugmsg(3, "error:", e)

		try:
			import tkinter as tk
			base.debugmsg(0, "		Tcl/Tk Version", tk.Tcl().call("info", "patchlevel"))
		except Exception as e:
			base.debugmsg(3, "error:", e)

	def BuildCore(self):
		base.debugmsg(5, "BuildCore")

		base.debugmsg(6, "Plan:scenariofile: ", base.config['Plan']['ScenarioFile'])
		base.debugmsg(5, "BuildCorePlan")
		self.BuildCorePlan()
		base.debugmsg(5, "BuildCoreMonitoring")
		self.BuildCoreMonitoring()
		base.debugmsg(5, "BuildCoreRun")
		self.BuildCoreRun()

	def scheduled_start(self):
		while base.keeprunning:
			if base.run_starttime > 0:
				sec2st = base.run_starttime - int(time.time())
				if sec2st < 1:
					base.run_start = 0
					base.run_starttime = 0
					base.debugmsg(5, "sec2st:", sec2st)
					autostart = threading.Thread(target=self.autostart)
					autostart.start()
			time.sleep(1)

	def autostart(self):
		base.debugmsg(5, "appstarted:", base.appstarted)
		# wait for mainloops to finished
		while not base.appstarted:
			time.sleep(1)
			base.debugmsg(5, "appstarted:", base.appstarted)

		if base.run_start < 1:
			neededagents = 1
			if base.args.agents:
				neededagents = int(base.args.agents)

			base.debugmsg(5, "len(base.Agents):", len(base.Agents), "	neededagents:", neededagents)
			# agntlst = list(base.Agents.keys())
			# while len(base.Agents) < neededagents:
			while base.agents_ready() < neededagents and base.keeprunning:
				base.debugmsg(1, "Waiting for Agents")
				# base.debugmsg(3, "Agents:", len(base.Agents), "	Agents Needed:", neededagents)
				base.debugmsg(3, "Agents:", base.agents_ready(), "	Agents Needed:", neededagents)
				time.sleep(10)

			if base.keeprunning:
				if base.args.nogui:
					base.debugmsg(5, "core.ClickPlay")
					self.ClickPlay()
				else:
					base.debugmsg(5, "base.gui.ClickPlay")
					base.gui.ClickPlay()

	def mainloop(self):

		base.debugmsg(5, "mainloop start")

		if base.args.run and base.run_starttime < 1:
			# auto click play ?
			# self.autostart()
			autostart = threading.Thread(target=self.autostart)
			autostart.start()

		autostart = threading.Thread(target=self.scheduled_start)
		autostart.start()

		if not base.args.nogui:
			base.gui.mainloop()

		while base.run_dbthread:
			time.sleep(10)

		base.debugmsg(5, "mainloop end")

	def on_closing(self, _event=None, *args):
		# , _event=None is required for any function that has a shortcut key bound to it

		base.keeprunning = False
		self.neededagents = 0

		if base.appstarted:
			try:
				base.debugmsg(0, "Shutdown Agent Manager")
				base.agenthttpserver.shutdown()
				base.debugmsg(9, "Shutdown Agent Manager after")
			except Exception:
				pass

		try:
			if base.Agentserver.is_alive():
				base.debugmsg(9, "Join Agent Manager Thread")
				base.Agentserver.join(timeout=30)
				base.debugmsg(9, "Join Agent Manager Thread after")
		except Exception:
			pass

		try:
			base.run_dbthread = False
			if base.dbthread.is_alive():
				base.debugmsg(9, "Join DB Thread")
				base.dbthread.join(timeout=30)
				base.debugmsg(9, "Join DB Thread after")
		except Exception:
			pass

		try:
			base.debugmsg(3, "Save ini File")
			base.saveini()
		except Exception:
			pass

		time.sleep(1)
		base.debugmsg(2, "Exit")
		try:
			sys.exit(0)
		except SystemExit as e:
			try:
				remaining_threads = [t for t in threading.enumerate() if t is not threading.main_thread() and t.is_alive()]
				if remaining_threads:
					base.debugmsg(5, "Failed to gracefully exit RFSwarm-Manager. Forcing immediate exit.")
					for thread in remaining_threads:
						base.debugmsg(9, "Thread name:", thread.name)
					os._exit(0)
				else:
					raise e

			except Exception as e:
				base.debugmsg(3, "Failed to exit with error:", e)
				os._exit(1)
		sys.stdout.flush()
		sys.stderr.flush()

	def create_icons(self):
		base.debugmsg(0, "Creating application icons for RFSwarm Manager")
		appname = "RFSwarm Manager"
		namelst = appname.split()
		base.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		base.debugmsg(6, "projname:", projname)
		pipdata = importlib.metadata.distribution(projname)
		# print("files:", pipdata.files)
		# print("file0:", pipdata.files[0])
		manager_executable = os.path.abspath(str(pipdata.locate_file(pipdata.files[0])))
		base.debugmsg(5, "manager_executable:", manager_executable)

		script_dir = os.path.dirname(os.path.abspath(__file__))
		base.debugmsg(5, "script_dir:", script_dir)
		icon_dir = os.path.join(pipdata.locate_file('rfswarm_manager'), "icons")
		base.debugmsg(5, "icon_dir:", icon_dir)

		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				try:
					base.ensuredir("/usr/share/applications")
					directoryfilename = os.path.join("/usr/share/applications", "rfswarm.directory")
					directorydata = ["test"]
					with open(directoryfilename, 'w') as df:
						df.writelines(directorydata)
					os.remove(directoryfilename)
					fileprefix = "/usr/share"
				except Exception:
					pass

			fileprefix = os.path.expanduser(fileprefix)

			# base.debugmsg(5, "Create .directory file")
			# directorydata = []
			# directorydata.append('[Desktop Entry]\n')
			# directorydata.append('Type=Directory\n')
			# directorydata.append('Name=RFSwarm\n')
			# directorydata.append('Icon=rfswarm-logo\n')
			#
			# directoryfilename = os.path.join(fileprefix, "desktop-directories", "rfswarm.directory")
			# directorydir = os.path.dirname(directoryfilename)
			# base.ensuredir(directorydir)
			#
			# base.debugmsg(5, "directoryfilename:", directoryfilename)
			# with open(directoryfilename, 'w') as df:
			# 	df.writelines(directorydata)
			#
			# directoryfilename = os.path.join(fileprefix, "applications", "rfswarm.directory")
			# directorydir = os.path.dirname(directoryfilename)
			# base.ensuredir(directorydir)
			# base.debugmsg(5, "directoryfilename:", directoryfilename)
			# with open(directoryfilename, 'w') as df:
			# 	df.writelines(directorydata)

			base.debugmsg(5, "Create .desktop file")
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

			dektopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
			dektopdir = os.path.dirname(dektopfilename)
			base.ensuredir(dektopdir)

			base.debugmsg(5, "dektopfilename:", dektopfilename)
			with open(dektopfilename, 'w') as df:
				df.writelines(desktopdata)

			base.debugmsg(5, "Copy icons")
			# /usr/share/icons/hicolor/128x128/apps/
			# 	1024x1024  128x128  16x16  192x192  22x22  24x24  256x256  32x32  36x36  42x42  48x48  512x512  64x64  72x72  8x8  96x96
			# or
			#  ~/.local/share/icons/hicolor/256x256/apps/
			src_iconx128 = os.path.join(icon_dir, projname + "-128.png")
			base.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", projname + ".png")
			dst_icondir = os.path.dirname(dst_iconx128)
			base.ensuredir(dst_icondir)
			base.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

			src_iconx128 = os.path.join(icon_dir, "rfswarm-logo-128.png")
			base.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", "rfswarm-logo.png")
			base.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

		if platform.system() == 'Darwin':
			base.debugmsg(5, "Create folder structure in /Applications")

			src_iconx1024 = os.path.join(icon_dir, projname + "-1024.png")

			self.create_macos_app_bundle(appname, pipdata.version, manager_executable, src_iconx1024)

		if platform.system() == 'Windows':
			base.debugmsg(5, "Create Startmenu shorcuts")
			roam_appdata = os.environ["APPDATA"]
			scutpath = os.path.join(roam_appdata, "Microsoft", "Windows", "Start Menu", appname + ".lnk")
			# targetpath = "c:\\Users\\Dave\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\rfswarm.exe"
			# iconpath = "c:\\Users\\Dave\\AppData\\Local\\Programs\\Python\\Python311\\Lib\site-packages\\rfswarm_manager\\icons\\rfswarm-manager-128.ico"
			src_iconx128 = os.path.join(icon_dir, projname + "-128.ico")

			self.create_windows_shortcut(scutpath, manager_executable, src_iconx128, "Performance testing with robot test cases", True)

	def create_windows_shortcut(self, scutpath, targetpath, iconpath, desc, minimised=False):
		pslst = []

		directorydir = os.path.dirname(scutpath)
		base.ensuredir(directorydir)

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
		base.debugmsg(6, "psscript:", psscript)

		response = os.popen('powershell.exe -command ' + psscript).read()

		base.debugmsg(6, "response:", response)

	def create_macos_app_bundle(self, name, version, exesrc, icosrc):

		appspath = "~/Applications"
		if os.access("/Applications", os.W_OK):
			appspath = "/Applications"

		appspath = os.path.expanduser(appspath)

		# https://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

		apppath = os.path.join(appspath, name + ".app")
		MacOSFolder = os.path.join(apppath, "Contents", "MacOS")
		base.ensuredir(MacOSFolder)

		# need to create the icon file:
		# https://stackoverflow.com/questions/646671/how-do-i-set-the-icon-for-my-applications-mac-os-x-app-bundle
		namelst = name.split()
		base.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		base.debugmsg(6, "projname:", projname)
		signature = "RFS{0}".format(namelst[1].upper())
		base.debugmsg(6, "signature:", signature)

		ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
		iconset = os.path.join(ResourcesFolder, projname + ".iconset")
		icnsfile = os.path.join(ResourcesFolder, projname + ".icns")
		base.ensuredir(iconset)

		# Normal screen icons
		base.debugmsg(6, "Normal screen icons")
		for size in [16, 32, 64, 128, 256, 512]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{0}x{0}.png'".format(size, icosrc, iconset)
			base.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			base.debugmsg(6, "response:", response)

		# Retina display icons
		base.debugmsg(6, "Retina display icons")
		for size in [32, 64, 128, 256, 512, 1024]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{3}x{3}x2.png'".format(size, icosrc, iconset, int(size / 2))
			base.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			base.debugmsg(6, "response:", response)

		# Make a multi-resolution Icon
		base.debugmsg(6, "Make a multi-resolution Icon")
		cmd = "iconutil -c icns -o '{0}' '{1}'".format(icnsfile, iconset)
		base.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		base.debugmsg(6, "response:", response)

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
		base.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		base.debugmsg(6, "response:", response)

		# # Try re-registering your application with Launch Services:
		# # /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f /Applications/MyTool.app
		# lsregister = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
		# cmd = "{0} -f '{1}'".format(lsregister, apppath)
		# base.debugmsg(6, "cmd:", cmd)
		# response = os.popen(cmd).read()
		# base.debugmsg(6, "response:", response)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Messages
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def display_warning(self, message):
		if not base.args.nogui:
			base.debugmsg(0, message)
			base.gui.display_warning(message)
		else:
			base.debugmsg(0, message)
			self.on_closing(message)

	def display_info(self, message):
		if not base.args.nogui:
			base.debugmsg(0, message)
			base.gui.display_info(message)
		else:
			base.debugmsg(0, message)
			self.on_closing(message)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Server
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def run_agent_server(self):

		srvip = base.config['Server']['BindIP']
		srvport = int(base.config['Server']['BindPort'])
		if len(srvip) > 0:
			base.srvdisphost = srvip
			ip = ipaddress.ip_address(srvip)
			base.debugmsg(5, "ip.version:", ip.version)
			if ip.version == 6 and sys.version_info < (3, 8):
				base.debugmsg(0, "Python 3.8 or higher required to bind to IPv6 Addresses")
				pyver = "{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
				base.debugmsg(0, "Python Version:", pyver, "	IP Version:", ip.version, "	IP Address:", srvip)
				srvip = ''
				base.srvdisphost = socket.gethostname()
		else:
			base.srvdisphost = socket.gethostname()

		server_address = (srvip, srvport)
		try:
			base.agenthttpserver = ThreadingHTTPServer(server_address, AgentServer)
		except PermissionError:
			base.debugmsg(0, "Permission denied when trying :", server_address)
			self.on_closing()
			return False
		except Exception as e:
			base.debugmsg(5, "e:", e)
			self.on_closing()
			return False

		base.appstarted = True
		base.debugmsg(5, "appstarted:", base.appstarted)
		base.debugmsg(1, "Starting Agent Manager", "http://{}:{}/".format(base.srvdisphost, srvport))
		base.agenthttpserver.serve_forever()

	def register_agent(self, agentdata):
		base.debugmsg(7, "agentdata:", agentdata)
		agentname = agentdata["AgentName"]

		base.add_scriptfilter("Agent: {}".format(agentname))

		AssignedRobots = 0
		if agentname in base.Agents and "AssignedRobots" in base.Agents[agentname]:
			AssignedRobots = base.Agents[agentname]["AssignedRobots"]
		agentdata["AssignedRobots"] = AssignedRobots

		AssignedMRobots = 0
		if agentname in base.Agents and "AssignedMRobots" in base.Agents[agentname]:
			AssignedMRobots = base.Agents[agentname]["AssignedMRobots"]
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

		base.Agents[agentdata["AgentName"]] = agentdata

		base.debugmsg(9, "register_agent: agentdata:", agentdata)

		t = threading.Thread(target=self.UpdateAgents, name="UpdateAgents")
		t.start()

		# add filter options to the filter list
		if "Properties" in agentdata:
			filterexclude = ["RobotFramework: Libraries", "RFSwarmAgent: Version"]
			valexclude = [True, False, "", "True", "False"]
			for prop in agentdata["Properties"]:
				base.debugmsg(8, "prop:", prop)
				if prop not in filterexclude:
					t = threading.Thread(target=base.add_scriptfilter, args=(prop, ))
					t.start()
					if agentdata["Properties"][prop] not in valexclude:
						val = "{}: {}".format(prop, agentdata["Properties"][prop])
						t = threading.Thread(target=base.add_scriptfilter, args=(val, ))
						t.start()

			if "RFSwarmAgent: Version" in agentdata["Properties"]:
				prop = "RFSwarmAgent: Version: {}".format(agentdata["Properties"]["RFSwarmAgent: Version"])
				t = threading.Thread(target=base.add_scriptfilter, args=(prop, ))
				t.start()

		# save data to db

		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Status", agentdata["Status"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "LastSeen", agentdata["LastSeen"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "AssignedRobots", agentdata["AssignedRobots"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Robots", agentdata["Robots"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Monitor", agentdata["Monitor"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Load", agentdata["LOAD%"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "CPU", agentdata["CPU%"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "MEM", agentdata["MEM%"], agentdata["AgentName"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "NET", agentdata["NET%"], agentdata["AgentName"])
		# FileCount was added in v1.3.2
		if "FileCount" in agentdata:
			base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "FileCount", agentdata["FileCount"], agentdata["AgentName"])

		if "AgentIPs" in agentdata:
			for ip in agentdata["AgentIPs"]:
				base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "IPAddress", ip, agentdata["AgentName"])
		if "Properties" in agentdata:
			for prop in agentdata["Properties"]:
				base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], prop, agentdata["Properties"][prop], agentdata["AgentName"])

	def register_result(self, AgentName, result_name, result, elapsed_time, start_time, end_time, index, robot, iter, sequence):
		base.debugmsg(9, "register_result")
		resdata = (index, robot, iter, AgentName, sequence, result_name, result, elapsed_time, start_time, end_time)
		base.debugmsg(7, "resdata:", resdata)
		base.dbqueue["Results"].append(resdata)
		base.debugmsg(9, "dbqueue Results:", base.dbqueue["Results"])

		if not base.args.nogui:
			ut = threading.Thread(target=base.gui.delayed_UpdateRunStats)
			ut.start()

	def register_metric(self, PrimaryMetric, MetricType, MetricTime, SecondaryMetrics, DataSource):
		# core.register_metric(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"], jsonreq["AgentName"])
		base.debugmsg(7, "PrimaryMetric:", PrimaryMetric, "	MetricType:", MetricType, "	MetricTime:", MetricTime, "	SecondaryMetrics:", SecondaryMetrics, "	DataSource:", DataSource)

		# Save Metric Data

		for key in SecondaryMetrics:
			base.debugmsg(7, PrimaryMetric, MetricType, MetricTime, key, SecondaryMetrics[key], DataSource)
			base.save_metrics(PrimaryMetric, MetricType, MetricTime, key, SecondaryMetrics[key], DataSource)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Plan
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildCorePlan(self):
		base.debugmsg(5, "BuildCorePlan")

		base.debugmsg(6, "Plan:scenariofile: ", base.config['Plan']['ScenarioFile'])
		base.debugmsg(6, "ScenarioFile: ", len(base.config['Plan']['ScenarioFile']), base.config['Plan']['ScenarioFile'])
		if len(base.config['Plan']['ScenarioFile']) > 0:
			load_result = self.OpenFile(base.config['Plan']['ScenarioFile'])
			if not base.args.nogui and load_result == 1:
				base.gui.OpenINIGraphs()
		else:
			base.addScriptRow()

	def OpenFile(self, ScenarioFile):
		fileok = True

		base.debugmsg(6, "ScenarioFile: ", ScenarioFile)
		base.debugmsg(6, "base.config['Plan']['ScenarioFile']: ", base.config['Plan']['ScenarioFile'])
		base.config['Plan']['ScenarioDir'] = base.inisafedir(os.path.dirname(ScenarioFile))
		base.debugmsg(6, "base.config['Plan']['ScenarioDir']: ", base.config['Plan']['ScenarioDir'])

		base.debugmsg(6, "Config graph list: ")
		base.debugmsg(6, "base.config['GUI']['graph_list']: ", base.config['GUI']['graph_list'])
		iniglist = list(base.config['GUI']['graph_list'].split(","))
		base.debugmsg(9, "iniglist: ", iniglist)
		base.config['GUI']['graph_list'] = base.inisafevalue(",".join(set(iniglist)))
		base.debugmsg(6, "base.config['GUI']['graph_list']: ", base.config['GUI']['graph_list'])

		filedata = configparser.ConfigParser()
		base.debugmsg(6, "filedata: ", filedata._sections)

		if os.path.isfile(ScenarioFile):
			base.debugmsg(9, "ScenarioFile: ", ScenarioFile)
			try:
				arrfile = os.path.splitext(ScenarioFile)
				base.debugmsg(5, "arrfile: ", arrfile)
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
						base.debugmsg(5, "read yaml file")
						with open(ScenarioFile, 'r', encoding="utf-8") as f:
							filedict = yaml.safe_load(f)
						base.debugmsg(5, "filedict: ", filedict)
						filedict = base.configparser_safe_dict(filedict)
						base.debugmsg(5, "filedict: ", filedict)
					if arrfile[1].lower() == ".json":
						# read json file
						base.debugmsg(5, "read json file")
						with open(ScenarioFile, 'r', encoding="utf-8") as f:
							filedict = json.load(f)
						base.debugmsg(5, "filedict: ", filedict)
						filedict = base.configparser_safe_dict(filedict)
						base.debugmsg(5, "filedict: ", filedict)
					base.debugmsg(5, "filedict: ", filedict)
					filedata.read_dict(filedict)
				if base.config['Plan']['ScenarioFile'] != ScenarioFile:
					base.debugmsg(6, "ScenarioFile:", ScenarioFile)
					base.config['Plan']['ScenarioFile'] = base.inisafevalue(ScenarioFile)
					base.saveini()
			except Exception:
				base.config['Plan']['ScenarioFile'] = ""
		else:
			if len(ScenarioFile) > 1:
				# error file not exist
				msg = "Scenario file Not found:\n" + ScenarioFile
				self.display_warning(msg)
			return 1

		base.debugmsg(6, "filedata: ", filedata)

		scriptcount = 0
		monitorcount = 0
		graphlist = []
		if "Scenario" in filedata:
			base.debugmsg(6, "Scenario:", filedata["Scenario"])
			if "scriptcount" in filedata["Scenario"]:
				scriptcount = int(filedata["Scenario"]["scriptcount"])
				base.debugmsg(8, "scriptcount:", scriptcount)

			if "graphlist" in filedata["Scenario"]:
				graphlist = filedata["Scenario"]["graphlist"].split(",")

			if "uploadmode" in filedata["Scenario"]:
				base.uploadmode = filedata['Scenario']['uploadmode']

			if "monitortimebefore" in filedata["Scenario"]:
				base.mtimebefore = int(filedata['Scenario']['monitortimebefore'])
				base.debugmsg(5, "base.mtimebefore:", base.mtimebefore)
				self.msr_delayb4_validate("OpenFile", base.mtimebefore)

			if "monitortimeafter" in filedata["Scenario"]:
				base.mtimeafter = int(filedata['Scenario']['monitortimeafter'])
				base.debugmsg(5, "base.mtimeafter:", base.mtimeafter)
				self.msr_delayaft_validate("OpenFile", base.mtimeafter)

			if "monitorcount" in filedata["Scenario"]:
				monitorcount = int(filedata["Scenario"]["monitorcount"])
				base.debugmsg(5, "monitorcount:", monitorcount)

		else:
			base.debugmsg(1, "File contains no scenario:", ScenarioFile)
			base.config['Plan']['ScenarioFile'] = ""
			return 1

		if "Script Defaults" in filedata:
			base.scriptdefaults = filedata['Script Defaults']

		# Set base.config['Plan']['ScriptDir']
		base.debugmsg(5, "scriptcount:", scriptcount)
		filelst = []

		for i in range(scriptcount):
			istr = str(i + 1)
			base.debugmsg(5, "istr:", istr)
			if istr in filedata:
				base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				if "script" in filedata[istr]:
					base.debugmsg(5, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(base.config['Plan']['ScenarioDir'], scriptname)
						base.debugmsg(5, "combined:", combined)
						scriptname = os.path.abspath(combined)
					base.debugmsg(5, "scriptname:", scriptname)

					if scriptname not in filelst:
						filelst.append(scriptname)

		for i in range(monitorcount):
			istr = "m{}".format(i + 1)
			base.debugmsg(5, "istr:", istr)
			if istr in filedata:
				base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				if "script" in filedata[istr]:
					base.debugmsg(5, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(base.config['Plan']['ScenarioDir'], scriptname)
						base.debugmsg(5, "combined:", combined)
						scriptname = os.path.abspath(combined)
					base.debugmsg(5, "scriptname:", scriptname)

					if scriptname not in filelst:
						filelst.append(scriptname)

		if len(filelst) > 0:
			commonpath = os.path.commonpath(filelst)
			base.debugmsg(5, "commonpath: ", commonpath)
			base.config['Plan']['ScriptDir'] = base.inisafedir(commonpath)
			base.saveini()
		else:
			base.config['Plan']['ScriptDir'] = base.inisafedir(base.dir_path)
			base.debugmsg(5, "ScriptDir: ", base.config['Plan']['ScriptDir'])
			base.saveini()

		rowcount = 0
		for i in range(scriptcount):
			istr = str(i + 1)
			if istr in filedata:
				base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				rowcount += 1

				# if i not in base.scriptlist:
				# 	base.scriptlist.append({})
				# 	base.scriptlist[ii]["Index"] = ii
				if not base.args.nogui:
					if rowcount + 1 > base.gui.scriptgrid.grid_size()[1]:		# grid_size tupple: (cols, rows)
						base.addScriptRow()
				else:
					base.addScriptRow()

				# users = 13
				if "robots" in filedata[istr] or "users" in filedata[istr]:
					if "robots" in filedata[istr]:
						base.debugmsg(8, "filedata[", istr, "][robots]:", filedata[istr]["robots"])
						self.sr_users_validate(rowcount, int(filedata[istr]["robots"]))
					else:
						base.debugmsg(8, "filedata[", istr, "][users]:", filedata[istr]["users"])
						self.sr_users_validate(rowcount, int(filedata[istr]["users"]))
						# delay = 0
				else:
					base.debugmsg(3, "robots missing [", istr, "]")
					fileok = False
				if "delay" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][delay]:", filedata[istr]["delay"])
					self.sr_delay_validate(rowcount, int(filedata[istr]["delay"]))
					# rampup = 60
				else:
					base.debugmsg(3, "delay missing [", istr, "]")
					fileok = False
				if "rampup" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][rampup]:", filedata[istr]["rampup"])
					self.sr_rampup_validate(rowcount, int(filedata[istr]["rampup"]))
					# run = 600
				else:
					base.debugmsg(3, "rampup missing [", istr, "]")
					fileok = False
				if "run" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][run]:", filedata[istr]["run"])
					self.sr_run_validate(rowcount, int(filedata[istr]["run"]))
					# script = /Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot
				else:
					base.debugmsg(3, "run missing [", istr, "]")
					fileok = False
				if "script" in filedata[istr]:
					base.debugmsg(7, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)

					base.debugmsg(7, "scriptname:", scriptname)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(base.config['Plan']['ScenarioDir'], scriptname)
						base.debugmsg(7, "combined:", combined)
						scriptname = os.path.abspath(combined)
					base.debugmsg(7, "scriptname:", scriptname)
					self.sr_file_validate(rowcount, scriptname)
				else:
					base.debugmsg(3, "script missing [", istr, "]")
					fileok = False
				if "test" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][test]:", filedata[istr]["test"])
					self.sr_test_validate("row{}".format(rowcount), filedata[istr]["test"])
				else:
					base.debugmsg(3, "test missing [", istr, "]")
					fileok = False

				if "resultnamemode" in filedata[istr]:
					base.debugmsg(8, "resultnamemode:", filedata[istr]["resultnamemode"])
					base.scriptlist[rowcount]["resultnamemode"] = filedata[istr]["resultnamemode"]

				if "excludelibraries" in filedata[istr]:
					base.debugmsg(8, "excludelibraries:", filedata[istr]["excludelibraries"])
					base.scriptlist[rowcount]["excludelibraries"] = filedata[istr]["excludelibraries"]

				if "robotoptions" in filedata[istr]:
					base.debugmsg(8, "robotoptions:", filedata[istr]["robotoptions"])
					base.scriptlist[rowcount]["robotoptions"] = filedata[istr]["robotoptions"]

				# testrepeater = True
				if "testrepeater" in filedata[istr]:
					base.scriptlist[rowcount]["testrepeater"] = base.str2bool(filedata[istr]["testrepeater"])
				# injectsleepenabled = True
				if "injectsleepenabled" in filedata[istr]:
					base.scriptlist[rowcount]["injectsleepenabled"] = base.str2bool(filedata[istr]["injectsleepenabled"])
				# injectsleepminimum = 18
				if "injectsleepminimum" in filedata[istr] and len(filedata[istr]["injectsleepminimum"]) > 0:
					base.scriptlist[rowcount]["injectsleepminimum"] = int(filedata[istr]["injectsleepminimum"])
				# injectsleepmaximum = 33
				if "injectsleepmaximum" in filedata[istr] and len(filedata[istr]["injectsleepmaximum"]) > 0:
					base.scriptlist[rowcount]["injectsleepmaximum"] = int(filedata[istr]["injectsleepmaximum"])
				# disableloglog
				if "disableloglog" in filedata[istr]:
					base.scriptlist[rowcount]["disableloglog"] = base.str2bool(filedata[istr]["disableloglog"])
				# disablelogreport
				if "disablelogreport" in filedata[istr]:
					base.scriptlist[rowcount]["disablelogreport"] = base.str2bool(filedata[istr]["disablelogreport"])
				# disablelogoutput
				if "disablelogoutput" in filedata[istr]:
					base.scriptlist[rowcount]["disablelogoutput"] = base.str2bool(filedata[istr]["disablelogoutput"])

				if "filters" in filedata[istr]:
					base.debugmsg(9, "filedata[istr][filters]:", filedata[istr]["filters"], type(filedata[istr]["filters"]))
					filtr = filedata[istr]["filters"].replace("'", '"')
					base.debugmsg(9, "filtr:", filtr, type(filtr))
					filtrs = json.loads(filtr)
					base.debugmsg(9, "filtrs:", filtrs, type(filtrs))
					base.scriptlist[rowcount]["filters"] = filtrs

				if not fileok:
					base.debugmsg(1, "Scenario file is damaged:", ScenarioFile)
					return 1

		rowcount = 0
		for i in range(monitorcount):
			istr = "m{}".format(i + 1)
			if istr in filedata:
				base.debugmsg(5, "filedata[", istr, "]:", filedata[istr])
				rowcount += 1

				# if i not in base.scriptlist:
				# 	base.scriptlist.append({})
				# 	base.scriptlist[ii]["Index"] = ii
				# if not base.args.nogui:
				# 	if rowcount + 1 > base.gui.scriptgrid.grid_size()[1]:		# grid_size tupple: (cols, rows)
				# 		base.addMScriptRow()
				# else:
				base.addMScriptRow()

				# users = 13
				# if "robots" in filedata[istr] or "users" in filedata[istr]:
				# 	if "robots" in filedata[istr]:
				# 		base.debugmsg(8, "filedata[", istr, "][robots]:", filedata[istr]["robots"])
				# 		self.msr_users_validate(rowcount, int(filedata[istr]["robots"]))
				# 	else:
				# 		base.debugmsg(8, "filedata[", istr, "][users]:", filedata[istr]["users"])
				# 		self.msr_users_validate(rowcount, int(filedata[istr]["users"]))
				# 		# delay = 0
				# else:
				# 	base.debugmsg(3, "robots missing [", istr, "]")
				# 	fileok = False
				# if "delay" in filedata[istr]:
				# 	base.debugmsg(8, "filedata[", istr, "][delay]:", filedata[istr]["delay"])
				# 	self.msr_delay_validate(rowcount, int(filedata[istr]["delay"]))
				# 	# rampup = 60
				# else:
				# 	base.debugmsg(3, "delay missing [", istr, "]")
				# 	fileok = False
				# if "rampup" in filedata[istr]:
				# 	base.debugmsg(8, "filedata[", istr, "][rampup]:", filedata[istr]["rampup"])
				# 	self.msr_rampup_validate(rowcount, int(filedata[istr]["rampup"]))
				# 	# run = 600
				# else:
				# 	base.debugmsg(3, "rampup missing [", istr, "]")
				# 	fileok = False
				# if "run" in filedata[istr]:
				# 	base.debugmsg(8, "filedata[", istr, "][run]:", filedata[istr]["run"])
				# 	self.msr_run_validate(rowcount, int(filedata[istr]["run"]))
				# 	# script = /Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot
				# else:
				# 	base.debugmsg(3, "run missing [", istr, "]")
				# 	fileok = False

				if "script" in filedata[istr]:
					base.debugmsg(5, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if '\\' in scriptname:
						scriptnamearr = scriptname.split('\\')
						scriptname = "/".join(scriptnamearr)

					base.debugmsg(5, "scriptname:", scriptname)
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(base.config['Plan']['ScenarioDir'], scriptname)
						base.debugmsg(7, "combined:", combined)
						scriptname = os.path.abspath(combined)
					base.debugmsg(7, "scriptname:", scriptname)
					self.msr_file_validate(rowcount, scriptname)
				else:
					base.debugmsg(3, "script missing [", istr, "]")
					fileok = False
				if "test" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][test]:", filedata[istr]["test"])
					self.msr_test_validate("mrow{}".format(rowcount), filedata[istr]["test"])
				else:
					base.debugmsg(3, "test missing [", istr, "]")
					fileok = False

				if "resultnamemode" in filedata[istr]:
					base.debugmsg(8, "resultnamemode:", filedata[istr]["resultnamemode"])
					base.mscriptlist[rowcount]["resultnamemode"] = filedata[istr]["resultnamemode"]

				if "excludelibraries" in filedata[istr]:
					base.debugmsg(8, "excludelibraries:", filedata[istr]["excludelibraries"])
					base.mscriptlist[rowcount]["excludelibraries"] = filedata[istr]["excludelibraries"]

				if "robotoptions" in filedata[istr]:
					base.debugmsg(8, "robotoptions:", filedata[istr]["robotoptions"])
					base.mscriptlist[rowcount]["robotoptions"] = filedata[istr]["robotoptions"]

				# testrepeater = True
				if "testrepeater" in filedata[istr]:
					base.mscriptlist[rowcount]["testrepeater"] = base.str2bool(filedata[istr]["testrepeater"])
				# injectsleepenabled = True
				if "injectsleepenabled" in filedata[istr]:
					base.mscriptlist[rowcount]["injectsleepenabled"] = base.str2bool(filedata[istr]["injectsleepenabled"])
				# injectsleepminimum = 18
				if "injectsleepminimum" in filedata[istr] and len(filedata[istr]["injectsleepminimum"]) > 0:
					base.mscriptlist[rowcount]["injectsleepminimum"] = int(filedata[istr]["injectsleepminimum"])
				# injectsleepmaximum = 33
				if "injectsleepmaximum" in filedata[istr] and len(filedata[istr]["injectsleepmaximum"]) > 0:
					base.mscriptlist[rowcount]["injectsleepmaximum"] = int(filedata[istr]["injectsleepmaximum"])
				# disableloglog
				if "disableloglog" in filedata[istr]:
					base.mscriptlist[rowcount]["disableloglog"] = base.str2bool(filedata[istr]["disableloglog"])
				# disablelogreport
				if "disablelogreport" in filedata[istr]:
					base.mscriptlist[rowcount]["disablelogreport"] = base.str2bool(filedata[istr]["disablelogreport"])
				# disablelogoutput
				if "disablelogoutput" in filedata[istr]:
					base.mscriptlist[rowcount]["disablelogoutput"] = base.str2bool(filedata[istr]["disablelogoutput"])

				if "filters" in filedata[istr]:
					base.debugmsg(9, "filedata[istr][filters]:", filedata[istr]["filters"], type(filedata[istr]["filters"]))
					filtr = filedata[istr]["filters"].replace("'", '"')
					base.debugmsg(9, "filtr:", filtr, type(filtr))
					filtrs = json.loads(filtr)
					base.debugmsg(9, "filtrs:", filtrs, type(filtrs))
					base.mscriptlist[rowcount]["filters"] = filtrs

				if not fileok:
					base.debugmsg(1, "Scenario file is damaged:", ScenarioFile)
					return 1

		base.debugmsg(9, "config graph_list: ", base.config['GUI']['graph_list'])

		base.debugmsg(9, "graphlist: ", graphlist)
		base.debugmsg(9, "iniglist: ", iniglist)
		base.config['GUI']['graph_list'] = base.inisafevalue(",".join(set(iniglist + graphlist)))

		base.debugmsg(9, "config graph_list: ", base.config['GUI']['graph_list'])

		if not base.args.nogui:
			base.gui.ClearScenarioGraphs()

		for iniid in graphlist:
			if iniid in filedata:
				base.debugmsg(5, "iniid: ", iniid, " 	filedata[iniid]:", filedata[iniid])
				base.config[iniid] = base.inisafevalue(filedata[iniid])
				if not base.args.nogui:
					base.gui.AddScenarioGraph(filedata[iniid]["name"], iniid)

		if not base.args.nogui:
			base.gui.OpenINIGraphs()
			time.sleep(0.250)

			base.debugmsg(5, "Call base.gui.pln_update_graph")
			base.gui.pln_graph_update = False
			t = threading.Thread(target=base.gui.pln_update_graph)
			t.start()

		return 0

	def ClickPlay(self, _event=None):

		base.debugmsg(0, "Test Started:	", int(time.time()), "[", datetime.now().isoformat(sep=' ', timespec='seconds'), "]")

		# before we start any robots we need to make sure the assigned robot counts are zero
		for nxtagent in base.Agents.keys():
			base.Agents[nxtagent]["AssignedRobots"] = 0
			base.Agents[nxtagent]["AssignedMRobots"] = 0

		base.run_abort = False
		base.run_start = 0
		base.run_end = 0
		base.plan_end = 0
		base.mon_end = 0
		base.run_finish = 0
		base.posttest = False
		base.run_paused = False
		base.MetricIDs = {}

		base.robot_schedule = base.robot_schedule_template

		warnings = self.Pre_Run_Checks()
		if len(warnings) > 0:
			# report warnings and stop test from running
			base.run_abort = False
			base.run_end = int(time.time()) - 1
			base.plan_end = int(time.time()) - 1
			base.mon_end = int(time.time()) - 1
			base.run_finish = int(time.time()) - 1

			for warning in warnings:
				base.debugmsg(0, warning)

			return 0

		sec2st = base.run_starttime - int(time.time())
		if sec2st < 1:
			mstarttime = int(time.time())
			mendtime = base.mon_end - mstarttime
			starttime = mstarttime + base.mtimebefore
			datafiletime = datetime.now().strftime("%Y%m%d_%H%M%S")
			if len(base.config['Plan']['ScenarioFile']) > 0:
				filename = os.path.basename(base.config['Plan']['ScenarioFile'])
				sname = os.path.splitext(filename)[0]
				base.run_name = "{}_{}".format(datafiletime, sname)
			else:
				base.run_name = "{}_{}".format(datafiletime, "Scenario")
			base.debugmsg(5, "base.run_name:", base.run_name)

			# give some time (10ms) to create the db before starting monitoring
			time.sleep(1)
			base.debugmsg(5, "core.run_start_threads")
			t = threading.Thread(target=core.run_start_threads)
			t.start()
			if not base.args.nogui:
				time.sleep(0.1)
				base.debugmsg(5, "base.gui.delayed_UpdateRunStats")
				ut = threading.Thread(target=base.gui.delayed_UpdateRunStats)
				ut.start()
				base.debugmsg(9, "base.gui.tabs.tabs()", base.gui.tabs.tabs())
				base.debugmsg(8, "base.gui.tabids", base.gui.tabids)
				base.debugmsg(7, "base.gui.tabids['Run']", base.gui.tabids['Run'])
				# self.tabids['Run']
				# base.gui.tabs.select(2)
				base.gui.tabs.select(base.gui.tabids['Run'])

			# wait till db has been opened
			while base.run_name != base.run_name_current:
				time.sleep(0.1)
			while not base.dbready:
				time.sleep(0.1)

			# base.save_metrics(base.run_name, "Scenario", int(time.time()), "starttime", base.run_starttime, base.srvdisphost)
			base.save_metrics(base.run_name, "Scenario", starttime, "Start", starttime, base.srvdisphost)
			base.save_metrics("Time", "Scenario", starttime, "Start", starttime, base.srvdisphost)

			base.save_metrics("Manager", "rfswarm", starttime, "Version", base.version, base.srvdisphost)

			# collect list of test cases and robot files
			# --- save_metrics(self, PMetricName, MetricType, MetricTime, SMetricName, MetricValue):
			for grp in base.scriptlist:
				base.debugmsg(5, "grp", grp)
				if "Test" in grp.keys() and len(grp["Test"]) > 0:
					base.debugmsg(5, "grp[Index]", grp['Index'])
					base.save_metrics("Local_Path_{}".format(grp['Index']), "Scenario", starttime, grp['Script'], grp['Test'], base.srvdisphost)

					relpath = base.get_relative_path(base.config['Plan']['ScenarioFile'], grp['Script'])
					base.save_metrics("Test_{}".format(grp['Index']), "Scenario", starttime, relpath, grp['Test'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Test", starttime, relpath, grp['Test'], base.srvdisphost)

					base.save_metrics("Robots_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['Robots'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Robots", starttime, grp['Test'], grp['Robots'], base.srvdisphost)

					base.save_metrics("Delay_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['Delay'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Delay", starttime, grp['Test'], grp['Delay'], base.srvdisphost)

					base.save_metrics("Ramp_Up_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['RampUp'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Ramp_Up", starttime, grp['Test'], grp['RampUp'], base.srvdisphost)

					base.save_metrics("Run_{}".format(grp['Index']), "Scenario", starttime, grp['Test'], grp['Run'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Run", starttime, grp['Test'], grp['Run'], base.srvdisphost)

			for grp in base.mscriptlist:
				base.debugmsg(5, "grp", grp)
				if "Test" in grp.keys() and len(grp["Test"]) > 0:
					base.debugmsg(5, "grp[Index]", grp['Index'])
					base.save_metrics("Local_Path_{}".format(grp['Index']), "Scenario", mstarttime, grp['Script'], grp['Test'], base.srvdisphost)

					relpath = base.get_relative_path(base.config['Plan']['ScenarioFile'], grp['Script'])
					base.save_metrics("Test_{}".format(grp['Index']), "Scenario", mstarttime, relpath, grp['Test'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Test", mstarttime, relpath, grp['Test'], base.srvdisphost)

					base.save_metrics("Robots_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], grp['Robots'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Robots", mstarttime, grp['Test'], grp['Robots'], base.srvdisphost)

					base.save_metrics("Delay_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], grp['Delay'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Delay", mstarttime, grp['Test'], grp['Delay'], base.srvdisphost)

					base.save_metrics("Ramp_Up_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], grp['RampUp'], base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Ramp_Up", mstarttime, grp['Test'], grp['RampUp'], base.srvdisphost)

					base.save_metrics("Run_{}".format(grp['Index']), "Scenario", mstarttime, grp['Test'], mendtime, base.srvdisphost)
					base.save_metrics(grp['Index'], "Scenario_Run", mstarttime, grp['Test'], mendtime, base.srvdisphost)

	def Pre_Run_Checks(self, _event=None):
		warnings = []

		# good
		# grp {'Index': 1, 'Robots': 2, 'Delay': 0, 'RampUp': 45, 'Run': 60, 'Test': 'RFSwarm Demo Test', 'TestVar': <tkinter.StringVar object at 0x7f6a4b911ea0>, 'Script': '/home/dave/Documents/Github/rfswarm/Tests/Demo/rfswarm_demo.robot', 'ScriptHash': '03ad3be39fcfd8f37dfe1db445192728'}
		# bad
		# grp {'Index': 1, 'Robots': 10, 'Delay': 0, 'RampUp': 1800, 'Run': 7200, 'Test': '', 'TestVar': <tkinter.StringVar object at 0x7f7fe07dfe50>}

		base.debugmsg(5, "scriptlist:", base.scriptlist)
		for grp in base.scriptlist:
			base.debugmsg(5, "grp", grp)
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

				grp_plan_end = int(time.time()) + base.mtimebefore + grp['Delay'] + grp["RampUp"] + grp['Run'] + grp["RampUp"]
				# mtimebefore = 0
				# mtimeafter = 0
				if grp_plan_end > base.plan_end:
					base.plan_end = grp_plan_end
					base.debugmsg(5, "base.plan_end:", base.plan_end)
					base.mon_end = base.plan_end + base.mtimeafter

		base.debugmsg(5, "mscriptlist:", base.mscriptlist)
		for grp in base.mscriptlist:
			base.debugmsg(5, "grp", grp)
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
		base.debugmsg(5, "RFSwarmCore: BuildCoreMonitoring")

	def msr_delayb4_validate(self, *args):
		base.debugmsg(5, "args", args)
		if not base.args.nogui:
			base.gui.msr_delayb4_validate(*args)
		return True

	def msr_delayaft_validate(self, *args):
		base.debugmsg(5, "args", args)
		if not base.args.nogui:
			base.gui.msr_delayaft_validate(*args)
		return True

	def msr_file_validate(self, r, *args):
		base.debugmsg(5, "r:", r, "	args:", args)
		if args:
			scriptfile = args[0]
		else:
			scriptfile = ""

		if not os.path.exists(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\ncannot be found by RFSwarm Manager."
			if not base.args.nogui:
				self.display_warning(msg)
			else:
				base.debugmsg(0, msg)
			return False
		elif not os.path.isfile(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\nis a directory, not a file."
			if not base.args.nogui:
				self.display_warning(msg)
			else:
				base.debugmsg(0, msg)
			return False

		base.debugmsg(5, "scriptfile:", scriptfile)
		if len(scriptfile) > 0:
			base.mscriptlist[r]["Script"] = scriptfile
			relpath = base.get_relative_path(base.config['Plan']['ScriptDir'], scriptfile)
			script_hash = base.hash_file(scriptfile, relpath)
			base.mscriptlist[r]["ScriptHash"] = script_hash

			if script_hash not in base.scriptfiles:
				base.scriptfiles[script_hash] = {
					"id": script_hash,
					"localpath": scriptfile,
					"relpath": relpath,
					"type": "script"
				}

				t = threading.Thread(target=base.find_dependancies, args=(script_hash, ))
				t.start()

		else:
			if "ScriptHash" in base.mscriptlist[r]:
				oldhash = base.mscriptlist[r]["ScriptHash"]
				t = threading.Thread(target=base.remove_hash, args=(oldhash, ))
				t.start()

			base.mscriptlist[r]["Script"] = ''
			base.mscriptlist[r]["ScriptHash"] = ''

		self.plan_scnro_chngd = True
		if not base.args.nogui:
			base.gui.msr_file_validate(r, *args)
		return True

	def msr_test_validate(self, *args):
		base.debugmsg(5, "args:", args)
		# r = int(args[0][-1:])+1
		r = int(args[0][4:])
		base.debugmsg(5, "r:", r)

		v = None
		if len(args) > 1 and len(args[1]) > 1:
			v = args[1]
			base.debugmsg(5, "v:", v)
			base.mscriptlist[r]["Test"] = v

		base.debugmsg(5, "mscriptlist[r]:", base.mscriptlist[r])

		if not base.args.nogui:
			base.gui.msr_test_validate(*args)
		return True

	def update_monitoring_jobs_mon_end(self, *args):
		base.debugmsg(5, "args:", args)
		for agnt in base.robot_schedule["Agents"].keys():
			for grurid in base.robot_schedule["Agents"][agnt].keys():
				base.debugmsg(5, "grurid:", grurid)
				if grurid[0] == "m":
					base.debugmsg(5, "grurid:", grurid, "New EndTime", base.mon_end)
					base.robot_schedule["Agents"][agnt][grurid]["EndTime"] = base.mon_end

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Run
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildCoreRun(self):
		base.debugmsg(5, "RFSwarmCore: BuildCoreRun")

	def ClickStop(self, _event=None):

		if base.run_end < int(time.time()):
			# abort run?
			base.run_abort = True
			base.debugmsg(5, "base.run_abort:", base.run_abort)
		else:
			base.run_end = int(time.time())  # time now
			base.debugmsg(0, "Run Stopped:", base.run_end, "[", datetime.now().isoformat(sep=' ', timespec='seconds'), "]")
			base.robot_schedule["End"] = base.run_end

			for agnt in base.robot_schedule["Agents"].keys():
				for grurid in base.robot_schedule["Agents"][agnt].keys():
					base.robot_schedule["Agents"][agnt][grurid]["EndTime"] = base.run_end
			base.mon_end = base.run_end

	def run_start_threads(self):

		if base.run_end > 0 and int(time.time()) > base.run_end:
			base.run_paused = True

		totrbts = 0
		currbts = 0

		# Start Monitoring robots
		base.debugmsg(5, "base.mscriptlist:", base.mscriptlist)
		for grp in base.mscriptlist:
			if "Test" in grp.keys() and len(grp["Test"]) > 0:
				base.debugmsg(5, "grp:", grp)
				nxtagent = None
				agentwarn = False
				while nxtagent is None:
					if 'filters' in grp:
						nxtagent = base.get_next_agent(grp['filters'])
						base.debugmsg(7, '(filters) next_agent:', nxtagent)
					else:
						nxtagent = base.get_next_agent([])
						base.debugmsg(9, '(filters else) next_agent:', nxtagent)
					base.debugmsg(5, '(Monitoring) next_agent:', nxtagent)
					if nxtagent is None:
						base.debugmsg(7, 'next_agent is None !!!')
						agentwarn = True
						if not base.args.nogui and not base.run_paused:
							base.debugmsg(7, 'base.args.nogui:', base.args.nogui, "base.run_paused:", base.run_paused)
							self.display_warning("Not enough Agents available to run Monitoring Robots!\n\nTest run is paused, please add agents to continue or click stop to abort.")
							base.debugmsg(7, 'base.args.nogui:', base.args.nogui, "base.run_paused:", base.run_paused)

						base.debugmsg(5, 'Not enough Agents available to run Robots! (Monitoring)')
						base.debugmsg(0, 'Not enough Agents available to run Monitoring Robots!')
						time.sleep(10)
					elif agentwarn:
						agentwarn = False
						if not base.args.nogui:
							self.display_info("Enough Agents available to run Monitoring Robots, test will now resume.")
						base.debugmsg(0, 'Enough Agents available to run Monitoring Robots, resuming.')
				# now we have agent for monitoring rorbot assign robobt

				if base.run_start < 1:
					base.run_start = int(time.time())  # time now
					base.robot_schedule = base.robot_schedule_template
					base.robot_schedule["RunName"] = base.run_name
					base.robot_schedule["Agents"] = {}
					base.robot_schedule["Scripts"] = {}
					base.robot_schedule["Start"] = base.run_start

					if not base.args.nogui:
						stm = time.localtime(base.robot_schedule["Start"])
						base.gui.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))

				gid = grp["Index"]
				base.debugmsg(5, "gid", gid, " 	robot_schedule[Scripts].keys()", base.robot_schedule["Scripts"].keys())
				if gid not in base.robot_schedule["Scripts"].keys():
					base.robot_schedule["Scripts"][gid] = {}

				nxtuid = 1
				uid = nxtuid
				grurid = "{}_{}_{}".format(gid, uid, int(time.time()))
				base.debugmsg(9, 'uid', uid)
				base.robot_schedule["Scripts"][gid][uid] = grurid

				if nxtagent not in base.robot_schedule["Agents"].keys():
					base.robot_schedule["Agents"][nxtagent] = {}

				base.robot_schedule["Agents"][nxtagent][grurid] = {
					"ScriptHash": grp["ScriptHash"],
					"Test": grp["Test"],
					"StartTime": int(time.time()),
					"EndTime": base.mon_end,
					"id": grurid
				}

				if "resultnamemode" in grp:
					base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = grp["resultnamemode"]
				else:
					if "resultnamemode" in base.scriptdefaults:
						base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = base.scriptdefaults["resultnamemode"]
					else:
						base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = base.resultnamemodedefault

				if "excludelibraries" in grp:
					base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = grp["excludelibraries"]
				else:
					if "excludelibraries" in base.scriptdefaults:
						base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = base.scriptdefaults["excludelibraries"]
					else:
						base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = base.excludelibrariesdefault

				if "robotoptions" in grp:
					base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = grp["robotoptions"]
				else:
					if "robotoptions" in base.scriptdefaults:
						base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = base.scriptdefaults["robotoptions"]

				tr = base.testrepeaterdefault
				if "testrepeater" in base.scriptdefaults:
					tr = base.scriptdefaults["testrepeater"]
				if "testrepeater" in grp:
					tr = grp["testrepeater"]
				base.robot_schedule["Agents"][nxtagent][grurid]["testrepeater"] = str(tr)

				# injectsleepenableddefault = False
				ise = base.injectsleepenableddefault
				if "injectsleepenabled" in base.scriptdefaults:
					ise = base.scriptdefaults["injectsleepenabled"]
				if "injectsleepenabled" in grp:
					ise = grp["injectsleepenabled"]
				base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepenabled"] = str(ise)
				if base.str2bool(ise):
					# injectsleepminimumdefault = 15
					ismn = base.injectsleepminimumdefault
					if "injectsleepminimum" in base.scriptdefaults:
						ismn = base.scriptdefaults["injectsleepminimum"]
					if "injectsleepminimum" in grp:
						ismn = grp["injectsleepminimum"]
					base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepminimum"] = str(ismn)
					# injectsleepmaximumdefault = 45
					ismx = base.injectsleepmaximumdefault
					if "injectsleepmaximum" in base.scriptdefaults:
						ismx = base.scriptdefaults["injectsleepmaximum"]
					if "injectsleepmaximum" in grp:
						ismx = grp["injectsleepmaximum"]
					base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepmaximum"] = str(ismx)

				# disableloglogdefault = False
				dll = base.disableloglogdefault
				if "disableloglog" in base.scriptdefaults:
					dll = base.scriptdefaults["disableloglog"]
				if "disableloglog" in grp:
					dll = grp["disableloglog"]
				base.robot_schedule["Agents"][nxtagent][grurid]["disableloglog"] = str(dll)
				# disablelogreportdefault = False
				dlr = base.disablelogreportdefault
				if "disablelogreport" in base.scriptdefaults:
					dlr = base.scriptdefaults["disablelogreport"]
				if "disablelogreport" in grp:
					dlr = grp["disablelogreport"]
				base.robot_schedule["Agents"][nxtagent][grurid]["disablelogreport"] = str(dlr)
				# disablelogoutputdefault = False
				dlo = base.disablelogoutputdefault
				if "disablelogoutput" in base.scriptdefaults:
					dlo = base.scriptdefaults["disablelogoutput"]
				if "disablelogoutput" in grp:
					dlo = grp["disablelogoutput"]
				base.robot_schedule["Agents"][nxtagent][grurid]["disablelogoutput"] = str(dlo)

				base.Agents[nxtagent]["AssignedMRobots"] += 1
				base.debugmsg(5, "base.Agents[", nxtagent, "][AssignedMRobots]:", base.Agents[nxtagent]["AssignedMRobots"])

				# currbts += 1
				# base.debugmsg(2, "Robot:", currbts, "	Test:", grp["Test"], "	Assigned to:", nxtagent)
				base.debugmsg(2, "Monitoring Robot:", " Test:", grp["Test"], "	Assigned to:", nxtagent)

				# base.debugmsg(9, "robot_schedule", base.robot_schedule)

		# Start Plan robots
		base.debugmsg(8, "base.scriptlist:", base.scriptlist)
		for grp in base.scriptlist:
			if "Robots" in grp:
				base.debugmsg(9, "run_start_threads: totrbts", totrbts, " 	grp:", grp)
				totrbts += int(grp["Robots"])
				base.debugmsg(8, "run_start_threads: totrbts", totrbts)

		base.debugmsg(8, 'currbts:', currbts, "	totrbts:", totrbts, "	run_paused:", base.run_paused)
		while currbts < totrbts:
			base.debugmsg(6, "while totrbts", totrbts, " 	currbts:", currbts)
			# totrbts = 0

			if "Start" not in base.robot_schedule:
				base.robot_schedule["Start"] = 0

			if base.run_end > 0 and int(time.time()) > base.run_end:
				break

			if base.run_paused and int(time.time()) < base.run_end:
				nxtagent = base.get_next_agent([])
				base.debugmsg(6, '(if) next_agent:', nxtagent)
				if nxtagent is None:
					base.run_paused = True
					base.debugmsg(5, 'Not enough Agents available to run Robots! (if)')
					base.debugmsg(3, 'Not enough Agents available to run Robots!')
					time.sleep(10)
				else:
					base.run_paused = False
					if not base.args.nogui:
						self.display_info("Enough Agents available to run Robots, test will now resume.")
					base.debugmsg(0, 'Enough Agents available to run Robots, resuming.')
			else:
				for grp in base.scriptlist:
					base.debugmsg(9, "grp", grp)
					if "Test" in grp.keys() and len(grp["Test"]) > 0:
						base.debugmsg(6, "while totrbts", totrbts, " 	currbts:", currbts)
						base.debugmsg(9, "grp[Index]", grp['Index'])

						if 'filters' in grp:
							nxtagent = base.get_next_agent(grp['filters'])
							base.debugmsg(7, '(filters) next_agent:', nxtagent)
						else:
							nxtagent = base.get_next_agent([])
							base.debugmsg(9, '(filters else) next_agent:', nxtagent)
						base.debugmsg(7, '(else) next_agent:', nxtagent)

						if nxtagent is None:
							base.debugmsg(7, 'next_agent is None !!!')
							if not base.args.nogui and not base.run_paused:
								base.debugmsg(7, 'base.args.nogui:', base.args.nogui, "base.run_paused:", base.run_paused)
								self.display_warning("Not enough Agents available to run Robots!\n\nTest run is paused, please add agents to continue or click stop to abort.")
								base.debugmsg(7, 'base.args.nogui:', base.args.nogui, "base.run_paused:", base.run_paused)
							base.run_paused = True

							base.debugmsg(5, 'Not enough Agents available to run Robots! (else)')
							base.debugmsg(0, 'Not enough Agents available to run Robots!')
							time.sleep(10)
							break
						else:
							colour = base.line_colour(grp["Index"])
							base.debugmsg(9, "Line colour", colour)

							if base.run_start < 1:
								base.run_start = int(time.time())  # time now
								base.robot_schedule = base.robot_schedule_template
								base.robot_schedule["RunName"] = base.run_name
								base.robot_schedule["Agents"] = {}
								base.robot_schedule["Scripts"] = {}
								base.robot_schedule["Start"] = base.run_start

								if not base.args.nogui:
									stm = time.localtime(base.robot_schedule["Start"])
									base.gui.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))

								base.run_end = base.run_start + base.mtimebefore + grp["Delay"] + grp["RampUp"] + grp["Run"]
								base.debugmsg(9, grp['Index'], " 	run_start:", base.run_start, " 	Delay:", grp["Delay"], " 	RampUp:", grp["RampUp"], " 	Run:", grp["Run"], " 	run_end:", base.run_end)
								base.robot_schedule["End"] = base.run_end

								# totrbts = 0

							gid = grp["Index"]
							base.debugmsg(9, "gid", gid, " 	robot_schedule[Scripts].keys()", base.robot_schedule["Scripts"].keys())
							if gid not in base.robot_schedule["Scripts"].keys():
								base.robot_schedule["Scripts"][gid] = {}
								base.debugmsg(9, "totrbts", totrbts)
								# totrbts += int(grp["Robots"])
								base.debugmsg(9, "totrbts", totrbts)

							if gid not in base.scriptgrpend.keys() or base.scriptgrpend[gid] < base.run_start:
								base.scriptgrpend[gid] = base.run_start + base.mtimebefore + grp["Delay"] + grp["RampUp"] + grp["Run"]
								base.debugmsg(9, "gid:", gid, " 	run_start:", base.run_start, "	base.mtimebefore:", base.mtimebefore, " 	Delay:", grp["Delay"], " 	RampUp:", grp["RampUp"], " 	Run:", grp["Run"], " 	run_end:", base.run_end)
								if base.scriptgrpend[gid] > base.run_end:
									base.run_end = base.scriptgrpend[gid]

							time_elapsed = int(time.time()) - base.run_start
							base.debugmsg(9, 'time_elapsed', time_elapsed, " Monitoring Delay", base.mtimebefore, " Delay", grp["Delay"])
							if time_elapsed > (base.mtimebefore + grp["Delay"]) - 1:
								uid = 0
								nxtuid = len(base.robot_schedule["Scripts"][gid]) + 1
								base.debugmsg(9, 'nxtuid', nxtuid)
								# Determine if we should start another user?
								if nxtuid < grp["Robots"] + 1:
									if grp["RampUp"] > 0:
										rupct = (time_elapsed - (base.mtimebefore + grp["Delay"])) / grp["RampUp"]
										# base.mtimebefore
										# rupct - Ramp-up percent
									else:
										rupct = 1
									base.debugmsg(9, 'rupct', rupct)
									# ruusr - Ramp-up user
									ruusr = int(grp["Robots"] * rupct) + 1
									base.debugmsg(9, 'nxtuid', nxtuid, 'ruusr', ruusr)
									if nxtuid < ruusr + 1:
										uid = nxtuid
										grurid = "{}_{}_{}".format(gid, uid, int(time.time()))
										base.debugmsg(9, 'uid', uid)
										base.robot_schedule["Scripts"][gid][uid] = grurid

										if nxtagent not in base.robot_schedule["Agents"].keys():
											base.robot_schedule["Agents"][nxtagent] = {}

										base.robot_schedule["Agents"][nxtagent][grurid] = {
											"ScriptHash": grp["ScriptHash"],
											"Test": grp["Test"],
											"StartTime": int(time.time()),
											"EndTime": base.scriptgrpend[gid],
											"id": grurid
										}

										if "resultnamemode" in grp:
											base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = grp["resultnamemode"]
										else:
											if "resultnamemode" in base.scriptdefaults:
												base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = base.scriptdefaults["resultnamemode"]
											else:
												base.robot_schedule["Agents"][nxtagent][grurid]["resultnamemode"] = base.resultnamemodedefault

										if "excludelibraries" in grp:
											base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = grp["excludelibraries"]
										else:
											if "excludelibraries" in base.scriptdefaults:
												base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = base.scriptdefaults["excludelibraries"]
											else:
												base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = base.excludelibrariesdefault

										if "robotoptions" in grp:
											base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = grp["robotoptions"]
										else:
											if "robotoptions" in base.scriptdefaults:
												base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = base.scriptdefaults["robotoptions"]

										tr = base.testrepeaterdefault
										if "testrepeater" in base.scriptdefaults:
											tr = base.scriptdefaults["testrepeater"]
										if "testrepeater" in grp:
											tr = grp["testrepeater"]
										base.robot_schedule["Agents"][nxtagent][grurid]["testrepeater"] = str(tr)

										# injectsleepenableddefault = False
										ise = base.injectsleepenableddefault
										if "injectsleepenabled" in base.scriptdefaults:
											ise = base.scriptdefaults["injectsleepenabled"]
										if "injectsleepenabled" in grp:
											ise = grp["injectsleepenabled"]
										base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepenabled"] = str(ise)
										if base.str2bool(ise):
											# injectsleepminimumdefault = 15
											ismn = base.injectsleepminimumdefault
											if "injectsleepminimum" in base.scriptdefaults:
												ismn = base.scriptdefaults["injectsleepminimum"]
											if "injectsleepminimum" in grp:
												ismn = grp["injectsleepminimum"]
											base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepminimum"] = str(ismn)
											# injectsleepmaximumdefault = 45
											ismx = base.injectsleepmaximumdefault
											if "injectsleepmaximum" in base.scriptdefaults:
												ismx = base.scriptdefaults["injectsleepmaximum"]
											if "injectsleepmaximum" in grp:
												ismx = grp["injectsleepmaximum"]
											base.robot_schedule["Agents"][nxtagent][grurid]["injectsleepmaximum"] = str(ismx)

										# disableloglogdefault = False
										dll = base.disableloglogdefault
										if "disableloglog" in base.scriptdefaults:
											dll = base.scriptdefaults["disableloglog"]
										if "disableloglog" in grp:
											dll = grp["disableloglog"]
										base.robot_schedule["Agents"][nxtagent][grurid]["disableloglog"] = str(dll)
										# disablelogreportdefault = False
										dlr = base.disablelogreportdefault
										if "disablelogreport" in base.scriptdefaults:
											dlr = base.scriptdefaults["disablelogreport"]
										if "disablelogreport" in grp:
											dlr = grp["disablelogreport"]
										base.robot_schedule["Agents"][nxtagent][grurid]["disablelogreport"] = str(dlr)
										# disablelogoutputdefault = False
										dlo = base.disablelogoutputdefault
										if "disablelogoutput" in base.scriptdefaults:
											dlo = base.scriptdefaults["disablelogoutput"]
										if "disablelogoutput" in grp:
											dlo = grp["disablelogoutput"]
										base.robot_schedule["Agents"][nxtagent][grurid]["disablelogoutput"] = str(dlo)

										base.Agents[nxtagent]["AssignedRobots"] += 1
										base.debugmsg(5, "base.Agents[", nxtagent, "][AssignedRobots]:", base.Agents[nxtagent]["AssignedRobots"])

										currbts += 1
										base.debugmsg(2, "Robot:", currbts, "	Test:", grp["Test"], "	Assigned to:", nxtagent)

										base.debugmsg(9, "robot_schedule", base.robot_schedule)

						if base.run_end > 0 and int(time.time()) > base.run_end:
							base.debugmsg(6, "Test Paused: run_end:", base.run_end, "	time:", int(time.time()))
							base.run_paused = True
							break

						time.sleep(0.1)
						if not base.args.nogui:
							etm = time.gmtime(int(time.time()) - base.robot_schedule["Start"])
							base.gui.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))

		base.debugmsg(2, "Robot Ramp Up Completed")

	def sr_users_validate(self, *args):
		base.debugmsg(5, "args:", args)
		usrs = 0
		if args:
			r = args[0]
			if len(args) > 1:
				usrs = args[1]
			base.debugmsg(6, "Row:", r, "Robots:", usrs)
			base.debugmsg(8, "base.scriptlist:", base.scriptlist)
			base.scriptlist[r]["Robots"] = int(usrs)

		if not base.args.nogui:
			base.gui.sr_users_validate(*args)
		return True

	def sr_delay_validate(self, *args):
		base.debugmsg(5, "args:", args)
		if args:
			r = args[0]
			dly = 0
			if len(args) > 1:
				dly = str(args[1])
			base.debugmsg(6, "Row:", r, "Delay:", dly)
			base.scriptlist[r]["Delay"] = int(dly)

		if not base.args.nogui:
			base.gui.sr_delay_validate(*args)
		return True

	def sr_rampup_validate(self, *args):
		base.debugmsg(5, "args:", args)
		if args:
			r = args[0]
			rmp = None
			if len(args) > 1:
				rmp = str(args[1])
			base.debugmsg(6, "Row:", r, "RampUp:", rmp)
			base.scriptlist[r]["RampUp"] = int(rmp)

		if not base.args.nogui:
			base.gui.sr_rampup_validate(*args)
		return True

	def sr_run_validate(self, *args):
		base.debugmsg(5, "args:", args)
		if args:
			r = args[0]
			run = None
			if len(args) > 1:
				run = str(args[1])
			base.debugmsg(6, "Row:", r, "Run:", run)
			base.scriptlist[r]["Run"] = int(run)

		if not base.args.nogui:
			base.gui.sr_run_validate(*args)
		return True

	def sr_file_validate(self, r, *args):
		base.debugmsg(9, "r:", r, "	args:", args)
		if args:
			scriptfile = args[0]
		else:
			scriptfile = ""

		if not os.path.exists(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\ncannot be found by RFSwarm Manager."
			if not base.args.nogui:
				self.display_warning(msg)
			else:
				base.debugmsg(0, msg)
			return False
		elif not os.path.isfile(scriptfile):
			msg = "The referenced file:\n" + scriptfile + "\n\nis a directory, not a file."
			if not base.args.nogui:
				self.display_warning(msg)
			else:
				base.debugmsg(0, msg)
			return False

		base.debugmsg(7, "scriptfile:", scriptfile)
		if len(scriptfile) > 0:
			base.scriptlist[r]["Script"] = scriptfile
			relpath = base.get_relative_path(base.config['Plan']['ScriptDir'], scriptfile)
			script_hash = base.hash_file(scriptfile, relpath)
			base.scriptlist[r]["ScriptHash"] = script_hash

			if script_hash not in base.scriptfiles:
				base.scriptfiles[script_hash] = {
					"id": script_hash,
					"localpath": scriptfile,
					"relpath": relpath,
					"type": "script"
				}

				t = threading.Thread(target=base.find_dependancies, args=(script_hash, ))
				t.start()

		else:
			if "ScriptHash" in base.scriptlist[r]:
				oldhash = base.scriptlist[r]["ScriptHash"]
				t = threading.Thread(target=base.remove_hash, args=(oldhash, ))
				t.start()

			base.scriptlist[r]["Script"] = ''
			base.scriptlist[r]["ScriptHash"] = ''

		self.plan_scnro_chngd = True
		if not base.args.nogui:
			base.gui.sr_file_validate(r, *args)
		return True

	def sr_test_validate(self, *args):
		base.debugmsg(5, "args:", args)
		# r = int(args[0][-1:])+1
		r = int(args[0][3:])
		base.debugmsg(9, "r:", r)

		v = None
		if len(args) > 1 and len(args[1]) > 1:
			v = args[1]
			base.debugmsg(9, "v:", v)
			base.scriptlist[r]["Test"] = v

		base.debugmsg(9, "scriptlist[r]:", base.scriptlist[r])

		if not base.args.nogui:
			base.gui.sr_test_validate(*args)
		return True

	def UpdateAgents(self):

		uploadcount = 0
		removeagents = []
		robot_count = 0
		monitor_count = 0
		time_elapsed = int(time.time()) - base.agenttgridupdate
		if time_elapsed >= 5:
			base.debugmsg(6, "time_elapsed:", time_elapsed)

			base.agenttgridupdate = int(time.time())
			agntlst = list(base.Agents.keys())
			base.debugmsg(6, "agntlst:", agntlst)
			for agnt in agntlst:

				includerobots = True

				if "Uploading" in base.Agents[agnt]["Status"]:
					uploadcount += 1

				tm = base.Agents[agnt]["LastSeen"]
				agnt_elapsed = int(time.time()) - tm
				if agnt_elapsed > 30:
					base.Agents[agnt]["Status"] = "Offline?"
					includerobots = False
				if agnt_elapsed > 300:
					removeagents.append(agnt)
					includerobots = False

				if includerobots:
					robot_count += base.Agents[agnt]["Robots"]
					monitor_count += base.Agents[agnt]["Monitor"]

			if base.total_robots > 0 and robot_count < 1 and base.total_monitor > 0 and monitor_count < 1:
				# run finished so clear run name
				base.save_metrics(base.run_name, "Scenario", int(time.time()), "total_robots", robot_count, base.srvdisphost)
				base.save_metrics(base.run_name, "Scenario", int(time.time()), "monitor_robots", monitor_count, base.srvdisphost)
				base.save_metrics(base.run_name, "Scenario", int(time.time()), "End_Time", int(time.time()), base.srvdisphost)
				base.save_metrics("Time", "Scenario", int(time.time()), "End", int(time.time()), base.srvdisphost)
				base.run_name = ""
				base.robot_schedule["RunName"] = base.run_name

			# Update base.mon_end time on monitoring robot's jobs in the situations where:
			# base.total_robots > 0 and time now + base.mtimeafter is greater than base.mon_end
			# (Ensure we monitor long enough)
			if base.total_robots > 0:
				new_mon_end = int(time.time()) + base.mtimeafter
				if new_mon_end > base.mon_end:
					base.mon_end = new_mon_end
					self.update_monitoring_jobs_mon_end()

			# base.total_robots > 0 and robot_count < 1 and time now + base.mtimeafter is less than base.mon_end
			# (Ensure we don't monitor too long)
			if base.total_robots > 0 and robot_count < 1:
				new_mon_end = int(time.time()) + base.mtimeafter
				if new_mon_end < base.mon_end:
					base.mon_end = new_mon_end
					self.update_monitoring_jobs_mon_end()

			base.total_robots = robot_count
			base.total_monitor = monitor_count

			for agnt in removeagents:
				# this should prevent issue RuntimeError: dictionary changed size during iteration
				del base.Agents[agnt]

			# temp. fix for disconnecting agent when inactive:
			self.updatethread = threading.Thread(target=self.delayed_UpdateAgents)
			self.updatethread.start()

			if not base.args.nogui:
				base.debugmsg(6, "nogui:", base.args.nogui)
				try:
					base.gui.UpdateAgents()
				except Exception:
					pass

			# Save Total Robots Metric
			if len(base.run_name) > 0:
				base.save_metrics(base.run_name, "Scenario", int(time.time()), "total_robots", base.total_robots, base.srvdisphost)
				base.save_metrics(base.run_name, "Scenario", int(time.time()), "monitor_robots", base.total_monitor, base.srvdisphost)
			else:
				base.save_metrics("PreRun", "Scenario", int(time.time()), "total_robots", base.total_robots, base.srvdisphost)
				base.save_metrics("PreRun", "Scenario", int(time.time()), "monitor_robots", base.total_monitor, base.srvdisphost)

			# if base.args.run:
			base.debugmsg(5, "base.args.run:", base.args.run, "	base.args.nogui:", base.args.nogui, "	run_end:", base.run_end, "	time:", int(time.time()))
			base.debugmsg(5, "base.posttest:", base.posttest, "	total_robots:", base.total_robots)
			base.debugmsg(5, "base.posttest:", base.posttest, "	total_monitor:", base.total_monitor)
			base.debugmsg(5, "run_finish:", base.run_finish, "	time:", int(time.time()), "uploadcount:", uploadcount)
			if base.run_end > 0\
				and base.run_end < int(time.time())\
				and base.total_robots < 1\
				and base.total_monitor < 1\
				and not base.posttest\
				and base.run_finish < 1\
				and uploadcount < 1:

				base.run_finish = int(time.time())
				base.debugmsg(5, "run_end:", base.run_end, "	time:", int(time.time()), "	total_robots:", base.total_robots, "	total_monitor", base.total_monitor)
				# base.save_metrics(base.run_name, "Scenario", base.run_finish, "End_Time", base.run_finish, base.srvdisphost)
				base.save_metrics("Time", "Scenario", base.run_finish, "Upload_Finished", base.run_finish, base.srvdisphost)

				if not base.args.nogui:
					time.sleep(1)
					base.gui.delayed_UpdateRunStats()

			if base.run_finish > 0 and base.run_finish + 60 < int(time.time()) and not base.posttest:
				base.debugmsg(0, "Test Completed:	", base.run_finish, "[", datetime.now().isoformat(sep=' ', timespec='seconds'), "]")
				base.posttest = True
				if base.args.nogui:
					base.debugmsg(9, "report_text")
					base.report_text()
					base.debugmsg(6, "on_closing")
					self.on_closing()
				else:
					time.sleep(1)
					base.gui.delayed_UpdateRunStats()

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
		while base.run_dbthread:
			time.sleep(300)


base = RFSwarmBase()

core = RFSwarmCore()
# core = rfswarm()

try:
	core.mainloop()
except KeyboardInterrupt:
	core.on_closing()
except Exception as e:
	base.debugmsg(1, "core.Exception:", e)
	core.on_closing()