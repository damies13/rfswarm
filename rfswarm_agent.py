#!/usr/bin/python
#
#	Robot Framework Swarm
#
#    Version v0.4.5-alpha
#


# https://stackoverflow.com/questions/48090535/csv-file-reading-and-find-the-value-from-nth-column-using-robot-framework

import sys
import os
import tempfile
import configparser

import lzma
import base64



# import robot

import random
import time
from datetime import datetime
import threading
import subprocess
import requests
import psutil
# import platform
import socket
import json
import xml.etree.ElementTree as ET
import shutil

import argparse

class RFSwarmAgent():

	version = "v0.4.5-alpha"
	config = None
	isconnected = False
	isrunning = False
	isstopping = False
	run_name = None
	swarmserver = None
	agentdir = None
	scriptdir = None
	logdir = None
	agentini = None
	ipaddresslist = []
	netpct = 0
	mainloopinterval = 10
	scriptlist = {}
	jobs = {}
	robotcount = 0
	status = "Ready"
	excludelibraries = []
	args = None

	def __init__(self, master=None):
		print("Robot Framework Swarm: Run Agent")
		print("	Version", self.version)
		# print("RFSwarmAgent: __init__")
		# print("gettempdir", tempfile.gettempdir())
		# print("tempdir", tempfile.tempdir)

		parser = argparse.ArgumentParser()
		# parser.add_argument('--foo', help='foo help')
		parser.add_argument('-v', '--version', help='Display the version and exit', action='store_true')
		parser.add_argument('-i', '--ini', nargs='?', help='path to alternate ini file')
		parser.add_argument('-s', '--server', nargs='?', help='The server to connect to e.g. http://localhost:8138/')
		parser.add_argument('-d', '--agentdir', nargs='?', help='The directory the agent should use for files')
		parser.add_argument('-r', '--robot', nargs='?', help='The robot framework executable')
		self.args = parser.parse_args()

		if self.args.version:
			exit()


		self.config = configparser.ConfigParser()
		scrdir = os.path.dirname(__file__)
		# print("RFSwarmAgent: __init__: scrdir: ", scrdir)
		self.agentini = os.path.join(scrdir, "RFSwarmAgent.ini")

		if self.args.ini:
			print("RFSwarmAgent: __init__: self.args.ini: ", self.args.ini)
			self.agentini = self.args.ini

		if os.path.isfile(self.agentini):
			# print("RFSwarmAgent: __init__: agentini: ", self.agentini)
			self.config.read(self.agentini)
		else:
			self.saveini()



		if 'Agent' not in self.config:
			self.config['Agent'] = {}
			self.saveini()

		if 'agentdir' not in self.config['Agent']:
			self.config['Agent']['agentdir'] = os.path.join(tempfile.gettempdir(), "rfswarmagent")
			self.saveini()


		self.agentdir = self.config['Agent']['agentdir']
		if self.args.agentdir:
			print("RFSwarmAgent: __init__: self.args.agentdir: ", self.args.agentdir)
			self.agentdir = self.args.agentdir
		self.ensuredir(self.agentdir)

		self.scriptdir = os.path.join(self.agentdir, "scripts")
		self.ensuredir(self.scriptdir)

		self.logdir = os.path.join(self.agentdir, "logs")
		self.ensuredir(self.logdir)


		if 'excludelibraries' not in self.config['Agent']:
			self.config['Agent']['excludelibraries'] = "BuiltIn,String,OperatingSystem,perftest"
			self.saveini()

		# self.excludelibraries = ["BuiltIn", "String", "OperatingSystem", "perftest"]
		self.excludelibraries = self.config['Agent']['excludelibraries'].split(",")
		# print("RFSwarmAgent: __init__: self.excludelibraries:", self.excludelibraries)

	def mainloop(self):
		# print("RFSwarmAgent: mainloop")
		prev_status = self.status
		while True:
			print("RFSwarmAgent: mainloop: Running", datetime.now().isoformat(sep=' ',timespec='seconds'),
				"(",int(time.time()),")"
				"isconnected:", self.isconnected,
				"isrunning:", self.isrunning,
				"isstopping:", self.isstopping
			)

			if not self.isconnected:
				# self.isrunning = False # Not sure if I need this?
				# self.connectserver()
				t = threading.Thread(target=self.connectserver)
				t.start()
				self.isrunning = False

			if self.isconnected:
				# self.updatestatus()
				t0 = threading.Thread(target=self.updatestatus)
				t0.start()

				t1 = threading.Thread(target=self.getjobs)
				t1.start()

				if self.isrunning:
					self.mainloopinterval = 2
					self.status = "Running"
					if self.isstopping:
						self.status = "Stopping"
					# else:
					t2 = threading.Thread(target=self.runjobs)
					t2.start()
				else:
					self.status = "Ready"
					self.mainloopinterval = 10
					t2 = threading.Thread(target=self.getscripts)
					t2.start()

			if prev_status == "Stopping" and self.status == "Ready":
				# neet to reset something
				# I guess we can just reset the jobs disctionary?
				self.jobs = {}
				# pass

			time.sleep(self.mainloopinterval)

	def updateipaddresslist(self):
		if len(self.ipaddresslist)<1:
			self.ipaddresslist = []
			iflst = psutil.net_if_addrs()
			for nic in iflst.keys():
				# print("nic", nic)
				for addr in iflst[nic]:
					 # '127.0.0.1', '::1', 'fe80::1%lo0'
					# print("addr", addr.address)
					if addr.address not in ['127.0.0.1', '::1', 'fe80::1%lo0']:
						self.ipaddresslist.append(addr.address)

	def updatenetpct(self):
		netpctlist = []
		# self.netpct = 0
		niccounters0 = psutil.net_io_counters(pernic=True)
		time.sleep(1)
		niccounters1 = psutil.net_io_counters(pernic=True)
		nicstats = psutil.net_if_stats()
		for nic in nicstats.keys():
			if nicstats[nic].speed>0:
				# print("Speed:", nicstats[nic].speed)
				bytes_speed = nicstats[nic].speed * 1024 * 1024
				bytes_sent_sec = niccounters1[nic].bytes_sent - niccounters0[nic].bytes_sent
				bytes_recv_sec = niccounters1[nic].bytes_recv - niccounters0[nic].bytes_recv
				# print("bytes_speed:	", bytes_speed)
				# print("bytes_sent_sec:	", bytes_sent_sec)
				# print("bytes_recv:	", bytes_recv_sec)
				bytes_max_sec = max([bytes_sent_sec, bytes_recv_sec])
				# print("bytes_max_sec:	", bytes_max_sec)
				if bytes_max_sec > 0:
					netpctlist.append((bytes_max_sec/bytes_speed)*100)
				else:
					netpctlist.append(0)

		if len(netpctlist)>0:
			# print("netpctlist:	", netpctlist)
			self.netpct = max(netpctlist)
			# print("self.netpct:	", self.netpct)
		else:
			self.netpct = 0


	def updatestatus(self):
		# print("self.swarmserver:", self.swarmserver)
		uri = self.swarmserver + "AgentStatus"

		# self.updateipaddresslist()
		t1 = threading.Thread(target=self.updateipaddresslist)
		t1.start()
		# self.updatenetpct()
		t2 = threading.Thread(target=self.updatenetpct)
		t2.start()

		payload = {
			"AgentName": socket.gethostname(),
			"AgentFQDN": socket.getfqdn(),
			"AgentIPs": self.ipaddresslist,
			"CPU%": psutil.cpu_percent(),
			"MEM%": dict(psutil.virtual_memory()._asdict())["percent"],
			"NET%": self.netpct,
			"Robots": self.robotcount,
			"Status": self.status
		}
		try:
			r = requests.post(uri, json=payload)
			# print(r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False
		except:
			# print(r.status_code, r.text)
			print("Server Disconected", datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

	def connectserver(self):
		# print("RFSwarmAgent: connectserver")
		if self.swarmserver is None:
			self.findserver()
		if self.swarmserver is not None:
			print("RFSwarmAgent: connectserver: Try connecting to", self.swarmserver)
			# print("self.swarmserver:", self.swarmserver)
			try:
				r = requests.get(self.swarmserver)
				# print(r.status_code, r.text)
				if (r.status_code == requests.codes.ok):
					self.isconnected = True
			except:
				pass

	def findserver(self):
		# print("RFSwarmAgent: findserver")
		# print("RFSwarmAgent: findserver:", self.config)
		if 'Agent' in self.config:
			# print("RFSwarmAgent: findserver:", self.config['Agent'])
			pass
		else:
			self.config['Agent'] = {}
			self.saveini()

		if 'swarmserver' in self.config['Agent']:
			# print("RFSwarmAgent: findserver: Agent:swarmserver =", self.config['Agent']['swarmserver'])
			self.swarmserver = self.config['Agent']['swarmserver']
		else:
			self.config['Agent']['swarmserver'] = "http://localhost:8138/"
			self.saveini()


	def getscripts(self):
		# print("getscripts")
		uri = self.swarmserver + "Scripts"
		payload = {
			"AgentName": socket.gethostname()
		}
		# print("getscripts: payload: ", payload)
		try:
			r = requests.post(uri, json=payload)
			# print("getscripts: resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False

		except Exception as e:
			# print("getscripts: Exception:", e)
			print("Server Disconected", datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			# print("getscripts: jsonresp:", jsonresp)
		except Exception as e:
			print("getscripts: Exception:", e)

		for s in jsonresp["Scripts"]:
			hash = s['Hash']
			# print("getscripts: hash:", hash)
			if hash not in self.scriptlist:
				self.scriptlist[hash] = {'id': hash}
				t = threading.Thread(target=self.getfile, args=(hash,))
				t.start()

	def getfile(self, hash):
		# print("getfile: hash: ", hash)
		uri = self.swarmserver + "File"
		payload = {
			"AgentName": socket.gethostname(),
			"Hash": hash
		}
		try:
			r = requests.post(uri, json=payload)
			# print("getfile: resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False

		except Exception as e:
			print("Server Disconected", datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			# print("getfile: jsonresp:", jsonresp)
		except Exception as e:
			print("getfile: Exception:", e)

		try:
			# print('scriptdir', self.scriptdir)
			localfile = os.path.abspath(os.path.join(self.scriptdir, jsonresp['File']))
			print('getfile: localfile', localfile)

		except Exception as e:
			print("getfile: Exception:", e)

		try:
			self.scriptlist[hash]['localfile'] = localfile
			self.scriptlist[hash]['file'] = jsonresp['File']

			# self.scriptlist[hash][]

			filedata = jsonresp['FileData']
			# print("filedata:", filedata)
			# print("getfile: filedata:")

			decoded = base64.b64decode(filedata)
			# print("b64decode: decoded:", decoded)
			# print("getfile: b64decode:")

			uncompressed = lzma.decompress(decoded)
			# print("uncompressed:", uncompressed)
			# print("getfile: uncompressed:")

			localfiledir = os.path.dirname(localfile)
			# print("getfile: localfiledir:", localfiledir)
			self.ensuredir(localfiledir)
			# print("getfile: ensuredir:")

			with open(localfile, 'wb') as afile:
				# print("getfile: afile:")
				afile.write(uncompressed)
				# print("getfile: write:")

		except Exception as e:
			print("getfile: Exception:", e)

	def getjobs(self):
		# print("getjobs")
		uri = self.swarmserver + "Jobs"
		payload = {
			"AgentName": socket.gethostname()
		}
		# print("getjobs: payload: ", payload)
		try:
			r = requests.post(uri, json=payload)
			# print("getjobs: resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False

		except Exception as e:
			print("Server Disconected", datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			# print("getjobs: r.text:", r.text)
			jsonresp = json.loads(r.text)
			# print("getjobs: jsonresp:", jsonresp)


			if jsonresp["StartTime"] < int(time.time()) < (jsonresp["EndTime"]+300):
				self.isrunning = True
				self.run_name = jsonresp["RunName"]
				for s in jsonresp["Schedule"].keys():
					# print("getjobs: s:", s)
					if s not in self.jobs.keys():
						self.jobs[s] = {}
					for k in jsonresp["Schedule"][s].keys():
						# print("getjobs: self.jobs[",s,"][",k,"]", jsonresp["Schedule"][s][k])
						self.jobs[s][k] = jsonresp["Schedule"][s][k]

				if int(time.time()) > jsonresp["EndTime"]:
					self.isstopping = True
				if self.isstopping and self.robotcount < 1:
					self.jobs = {}
					self.isrunning = False
					self.isstopping = False
			else:
				if self.robotcount < 1:
					self.isrunning = False
					self.isstopping = False
				else:
					self.isstopping = True

			# print("getjobs: isrunning:", self.isrunning, "	isstopping:", self.isstopping)
			# print("getjobs: self.jobs:", self.jobs)



		except Exception as e:
			print("getjobs: Exception:", e)

	def runjobs(self):
		# print("runjobs: self.jobs:", self.jobs)
		workingkeys = list(self.jobs.keys())
		for jobid in workingkeys:
			if jobid in self.jobs.keys():
				# print("runjobs: jobid:", jobid)
				run_t = True
				if "Thread" in self.jobs[jobid].keys():
					if self.jobs[jobid]["Thread"].isAlive():
						run_t = False
						# print("runjobs: Thread already running run_t:", run_t)

				# print("runjobs: run_t:", run_t)

				if run_t and self.jobs[jobid]["StartTime"] < int(time.time()) < self.jobs[jobid]["EndTime"]:
					t = threading.Thread(target=self.runthread, args=(jobid, ))
					t.start()
					self.jobs[jobid]["Thread"] = t
				time.sleep(0.1)


	def runthread(self, jobid):
		now = int(time.time())
		if "ScriptIndex" not in self.jobs[jobid]:
			# print("runthread: jobid:", jobid)
			# print("runthread: job data:", self.jobs[jobid])
			jobarr = jobid.split("_")
			self.jobs[jobid]["ScriptIndex"] = jobarr[0]
			self.jobs[jobid]["VUser"] = jobarr[1]
			self.jobs[jobid]["Iteration"] = 0
			# print("runthread: job data:", self.jobs[jobid])

		self.jobs[jobid]["Iteration"] += 1

		hash = self.jobs[jobid]['ScriptHash']
		# print("runthread: hash:", hash)
		test = self.jobs[jobid]['Test']
		# print("runthread: test:", test)
		localfile = self.scriptlist[hash]['localfile']
		# print("runthread: localfile:", localfile)

		file = self.scriptlist[hash]['file']
		# print("runthread: file:", file)

		farr = os.path.splitext(file)
		# print("runthread: farr:", farr)

		# self.run_name
		# scriptdir = None
		# logdir = None

		rundir = os.path.join(self.logdir, self.run_name)
		try:
			if not os.path.exists(rundir):
				os.makedirs(rundir)
		except:
			pass

		threaddirname = self.make_safe_filename("{}_{}_{}".format(farr[0], jobid, now))
		odir = os.path.join(self.logdir, self.run_name, threaddirname)
		# print("runthread: odir:", odir)
		try:
			if not os.path.exists(odir):
				os.makedirs(odir)
		except:
			pass

		oprefix = self.make_safe_filename(test)
		# print("runthread: oprefix:", oprefix)
		logFileName = os.path.join(odir, "{}.log".format(oprefix))
		# print("runthread: logFileName:", logFileName)
		outputFileName = "{}_output.xml".format(oprefix)
		outputFile = os.path.join(odir, outputFileName)
		# print("runthread: outputFile:", outputFile)


		if 'Agent' not in self.config:
			self.config['Agent'] = {}
			self.saveini()

		if 'robotcmd' not in self.config['Agent']:
			self.config['Agent']['robotcmd'] = "robot"
			self.saveini()

		robotcmd = self.config['Agent']['robotcmd']

		cmd = [robotcmd]
		cmd.append("-t")
		cmd.append('"'+test+'"')
		# cmd.append(testcs)
		cmd.append("-d")
		cmd.append(odir)

		cmd.append("-v index:{}".format(self.jobs[jobid]["ScriptIndex"]))
		cmd.append("-v vuser:{}".format(self.jobs[jobid]["VUser"]))
		cmd.append("-v iteration:{}".format(self.jobs[jobid]["Iteration"]))

		cmd.append("-o")
		cmd.append(outputFile)

		cmd.append(localfile)

		robotexe = shutil.which(robotcmd)
		# print("runthread: robotexe:", robotexe)
		if robotexe is not None:
			self.robotcount += 1

			# result = subprocess.call(" ".join(cmd), shell=True)
			# https://stackoverflow.com/questions/4856583/how-do-i-pipe-a-subprocess-call-to-a-text-file
			with open(logFileName, "w") as f:
				# result = subprocess.call(" ".join(cmd), shell=True, stdout=f, stderr=f)
				result = subprocess.call(" ".join(cmd), shell=True, stdout=f, stderr=subprocess.STDOUT)
				# print("runthread: result:", result)
				if result != 0:
					print("Robot returned an error (", result, ") please check the log file:", logFileName)

			if os.path.exists(outputFile):
				t = threading.Thread(target=self.run_process_output, args=(outputFile, self.jobs[jobid]["ScriptIndex"], self.jobs[jobid]["VUser"], self.jobs[jobid]["Iteration"]))
				t.start()
			else:
				print("Robot didn't create (", outputFile, ") please check the log file:", logFileName)

			self.robotcount += -1
		else:
			print("Could not find robot executeable:", robotexe)

	def run_process_output(self, outputFile, index, vuser, iter):
		# This should be a better way to do this
		# https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
		# https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-examples

		seq = 0
		# .//kw[@library!='BuiltIn' and msg]
		# .//kw[@library!='BuiltIn' and msg]/msg
		# .//kw[@library!='BuiltIn' and msg]/status/@status
		# .//kw[@library!='BuiltIn' and msg]/status/@starttime
		# .//kw[@library!='BuiltIn' and msg]/status/@endtime
		try:
			tree = ET.parse(outputFile)
		except:
			print("Error parsing XML file:", outputFile)
		# print("tree: '", tree)
		root = tree.getroot()
		# print("root: '", root)
		# .//kw/msg/..[not(@library='BuiltIn')]
		for result in root.findall(".//kw/msg/..[@library]"):
			# print("run_process_output: result: ", result)
			library = result.get('library')
			# if library not in ["BuiltIn", "String", "OperatingSystem", "perftest"]:
			if library not in self.excludelibraries:
				# print("run_process_output: library: ", library)
				seq += 1
				# print("result: library:", library)
				txn = result.find('msg').text
				# print("result: txn:", txn)

				el_status = result.find('status')
				status = el_status.get('status')
				# print("result: status:", status)
				starttime = el_status.get('starttime')
				# print("result: starttime:", starttime)
				endtime = el_status.get('endtime')
				# print("result: endtime:", endtime)

				# 20191026 09:34:23.044
				startdate = datetime.strptime(starttime, '%Y%m%d %H:%M:%S.%f')
				enddate = datetime.strptime(endtime, '%Y%m%d %H:%M:%S.%f')

				elapsedtime = enddate.timestamp() - startdate.timestamp()

				# print("resultname: '", txn,
				# 		"' result'", status,
				# 		"' elapsedtime'", elapsedtime,
				# 		"' starttime'", starttime,
				# 		"' endtime'", endtime, "'"
				# 		)


				# Send result to server
				uri = self.swarmserver + "Result"
				# print("run_proces_output: uri", uri)

				# requiredfields = ["AgentName", "ResultName", "Result", "ElapsedTime", "StartTime", "EndTime"]

				payload = {
					"AgentName": socket.gethostname(),
					"ResultName": txn,
					"Result": status,
					"ElapsedTime": elapsedtime,
					"StartTime": startdate.timestamp(),
					"EndTime": enddate.timestamp(),
					"ScriptIndex": index,
					"VUser": vuser,
					"Iteration": iter,
					"Sequence": seq
				}

				# print("run_proces_output: payload", payload)
				try:
					r = requests.post(uri, json=payload)
					# print("run_proces_output: ",r.status_code, r.text)
					if (r.status_code != requests.codes.ok):
						self.isconnected = False
				except Exception as e:
					# print("run_proces_output: ",r.status_code, r.text)
					# print("run_proces_output: Exception: ", e)
					print("Server Disconected", datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
					self.isconnected = False



	def make_safe_filename(self, s):
		def safe_char(c):
			if c.isalnum():
				return c
			else:
				return "_"
		return "".join(safe_char(c) for c in s).rstrip("_")

	def saveini(self):
		with open(self.agentini, 'w') as configfile:    # save
		    self.config.write(configfile)

	def ensuredir(self, dir):
		try:
			os.mkdir(dir, mode=0o777)
			# print("Directory Created: ", dir)
		except FileExistsError:
			# print("Directory Exists: ", dir)
			pass
		except Exception as e:
			print("Directory Create failed: ", dir)
			print("with error: ", e)


rfsa = RFSwarmAgent()
try:
	rfsa.mainloop()
except KeyboardInterrupt:
	pass
except Exception as e:
	print("rfsa.Exception:", e)
	pass
