#!/usr/bin/python
#
#	Robot Framework Swarm
#		Manager
#    Version 0.7.1
#

# 	Helpful links
#
#

import sys
import platform
import signal
import os
import tempfile
import glob
import configparser
import hashlib
import lzma
import base64
import sqlite3
import math

# import robot

import socket
import ipaddress
import random
import time
from datetime import datetime
import re
import threading
import subprocess
import requests
from operator import itemgetter
import csv

import xml.etree.ElementTree as ET

import inspect

# import Tkinter as tk				#python2
import tkinter as tk				#python3
# import ttk						#python2
import tkinter.ttk as ttk			#python3
# import tkFileDialog as tkf		#python2
import tkinter.filedialog as tkf	#python3
import tkinter.messagebox as tkm	#python3


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
import urllib.parse
import json

import argparse


__name__ = "rfswarm"

class percentile:
	def __init__(self):
		self.count = 0
		self.percent = 90
		self.values = []

	def step(self, value, percent):
		base.debugmsg(9, "value:", value, "	percent:", percent)
		if value is None:
			return
		self.count += 1
		self.values.append(value)
		self.percent = percent

	def finalize(self):
		try:
			mincount = 100/(100-self.percent)
			if self.count < mincount:
				# Need at least 10 samples to get a useful percentile
				return None
			base.debugmsg(9, "percentile: finalize: mincount:", mincount, "	self.count:", self.count, "	self.percent:", self.percent, "	self.values:", self.values)
			nth = self.count * (self.percent/100)
			base.debugmsg(9, "percentile: finalize: nth:", nth)
			nthi = int(nth)
			# nthi = int(math.ceil(self.count * (self.percent/100)))
			self.values.sort()
			base.debugmsg(8, "percentile: finalize: nthi:", nthi, "	self.values[nthi]:", self.values[nthi], "	self.values:", self.values)
			return self.values[nthi]
			# return self.count
		except Exception as e:
			base.debugmsg(5, "Exception:", e)

class stdevclass:
	def __init__(self):
		self.M = 0.0
		self.S = 0.0
		self.k = 1

	def step(self, value):
		if value is None:
			return
		tM = self.M
		self.M += (value - tM) / self.k
		self.S += (value - tM) * (value - self.M)
		self.k += 1

	def finalize(self):
		base.debugmsg(9, "self.k:", self.k, "	self.S:", self.S, "	self.M:", self.M)
		if self.k < 3:
			return None
		try:
			res = math.sqrt(self.S / (self.k-2))
			base.debugmsg(8, "res:", res)
			return res
		except Exception as e:
			base.debugmsg(5, "Exception:", e)


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
				if (parsed_path.path == "/AgentStatus"):
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

				if (parsed_path.path == "/Scripts"):
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

				if (parsed_path.path == "/File"):
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
						#	jsonresp["POST"]["File"]["Body"]["Action"] = "<Upload/Download/Status>"
						if "Action" in jsonreq and len(jsonreq["Action"])>0 and jsonreq["Action"] in ["Upload","Download","Status"]:
							if jsonreq["Action"] == "Download":
								if "Hash" in jsonreq and len(jsonreq["Hash"])>0 and jsonreq["Hash"] in base.scriptfiles:
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
								if "Hash" in jsonreq and len(jsonreq["Hash"])>0:
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
								if "Hash" in jsonreq and len(jsonreq["Hash"])>0:
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
											logdir = os.path.join(base.datapath, "logs"+str(int(time.time())))

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


				if (parsed_path.path == "/Jobs"):
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

						# base.robot_schedule["Agents"]
						if jsonresp["AgentName"] in base.robot_schedule["Agents"].keys():
							jsonresp["Schedule"] = base.robot_schedule["Agents"][jsonresp["AgentName"]]
						else:
							jsonresp["Schedule"] = {}


				# , "Result"
				if (parsed_path.path == "/Result"):
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

						core.register_result(jsonreq["AgentName"], jsonreq["ResultName"], jsonreq["Result"],
									jsonreq["ElapsedTime"], jsonreq["StartTime"], jsonreq["EndTime"],
									jsonreq["ScriptIndex"], jsonreq["Robot"], jsonreq["Iteration"],
									jsonreq["Sequence"])

						jsonresp["Result"] = "Queued"
						base.debugmsg(7, "Result: jsonresp[\"Result\"]:", jsonresp["Result"])


				if (parsed_path.path == "/Metric"):
					base.debugmsg(7, "Metric")
					jsonreq = json.loads(rawData)
					base.debugmsg(7, "Metric: jsonreq:", jsonreq)
					requiredfields = ["PrimaryMetric", "MetricType", "MetricTime", "SecondaryMetrics"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							base.debugmsg(9, httpcode, ":", message)
							break

					if httpcode == 200:
						base.debugmsg(7, "Result: httpcode:", httpcode)
						jsonresp["Metric"] = jsonreq["PrimaryMetric"]

						# core.register_metric(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"])
						t = threading.Thread(target=core.register_metric, args=(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"], ))
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
		self.end_headers()
		self.wfile.write(bytes(message,"utf-8"))
		threadend = time.time()
		# base.debugmsg(5, parsed_path.path, "	threadstart:", "%.3f" % threadstart, "threadend:", "%.3f" % threadend, "Time Taken:", "%.3f" % (threadend-threadstart))
		base.debugmsg(5, "%.3f" % (threadend-threadstart), "seconds for ", parsed_path.path)
		return
	def do_GET(self):
		threadstart = time.time()
		httpcode = 200
		try:
			parsed_path = urllib.parse.urlparse(self.path)
			if (parsed_path.path == '/'):
				jsonresp = {}

				jsonresp["POST"] = {}
				jsonresp["POST"]["AgentStatus"] = {}
				jsonresp["POST"]["AgentStatus"]["URI"] = "/AgentStatus"
				jsonresp["POST"]["AgentStatus"]["Body"] = {}
				jsonresp["POST"]["AgentStatus"]["Body"]["AgentName"] = "<Agent Host Name>"
				jsonresp["POST"]["AgentStatus"]["Body"]["Status"] = "<Agent Status>"
				jsonresp["POST"]["AgentStatus"]["Body"]["AgentIPs"] = ["<Agent IP Address>","<Agent IP Address>"]
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
				jsonresp["POST"]["Metric"]["Body"]["SecondaryMetrics"]["Secondary Metric Name, e.g. CPUCount"] = "<Value>, e.g. 4"


				message = json.dumps(jsonresp)
			else:
				httpcode = 404
				message = "Unrecognised request: '{}'".format(parsed_path)
		except Exception as e:
			base.debugmsg(6, "AgentServer: do_GET:", e)
			httpcode = 500
			message = str(e)

		self.send_response(httpcode)
		self.end_headers()
		self.wfile.write(bytes(message,"utf-8"))
		threadend = time.time()
		# base.debugmsg(5, parsed_path.path, "		threadstart:", "%.3f" % threadstart, "threadend:", "%.3f" % threadend, "Time Taken:", "%.3f" % (threadend-threadstart))
		base.debugmsg(5, "%.3f" % (threadend-threadstart), "seconds for ", parsed_path.path)
		return
	def handle_http(self):
		return
	def respond(self):
		return

	# 	log_request is here to stop BaseHTTPRequestHandler logging to the console
	# 		https://stackoverflow.com/questions/10651052/how-to-quiet-simplehttpserver/10651257#10651257
	def log_request(self, code='-', size='-'):
		pass



class RFSwarmBase:
	version="0.7.1"
	debuglvl = 0

	config = None
	manager_ini = None

	save_ini = True

	scriptcount = 0
	scriptlist = [{}]
	scriptfiles = {}
	scriptgrpend = {}

	uploadfiles = {}

	index = ""
	file = ""
	sheet = ""


	run_abort = False
	run_name = ""
	run_name_current = ""
	run_start = 0
	run_end = 0
	run_finish = 0
	run_paused = False
	run_threads = {}
	total_robots = 0
	robot_schedule = {"RunName": "", "Agents": {}, "Scripts": {}}
	agentserver = None
	agenthttpserver = None
	updatethread = None

	Agents = {}
	agenttgridupdate = 0
	posttest = False

	dir_path = os.path.dirname(os.path.realpath(__file__))
	resultsdir = ""
	run_dbthread = True
	dbthread = None
	datapath = ""
	dbfile = ""
	datadb = None
	dbqueue = {"Write": [], "Read": [], "ReadResult": {}, "Results": [], "Metric": [], "Metrics": []}
	MetricIDs = {}
	scriptfilters = [""]

	# #000000 = Black
	defcolours = ['#000000']

	appstarted = False

	args = None

	gui = None

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# base application
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




	def findiniloctaion(self):

		if self.args.ini:
			self.debugmsg(1, "self.args.ini: ", self.args.ini)
			return self.args.ini

		inilocations = []

		srcdir = os.path.join(os.path.dirname(__file__))
		self.debugmsg(7, "srcdir[-2]: ", srcdir[-2:])
		if srcdir[-2:] == "/.":
			srcdir = srcdir[0:-2]
		self.debugmsg(7, "srcdir: ", srcdir)

		inifilename = "RFSwarmManager.ini"
		# default location for all previous versions
		inilocations.append(os.path.join(srcdir, inifilename))
		# probably best location
		inilocations.append(os.path.join(os.path.expanduser("~"), ".rfswarm", inifilename))
		# last resort location
		inilocations.append(os.path.join(tempfile.gettempdir(), inifilename))

		self.debugmsg(6, "inilocations: ", inilocations)


		for iniloc in inilocations:
			self.debugmsg(7, "iniloc: ", iniloc)
			if os.path.isfile(iniloc):
				self.debugmsg(7, "iniloc exists")
				return iniloc
			else:
				# can we write to this location?
				# 	if anything in the try statement fails then we can't so progress to next location
				self.debugmsg(7, "iniloc can be created?")
				try:
					loc = os.path.dirname(iniloc)
					self.debugmsg(7, "loc: ", loc)
					self.debugmsg(7, "loc isdir:", os.path.isdir(loc))
					if not os.path.isdir(loc):
						self.debugmsg(7, "creating loc")
						os.makedirs(loc)
						self.debugmsg(7, "loc created")

					self.debugmsg(7, "os.access(loc): ", os.access(loc, os.X_OK | os.W_OK))
					if os.access(loc, os.X_OK | os.W_OK):
						self.debugmsg(7, "iniloc can be created!")
						return iniloc
				except:
					pass
		# This should cause saveini to fail?
		return None



	def debugmsg(self, lvl, *msg):
		msglst = []
		prefix = ""
		if self.debuglvl >= lvl:
			try:
				if self.debuglvl >= 4:
					stack = inspect.stack()
					the_class = stack[1][0].f_locals["self"].__class__.__name__
					the_method = stack[1][0].f_code.co_name
					the_line = stack[1][0].f_lineno
					# print("RFSwarmBase: debugmsg: I was called by {}.{}()".format(str(the_class), the_method))
					prefix = "{}: {}({}): [{}:{}]	".format(str(the_class), the_method, the_line, self.debuglvl, lvl)
					# <36 + 1 tab
					# if len(prefix.strip())<36:
					# 	prefix = "{}	".format(prefix)
					# <32 + 1 tab
					if len(prefix.strip())<32:
						prefix = "{}	".format(prefix)
					# <28 + 1 tab
					# if len(prefix.strip())<28:
					# 	prefix = "{}	".format(prefix)
					# <24 + 1 tab
					if len(prefix.strip())<24:
						prefix = "{}	".format(prefix)

					msglst.append(str(prefix))

				for itm in msg:
					msglst.append(str(itm))
				print(" ".join(msglst))
			except:
				pass


	def str2bool(self, instr):
		base.debugmsg(9, "instr:", instr)
		# if instr in ["True", "true", "TRUE", "YES", "yes", "Yes", "1"]:
		# 	return True
		# return False
		return str(instr).lower()  in ("yes", "true", "t", "1")

	def dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def run_db_thread(self):
		while base.run_dbthread:
			if (self.datadb is None) or (base.run_name != base.run_name_current):
				base.debugmsg(9, "run_db_thread: ensure_db")
				self.ensure_db()

			if self.datadb is not None:

				# process db queues

				# Results
				if len(base.dbqueue["Results"])>0:
					base.debugmsg(9, "run_db_thread: dbqueue: Results")
					resdata = list(base.dbqueue["Results"])
					base.dbqueue["Results"] = []
					base.debugmsg(7, "dbqueue: Results: resdata:", resdata)
					try:
						sql = "INSERT INTO Results VALUES (?,?,?,?,?,?,?,?,?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, resdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						base.debugmsg(1, "run_db_thread: dbqueue: Results: Exception:", e)
						base.debugmsg(1, "run_db_thread: dbqueue: Results: ", sql, resdata)


				# Metric
				if len(base.dbqueue["Metric"])>0:
					base.debugmsg(9, "run_db_thread: dbqueue: Metric")
					resdata = list(base.dbqueue["Metric"])
					base.dbqueue["Metric"] = []
					base.debugmsg(9, "run_db_thread: dbqueue: Metric: resdata:", resdata)
					try:
						sql = "INSERT OR IGNORE INTO Metric VALUES (?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, resdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						base.debugmsg(1, "run_db_thread: dbqueue: Metric: Exception:", e)
						base.debugmsg(1, "run_db_thread: dbqueue: Metric: ", sql, resdata)

				# Metrics
				if len(base.dbqueue["Metrics"])>0:
					base.debugmsg(9, "run_db_thread: dbqueue: Metrics")
					resdata = list(base.dbqueue["Metrics"])
					base.dbqueue["Metrics"] = []
					base.debugmsg(9, "run_db_thread: dbqueue: Metrics: resdata:", resdata)
					try:
						sql = "INSERT INTO Metrics VALUES (?,?,?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, resdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						base.debugmsg(1, "run_db_thread: dbqueue: Metrics: Exception:", e)
						base.debugmsg(1, "run_db_thread: dbqueue: Metrics: ", sql, resdata)


				# General Write
				if len(base.dbqueue["Write"])>0:
					base.debugmsg(9, "run_db_thread: dbqueue: Write")
					tmpq = list(base.dbqueue["Write"])
					base.dbqueue["Write"] = []
					base.debugmsg(9, "run_db_thread: dbqueue: Write: tmpq:", tmpq)
					for item in tmpq:
						if item["SQL"] and item["VALUES"]:
							try:
								base.debugmsg(9, "run_db_thread: dbqueue: Write: SQL:", item["SQL"], " 	VALUES:", item["VALUES"])
								cur = self.datadb.cursor()
								cur.execute(item["SQL"], item["VALUES"])
								cur.close()
								self.datadb.commit()
							except Exception as e:
								base.debugmsg(1, "run_db_thread: dbqueue: Write: Exception:", e)
								base.debugmsg(1, "run_db_thread: dbqueue: Write: Item:", item)
						else:
							base.debugmsg(1, "run_db_thread: dbqueue: Write: Item not written, missing key SQL or VALUES")
							base.debugmsg(1, "run_db_thread: dbqueue: Write: Item:", item)

				# General Read
				if len(base.dbqueue["Read"])>0:
					base.debugmsg(7, "run_db_thread: dbqueue: Read")
					tmpq = list(base.dbqueue["Read"])
					base.dbqueue["Read"] = []
					base.debugmsg(7, "run_db_thread: dbqueue: Read: tmpq:", tmpq)
					for item in tmpq:
						if "SQL" in item: # and item["VALUES"]:
							try:
								base.debugmsg(7, "run_db_thread: dbqueue: Read: SQL:", item["SQL"])
								self.datadb.row_factory = self.dict_factory
								cur = self.datadb.cursor()
								cur.execute(item["SQL"])
								result = cur.fetchall()
								base.debugmsg(7, "run_db_thread: dbqueue: Read: result:", result)
								cur.close()
								self.datadb.commit()

								base.debugmsg(7, "run_db_thread: dbqueue: Read: result:", result)
								if "KEY" in item:
									base.dbqueue["ReadResult"][item["KEY"]] = result

							except Exception as e:
								base.debugmsg(1, "run_db_thread: dbqueue: Read: Exception:", e)
								base.debugmsg(1, "run_db_thread: dbqueue: Read: Item:", item)
						else:
							base.debugmsg(1, "run_db_thread: dbqueue: Read: Item not written, missing key SQL or VALUES")
							base.debugmsg(1, "run_db_thread: dbqueue: Read: Item:", item)



			time.sleep(0.1)
			# end of while base.run_dbthread

		if self.datadb is not None:
			self.datadb.close()
			self.datadb = None

	def ensure_db(self):
		createschema = False
		base.debugmsg(9, "run_name:", base.run_name)
		if len(base.run_name)>0:
			if base.run_name != base.run_name_current:
				base.run_name_current = base.run_name
				createschema = True
				self.MetricIDs = {}

			if createschema and self.datadb is not None:
				base.debugmsg(5, "Disconnect and close DB")
				self.datadb.commit()
				self.datadb.close()
				self.datadb = None
				self.MetricIDs = {}

			# check if dir exists
			base.debugmsg(5, "dir_path:", base.dir_path)
			# self.resultsdir = os.path.join(base.dir_path, "results")
			if 'ResultsDir' not in base.config['Run']:
				base.config['Run']['ResultsDir'] = os.path.join(base.dir_path, "results")
				base.saveini()
			self.resultsdir = base.config['Run']['ResultsDir']

			if not os.path.exists(self.resultsdir):
				try:
					os.mkdir(self.resultsdir)
				except Exception as e:
					if not os.path.exists(self.resultsdir):
						base.debugmsg(0, "Unable to create resultsdir:", self.resultsdir, "\n", str(e))
						core.on_closing()

			base.datapath = os.path.join(self.resultsdir, base.run_name)
			base.debugmsg(1, "datapath:", base.datapath)
			if not os.path.exists(base.datapath):
				try:
					os.mkdir(base.datapath)
				except Exception as e:
					if not os.path.exists(self.datapath):
						base.debugmsg(0, "Unable to create datapath:", self.datapath, "\n", str(e))
						core.on_closing()

			# check if db exists
			self.dbfile = os.path.join(base.datapath, "{}.db".format(base.run_name))
			base.debugmsg(5, "dbfile:", self.dbfile)
			if not os.path.exists(self.dbfile):
				createschema = True

			if self.datadb is None:
				base.debugmsg(5, "Connect to DB")
				self.datadb = sqlite3.connect(self.dbfile)
				self.datadb.create_aggregate("percentile", 2, percentile)
				self.datadb.create_aggregate("stdev", 1, stdevclass)
				self.MetricIDs = {}

			if createschema:
				base.debugmsg(5, "Create Schema")
				c = self.datadb.cursor()
				# create tables

				c.execute('''CREATE TABLE Results
					(script_index int, robot int, iteration int, agent text, sequence int, result_name text, result text, elapsed_time num, start_time num, end_time num)''')

				c.execute('''CREATE TABLE Metric
					(Name TEXT NOT NULL, Type TEXT NOT NULL, PRIMARY KEY("Name"))''')

				c.execute('''CREATE TABLE Metrics
					(ParentID INTEGER NOT NULL, Time INTEGER NOT NULL, Key TEXT NOT NULL, Value TEXT)''')


				# create indexes?
				c.execute('''
				CREATE INDEX "idx_metric_type" ON "Metric" ("Type"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metrics_parentid_key" ON "Metrics" ( "ParentID"	ASC, "Key"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metrics_parentid_time_key" ON "Metrics" ( "ParentID"	ASC, "Time"	ASC, "Key"	ASC)
				''')


 				# create views

				c.execute('''
				CREATE VIEW "Summary" AS
				SELECT
					r.result_name
					, min(rp.elapsed_time) "min", avg(rp.elapsed_time) "avg", max(rp.elapsed_time)  "max"
					, count(rp.result) as _pass
					, (Select count(rf.result) from Results as rf where r.rowid == rf.rowid AND rf.result == "FAIL" ) _fail
					, (Select count(ro.result) from Results as ro where r.rowid == ro.rowid AND ro.result <> "PASS" AND ro.result <> "FAIL" ) _other
				FROM Results as r
					LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == "PASS"
				GROUP BY
					r.result_name
				ORDER BY r.sequence
				''')

				#
				# SELECT
				# 	r.result_name,
				# 	min(rp.elapsed_time) "min", avg(rp.elapsed_time) "avg", max(rp.elapsed_time)  "max",
				# 	count(rp.result) as _pass,
				# 	count(rf.result) as _fail,
				# 	count(ro.result) as _other
				#
				# FROM Results as r
				# 	LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == "PASS"
				# 	LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == "FAIL"
				# 	LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> "PASS" AND ro.result <> "FAIL"
				# GROUP BY
				# 	r.result_name
				# ORDER BY r.sequence

				c.execute('''
				CREATE VIEW "AgentList" as
				SELECT
					a.Name "AgentName"
					, s.Value "AgentStatus"
					, max(s.Time) as "AgentLastSeen"
						, (Select ra.Value from Metrics ra where ra.ParentID = a.ROWID and ra.Key = "AssignedRobots"  and ra.Time = s.Time) "AgentAssigned"
						, (Select r.Value from Metrics r where r.ParentID = a.ROWID and r.Key = "Robots"  and r.Time = s.Time) "AgentRobots"
						, (Select max(l.Value) from Metrics l where l.ParentID = a.ROWID and l.Key = "Load"  and l.Time = s.Time) "AgentLoad"
						, (Select max(c.Value) from Metrics c where c.ParentID = a.ROWID and c.Key = "CPU"  and c.Time = s.Time) "AgentCPU"
						, (Select max(m.Value) from Metrics m where m.ParentID = a.ROWID and m.Key = "MEM"  and m.Time = s.Time) "AgentMEM"
						, (Select max(n.Value) from Metrics n where n.ParentID = a.ROWID and n.Key = "NET"  and n.Time = s.Time) "AgentNET"
				from Metric a
					left join Metrics s on s.ParentID = a.ROWID and s.Key = "Status"
				where a.Type = "Agent"
				GROUP by s.ParentID
				ORDER by a.Name
				''')

				#
				# SELECT
				# 	a.Name "AgentName"
				# 	, s.Value "AgentStatus"
				# 	, max(s.Time) as "AgentLastSeen"
				# 	, ra.Value "AgentAssigned"
				# 	, r.Value "AgentRobots"
				# 	, max(l.Value) "AgentLoad"
				# 	, max(c.Value) "AgentCPU"
				# 	, max(m.Value) "AgentMEM"
				# 	, max(n.Value) "AgentNET"
				# from Metric a
				# 	left join Metrics s on s.ParentID = a.ROWID and s.Key = "Status"
				# 	left join Metrics r on r.ParentID = a.ROWID and r.Key = "Robots" and r.Time = s.Time
				# 	left join Metrics ra on ra.ParentID = a.ROWID and ra.Key = "AssignedRobots" and ra.Time = s.Time
				# 	left join Metrics l on l.ParentID = a.ROWID and l.Key = "Load" and l.Time = s.Time
				# 	left join Metrics c on c.ParentID = a.ROWID and c.Key = "CPU" and c.Time = s.Time
				# 	left join Metrics m on m.ParentID = a.ROWID and m.Key = "MEM" and m.Time = s.Time
				# 	left join Metrics n on m.ParentID = a.ROWID and n.Key = "NET" and n.Time = s.Time
				# where a.Type = "Agent"
				# GROUP by s.ParentID
				# ORDER by a.Name

				c.execute('''
				CREATE VIEW "AgentHistory" as
				SELECT
					a.Name "AgentName"
					, s.Value "AgentStatus"
					, max(s.Time) as "AgentLastSeen"
						, (Select ra.Value from Metrics ra where ra.ParentID = a.ROWID and ra.Key = "AssignedRobots"  and ra.Time = s.Time) "AgentAssigned"
						, (Select r.Value from Metrics r where r.ParentID = a.ROWID and r.Key = "Robots"  and r.Time = s.Time) "AgentRobots"
						, (Select max(l.Value) from Metrics l where l.ParentID = a.ROWID and l.Key = "Load"  and l.Time = s.Time) "AgentLoad"
						, (Select max(c.Value) from Metrics c where c.ParentID = a.ROWID and c.Key = "CPU"  and c.Time = s.Time) "AgentCPU"
						, (Select max(m.Value) from Metrics m where m.ParentID = a.ROWID and m.Key = "MEM"  and m.Time = s.Time) "AgentMEM"
						, (Select max(n.Value) from Metrics n where n.ParentID = a.ROWID and n.Key = "NET"  and n.Time = s.Time) "AgentNET"
				from Metric a
					left join Metrics s on s.ParentID = a.ROWID and s.Key = "Status"
				where a.Type = "Agent"
				group by a.ROWID, s.Time
				ORDER by a.Name, s.Time
				''')

				#
				# SELECT
				# 	a.Name "AgentName"
				# 	, s.Value "AgentStatus"
				# 	, max(s.Time) as "AgentLastSeen"
				# 	, ra.Value "AgentAssigned"
				# 	, r.Value "AgentRobots"
				# 	, max(l.Value) "AgentLoad"
				# 	, max(c.Value) "AgentCPU"
				# 	, max(m.Value) "AgentMEM"
				# 	, max(n.Value) "AgentNET"
				# from Metric a
				# 	left join Metrics s on s.ParentID = a.ROWID and s.Key = "Status"
				# 	left join Metrics r on r.ParentID = a.ROWID and r.Key = "Robots" and r.Time = s.Time
				# 	left join Metrics ra on ra.ParentID = a.ROWID and ra.Key = "AssignedRobots" and ra.Time = s.Time
				# 	left join Metrics l on l.ParentID = a.ROWID and l.Key = "Load" and l.Time = s.Time
				# 	left join Metrics c on c.ParentID = a.ROWID and c.Key = "CPU" and c.Time = s.Time
				# 	left join Metrics m on m.ParentID = a.ROWID and m.Key = "MEM" and m.Time = s.Time
				# 	left join Metrics n on m.ParentID = a.ROWID and n.Key = "NET" and n.Time = s.Time
				# where a.Type = "Agent"
				# group by a.ROWID, s.Time
				# ORDER by a.Name, s.Time


				c.execute('''
				CREATE VIEW "ResultSummary" as
				SELECT
					a.Name
					, max(e.Time) as "_EntryTime"
					, (Select mn.Value from Metrics mn where mn.ParentID = a.ROWID and mn.Key like "min%" and e.Time = mn.Time ) "Min"
					, (Select av.Value from Metrics av where av.ParentID = a.ROWID and av.Key = "avg" and e.Time = av.Time ) "Average"
					, (Select sd.Value from Metrics sd where sd.ParentID = a.ROWID and sd.Key like "stDev%" and e.Time = sd.Time ) "StDev"
					, (Select pct.Key from Metrics pct where pct.ParentID = a.ROWID and pct.Key like "%ile" and e.Time = pct.Time ) "%ile_Key"
					, (Select pct.Value from Metrics pct where pct.ParentID = a.ROWID and pct.Key like "%ile" and e.Time = pct.Time ) "%ile_Value"
					, (Select mx.Value from Metrics mx where mx.ParentID = a.ROWID and mx.Key like "max%" and e.Time = mx.Time ) "Max"
					, (Select ps.Value from Metrics ps where ps.ParentID = a.ROWID and ps.Key like "_pass%" and e.Time = ps.Time ) "Pass"
					, (Select fl.Value from Metrics fl where fl.ParentID = a.ROWID and fl.Key like "_fail%" and e.Time = fl.Time ) "Fail"
					, (Select ot.Value from Metrics ot where ot.ParentID = a.ROWID and ot.Key like "_other%" and e.Time = ot.Time ) "Other"
				from Metric a
					left join Metrics e on e.ParentID = a.ROWID and e.Key = "EntryTime"
				where a.Type = "Summary"
				GROUP by a.ROWID
				ORDER by a.ROWID
				''')

				# SELECT
				# 	a.Name
				# 	, max(e.Time) as "_EntryTime"
				# 	, mn.Value "Min"
				# 	, av.Value "Average"
				# 	, sd.Value "StDev"
				# 	, pct.Key "%ile_Key"
				# 	, pct.Value "%ile_Value"
				# 	, mx.Value "Max"
				# 	, ps.Value "Pass"
				# 	, fl.Value "Fail"
				# 	, ot.Value "Other"
				# from Metric a
				# 	left join Metrics e on e.ParentID = a.ROWID and e.Key = "EntryTime"
				# 	left join Metrics mn on mn.ParentID = a.ROWID and mn.Key like "min%" and e.Time = mn.Time
				# 	left join Metrics av on av.ParentID = a.ROWID and av.Key = "avg" and e.Time = av.Time
				# 	left join Metrics sd on sd.ParentID = a.ROWID and sd.Key like "stDev%" and e.Time = sd.Time
				# 	left join Metrics pct on pct.ParentID = a.ROWID and pct.Key like "%ile" and e.Time = pct.Time
				# 	left join Metrics mx on mx.ParentID = a.ROWID and mx.Key like "max%" and e.Time = mx.Time
				# 	left join Metrics ps on ps.ParentID = a.ROWID and ps.Key like "_pass%" and e.Time = ps.Time
				# 	left join Metrics fl on fl.ParentID = a.ROWID and fl.Key like "_fail%" and e.Time = fl.Time
				# 	left join Metrics ot on ot.ParentID = a.ROWID and ot.Key like "_other%" and e.Time = ot.Time
				# where a.Type = "Summary" -- and a.ROWID = 9
				# GROUP by a.ROWID
				# ORDER by a.ROWID

				c.execute('''
				CREATE VIEW "MetricData" as
				SELECT
					  m.Name "PrimaryMetric"
					, m.Type "MetricType"
					, ms.Time "MetricTime"
					, ms.Key "SecondaryMetric"
					, ms.Value "MetricValue"
				FROM Metric as m
				JOIN Metrics ms on m.ROWID = ms.ParentID
				''')



				self.datadb.commit()

	def PrettyColName(self, colname):
		base.debugmsg(8, "PrettyColName: colname:", colname)
		newcolname = colname
		# if newcolname[:1] == '_':
		# 	newcolname = newcolname[1:]
		# newcolname = newcolname.replace("_", " ")

		cnlst = colname.split("_")
		ncnlst = []
		base.debugmsg(9, "PrettyColName: cnlst:", cnlst)
		for word in cnlst:
			base.debugmsg(9, "PrettyColName: word:", word)
			if len(word)>0:
				ncnlst.append(word.capitalize())
		base.debugmsg(9, "PrettyColName: ncnlst:", ncnlst)
		newcolname = " ".join(ncnlst)

		base.debugmsg(8, "PrettyColName: newcolname:", newcolname)

		return newcolname

	def line_colour(self, grp):
		if grp<len(base.defcolours):
			return base.defcolours[grp]
		else:
			newcolour = self.make_colour()
			base.debugmsg(9, "Initial newcolour:", newcolour)
			while newcolour in base.defcolours:
				base.debugmsg(9, base.defcolours)
				newcolour = self.make_colour()
				base.debugmsg(9, "newcolour:", newcolour)
			base.defcolours.append(newcolour)
			return newcolour

	def make_colour(self):
		hexchr = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
		r1 = hexchr[random.randrange(len(hexchr))]
		r2 = hexchr[random.randrange(len(hexchr))]
		g1 = hexchr[random.randrange(len(hexchr))]
		g2 = hexchr[random.randrange(len(hexchr))]
		b1 = hexchr[random.randrange(len(hexchr))]
		b2 = hexchr[random.randrange(len(hexchr))]
		return "#{}{}{}{}{}{}".format(r1,r2,g1,g2,b1,b2)

	def format_sec(self, sec_in):
		if sec_in>3599:
			hrs = int(sec_in/3600)
			mins = int(sec_in/60) - (hrs*60)
			# secs = sec_in - (((hrs*60) + mins) * 60)
			if mins>0:
				return "{}:{}".format(hrs, mins)
			return "{}".format(hrs)
		if sec_in>59:
			mins = int(sec_in/60)
			secs = sec_in - (mins * 60)
			if secs>0:
				return "{}:{}".format(mins, secs)
			return "{}".format(mins)
		return "{}".format(sec_in)

	def hash_file(self, file, relpath):
		BLOCKSIZE = 65536
		hasher = hashlib.md5()
		hasher.update(str(os.path.getmtime(file)).encode('utf-8'))
		hasher.update(relpath.encode('utf-8'))
		# with open(file, 'rb') as afile:
		# 	buf = afile.read(BLOCKSIZE)
		# 	while len(buf) > 0:
		# 		hasher.update(buf)
		# 		buf = afile.read(BLOCKSIZE)
		#
		# 	Intermittant issue : Too many open files, it seems that with open is not always closing files?
		#
		# Exception in thread Thread-1413:
		# Traceback (most recent call last):
		#   File "/usr/local/Cellar/python/3.7.4/Frameworks/Python.framework/Versions/3.7/lib/python3.7/threading.py", line 926, in _bootstrap_inner
		#     self.run()
		#   File "/usr/local/Cellar/python/3.7.4/Frameworks/Python.framework/Versions/3.7/lib/python3.7/threading.py", line 870, in run
		#     self._target(*self._args, **self._kwargs)
		#   File "./rfswarm.py", line 1034, in check_files_changed
		#     script_hash = base.hash_file(file_data['localpath'], file_data['relpath'])
		#   File "./rfswarm.py", line 901, in hash_file
		#     with open(file, 'rb') as afile:
		# OSError: [Errno 24] Too many open files: '/Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot'

		afile = open(file, 'rb')
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
		afile.close()
		base.debugmsg(3, "file:", file, "	hash:", hasher.hexdigest())
		return hasher.hexdigest()

	def remove_hash(self, hash):
		remove = True
		# base.scriptlist[r]["ScriptHash"]
		base.debugmsg(8, "scriptlist:", base.scriptlist)
		for scr in range(len(base.scriptlist)):
			if "ScriptHash" in base.scriptlist[scr] and base.scriptlist[scr]["ScriptHash"] == hash:
				remove = False

		if remove:
			del self.scriptfiles[hash]

	def tick_counter(self):
		#
		# This function is simply a way to roughly measure the number of agents being used
		# without collecting any other data from the user or thier machine.
		#
		# A simple get request on this file on startup or once a day should make it appear
		# in the github insights if people are actually using this application.
		#
		# t = threading.Thread(target=self.tick_counter)
		# t.start()
		# only tick once per day
		# 1 day, 24 hours  = 60 * 60 * 24
		aday = 60 * 60 * 24
		while True:

			ver = self.version
			if ver[0] != 'v':
				ver = "v" + ver

			# https://github.com/damies13/rfswarm/blob/v0.6.2/Doc/Images/z_manager.txt
			url = "https://github.com/damies13/rfswarm/blob/"+ver+"/Doc/Images/z_manager.txt"
			try:
				r = requests.get(url)
				self.debugmsg(9, "tick_counter:", r.status_code)
			except:
				pass
			time.sleep(aday)



	def find_dependancies(self, hash):
		keep_going = True
		checking = False

		# determine if is a robot file
		base.debugmsg(8, "RFSwarmCore: find_dependancies", self.scriptfiles[hash])
		localpath = self.scriptfiles[hash]['localpath']
		localdir = os.path.dirname(localpath)
		base.debugmsg(9, "RFSwarmCore: find_dependancies: localdir", localdir)
		filename, fileext = os.path.splitext(localpath)

		base.debugmsg(9, "RFSwarmCore: find_dependancies: filename, fileext:", filename, fileext)

		if (fileext in [".robot", ".Robot"] and keep_going):
			with open(localpath, 'rb') as afile:
				for fline in afile:
					line = fline.decode("utf-8")
					if checking and '*** ' in line:
						checking = False

					if checking:
						base.debugmsg(9, "RFSwarmCore: find_dependancies: line", line)
						try:
							if line.strip()[:1] != "#":
								linearr = line.strip().split()
								base.debugmsg(7, "find_dependancies: linearr", linearr)
								resfile = None;
								if len(linearr)>1 and linearr[0].upper() in ['RESOURCE','VARIABLES','LIBRARY']:
									base.debugmsg(9, "find_dependancies: linearr[1]", linearr[1])
									resfile = linearr[1]
								if not resfile and len(linearr)>2 and (linearr[0].upper() == 'METADATA' and linearr[1].upper() == 'FILE'):
									base.debugmsg(9, "find_dependancies: linearr[2]", linearr[2])
									resfile = linearr[2]
								if not resfile and len(linearr)>2 and (linearr[0].upper() == 'IMPORT' and linearr[1].upper() == 'LIBRARY'):
									base.debugmsg(9, "find_dependancies: linearr[2]", linearr[2])
									resfile = linearr[2]
								if resfile:
									base.debugmsg(7, "find_dependancies: resfile", resfile)
									# here we are assuming the resfile is a relative path! should we also consider files with full local paths?
									localrespath = os.path.abspath(os.path.join(localdir, resfile))
									base.debugmsg(8, "find_dependancies: localrespath", localrespath)
									if os.path.isfile(localrespath):
										newhash = self.hash_file(localrespath, resfile)
										base.debugmsg(9, "find_dependancies: newhash", newhash)
										self.scriptfiles[newhash] = {
												'id': newhash,
												'localpath': localrespath,
												'relpath': resfile,
												'type': linearr[0]
											}

										t = threading.Thread(target=base.find_dependancies, args=(newhash, ))
										t.start()

									else:
										filelst = glob.glob(localrespath)
										for file in filelst:
											base.debugmsg(9, "find_dependancies: file", file)
											relpath = file.replace(localdir, "")[1:]
											base.debugmsg(9, "find_dependancies: relpath", relpath)
											newhash = self.hash_file(file, relpath)
											base.debugmsg(9, "find_dependancies: newhash", newhash)
											self.scriptfiles[newhash] = {
													'id': newhash,
													'localpath': file,
													'relpath': relpath,
													'type': linearr[0]
												}

						except Exception as e:
							base.debugmsg(6, "find_dependancies: line", line)
							base.debugmsg(6, "find_dependancies: Exception", e)
							base.debugmsg(6, "find_dependancies: linearr", linearr)

					# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#test-data-sections
					match = re.search('\*+([^*\v]+)', line)
					if match is not None:
						base.debugmsg(6, "find_dependancies: match.group(0)", match.group(1))
						if match.group(1).strip().upper() in ['SETTINGS', 'SETTING', 'TEST CASES', 'TEST CASE', 'TASKS', 'TASK', 'KEYWORDS', 'KEYWORD']:
							checking = True


	def check_files_changed(self):
		# self.scriptfiles[hash]
		checkhashes = list(self.scriptfiles.keys())
		base.debugmsg(6, "checkhashes:", checkhashes)
		for chkhash in checkhashes:
			file_data = self.scriptfiles[chkhash]
			script_hash = base.hash_file(file_data['localpath'], file_data['relpath'])
			if script_hash != chkhash:
				# file changed
				base.debugmsg(3, "File's hash has changed: chkhash:", chkhash, "	script_hash:",script_hash, "	localpath:", file_data['localpath'])

				# check if file is in script list and update it's hash
				# base.scriptlist[r]["ScriptHash"] = script_hash
				for iid in range(len(base.scriptlist)):
					base.debugmsg(3, "base.scriptlist[",iid,"]:", base.scriptlist[iid])
					if "ScriptHash" in base.scriptlist[iid] and chkhash == base.scriptlist[iid]["ScriptHash"]:
						base.scriptlist[iid]["ScriptHash"] = script_hash
						break;

				if script_hash not in base.scriptfiles:
					file_data['id'] = script_hash
					base.scriptfiles[script_hash] = file_data

					t = threading.Thread(target=base.find_dependancies, args=(script_hash, ))
					t.start()

					self.remove_hash(chkhash)

	def get_relative_path(self, path1, path2):
		base.debugmsg(7, "path1:", path1)
		base.debugmsg(7, "path2:", path2)
		# commonpath = os.path.commonpath([path1, path2])

		base.debugmsg(8, "os.path.isdir(path1):", os.path.isdir(path1))
		base.debugmsg(8, "os.path.isfile(path1):", os.path.isfile(path1))
		# if not os.path.isdir(path1):
		if os.path.isfile(path1) or not os.path.exists(path1):
			path1 = os.path.dirname(path1)
			base.debugmsg(7, "path1:", path1)

		relpath = os.path.relpath(path2, start=path1)
		# https://www.geeksforgeeks.org/python-os-path-relpath-method/
		base.debugmsg(5, "relpath:", relpath)
		return relpath

	def save_upload_file(self, hash):
		base.debugmsg(7, "hash:", hash)
		# base.uploadfiles[jsonreq["Hash"]] = jsonreq
		base.debugmsg(7, "uploadfile:", self.uploadfiles[hash])

		# uploadfile: {
		# 	'AgentName': 'DavesMBP',
		# 	'Action': 'Upload',
		# 	'Hash': 'e60dd517d3b36ccd4aaa27286cbbaa7b',
		# 	'File': 'OC_Demo_2_1_1_1608356330_1_1608356333/Browse_Store_Product_1_output.xml',
		# 	'FileData': 		,
		# 	'LocalFile': '/Users/dave/Documents/GitHub/rfswarm/results/20201219_153823_3u_test_quick/logs/OC_Demo_2_1_1_1608356330_1_1608356333/Browse_Store_Product_1_output.xml'
		# }
		try:
			localfile = self.uploadfiles[hash]['LocalFile']
			# self.uploadfiles[hash]['File'] = jsonresp['File']
			base.debugmsg(3, "file:", localfile, "hash:", hash)

			# self.scriptlist[hash][]

			filedata = self.uploadfiles[hash]['FileData']

			self.debugmsg(6, "filedata:", filedata)
			self.debugmsg(6, "filedata:")

			decoded = base64.b64decode(filedata)
			self.debugmsg(6, "b64decode: decoded:", decoded)
			self.debugmsg(6, "b64decode:")

			uncompressed = lzma.decompress(decoded)
			self.debugmsg(6, "uncompressed:", uncompressed)
			self.debugmsg(6, "uncompressed:")

			localfiledir = os.path.dirname(localfile)
			self.debugmsg(6, "localfiledir:", localfiledir)
			ed = self.ensuredir(localfiledir)
			self.debugmsg(6, "ensuredir:", ed)

			with open(localfile, 'wb') as afile:
				self.debugmsg(6, "afile:")
				afile.write(uncompressed)
				self.debugmsg(6, "write:")

		except Exception as e:
			self.debugmsg(1, "Exception:", e)

	def ensuredir(self, dir):
		if len(dir)<1:
			return True
		if os.path.exists(dir):
			return True
		try:
			patharr = os.path.split(dir)
			self.debugmsg(6, "patharr: ", patharr)
			self.ensuredir(patharr[0])
			os.mkdir(dir, mode=0o777)
			self.debugmsg(5, "Directory Created: ", dir)
			return True
		except FileExistsError:
			self.debugmsg(5, "Directory Exists: ", dir)
			return False
		except Exception as e:
			self.debugmsg(1, "Directory Create failed: ", dir)
			self.debugmsg(1, "with error: ", e)
			return False

	def saveini(self):
		self.debugmsg(6, "save_ini:", self.save_ini)
		if self.save_ini:
			with open(base.manager_ini, 'w') as configfile:    # save
				base.config.write(configfile)
				self.debugmsg(6, "File Saved:", self.manager_ini)

	def get_next_agent(self, filters):
		base.debugmsg(9, "get_next_agent")
		base.debugmsg(8, "get_next_agent: base.Agents:", base.Agents)
		if len(base.Agents) <1:
			base.debugmsg(7, "Agents:",len(base.Agents))
			return None

		if base.args.agents:
			neededagents = int(base.args.agents)
			base.debugmsg(7, "Agents:",len(base.Agents),"	Agents Needed:", neededagents)
			if len(base.Agents) < neededagents:
				return None


		base.debugmsg(7, "filters:", filters)
		f_requre = []
		f_exclude = []
		for filt in filters:
			if filt['rule'] == 'Require':
				f_requre.append(filt['optn'])
			if filt['rule'] == 'Exclude':
				f_exclude.append(filt['optn'])


		loadtpl = []
		robottpl = []
		for agnt in base.Agents.keys():
			base.debugmsg(7, "agnt:", agnt)
			agntnamefilter = "Agent: {}".format(agnt)
			# check if this agent is specifically excluded
			base.debugmsg(7, "agntnamefilter:", agntnamefilter, "f_exclude:", f_exclude)
			if agntnamefilter not in f_exclude:
				# check if this agent is specifically required, if so no need for further evaluation
				if agntnamefilter in f_requre:
					base.debugmsg(7, "Agent Matched Require Filter:", agntnamefilter)
					return agnt

				# if we got this far, determine if agent meets requirements based on filter rules
				addagnt = False
				base.debugmsg(7, "addagnt:", addagnt)

				if len(filters)<1:
					# there are no filters applied
					addagnt = True
					base.debugmsg(7, "no filters applied", "addagnt:", addagnt)

				# if agent has Properties, compare filters against these
				if "Properties" in base.Agents[agnt]:
					# if all requried filter items in properties
					requirematch = 0
					for fil in f_requre:
						if fil in base.Agents[agnt]["Properties"]:
							requirematch += 1
							base.debugmsg(7, "Matched Required Filter:", fil)
						else:
							# split filter removeing last item, then try compare again
							filarr = fil.rsplit(":", 1)
							if len(filarr)>1:
								if filarr[0] in base.Agents[agnt]["Properties"]:
									if filarr[1].strip() == base.Agents[agnt]["Properties"][filarr[0]].strip():
										requirematch += 1
										base.debugmsg(7, "Matched Required Filter:", fil)

					if requirematch == len(f_requre):
						addagnt = True
						base.debugmsg(7, "requirematch:", requirematch, "required:", len(f_requre), "addagnt:", addagnt)

					# if any excluded filter items in properties
					for fil in f_exclude:
						if fil in base.Agents[agnt]["Properties"]:
							addagnt = False
							base.debugmsg(7, "Matched Excluded Filter:", fil, "addagnt:", addagnt)
						else:
							# split filter removeing last item, then try compare again
							filarr = fil.rsplit(":", 1)
							if len(filarr)>1:
								if filarr[0] in base.Agents[agnt]["Properties"]:
									if filarr[1].strip() == base.Agents[agnt]["Properties"][filarr[0]].strip():
										addagnt = False
										base.debugmsg(7, "Matched Excluded Filter:", fil, "addagnt:", addagnt)

				base.debugmsg(7, "Final result: addagnt:", addagnt)
				if addagnt:
					loadtpl.append([agnt, base.Agents[agnt]['LOAD%']])
					robottpl.append([agnt, base.Agents[agnt]['AssignedRobots']])

			else:
				base.debugmsg(7, "Agent Matched Exclude Filter:", agntnamefilter)



		base.debugmsg(7, "robottpl:", robottpl)
		if len(robottpl)<1:
			base.debugmsg(7, "robottpl empty, return None")
			return None

		# Start with agent with least robots
		robottpl.sort(key=itemgetter(1))
		base.debugmsg(9, "robottpl:", robottpl)
		if robottpl[0][1] < 10:
			return robottpl[0][0]
		else:
			# try for agent with least load
			base.debugmsg(7, "loadtpl:", loadtpl)
			if len(loadtpl)<1:
				# this should never happen!!!
				return None
			loadtpl.sort(key=itemgetter(1))
			base.debugmsg(9, "loadtpl:", loadtpl)
			if loadtpl[0][1] < 95:
				return loadtpl[0][0]
			else:
				return None

	def addScriptRow(self):
		base.scriptcount += 1

		row = int("{}".format(base.scriptcount))
		base.scriptlist.append({})

		base.scriptlist[base.scriptcount]["Index"] = base.scriptcount

		num = "10"
		base.scriptlist[base.scriptcount]["Robots"] = int(num)

		num = "0"
		base.scriptlist[base.scriptcount]["Delay"] = int(num)

		num = "1800"	# 30 minutes
		base.scriptlist[base.scriptcount]["RampUp"] = int(num)

		# num = "18000"  # 18000 sec = 5 hours
		num = "7200" # 3600 sec = 1hr, 7200 sec = 2 hours
		base.scriptlist[base.scriptcount]["Run"] = int(num)

		base.scriptlist[row]["Test"] = ""

		if not base.args.nogui and base.gui:
			base.gui.addScriptRow()

	def UpdateRunStats_SQL(self):

		display_percentile = base.config['Run']['display_percentile']
		base.debugmsg(6, "display_percentile:", display_percentile)

		gblist = []
		display_index = base.str2bool(base.config['Run']['display_index'])
		base.debugmsg(6, "display_index:", display_index)
		if display_index:
			gblist.append("r.script_index")

		display_iteration = base.str2bool(base.config['Run']['display_iteration'])
		base.debugmsg(6, "display_iteration:", display_iteration)
		if display_iteration:
			gblist.append("r.iteration")

		display_sequence = base.str2bool(base.config['Run']['display_sequence'])
		base.debugmsg(6, "display_sequence:", display_sequence)
		if display_sequence:
			gblist.append("r.sequence")

		gblist.append("r.result_name")
		base.debugmsg(6, "gblist:", gblist)

		gbcols = ", ".join(gblist)

		base.debugmsg(6, "gbcols:", gbcols)

		sql = "SELECT "
		if len(gblist)>0:
			sql += 	gbcols
			sql += 	", "
		sql += 		"round(min(rp.elapsed_time),3) 'min', "
		sql += 		"round(avg(rp.elapsed_time),3) 'avg', "
		sql += 		"round(percentile(rp.elapsed_time, {}),3) '{}%ile', ".format(display_percentile, display_percentile)
		sql += 		"round(max(rp.elapsed_time),3) 'max', "
		sql += 		"round(stdev(rp.elapsed_time),3) 'stDev', "
		sql += 		"count(rp.result) as _pass, "
		sql += 		"count(rf.result) as _fail, "
		sql += 		"count(ro.result) as _other "
		sql += "FROM Results as r "
		sql += 		"LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == 'PASS' "
		sql += 		"LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == 'FAIL' "
		sql += 		"LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> 'PASS' AND ro.result <> 'FAIL' "
		sql += "WHERE r.start_time>{} ".format(base.robot_schedule["Start"])
		if len(gblist)>0:
			sql += "GROUP BY  "
			sql += 		gbcols

		sql += " ORDER BY r.sequence"

		base.debugmsg(7, "sql:", sql)

		base.dbqueue["Read"].append({"SQL": sql, "KEY": "RunStats"})

		t = threading.Thread(target=self.SaveRunStats_SQL)
		t.start()


	def SaveRunStats_SQL(self):

		base.debugmsg(7, "Wait for RunStats")
		while "RunStats" not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)
			base.debugmsg(9, "Wait for RunStats")

		RunStats = base.dbqueue["ReadResult"]["RunStats"]
		base.debugmsg(7, "RunStats:", RunStats)


		# Save Metric Data
		# 	First ensure a metric for this agent exists
		if "Summary" not in base.MetricIDs:
			base.MetricIDs["Summary"] = {}

		for stat in RunStats:
			base.debugmsg(7, "stat:", stat)
			statname = stat["result_name"]
			if statname not in base.MetricIDs["Summary"]:
				# create the agent metric
				base.dbqueue["Metric"].append( (statname, "Summary") )

				# get the agent metric id
				base.debugmsg(7, "statname:", statname)
				safestatname = statname.replace('"', r'""')
				sql = 'select ROWID from Metric where Name = "'+safestatname+'"'
				base.debugmsg(7, "sql:", sql)
				base.dbqueue["Read"].append({"SQL": sql, "KEY": "Metric_"+statname})


		# Read Metric ID's
		for stat in RunStats:
			base.debugmsg(7, "stat:", stat)
			statname = stat["result_name"]
			if statname not in base.MetricIDs["Summary"]:
				if "Read" in base.dbqueue:
					base.debugmsg(7, "Read", base.dbqueue["Read"])
				if "ReadResult" in base.dbqueue:
					base.debugmsg(7, "ReadResult", base.dbqueue["ReadResult"])
				base.debugmsg(7, "Wait for Metric_"+statname)
				while "Metric_"+statname not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)
					base.debugmsg(9, "Waiting for Metric_"+statname)
				if "ReadResult" in base.dbqueue:
					base.debugmsg(7, "ReadResult", base.dbqueue["ReadResult"])
				base.debugmsg(7, "Wait for Metric_"+statname+">0")
				while len(base.dbqueue["ReadResult"]["Metric_"+statname])<1:
					time.sleep(0.1)
					base.debugmsg(9, "Waiting for Metric_"+statname+">0")

				if "Metric_"+statname in base.dbqueue["ReadResult"] and len(base.dbqueue["ReadResult"]["Metric_"+statname])>0:
					base.debugmsg(7, "Metric_"+statname+":", base.dbqueue["ReadResult"]["Metric_"+statname])

					base.MetricIDs["Summary"][statname] = base.dbqueue["ReadResult"]["Metric_"+statname][0]["rowid"]
					base.debugmsg(7, "MetricIDs[Summary]:", base.MetricIDs["Summary"])

			# Next save the Metrics
			if statname in base.MetricIDs["Summary"]:
				m_StatID = base.MetricIDs["Summary"][statname]
				m_Time = int(time.time())
				base.debugmsg(7, "m_StatID:", m_StatID, "	m_Time:", m_Time)

				base.dbqueue["Metrics"].append( (m_StatID, m_Time, "EntryTime", m_Time) )

				# stat: {'result_name': "Opening url 'http://opencart3/'", 'min': 0.411,
				# 			'avg': 0.439, '90%ile': None, 'max': 0.467, 'stDev': 0.04,
				# 			'_pass': 2, '_fail': 0, '_other': 0}

				for stati in stat:
					base.debugmsg(7, "stati:", stati, "	stat[stati]:", stat[stati])
					if stati != "result_name":
						base.dbqueue["Metrics"].append( (m_StatID, m_Time, stati, stat[stati]) )
						base.debugmsg(7, "Saving m_StatID:", m_StatID, "	m_Time:", m_Time, "	stati:", stati, "	stat[stati]:", stat[stati])



	def report_text(self, _event=None):
		base.debugmsg(6, "report_text")
		colno = 0
		base.debugmsg(6, "RunStats")
		base.debugmsg(6, "UpdateRunStats_SQL")
		base.UpdateRunStats_SQL()
		if "RunStats" not in base.dbqueue["ReadResult"]:
			base.debugmsg(6, "Wait for RunStats")
			while "RunStats" not in base.dbqueue["ReadResult"]:
				time.sleep(0.1)
			base.debugmsg(6, "Wait for RunStats>0")
			while len(base.dbqueue["ReadResult"]["RunStats"])<1:
				time.sleep(0.1)


		if "RunStats" in base.dbqueue["ReadResult"] and len(base.dbqueue["ReadResult"]["RunStats"])>0:
			base.debugmsg(7, "RunStats:", base.dbqueue["ReadResult"]["RunStats"])

			# request agent data for agent report
			sql = "SELECT * "
			sql += "FROM AgentHistory as a "
			sql += "WHERE a.AgentLastSeen>{} ".format(base.robot_schedule["Start"])
			sql += " ORDER BY a.AgentLastSeen"
			base.dbqueue["Read"].append({"SQL": sql, "KEY": "Agents"})
			# request agent data for agent report

			# request raw data for agent report
			sql = "SELECT * "
			sql += "FROM Results as r "
			sql += "WHERE r.start_time>{} ".format(base.robot_schedule["Start"])
			sql += " ORDER BY r.start_time"
			base.dbqueue["Read"].append({"SQL": sql, "KEY": "RawResults"})
			# request raw data for agent report


			fileprefix = base.run_name
			base.debugmsg(8, "fileprefix:", fileprefix)
			if len(fileprefix)<1:
				fileprefix = os.path.split(base.datapath)[-1]
				base.debugmsg(9, "fileprefix:", fileprefix)
			txtreport = os.path.join(base.datapath, "{}_summary.csv".format(fileprefix))
			base.debugmsg(7, "txtreport:", txtreport)
			base.debugmsg(1, "Summary File:", txtreport)
			base.debugmsg(6, "RunStats:", base.dbqueue["ReadResult"]["RunStats"])
			cols = []
			for col in base.dbqueue["ReadResult"]["RunStats"][0].keys():
				base.debugmsg(9, "colno:", colno, "col:", col)
				cols.append (base.PrettyColName(col))
			base.debugmsg(9, "cols:", cols)
			with open(txtreport, 'w', newline='') as csvfile:
				writer = csv.writer(csvfile, dialect='excel')
				writer.writerow(cols)
				for row in base.dbqueue["ReadResult"]["RunStats"]:
					rowdata = row.values()
					writer.writerow(rowdata)

			if not base.args.nogui:
				tkm.showinfo("RFSwarm - Info", "Report data saved to: {}".format(base.datapath))

		base.debugmsg(6, "Wait for Agents")
		while "Agents" not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)
		base.debugmsg(6, "Wait for Agents>0")
		while len(base.dbqueue["ReadResult"]["Agents"])<1:
			time.sleep(0.1)

		if "Agents" in base.dbqueue["ReadResult"] and len(base.dbqueue["ReadResult"]["Agents"])>0:
			fileprefix = base.run_name
			base.debugmsg(9, "fileprefix:", fileprefix)
			if len(fileprefix)<1:
				fileprefix = os.path.split(base.datapath)[-1]
				base.debugmsg(9, "fileprefix:", fileprefix)
			txtreport = os.path.join(base.datapath, "{}_agent_data.csv".format(fileprefix))
			base.debugmsg(6, "txtreport:", txtreport)
			base.debugmsg(1, "Agent Data:", txtreport)
			cols = []
			for col in base.dbqueue["ReadResult"]["Agents"][0].keys():
				base.debugmsg(9, "UpdateRunStats: colno:", colno, "col:", col)
				cols.append (base.PrettyColName(col))
			base.debugmsg(9, "cols:", cols)
			with open(txtreport, 'w', newline='') as csvfile:
				# writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				writer = csv.writer(csvfile, dialect='excel')
				writer.writerow(cols)
				for row in base.dbqueue["ReadResult"]["Agents"]:
					rowdata = row.values()
					writer.writerow(rowdata)


		base.debugmsg(6, "Wait for RawResults")
		while "RawResults" not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)
		base.debugmsg(6, "Wait for RawResults>0")
		while len(base.dbqueue["ReadResult"]["RawResults"])<1:
			time.sleep(0.1)

		if "RawResults" in base.dbqueue["ReadResult"] and len(base.dbqueue["ReadResult"]["RawResults"])>0:
			fileprefix = base.run_name
			base.debugmsg(9, "fileprefix:", fileprefix)
			if len(fileprefix)<1:
				fileprefix = os.path.split(base.datapath)[-1]
				base.debugmsg(9, "fileprefix:", fileprefix)
			txtreport = os.path.join(base.datapath, "{}_raw_result_data.csv".format(fileprefix))
			base.debugmsg(6, "txtreport:", txtreport)
			base.debugmsg(1, "Raw Result Data:", txtreport)
			cols = []
			for col in base.dbqueue["ReadResult"]["RawResults"][0].keys():
				base.debugmsg(9, "colno:", colno, "col:", col)
				cols.append (base.PrettyColName(col))
			base.debugmsg(9, "cols:", cols)
			with open(txtreport, 'w', newline='') as csvfile:
				# writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				writer = csv.writer(csvfile, dialect='excel')
				writer.writerow(cols)
				for row in base.dbqueue["ReadResult"]["RawResults"]:
					rowdata = row.values()
					writer.writerow(rowdata)

	def report_html(self, _event=None):
		print("report_html")
		if not base.args.nogui:
			tkm.showwarning("RFSwarm - Warning", "Generating HTML Reports not implimented yet")
		else:
			base.debugmsg(1, "RFSwarm - Warning", "Generating HTML Reports not implimented yet")

	def report_word(self, _event=None):
		print("report_word")
		if not base.args.nogui:
			tkm.showwarning("RFSwarm - Warning", "Generating Word Reports not implimented yet")
		else:
			base.debugmsg(1, "RFSwarm - Warning", "Generating Word Reports not implimented yet")


	def create_metric(self, MetricName, MetricType):
		# Save Metric Data
		# 	First ensure a metric for this agent exists
		if MetricType not in self.MetricIDs:
			self.MetricIDs[MetricType] = {}
		if MetricName not in self.MetricIDs[MetricType]:
			# create the agent metric
			self.dbqueue["Metric"].append( (MetricName, MetricType) )
			# get the agent metric id
			sql = 'select ROWID from Metric where Name = "'+MetricName+'"'
			self.debugmsg(5, "sql:", sql)
			self.dbqueue["Read"].append({"SQL": sql, "KEY": "Metric_"+MetricName})

			if "Read" in self.dbqueue:
				self.debugmsg(9, "Read", self.dbqueue["Read"])
			if "ReadResult" in self.dbqueue:
				self.debugmsg(9, "ReadResult", self.dbqueue["ReadResult"])
			self.debugmsg(5, "Wait for Metric_"+MetricName)
			while "Metric_"+MetricName not in self.dbqueue["ReadResult"]:
				time.sleep(0.1)
				self.debugmsg(9, "Waiting for Metric_"+MetricName)
			if "ReadResult" in self.dbqueue:
				self.debugmsg(7, "ReadResult", self.dbqueue["ReadResult"])
			self.debugmsg(5, "Wait for Metric_"+MetricName+">0")
			while len(self.dbqueue["ReadResult"]["Metric_"+MetricName])<1:
				time.sleep(0.1)
				self.debugmsg(5, "Waiting for Metric_"+MetricName+">0")

			if "Metric_"+MetricName in self.dbqueue["ReadResult"] and len(self.dbqueue["ReadResult"]["Metric_"+MetricName])>0:
				self.debugmsg(5, "Metric_"+MetricName+":", self.dbqueue["ReadResult"]["Metric_"+MetricName])

				if MetricType not in self.MetricIDs:
					self.MetricIDs[MetricType] = {}

				self.MetricIDs[MetricType][MetricName] = self.dbqueue["ReadResult"]["Metric_"+MetricName][0]["rowid"]
				self.debugmsg(7, "MetricIDs[MetricType]:", self.MetricIDs[MetricType])

		return self.MetricIDs[MetricType][MetricName]

	def save_metrics(self, PMetricName, MetricType, MetricTime, SMetricName, MetricValue):
		if self.datadb is not None:
			self.debugmsg(7, PMetricName, MetricType, MetricTime, SMetricName, MetricValue)
			metricid = self.create_metric(PMetricName, MetricType)
			self.debugmsg(7, "metricid:", metricid, MetricTime, SMetricName, MetricValue)
			self.dbqueue["Metrics"].append( (metricid, MetricTime, SMetricName, MetricValue) )

	def add_scriptfilter(self, filtername):
		self.debugmsg(7, "filtername:", filtername, self.scriptfilters)
		if filtername not in self.scriptfilters:
			self.scriptfilters.append(filtername)
			self.scriptfilters.sort()
		self.debugmsg(9, "filtername:", filtername, self.scriptfilters)

	def sec2hms(self, sec):
		base.debugmsg(6, "type(sec):",type(sec), sec)
		if (isinstance(sec, time.struct_time)):
			sec = time.mktime(sec)
			base.debugmsg(6, "type(sec):",type(sec), sec)
		h = int(sec/3600)
		m = int((sec-h*3600)/60)
		s = int((sec-h*3600)-m*60)
		hms = "{:02}:{:02}:{:02}".format(h,m,s)
		return hms

	def hms2sec(self, hms):
		sec = 0
		arrhms = str(hms).split(":")
		base.debugmsg(6, "arrhms:",arrhms)
		if len(arrhms)==3:
			h = int(arrhms[0])
			m = int(arrhms[1])
			s = int(arrhms[2])
			sec = (h*3600)+(m*60)+s
		if len(arrhms)==2:
			h = 0
			m = int(arrhms[0])
			s = int(arrhms[1])
			sec = (h*3600)+(m*60)+s
		if len(arrhms)==1:
			sec = int(arrhms[0])
		return sec



# class rfswarm:
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
		parser.add_argument('-i', '--ini', help='path to alternate ini file') # nargs='?',
		parser.add_argument('-s', '--scenario', help='Load this scenario file')
		parser.add_argument('-r', '--run', help='Run the scenario automatically after loading', action='store_true')
		parser.add_argument('-a', '--agents', help='Wait for this many agents before starting (default 1)')
		parser.add_argument('-n', '--nogui', help='Don\'t display the GUI', action='store_true')
		parser.add_argument('-d', '--dir', help='Results directory')
		parser.add_argument('-e', '--ipaddress', help='IP Address to bind the server to')
		parser.add_argument('-p', '--port', help='Port number to bind the server to')
		base.args = parser.parse_args()

		base.debugmsg(6, "base.args: ", base.args)

		if base.args.debug:
			base.debuglvl = int(base.args.debug)

		if base.args.version:
			exit()

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
			except:
				pass

		# old ini file

		if base.args.ini:
			base.save_ini = False
			base.debugmsg(5, "base.args.ini: ", base.args.ini)
			base.manager_ini = base.args.ini

		if os.path.isfile(base.manager_ini):
			base.debugmsg(7, "agentini: ", base.manager_ini)
			base.config.read(base.manager_ini)
		else:
			base.saveini()

		base.debugmsg(0, "	Configuration File: ", base.manager_ini)

		base.debugmsg(5, "base.config: ", base.config._sections)
		if base.args.scenario:
			base.save_ini = False
			base.debugmsg(5, "base.args.scenario: ", base.args.scenario)
			scenariofile = os.path.abspath(base.args.scenario)
			base.debugmsg(5, "scenariofile: ", scenariofile)
			if 'Plan' not in base.config:
				base.config['Plan'] = {}
			base.config['Plan']['ScenarioFile'] = scenariofile

		if base.args.dir:
			base.save_ini = False
			base.debugmsg(5, "base.args.dir: ", base.args.dir)
			ResultsDir = os.path.abspath(base.args.dir)
			base.debugmsg(5, "ResultsDir: ", ResultsDir)
			if 'Run' not in base.config:
				base.config['Run'] = {}
			base.config['Run']['ResultsDir'] = ResultsDir

		if base.args.ipaddress:
			base.save_ini = False
			base.debugmsg(5, "base.args.ipaddress: ", base.args.ipaddress)
			if 'Server' not in base.config:
				base.config['Server'] = {}
			base.config['Server']['BindIP'] = base.args.ipaddress

		if base.args.port:
			base.save_ini = False
			base.debugmsg(5, "base.args.port: ", base.args.port)
			if 'Server' not in base.config:
				base.config['Server'] = {}
			base.config['Server']['BindPort'] = base.args.port


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

		#
		# Plan
		#

		if 'Plan' not in base.config:
			base.config['Plan'] = {}
			base.saveini()

		if 'ScriptDir' not in base.config['Plan']:
			base.config['Plan']['ScriptDir'] = base.dir_path
			base.saveini()

		if 'ScenarioDir' not in base.config['Plan']:
			base.config['Plan']['ScenarioDir'] = base.dir_path
			base.saveini()

		if 'ScenarioFile' not in base.config['Plan']:
			base.config['Plan']['ScenarioFile'] = ""
			base.saveini()
		else:
			# check file exists - it may have been deleted since rfswarm last ran with this ini file
			if not os.path.exists(base.config['Plan']['ScenarioFile']):
				base.config['Plan']['ScenarioFile'] = ""
				base.config['Plan']['ScriptDir'] = base.dir_path
				base.config['Plan']['ScenarioDir'] = base.dir_path
				base.saveini()


		#
		# Run
		#


		if 'Run' not in base.config:
			base.config['Run'] = {}
			base.saveini()

		if 'ResultsDir' not in base.config['Run']:
			base.config['Run']['ResultsDir'] = os.path.join(base.dir_path, "results")
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
			base.gui = RFSwarmGUI()



		self.BuildCore()

		base.debugmsg(5, "run_agent_server")
		base.Agentserver = threading.Thread(target=self.run_agent_server)
		base.Agentserver.start()
		base.debugmsg(5, "run_db_thread")
		base.run_dbthread = True
		base.dbthread = threading.Thread(target=base.run_db_thread)
		base.dbthread.start()

		t = threading.Thread(target=base.tick_counter)
		t.start()




	def BuildCore(self):
		base.debugmsg(5, "BuildCore")

		base.debugmsg(5, "BuildCorePlan")
		self.BuildCorePlan()
		base.debugmsg(5, "BuildCoreRun")
		self.BuildCoreRun()

	def autostart(self):
		base.debugmsg(5, "appstarted:", base.appstarted)
		# wait for mainloops to finished
		while not base.appstarted:
			time.sleep(1)
			base.debugmsg(5, "appstarted:", base.appstarted)


		if base.run_start <1:
			neededagents = 1
			if base.args.agents:
				neededagents = int(base.args.agents)

			base.debugmsg(5, "len(base.Agents):", len(base.Agents), "	neededagents:", neededagents)
			# agntlst = list(base.Agents.keys())
			while len(base.Agents) < neededagents:
				base.debugmsg(1, "Waiting for Agents")
				base.debugmsg(3, "Agents:", len(base.Agents), "	Agents Needed:", neededagents)
				time.sleep(10)

			if base.args.nogui:
				base.debugmsg(5, "core.ClickPlay")
				self.ClickPlay()
			else:
				base.debugmsg(5, "base.gui.ClickPlay")
				base.gui.ClickPlay()

	def mainloop(self):

		if base.args.run:
			# auto click play ?
			# self.autostart()
			autostart = threading.Thread(target=self.autostart)
			autostart.start()

		if not base.args.nogui:
			base.gui.mainloop()


	def on_closing(self, _event=None, *args):
		# , _event=None is required for any function that has a shortcut key bound to it

		if base.appstarted:
			try:
				base.debugmsg(0, "Shutdown Agent Manager")
				base.agenthttpserver.shutdown()
			except:
				pass
		try:
			base.debugmsg(3, "Join Agent Manager Thread")
			base.Agentserver.join()
		except:
			pass

		try:
			base.run_dbthread = False
			base.debugmsg(3, "Join DB Thread")
			base.dbthread.join()
		except:
			pass

		try:
			base.debugmsg(3, "Save ini File")
			base.saveini()
		except:
			pass

		time.sleep(1)
		base.debugmsg(2, "Exit")
		try:
			sys.exit(0)
		except SystemExit:
			try:
				os._exit(0)
			except:
				pass


	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Server
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def run_agent_server(self):


		srvip = base.config['Server']['BindIP']
		srvport = int(base.config['Server']['BindPort'])
		if len(srvip)>0:
			srvdisphost = srvip
			ip = ipaddress.ip_address(srvip)
			base.debugmsg(5, "ip.version:", ip.version)
			if ip.version == 6 and sys.version_info < (3, 8):
				base.debugmsg(0, "Python 3.8 or higher required to bind to IPv6 Addresses")
				pyver = "{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
				base.debugmsg(0, "Python Version:",pyver,"	IP Version:", ip.version, "	IP Address:", srvip)
				srvip = ''
				srvdisphost = socket.gethostname()
		else:
			srvdisphost = socket.gethostname()


		server_address = (srvip, srvport)
		try:
			base.agenthttpserver = ThreadingHTTPServer(server_address, AgentServer)
		except PermissionError:
			base.debugmsg(0, "Permission denied when trying :",server_address)
			self.on_closing()
			return False
		except Exception as e:
			base.debugmsg(5, "e:", e)
			self.on_closing()
			return False


		base.appstarted = True
		base.debugmsg(5, "appstarted:", base.appstarted)
		base.debugmsg(1, "Starting Agent Manager", "http://{}:{}/".format(srvdisphost, srvport))
		base.agenthttpserver.serve_forever()

	def register_agent(self, agentdata):
		base.debugmsg(7, "agentdata:", agentdata)

		base.add_scriptfilter("Agent: {}".format(agentdata["AgentName"]))

		# if "AssignedRobots" not in base.Agents[agnt].keys():
		# 	print("get_next_agent: addinig AssignedRobots to ", agnt)
		# 	print("get_next_agent: base.Agents:", base.Agents)
		# 	base.Agents[agnt]["AssignedRobots"] = 0
		AssignedRobots = 0
		if agentdata["AgentName"] in base.Agents and "AssignedRobots" in base.Agents[agentdata["AgentName"]]:
			AssignedRobots = base.Agents[agentdata["AgentName"]]["AssignedRobots"]
		agentdata["AssignedRobots"] = AssignedRobots

		agentdata["LastSeen"] = int(time.time())
		if "Status" not in agentdata.keys():
			agentdata["Status"] = "Unknown"
			if agentdata["Robots"] == 0:
				agentdata["Status"] = "Ready"
			if agentdata["Robots"] > 0:
				agentdata["Status"] = "Running"

		load = max([agentdata["CPU%"], agentdata["MEM%"], agentdata["NET%"] ])
		agentdata["LOAD%"] = load
		if load>80:
			agentdata["Status"] = "Warning"
		if load>95:
			agentdata["Status"] = "Critical"

		base.Agents[agentdata["AgentName"]] = agentdata

		base.debugmsg(9, "register_agent: agentdata:", agentdata)

		# base.gui.UpdateAgents()
		t = threading.Thread(target=self.UpdateAgents)
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

		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Status", agentdata["Status"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "LastSeen", agentdata["LastSeen"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "AssignedRobots", agentdata["AssignedRobots"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Robots", agentdata["Robots"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "Load", agentdata["LOAD%"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "CPU", agentdata["CPU%"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "MEM", agentdata["MEM%"])
		base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "NET", agentdata["NET%"])

		if "AgentIPs" in agentdata:
			for ip in agentdata["AgentIPs"]:
				base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], "IPAddress", ip)
		if "Properties" in agentdata:
			for prop in agentdata["Properties"]:
				base.save_metrics(agentdata["AgentName"], "Agent", agentdata["LastSeen"], prop, agentdata["Properties"][prop])


	def register_result(self, AgentName, result_name, result, elapsed_time, start_time, end_time, index, robot, iter, sequence):
		base.debugmsg(9, "register_result")
		resdata = (index, robot, iter, AgentName, sequence, result_name, result, elapsed_time, start_time, end_time)
		base.debugmsg(7, "resdata:", resdata)
		base.dbqueue["Results"].append(resdata)
		base.debugmsg(9, "dbqueue Results:", base.dbqueue["Results"])

		if not base.args.nogui:
			ut = threading.Thread(target=base.gui.delayed_UpdateRunStats)
			ut.start()

	def register_metric(self, PrimaryMetric, MetricType, MetricTime, SecondaryMetrics):
		# core.register_metric(jsonreq["PrimaryMetric"], jsonreq["MetricType"], jsonreq["MetricTime"], jsonreq["SecondaryMetrics"])
		base.debugmsg(7, "PrimaryMetric:", PrimaryMetric, "	MetricType:", MetricType, "	MetricTime:", MetricTime, "	SecondaryMetrics:", SecondaryMetrics)

		# Save Metric Data

		for key in SecondaryMetrics:
			base.debugmsg(7, PrimaryMetric, MetricType, MetricTime, key, SecondaryMetrics[key])
			base.save_metrics(PrimaryMetric, MetricType, MetricTime, key, SecondaryMetrics[key])


	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Plan
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildCorePlan(self):
		base.debugmsg(5, "BuildCorePlan")

		if len(base.config['Plan']['ScenarioFile'])>0:
			self.OpenFile(base.config['Plan']['ScenarioFile'])
		else:
			base.addScriptRow()

	def OpenFile(self, ScenarioFile):
		fileok = True

		base.debugmsg(6, "ScenarioFile: ", ScenarioFile)
		base.debugmsg(6, "base.config['Plan']['ScenarioFile']: ", base.config['Plan']['ScenarioFile'])
		base.config['Plan']['ScenarioDir'] = os.path.dirname(ScenarioFile)
		base.debugmsg(6, "base.config['Plan']['ScenarioDir']: ", base.config['Plan']['ScenarioDir'])
		if base.config['Plan']['ScenarioFile'] != ScenarioFile:
			base.debugmsg(6, "ScenarioFile:", ScenarioFile)
			base.config['Plan']['ScenarioFile'] = ScenarioFile
			base.saveini()

		filedata = configparser.ConfigParser()
		base.debugmsg(6, "filedata: ", filedata._sections)

		if os.path.isfile(ScenarioFile):
			base.debugmsg(9, "ScenarioFile: ", ScenarioFile)
			filedata.read(ScenarioFile)

		base.debugmsg(6, "filedata: ", filedata)

		scriptcount = 0
		if "Scenario" in filedata:
			base.debugmsg(6, "Scenario:", filedata["Scenario"])
			if "scriptcount" in filedata["Scenario"]:
				scriptcount = int(filedata["Scenario"]["scriptcount"])
				base.debugmsg(8, "scriptcount:", scriptcount)
		else:
			base.debugmsg(1, "File contains no scenario:", ScenarioFile)
			return 1

		rowcount = 0
		for i in range(scriptcount):
			ii = i+1
			istr = str(ii)
			if istr in filedata:
				base.debugmsg(8, "filedata[",istr,"]:", filedata[istr])
				rowcount += 1

				# if i not in base.scriptlist:
				# 	base.scriptlist.append({})
				# 	base.scriptlist[ii]["Index"] = ii
				if not base.args.nogui:
					if ii+1 > base.gui.scriptgrid.grid_size()[1]:		# grid_size tupple: (cols, rows)
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
						# base.scriptlist[ii]["users"] = filedata[istr]["users"]
						self.sr_users_validate(rowcount, int(filedata[istr]["users"]))
						# delay = 0
				else:
					base.debugmsg(3, "robots missing [",istr,"]")
					fileok = False
				if "delay" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][delay]:", filedata[istr]["delay"])
					# base.scriptlist[ii]["delay"] = filedata[istr]["delay"]
					self.sr_delay_validate(rowcount, int(filedata[istr]["delay"]))
					# rampup = 60
				else:
					fileok = False
				if "rampup" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][rampup]:", filedata[istr]["rampup"])
					# base.scriptlist[ii]["rampup"] = filedata[istr]["rampup"]
					self.sr_rampup_validate(rowcount, int(filedata[istr]["rampup"]))
					# run = 600
				else:
					fileok = False
				if "run" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][run]:", filedata[istr]["run"])
					# base.scriptlist[ii]["run"] = filedata[istr]["run"]
					self.sr_run_validate(rowcount, int(filedata[istr]["run"]))
					# script = /Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot
				else:
					fileok = False
				if "script" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][script]:", filedata[istr]["script"])
					scriptname = filedata[istr]["script"]
					if not os.path.isabs(scriptname):
						# relative path, need to find absolute path
						combined = os.path.join(base.config['Plan']['ScenarioDir'], scriptname)
						base.debugmsg(8, "combined:", combined)
						scriptname = os.path.abspath(combined)
					base.debugmsg(8, "scriptname:", scriptname)
					self.sr_file_validate(rowcount, scriptname)
				else:
					fileok = False
				if "test" in filedata[istr]:
					base.debugmsg(8, "filedata[", istr, "][test]:", filedata[istr]["test"])
					# base.scriptlist[ii]["test"] = filedata[istr]["test"]
					self.sr_test_validate("row{}".format(rowcount), filedata[istr]["test"])
				else:
					fileok = False

				if "excludelibraries" in filedata[istr]:
					base.scriptlist[ii]["excludelibraries"] = filedata[istr]["excludelibraries"]

				if "robotoptions" in filedata[istr]:
					base.scriptlist[ii]["robotoptions"] = filedata[istr]["robotoptions"]

				if "filters" in filedata[istr]:
					base.debugmsg(9, "filedata[istr][filters]:", filedata[istr]["filters"], type(filedata[istr]["filters"]))
					filtr = filedata[istr]["filters"].replace("'", '"')
					base.debugmsg(9, "filtr:", filtr, type(filtr))
					filtrs = json.loads(filtr)
					base.debugmsg(9, "filtrs:", filtrs, type(filtrs))
					base.scriptlist[ii]["filters"] = filtrs


				if not fileok:
					base.debugmsg(1, "Scenario file is damaged:", ScenarioFile)
					return 1




	def ClickPlay(self, _event=None):

		base.debugmsg(0, "Test Started:	", int(time.time()), "[",datetime.now().isoformat(sep=' ',timespec='seconds'),"]")

		# before we start any robots we need to make sure the assigned robot counts are zero
		for nxtagent in base.Agents.keys():
			base.Agents[nxtagent]["AssignedRobots"] = 0


		datafiletime = datetime.now().strftime("%Y%m%d_%H%M%S")
		if len(base.config['Plan']['ScenarioFile'])>0:
			filename = os.path.basename(base.config['Plan']['ScenarioFile'])
			sname = os.path.splitext(filename)[0]
			base.run_name = "{}_{}".format(datafiletime, sname)
		else:
			base.run_name = "{}_{}".format(datafiletime, "Scenario")
		base.debugmsg(5, "base.run_name:", base.run_name)

		base.run_abort = False
		base.run_start = 0
		base.run_end = 0
		base.run_finish = 0
		base.posttest = False
		base.run_paused = False
		base.MetricIDs = {}

		base.robot_schedule = {"RunName": "", "Agents": {}, "Scripts": {}}
		base.debugmsg(5, "core.run_start_threads")
		t = threading.Thread(target=core.run_start_threads)
		t.start()
		if not base.args.nogui:
			time.sleep(1)
			base.debugmsg(5, "base.gui.delayed_UpdateRunStats")
			ut = threading.Thread(target=base.gui.delayed_UpdateRunStats)
			ut.start()




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
			base.run_end = int(time.time()) #time now
			base.debugmsg(0, "Run Stopped:", base.run_end, "[",datetime.now().isoformat(sep=' ',timespec='seconds'),"]")
			base.robot_schedule["End"] = base.run_end

			for agnt in base.robot_schedule["Agents"].keys():
				for grurid in base.robot_schedule["Agents"][agnt].keys():
					base.robot_schedule["Agents"][agnt][grurid]["EndTime"] = base.run_end

	def run_start_threads(self):

		if base.run_end>0 and int(time.time())>base.run_end:
			base.run_paused = True

		totrbts = 0
		currbts = 0

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


			if base.run_end>0 and int(time.time())>base.run_end:
				break

			if base.run_paused and int(time.time())<base.run_end:
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
						tkm.showinfo("RFSwarm - Info", "Enough Agents available to run Robots, test will now resume.")
					base.debugmsg(0, 'Enough Agents available to run Robots, resuming.')
			else:
				for grp in base.scriptlist:
					base.debugmsg(9, "grp", grp)
					if "Test" in grp.keys() and len(grp["Test"])>0:
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
							# MsgBox = tkm.askyesno('Save Scenario','Do you want to save the current scenario?')
							if not base.args.nogui and not base.run_paused:
								base.debugmsg(7, 'base.args.nogui:', base.args.nogui, "base.run_paused:", base.run_paused)
								tkm.showwarning("RFSwarm - Warning", "Not enough Agents available to run Robots!\n\nTest run is paused, please add agents to continue or click stop to abort.")
								# tkm.showinfo("RFSwarm - Warning", "Not enough Agents available to run Robots! Test run is paused, please add agents to continue or click stop to abort.")
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
								base.run_start = int(time.time()) #time now
								base.robot_schedule = {}
								base.robot_schedule["RunName"] = base.run_name
								base.robot_schedule["Agents"] = {}
								base.robot_schedule["Scripts"] = {}
								base.robot_schedule["Start"] = base.run_start

								if not base.args.nogui:
									stm = time.localtime(base.robot_schedule["Start"])
									base.gui.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))

								base.run_end = int(time.time()) + grp["Run"]
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
								base.scriptgrpend[gid] = base.run_start + grp["Delay"] + grp["RampUp"] + grp["Run"]

							time_elapsed = int(time.time()) - base.run_start
							base.debugmsg(9, 'time_elapsed', time_elapsed, "Delay", grp["Delay"])
							if time_elapsed > grp["Delay"] - 1:
								uid = 0
								nxtuid = len(base.robot_schedule["Scripts"][gid]) + 1
								base.debugmsg(9, 'nxtuid', nxtuid)
								# Determine if we should start another user?
								if nxtuid < grp["Robots"]+1:
									if grp["RampUp"] > 0:
										rupct = (time_elapsed - grp["Delay"]) /grp["RampUp"]
									else:
										rupct = 1
									base.debugmsg(9, 'rupct', rupct)
									ruusr = int(grp["Robots"] * rupct)
									base.debugmsg(9, 'nxtuid', nxtuid, 'ruusr', ruusr)
									if nxtuid < ruusr+1:
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

										if "excludelibraries" in grp:
											base.robot_schedule["Agents"][nxtagent][grurid]["excludelibraries"] = grp["excludelibraries"]

										if "robotoptions" in grp:
											base.robot_schedule["Agents"][nxtagent][grurid]["robotoptions"] = grp["robotoptions"]

										base.run_end = int(time.time()) + grp["Run"]
										base.robot_schedule["End"] = base.run_end

										base.Agents[nxtagent]["AssignedRobots"] += 1
										base.debugmsg(5, "base.Agents[",nxtagent,"][AssignedRobots]:", base.Agents[nxtagent]["AssignedRobots"])

										currbts += 1
										base.debugmsg(2, "Robot:", currbts, "	Test:", grp["Test"], "	Assigned to:", nxtagent)

										base.debugmsg(9, "robot_schedule", base.robot_schedule)

						if base.run_end>0 and int(time.time())>base.run_end:
							base.debugmsg(6, "Test Paused: run_end:", base.run_end, "	time:", int(time.time()))
							base.run_paused = True
							break

						time.sleep(0.1)
						if not base.args.nogui:
							etm = time.gmtime(int(time.time()) - base.robot_schedule["Start"])
							base.gui.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))

		base.debugmsg(2, "Robot Ramp Up Completed")

	def sr_users_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			v = None
			if len(args)>1:
				usrs = args[1]
		base.debugmsg(6, "Row:", r, "Robots:", usrs)
		base.debugmsg(8, "base.scriptlist:", base.scriptlist)
		base.scriptlist[r]["Robots"] = int(usrs)

		if not base.args.nogui:
			base.gui.sr_users_validate(*args)
		return True

	def sr_delay_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			dly = 0
			if len(args)>1:
				dly = str(args[1])
			base.debugmsg(6, "Row:", r, "Delay:", dly)
			base.scriptlist[r]["Delay"] = int(dly)

		if not base.args.nogui:
			base.gui.sr_delay_validate(*args)
		return True

	def sr_rampup_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			rmp = None
			if len(args)>1:
				rmp = str(args[1])
			base.debugmsg(6, "Row:", r, "RampUp:", rmp)
			base.scriptlist[r]["RampUp"] = int(rmp)

		if not base.args.nogui:
			base.gui.sr_rampup_validate(*args)
		return True

	def sr_run_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			run = None
			if len(args)>1:
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
		base.debugmsg(7, "scriptfile:", scriptfile)
		if len(scriptfile)>0:
			base.scriptlist[r]["Script"] = scriptfile
			script_hash = base.hash_file(scriptfile, os.path.basename(scriptfile))
			base.scriptlist[r]["ScriptHash"] = script_hash

			if script_hash not in base.scriptfiles:
				base.scriptfiles[script_hash] = {
					"id": script_hash,
					"localpath": scriptfile,
					"relpath": os.path.basename(scriptfile),
					"type": "script"
				}

				t = threading.Thread(target=base.find_dependancies, args=(script_hash, ))
				t.start()

			base.config['Plan']['ScriptDir'] = os.path.dirname(scriptfile)
			base.saveini()
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
		if len(args)>1 and len(args[1])>1:
			v = args[1]
			base.debugmsg(9, "v:", v)
			base.scriptlist[r]["Test"] = v

		base.debugmsg(9, "scriptlist[r]:", base.scriptlist[r])


		if not base.args.nogui:
			base.gui.sr_test_validate(*args)
		return True


	def UpdateAgents(self):

		uploadcount = 0
		rnum = 0
		removeagents = []
		robot_count = 0
		displayagent = True
		time_elapsed = int(time.time()) - base.agenttgridupdate
		if (time_elapsed>=5):
			base.debugmsg(6, "time_elapsed:", time_elapsed)

			base.agenttgridupdate = int(time.time())
			agntlst = list(base.Agents.keys())
			base.debugmsg(6, "agntlst:", agntlst)
			for agnt in agntlst:

				if "Uploading" in base.Agents[agnt]["Status"]:
					uploadcount += 1

				displayagent = True
				tm = base.Agents[agnt]["LastSeen"]
				agnt_elapsed = int(time.time()) - tm
				if agnt_elapsed>15:
					base.Agents[agnt]["Status"] = "Offline?"
				if agnt_elapsed>60:
					removeagents.append(agnt)
					# del base.Agents[agnt]
					displayagent = False


				robot_count += base.Agents[agnt]["Robots"]

			if base.total_robots>0 and robot_count <1:
				# run finished so clear run name
				base.run_name = ""
				base.robot_schedule["RunName"] = base.run_name

			base.total_robots = robot_count

			for agnt in removeagents:
				# this should prevent issue RuntimeError: dictionary changed size during iteration
				del base.Agents[agnt]

			if rnum>0:
				self.updatethread = threading.Thread(target=self.delayed_UpdateAgents)
				self.updatethread.start()

			if not base.args.nogui:
				base.debugmsg(6, "nogui:", base.args.nogui)
				try:
					base.gui.UpdateAgents()
				except:
					pass

			# Save Total Robots Metric
			if len(base.run_name)>0:
				base.save_metrics(base.run_name, "Scenario", int(time.time()), "total_robots", base.total_robots)
			else:
				base.save_metrics("PreRun", "Scenario", int(time.time()), "total_robots", base.total_robots)


			# if base.args.run:
			base.debugmsg(5, "base.args.run:", base.args.run, "	base.args.nogui:", base.args.nogui, "	run_end:", base.run_end, "	time:", int(time.time()))
			base.debugmsg(5, "base.posttest:", base.posttest, "	total_robots:", base.total_robots)
			base.debugmsg(5, "run_finish:", base.run_finish, "	time:", int(time.time()), "uploadcount:", uploadcount)
			if base.run_end > 0 and base.run_end < int(time.time()) and base.total_robots < 1 and not base.posttest and base.run_finish < 1 and uploadcount < 1:
				base.run_finish = int(time.time())
				base.debugmsg(5, "run_end:", base.run_end, "	time:", int(time.time()), "	total_robots:", base.total_robots)
				if not base.args.nogui:
					time.sleep(1)
					base.gui.delayed_UpdateRunStats()

			if base.run_finish > 0 and base.run_finish + 60 < int(time.time()) and not base.posttest:
			# if base.run_finish > 0 and base.run_end + 5 < base.run_finish and not base.posttest:
				base.debugmsg(0, "Test Completed:	", base.run_finish, "[",datetime.now().isoformat(sep=' ',timespec='seconds'),"]")
				base.posttest = True
				if base.args.nogui:
					base.debugmsg(9, "report_text")
					base.report_text()
					base.debugmsg(6, "on_closing")
					self.on_closing()
				else:
					time.sleep(1)
					base.gui.delayed_UpdateRunStats()

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# End class RFSwarmCore
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




class RFSwarmGUI(tk.Frame):
# class RFSwarmGUI:
	titleprefix = 'Robot Framework Swarm'

	# GUI = None
	tabs = None

	pln_graph = None
	scriptgrid = None
	scrollable_sg = None

	agenttgrid = None
	scrollable_ag = None

	rungrid = None
	rungridupdate = 0
	scrollable_rg = None

	plan_scnro_chngd = False

	plancolidx = 0
	plancolusr = 1
	plancoldly = 2
	plancolrmp = 3
	plancolrun = 4
	plancolnme = 5
	plancolscr = 6
	plancoltst = 7
	plancolset = 8
	plancoladd = 99

	display_agents = {}
	display_run = {}
	# imgdata = {}

	rfstheme = {}

	imgdata = {}
	b64 = {}

	elements = {}


	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# core application
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



	def __init__(self, master=None):

		self.root = tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		tk.Frame.__init__(self, self.root)
		# self.grid(sticky="nsew")
		self.grid(sticky="news", ipadx=0, pady=0)
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		# set initial window size
		self.root.geometry(base.config['GUI']['win_width'] + "x" + base.config['GUI']['win_height'])

		self.root.resizable(True, True)

		base.debugmsg(5, "self.root", self.root)
		base.debugmsg(5, "self.root[background]", self.root["background"])
		self.rootBackground = self.root["background"]

		# for i in range(0, 16):
		# 	val = "#"+format(i, 'x')+format(i, 'x')+format(i, 'x')
		# 	base.debugmsg(5, "val: ",val, self.rootBackground)
		# 	if self.rootBackground < val:
		# 		base.debugmsg(5, "less than")
		# 	if self.rootBackground > val:
		# 		base.debugmsg(5, "more than")
		# self.rootBackground.value

		# bgclr = winfo rbg . systemWindowBackgroundColor
		# base.debugmsg(5, "systemWindowBackgroundColor", systemWindowBackgroundColor())
		# base.debugmsg(5, "bgclr", bgclr)
		# https://github.com/tcltk/tk/blob/main/macosx/README


		base.debugmsg(6, "BuildUI")

		self.BuildUI()

		try:
			base.debugmsg(6, "pln_update_graph")
			ug = threading.Thread(target=self.pln_update_graph)
			ug.start()
		except:
			pass


	def on_closing(self, _event=None):

		base.debugmsg(3, "Close Scenario")
		sf = base.config['Plan']['ScenarioFile']
		try:
			self.mnu_file_Close()
		except:
			pass
		# mnu_file_Close clears this value, need to set it back so that it is saved
		# 		in the ini file so the next app open loads the file
		base.config['Plan']['ScenarioFile'] = sf

		base.debugmsg(3, "Close GUI")
		try:
			self.destroy()
		except:
			pass
		core.on_closing()


	def updateTitle(self):
		titletext = "{} - {}".format(self.titleprefix, "Untitled")
		if 'Plan' in base.config and 'ScenarioFile' in base.config['Plan']:
			if len(base.config['Plan']['ScenarioFile'])>0:
				titletext = "{} - {}".format(self.titleprefix, base.config['Plan']['ScenarioFile'])

		self.master.title(titletext)


	def get_icon(self, icontext):
		# # https://www.daniweb.com/programming/software-development/code/216634/jpeg-image-embedded-in-python
		base.debugmsg(5, "icontext:", icontext)
		# http://www.famfamfam.com/lab/icons/silk/
		files = {}
		# files["New"] = "famfamfam_silk_icons/icons/page_white.edt.gif"
		# files["Save"] = "famfamfam_silk_icons/icons/disk.gif"
		# files["SaveAs"] = "famfamfam_silk_icons/icons/disk_multiple.gif"
		# files["Open"] = "famfamfam_silk_icons/icons/folder_explore.gif"
		# files["Play"] = "famfamfam_silk_icons/icons/resultset_next.gif"
		# files["Stop"] = "famfamfam_silk_icons/icons/stop.gif"
		# files["report_text"] = "famfamfam_silk_icons/icons/report.gif"
		# files["report_html"] = "famfamfam_silk_icons/icons/report_go.gif"
		# files["report_word"] = "famfamfam_silk_icons/icons/report_word.gif"
		# files["Abort"] = "../famfamfam_silk_icons/icons/bomb.gif"
		# files["Aborted"] = "../famfamfam_silk_icons/icons/stop_grey.gif"

		# files["Advanced"] = "../famfamfam_silk_icons/icons/cog.gif"
		# files["Delete"] = "../famfamfam_silk_icons/icons/cross.gif"
		# files["Delete"] = "../famfamfam_silk_icons/icons/bin_empty.gif"
		# files["Script"] = "../famfamfam_silk_icons/icons/script.gif"
		# files["AddRow"] = "../famfamfam_silk_icons/icons/script_add.gif"
		# files["AddRow"] = "../famfamfam_silk_icons/icons/add.gif"



		if icontext in files:
			base.debugmsg(6, "icontext:", icontext)
			scrdir = os.path.dirname(__file__)
			base.debugmsg(6, "scrdir:", scrdir)
			imgfile = os.path.join(scrdir, files[icontext])
			base.debugmsg(6, "imgfile:", imgfile)
			if os.path.isfile(imgfile):
				base.debugmsg(0, "isfile: imgfile:", imgfile)
				with open(imgfile,"rb") as f:
					img_raw = f.read()
				base.debugmsg(0, "img_raw:", img_raw)
				# b64 = base64.encodestring(img_raw)
				# img_text = 'img_b64 = \\\n"""{}"""'.format(b64)

				self.imgdata[icontext] = tk.PhotoImage(file=imgfile)
				base.debugmsg(0, "imgdata[icontext]:", self.imgdata[icontext])


				return self.imgdata[icontext]
			else:
				base.debugmsg(6, "File not found imgfile:", imgfile)



		# png_b64 = """b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAC4SURBVCjPdZFbDsIgEEWnrsMm7oGGfZro\nhxvU+Iq1TyjU60Bf1pac4Yc5YS4ZAtGWBMk/drQBOVwJlZrWYkLhsB8UV9K0BUrPGy9cWbng2CtE\nEUmLGppPjRwpbixUKHBiZRS0p+ZGhvs4irNEvWD8heHpbsyDXznPhYFOyTjJc13olIqzZCHBouE0\nFRMUjA+s1gTjaRgVFpqRwC8mfoXPPEVPS7LbRaJL2y7bOifRCTEli3U7BMWgLzKlW/CuebZPAAAA\nAElFTkSuQmCC\n'"""

		self.b64 = {}
		# gif's
		self.b64["New"] = b'GIF89a\x10\x00\x10\x00\xe7\xfd\x00\x00\x00\x00\x01\x01\x01\x02\x02\x02\x03\x03\x03\x04\x04\x04\x05\x05\x05\x06\x06\x06\x07\x07\x07\x08\x08\x08\t\t\t\n\n\n\x0b\x0b\x0b\x0c\x0c\x0c\r\r\r\x0e\x0e\x0e\x0f\x0f\x0f\x10\x10\x10\x11\x11\x11\x12\x12\x12\x13\x13\x13\x14\x14\x14\x15\x15\x15\x16\x16\x16\x17\x17\x17\x18\x18\x18\x19\x19\x19\x1a\x1a\x1a\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!"""###$$$%%%&&&\'\'\'((()))***+++,,,---...///000111222333444555666777888999:::;;;<<<===>>>???@@@AAABBBCCCDDDEEEFFFGGGHHHIIIJJJKKKLLLMMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~\x7f\x7f\x7f\x80\x80\x80\x81\x81\x81\x82\x82\x82\x83\x83\x83\x84\x84\x84\x85\x85\x85\x86\x86\x86\x87\x87\x87\x88\x88\x88\x89\x89\x89\x8a\x8a\x8a\x8b\x8b\x8b\x8c\x8c\x8c\x8d\x8d\x8d\x8e\x8e\x8e\x8f\x8f\x8f\x90\x90\x90\x91\x91\x91\x92\x92\x92\x93\x93\x93\x94\x94\x94\x95\x95\x95\x96\x96\x96\x97\x97\x97\x98\x98\x98\x99\x99\x99\x9a\x9a\x9a\x9b\x9b\x9b\x9c\x9c\x9c\x9d\x9d\x9d\x9e\x9e\x9e\x9f\x9f\x9f\xa0\xa0\xa0\xa1\xa1\xa1\xa2\xa2\xa2\xa3\xa3\xa3\xa4\xa4\xa4\xa5\xa5\xa5\xa6\xa6\xa6\xa7\xa7\xa7\xa8\xa8\xa8\xa9\xa9\xa9\xaa\xaa\xaa\xab\xab\xab\xac\xac\xac\xad\xad\xad\xae\xae\xae\xaf\xaf\xaf\xb0\xb0\xb0\xb1\xb1\xb1\xb2\xb2\xb2\xb3\xb3\xb3\xb4\xb4\xb4\xb5\xb5\xb5\xb6\xb6\xb6\xb7\xb7\xb7\xb8\xb8\xb8\xb9\xb9\xb9\xba\xba\xba\xbb\xbb\xbb\xbc\xbc\xbc\xbd\xbd\xbd\xbe\xbe\xbe\xbf\xbf\xbf\xc0\xc0\xc0\xc1\xc1\xc1\xc2\xc2\xc2\xc3\xc3\xc3\xc4\xc4\xc4\xc5\xc5\xc5\xc6\xc6\xc6\xc7\xc7\xc7\xc8\xc8\xc8\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xce\xce\xce\xcf\xcf\xcf\xd0\xd0\xd0\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd6\xd6\xd6\xd7\xd7\xd7\xd8\xd8\xd8\xd9\xd9\xd9\xda\xda\xda\xdb\xdb\xdb\xdc\xdc\xdc\xdd\xdd\xdd\xde\xde\xde\xdf\xdf\xdf\xe0\xe0\xe0\xe1\xe1\xe1\xe2\xe2\xe2\xe3\xe3\xe3\xe4\xe4\xe4\xe5\xe5\xe5\xe6\xe6\xe6\xe7\xe7\xe7\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xeb\xeb\xeb\xec\xec\xec\xed\xed\xed\xee\xee\xee\xef\xef\xef\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\x8e\x00\xff\x89\x19H\xb0\xa0\x98\x7f\x08\x11\x8a\xc1\xb7\x8f\x9f\xc3\x87\xf8(\x1dL(f\x1f\xbdz\x18\xe3\xbdK\xc7\xef\\\xa5\x89\x02\xf9\xdd\xcbw\xef\xde<x\xea\xf8\xd9\xa3\x97i\xa2\x18~\xf9b\xde\xb3\'o\xddC~.\xf95\xd4\x89\xaf^<v\xea\xcc\xe1Tx\x93g=y\xef\xda\r\rYt\x1f>{\xf3\xe4-}Y\x94\x9f\xbe|\xf6\xecM\xad\xaa3&\xbe\xad\x0f\xf7\x89\xd5\xa7\x0f\xdf\xd7\x9ca\xf7\x91]\x0b6\xadX\xb1m\xb9:t\x99O\xae\xc3|.\r\xea\x1d\xf8/ \x00;'
		self.b64["Save"] = b'GIF89a\x10\x00\x10\x00\xe7\x98\x001`\xa61`\xa71`\xa81a\xa82a\xa82a\xa92a\xaa2b\xaa2b\xab2c\xac3c\xad3d\xae3d\xaf3e\xb04e\xb14f\xb24f\xb34g\xb45h\xb55h\xb65h\xb75i\xb75i\xb85i\xb95j\xba6j\xba6j\xbb6k\xbb6k\xbc7k\xba8k\xbb8l\xbb9l\xbc:m\xbb;n\xbd>p\xbb^\x89\xc9d\x8c\xc8e\x8c\xc8e\x8d\xc9e\x8d\xcaf\x8d\xc9g\x8e\xc9i\x90\xcah\x90\xcdl\x92\xcbm\x92\xcbj\x93\xcfm\x96\xd3p\x99\xd6y\x98\xc7q\x99\xd8r\x9b\xd9|\x9a\xc8s\x9b\xd9s\x9b\xdar\x9c\xdb|\x9b\xc9t\x9c\xdat\x9d\xdct\x9e\xddu\x9e\xdev\x9f\xddv\x9f\xdew\x9f\xde\x81\x9e\xccw\xa0\xdew\xa0\xdfx\xa1\xe0x\xa2\xe0y\xa2\xe1z\xa2\xe0z\xa2\xe1z\xa2\xe2z\xa3\xe1z\xa3\xe2z\xa3\xe3{\xa3\xe1{\xa3\xe2\x84\xa3\xcez\xa4\xe3{\xa4\xe2{\xa4\xe3}\xa6\xe6}\xa7\xe7~\xa8\xe7~\xa8\xe8\x8a\xa7\xd2\x80\xaa\xe9\x8e\xab\xd5\x95\xb0\xda\x88\xc0b\x9a\xb5\xdd\x9f\xba\xe1\xa4\xbe\xe4\xa9\xc2\xe7\xad\xc5\xea\xad\xc6\xeb\xb3\xca\xed\xb6\xcc\xee\xb8\xce\xef\xba\xd0\xee\xbb\xd0\xef\xbd\xd0\xec\xbe\xd2\xf0\xc3\xd5\xef\xc2\xd5\xf2\xc2\xdc\xbf\xc5\xd8\xf2\xc7\xd9\xf4\xc9\xdc\xf4\xcc\xdd\xf5\xd0\xdf\xf6\xd1\xdf\xf6\xd1\xe0\xf6\xd1\xe0\xf7\xd8\xe5\xf6\xd9\xe5\xf7\xdb\xe6\xf7\xdb\xe7\xf7\xdb\xe7\xf8\xdd\xe8\xf8\xdf\xe9\xf8\xdf\xe9\xf9\xe1\xec\xf9\xe2\xec\xf9\xe3\xed\xf9\xe5\xed\xfa\xe8\xf0\xfa\xe9\xf0\xfa\xea\xf0\xfa\xe9\xf1\xfa\xea\xf1\xfb\xeb\xf1\xfb\xed\xf2\xfb\xee\xf3\xfb\xee\xf4\xfb\xee\xf4\xfc\xef\xf4\xfc\xf0\xf5\xfc\xf1\xf6\xfc\xf2\xf6\xfc\xf3\xf7\xfd\xf3\xf8\xfd\xf6\xf9\xfd\xf6\xfa\xfd\xf6\xfa\xfe\xf7\xfa\xfd\xf7\xfa\xfe\xf8\xfa\xfe\xf7\xfb\xfe\xf8\xfb\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xfe\x00\xffq\x18\xc8a\xc3\x06\r\x1a@\x88\x08\xe1a\xc4?\x81r\xe6\\\xb2\x04i\x91 C\x90&\x15\xd2s\x86\x84\xc08X$E*q\x88P\xa3K\x8c\xfa\xe0)sf\x04\x078V\x181*1\x08\xd1$H\x80\xf2\xd8Q\x92\xa6\x02\x877U\x00\x01J\x11\xe8Q%E{\xee\xd4)\xf2e\xc2\x067T\xf8\xf0\xf1\x93h\x92\xa3?J\xe9\x08\xf1\x12aC\x9b)%N\xa8h\xe1b\x85\x89\x12hut\x81\xa0\x81\x8d\x14&P\xa28ibd\xc8\x0f\x1e8vpq\xa0A\r\x13&N\x9cD1BDH\x8f\x1d7lha\xa0\x01\xcd\x92%J\xe6\x12\x01\xe2c\x07\x8d\x191\xb2(\xc8`&\xc9\xa5\xcf\xa0C\xc3\xb8\x82\xc0\x03\x19#\x94\xb6\xa8^\xad\x1a\xd2\x8b\'\x06>\x8cABi\x8d\xed\xdb\xb6!\xb1\x08B\xa0\x83\x98#\xa9Y\xaf\x86\x84"G\x00\x0ca\xc0\x84^~\xa9\x86\x8c\x00\x19.X\xa0 !\xc2\x83\x06\x0b\x12\x1c(  \x00\x80\x01\x01\x01\x00;'
		self.b64["SaveAs"] = b'GIF89a\x10\x00\x10\x00\xc6u\x00._\xa63h\xba:i\xaa>j\xabDm\xabDp\xb0W~\xbbQ\x7f\xc3S\x7f\xc1S\x80\xc5T\x81\xc4U\x83\xc6X\x84\xc3]\x84\xbf[\x86\xc7]\x88\xc8_\x89\xc9`\x89\xc9a\x8a\xc7a\x8b\xc9b\x8b\xc8a\x8b\xcbh\x8b\xd3e\x8d\xcae\x8d\xccl\x8b\xcdn\x8a\xd7f\x8e\xc7m\x8b\xdah\x8e\xcdl\x8d\xdci\x90\xcdp\x8f\xe1n\x93\xcco\x96\xccn\x97\xd4q\x97\xd0q\x98\xd0s\x98\xces\x99\xd1u\x99\xd1s\x9a\xd4u\x9a\xd0w\x9a\xd2w\x9b\xd2w\x9c\xd2y\x9c\xd5z\x9d\xd3{\x9c\xddw\x9e\xd9x\x9e\xd8{\x9e\xd4x\x9f\xd8y\x9f\xdby\xa0\xd9z\xa0\xd9{\xa1\xdc}\xa2\xd9|\xa3\xdb\x80\xa3\xd5}\xa3\xde\x85\xa2\xdd\x82\xa4\xd6~\xa5\xdd\x80\xa6\xdd\x81\xa7\xe1\x81\xa7\xe2\x85\xa8\xdd\x84\xbfQ\x8f\xae\xda\x84\xbfT\x8c\xaf\xe4\x96\xb2\xee\x91\xb6\xd6\x92\xb5\xe6\x97\xb6\xea\x9a\xb6\xef\x99\xb8\xea\x9c\xbc\xe0\x98\xc9o\x99\xc9q\x9e\xbc\xee\x9b\xbd\xed\xa1\xbe\xea\xa1\xbf\xea\xa1\xbf\xef\x9e\xc0\xef\xb3\xc7\xe3\xb0\xcd\xf3\xbb\xcd\xe6\xba\xce\xef\xb8\xd2\xf4\xc7\xee\x87\xc7\xee\x8c\xd7\xf4\xa2\xd7\xf6\xa2\xe6\xf0\xef\xe5\xf1\xed\xe6\xf1\xed\xe6\xf1\xef\xe8\xf3\xea\xe9\xf4\xe4\xed\xf1\xf8\xea\xf3\xf3\xed\xf5\xf3\xf2\xf6\xfb\xf1\xf8\xff\xf7\xfb\xff\xfa\xfb\xfd\xfa\xfc\xfd\xfb\xfc\xfd\xfb\xfc\xfe\xff\xff\xdd\xff\xff\xe0\xfc\xfd\xfe\xfd\xfd\xfe\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\x7f\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb2\x80\x7f\x82\x83\x84\x85\x82#3%>\x1d\x1f*\'\x14\x86\x7f\x18XuWu\x97uT\x11\x86\x0eV9/;E+,-$\x90\x84\x0fU([uYtuif\x9a\x84\x17M\x10R\x88\x8a\x8c\x8e\xa7\x7f\x13J\x15Q\x93\x95\x98\x99\x9b\x7f\nK&S\x9du!\x97kjG\x12\x82\x07L"I\xa9mosrlnC\x08\x82\x0bZ\x1bN\xb5?@:7642\r\x82\x01\x0c\tH\xbfBA<851)\x06\x84\xe4\xc9\xce\x88\x19\x03&\x0c\x1a\x17\x05\x08\xc9\xb3F\x86\xc8\x13(F\xca\xc0\x10`\x88\x1c\x1c.^\xbet\x89\xd3c\x80!y\x16@x\xe0\xa0!\x03\x01\x00\x91R\n\n\x04\x00;'
		self.b64["Open"] = b'GIF89a\x10\x00\x10\x00\xe7\x87\x00\xb6\x83I\xba\x8aP\xd8\x87-\xbc\x8cT\xd8\x88-\xd9\x8e3\xc8\x95^\xda\x945\xc9\x98b\xda\x9a6\x97\xa3\xb6\x99\xa3\xb2\xda\xa16\xda\xa67\xd4\xa7G\xda\xaa6\xda\xab5\xda\xab6\xda\xae4\xda\xaf5\xda\xaf6\xb5\xaf\xa8\xb2\xb3\xa7\xda\xb36\x9a\xb6\xd9\xd9\xb44\xdb\xb6<\x9b\xba\xdf\x9e\xbd\xe0\xd3\xb8\x9c\xa4\xc1\xe4\xde\xb9\x92\xa8\xc2\xe0\xa7\xc4\xe5\xa8\xc4\xe5\xe1\xc2^\xa9\xc5\xe6\xb3\xc6\xc8\xaa\xc6\xe6\xe2\xc3_\xe2\xc3`\xab\xc6\xe6\xe9\xc1s\xe3\xc7k\xe4\xc7k\xe5\xcat\xb4\xcd\xe9\xed\xcaj\xea\xcbl\xba\xcf\xe2\xe6\xcdy\xb8\xd0\xeb\xb3\xd1\xf3\xd3\xd2\xa3\xee\xcfr\xee\xcfv\xee\xce\x88\xef\xd0z\xd4\xd4\xa9\xef\xd2\x80\xef\xd3\x85\xbd\xd8\xf3\xf2\xd5\x81\xef\xd4\x94\xc1\xda\xf4\xf3\xd7\x86\xf5\xdac\xf3\xd8\x8e\xc4\xdc\xf4\xc9\xdc\xf2\xc6\xdd\xf4\xc9\xdd\xf2\xc5\xde\xf5\xf3\xda\x96\xc6\xde\xf5\xf6\xder\xf6\xdev\xf4\xdc\x93\xf4\xdb\x9e\xc7\xe0\xf7\xca\xe0\xf6\xf5\xde\x91\xf5\xde\x94\xf4\xdd\xa7\xcb\xe2\xf8\xf7\xe1\x81\xcd\xe2\xf8\xcc\xe3\xf8\xf7\xe2\x85\xf5\xe0\x9f\xce\xe3\xf8\xf7\xe3\x8b\xf6\xe1\xac\xf8\xe4\x8e\xd6\xe4\xf3\xd6\xe5\xf5\xf8\xe5\x91\xd3\xe6\xf8\xf8\xe6\x95\xdb\xe7\xf5\xf9\xe8\x9c\xf9\xe9\xa1\xf9\xe9\xa4\xdc\xea\xf8\xf6\xe9\xc9\xdf\xec\xf8\xfa\xec\xac\xfa\xed\xb3\xfb\xef\xb9\xfa\xf0\xdc\xfc\xf2\xc8\xfc\xf6\xd8\xfb\xf6\xe8\xfb\xf7\xe9\xfb\xf7\xea\xfd\xfa\xf1\xfe\xfa\xef\xfd\xfa\xf2\xfe\xfb\xee\xfe\xfb\xef\xfe\xfc\xf0\xfe\xfc\xf1\xfe\xfc\xf2\xfe\xfc\xf3\xfe\xfc\xf6\xfe\xfc\xf7\xff\xfc\xf5\xfe\xfd\xf4\xff\xfd\xf6\xff\xfd\xf8\xff\xfd\xfa\xfe\xfe\xfd\xff\xfe\xfd\xff\xfe\xfe\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xca\x00\xff\t\x1cH\xb0\xe0\xbf\x0c#P(<\xa1\xc1\xe0\xc0\x0b\x83\x0c\x15"dH\x0e\x8b\x15\x18e\xb4\x188\xa1O\x97(Y\xb8\xdc\xf9\xb3\'\xcf\x1d;\x82(\x08|0GJ\x13\x1f/`\xf0\xd8\x91\xe3\x86\x8d8\x12\x04B\x80\xf3\x03\x87\n4z\xf6\xe8\xc1s\xd2P\x04\x81\r\x0c\x05\x02\xe4g\xcf\x1b1:Jp\x08\x11\xc3\x81@\x06|\xdc\xb0QCfK\r\x17c\xd2\x1c\x99aA`\x82:k\xcc\x88\xc1\xc2\xc4\x84\x17(J\x90\x84\x01!\xf0\x00\x9d2`\xaa,\x11\xc2\xe1\x8c\x11"=\xacx\x10X\xa0\xcd\x14\'I\x86\x04\x11\xf1\x05H\x8f\x1eW0\x0c$ \x80\x80e\x02\x15\x8ahyB\x85\xc6\x02\x87\x04S\x90\xd8\xa0\xa0\x83\x01\xd0\x06\x11|\x00\x80\xba\xe0\x80\x00\xad\r\x06\x04\x00;'
		self.b64["Play"] = b'GIF89a\x10\x00\x10\x00\xa56\x00\x14A\xb7\x15E\xb9\x16J\xbd\x16N\xc0\x17P\xbd\x18S\xc0\x18Y\xc4\x19Y\xc6\x1ab\xc6\x1ab\xc9#n\xcd,r\xcd;q\xcc<t\xcf5w\xd2=w\xd0?z\xd0C\x7f\xd3C\x84\xd6G\x84\xd6K\x88\xd6S\x8e\xdb`\x95\xdda\x97\xddb\x97\xe1n\xa0\xe2r\xa1\xdft\xa2\xe2t\xa3\xe0u\xa3\xdfu\xa4\xe3w\xa4\xe0y\xa6\xe0y\xa7\xe6~\xa8\xe1|\xa9\xe1|\xa9\xe8~\xa9\xe8\x80\xaa\xe3\x81\xab\xe2\x81\xab\xe3\x80\xab\xe8\x80\xab\xea\x87\xaf\xe4\x87\xb0\xe8\x8a\xb1\xe4\x90\xb5\xe7\x92\xb7\xe8\x99\xbb\xe9\x99\xbb\xea\xa1\xc1\xec\xa3\xc2\xed\xa8\xc7\xee\xad\xc8\xef\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00?\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06K\xc0\x9fpH,\x1a\x8f\xc8T\tiT\x916Lb\xa8\xc6\xb2D\x85\x19\xda\xcc3\xb9bd/\xd8e\x11\xad\xc4L\xa8\x16\x05\xc1\x94\xb88\x9fS\xe4\xc0t\xac4#H!\xaa\x10\x81\x1e\x04W\t\x1d\r\x02W?\x06\x0c\x01\x87?\x03\x00\x8c\x90\x91A\x00;'
		self.b64["Stop"] = b'GIF89a\x10\x00\x10\x00\xe7\x84\x00\xd5>5\xd8G>\xd7H@\xd8H@\xfaB%\xd9KC\xd9KD\xfdF(\xdaOG\xfeI,\xffK,\xdbUM\xffO0\xffO1\xffP2\xffP3\xddYQ\xdc[S\xffU7\xde^T\xffY;\xffY<\xffZ<\xdebZ\xff\\?\xff^@\xff^A\xf9`H\xffcF\xe0jc\xffdF\xfdeJ\xe0le\xe4lc\xffgH\xffgN\xffiK\xffnO\xffnP\xffoP\xe4ul\xffpO\xe3xq\xffsU\xfftU\xfftZ\xffxY\xffyZ\xe7\x81y\xff~_\xff~`\xff\x7f_\xe5\x84}\xff\x80`\xff\x81g\xff\x83e\xe6\x8a\x85\xe8\x8b\x83\xff\x89i\xf2\x8b}\xf7\x8d}\xe7\x91\x8b\xff\x8dm\xff\x8en\xfa\x8e}\xff\x8eo\xff\x8fs\xea\x93\x8c\xff\x90o\xfc\x90\x7f\xf4\x94\x86\xff\x93s\xff\x93t\xfa\x93\x84\xff\x93x\xe9\x97\x92\xe9\x98\x92\xf6\x96\x89\xff\x95\x84\xea\x9a\x95\xfa\x97\x89\xff\x98v\xff\x98x\xff\x99x\xff\x99\x87\xea\x9e\x98\xff\x9b\x8a\xed\x9f\x98\xff\x9d|\xeb\xa0\x9b\xff\x9e|\xeb\xa2\x9d\xff\xa0}\xff\xa0~\xeb\xa3\x9e\xff\xa1\x85\xff\xa2\x81\xec\xa5\xa0\xff\xa1\x90\xff\xa5\x81\xfa\xa5\x96\xff\xa7\x84\xff\xa7\x85\xff\xaa\x86\xef\xac\xa5\xee\xad\xa6\xff\xab\x89\xff\xaa\x98\xfb\xad\x9e\xfb\xad\x9f\xff\xae\x91\xff\xaf\x8b\xf0\xb1\xa9\xfc\xb2\xa2\xfb\xba\xac\xff\xbb\x9c\xff\xbb\xa6\xff\xbf\xa0\xff\xbe\xab\xff\xc2\xa3\xfb\xc3\xb4\xff\xc4\xb1\xfc\xc8\xb7\xfc\xcd\xbc\xff\xcd\xb8\xff\xce\xb9\xff\xcf\xbb\xfc\xd1\xc1\xff\xd1\xbd\xfc\xd3\xc2\xfc\xd4\xc4\xff\xd6\xc1\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xc6\x00\xff\t\x1cH\xb0\xa0A/a\xb6d\xa9\xb2\xc4\xe0@8\x81\x06\x01\xf2\xd3G\xcf\x15\x87i\x04\xddy\xa3\xa6L\x177x\x86\x14D\xf3\xa7\xce\x193`\xb0H!\xf2EN\x8e\x81O\xf6\xcc\x19\x03F\xcb\x14$At\xd4P\xc2\x06\x84@&|\xb8`\x99r\xe4\x87\x8e\x1b2\\\xa4X\xd3A`\x8f<Q\x8a\x1e\x8d\xf1bE\t\x11b.\x08\xc4a\xc7\xc7\xd4\x17,N\x90\xe0\x80\xc1J\x04\x814\xe8\xcc\xa0\xba\xc2\x04\t\x0f\x1a(4\xa0\xb2@\xa0\x8a8BR\x94x\xab\xc1\x82\x04\x05#\x92\x0c\x18\x08\xa3\x8d\x8d\x0c\x19*Hxp\xe0C\x93\t\x05Q\x90i\xe1\x80A\x02\x02\x1b\x8c@p\x18\x02\x8a\x93"@x\xec\xd8\xec\xf0\x9f\x01\x04\x05\x04\x04\x00P\xba5\xc1\x80\x00;'
		self.b64["report_text"] = b'GIF89a\x10\x00\x10\x00\xc6\\\x00~1\x18\xabB!\xacC!\xaeF"\xaeI"\xa5K,\xafK#\xb1N#\xb2Q$\xb2R%\xb4U%\xb5V&\xb7Y&\xb7[&\xaf]5\xb8^\'\xb8_\'\xbaa(\xbexI\xb3yc\xb3|d\xb5\x7fe\xb5\x82f\xb7\x83gj\x93\xd4\xb9\x87gj\x98\xd9\xc2\x8bdk\x99\xdan\x9a\xdc\xbf\x8fao\x9b\xdcr\x9c\xdcq\x9d\xdd\xc1\x92cq\x9e\xdfs\x9e\xdf\xc2\x94ds\x9f\xe0t\xa0\xe0v\xa0\xe0\xc3\x96ev\xa2\xe0w\xa3\xe1x\xa3\xe1\xc4\x99f\xc5\x9agz\xa5\xe1\xa0\xbe\xea\xa1\xbf\xea\xa2\xc0\xea\xa3\xc0\xea\xca\xc6\xc4\xcc\xc6\xc0\xc7\xc7\xc7\xcd\xc6\xc0\xca\xc7\xc4\xcd\xc7\xc0\xcd\xc7\xc1\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd8\xd8\xd8\xdc\xdc\xdc\xe6\xe6\xe6\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xec\xec\xec\xed\xed\xed\xee\xee\xee\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\x7f\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xbf\x80\x7f\x7f\x1b\x12\x11\x82\x87\x88\x87>8:\x10Z\x8f\x90\x91\x87\x19.\x0fU\x97USR\x9bPY\x82\x8b9\r\x98\x97S\xa5QX\x87\x17-\x0cVV/,+*(\'R\xa8\x7f>49\x0bWW,3210#RU\x87\x16)\nXX\xb2\'$ \x1fPT\x9f\xb9\tYX\xadVUQPNM\x87\x15%\x08\xd7&!\x1d\x1c\x1a\x18JK\xd37\x07XW\xd9T\xcaXP@\x87\x14"\x06\xbcWT\xa7\xf4;H\xa6\xd5 \xa0\xcc\x8a\x94\'Y\xa0\xf08\xa2\xe5\xd0\x04\x0f\x03\x94\xf5k\x12ea\x96\x86\xb7h\xd4\x10\xb0%\x8bA&D\x92p\x19y\xa8\x80\x83\x00F\x8a\x0c\t\x02D\x08\x90\x1e?l \x02\x90\xa8\xe6\x9f@\x00;'
		self.b64["report_html"] = b'GIF89a\x10\x00\x10\x00\xe7\x86\x00~1\x18\xabB!\xacC!\xaeF"\xaeI"\xa5K,\xafK#\x1e{\x03!|\x00\xb1N#\xb2Q$%\x7f\x00\xb2R%\xb4U%\xb5V&\xb7Y&1\x83\x15\xb7[&2\x86\t\xaf]53\x87\x15\xb8^\'6\x88\t\xb8_\'4\x89\x18\xbaa(<\x8b\x10D\x8f\x16F\x90\x19J\x91\x1cR\x97"W\x98(\xbexI\xb3yc[\x9b)\xb3|d\xb5\x7feb\x9e1^\x9f:c\x9f1\\\xa0<e\x9f1c\x9f8\xb5\x82f\xb7\x83g_\xa1Ch\xa25b\xa3Fk\xa37\xb9\x87gn\xa49f\xa5Hh\xa5Fo\xa5=p\xa6?\xc2\x8bdn\x9a\xdc\xbf\x8fao\x9b\xdcr\x9c\xdcq\x9d\xdd\xc1\x92ct\xabOq\x9e\xdfs\x9e\xdf\xc2\x94ds\x9f\xe0t\xa0\xe0v\xa0\xe0\xc3\x96ev\xa2\xe0|\xafUw\xa3\xe1x\xa3\xe1\xc4\x99f\xc5\x9agz\xa5\xe1\x81\xb3Z\x80\xb3a\x82\xb5g\x85\xb6f\x85\xb6j\x89\xb8k\x8e\xbao\x90\xbct\x96\xc1\x80\x97\xc2\x82\x98\xc2\x83\x9e\xc5\x88\xa1\xc6\x8a\xa1\xc7\x8a\xa0\xbe\xea\xb1\xc0\xae\xa1\xbf\xea\xa5\xc8\x8d\xa2\xc0\xea\xa3\xc0\xea\xa9\xca\x90\xa8\xcb\x90\xaa\xcb\x91\xad\xcd\x94\xb0\xce\x96\xca\xc6\xc4\xcc\xc6\xc0\xc7\xc7\xc7\xcd\xc6\xc0\xca\xc7\xc4\xcd\xc7\xc0\xcd\xc7\xc1\xcc\xcc\xcc\xca\xce\xc8\xd1\xd1\xd1\xd2\xd2\xd2\xd4\xd4\xd4\xd8\xd8\xd8\xdc\xdc\xdc\xd9\xe9\xd5\xe5\xe7\xe3\xec\xec\xec\xee\xee\xee\xed\xef\xeb\xf0\xf0\xf0\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xdd\x00\xff\xfd\xbb\x01"\x83\xc0\x83\x08\x0f\xb6Q\xc3\xe6\x02\xa1\x87\x10#\x1e\x8c\xb1\xa4\xc2\x9f\x8b\x7f\xfa\xf0\xd9\xa8g\x90\xc0\x85k"`\xbc\xd8\xa7\xe4\x1eA\x07Y(y\x00\x08\x10\x93$H\x8c\x10\x19\xc2\x07\xe5\xbf6f\xd68\x08\x14(\t\x98/]\xb6\xfc\xe0\xf3\xe7\xe0\x8a"\r\x04\t\x929\x04\xc8\x0e\x1dz\xfc|\xcc\xc9`\x90\xa0\x96\x80l\xa4\xc0\x93\xe7\xceA\x12A\x14\\\x15\xc2\x03\x87\x8a&\x1f\xea\xd8\x99\x9a&\x81\xa0\x1a2\\\x9482\xc6\x07\x077\x07G\xf40\x10\x08F\x192c\xc4P\xd1B\xc3\xc2\xd43\x04\x04\x9d 3E\n\x14\'O\xae\xa0X 0D\x8e\x01\x82D\x84\xf1\x92\x05K\x14+3(\x1c\x16P\xc8C\x87\r\x1aLTy\x81\x81\xce\xc1\x02\x13\x02\xcc\x91\x13\x07\xce\x1b\t- pA\x83\x10@\xc2\x7f\x08\x0e \x0c\x08\x00;'
		self.b64["report_word"] = b'GIF89a\x10\x00\x10\x00\xe7\x8c\x00~1\x18\xabB!\xacC!\xaeF"\xaeI"\xa5K,\xafK#\xb1N#\xb2Q$\xb2R%\xb4U%\xb5V&Rg\xc1Uf\xc4Tf\xc8\xb7Y&\xb7[&Vh\xc7\xaf]5Wj\xc8\xb8^\'Xk\xc8\xb8_\'Ym\xca\xbaa([o\xcaQt\xd1[s\xca\\v\xcc[y\xd0V{\xd0^{\xceZ}\xd3X\x7f\xd0\\\x7f\xd0g|\xcfd}\xd1T\x82\xd1f~\xd0e\x7f\xd1d\x80\xd1h\x80\xd1c\x83\xd0]\x85\xd2\xbexI\xb3ych\x85\xd3c\x88\xd0\xb3|df\x88\xd0\xb5\x7feg\x8d\xd1m\x8c\xd4\xb5\x82f\xb7\x83gi\x91\xd3s\x8e\xd5n\x90\xd4d\x94\xcbv\x8e\xd4w\x8e\xd5j\x93\xd3\xb9\x87gy\x8f\xd5i\x94\xd4z\x8f\xd5k\x94\xd3o\x93\xd5x\x92\xd6p\x95\xd6k\x97\xd3k\x98\xd3x\x95\xd6\xc2\x8bd{\x95\xd7l\x9a\xd4m\x9a\xd4h\x9d\xd5\xbf\x8fam\x9c\xd4l\x9d\xd5\xc1\x92cx\x9c\xd7\x83\x9a\xd7\xc2\x94d\xc3\x96e\xc4\x99f\xc5\x9ag\x8b\xa1\xda\x90\xa5\xdb\x93\xa5\xdb\x93\xaa\xdd\xa4\xb2\xe1\xa9\xb7\xe3\xb0\xc1\xe6\xca\xc6\xc4\xcc\xc6\xc0\xc7\xc7\xc7\xcd\xc6\xc0\xca\xc7\xc4\xcd\xc7\xc0\xcd\xc7\xc1\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd8\xd8\xd8\xdc\xdc\xdc\xd9\xdf\xf2\xda\xdf\xf2\xe9\xe9\xe9\xe6\xea\xf7\xe9\xec\xf7\xe9\xed\xf8\xed\xed\xed\xec\xef\xf8\xed\xef\xf8\xed\xef\xf9\xed\xf0\xf9\xef\xf1\xf9\xf2\xf2\xf2\xf4\xf4\xf4\xf5\xf5\xf5\xf7\xf7\xf7\xf6\xf7\xfc\xf8\xf8\xf8\xf7\xf9\xfc\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfb\xfb\xfe\xfb\xfc\xfe\xfc\xfc\xfc\xfc\xfc\xfe\xfd\xfd\xfd\xfd\xfe\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xde\x00\xff\xfdK\xc2\x02\x83\xc0\x83\x08\x0f\x9e\x19S\xc6\x02\xa2\x87\x10#\x1e\xf4q\x85\xc2\x9f\x8b\x7f\xfc\xf4\xd9\xc8\xa7\x90\xc0\x85d \xfci\xf2D\x07\x13#Bn\xccx\xd1@\xa0\r+\x0f\x02A\x11t\xa8\xa6\xcd:-\xcf|!\xb3`\xd0\x92DR\x80l\xc9\xa1\x04\x8b\x88\x96\xffjTQ@\xe8\xc8\xa1"C\xbc\xac\xc82\xa5C\xce\x9d\t\n\xf58\x84\x84\x06\x91\x10;HhA*\x83\n\x02B3\x0e\xe1(\x81"\x85\x06\x13p\xae\x8a9@(\x86!\x17\x1e\xba\x04\x01\xc1\xe5\x0eR\x18Q\x0c\x0cR\xb1\xe8\x04\x0f@?F\xcc\xd9s\x15\x0c\x01B\x1f\xe8\xe8\xc9\x83\xe7\x8e\xe58H[8\x19@\x88\xc3\x06\x06\x19.T\x98\x10\xc1Ac\x01\x8a\n\x05\xeac\xa7\x8d\x1cF\xb0\x0f\x16\x90\x10\xe0\x8d\x1b6j\xd2\xacIc\x06M\x18\x84\x00\x12\n\xff\x17\x10\x00;'

		self.b64["Abort"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\n\n\n\x14\x14\x14\x1c\x1c\x1c###---444;;;CCCLLLQMHTTT\\\\\\bbbzgAlll\x87m8tttytf{{{\x83~r\x99~B\xb0\x7f$\x83\x80x\x83\x83\x83\x9c\x85Q\x8e\x8d\x8b\xc0\x8d\x1b\xc4\x8f \x91\x91\x91\x99\x94\x8d\xdc\x96\x06\xb3\x9d^\xbb\x9fI\xf4\x9f\x00\xf9\x9f\r\xf8\xa2\x0b\xff\xa42\xfa\xa6\x10\xf5\xab\x01\xfc\xad\x00\xb8\xaf\x99\xff\xb1<\xf9\xb3\x00\xf6\xb6\x07\xff\xb7A\xce\xbb\x87\xfd\xbb\x00\xfc\xbc"\xf8\xc1\x1b\xff\xc3K\xff\xc6\x00\xfe\xc9>\xfe\xcc@\xe7\xce\x89\xeb\xd2\x8c\xfa\xd4b\xf4\xd5\x80\xf1\xd7\x8f\xfa\xdd\x8f\xff\xdd\x99\xfb\xde\x91\xfb\xe0\x91\xff\xff\x80\xff\xff\xaa\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00B\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb3\x80B\x82\x83\x84/\x84\x84=\x89;\x82/\x8d+\x87>\x89:78!/40+(\x88=.\x1a)9152*&\'\x84\x1e6;\x12\x0f ,0-%#\x1f\x84\x13\x147\x17\x05\x18\x14\'\'$\x1c\x05\x83\x13\x1d\t\x11\x0c\x03\x0f\x19\x15\x1b\x10\x16\n\x03\x82\xc3\r\x05\x04\r\x13\x0f\r\x0e\t\t\x0b\x02\x82\x0f\x1d\x13\xe2\x11\xd8\x0b\t\x08\x08\x0b\x01\x82\r\x18\xe4\xd8\x0c\xe6\x08\x07\x07\t\xebB\x0c\xe4\r\x0c\xf1\xe7\x07\x06\x06\x0e\xdcK\xd0\xa0\x819\x7f\xff\x02\x12\xb8\'\xc4\x80At\t\x0b\x04d(\x84\x9a\xb9\x84\x00\r\x04\x00ph\x80\x00\x03\x10\r\x10\x00\xc0\xf1\x90 \x01\x01R\x92<\x14\x08\x00;'

		self.b64["Aborted"] = b'GIF87a\x10\x00\x10\x00\xd5\x00\x00\x00\x00\x00\x1b\x1b\x1c\'\'((\'(112=<=FEFGFHOMOUSU[Z[_^``_adbdigiljmompqoqtrt{z|\x7f}\x80\x80~\x81\x85\x83\x85\x89\x87\x8a\x8c\x8a\x8d\x8f\x8d\x90\x90\x8e\x91\x94\x92\x95\x97\x95\x98\x99\x96\x99\x9c\x9a\x9d\xa0\x9e\xa1\xa3\xa1\xa4\xa7\xa5\xa8\xa9\xa6\xaa\xad\xaa\xae\xb1\xae\xb1\xb5\xb3\xb6\xb8\xb6\xb9\xbb\xb9\xbc\xc4\xc2\xc5\xc8\xc6\xc9\xcc\xca\xcd\xd1\xcf\xd2\xd6\xd4\xd7\xd7\xd4\xd8\xd9\xd6\xda\xdc\xd9\xdd\xe0\xdd\xe1\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\n\x002\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06\x98@\x99pH,\x1aA"\x10\xe8\xd31\x0eK/\xd8\xcb\xe5Z\x81\x9c\xa4\x97\xcaT"\x89L\xaaM1\x9b\xea\x8eB \xcf\x08\x85\x19zX\xa8\xd1(\xe9\xe9l0\x9eRC\xd8i\x89\xd0uw\x17\x16\x13%\x0bB\x1a*iv\x18\x83\x14\x13\x12#\tB\x17)\x1c\x82\x16\x15\x90\x11\x0f \x07B\x15l\x8e\x90\x12\x0f\x0e\x0b \x05B\x12\'\x1e\x13\xa4\xa6\r\n\x12\x1e\x01C\x85\x18\x0f\xb1\x0c\t\x11\x1e\x08E\x10#\x15\x0c\x0b\n\x08\x0e\x1d\x06N\r\x1f\x1f\x1e\x1b\x1b\x19\xcbN2\x03\x04\x02\x01\x01\x00\xd5\xddDA\x00;'

		# files["AddRow"] = "../famfamfam_silk_icons/icons/add.gif"
		self.b64["AddRow"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00,|\x1d+~"&\x80\x1e/\x81)0\x81\'3\x83)8\x87.=\x8a2A\x8e5E\x8f9K\x92?Q\x95CN\x9a>U\x9bE]\x9dLb\xa0Me\xa2Ri\xa5Zh\xa6Vj\xabVl\xab[f\xacRu\xacat\xad_z\xb2d~\xb3h\x83\xb5kn\xb6V\x88\xb8op\xb9W\x87\xbaqt\xbb\\}\xbbk\x8a\xbcr}\xbde\x8b\xbfzp\xc2by\xc2c\x8d\xc3{|\xc4i\x92\xc6\x80~\xc8o\x89\xc9\x7f\x86\xcbz\x99\xcc\x86\x81\xcdu\x8d\xcd\x83\x99\xcd\x8a\x93\xce\x88\xa5\xcf\x94\x8a\xd0}\xa7\xd1\x97\x8e\xd3\x83\x99\xd4\x8b\x96\xd5\x8a\xac\xd5\x9e\x9e\xd9\x92\xa1\xda\x97\xb5\xda\xa6\xb8\xdb\xab\xa6\xdc\x9c\xb5\xdd\xaa\xbb\xde\xb0\xb0\xe0\xa7\xb6\xe0\xad\xbc\xe3\xb5\xcc\xe6\xc4\xc6\xe8\xc1\xcf\xe9\xca\xd5\xeb\xd0\xd8\xee\xd3\xdd\xf1\xd9\xe1\xf2\xdd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00K\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb1\x80K\x82\x83\x84\x85\x86"\x1b\x1b\x19\x17\x17\x86\x82"\x1f2CFE?!\x13\x11\x85\x90?IB=:@D\'\x0f\x0f\x84\x1f<H91/775B!\x0e\x83\x1d-G:7+JJ,(*A\x0e\x0b\x82\x1b>@/,!\xba\x15  6)\n\x82\x1aB6,\xba\xd5J\x1e(8\x08\x82\x19>3.\xd6\xba\x1e#\xda\x82\x1807(%\x16\xe2\x1e -$\x06\x82\x15\x16>&\xcb\xe2\x1c ;\t\xf2\x82\x11!|,\xf3\xc0A\xdf\x8e\n\xfe\x04Ax\xd0\xad\xc5\x88\x11-vP( \xa0\x90\x03\x06\rN\xd0\xa0A\x02\x01EGK\x14$@p\xc0\x00\x01\x90(\t\x05\x02\x00;'

		# files["AddRow"] = "../famfamfam_silk_icons/icons/script_add.gif"
		# self.b64["AddRow"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x003Y\x8c+Z\x90/`\x935`\x962e\x9a>h\x9b5i\x9f3j\x125k\x1b9m\xa6?oW<p\x1b@s\xa6@s\xacDw\xb3Fw\'J{,D\x82\xb8V\x84BI\x85\xbaW\x85\xb5R\x86\xb9D\x88\xbbI\x88\xbe_\x8aHQ\x8c"L\x8e\xc6S\x8e\xc4U\x8e\xaae\x8eMU\x8f(W\x8f\xd5Y\x8f\xccl\x90\xb9\\\x92\xd7O\x94\xcbS\x95\xcab\x97\xd9f\x99\xccs\x99_T\x9b\xd1l\x9e\xd9q\x9e\xd3V\xa1\xd7p\xa1\xe1\\\xa5\xdc\x85\xa5\xc8{\xa6\xda^\xa9\xdf\x81\xac`^\xad\xe2`\xad\xe4\x8c\xaf\xd6g\xb1\xe5l\xb3\xe6\x98\xb3\x88\x94\xb6\xa6w\xb8\xe8\x87\xb9\xe0\x87\xbb_\x9b\xbb\xad\xa4\xbb\xd7\x8d\xbcd\x8f\xbci\x81\xbd\xea\x8c\xc1\xea\x9b\xc7\xeb\xb4\xc7\xe0\xa3\xc8\xf7\xa7\xcc\xea\xae\xd0\xf7\xb3\xd1\xed\xb3\xd4\x94\xb7\xd5\x9d\xc4\xd5\xe7\xb6\xd6\xf9\xc2\xda\xee\xc2\xdb\xf2\xbe\xdc\xf9\xc2\xdd\xf9\xc7\xe0\xf5\xd4\xe0\xee\xcb\xe2\xfa\xd3\xe5\xfa\xd1\xe6\xbb\xd9\xe7\xf5\xd6\xe9\xfc\xda\xea\xfc\xe3\xea\xf5\xe2\xee\xfc\xe5\xf0\xfd\xed\xf3\xfc\xf0\xf6\xfe\xf6\xfa\xfd\x00\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00a\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xce\x80a\x823A:763\x89\x8943\x82a1B`\x92`^\\XTQF1.\x82.C`Z[\\\\^^\x92^N\x9ca,F`WXX\xa1[[`-`;\x82)H]SSTT\xafX`+M)\x82%NZP\xcb\xbd\xbe`!$$\x82\x1bVTOO\xcb\xcc`%\x8ea\x18\xbc\xd8\xd9PS`\x1c\xdd\x14^\xe2\xd9S^\x12\xdd\x16`\xeaP=(\x1e\x13\x10\x8e\xf0\xea92IU@\x1f\x10\x84QPcK\x91#L\xb0eH\x92\x04\xcc\x8f\x1f\x08\x0e\x1c\xa8\x00C\x85\n\x13#@DP2)\t\x82\x02/&\x9d\xea\xc2\xe0\x07\x0f0< \x0e\x10\xe1\x83\xc8\x12)YH\xe1\xd0\xf0#\xc9\x0f\r\x02\x05\xe8\xdc)\x80\x80\x81\x05\t\x10\x08\r\x13\x08\x00;'


		self.b64["Script"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x003Y\x8c,Z\x91,]\x8e/`\x935`\x962e\x994g\xa0>h\x9b5i\x9f9n\xa6@s\xa6@s\xacMt\xa4=u\xaaDw\xb3@{\xb2D\x82\xb8^\x82\xaeI\x85\xbaW\x85\xb5R\x86\xb9D\x88\xbbI\x88\xbeL\x8e\xc6S\x8e\xc4U\x8e\xaaV\x8f\xd5Y\x8f\xccl\x90\xb9\\\x92\xd7O\x94\xcbS\x95\xcab\x97\xd9f\x99\xccT\x9b\xd1h\x9e\xe3l\x9e\xd9q\x9e\xd3\x80\x9e\xc2V\xa1\xd7p\xa1\xe1\\\xa5\xdc\x85\xa5\xc8{\xa6\xda^\xa9\xdf^\xad\xe2`\xad\xe4\x86\xaf\xe5\x8c\xaf\xd6\x96\xb0\xcfg\xb1\xe5l\xb3\xe6w\xb8\xe8\x87\xb9\xe0\xa4\xbb\xd7\xa3\xbc\xd9\x81\xbd\xea\x8c\xc1\xea\x9b\xc7\xeb\xb4\xc7\xe0\xa3\xc8\xf7\xa7\xcc\xea\xbb\xcf\xe3\xae\xd0\xf7\xb3\xd1\xed\xc4\xd5\xe7\xb6\xd6\xf9\xc2\xda\xee\xc2\xdb\xf2\xbe\xdc\xf9\xc2\xdd\xf9\xce\xdd\xec\xc7\xe0\xf5\xd4\xe0\xee\xc7\xe2\xfa\xcb\xe2\xfa\xd3\xe5\xfa\xd9\xe7\xf5\xd6\xe9\xfc\xdb\xea\xfc\xe3\xec\xf5\xe2\xed\xfc\xe5\xf0\xfd\xec\xf4\xfc\xf1\xf6\xfe\xf6\xfa\xfd\x00\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00Y\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc4\x80Y\x82.9543.\x89\x89/.\x82Y-:X\x92XVTPMI>-*\x82*;XRSTTVV\x92VE\x9cY(>XOPP\xa1SSX)X6\x82#AULLMM\xafPX&D#\x82 ERG\xcb\xbd\xbeX\x1c\x1f\x1f\x82\x18NMFF\xcb\xccX \x8eY\x17\xbc\xd8\xd9GLX\x19\xdd\x13V\xe2\xd9LV\x11\xdd\x15X\xea\xcbMQ\x10\xef\xf1\xf2PH\x0e\x8e\n1S=\x80\x0c\xc1\xb6\x84\t\x95\x1f\n\x04%H@\x81E\x89\x12!<l\xd8@\xa2\t\x8e\x03\x82\x0c\xac\x98t\xaaJ\x15\x18Pd\x18\x10D\xa0\xc3\r\x1eB\x94D!\x05J\xca\t\x01\x8e\x04\xc8\x9c)\xa0\x00\x82\x06\x12`\n\n\x04\x00;'

		# files["Delete"] = "../famfamfam_silk_icons/icons/bin_empty.gif"
		# self.b64["Delete"] =b'GIF87a\x10\x00\x10\x00\xc4\x00\x00\x00\x00\x00___dddmmmssszzz\x83\x83\x83\x8d\x8d\x8d\x93\x93\x93\x9b\x9b\x9b\xa3\xa3\xa3\xab\xab\xab\xb5\xb5\xb5\xb9\xb9\xb9\xc4\xc4\xc4\xcd\xcd\xcd\xd3\xd3\xd3\xdb\xdb\xdb\xe4\xe4\xe4\xec\xec\xec\xf3\xf3\xf3\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00\x16\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x05\x8a\xa0%\x8edi\x9e\xa88\x1c\xc8\xc1\x1e\xc3I\x1c\x8f\x14A\xd1c\xc4\xa5!Q\x13\tD2y\x14J\x0b\xc6\x82x\x8bHZ\xa3\xc5B\xa1hL\xa7T\x87A\xb4\x88L(\x12\xe5c\xec`0\x8e\x0bG\xf0;Q\xe6 \x89\xb3Ea\x8b8\'\x13\xc3;N\x98K\x1c\x108?\x05\x0e\x0f\x10\x08\x0c1\t^V\x0f\x11\x14\x04\x85\x10\x07\x89\x16\x88`v\x8f\x03\x10\x86\x07\r\x02"\x94@\x12a\x08\xa47\n\xa0"\x05]7\x02\x04\x04\x03\x02\xb3%\xb1\xb3\x01(!\x00;'

		# files["Delete"] = "../famfamfam_silk_icons/icons/cross.gif"
		self.b64["Delete"] = b'GIF87a\x10\x00\x10\x00\xd5\x00\x00\x00\x00\x00\xe4\x14\x18\xe3\x1a\x1e\xdf  \xdf @\xe7%&\xea)+\xe7**\xe9.1\xec34\xff33\xed;=\xf1<>\xef?B\xdf@@\xefCE\xefCK\xf1CE\xf4EH\xf4KM\xf3LQ\xffSV\xf6TV\xf6UZ\xffVZ\xf5Z\\\xfa]^\xf7^`\xf8^b\xff`\x80\xfcbd\xf9gi\xfbjm\xfdmp\xfert\xffwy\xffz}\xff~\x81\xff\x81\x82\xff\x87\x8a\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00)\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06t\xc0\x94pH,\x1a\x8f\x1a\xe3hd\xf4|(\xc4Q\xa9$"r@$\xcec("\x9dH \xe1\x95\xb4\x89\x14A"\x93\xc8\x93\xc1f\xb6\xcdP\x89D\x1a\xbd\x8f\xc2\x0cI\x83\x115\xf0y#\x15\x15"fx\x19\x1e""! \x16\x0bG\x17\x89\x17\r\x0b\x13\x1e\x13\tE\x91"\x8eB\x08\x11\x1e\x12\x06C\x13\x16\x1e\x9dC\x05\x0c\x13\x06\x01C\x10\x13\x8fE\x02\xadE\xb2F\xae\x80\x80A\x00;'

		self.b64["Advanced"] = b'GIF87a\x10\x00\x10\x00\xc4\x00\x00\x00\x00\x00GGGMMMTTT[[[ccclllpppyyy\x82\x82\x82\x8d\x8d\x8d\x94\x94\x94\x9c\x9c\x9c\xa5\xa5\xa5\xac\xac\xac\xb4\xb4\xb4\xbc\xbc\xbc\xc4\xc4\xc4\xcb\xcb\xcb\xd4\xd4\xd4\xdc\xdc\xdc\xe5\xe5\xe5\xeb\xeb\xeb\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00\x18\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x05\x91 &\x8e\x92\x14Ac\xaaFU\xe5\xa8\xe3Tb\x11E=\x98\xd341eQ\xa7\xc9\xe4\xe1\x90T \n\x91\x892\xb1\t\x99%\xc4a\x14\x91I \x8cFd\x8bTn)\xd7\x04"\xa1\xd8J\x14\x89D\xc4bm$D\x0c\xc7\xa9f`M"\x92\xc7B\xb4\x90C\xaa\x05\r\x0b\rw\x12\x0c\x0c\x0be\x10\x10\x05\x03\x03"rf\x0e~D\x06#:\x85V&\x10\x12\x06\x05"\r\x10\x14nj\x11\x06\x06\x84\t\x8f"\t\x9e\x18\t%\x9f\x03\x02\x010\xac\x10\x0f\x04\xb6*\x06\xb3\xab)!\x00;'

		# png's
		# b64["New"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAC4SURBVCjPdZFbDsIgEEWnrsMm7oGGfZro\nhxvU+Iq1TyjU60Bf1pac4Yc5YS4ZAtGWBMk/drQBOVwJlZrWYkLhsB8UV9K0BUrPGy9cWbng2CtE\nEUmLGppPjRwpbixUKHBiZRS0p+ZGhvs4irNEvWD8heHpbsyDXznPhYFOyTjJc13olIqzZCHBouE0\nFRMUjA+s1gTjaRgVFpqRwC8mfoXPPEVPS7LbRaJL2y7bOifRCTEli3U7BMWgLzKlW/CuebZPAAAA\nAElFTkSuQmCC\n"""
		# b64["Save"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAH+SURBVBgZBcE9i11VGAbQtc/sO0OCkqhg\nhEREAwpWAWUg8aMVf4KFaJEqQtAipTZWViKiCGOh2Ap2gmJhlSIWFsFOxUK0EsUM3pl79n4f12qH\nb3z3Fh7D83gC95GOJsDe0ixLk5Qq/+xv/Lw9Xd+78/HLX3Y8fXTr2nWapy4eCFKxG7Fby97SnDlY\ntMbxthyfzHO//nl85fNvfvnk8MbX5xa8IHx1518Vkrj54Q+qQms2vVmWZjdiu5ZR2rT01166/NCZ\ng/2PFjwSVMU6yjoC1oq+x6Y3VbHdlXWExPd379nf7Nmejv2Os6OC2O4KLK0RNn3RNCdr2Z5GJSpU\n4o+/TkhaJ30mEk5HwNuvX7Hpi76wzvjvtIwqVUSkyjqmpHS0mki8+9mPWmuWxqYvGkbFGCUAOH/+\nQevYI9GFSqmaHr5wkUYTAlGhqiRRiaqiNes6SOkwJwnQEqBRRRJEgkRLJGVdm6R0GLMQENE0Ekmk\nSkQSVVMqopyuIaUTs0J455VLAAAAAODW0U/GiKT0pTWziEj44PZ1AAAAcPPqkTmH3QiJrlEVDXDt\n0qsAAAAAapa5BqUnyaw0Am7//gUAAAB49tEXzTmtM5KkV/y2G/X4M5fPao03n/sUAAAAwIX7y5yB\nv9vhjW/fT/IkuSp5gJKElKRISYoUiSRIyD1tufs/IXxui20QsKIAAAAASUVORK5CYII=\n"""
		# b64["SaveAs"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAJFSURBVDjLpZPNS1RhFMZ/5733zkzjR/ZB\nCUpoJdUiBCkll4m0CUKJIGpVSLjyL2gntDFop6shAolWbcSNIW0ircHBUHCloo3VjNY0jjP3831b\nWA5ai8Bnfc7vPOfhHDHGcBjZAENji7N1cSj7IcdqY2zkKoiC2qSFNsKPYoXpTPbBynj/4j8BlbLL\n9c4L3OqoZWLmM4/vXdpX9OJtHq0lBXQdBIgxhvtPZmZ7ui+yspZrjwKfWExxtMbh66YLAgj4geZn\nyd2YzmT7Vsb75/c5UEqwDLgVl55r57hxuYY3c18Y6mtDgO1KSBBETMwV0VpeA2f3ARKOwvUCcgWX\n9bzH0NhqvC4Okx9zBzNpPdGQ4OHIrJnOZLtWxvs/2AChNnhRiFIKy8j/ZjILiALYLgc4YnO8zsJS\nIWUv4Pt2CMBU+tteoxtC0YN8wUdEV1eItMHCIdSagru5l0kQaZ4OdqC1wQAWhqQNnudR3PGrANu2\naGmE9FJATSxJwinhegHDr1ZRAmGk0ZHGAMYYMJB0dh0ogOVs6VNqcoGtosYv1+9lYikHERvBQsQC\nozBGCMIQ3w+rDtKjvQMAd4bfL59vFqYzQasjNoM36wi1vzvHgBFNwo4x8nKNreJOFfBHy9nSXGpy\noSPSYOGgqZCae8TJ5BkERb68zsDVZygSlD3/b0B6tPf2byempRFO127T095JQ6wJFBTcJk7VhCRj\nYItUT/mgrgxOvWtrPtLdEG8gYdcT6gDRGjERWsosrS2TKwbMP78rcth3/gX/0SEvLZFG1QAAAABJ\nRU5ErkJggg==\n"""
		# b64["Open"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAI5SURBVBgZpcE9SFVhAMfh33vue49X85ih\n1tUI0cXbF7QkCA5BQVAtbU3VUC3O0dbHWHNQUxE0NQYREUU0BoHUYB9qVJRdLe/V+6HnnPe8/4xu\n5NIQPo+RxEbYdw/2Txa6du0yJuAvEddmPmeuOgbErGf4pTFy7LVjjTUKSjvGb+eNMSDWCIzBrX4f\nLk9e+SwQLbmwS8rS+frc0/PAPdZYnFbxSVv87QZZkoOgC2MiCgMHGRi9GiIBHuQBYYLO4vv74xeB\ne6yxpCaQT8iSEHnhVz6RNsrU55+RL/SDUvAJkgMcUelCiPwgLRajgncrJE1Q0iCtLROVTlHo2QkY\nQIAHCRDGdkMWWFosaYBt30r3zjOABwnh8ckXXPUJ04u9fFgeZGGlSHtbnp5NdQbcFkOLJZWUreKb\nr1C2hLIaclV8WmG6UuRjeoDSUCd78jnmlxIqtZjZztN2N78FxEje4dMFfLKAT8r4pIzSBabqBxne\n1kElNswtZziTY/vWiObmsRwtlkQyZMgtIldFroqyJeSWqK8khGEeFzu8IHaiYHM4Wf6wSnzFNX90\npPUwwkeBlAcfgXrpaMuTpBlpBs6LX2Sg2Wjwh9VqfG325vFRxCEMEetEI8P5WvFILmoPiTNhA8Pc\nYop+vNWjSxOnDl95fMdI4l+uP/w41GY5uaUzvOwFy43Yu/KUGe/7ahozz2uzUy/PGUn8j/uXj54t\n9hev9Q3t637z4mHTSOJ/3Z0onegf3nvLe9duJLERPwFUpzZM2BWatgAAAABJRU5ErkJggg==\n"""
		# b64["Play"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAEdSURBVDjLY/j//z8DJZiB6gY0rH7xpW7l\ni3YKDHj1v2bli38lix61k2VA5fJn/9eeeP+/fcOL/wlT7/aRbEDegkf/Vxx/93/xobf/S5c8/u/e\ncm0eSQYkTX/4f+HBN/8nbX/xf+bul/8Tp9/9r1N0dgnRBgT33QZqfPW/YdXj/42rH//v2vjkv3fH\ntf9SScceEWWAc8u1/xO2Pv9fsvjB//IlD4CGPPrvXH/5v2Tksc1EGWBaful/+/on/4sW3gfGxsP/\n9lUX/ksEH1gj6rqdhSgDlPPO/q9b8fB/5bIH/23LL/wXD9i7kqRAlEo6+b908f3/NiXn/4t57V1E\ncjRKRB75b1145r+o684FZCUkMb8D/0Uct88euMxEKgYA7Ojrv4CgE7EAAAAASUVORK5CYII=\n"""
		# b64["Stop"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAJOSURBVDjLpZI9T1RBFIaf3buAoBgJ8rl6\nQVBJVNDCShMLOhBj6T+wNUaDjY0WmpBIgYpAjL/AShJ+gVYYYRPIony5IETkQxZ2770zc2fGYpfl\nQy2MJzk5J5M5z/vO5ESstfxPxA4erL4Zuh4pLnoaiUZdq7XAGKzRJVbIBZ3JPLJaD9c/eCj/CFgZ\nfNl5qK5q8EhTXdxxLKgQjAFr0NK0ppOpt9n51D2gd2cmsvOElVcvOoprKvuPtriNzsY8rH+H0ECo\nQEg4WklY1czP8akZby51p6G3b6QAWBl43llSVTlUfuZE3NmYh9Vl0HkHSuVq4ENFNWFdC+uJ5JI/\n9/V2Y//rkShA1HF6yk/VxJ0f07CcgkCB7+fSC8Dzcy7mp4l9/khlUzwecaI9hT+wRrsOISylcsph\nCFLl1RXIvBMpYDZJrKYRjHELACNEgC/KCQQofWBQ5nuV64UAP8AEfrDrQEiLlJD18+p7BguwfAoB\nUmKEsLsAGZSiFWxtgWWP4gGAkuB5YDRWylKAKIDJZBa1H8Kx47C1Cdls7qLnQTZffQ+20lB7EiU1\nent7sQBQ6+vdq2PJ5dC9ABW1sJnOQbL5Qc/HpNOYehf/4lW+jY4vh2tr3fsWafrWzRtlDW5f9aVz\njUVj72FmCqzBypBQCKzbjLp8jZUPo7OZyYm7bYkvw/sAAFMd7V3lp5sGqs+fjRcZhVYKY0xupwys\nfpogk0jcb5ucffbbKu9Esv1Kl1N2+Ekk5rg2DIXRmog1Jdr3F/Tm5mO0edc6MSP/CvjX+AV0DoH1\nZ+D54gAAAABJRU5ErkJggg==\n"""
		#
		#
		if icontext in self.b64:
			self.imgdata[icontext] = tk.PhotoImage(data=self.b64[icontext])
			base.debugmsg(9, "self.imgdata[icontext]:", self.imgdata[icontext])
			return self.imgdata[icontext]

	def BuildUI(self):
		p = None
		r = None
		a = None

		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		self.bind("<Configure>", self.save_window_size)

		base.debugmsg(6, "self.tabs")
		# this removes a lot of wasted space and gives it back to the data in each tab
		#   I tried a value of 0, but it needed something, so 5 worked nicely, I think
		# 	the system default is ~20 on macos 11
		self.tabs = ttk.Notebook(self, padding=5)
		# self.tabs = ttk.Notebook(self)
		base.debugmsg(5, "self.tabs", self.tabs)
		# base.debugmsg(5, "self.tabs", self.tabs["background"])

		base.debugmsg(6, "p")
		p = ttk.Frame(self.tabs)   # first page, which would get widgets gridded into it
		p.grid(row=0, column=0, sticky="nsew")
		# p.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
		base.debugmsg(6, "r")
		r = ttk.Frame(self.tabs)   # second page
		r.grid(row=0, column=0, sticky="nsew")
		base.debugmsg(6, "a")
		a = ttk.Frame(self.tabs)   # 3rd page
		a.grid(row=0, column=0, sticky="nsew")
		self.tabs.add(p, text='Plan')
		self.tabs.add(r, text='Run')
		self.tabs.add(a, text='Agents')
		self.tabs.grid(column=0, row=0, sticky="nsew")
		# self.tabs.grid(column=0, row=0, padx=0, pady=0, sticky="nsew")

		self.ConfigureStyle()


		base.debugmsg(6, "BuildMenu")
		self.BuildMenu()

		base.debugmsg(6, "BuildPlan")
		self.BuildPlan(p)
		base.debugmsg(6, "BuildRun")
		self.BuildRun(r)
		base.debugmsg(6, "BuildAgent")
		self.BuildAgent(a)




	def BuildMenu(self):
		# creating a root menu to insert all the sub menus
		window = self.master
		root_menu = tk.Menu(window)
		window.config(menu = root_menu)

			# sub_menu.add_command(label="Print", command=self.print_, accelerator="Command-P")
			# https://stackoverflow.com/questions/16847584/how-do-i-get-the-mac-command-symbol-in-a-tkinter-menu

		# creating sub menus in the root menu
		file_menu = tk.Menu(root_menu) # it intializes a new su menu in the root menu
		root_menu.add_cascade(label = "File", menu = file_menu) # it creates the name of the sub menu

		accelkey = "Ctrl"
		if sys.platform.startswith('darwin'):
			accelkey = "Command"

		file_menu.add_command(label = "New", command = self.mnu_file_New, accelerator="{}-n".format(accelkey)) # it adds a option to the sub menu 'command' parameter is used to do some action
		window.bind('n', self.mnu_file_New)
		file_menu.add_command(label = "Open", command = self.mnu_file_Open, accelerator="{}-o".format(accelkey))
		window.bind('o', self.mnu_file_Open)
		file_menu.add_command(label = "Save", command = self.mnu_file_Save, accelerator="{}-s".format(accelkey))
		window.bind('s', self.mnu_file_Save)
		file_menu.add_command(label = "Save As", command = self.mnu_file_SaveAs, accelerator="{}-a".format(accelkey))
		window.bind('a', self.mnu_file_SaveAs)
		file_menu.add_command(label = "Close", command = self.mnu_file_Close, accelerator="{}-l".format(accelkey))
		window.bind('l', self.mnu_file_Close)

		file_menu.add_separator() # it adds a line after the 'Open files' option
		# if sys.platform.startswith('darwin'):
		# 	file_menu.add_command(label = "Quit", command = self.on_closing, accelerator="Command-q")
		# 	window.bind('q', self.on_closing)  # This doesn't work yet, the mac python overrides it ?
		# else:
		file_menu.add_command(label = "Exit", command = self.on_closing, accelerator="{}-x".format(accelkey))
		window.bind('x', self.on_closing)

		# creting another sub menu
		run_menu = tk.Menu(root_menu)
		root_menu.add_cascade(label = "Run", menu = run_menu)
		run_menu.add_command(label = "Play", command = self.ClickPlay, accelerator="{}-p".format(accelkey))
		window.bind('p', self.ClickPlay)
		run_menu.add_command(label = "Stop", command = self.ClickStop, accelerator="{}-t".format(accelkey))
		window.bind('t', self.ClickStop)


		window.protocol("WM_DELETE_WINDOW", self.on_closing)
		window.protocol("WM_QUERYENDSESSION", self.on_closing)
		window.protocol("WM_ENDSESSION", self.on_closing)
		window.protocol("WM_QUIT", self.on_closing)
		window.protocol("WM_DESTROY", self.on_closing)
		window.protocol("WM_CLOSE", self.on_closing)
		window.protocol("CTRL_SHUTDOWN_EVENT", self.on_closing)
		window.protocol("HWND_MESSAGE", self.on_closing)

		signal.signal(signal.SIGTERM, self.on_closing)

	def save_window_size(self, event):
		base.debugmsg(6, "save_window_size")
		try:
			base.debugmsg(6, "winfo_width:", self.winfo_width(), "	winfo_height:",self.winfo_height())
			base.config['GUI']['win_width'] = str(self.winfo_width())
			base.config['GUI']['win_height'] = str(self.winfo_height())
			base.saveini()
		except e:
			base.debugmsg(6, "save_window_size except:", e)
			return False

	def ConfigureStyle(self):

		# we really only seem to need this for MacOS 11 and up for now
		# base.debugmsg(5, "sys.platform", sys.platform)
		# base.debugmsg(5, "platform.system", platform.system())
		# base.debugmsg(5, "platform.release", platform.release())
		# base.debugmsg(5, "platform.mac_ver", platform.mac_ver())

		if sys.platform.startswith('darwin'):
			release, _, machine = platform.mac_ver()
			split_ver = release.split('.')
			if int(split_ver[0]) > 10:
				# Theme settings for ttk
				style = ttk.Style()
				# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-style-layer.html
				# base.debugmsg(5, "style.layout", style.layout)
				# # list = style.layout()
				# # base.debugmsg(5, "list", list)
				# base.debugmsg(5, "style.element_names", style.element_names)
				# list = style.element_names()
				# base.debugmsg(5, "list", list)
				# base.debugmsg(5, "style.theme_names", style.theme_names)
				# list = style.theme_names()
				# base.debugmsg(5, "list", list)


				# style.layout("rfsinput", style.layout('TEntry'))
				# style.configure("rfsinput", **style.configure('TEntry'))
				# style.map("rfsinput", **style.map('TEntry'))
				# style.map("rfsinput",
				#     fieldbackground=[(['!invalid','!disabled'], '#fff'),
				#                      (['!invalid','disabled'], '#aaa')]
				# )
				# style.map("rfsinput",
				#     fieldbackground=[(['!invalid','!disabled'], '#fff'),
				#                      (['!invalid','disabled'], '#aaa'),
				#                      (['invalid','!disabled'], '#ff4040'),
				#                      (['invalid','disabled'], '#ffc0c0')]
				# )
				# style.configure("rfs.Entry", foreground="black")
				# style.configure("rfs.Entry", foreground="systemControlTextColor")
				# style.configure("rfs.Entry", foreground=self.rootBackground)	# systemWindowBackgroundColor
				# base.debugmsg(5, "self.rootBackground", self.rootBackground)
				# style.configure("rfs.Entry", foreground=self.rootBackground)	# systemControlTextColor

				# style.configure("rfs.Entry", foreground="systemControlAccentColor")
				# style.configure("rfs.Entry", foreground="systemControlTextColor")
				# style.configure("rfs.Entry", foreground="systemDisabledControlTextColor")
				# style.configure("rfs.Entry", foreground="systemLabelColor")
				# style.configure("rfs.Entry", foreground="systemLinkColor")
				# style.configure("rfsinput", foreground="systemPlaceholderTextColor")
				# style.configure("rfs.Entry", foreground="systemSelectedTextBackgroundColor")
				# style.configure("rfs.Entry", foreground="systemSelectedTextColor")
				# style.configure("rfs.Entry", foreground="systemSeparatorColor")
				# style.configure("rfs.Entry", foreground="systemTextBackgroundColor")
				# style.configure("rfs.Entry", foreground="systemTextColor")

				# style.layout("rfsinput", style.layout('TLabel'))
				# style.configure("rfsinput", **style.configure('TLabel'))
				# style.map("rfsinput", **style.map('TLabel'))
				# style.configure("TLabel", foreground="systemPlaceholderTextColor")
				style.configure("TLabel", foreground="#000")
				style.configure("TEntry", foreground="systemPlaceholderTextColor")
				# style.configure("TButton", foreground="systemPlaceholderTextColor")
				style.configure("TButton", foreground="#000")
				# style.configure("TCombobox", foreground="systemPlaceholderTextColor")
				# style.configure("TCombobox", foreground="#000")
				# style.configure("TComboBox", foreground="#000")
				# style.configure("Combobox", foreground="#000")
				# style.configure("ComboBox", foreground="#000")
				#
				# style.configure("OptionMenu", foreground="#000")
				# style.configure("TOptionMenu", foreground="#000")
				# style.configure("Optionmenu", foreground="#000")
				# style.configure("TOptionmenu", foreground="#000")

				# style.configure("Menubutton", foreground="#000")
				style.configure("TMenubutton", foreground="#000")

				# self.rfstheme["default"] = "systemPlaceholderTextColor"
				# self.rfstheme["default"] = "#000"

				# style.configure("Canvas", foreground="#000")
				style.configure("Canvas", fill="#000")
				style.configure("Canvas", activefill="#000")

				# style.configure("Spinbox", foreground="#000")
				style.configure("TSpinbox", foreground="#000")


	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Plan
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildPlan(self, p):

		base.debugmsg(6, "config")

		base.debugmsg(6, "updateTitle")
		self.updateTitle()





		planrow = 0
		p.columnconfigure(planrow, weight=1)
		p.rowconfigure(planrow, weight=0) # weight=0 means don't resize with other grid rows / keep a fixed size
		# Button Bar
		base.debugmsg(6, "Button Bar")

		bbar = ttk.Frame(p)
		bbar.grid(column=0, row=planrow, sticky="nsew")
		bbargrid = ttk.Frame(bbar)
		bbargrid.grid(row=0, column=0, sticky="nsew")

		# new
		base.debugmsg(7, "Button New")
		btnno = 0
		icontext = "New"
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		self.iconew = self.get_icon(icontext)
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		base.debugmsg(9, "self.imgdata:[",icontext,"]", self.imgdata[icontext])
		bnew = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', command=self.mnu_file_New)
		# bnew = ttk.Button(bbargrid, image=self.iconew, padding='3 3 3 3', command=self.mnu_file_New)
		# bnew = ttk.Button(bbargrid, text="New", command=self.mnu_file_New)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# open
		base.debugmsg(7, "Button Open")
		btnno += 1

		icontext = "Open"
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		self.icoopen = self.get_icon(icontext)
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		base.debugmsg(9, "self.imgdata:[",icontext,"]", self.imgdata[icontext])
		bopen = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', command=self.mnu_file_Open)
		# self.icoopen = self.get_icon("Open")
		# bopen = ttk.Button(bbargrid, image=self.icoopen, padding='3 3 3 3', command=self.mnu_file_Open)
		# bopen = ttk.Button(bbargrid, text="Open", command=self.mnu_file_Open)
		bopen.grid(column=btnno, row=0, sticky="nsew")

		# save
		base.debugmsg(7, "Button Save")
		btnno += 1
		icontext = "Save"
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		self.icoSave = self.get_icon(icontext)
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		base.debugmsg(9, "self.imgdata:[",icontext,"]", self.imgdata[icontext])
		bSave = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', command=self.mnu_file_Save)
		# bSave = ttk.Button(bbargrid, image=self.icoSave, padding='3 3 3 3', command=self.mnu_file_Save)
		# bSave = ttk.Button(bbargrid, text="Save", command=self.mnu_file_Save)
		bSave.grid(column=btnno, row=0, sticky="nsew")

		# play
		base.debugmsg(7, "Button Play")
		btnno += 1
		icontext = "Play"
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		self.icoPlay = self.get_icon(icontext)
		base.debugmsg(9, "self.imgdata:", self.imgdata)
		base.debugmsg(9, "self.imgdata:[",icontext,"]", self.imgdata[icontext])
		bPlay = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', text="Play", command=self.ClickPlay)
		# bPlay = ttk.Button(bbargrid, image=self.icoPlay, padding='3 3 3 3', command=self.ClickPlay)
		# bPlay = ttk.Button(bbargrid, text="Play", command=self.ClickPlay)
		bPlay.grid(column=btnno, row=0, sticky="nsew")




		planrow += 1
		# p.columnconfigure(0, weight=1)
		p.rowconfigure(planrow, weight=1)
		# Plan Graph
		base.debugmsg(6, "Plan Graph")

		# defaultcolour = self.rfstheme["default"]

		self.pln_graph = tk.Canvas(p)
		# self.pln_graph = tk.Canvas(p, fill="#000")
		# self.pln_graph = tk.Canvas(p, selectforeground="#000")
		self.pln_graph.grid(column=0, row=planrow, sticky="nsew") # sticky="wens"

		# self.pln_graph.columnconfigure(0, weight=1)
		# self.pln_graph.rowconfigure(0, weight=1)

		self.pln_graph.bind("<Configure>", self.CanvasResize)




		planrow += 1
		# p.columnconfigure(0, weight=1)
		p.rowconfigure(planrow, weight=1)
		# Plan scripts
		base.debugmsg(6, "Plan scripts")


		# # 2020-12-27 try again
		sg = tk.Frame(p)
		sg.grid(row=planrow, column=0, pady=(0, 0), sticky='news')
		sg.grid_rowconfigure(0, weight=1)
		sg.grid_columnconfigure(0, weight=1)

		self.sg_canvas = tk.Canvas(sg)
		self.sg_canvas.grid(row=0, column=0, sticky="news")

		# Link a scrollbar to the canvas
		sg_vsb = tk.Scrollbar(sg, orient="vertical", command=self.sg_canvas.yview)
		sg_vsb.grid(row=0, column=1, sticky='ns')
		self.sg_canvas.configure(yscrollcommand=sg_vsb.set)

		# Link another scrollbar to the canvas
		sg_hsb = tk.Scrollbar(sg, orient="horizontal", command=self.sg_canvas.xview)
		sg_hsb.grid(row=1, column=0, sticky='ew')
		self.sg_canvas.configure(xscrollcommand=sg_hsb.set)


		self.scriptgrid = tk.Frame(self.sg_canvas)
		self.sg_canvas.create_window((0, 0), window=self.scriptgrid, anchor='nw')




		# label row 0 of sg
		self.scriptgrid.columnconfigure(self.plancolidx, weight=0)
		idx = ttk.Label(self.scriptgrid, text="Index")
		idx.grid(column=self.plancolidx, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolusr, weight=0)
		usr = ttk.Label(self.scriptgrid, text="Robots")
		usr.grid(column=self.plancolusr, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancoldly, weight=0)
		usr = ttk.Label(self.scriptgrid, text="Delay")
		usr.grid(column=self.plancoldly, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolrmp, weight=0)
		usr = ttk.Label(self.scriptgrid, text="Ramp Up")
		usr.grid(column=self.plancolrmp, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolrun, weight=0)
		usr = ttk.Label(self.scriptgrid, text="Run")
		usr.grid(column=self.plancolrun, row=0, sticky="nsew")

		# self.scriptgrid.columnconfigure(self.plancolnme, weight=5)
		# nme = ttk.Label(self.scriptgrid, text="Name")
		# nme.grid(column=self.plancolnme, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolscr, weight=5)
		scr = ttk.Label(self.scriptgrid, text="Script")
		scr.grid(column=self.plancolscr, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancoltst, weight=5)
		tst = ttk.Label(self.scriptgrid, text="Test")
		tst.grid(column=self.plancoltst, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancoltst, weight=5)
		tst = ttk.Label(self.scriptgrid, text="Settings")
		tst.grid(column=self.plancolset, row=0, sticky="nsew")

		icontext = "AddRow"
		self.icoAddRow = self.get_icon(icontext)
		self.scriptgrid.columnconfigure(self.plancoladd, weight=0)
		new = ttk.Button(self.scriptgrid, image=self.imgdata[icontext], padding='3 3 3 3', text="+", command=base.addScriptRow, width=1)
		new.grid(column=self.plancoladd, row=0, sticky="nsew")


		self.icoScript = self.get_icon("Script")
		self.icoAdvanced = self.get_icon("Advanced")
		self.icoDelete = self.get_icon("Delete")

		# self.scrollable_sg.update()
		# update scrollbars
		self.scriptgrid.update_idletasks()
		self.sg_canvas.config(scrollregion=self.sg_canvas.bbox("all"))

	def CanvasResize(self, event):
		base.debugmsg(6, "event:", event)
		self.pln_update_graph()

	def ClickPlay(self, _event=None):

		self.display_run['start_time'].set("  --:--:--  ")
		self.display_run['elapsed_time'].set("  --:--:--  ")
		self.display_run['finish_time'].set("  --:--:--  ")
		base.debugmsg(6, "Test Started:	", int(time.time()), "[",datetime.now().isoformat(sep=' ',timespec='seconds'),"]")

		icontext = "Stop"
		self.icoStop = self.get_icon(icontext)
		self.elements["Run"]["btn_stop"]["image"] = self.icoStop

		self.tabs.select(1)

		core.ClickPlay()

	def pln_update_graph(self):

		totcolour = "#000000"
		gridcolour = "#cfcfcf"
		defaultcolour = "#000000"



		base.debugmsg(6, "pln_update_graph")
		base.debugmsg(6, "pln_graph:", self.pln_graph)
		base.debugmsg(6, "scriptlist:", base.scriptlist)
		try:
			base.debugmsg(6, "winfo_width:", self.pln_graph.winfo_width(), "	winfo_height:",self.pln_graph.winfo_height())
			graphh = self.pln_graph.winfo_height()
			graphw = self.pln_graph.winfo_width()
		except:
			return False

		base.debugmsg(6, "graphh", graphh, "graphw", graphw)


		axissz = 10
		if graphw > graphh:
			# axissz = int(graphh * 0.1)
			axissz = (graphh * 0.1)
		else:
			# axissz = int(graphw * 0.1)
			axissz = (graphw * 0.1)

		base.debugmsg(6, 'axissz:', axissz)

		#  work out max users
		mxuser = 0
		mxusero = 0
		for grp in base.scriptlist:
			if "Robots" in grp.keys():
				mxuser += grp["Robots"]
				mxusero += grp["Robots"]
		base.debugmsg(6, "mxuser", mxuser)
		if mxuser <10:
			mxuser += 1
		else:
			mxuser = int(mxuser*1.15)
		base.debugmsg(5, "mxuser", mxuser)


		#  work out max duration
		mxdur = 0
		for grp in base.scriptlist:
			if "Robots" in grp.keys():
				dur = grp["Delay"] + (grp["RampUp"]*2) + grp["Run"]
				dur = int(dur * 1.03)
				if mxdur < dur:
					mxdur = dur
		base.debugmsg(6, "mxdur", mxdur)

		totrbtsxy = {}
		totcounts = {}
		totcounts[0] = 0
		base.debugmsg(6, 'totcounts', totcounts)
		base.debugmsg(6, 'totcounts.keys()', totcounts.keys())
		totinc = 1
		if mxdur > 60:
			totinc = 10
		if mxdur > 3600:
			totinc = 60

		self.pln_graph.delete("all")

		ym0 = graphh-int(axissz/2)	# point below x axis
		ym1 = graphh-axissz			# x axis line
		ym2 = 0						# top of graph
		base.debugmsg(5, "ym0:", ym0, "	ym1:", ym1, "	ym2:", ym2)

		xm1 = axissz			# y axis line
		if mxusero>99:
			xm1 = (axissz*2)
		if mxusero>9999:
			xm1 = (axissz*3)

		xm0 = int(xm1/2)			# point to left of y axis
		xm2 = graphw				# right hand site of x axis
		xmt = xm2-xm1				# total lenght of x axis

		base.debugmsg(5, "xm0:", xm0, "	xm1:", xm1, "	xm2:", xm2, "	xmt:",xmt)

		# y-axis
		self.pln_graph.create_line(xm1, ym1, xm1, ym2, fill=defaultcolour)
		# self.pln_graph.create_line(xm1, ym1, xm1, ym2)
		# self.pln_graph.create_line(xm1, ym1, xm1, ym2, fill=gridcolour)
		# x-axis
		# base.gui.pln_graph.create_line(10, graphh-10, graphw, graphh-10, fill="blue")
		self.pln_graph.create_line(xm1, ym1, xm2, ym1, fill=defaultcolour)
		# self.pln_graph.create_line(xm1, ym1, xm2, ym1)

		# draw zero
		self.pln_graph.create_line(xm1, ym0, xm1, ym1, fill=defaultcolour)
		self.pln_graph.create_line(xm0, ym1, xm1, ym1, fill=defaultcolour)
		self.pln_graph.create_text([xm0, ym0], text="0", fill=defaultcolour)
		# self.pln_graph.create_line(xm1, ym0, xm1, ym1)
		# self.pln_graph.create_line(xm0, ym1, xm1, ym1)
		# self.pln_graph.create_text([xm0, ym0], text="0")

		# populate x axis	(time)
		base.debugmsg(5, "populate x axis	(time)")
		base.debugmsg(9, "mxdur", mxdur)
		durinc = 1
		if mxdur > 30:		# 30 sec
			durinc = 15		# 15 sec
		if mxdur > 120:		# 120 = 2 min
			durinc = 60		# 1 min
		if mxdur > 1800:	# 60 * 30 = 1800 sec = 1/2hr
			durinc = 300	# 5 min
		if mxdur > 3600:	# 60 * 60 = 3600 sec = 1hr
			durinc = 600	# 10 min
		if mxdur > 7200:	# 60 * 60 * 2 = 7200 sec = 2hr
			durinc = 3600	# 1 hr
		if mxdur > 36000:	# 60 * 60 * 10= 36000 sec = 10hr
			durinc = 7200	# 2 hr
		base.debugmsg(9, "durinc", durinc)

		if mxdur>0:
			mrkpct = durinc / (mxdur * 1.0)
		else:
			mrkpct = 0
		base.debugmsg(9, "mrkpct", mrkpct)
		base.debugmsg(9, "xm1", xm1, "xm2", xm2, "xm2-xm1", xm2-xm1)
		mrkinc = int(xmt * mrkpct)
		base.debugmsg(9, "mrkinc", mrkinc)
		if mrkinc < 1:
			mrkinc = 1

		tmmrk = xm1 + mrkinc
		base.debugmsg(9, "tmmrk", tmmrk)
		base.debugmsg(9, "durinc", durinc)
		durmrk = durinc
		base.debugmsg(9, "durmrk", durmrk)
		while durmrk < mxdur+1:
			base.debugmsg(9, "x1", tmmrk, "y1", ym0, "x2", tmmrk, "y2", ym1)
			# base.gui.pln_graph.create_line(tmmrk, ym0, tmmrk, ym1)
			self.pln_graph.create_line(tmmrk, ym1, tmmrk, ym2, fill=gridcolour)
			base.debugmsg(9, "format_sec({})".format(durmrk), base.format_sec(durmrk))
			self.pln_graph.create_text([tmmrk, ym0], text=base.format_sec(durmrk), fill=defaultcolour)
			# self.pln_graph.create_text([tmmrk, ym0], text=base.format_sec(durmrk))

			tmmrk += mrkinc
			base.debugmsg(9, "tmmrk", tmmrk)
			durmrk += durinc
			base.debugmsg(9, "durmrk", durmrk)



		# populate y axis	(Robots)
		base.debugmsg(9, "populate y axis	(Robots)")
		usrinc = 1
		if mxuser > 15:
			usrinc = int((mxusero/100)+0.9)*10
		base.debugmsg(9, "mxusero", mxusero)
		base.debugmsg(9, "usrinc", usrinc)
		base.debugmsg(9, "usrinc", usrinc)
		usrmrk = usrinc
		if mxuser>0:
			mrkpct = usrmrk / (mxuser * 1.0)
		else:
			mrkpct = 0
		base.debugmsg(9, "mrkpct", mrkpct)
		txtmrkoffset = int(int(ym1 * mrkpct)/2)
		base.debugmsg(9, "txtmrkoffset", txtmrkoffset)
		while usrmrk < mxuser:
			base.debugmsg(9, "usrmrk", usrmrk)
			mrkpct = usrmrk / (mxuser * 1.0)
			base.debugmsg(9, "mrkpct", mrkpct)
			mrk = ym1 - int(ym1 * mrkpct)
			base.debugmsg(9, "mrk", mrk)
			txtmrk = mrk + txtmrkoffset
			# base.gui.pln_graph.create_line(xm0, mrk, xm1, mrk)
			self.pln_graph.create_line(xm1, mrk, xm2, mrk, fill=gridcolour)
			# base.gui.pln_graph.create_text([xm0, txtmrk], text="{}".format(usrmrk))
			self.pln_graph.create_text([xm0, mrk], text="{}".format(usrmrk), fill=defaultcolour)
			# self.pln_graph.create_text([xm0, mrk], text="{}".format(usrmrk))

			usrmrk += usrinc


		xlen = xmt

		delx = 0
		base.debugmsg(6, "For grp In scriptlist")
		for grp in base.scriptlist:
			if "Robots" in grp.keys():
				base.debugmsg(6, "Index", grp["Index"])
				colour = base.line_colour(grp["Index"])
				base.debugmsg(6, "Index", grp["Index"], "Line colour", colour)
				# delay
				delaypct = grp["Delay"] / (mxdur * 1.0)
				delx = int(xlen * delaypct) + xm1
				base.debugmsg(6, "Index", grp["Index"], "Delay:", grp["Delay"], "	(xlen:",xlen," * delaypct:", delaypct, ") + xm1:", xm1, " = delx:", delx)
				# ramp-up
				rusx = delx
				rusy = graphh-axissz
				usrpct = grp["Robots"] / (mxuser * 1.0)
				base.debugmsg(6, "Index", grp["Index"], "RampUp:Robots", grp["Robots"], "/ mxuser", mxuser, " = usrpct", usrpct)
				rudpct = grp["RampUp"] / (mxdur * 1.0)
				ruex = int(xlen * rudpct) + delx
				base.debugmsg(6, "Index", grp["Index"], "RampUp:RampUp", grp["RampUp"], "ruex", ruex)
				ruey = rusy - int(rusy * usrpct)
				base.debugmsg(6, "Index", grp["Index"], "RampUp:rusx", str(rusx), "rusy", str(rusy), "ruex", str(ruex), "ruey", str(ruey))
				self.pln_graph.create_line(rusx, rusy, ruex, ruey, fill=colour)

				index = grp["Index"]
				if index not in totrbtsxy:
					totrbtsxy[index] = {}
				if "addpct" not in totrbtsxy:
					totrbtsxy["addpct"] = {}

				totrbtsxy[index]['delaypct'] = delaypct
				totrbtsxy[index]['usrpct'] = usrpct
				totrbtsxy[index]['rudpct'] = rudpct

				if delaypct not in totrbtsxy["addpct"]:
					totrbtsxy["addpct"][delaypct] = 0

				totrbtsxy["addpct"][delaypct] += 0

				rutpct = delaypct + rudpct
				if rutpct not in totrbtsxy["addpct"]:
					totrbtsxy["addpct"][rutpct] = 0
				totrbtsxy["addpct"][rutpct] += usrpct


				# Run
				rnpct = grp["Run"] / (mxdur * 1.0)
				rnex = int(xlen * rnpct) + ruex
				base.debugmsg(6, "Index", grp["Index"], "rnex", rnex)
				self.pln_graph.create_line(ruex, ruey, rnex, ruey, fill=colour)

				rntpct = delaypct + rudpct + rnpct
				if rntpct not in totrbtsxy["addpct"]:
					totrbtsxy["addpct"][rntpct] = 0
				totrbtsxy["addpct"][rntpct] += 0


				# ramp-down
				rdex = rnex+(ruex-rusx)
				base.debugmsg(6, "Index", grp["Index"], "rdex", rdex)
				self.pln_graph.create_line(rnex, ruey, rdex, rusy, fill=colour, dash=(4, 4))

				rdtpct = delaypct + rudpct + rnpct + rudpct
				if rdtpct not in totrbtsxy["addpct"]:
					totrbtsxy["addpct"][rdtpct] = 0
				totrbtsxy["addpct"][rdtpct] += (usrpct * -1)

		base.debugmsg(6, "Total Robots")
		base.debugmsg(6, "totrbtsxy:", totrbtsxy)

		sy = graphh-axissz
		prevx = 0
		prevx2 = 0
		prevy = 0
		k = "addpct"

		addzero = 0

		rusy = graphh-axissz
		if k in totrbtsxy:
			for x in sorted(totrbtsxy[k].keys()):
				newx = x
				newy = prevy + totrbtsxy[k][x]

				base.debugmsg(6, "prevx", prevx, "prevy", prevy, "newx", newx, "newy", newy)

				if addzero > 1:
					prevx = prevx2
					base.debugmsg(6, "prevx", prevx, "prevy", prevy, "newx", newx, "newy", newy)

				if newy == prevy:
					addzero += 1
					base.debugmsg(6, "addzero:", addzero)
					prevx2 = prevx
				else:
					addzero = 0



				x1 = int(xlen * prevx) + xm1
				x2 = int(xlen * newx) + xm1

				y1 = rusy - int(rusy * prevy)
				y2 = rusy - int(rusy * newy)

				base.debugmsg(6, "x1", x1, "y1", y1, "x2", x2, "y2", y2)

				self.pln_graph.create_line(x1, y1, x2, y2, fill=totcolour)

				prevx = newx
				prevy = newy

		base.debugmsg(6, "pln_update_graph done")

	def pln_update_graph_orig(self):
		base.debugmsg(6, "pln_update_graph")
		base.debugmsg(7, "pln_graph:", self.pln_graph)
		base.debugmsg(9, "scriptlist:", base.scriptlist)
		try:
			base.debugmsg(9, "winfo_width:", self.pln_graph.winfo_width(), "	winfo_height:",self.pln_graph.winfo_height())
			graphh = self.pln_graph.winfo_height()
			graphw = self.pln_graph.winfo_width()
		except:
			return False

		base.debugmsg(9, "graphh", graphh, "graphw", graphw)


		axissz = 10
		if graphw > graphh:
			axissz = int(graphh * 0.1)
		else:
			axissz = int(graphw * 0.1)

		#  work out max users
		mxuser = 0
		mxusero = 0
		for grp in base.scriptlist:
			if "Robots" in grp.keys():
				mxuser += grp["Robots"]
				mxusero += grp["Robots"]
		base.debugmsg(6, "mxuser", mxuser)
		if mxuser <10:
			mxuser += 1
		else:
			mxuser = int(mxuser*1.15)
		base.debugmsg(5, "mxuser", mxuser)


		#  work out max duration
		mxdur = 0
		for grp in base.scriptlist:
			if "Robots" in grp.keys():
				dur = grp["Delay"] + (grp["RampUp"]*2) + grp["Run"]
				dur = int(dur * 1.03)
				if mxdur < dur:
					mxdur = dur
		base.debugmsg(6, "mxdur", mxdur)

		totcounts = {}
		totcounts[0] = 0
		base.debugmsg(6, 'totcounts', totcounts)
		base.debugmsg(6, 'totcounts.keys()', totcounts.keys())
		totinc = 1
		if mxdur > 60:
			totinc = 10
		if mxdur > 3600:
			totinc = 60

		self.pln_graph.delete("all")

		ym0 = graphh-int(axissz/2)	# point below x axis
		ym1 = graphh-axissz			# x axis line
		ym2 = 0						# top of graph

		xm1 = axissz			# y axis line
		if mxusero>99:
			xm1 = (axissz*2)
		if mxusero>9999:
			xm1 = (axissz*3)

		xm0 = int(xm1/2)			# point to left of y axis
		xm2 = graphw				# right hand site of x axis
		xmt = xm2-xm1				# total lenght of x axis

		# y-axis
		self.pln_graph.create_line(xm1, ym1, xm1, ym2)
		# x-axis
		# base.gui.pln_graph.create_line(10, graphh-10, graphw, graphh-10, fill="blue")
		self.pln_graph.create_line(xm1, ym1, xm2, ym1)

		# draw zero
		self.pln_graph.create_line(xm1, ym0, xm1, ym1)
		self.pln_graph.create_line(xm0, ym1, xm1, ym1)
		self.pln_graph.create_text([xm0, ym0], text="0")

		# populate x axis	(time)
		base.debugmsg(5, "populate x axis	(time)")
		base.debugmsg(9, "mxdur", mxdur)
		durinc = 1
		if mxdur > 30:		# 30 sec
			durinc = 15		# 15 sec
		if mxdur > 120:		# 120 = 2 min
			durinc = 60		# 1 min
		if mxdur > 1800:	# 60 * 30 = 1800 sec = 1/2hr
			durinc = 300	# 5 min
		if mxdur > 3600:	# 60 * 60 = 3600 sec = 1hr
			durinc = 600	# 10 min
		if mxdur > 7200:	# 60 * 60 * 2 = 7200 sec = 2hr
			durinc = 3600	# 1 hr
		if mxdur > 36000:	# 60 * 60 * 10= 36000 sec = 10hr
			durinc = 7200	# 2 hr
		base.debugmsg(9, "durinc", durinc)

		if mxdur>0:
			mrkpct = durinc / (mxdur * 1.0)
		else:
			mrkpct = 0
		base.debugmsg(9, "mrkpct", mrkpct)
		base.debugmsg(9, "xm1", xm1, "xm2", xm2, "xm2-xm1", xm2-xm1)
		mrkinc = int(xmt * mrkpct)
		base.debugmsg(9, "mrkinc", mrkinc)
		if mrkinc < 1:
			mrkinc = 1

		tmmrk = xm1 + mrkinc
		base.debugmsg(9, "tmmrk", tmmrk)
		base.debugmsg(9, "durinc", durinc)
		durmrk = durinc
		base.debugmsg(9, "durmrk", durmrk)
		gridcolour = "#cfcfcf"
		while durmrk < mxdur+1:
			base.debugmsg(9, "x1", tmmrk, "y1", ym0, "x2", tmmrk, "y2", ym1)
			# base.gui.pln_graph.create_line(tmmrk, ym0, tmmrk, ym1)
			self.pln_graph.create_line(tmmrk, ym1, tmmrk, ym2, fill=gridcolour)
			base.debugmsg(9, "format_sec({})".format(durmrk), base.format_sec(durmrk))
			self.pln_graph.create_text([tmmrk, ym0], text=base.format_sec(durmrk))

			tmmrk += mrkinc
			base.debugmsg(9, "tmmrk", tmmrk)
			durmrk += durinc
			base.debugmsg(9, "durmrk", durmrk)



		# populate y axis	(Robots)
		base.debugmsg(9, "populate y axis	(Robots)")
		usrinc = 1
		if mxuser > 15:
			usrinc = int((mxusero/100)+0.9)*10
		base.debugmsg(9, "mxusero", mxusero)
		base.debugmsg(9, "usrinc", usrinc)
		base.debugmsg(9, "usrinc", usrinc)
		usrmrk = usrinc
		if mxuser>0:
			mrkpct = usrmrk / (mxuser * 1.0)
		else:
			mrkpct = 0
		base.debugmsg(9, "mrkpct", mrkpct)
		txtmrkoffset = int(int(ym1 * mrkpct)/2)
		base.debugmsg(9, "txtmrkoffset", txtmrkoffset)
		while usrmrk < mxuser:
			base.debugmsg(9, "usrmrk", usrmrk)
			mrkpct = usrmrk / (mxuser * 1.0)
			base.debugmsg(9, "mrkpct", mrkpct)
			mrk = ym1 - int(ym1 * mrkpct)
			base.debugmsg(9, "mrk", mrk)
			txtmrk = mrk + txtmrkoffset
			# base.gui.pln_graph.create_line(xm0, mrk, xm1, mrk)
			self.pln_graph.create_line(xm1, mrk, xm2, mrk, fill=gridcolour)
			# base.gui.pln_graph.create_text([xm0, txtmrk], text="{}".format(usrmrk))
			self.pln_graph.create_text([xm0, mrk], text="{}".format(usrmrk))

			usrmrk += usrinc


		xlen = xmt

		delx = 0
		base.debugmsg(6, "For grp In scriptlist")
		for grp in base.scriptlist:
			if "Robots" in grp.keys():
				base.debugmsg(6, "Index", grp["Index"])
				colour = base.line_colour(grp["Index"])
				base.debugmsg(6, "Index", grp["Index"], "Line colour", colour)
				# delay
				delaypct = grp["Delay"] / (mxdur * 1.0)
				delx = int(xlen * delaypct) + xm1
				base.debugmsg(6, "Index", grp["Index"], "Delay", grp["Delay"], "delx", delx)
				# ramp-up
				rusx = delx
				rusy = graphh-axissz
				usrpct = grp["Robots"] / (mxuser * 1.0)
				base.debugmsg(9, "Index", grp["Index"], "RampUp:Robots", grp["Robots"], "/ mxuser", mxuser, " = usrpct", usrpct)
				rudpct = grp["RampUp"] / (mxdur * 1.0)
				ruex = int(xlen * rudpct) + delx
				base.debugmsg(9, "Index", grp["Index"], "RampUp:RampUp", grp["RampUp"], "ruex", ruex)
				ruey = rusy - int(rusy * usrpct)
				base.debugmsg(6, "Index", grp["Index"], "RampUp:rusx", rusx, "rusy", rusy, "ruex", ruex, "ruey", ruey)
				self.pln_graph.create_line(rusx, rusy, ruex, ruey, fill=colour)

				# Run
				rnpct = grp["Run"] / (mxdur * 1.0)
				rnex = int(xlen * rnpct) + ruex
				base.debugmsg(6, "Index", grp["Index"], "rnex", rnex)
				self.pln_graph.create_line(ruex, ruey, rnex, ruey, fill=colour)

				# ramp-down
				rdex = rnex+(ruex-rusx)
				base.debugmsg(6, "Index", grp["Index"], "rdex", rdex)
				self.pln_graph.create_line(rnex, ruey, rdex, rusy, fill=colour, dash=(4, 4))

				# totcounts = {}
				# totinc = 1
				# if mxdur > 60:
				totnxt = 0
				base.debugmsg(6, "Index", grp["Index"], 'totnxt', totnxt)
				base.debugmsg(8, "Index", grp["Index"], 'totcounts', totcounts)
				base.debugmsg(8, "Index", grp["Index"], 'totcounts.keys()', totcounts.keys())
				while totnxt < mxdur:
					totnxt += totinc
					base.debugmsg(6, "Index", grp["Index"], 'totnxt', totnxt)
					if totnxt not in totcounts.keys():
						totcounts[totnxt] = 0
						base.debugmsg(6, "Index", grp["Index"], 'totcounts[',totnxt,']', totcounts[totnxt])
					# if totnxt < grp["Delay"]:
					# 	totcounts[totnxt] += 0
					if totnxt > grp["Delay"] and totnxt < (grp["RampUp"] + grp["Delay"]):
						# calculate users during RampUp
						rupct = (totnxt - grp["Delay"]) /grp["RampUp"]
						base.debugmsg(9, 'rupct', rupct)
						ruusr = int(grp["Robots"] * rupct)
						base.debugmsg(9, 'ruusr', ruusr)
						base.debugmsg(9, 'totcounts', totcounts)
						base.debugmsg(9, 'totcounts[totnxt]', totcounts[totnxt])
						totcounts[totnxt] = int(totcounts[totnxt] + ruusr)
						base.debugmsg(6, "Index", grp["Index"], 'totcounts[',totnxt,']', totcounts[totnxt])
						base.debugmsg(9, 'ruusr', ruusr)
						base.debugmsg(9, 'totcounts[totnxt]', totcounts[totnxt])

					if totnxt > (grp["Delay"] + grp["RampUp"] - 1) \
						and totnxt < (grp["Delay"] + grp["RampUp"] + grp["Run"] + 1):
						# all users running
						base.debugmsg(9, 'run:totnxt', totnxt)
						base.debugmsg(9, 'run:grp["Robots"]', grp["Robots"])
						totcounts[totnxt] += grp["Robots"]
						base.debugmsg(6, "Index", grp["Index"], 'totcounts[',totnxt,']', totcounts[totnxt])
					if totnxt > (grp["RampUp"] + grp["Delay"] + grp["Run"]) \
						and totnxt < (grp["Delay"] + (grp["RampUp"] *2 ) + grp["Run"]):
						# calculate users during RampDown
						base.debugmsg(9, 'RampDown:totnxt', totnxt)
						drr = grp["Delay"] + grp["RampUp"] + grp["Run"]
						base.debugmsg(9, 'RampDown:drr', drr)
						rdsec = totnxt - drr
						base.debugmsg(9, 'RampDown:rdsec', rdsec)

						rdpct = rdsec /grp["RampUp"]
						base.debugmsg(9, 'RampDown:rdpct', rdpct)
						ruusr = int(grp["Robots"] * rdpct)
						base.debugmsg(9, 'RampDown:ruusr', ruusr)
						totcounts[totnxt] += grp["Robots"] - ruusr
						base.debugmsg(6, "Index", grp["Index"], 'totcounts[',totnxt,']', totcounts[totnxt])

		base.debugmsg(6, "Total Robots")

		totcolour = "#000000"
		# totcolour = "#0459af"
		sy = graphh-axissz
		prevkey = 0
		prevx = 0
		prevy = sy
		prevval = 0
		rampdown = False
		for key in totcounts.keys():
			if rampdown == False and totcounts[key] < prevval:
				rampdown = True
				base.debugmsg(6, prevkey, totcounts[prevkey])

				usrpct = prevval / (mxuser * 1.0)
				base.debugmsg(6, "Robots", totcounts[key], "/ mxuser", mxuser, " = usrpct", usrpct)
				newy = sy - int(sy * usrpct)

				keypct = prevkey / (mxdur * 1.0)
				base.debugmsg(6, "key", key, "/ mxdur", mxdur, " = keypct", keypct)
				newx = int(xlen * keypct) + delx

				base.debugmsg(6, "prevx", prevx, "prevy", prevy, "newx", newx, "newy", newy)

				self.pln_graph.create_line(prevx, prevy, newx, newy, fill=totcolour)

				prevx = newx
				prevy = newy

			if totcounts[key] != prevval:
				base.debugmsg(6, key, totcounts[key])
				prevval = totcounts[key]

				usrpct = totcounts[key] / (mxuser * 1.0)
				base.debugmsg(6, "TU: Robots", totcounts[key], "/ mxuser", mxuser, " = usrpct", usrpct)
				newy = sy - int(sy * usrpct)

				keypct = key / (mxdur * 1.0)
				base.debugmsg(6, "TU: key", key, "/ mxdur", mxdur, " = keypct", keypct)
				newx = int(xlen * keypct) + delx

				base.debugmsg(6, "TU: prevx", prevx, "prevy", prevy, "newx", newx, "newy", newy)

				if rampdown:
					self.pln_graph.create_line(prevx, prevy, newx, newy, fill=totcolour, dash=(4, 4))
				else:
					self.pln_graph.create_line(prevx, prevy, newx, newy, fill=totcolour)

				prevx = newx
				prevy = newy


			prevkey = key

	def addScriptRow(self):
		base.debugmsg(6, "addScriptRow")
		row = base.scriptcount

		colour = base.line_colour(base.scriptcount)
		base.debugmsg(5, "colour:", colour)

		idx = tk.Label(self.scriptgrid, text=str(base.scriptcount))
		idx['bg'] = colour
		idx.grid(column=self.plancolidx, row=base.scriptcount, sticky="nsew")


		num = base.scriptlist[base.scriptcount]["Robots"]
		usr = ttk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout")
		# usr = ttk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout", style="BW.TLabel")
		# usr = ttk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout", style="rfsinput")
		# usr = tk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout", fg="systemControlTextColor")
		# usr = tk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout")
		# systemControlTextColor
		usr.config(validatecommand=lambda: self.sr_users_validate(row))
		usr.grid(column=self.plancolusr, row=base.scriptcount, sticky="nsew")
		usr.insert(0, num)
		base.scriptlist[base.scriptcount]["Robots"] = int(num)

		num = base.scriptlist[base.scriptcount]["Delay"]
		# base.scriptlist[row]["TXT_Delay"] = tk.StringVar()
		dly = ttk.Entry(self.scriptgrid, width=8, justify="right", validate="focusout")
		dly.config(validatecommand=lambda: self.sr_delay_validate(row))
		dly.grid(column=self.plancoldly, row=base.scriptcount, sticky="nsew")
		dly.insert(0, base.sec2hms(num))
		base.scriptlist[base.scriptcount]["Delay"] = base.hms2sec(num)

		num = base.scriptlist[base.scriptcount]["RampUp"]
		rmp = ttk.Entry(self.scriptgrid, width=8, justify="right", validate="focusout")
		rmp.config(validatecommand=lambda: self.sr_rampup_validate(row))
		rmp.grid(column=self.plancolrmp, row=base.scriptcount, sticky="nsew")
		# rmp.insert(0, num)
		rmp.insert(0, base.sec2hms(num))
		base.scriptlist[base.scriptcount]["RampUp"] = base.hms2sec(num)

		num = base.scriptlist[base.scriptcount]["Run"]
		run = ttk.Entry(self.scriptgrid, width=8, justify="right", validate="focusout")
		run.config(validatecommand=lambda: self.sr_run_validate(row))
		run.grid(column=self.plancolrun, row=base.scriptcount, sticky="nsew")
		# run.insert(0, num)
		run.insert(0, base.sec2hms(num))
		base.scriptlist[base.scriptcount]["Run"] = base.hms2sec(num)

		fgf = ttk.Frame(self.scriptgrid)
		fgf.grid(column=self.plancolscr, row=base.scriptcount, sticky="nsew")
		scr = ttk.Entry(fgf, state="readonly", justify="right")
		scr.grid(column=0, row=0, sticky="nsew")
		fgf.columnconfigure(scr, weight=1)

		icontext = "Script"
		# self.icoScript = self.get_icon(icontext)
		# scrf = ttk.Button(fgf, image=self.imgdata[icontext], padding='3 0 3 0', text="...", width=1)
		scrf = ttk.Button(fgf, image=self.imgdata[icontext], text="...", width=1)
		scrf.config(command=lambda: self.sr_file_validate(row))
		scrf.grid(column=1, row=0, sticky="nsew")
		fgf.columnconfigure(scrf, weight=0)

		base.scriptlist[row]["TestVar"] = tk.StringVar(base.scriptlist[row]["Test"], name="row{}".format(row))
		base.scriptlist[row]["TestVar"].trace("w", self.sr_test_validate)
		tst = ttk.OptionMenu(self.scriptgrid, base.scriptlist[row]["TestVar"], None, "test")
		tst.config(width=20)
		tst.grid(column=self.plancoltst, row=base.scriptcount, sticky="nsew")


		icontext = "Advanced"
		# self.icoAdvanced = self.get_icon(icontext)
		self.scriptgrid.columnconfigure(self.plancoladd, weight=0)
		new = ttk.Button(self.scriptgrid, image=self.imgdata[icontext], text="Settings", command=lambda: self.sr_row_settings(row), width=1)
		new.grid(column=self.plancolset, row=base.scriptcount, sticky="nsew")


		icontext = "Delete"
		# self.icoDelete = self.get_icon(icontext)
		self.scriptgrid.columnconfigure(self.plancoladd, weight=0)
		new = ttk.Button(self.scriptgrid, image=self.imgdata[icontext], text="X", command=lambda: self.sr_remove_row(row), width=1)
		new.grid(column=self.plancoladd, row=base.scriptcount, sticky="nsew")

		# self.scrollable_sg.update()
		base.debugmsg(6, "base.args.nogui", base.args.nogui)
		if not base.args.nogui:
			try:
				base.debugmsg(6, "call pln_update_graph")
				self.pln_update_graph()
				base.debugmsg(6, "call fill_canvas")
				# self.scrollable_sg.fill_canvas()
				fc = threading.Thread(target=self.scrollable_sg.fill_canvas)
				fc.start()

			except:
				pass

		base.debugmsg(6, "addScriptRow done")

		# update scrollbars
		self.scriptgrid.update_idletasks()
		self.sg_canvas.config(scrollregion=self.sg_canvas.bbox("all"))


	def sr_users_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			v = None
			if len(args)>1:
				usrs = args[1]
				if not base.args.nogui:
					base.debugmsg(8, "sr_users_validate: len(grid_slaves):",len(self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)))
					while len(self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)) < 1:
						base.debugmsg(8, "sr_users_validate: len(grid_slaves):",len(self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)))
						time.sleep(0.01)
					base.debugmsg(9, "sr_users_validate: grid_slaves:",self.scriptgrid.grid_slaves(column=self.plancolusr, row=r))
					base.debugmsg(9, "sr_users_validate: grid_slaves[0]:",self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0])
					self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].delete(0,'end')
					self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].insert(0,usrs)

			if not base.args.nogui:
				usrs = self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].get()
			base.debugmsg(5, "Row:", r, "Robots:", usrs)
			base.scriptlist[r]["Robots"] = int(usrs)
			self.plan_scnro_chngd = True
			if not base.args.nogui:
				try:
					self.pln_update_graph()
				except:
					pass
			return True
		base.debugmsg(9, "RFSwarmGUI: grid_size:", self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			base.debugmsg(9, "RFSwarmGUI: r:", r)
			if r>0:
				usrs = self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].get()
				base.debugmsg(9, "Row:", r, "Robots:", usrs)
				base.scriptlist[r]["Robots"] = int(usrs)
				self.plan_scnro_chngd = True
		if not base.args.nogui:
			try:
				self.pln_update_graph()
			except:
				pass
		return True

	def sr_delay_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			v = None
			if len(args)>1:
				dly = str(args[1])
				idly = base.hms2sec(args[1])
				if not base.args.nogui:
					base.debugmsg(6, "Row:", r, "Delay:", dly)
					self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].delete(0,'end')
					self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].insert(0, base.sec2hms(idly))
			if not base.args.nogui:
				dly = self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].get()
				idly = base.hms2sec(dly)
				self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].delete(0,'end')
				self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].insert(0, base.sec2hms(idly))
			base.debugmsg(6, "Row:", r, "Delay:", dly)
			if len(dly)>0:
				base.scriptlist[r]["Delay"] = base.hms2sec(dly)
				self.plan_scnro_chngd = True
			else:
				base.scriptlist[r]["Delay"] = 0
				self.plan_scnro_chngd = True
			if not base.args.nogui:
				try:
					base.debugmsg(6, "try pln_update_graph (if)")
					self.pln_update_graph()
				except Exception as e:
					# base.debugmsg(6, "try pln_update_graph (if) Exception:", e)
					pass
			return True
		base.debugmsg(9, self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			base.debugmsg(9, r)
			if r>0:
				dly = self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].get()
				base.debugmsg(9, "Row:", r, "Delay:", dly)
				base.scriptlist[r]["Delay"] = base.hms2sec(dly)
				self.plan_scnro_chngd = True
		if not base.args.nogui:
			try:
				base.debugmsg(6, "try pln_update_graph (for)")
				self.pln_update_graph()
			except:
				pass
		return True

	def sr_rampup_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			rmp = None
			if len(args)>1:
				rmp = str(args[1])
				irmp = base.hms2sec(args[1])
				if not base.args.nogui:
					self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].delete(0,'end')
					self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].insert(0,base.sec2hms(irmp))
			if not base.args.nogui:
				rmp = self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].get()
				irmp = base.hms2sec(rmp)
				self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].delete(0,'end')
				self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].insert(0,base.sec2hms(irmp))
			base.debugmsg(6, "Row:", r, "RampUp:", rmp)
			base.scriptlist[r]["RampUp"] = base.hms2sec(rmp)
			self.plan_scnro_chngd = True
			if not base.args.nogui:
				try:
					self.pln_update_graph()
				except:
					pass
			return True
		base.debugmsg(9, self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			base.debugmsg(9, r)
			if r>0:
				rmp = self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].get()
				base.debugmsg(9, "Row:", r, "RampUp:", rmp)
				base.scriptlist[r]["RampUp"] = base.hms2sec(rmp)
				self.plan_scnro_chngd = True
		if not base.args.nogui:
			try:
				self.pln_update_graph()
			except:
				pass
		return True

	def sr_run_validate(self, *args):
		base.debugmsg(5, "args:",args)
		if args:
			r = args[0]
			run = None
			if len(args)>1:
				run = str(args[1])
				irun = base.hms2sec(args[1])
				if not base.args.nogui:
					self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].delete(0,'end')
					self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].insert(0,base.sec2hms(irun))
			if not base.args.nogui:
				run = self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].get()
				irun = base.hms2sec(run)
				self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].delete(0,'end')
				self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].insert(0,base.sec2hms(irun))
			base.debugmsg(6, "Row:", r, "Run:", run)
			base.scriptlist[r]["Run"] = base.hms2sec(run)
			self.plan_scnro_chngd = True
			if not base.args.nogui:
				try:
					self.pln_update_graph()
				except:
					pass
			return True
		base.debugmsg(9, self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			base.debugmsg(9, r)
			if r>0:
				run = self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].get()
				base.debugmsg(9, "Row:", r, "Run:", run)
				base.scriptlist[r]["Run"] = base.hms2sec(run)
				self.plan_scnro_chngd = True
		if not base.args.nogui:
			try:
				self.pln_update_graph()
			except:
				pass
		return True

	def sr_file_validate(self, r, *args):
		base.debugmsg(9, r)
		if not base.args.nogui:
			fg = self.scriptgrid.grid_slaves(column=self.plancolscr, row=r)[0].grid_slaves()
		base.debugmsg(9, fg)
		base.debugmsg(9, fg[1].get())
		if args:
			scriptfile = args[0]
		else:
			if not base.args.nogui:
				scriptfile = str(tkf.askopenfilename(initialdir=base.config['Plan']['ScriptDir'], title = "Select Robot Framework File", filetypes = (("Robot Framework","*.robot"),("all files","*.*"))))
			else:
				scriptfile = ""
		base.debugmsg(7, "scriptfile:", scriptfile)
		if len(scriptfile)>0:
			fg[1].configure(state='normal')
			fg[1].select_clear()
			fg[1].delete(0, 'end')
			fg[1].insert(0, os.path.basename(scriptfile))
			fg[1].configure(state='readonly')

			base.scriptlist[r]["Script"] = scriptfile
			base.debugmsg(8, "test: ", fg[1].get())
			script_hash = base.hash_file(scriptfile, os.path.basename(scriptfile))
			base.scriptlist[r]["ScriptHash"] = script_hash

			if script_hash not in base.scriptfiles:
				base.scriptfiles[script_hash] = {
					"id": script_hash,
					"localpath": scriptfile,
					"relpath": os.path.basename(scriptfile),
					"type": "script"
				}

				t = threading.Thread(target=base.find_dependancies, args=(script_hash, ))
				t.start()

			base.config['Plan']['ScriptDir'] = os.path.dirname(scriptfile)
			base.saveini()
			self.sr_test_genlist(r)
		else:
			fg[1].configure(state='normal')
			fg[1].delete(0, 'end')
			# fg[1].select_clear()
			fg[1].configure(state='readonly')
			if "ScriptHash" in base.scriptlist[r]:
				oldhash = base.scriptlist[r]["ScriptHash"]
				t = threading.Thread(target=base.remove_hash, args=(oldhash, ))
				t.start()

			base.scriptlist[r]["Script"] = ''
			base.scriptlist[r]["ScriptHash"] = ''


		self.plan_scnro_chngd = True

		if not base.args.nogui:
			try:
				self.pln_update_graph()
			except:
				pass
		return True

	def sr_test_validate(self, *args):
		base.debugmsg(6, "args:", args)
		# r = int(args[0][-1:])+1
		r = int(args[0][3:])
		base.debugmsg(9, "sr_test_validate: r:", r)

		if not base.args.nogui:
			# if 0 in self.scriptgrid.grid_slaves:
			base.debugmsg(9, "sr_test_validate: grid_slaves:", self.scriptgrid.grid_slaves(column=self.plancoltst, row=r))
			tol = self.scriptgrid.grid_slaves(column=self.plancoltst, row=r)[0]
			base.debugmsg(9, "sr_test_validate: tol:", tol)

		v = None
		if len(args)>1 and len(args[1])>1:
			v = args[1]
			base.debugmsg(9, "sr_test_validate: v:", v)
			if not base.args.nogui:
				base.scriptlist[r]["TestVar"].set(v)
			base.scriptlist[r]["Test"] = v
		else:
			if not base.args.nogui:
				base.debugmsg(9, "sr_test_validate: else")
				base.debugmsg(9, "sr_test_validate: scriptlist[r][TestVar].get():", base.scriptlist[r]["TestVar"].get())
				base.scriptlist[r]["Test"] = base.scriptlist[r]["TestVar"].get()

		base.debugmsg(9, "scriptlist[r]:", base.scriptlist[r])
		base.debugmsg(9, "scriptlist[r][TestVar].get():", base.scriptlist[r]["TestVar"].get())

		self.plan_scnro_chngd = True

		if not base.args.nogui:
			try:
				self.pln_update_graph()
			except:
				pass
		return True

	def sr_test_genlist(self, r):
		base.debugmsg(8, "Script File:",base.scriptlist[r]["Script"])
		tcsection = False
		tclist = [""]
		# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#test-data-sections
		regex = "^\*+[\s]*(Test Case|Task)"
		with open(base.scriptlist[r]["Script"]) as f:
			for line in f:
				base.debugmsg(9, "sr_test_genlist: tcsection:",tcsection, "	line:", line)
				if tcsection and line[0:3] == "***":
					tcsection = False
				if re.search(regex, line, re.IGNORECASE):
					base.debugmsg(9, "sr_test_genlist: re.search(",regex, ",", line,")", re.search(regex, line, re.IGNORECASE))
					tcsection = True
				if tcsection:
					if line[0:1] not in ('\t', ' ', '*', '#', '\n', '\r'):
						base.debugmsg(9, "", line[0:1], "")
						tclist.append(line[0:-1])
		base.debugmsg(8, tclist)
		if not base.args.nogui:
			tol = self.scriptgrid.grid_slaves(column=self.plancoltst, row=r)[0]
			base.debugmsg(9, tol)
			tol.set_menu(*tclist)

	def sr_remove_row(self, r):
		base.debugmsg(9, "sr_remove_row:", r)
		base.debugmsg(9, self.scriptgrid)
		relmts = self.scriptgrid.grid_slaves(row=r, column=None)
		base.debugmsg(9, relmts)
		for elmt in relmts:
			elmt.destroy()
		base.scriptlist[r] = {}

		# update scrollbars
		self.scriptgrid.update_idletasks()
		self.sg_canvas.config(scrollregion=self.sg_canvas.bbox("all"))

		try:
			self.pln_update_graph()
		except:
			pass
		return True

	def sr_row_settings(self, r):
		base.debugmsg(5, "r:", r)
		stgsWindow = tk.Toplevel(self.root)
		# self.grid(sticky="news", ipadx=0, pady=0)
		# self.root.resizable(False, False)		# this didn't work as expected, I expected the dialog to not be resizable instaed it stopped the main window from being resizable
		# self.root.resizable(True, True)

		stgsWindow.title("Settings for row {}".format(r))
		testname = ""
		try:
			testname = base.scriptlist[r]["TestVar"].get()
		except:
			pass
		base.debugmsg(5, "testname:", testname)
		if len(testname)>0:
			stgsWindow.title("Settings for {} ({})".format(testname, r))


		stgsWindow.excludelibrariesdefault = "BuiltIn,String,OperatingSystem,perftest"
		stgsWindow.Filters = {}

		base.debugmsg(5, "base.scriptlist[r]:", base.scriptlist[r])

		stgsWindow.excludelibrariescurrent = stgsWindow.excludelibrariesdefault
		if "excludelibraries" in base.scriptlist[r]:
			stgsWindow.excludelibrariescurrent = base.scriptlist[r]["excludelibraries"]
		base.debugmsg(5, "excludelibrariescurrent:", stgsWindow.excludelibrariescurrent)

		stgsWindow.robotoptionscurrent = ""
		if "robotoptions" in base.scriptlist[r]:
			stgsWindow.robotoptionscurrent = base.scriptlist[r]["robotoptions"]
		base.debugmsg(5, "robotoptionscurrent:", stgsWindow.robotoptionscurrent)

		row =0
		stgsWindow.lblBLNK = ttk.Label(stgsWindow, text = " ")	# just a blank row as a spacer before the filters
		stgsWindow.lblBLNK.grid(column=0, row=row, sticky="nsew")

		row +=1
		stgsWindow.lblEL = ttk.Label(stgsWindow, text = "Exclude libraries:")
		stgsWindow.lblEL.grid(column=0, row=row, sticky="nsew")

		row +=1
		# stgsWindow.inpEL = ttk.Entry(stgsWindow, text = excludelibrariesdefault)
		stgsWindow.inpEL = ttk.Entry(stgsWindow)
		stgsWindow.inpEL.delete(0,'end')
		stgsWindow.inpEL.insert(0, stgsWindow.excludelibrariescurrent)
		stgsWindow.inpEL.grid(column=0, row=row, columnspan=10, sticky="nsew")

		row +=1
		stgsWindow.lblBLNK = ttk.Label(stgsWindow, text = " ")	# just a blank row as a spacer before the filters
		stgsWindow.lblBLNK.grid(column=0, row=row, sticky="nsew")

		row +=1
		stgsWindow.lblRO = ttk.Label(stgsWindow, text = "Robot Options:")
		stgsWindow.lblRO.grid(column=0, row=row, sticky="nsew")

		row +=1
		stgsWindow.inpRO = ttk.Entry(stgsWindow)
		stgsWindow.inpRO.delete(0,'end')
		stgsWindow.inpRO.insert(0, stgsWindow.robotoptionscurrent)
		stgsWindow.inpRO.grid(column=0, row=row, columnspan=10, sticky="nsew")

		row +=1
		stgsWindow.lblBLNK = ttk.Label(stgsWindow, text = " ")	# just a blank row as a spacer before the filters
		stgsWindow.lblBLNK.grid(column=0, row=row, sticky="nsew")

		row +=1
		stgsWindow.lblAF = ttk.Label(stgsWindow, text = "Agent Filter:")
		stgsWindow.lblAF.grid(column=0, row=row, sticky="nsew")

		icontext = "AddRow"
		stgsWindow.btnAddFil = ttk.Button(stgsWindow, image=self.imgdata[icontext], text = "+", command=lambda: self.sr_row_settings_addf(r, stgsWindow), width=1)
		stgsWindow.btnAddFil.grid(column=9, row=row, sticky="news")

		row +=1
		stgsWindow.fmeFilters = tk.Frame(stgsWindow)
		stgsWindow.fmeFilters.grid(column=0, row=row, columnspan=10, sticky="nsew")

		if "filters" in base.scriptlist[r]:
			for f in base.scriptlist[r]["filters"]:
				base.debugmsg(5, "f:", f)
				base.add_scriptfilter(f['optn'])
				self.sr_row_settings_addf(r, stgsWindow, f['rule'], f['optn'])



		row +=1
		stgsWindow.lblBLNK = ttk.Label(stgsWindow, text = " ")	# just a blank row as a spacer before the buttons
		stgsWindow.lblBLNK.grid(column=0, row=row, sticky="nsew")

		row +=1
		btnSave = ttk.Button(stgsWindow, text = "Save", command=lambda: self.sr_row_settings_save(r, stgsWindow))
		btnSave.grid(column=6, row=row, sticky="nsew")

		btnCancel = ttk.Button(stgsWindow, text = "Cancel", command=stgsWindow.destroy)
		btnCancel.grid(column=7, row=row, columnspan=3, sticky="nsew") # cols 7, 8, 9

	def sr_row_settings_save(self, r, stgsWindow):
		base.debugmsg(7, "r:", r)
		base.debugmsg(7, "stgsWindow:", stgsWindow)
		el = stgsWindow.inpEL.get()
		base.debugmsg(7, "el:", el)
		if len(el)>0:
			if el != stgsWindow.excludelibrariesdefault:
				base.scriptlist[r]["excludelibraries"] = el
				self.plan_scnro_chngd = True
			else:
				if "excludelibraries" in base.scriptlist[r]:
					del base.scriptlist[r]["excludelibraries"]
		else:
			if "excludelibraries" in base.scriptlist[r]:
				del base.scriptlist[r]["excludelibraries"]
			self.plan_scnro_chngd = True

		# stgsWindow.inpRO
		ro = stgsWindow.inpRO.get()
		base.debugmsg(7, "el:", el)
		if len(ro)>0:
			if ro != stgsWindow.robotoptionscurrent:
				base.scriptlist[r]["robotoptions"] = ro
				self.plan_scnro_chngd = True
		else:
			if "robotoptions" in base.scriptlist[r]:
				del base.scriptlist[r]["robotoptions"]
			self.plan_scnro_chngd = True

		base.debugmsg(7, "stgsWindow.Filters:", stgsWindow.Filters)
		# stgsWindow.Filters
		if len(stgsWindow.Filters.keys())>0:
			base.scriptlist[r]["filters"] = []
			for fil in stgsWindow.Filters.keys():
				filtr = {}
				filtr["rule"] = stgsWindow.Filters[fil]["FilRule"].get()
				filtr["optn"] = stgsWindow.Filters[fil]["FilOpt"].get()

				if "filters" not in base.scriptlist[r]:
					base.scriptlist[r]["filters"] = []
				base.scriptlist[r]["filters"].append(filtr)
			self.plan_scnro_chngd = True
		else:
			if "filters" in base.scriptlist[r]:
				del base.scriptlist[r]["filters"]
			self.plan_scnro_chngd = True

		base.debugmsg(7, "base.scriptlist[r]:", base.scriptlist[r])

		stgsWindow.destroy()

		# MsgBox = tkm.askyesno('RFSwarm - Save Scenario','Do you want to save the current scenario?')
		# base.debugmsg(9, "MsgBox:", MsgBox)
		# if MsgBox:
		# 	self.mnu_file_Save()


	def sr_row_settings_addf(self, r, stgsWindow, *args):

		FilRule = [None, "Require", "Exclude"]

		base.debugmsg(5, "r:", r)
		xy = stgsWindow.fmeFilters.grid_size()
		base.debugmsg(5, "xy:", xy)
		fid = xy[1]

		stgsWindow.Filters[fid] = {}
		stgsWindow.Filters[fid]["FilRule"] = tk.StringVar()
		omfr = ttk.OptionMenu(stgsWindow.fmeFilters, stgsWindow.Filters[fid]["FilRule"], *FilRule)
		stgsWindow.Filters[fid]["FilRule"].set(FilRule[1])
		omfr.grid(column=0, row=fid, sticky="nsew")

		stgsWindow.Filters[fid]["FilOpt"] = tk.StringVar()
		omfo = ttk.OptionMenu(stgsWindow.fmeFilters, stgsWindow.Filters[fid]["FilOpt"], *base.scriptfilters)
		omfo.grid(column=1, row=fid, sticky="nsew")

		icontext = "Delete"
		stgsWindow.btnRemFil = ttk.Button(stgsWindow.fmeFilters, image=self.imgdata[icontext], text = "X", command=lambda: self.sr_row_settings_remf(fid, stgsWindow), width=1)
		stgsWindow.btnRemFil.grid(column=9, row=fid, sticky="nsew")
		# stgsWindow.btnRemFil.grid(column=9, row=fid, width=1)

		if len(args)>0:
			base.debugmsg(5, "args[0]:", args[0])
			stgsWindow.Filters[fid]["FilRule"].set(args[0])
		if len(args)>1:
			base.debugmsg(5, "args[1]:", args[1])
			stgsWindow.Filters[fid]["FilOpt"].set(args[1])

	def sr_row_settings_remf(self, r, stgsWindow):
		relmts = stgsWindow.fmeFilters.grid_slaves(row=r, column=None)
		base.debugmsg(5, relmts)


		for elmt in relmts:
			elmt.destroy()

		del stgsWindow.Filters[r]

		stgsWindow.update_idletasks()



	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Run
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


	def BuildRun(self, r):

		base.debugmsg(6, "config")

		if "Run" not in self.elements:
			self.elements["Run"] = {}

		rgbar = ttk.Frame(r)
		rgbar.grid(row=0, column=0, sticky="nsew")

		r.columnconfigure(0, weight=1)
		r.rowconfigure(0, weight=0)


		#
		# run info bar
		#
		base.debugmsg(6, "run info bar")
		usr = ttk.Label(rgbar, text="Unique by:") #, borderwidth=2, relief="raised")
		usr.grid(column=11, row=0, sticky="nsew") # , rowspan=2

		# gblist = ["script_index", "iteration", "sequence"]
		if "display_index" not in self.display_run:
			self.display_run['display_index'] = tk.BooleanVar()
			self.display_run['display_index'].set(base.str2bool(base.config['Run']['display_index']))
		usr = ttk.Label(rgbar, text="  Index  ") #, borderwidth=2, relief="raised")
		usr.grid(column=10, row=1, sticky="nsew")
		# chk = tk.Checkbutton(rgbar, text="Index", variable=self.display_run['display_index'], onvalue=1, offvalue=0) #, height = 2, width = 10)
		chk = tk.Checkbutton(rgbar, variable=self.display_run['display_index'], onvalue=True, offvalue=False, command=self.delayed_UpdateRunStats_bg) #, height = 2, width = 10)
		chk.grid(column=10, row=2, sticky="nsew")

		if "display_iteration" not in self.display_run:
			self.display_run['display_iteration'] = tk.BooleanVar()
			self.display_run['display_iteration'].set(base.str2bool(base.config['Run']['display_iteration']))
		usr = ttk.Label(rgbar, text="  Iteration  ") #, borderwidth=2, relief="raised")
		usr.grid(column=11, row=1, sticky="nsew")
		# chk = tk.Checkbutton(rgbar, text="Iteration", variable=self.display_run['display_iteration'], onvalue=1, offvalue=0) #, height = 2, width = 10)
		chk = tk.Checkbutton(rgbar, variable=self.display_run['display_iteration'], onvalue=True, offvalue=False, command=self.delayed_UpdateRunStats_bg) #, height = 2, width = 10)
		chk.grid(column=11, row=2, sticky="nsew")

		if "display_sequence" not in self.display_run:
			self.display_run['display_sequence'] = tk.BooleanVar()
			self.display_run['display_sequence'].set(base.str2bool(base.config['Run']['display_sequence']))
		usr = ttk.Label(rgbar, text="  Sequence  ") #, borderwidth=2, relief="raised")
		usr.grid(column=12, row=1, sticky="nsew")
		# chk = tk.Checkbutton(rgbar, text="Sequence", variable=self.display_run['display_sequence'], onvalue=1, offvalue=0) #, height = 2, width = 10)
		chk = tk.Checkbutton(rgbar, variable=self.display_run['display_sequence'], onvalue=True, offvalue=False, command=self.delayed_UpdateRunStats_bg) #, height = 2, width = 10)
		chk.grid(column=12, row=2, sticky="nsew")


		# display_percentile
		usr = ttk.Label(rgbar, text="  %ile  ") #, borderwidth=2, relief="raised")
		usr.grid(column=13, row=1, sticky="nsew")

		pct = ttk.Spinbox(rgbar, from_=1, to=99, validate="focusout", width=5, justify="right", validatecommand=self.delayed_UpdateRunStats_bg, command=self.delayed_UpdateRunStats_bg)
		pct.grid(column=13, row=2, sticky="nsew")
		pct.selection_clear()
		pct.insert(0, int(base.config['Run']['display_percentile']))
		self.display_run['display_percentile'] = pct


		if "start_time" not in self.display_run:
			self.display_run['start_time'] = tk.StringVar()
			# self.display_run['start_time'].set("  {}  ".format(base.total_robots))
			self.display_run['start_time'].set("  --:--:--  ")
		usr = ttk.Label(rgbar, text="  Start Time  ") #, borderwidth=2, relief="raised")
		usr.grid(column=20, row=1, sticky="nsew")
		usr = ttk.Label(rgbar, textvariable=self.display_run['start_time']) #, borderwidth=2, relief="groove")
		usr.grid(column=20, row=2, sticky="nsew")

		if "elapsed_time" not in self.display_run:
			self.display_run['elapsed_time'] = tk.StringVar()
			# self.display_run['elapsed_time'].set("  {}  ".format(base.total_robots))
			self.display_run['elapsed_time'].set("  --:--:--  ")
		usr = ttk.Label(rgbar, text="  Elapsed Time  ") #, borderwidth=2, relief="raised")
		usr.grid(column=21, row=1, sticky="nsew")
		usr = ttk.Label(rgbar, textvariable=self.display_run['elapsed_time']) #, borderwidth=2, relief="groove")
		usr.grid(column=21, row=2, sticky="nsew")

		if "total_robots" not in self.display_run:
			self.display_run['total_robots'] = tk.StringVar()
			self.display_run['total_robots'].set("  {}  ".format(base.total_robots))
		usr = ttk.Label(rgbar, text="  Robots  ") #, borderwidth=2, relief="raised")
		usr.grid(column=26, row=1, sticky="nsew")
		usr = ttk.Label(rgbar, textvariable=self.display_run['total_robots']) #, borderwidth=2, relief="groove")
		usr.grid(column=26, row=2, sticky="nsew")

		if "finish_time" not in self.display_run:
			self.display_run['finish_time'] = tk.StringVar()
			self.display_run['finish_time'].set("  --:--:--  ")
		usr = ttk.Label(rgbar, text="  Finish Time  ") #, borderwidth=2, relief="raised")
		usr.grid(column=29, row=1, sticky="nsew")
		usr = ttk.Label(rgbar, textvariable=self.display_run['finish_time']) #, borderwidth=2, relief="groove")
		usr.grid(column=29, row=2, sticky="nsew")


		icontext = "Stop"
		self.icoStop = self.get_icon(icontext)
		# self.elements["Run"]["btn_stop"]
		self.elements["Run"]["btn_stop"] = ttk.Button(rgbar, image=self.imgdata[icontext], padding='3 3 3 3', text="Stop", command=self.ClickStop)
		# self.elements["Run"]["btn_stop"] = ttk.Button(rgbar, text='Stop', command=self.ClickStop)
		self.elements["Run"]["btn_stop"].grid(column=39, row=1, sticky="nsew") # , rowspan=2


		icontext = "report_text"
		self.icoStop = self.get_icon(icontext)
		rpt = ttk.Button(rgbar, image=self.imgdata[icontext], padding='3 3 3 3', text="Stop", command=base.report_text)
		rpt.grid(column=50, row=1, sticky="nsew") # , rowspan=2

		# icontext = "report_html"
		# self.icoStop = self.get_icon(icontext)
		# rpt = ttk.Button(rgbar, image=self.imgdata[icontext], padding='3 3 3 3', text="Stop", command=self.report_html)
		# rpt.grid(column=51, row=1, sticky="nsew") # , rowspan=2
		#
		# icontext = "report_word"
		# self.icoStop = self.get_icon(icontext)
		# rpt = ttk.Button(rgbar, image=self.imgdata[icontext], padding='3 3 3 3', text="Stop", command=self.report_word)
		# rpt.grid(column=52, row=1, sticky="nsew") # , rowspan=2



		#
		# run results table
		#
		base.debugmsg(6, "run results table")

		r.rowconfigure(1, weight=1)

		rungridprnt = tk.Frame(r)
		rungridprnt.grid(row=1, column=0, pady=(0, 0), sticky='news')
		rungridprnt.grid_rowconfigure(0, weight=1)
		rungridprnt.grid_columnconfigure(0, weight=1)

		self.run_canvas = tk.Canvas(rungridprnt)
		self.run_canvas.grid(row=0, column=0, sticky="news")

		# Link a scrollbar to the canvas
		run_vsb = tk.Scrollbar(rungridprnt, orient="vertical", command=self.run_canvas.yview)
		run_vsb.grid(row=0, column=1, sticky='ns')
		self.run_canvas.configure(yscrollcommand=run_vsb.set)

		# Link another scrollbar to the canvas
		run_hsb = tk.Scrollbar(rungridprnt, orient="horizontal", command=self.run_canvas.xview)
		run_hsb.grid(row=1, column=0, sticky='ew')
		self.run_canvas.configure(xscrollcommand=run_hsb.set)


		self.rungrid = tk.Frame(self.run_canvas)
		self.run_canvas.create_window((0, 0), window=self.rungrid, anchor='nw')



		# set initial columns for the results grid
		if "columns" not in self.display_run:
			self.display_run["columns"] = {}
		if "rows" not in self.display_run:
			self.display_run["rows"] = {}

		collst = ["result_name", "result", "count", "min", "avg", "max"]
		colno = 0
		for col in collst:
			base.debugmsg(9, "BuildRun: colno:", colno, "col:", col)
			base.debugmsg(9, "BuildRun: display_run:", self.display_run)
			if colno in self.display_run["columns"]:
				currcol = self.display_run["columns"][colno].get()
				if col != currcol:
					self.display_run["columns"][colno].set("  {}  ".format(col))
			else:
				self.display_run["columns"][colno] = tk.StringVar()
				self.display_run["columns"][colno].set("  {}  ".format(col))

			base.debugmsg(9, "BuildRun: display_run[columns][colno]:", self.display_run["columns"][colno])

			grdcols = self.rungrid.grid_size()[0]
			base.debugmsg(9, "BuildRun: grdcols:", grdcols)
			grdcols += -1
			base.debugmsg(9, "BuildRun: grdcols:", grdcols, " 	colno:", colno)
			if grdcols < colno:
				usr = ttk.Label(self.rungrid, textvariable=self.display_run["columns"][colno], borderwidth=2, relief="raised")
				usr.grid(column=colno, row=0, sticky="nsew")

			colno += 1

		# self.scrollable_rg.update()
		# update scrollbars
		self.rungrid.update_idletasks()
		self.run_canvas.config(scrollregion=self.rungrid.bbox("all"))

	def delayed_UpdateRunStats_bg(self):

		display_index = self.display_run['display_index'].get()
		if display_index != base.str2bool(base.config['Run']['display_index']):
			base.config['Run']['display_index'] = str(display_index)
			base.saveini()

		display_iteration = self.display_run['display_iteration'].get()
		if display_iteration != base.str2bool(base.config['Run']['display_iteration']):
			base.config['Run']['display_iteration'] = str(display_iteration)
			base.saveini()

		display_sequence = self.display_run['display_sequence'].get()
		if display_sequence != base.str2bool(base.config['Run']['display_sequence']):
			base.config['Run']['display_sequence'] = str(display_sequence)
			base.saveini()

		# self.display_run['display_percentile']
		display_percentile = int(self.display_run['display_percentile'].get())
		if display_percentile != int(base.config['Run']['display_percentile']):
			base.config['Run']['display_percentile'] = str(display_percentile)
			base.saveini()

		# base.robot_schedule["Start"]
		if "Start" in base.robot_schedule:
			time_elapsed = int(time.time()) - self.rungridupdate
			if (time_elapsed>5):
				ut = threading.Thread(target=self.delayed_UpdateRunStats)
				ut.start()

	def delayed_UpdateRunStats(self):
		time_elapsed = int(time.time()) - self.rungridupdate
		if (time_elapsed>5):
			# queue sqls so UpdateRunStats should have the results

			display_percentile = base.config['Run']['display_percentile']
			if not base.args.nogui:
				display_percentile = int(self.display_run['display_percentile'].get())
			if display_percentile != int(base.config['Run']['display_percentile']):
				base.config['Run']['display_percentile'] = str(display_percentile)
				base.saveini()


			display_index = base.config['Run']['display_index']
			if not base.args.nogui:
				display_index = self.display_run['display_index'].get()
			base.debugmsg(9, "delayed_UpdateRunStats: display_index:", display_index, "	config[Run][display_index]:", base.config['Run']['display_index'], "	bool(config[Run][display_index]):", base.str2bool(base.config['Run']['display_index']))
			if display_index != base.str2bool(base.config['Run']['display_index']):
				base.config['Run']['display_index'] = str(display_index)
				base.saveini()

			display_iteration = base.config['Run']['display_iteration']
			if not base.args.nogui:
				display_iteration = self.display_run['display_iteration'].get()
			if display_iteration != base.str2bool(base.config['Run']['display_iteration']):
				base.config['Run']['display_iteration'] = str(display_iteration)
				base.saveini()

			display_sequence = base.config['Run']['display_sequence']
			if not base.args.nogui:
				display_sequence = self.display_run['display_sequence'].get()
			if display_sequence != base.str2bool(base.config['Run']['display_sequence']):
				base.config['Run']['display_sequence'] = str(display_sequence)
				base.saveini()

			base.UpdateRunStats_SQL()

			time.sleep(1)
			self.UpdateRunStats()

	def UpdateRunStats(self):
		rnum = 0
		removestat = []

		if "Start" in base.robot_schedule:
			stm = time.localtime(base.robot_schedule["Start"])
			self.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))
			# etm = time.gmtime(int(time.time()) - base.robot_schedule["Start"])
			etm = int(time.time()) - base.robot_schedule["Start"]
			# self.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))
			self.display_run['elapsed_time'].set("  {}  ".format(base.sec2hms(etm)))


		if base.posttest and base.run_finish>0:
			ftm = time.localtime(base.run_finish)
			self.display_run['finish_time'].set("  {}  ".format(time.strftime("%H:%M:%S", ftm)))
			# etm = time.gmtime(base.run_finish - base.robot_schedule["Start"])
			etm = base.run_finish - base.robot_schedule["Start"]
			# self.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))
			self.display_run['elapsed_time'].set("  {}  ".format(base.sec2hms(etm)))

		# update stop button
		if base.run_end < int(time.time()):
			icontext = "Abort"
			self.icoStop = self.get_icon(icontext)
			self.elements["Run"]["btn_stop"]["image"] = self.icoStop

		if base.run_finish > 0:
			icontext = "Aborted"
			self.icoStop = self.get_icon(icontext)
			self.elements["Run"]["btn_stop"]["image"] = self.icoStop

		time_elapsed = int(time.time()) - self.rungridupdate
		if (time_elapsed>5):
			self.rungridupdate = int(time.time())

			if "columns" not in self.display_run:
				self.display_run["columns"] = {}
			if "rows" not in self.display_run:
				self.display_run["rows"] = {}

			# if "RunStats" in base.dbqueue["ReadResult"] and len(base.dbqueue["ReadResult"]["RunStats"])>0:
			# 	print("UpdateRunStats: RunStats:", base.dbqueue["ReadResult"]["RunStats"])

			colno = 0
			if "RunStats" in base.dbqueue["ReadResult"] and len(base.dbqueue["ReadResult"]["RunStats"])>0:
				base.debugmsg(9, "UpdateRunStats: RunStats:", base.dbqueue["ReadResult"]["RunStats"])
				for col in base.dbqueue["ReadResult"]["RunStats"][0].keys():
					base.debugmsg(9, "UpdateRunStats: colno:", colno, "col:", col)
					colname = base.PrettyColName(col)
					base.debugmsg(9, "UpdateRunStats: colname:", colname)

					base.debugmsg(9, "UpdateRunStats: display_run:", self.display_run)
					if colno in self.display_run["columns"]:
						currcol = self.display_run["columns"][colno].get()
						if colname != currcol:
							self.display_run["columns"][colno].set("  {}  ".format(colname))
					else:
						self.display_run["columns"][colno] = tk.StringVar()
						self.display_run["columns"][colno].set("  {}  ".format(colname))

					base.debugmsg(9, "UpdateRunStats: display_run[columns][colno]:", self.display_run["columns"][colno])

					grdcols = self.rungrid.grid_size()[0]
					base.debugmsg(9, "UpdateRunStats: grdcols:", grdcols)
					grdcols += -1
					base.debugmsg(9, "UpdateRunStats: grdcols:", grdcols, " 	colno:", colno)
					if grdcols < colno:
						usr = ttk.Label(self.rungrid, textvariable=self.display_run["columns"][colno], borderwidth=2, relief="raised")
						usr.grid(column=colno, row=0, sticky="nsew")

					colno += 1

			colno += -1
			grdcols = self.rungrid.grid_size()[0]-1
			base.debugmsg(9, "UpdateRunStats: grdcols:", grdcols, "	colno:",colno)
			if grdcols>colno:
				base.debugmsg(9, "UpdateRunStats: need to remove columns grdcols:", grdcols, "	colno:",colno)
				c = grdcols
				while c>colno:
					base.debugmsg(9, "UpdateRunStats: need to remove rows c:", c, "	colno:",colno)
					relmts = self.rungrid.grid_slaves(row=None, column=c)
					base.debugmsg(9, relmts)
					for elmt in relmts:
						elmt.destroy()
					c += -1

			datarows = 0
			if "RunStats" in base.dbqueue["ReadResult"]:
				datarows = len(base.dbqueue["ReadResult"]["RunStats"])
			# datarows = len(base.dbqueue["ReadResult"]["RunStats_Pass"])
			grdrows = self.rungrid.grid_size()[1]-1
			base.debugmsg(9, "UpdateRunStats: grdrows:", grdrows, " > datarows:",datarows)
			if grdrows>datarows:
				base.debugmsg(9, "UpdateRunStats: need to remove rows grdrows:", grdrows, " > datarows:",datarows)
				r = grdrows
				while r>datarows:
					base.debugmsg(9, "UpdateRunStats: need to remove rows r:", r, " > datarows:",datarows)
					relmts = self.rungrid.grid_slaves(row=r, column=None)
					base.debugmsg(9, relmts)
					for elmt in relmts:
						elmt.destroy()
					r += -1

			rowno = 1
			if "RunStats" in base.dbqueue["ReadResult"]:
				for row in base.dbqueue["ReadResult"]["RunStats"]:
					newrow = False
					grdrows = self.rungrid.grid_size()[1]
					base.debugmsg(9, "UpdateRunStats: grdrows:", grdrows)

					if rowno not in self.display_run["rows"]:
						self.display_run["rows"][rowno] = {}

					colno = 0
					newcell = False
					for col in row.keys():
						base.debugmsg(9, "UpdateRunStats: colno:", colno, "col:", col)
						base.debugmsg(9, "UpdateRunStats: row[col]:", row[col])
						if colno>len(self.display_run["rows"][rowno])-1:
							self.display_run["rows"][rowno][colno] = tk.StringVar()

						self.display_run["rows"][rowno][colno].set("  {}  ".format(row[col]))

						relmts = self.rungrid.grid_slaves(row=rowno, column=colno)
						base.debugmsg(9, "UpdateRunStats: relmts:", relmts)

						# if newrow or newcell:
						if len(relmts) < 1:
							usr = ttk.Label(self.rungrid, textvariable=self.display_run["rows"][rowno][colno], borderwidth=2, relief="groove")
							usr.grid(column=colno, row=rowno, sticky="nsew")


						colno += 1

					rowno += 1


			# self.scrollable_rg.update()
			# update scrollbars
			self.rungrid.update_idletasks()
			self.run_canvas.config(scrollregion=self.rungrid.bbox("all"))


			ut = threading.Thread(target=self.delayed_UpdateRunStats)
			ut.start()

	def ClickStop(self, _event=None):
		if base.run_end < int(time.time()):
			base.debugmsg(5, "Stop Clicked nth time")

			if not base.run_abort and base.run_finish < 1:
				# dialog really abort run???
				base.debugmsg(5, "dialog really abort run???")
				# reallyabort = True
				# reallyabort = tkm.askyesno('RFSwarm - Abort Run','Do you want to abort this run? Clicking yes will kill all running robots!')
				reallyabort = tkm.askyesno('RFSwarm - Abort Run','Do you want to abort this run? Clicking yes will kill all running robots!', icon='warning')
				# reallyabort = tkm.askyesno('RFSwarm - Abort Run','Do you want to abort this run? Clicking yes will kill all running robots!', icon='error')
				if reallyabort:
					icontext = "Aborted"
					self.icoStop = self.get_icon(icontext)
					self.elements["Run"]["btn_stop"]["image"] = self.icoStop
					core.ClickStop()
		else:
			base.debugmsg(5, "Stop Clicked 1st time")
			icontext = "Abort"
			self.icoStop = self.get_icon(icontext)
			base.debugmsg(9, "icoStop", self.icoStop)
			base.debugmsg(9, "btn_stop", self.elements["Run"]["btn_stop"])
			self.elements["Run"]["btn_stop"]["image"] = self.icoStop
			base.debugmsg(9, "btn_stop", self.elements["Run"]["btn_stop"])

			core.ClickStop()




	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# Agents
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def BuildAgent(self, a):

		if not base.args.nogui:

			agentrow = 0
			a.columnconfigure(agentrow, weight=1)
			a.rowconfigure(agentrow, weight=1) # weight=0 means don't resize with other grid rows / keep a fixed size

			ag = tk.Frame(a)
			ag.grid(row=agentrow, column=0, pady=(0, 0), sticky='news')
			ag.grid_rowconfigure(0, weight=1)
			ag.grid_columnconfigure(0, weight=1)

			self.ag_canvas = tk.Canvas(ag)
			self.ag_canvas.grid(row=0, column=0, sticky="news")

			# Link a scrollbar to the canvas
			ag_vsb = tk.Scrollbar(ag, orient="vertical", command=self.ag_canvas.yview)
			ag_vsb.grid(row=0, column=1, sticky='ns')
			self.ag_canvas.configure(yscrollcommand=ag_vsb.set)

			# Link another scrollbar to the canvas
			ag_hsb = tk.Scrollbar(ag, orient="horizontal", command=self.ag_canvas.xview)
			ag_hsb.grid(row=1, column=0, sticky='ew')
			self.ag_canvas.configure(xscrollcommand=ag_hsb.set)


			self.agenttgrid = tk.Frame(self.ag_canvas)
			# self.scriptgrid = tk.Frame(self.sg_canvas, bg="blue")
			self.ag_canvas.create_window((0, 0), window=self.agenttgrid, anchor='nw')


			base.debugmsg(6, "Column Headings")

			usr = ttk.Label(self.agenttgrid, text="  Status  ", borderwidth=2, relief="raised")
			usr.grid(column=0, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  Agent  ", borderwidth=2, relief="raised")
			usr.grid(column=2, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  Last Seen  ", borderwidth=2, relief="raised")
			usr.grid(column=4, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  Assigned  ", borderwidth=2, relief="raised")
			usr.grid(column=5, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  Robots  ", borderwidth=2, relief="raised")
			usr.grid(column=6, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  Load  ", borderwidth=2, relief="raised")
			usr.grid(column=7, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  CPU %  ", borderwidth=2, relief="raised")
			usr.grid(column=8, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  MEM %  ", borderwidth=2, relief="raised")
			usr.grid(column=10, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  NET %  ", borderwidth=2, relief="raised")
			usr.grid(column=12, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  Version  ", borderwidth=2, relief="raised")
			usr.grid(column=13, row=0, sticky="nsew")

			usr = ttk.Label(self.agenttgrid, text="  Libraries  ", borderwidth=2, relief="raised")
			usr.grid(column=15, row=0, sticky="nsew")

			# update scrollbars
			self.agenttgrid.update_idletasks()
			self.ag_canvas.config(scrollregion=self.ag_canvas.bbox("all"))


	def delayed_UpdateAgents(self):
		time.sleep(10)
		self.UpdateAgents()

	def UpdateAgents(self):
		rnum = 0
		removeagents = []
		robot_count = 0
		displayagent = True
		base.debugmsg(6, "")

		base.agenttgridupdate = int(time.time())
		agntlst = list(base.Agents.keys())
		base.debugmsg(6, "agntlst:", agntlst)
		for agnt in agntlst:
			displayagent = True
			tm = base.Agents[agnt]["LastSeen"]
			agnt_elapsed = int(time.time()) - tm
			if agnt_elapsed>60:
				removeagents.append(agnt)
				# del base.Agents[agnt]
				displayagent = False

			if displayagent:
				rnum += 1
				dt = datetime.fromtimestamp(tm)
				workingkeys = self.display_agents.keys()
				if rnum not in workingkeys:
					self.display_agents[rnum] = {}
				if "Status" not in self.display_agents[rnum]:
					self.display_agents[rnum]["Status"] = tk.StringVar()
				if "Agent" not in self.display_agents[rnum]:
					self.display_agents[rnum]["Agent"] = tk.StringVar()
				if "LastSeen" not in self.display_agents[rnum]:
					self.display_agents[rnum]["LastSeen"] = tk.StringVar()
				if "Robots" not in self.display_agents[rnum]:
					self.display_agents[rnum]["Robots"] = tk.StringVar()
				if "LOAD%" not in self.display_agents[rnum]:
					self.display_agents[rnum]["LOAD%"] = tk.StringVar()
				if "CPU%" not in self.display_agents[rnum]:
					self.display_agents[rnum]["CPU%"] = tk.StringVar()
				if "MEM%" not in self.display_agents[rnum]:
					self.display_agents[rnum]["MEM%"] = tk.StringVar()
				if "NET%" not in self.display_agents[rnum]:
					self.display_agents[rnum]["NET%"] = tk.StringVar()
				if "AssignedRobots" not in self.display_agents[rnum]:
					self.display_agents[rnum]["AssignedRobots"] = tk.StringVar()

				if "Version" not in self.display_agents[rnum]:
					self.display_agents[rnum]["Version"] = tk.StringVar()

				if "Libraries" not in self.display_agents[rnum]:
					self.display_agents[rnum]["Libraries"] = tk.StringVar()

				base.debugmsg(7, "UpdateAgents: base.Agents[",agnt,"]:", base.Agents[agnt])

				self.display_agents[rnum]["Status"].set("  {}  ".format(base.Agents[agnt]["Status"]))
				self.display_agents[rnum]["Agent"].set("  {}  ".format(agnt))
				self.display_agents[rnum]["LastSeen"].set("  {}  ".format(dt.isoformat(sep=' ',timespec='seconds')))
				self.display_agents[rnum]["AssignedRobots"].set("  {}  ".format(base.Agents[agnt]["AssignedRobots"]))
				self.display_agents[rnum]["Robots"].set("  {}  ".format(base.Agents[agnt]["Robots"]))
				self.display_agents[rnum]["LOAD%"].set("  {}  ".format(base.Agents[agnt]["LOAD%"]))
				self.display_agents[rnum]["CPU%"].set("  {}  ".format(base.Agents[agnt]["CPU%"]))
				self.display_agents[rnum]["MEM%"].set("  {}  ".format(base.Agents[agnt]["MEM%"]))
				self.display_agents[rnum]["NET%"].set("  {}  ".format(base.Agents[agnt]["NET%"]))

				self.display_agents[rnum]["Version"].set("    ")
				if "Properties" in base.Agents[agnt] and "RFSwarmAgent: Version" in base.Agents[agnt]["Properties"]:
					self.display_agents[rnum]["Version"].set("  {}  ".format(base.Agents[agnt]["Properties"]["RFSwarmAgent: Version"]))
				self.display_agents[rnum]["Libraries"].set("    ")
				if "Properties" in base.Agents[agnt] and "RobotFramework: Libraries" in base.Agents[agnt]["Properties"]:
					self.display_agents[rnum]["Libraries"].set("  {}  ".format(base.Agents[agnt]["Properties"]["RobotFramework: Libraries"]))

				base.debugmsg(9, "UpdateAgents: display_agents:", self.display_agents)

			robot_count += base.Agents[agnt]["Robots"]

			grdrows = self.agenttgrid.grid_size()[1]
			if grdrows>0:
				grdrows += -1
			base.debugmsg(9, "grdrows:", grdrows, "	rnum:", rnum)
			if grdrows<rnum:
				self.add_agent_row(rnum)

		self.display_run['total_robots'].set("  {}  ".format(base.total_robots))
		base.debugmsg(9, "total_robots:", base.total_robots)
		if base.total_robots>0:
			# etm = time.gmtime(int(time.time()) - base.robot_schedule["Start"])
			etm = int(time.time()) - base.robot_schedule["Start"]
			# self.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))
			self.display_run['elapsed_time'].set("  {}  ".format(base.sec2hms(etm)))

		grdrows = self.agenttgrid.grid_size()[1]-1
		while grdrows>rnum:
			base.debugmsg(9, "grdrows",grdrows)
			try:
				self.UA_removerow(grdrows)
				self.display_agents[grdrows]
			except Exception as e:
				base.debugmsg(1, "grdrows:", grdrows, "Exception:", e)
			grdrows += -1


		# update scrollbars
		self.agenttgrid.update_idletasks()
		self.ag_canvas.config(scrollregion=self.ag_canvas.bbox("all"))


	def add_agent_row(self, rnum):
		base.debugmsg(9, "add_row: rnum:", rnum)
		base.debugmsg(9, "add_row: Status:", self.display_agents[rnum]["Status"])
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Status"], borderwidth=2, relief="groove")
		usr.grid(column=0, row=rnum, sticky="nsew")
		base.debugmsg(9, "add_row: Agent:", self.display_agents[rnum]["Agent"])
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Agent"], borderwidth=2, relief="groove")
		usr.grid(column=2, row=rnum, sticky="nsew")
		base.debugmsg(9, "add_row: LastSeen:", self.display_agents[rnum]["LastSeen"])
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["LastSeen"], borderwidth=2, relief="groove")
		usr.grid(column=4, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["AssignedRobots"], borderwidth=2, relief="groove")
		usr.grid(column=5, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Robots"], borderwidth=2, relief="groove")
		usr.grid(column=6, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["LOAD%"], borderwidth=2, relief="groove")
		usr.grid(column=7, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["CPU%"], borderwidth=2, relief="groove")
		usr.grid(column=8, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["MEM%"], borderwidth=2, relief="groove")
		usr.grid(column=10, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["NET%"], borderwidth=2, relief="groove")
		usr.grid(column=12, row=rnum, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Version"], borderwidth=2, relief="groove")
		usr.grid(column=13, row=rnum, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Libraries"], borderwidth=2, relief="groove")
		usr.grid(column=15, row=rnum, sticky="nsew")


		# update scrollbars
		self.agenttgrid.update_idletasks()
		self.ag_canvas.config(scrollregion=self.ag_canvas.bbox("all"))


	def UA_removerow(self, r):
		relmts = self.agenttgrid.grid_slaves(row=r, column=None)
		base.debugmsg(9, relmts)
		for elmt in relmts:
			elmt.destroy()

		# update scrollbars
		self.agenttgrid.update_idletasks()
		self.ag_canvas.config(scrollregion=self.ag_canvas.bbox("all"))


	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# menu functions
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def mnu_file_New(self, _event=None):
		base.debugmsg(9, "mnu_file_New")
		if len(base.config['Plan']['ScenarioFile'])>0:
			self.mnu_file_Close()

		self.updateTitle()
		while base.scriptcount > 0:
			self.sr_remove_row(base.scriptcount)
			base.scriptcount += -1
		base.scriptlist = [{}]
		base.addScriptRow()

	def mnu_file_Open(self, _event=None):
		base.debugmsg(9, "mnu_file_Open")
		base.debugmsg(9, "mnu_file_Open: _event:", _event, "	Type:", type(_event))
		# if type(_event) is not "<class 'str'>":
		if type(_event) is not type(""):
			self.mnu_file_Close()	# ensure any previous scenario is closed and saved if required
			ScenarioFile = str(tkf.askopenfilename(initialdir=base.config['Plan']['ScenarioDir'], title = "Select RFSwarm Scenario File", filetypes = (("RFSwarm","*.rfs"),("all files","*.*"))))
		else:
			ScenarioFile = _event

		base.debugmsg(6, "ScenarioFile:", ScenarioFile)

		core.OpenFile(ScenarioFile)
		base.gui.updateTitle()

		self.plan_scnro_chngd = False

	def mnu_file_Save(self, _event=None):
		base.debugmsg(9, "mnu_file_Save")
		if len(base.config['Plan']['ScenarioFile'])<1:
			self.mnu_file_SaveAs()
		else:

			base.debugmsg(8, "ScenarioFile:", base.config['Plan']['ScenarioFile'])
			base.debugmsg(8, "scriptlist:", base.scriptlist)
			filedata = configparser.ConfigParser()

			if 'Scenario' not in filedata:
				filedata['Scenario'] = {}

			scriptidx = str(0)
			if 'ScriptCount' not in filedata['Scenario']:
				# filedata['Scenario']['ScriptCount'] = str(len(base.scriptlist)-1)
				filedata['Scenario']['ScriptCount'] = scriptidx

			scriptcount = 0
			for scrp in base.scriptlist:
				base.debugmsg(8, "scrp:", scrp)
				if 'Index' in scrp:
					scrpcopy = scrp.copy()
					scriptcount += 1
					scriptidx = str(scriptcount)
					if 'Script' in scrpcopy:
						relpath = base.get_relative_path(base.config['Plan']['ScenarioFile'], scrp['Script'])
						base.debugmsg(8, "relpath:", relpath)
						scrpcopy['Script'] = relpath

					if scriptidx not in filedata:
						filedata[scriptidx] = {}
					for key in scrpcopy.keys():
						base.debugmsg(8, "key:", key)
						if key not in ['Index', 'TestVar', 'ScriptHash']:
							filedata[scriptidx][key] = str(scrpcopy[key])
							base.debugmsg(8, "filedata[",scriptidx,"][",key,"]:", filedata[scriptidx][key])

			filedata['Scenario']['ScriptCount'] = scriptidx
			with open(base.config['Plan']['ScenarioFile'], 'w') as sf:    # save
			    filedata.write(sf)

			self.updateTitle()

	def mnu_file_SaveAs(self, _event=None):
		base.debugmsg(9, "mnu_file_SaveAs")
		# asksaveasfilename
		ScenarioFile = str(tkf.asksaveasfilename(\
						initialdir=base.config['Plan']['ScenarioDir'], \
						title = "Save RFSwarm Scenario File", \
						filetypes = (("RFSwarm","*.rfs"),("all files","*.*"))\
						))
		base.debugmsg(9, "mnu_file_SaveAs: ScenarioFile:", ScenarioFile)
		if ScenarioFile is not None and len(ScenarioFile)>0:
			# ScenarioFile
			filetupl = os.path.splitext(ScenarioFile)
			base.debugmsg(9, "mnu_file_SaveAs: filetupl:", filetupl)
			if filetupl[1] != ".rfs":
				ScenarioFile += ".rfs"
				base.debugmsg(9, "mnu_file_SaveAs: ScenarioFile:", ScenarioFile)
			base.config['Plan']['ScenarioFile'] = ScenarioFile
			self.mnu_file_Save()

	def mnu_file_Close(self, _event=None):
		base.debugmsg(9, "mnu_file_Close")
		if self.plan_scnro_chngd:
			MsgBox = tkm.askyesno('RFSwarm - Save Scenario','Do you want to save the current scenario?')
			base.debugmsg(9, "mnu_file_Close: MsgBox:", MsgBox)
			if MsgBox:
				self.mnu_file_Save()

		base.config['Plan']['ScenarioFile'] = ""
		self.mnu_file_New()


	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# End class RFSwarmGUI
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
