#!/usr/bin/python
#
#	Robot Framework Swarm
#
#    Version v0.6.1-beta
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
import inspect


class RFSwarmAgent():

	version="0.6.1"
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
	listenerfile = None
	ipaddresslist = []
	agentname = None
	netpct = 0
	mainloopinterval = 10
	scriptlist = {}
	jobs = {}
	robotcount = 0
	status = "Ready"
	excludelibraries = []
	args = None
	xmlmode = False

	debuglvl = 0

	def __init__(self, master=None):
		self.debugmsg(0, "Robot Framework Swarm: Run Agent")
		self.debugmsg(0, "	Version", self.version)
		self.debugmsg(6, "__init__")
		self.debugmsg(6, "gettempdir", tempfile.gettempdir())
		self.debugmsg(6, "tempdir", tempfile.tempdir)

		parser = argparse.ArgumentParser()
		parser.add_argument('-g', '--debug', help='Set debug level, default level is 0')
		parser.add_argument('-v', '--version', help='Display the version and exit', action='store_true')
		parser.add_argument('-i', '--ini', help='path to alternate ini file')
		parser.add_argument('-s', '--server', help='The server to connect to e.g. http://localhost:8138/')
		parser.add_argument('-d', '--agentdir', help='The directory the agent should use for files')
		parser.add_argument('-r', '--robot', help='The robot framework executable')
		parser.add_argument('-x', '--xmlmode', help='XML Mode, fall back to pasing the output.xml after each iteration', action='store_true')
		parser.add_argument('-a', '--agentname', help='Set agent name')
		self.args = parser.parse_args()

		self.debugmsg(6, "self.args: ", self.args)

		if self.args.debug:
			self.debuglvl = int(self.args.debug)


		if self.args.version:
			exit()


		self.config = configparser.ConfigParser()
		scrdir = os.path.dirname(__file__)
		self.debugmsg(6, "scrdir: ", scrdir)
		self.agentini = os.path.join(scrdir, "RFSwarmAgent.ini")

		if self.args.ini:
			self.debugmsg(1, "self.args.ini: ", self.args.ini)
			self.agentini = self.args.ini

		if os.path.isfile(self.agentini):
			self.debugmsg(6, "agentini: ", self.agentini)
			self.config.read(self.agentini)
		else:
			self.saveini()

		self.debugmsg(0, "	Configuration File: ", self.agentini)

		self.agentname = socket.gethostname()
		if self.args.agentname:
			self.agentname = self.args.agentname


		if 'Agent' not in self.config:
			self.config['Agent'] = {}
			self.saveini()

		if 'agentname' not in self.config['Agent']:
			self.config['Agent']['agentname'] = self.agentname
			self.saveini()
		else:
			self.agentname = self.config['Agent']['agentname']

		if 'agentdir' not in self.config['Agent']:
			self.config['Agent']['agentdir'] = os.path.join(tempfile.gettempdir(), "rfswarmagent")
			self.saveini()

		if 'xmlmode' not in self.config['Agent']:
			self.config['Agent']['xmlmode'] = str(self.xmlmode)
			self.saveini()

		self.xmlmode = self.str2bool(self.config['Agent']['xmlmode'])
		if self.args.xmlmode:
			self.debugmsg(6, "self.args.xmlmode: ", self.args.xmlmode)
			self.xmlmode = self.str2bool(self.args.xmlmode)

		self.agentdir = self.config['Agent']['agentdir']
		if self.args.agentdir:
			self.debugmsg(1, "self.args.agentdir: ", self.args.agentdir)
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
		self.debugmsg(6, "self.excludelibraries:", self.excludelibraries)

		if not self.xmlmode:
			self.debugmsg(6, "self.xmlmode: ", self.xmlmode)
			self.create_listner_file()



	def debugmsg(self, lvl, *msg):
		msglst = []
		prefix = ""
		# print(self.debuglvl >= lvl, self.debuglvl, lvl, *msg)
		if self.debuglvl >= lvl:
			try:
				if self.debuglvl >= 4:
					stack = inspect.stack()
					the_class = stack[1][0].f_locals["self"].__class__.__name__
					the_method = stack[1][0].f_code.co_name
					prefix = "{}: {}: [{}:{}]	".format(str(the_class), the_method, self.debuglvl, lvl)
					if len(prefix.strip())<32:
						prefix = "{}	".format(prefix)
					if len(prefix.strip())<24:
						prefix = "{}	".format(prefix)

					msglst.append(str(prefix))

				for itm in msg:
					msglst.append(str(itm))
				print(" ".join(msglst))
			except:
				pass

	def str2bool(self, instr):
		return str(instr).lower()  in ("yes", "true", "t", "1")

	def mainloop(self):
		self.debugmsg(6, "mainloop")
		prev_status = self.status
		while True:
			self.debugmsg(2, "Running", datetime.now().isoformat(sep=' ',timespec='seconds'),
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
				self.debugmsg(6, "nic", nic)
				for addr in iflst[nic]:
					 # '127.0.0.1', '::1', 'fe80::1%lo0'
					self.debugmsg(6, "addr", addr.address)
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
				self.debugmsg(6, "Speed:", nicstats[nic].speed)
				bytes_speed = nicstats[nic].speed * 1024 * 1024
				bytes_sent_sec = niccounters1[nic].bytes_sent - niccounters0[nic].bytes_sent
				bytes_recv_sec = niccounters1[nic].bytes_recv - niccounters0[nic].bytes_recv
				self.debugmsg(6, "bytes_speed:	", bytes_speed)
				self.debugmsg(6, "bytes_sent_sec:	", bytes_sent_sec)
				self.debugmsg(6, "bytes_recv:	", bytes_recv_sec)
				bytes_max_sec = max([bytes_sent_sec, bytes_recv_sec])
				self.debugmsg(6, "bytes_max_sec:	", bytes_max_sec)
				if bytes_max_sec > 0:
					netpctlist.append((bytes_max_sec/bytes_speed)*100)
				else:
					netpctlist.append(0)

		if len(netpctlist)>0:
			self.debugmsg(6, "netpctlist:	", netpctlist)
			self.netpct = max(netpctlist)
			self.debugmsg(6, "self.netpct:	", self.netpct)
		else:
			self.netpct = 0


	def updatestatus(self):
		self.debugmsg(6, "self.swarmserver:", self.swarmserver)
		uri = self.swarmserver + "AgentStatus"

		# self.updateipaddresslist()
		t1 = threading.Thread(target=self.updateipaddresslist)
		t1.start()
		# self.updatenetpct()
		t2 = threading.Thread(target=self.updatenetpct)
		t2.start()

		payload = {
			"AgentName": self.agentname,
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
			self.debugmsg(8, r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False
		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Server Disconected", self.swarmserver, datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

	def connectserver(self):
		self.debugmsg(6, "connectserver")
		if self.swarmserver is None:
			self.findserver()
			if self.args.server:
				self.debugmsg(5, "self.args.server: ", self.args.server)
				self.swarmserver = self.args.server

		if self.swarmserver is not None:
			self.debugmsg(2, "Try connecting to", self.swarmserver)
			self.debugmsg(6, "self.swarmserver:", self.swarmserver)
			try:
				r = requests.get(self.swarmserver)
				self.debugmsg(6, r.status_code, r.text)
				if (r.status_code == requests.codes.ok):
					self.isconnected = True
					self.debugmsg(0, "Server Conected", self.swarmserver, datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			except:
				pass

	def findserver(self):
		self.debugmsg(6, "findserver")
		self.debugmsg(6, "findserver:", self.config)
		if 'Agent' in self.config:
			self.debugmsg(6, "findserver:", self.config['Agent'])
			pass
		else:
			self.config['Agent'] = {}
			self.saveini()

		if 'swarmserver' in self.config['Agent']:
			self.debugmsg(6, "findserver: Agent:swarmserver =", self.config['Agent']['swarmserver'])
			self.swarmserver = self.config['Agent']['swarmserver']
		else:
			self.config['Agent']['swarmserver'] = "http://localhost:8138/"
			self.saveini()


	def getscripts(self):
		self.debugmsg(6, "getscripts")
		uri = self.swarmserver + "Scripts"
		payload = {
			"AgentName": socket.gethostname()
		}
		self.debugmsg(6, "getscripts: payload: ", payload)
		try:
			r = requests.post(uri, json=payload)
			self.debugmsg(6, "getscripts: resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False

		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Server Disconected", self.swarmserver, datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			self.debugmsg(6, "getscripts: jsonresp:", jsonresp)
		except Exception as e:
			self.debugmsg(1, "getscripts: Exception:", e)

		for s in jsonresp["Scripts"]:
			hash = s['Hash']
			self.debugmsg(6, "getscripts: hash:", hash)
			if hash not in self.scriptlist:
				self.scriptlist[hash] = {'id': hash}
				t = threading.Thread(target=self.getfile, args=(hash,))
				t.start()

	def getfile(self, hash):
		self.debugmsg(6, "hash: ", hash)
		uri = self.swarmserver + "File"
		payload = {
			"AgentName": socket.gethostname(),
			"Hash": hash
		}
		try:
			r = requests.post(uri, json=payload)
			self.debugmsg(6, "resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False

		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Server Disconected", self.swarmserver, datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			self.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			self.debugmsg(1, "Exception:", e)

		try:
			self.debugmsg(7, 'scriptdir', self.scriptdir)
			localfile = os.path.abspath(os.path.join(self.scriptdir, jsonresp['File']))
			self.debugmsg(1, 'localfile', localfile)

		except Exception as e:
			self.debugmsg(0, "Exception:", e)

		try:
			self.scriptlist[hash]['localfile'] = localfile
			self.scriptlist[hash]['file'] = jsonresp['File']

			# self.scriptlist[hash][]

			filedata = jsonresp['FileData']
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
			self.ensuredir(localfiledir)
			self.debugmsg(6, "ensuredir:")

			with open(localfile, 'wb') as afile:
				self.debugmsg(6, "afile:")
				afile.write(uncompressed)
				self.debugmsg(6, "write:")

		except Exception as e:
			self.debugmsg(1, "Exception:", e)

	def getjobs(self):
		self.debugmsg(6, "getjobs")
		uri = self.swarmserver + "Jobs"
		payload = {
			"AgentName": socket.gethostname()
		}
		self.debugmsg(6, "getjobs: payload: ", payload)
		try:
			r = requests.post(uri, json=payload)
			self.debugmsg(6, "getjobs: resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.isconnected = False

		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Server Disconected", self.swarmserver, datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			self.debugmsg(6, "getjobs: r.text:", r.text)
			jsonresp = json.loads(r.text)
			self.debugmsg(6, "getjobs: jsonresp:", jsonresp)


			if jsonresp["StartTime"] < int(time.time()) < (jsonresp["EndTime"]+300):
				self.isrunning = True
				self.run_name = jsonresp["RunName"]
				for s in jsonresp["Schedule"].keys():
					self.debugmsg(6, "getjobs: s:", s)
					if s not in self.jobs.keys():
						self.jobs[s] = {}
					for k in jsonresp["Schedule"][s].keys():
						self.debugmsg(6, "getjobs: self.jobs[",s,"][",k,"]", jsonresp["Schedule"][s][k])
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

			self.debugmsg(6, "getjobs: isrunning:", self.isrunning, "	isstopping:", self.isstopping)
			self.debugmsg(6, "getjobs: self.jobs:", self.jobs)



		except Exception as e:
			self.debugmsg(1, "getjobs: Exception:", e)

	def runjobs(self):
		self.debugmsg(6, "runjobs: self.jobs:", self.jobs)
		workingkeys = list(self.jobs.keys())
		for jobid in workingkeys:
			if jobid in self.jobs.keys():
				self.debugmsg(6, "runjobs: jobid:", jobid)
				run_t = True
				if "Thread" in self.jobs[jobid].keys():
					if self.jobs[jobid]["Thread"].isAlive():
						run_t = False
						self.debugmsg(6, "runjobs: Thread already running run_t:", run_t)

				self.debugmsg(6, "runjobs: run_t:", run_t)

				if run_t and self.jobs[jobid]["StartTime"] < int(time.time()) < self.jobs[jobid]["EndTime"]:
					t = threading.Thread(target=self.runthread, args=(jobid, ))
					t.start()
					self.jobs[jobid]["Thread"] = t
				time.sleep(0.1)


	def runthread(self, jobid):
		now = int(time.time())
		if "ScriptIndex" not in self.jobs[jobid]:
			self.debugmsg(6, "runthread: jobid:", jobid)
			self.debugmsg(6, "runthread: job data:", self.jobs[jobid])
			jobarr = jobid.split("_")
			self.jobs[jobid]["ScriptIndex"] = jobarr[0]
			self.jobs[jobid]["VUser"] = jobarr[1]
			self.jobs[jobid]["Iteration"] = 0
			self.debugmsg(6, "runthread: job data:", self.jobs[jobid])

		self.jobs[jobid]["Iteration"] += 1

		hash = self.jobs[jobid]['ScriptHash']
		self.debugmsg(6, "runthread: hash:", hash)
		test = self.jobs[jobid]['Test']
		self.debugmsg(6, "runthread: test:", test)
		localfile = self.scriptlist[hash]['localfile']
		self.debugmsg(6, "runthread: localfile:", localfile)

		file = self.scriptlist[hash]['file']
		self.debugmsg(6, "runthread: file:", file)

		farr = os.path.splitext(file)
		self.debugmsg(6, "runthread: farr:", farr)

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
		self.debugmsg(6, "runthread: odir:", odir)
		try:
			if not os.path.exists(odir):
				os.makedirs(odir)
		except:
			pass

		oprefix = self.make_safe_filename(test)
		self.debugmsg(6, "runthread: oprefix:", oprefix)
		logFileName = os.path.join(odir, "{}.log".format(oprefix))
		self.debugmsg(6, "runthread: logFileName:", logFileName)
		outputFileName = "{}_output.xml".format(oprefix)
		outputFile = os.path.join(odir, outputFileName)
		self.debugmsg(6, "runthread: outputFile:", outputFile)


		if 'Agent' not in self.config:
			self.config['Agent'] = {}
			self.saveini()

		if 'robotcmd' not in self.config['Agent']:
			self.config['Agent']['robotcmd'] = "robot"
			self.saveini()

		robotcmd = self.config['Agent']['robotcmd']
		if self.args.robot:
			self.debugmsg(1, "runthread: self.args.robot: ", self.args.robot)
			robotcmd = self.args.robot

		cmd = [robotcmd]
		cmd.append("-t")
		cmd.append('"'+test+'"')
		# cmd.append(testcs)
		cmd.append("-d")
		cmd.append('"'+odir+'"')

		if self.xmlmode:
			cmd.append("-v index:{}".format(self.jobs[jobid]["ScriptIndex"]))
			cmd.append("-v vuser:{}".format(self.jobs[jobid]["VUser"]))
			cmd.append("-v iteration:{}".format(self.jobs[jobid]["Iteration"]))
		else:
			cmd.append("-M debuglevel:{}".format(self.debuglvl))
			cmd.append("-M index:{}".format(self.jobs[jobid]["ScriptIndex"]))
			cmd.append("-M vuser:{}".format(self.jobs[jobid]["VUser"]))
			cmd.append("-M iteration:{}".format(self.jobs[jobid]["Iteration"]))
			cmd.append("-M swarmserver:{}".format(self.swarmserver))
			cmd.append("-M excludelibraries:{}".format(",".join(self.excludelibraries)))
			cmd.append("--listener {}".format('"'+self.listenerfile+'"'))

		cmd.append("-o")
		cmd.append('"'+outputFile+'"')

		cmd.append('"'+localfile+'"')

		robotexe = shutil.which(robotcmd)
		self.debugmsg(6, "runthread: robotexe:", robotexe)
		if robotexe is not None:
			self.robotcount += 1

			try:
				# result = subprocess.call(" ".join(cmd), shell=True)
				# https://stackoverflow.com/questions/4856583/how-do-i-pipe-a-subprocess-call-to-a-text-file
				with open(logFileName, "w") as f:
					self.debugmsg(3, "Robot run with command: '", " ".join(cmd), "'")
					# result = subprocess.call(" ".join(cmd), shell=True, stdout=f, stderr=f)
					try:
						result = subprocess.call(" ".join(cmd), shell=True, stdout=f, stderr=subprocess.STDOUT)
						self.debugmsg(6, "runthread: result:", result)
						if result != 0:
							self.debugmsg(1, "Robot returned an error (", result, ") please check the log file:", logFileName)
					except Exception as e:
							self.debugmsg(1, "Robot returned an error:", e, " \nplease check the log file:", logFileName)
					f.close()

				if self.xmlmode:
					if os.path.exists(outputFile):
						if self.xmlmode:
							t = threading.Thread(target=self.run_process_output, args=(outputFile, self.jobs[jobid]["ScriptIndex"], self.jobs[jobid]["VUser"], self.jobs[jobid]["Iteration"]))
							t.start()
					else:
						self.debugmsg(1, "Robot didn't create (", outputFile, ") please check the log file:", logFileName)
			except Exception as e:
				self.debugmsg(7, "Robot returned an error:", e)

			self.robotcount += -1
		else:
			self.debugmsg(1, "Could not find robot executeable:", robotexe)

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
			self.debugmsg(1, "Error parsing XML file:", outputFile)
		self.debugmsg(6, "tree: '", tree)
		root = tree.getroot()
		self.debugmsg(6, "root: '", root)
		# .//kw/msg/..[not(@library='BuiltIn')]
		for result in root.findall(".//kw/msg/..[@library]"):
			self.debugmsg(6, "run_process_output: result: ", result)
			library = result.get('library')
			# if library not in ["BuiltIn", "String", "OperatingSystem", "perftest"]:
			if library not in self.excludelibraries:
				self.debugmsg(6, "run_process_output: library: ", library)
				seq += 1
				self.debugmsg(6, "result: library:", library)
				txn = result.find('msg').text
				self.debugmsg(6, "result: txn:", txn)

				el_status = result.find('status')
				status = el_status.get('status')
				self.debugmsg(6, "result: status:", status)
				starttime = el_status.get('starttime')
				self.debugmsg(6, "result: starttime:", starttime)
				endtime = el_status.get('endtime')
				self.debugmsg(6, "result: endtime:", endtime)

				# 20191026 09:34:23.044
				startdate = datetime.strptime(starttime, '%Y%m%d %H:%M:%S.%f')
				enddate = datetime.strptime(endtime, '%Y%m%d %H:%M:%S.%f')

				elapsedtime = enddate.timestamp() - startdate.timestamp()

				self.debugmsg(6, "resultname: '", txn,
						"' result'", status,
						"' elapsedtime'", elapsedtime,
						"' starttime'", starttime,
						"' endtime'", endtime, "'"
						)


				# Send result to server
				uri = self.swarmserver + "Result"

				self.debugmsg(6, "run_proces_output: uri", uri)

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

				self.debugmsg(6, "run_proces_output: payload", payload)
				try:
					r = requests.post(uri, json=payload)
					self.debugmsg(6, "run_proces_output: ",r.status_code, r.text)
					if (r.status_code != requests.codes.ok):
						self.isconnected = False
				except Exception as e:
					self.debugmsg(8, "Exception:", e)
					self.debugmsg(0, "Server Disconected", self.swarmserver, datetime.now().isoformat(sep=' ',timespec='seconds'), "(",int(time.time()),")")
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
			self.debugmsg(6, "Directory Created: ", dir)
		except FileExistsError:
			self.debugmsg(6, "Directory Exists: ", dir)
			pass
		except Exception as e:
			self.debugmsg(1, "Directory Create failed: ", dir)
			self.debugmsg(1, "with error: ", e)

	def create_listner_file(self):
		self.listenerfile = os.path.join(self.scriptdir, "RFSListener2.py")

		fd = []
		fd.append("")
		fd.append("import os")
		fd.append("import tempfile")
		fd.append("import sys")
		fd.append("import socket")
		fd.append("from datetime import datetime")
		fd.append("import time")
		fd.append("import requests")
		fd.append("import inspect")
		fd.append("")
		fd.append("class RFSListener2:")
		fd.append("	ROBOT_LISTENER_API_VERSION = 2")
		fd.append("")
		fd.append("	msg = None")
		fd.append("	swarmserver = \"http://localhost:8138/\"")
		fd.append("	excludelibraries = [\"BuiltIn\",\"String\",\"OperatingSystem\",\"perftest\"]")
		fd.append("	debuglevel = 0")
		fd.append("	index = 0")
		fd.append("	vuser = 0")
		fd.append("	iter = 0")
		fd.append("	seq = 0")
		fd.append("")
		fd.append("	def start_suite(self, name, attrs):")
		fd.append("		if 'debuglevel' in attrs['metadata']:")
		fd.append("			self.debuglevel = int(attrs['metadata']['debuglevel'])")
		fd.append("			self.debugmsg(6, 'debuglevel: ', self.debuglevel)")
		fd.append("		if 'index' in attrs['metadata']:")
		fd.append("			self.index = attrs['metadata']['index']")
		fd.append("			self.debugmsg(6, 'index: ', self.index)")
		fd.append("		if 'iteration' in attrs['metadata']:")
		fd.append("			self.iter = attrs['metadata']['iteration']")
		fd.append("			self.debugmsg(6, 'iter: ', self.iter)")
		fd.append("		if 'vuser' in attrs['metadata']:")
		fd.append("			self.vuser = attrs['metadata']['vuser']")
		fd.append("			self.debugmsg(6, 'vuser: ', self.vuser)")
		fd.append("		if 'swarmserver' in attrs['metadata']:")
		fd.append("			self.swarmserver = attrs['metadata']['swarmserver']")
		fd.append("			self.debugmsg(6, 'swarmserver: ', self.swarmserver)")
		fd.append("		if 'excludelibraries' in attrs['metadata']:")
		fd.append("			self.excludelibraries = attrs['metadata']['excludelibraries'].split(\",\")")
		fd.append("			self.debugmsg(6, 'excludelibraries: ', self.excludelibraries)")
		fd.append("")
		fd.append("	def log_message(self, message):")
		# fd.append("		self.debugmsg(8, 'message[\\'message\\']: ', message['message'])")
		# fd.append("		self.debugmsg(8, 'message[\\'message\\'][0:2]: ', message['message'][0:2])")
		fd.append("		if message['message'][0:2] != '${':")
		fd.append("			self.msg = None")
		fd.append("			self.msg = message")
		# fd.append("			self.debugmsg(6, 'message: ', message)")
		# fd.append("			self.debugmsg(6, 'self.msg: ', self.msg)")
		fd.append("")
		fd.append("	def end_keyword(self, name, attrs):")
		fd.append("		self.debugmsg(6, 'attrs[doc]: ', attrs['doc'])")
		fd.append("		self.debugmsg(6, 'self.msg: ', self.msg)")
		fd.append("		if self.msg is not None:")
		fd.append("			self.debugmsg(8, 'self.msg: attrs[libname]: ', attrs['libname'], '	excludelibraries:', self.excludelibraries)")
		fd.append("			if attrs['libname'] not in self.excludelibraries:")
		fd.append("				self.seq += 1")
		fd.append("				self.debugmsg(8, 'self.seq: ', self.seq)")
		fd.append("				startdate = datetime.strptime(attrs['starttime'], '%Y%m%d %H:%M:%S.%f')")
		fd.append("				enddate = datetime.strptime(attrs['endtime'], '%Y%m%d %H:%M:%S.%f')")
		fd.append("				self.debugmsg(6, 'ResultName: self.msg[message]: ', self.msg['message'])")
		fd.append("				payload = {")
		fd.append("					'AgentName': socket.gethostname(),")
		fd.append("					'ResultName': self.msg['message'],")
		fd.append("					'Result': attrs['status'],")
		fd.append("					'ElapsedTime': (attrs['elapsedtime']/1000),")
		fd.append("					'StartTime': startdate.timestamp(),")
		fd.append("					'EndTime': enddate.timestamp(),")
		fd.append("					'ScriptIndex': self.index,")
		fd.append("					'VUser': self.vuser,")
		fd.append("					'Iteration': self.iter,")
		fd.append("					'Sequence': self.seq")
		fd.append("				}")
		fd.append("				self.debugmsg(8, 'payload: ', payload)")
		fd.append("				self.send_result(payload)")
		# fd.append("				self.msg = None")
		fd.append("		elif 'doc' in attrs and len(attrs['doc'])>0:")
		fd.append("			self.debugmsg(8, 'attrs[doc]: attrs[libname]: ', attrs['libname'], '	excludelibraries:', self.excludelibraries)")
		fd.append("			if attrs['libname'] not in self.excludelibraries:")
		fd.append("				self.seq += 1")
		fd.append("				self.debugmsg(8, 'self.seq: ', self.seq)")
		fd.append("				startdate = datetime.strptime(attrs['starttime'], '%Y%m%d %H:%M:%S.%f')")
		fd.append("				enddate = datetime.strptime(attrs['endtime'], '%Y%m%d %H:%M:%S.%f')")
		fd.append("				self.debugmsg(8, 'attrs: ', attrs)")
		fd.append("				self.debugmsg(6, 'ResultName: attrs[doc]: ', attrs['doc'])")
		fd.append("				payload = {")
		fd.append("					'AgentName': socket.gethostname(),")
		fd.append("					'ResultName': attrs['doc'],")
		fd.append("					'Result': attrs['status'],")
		fd.append("					'ElapsedTime': (attrs['elapsedtime']/1000),")
		fd.append("					'StartTime': startdate.timestamp(),")
		fd.append("					'EndTime': enddate.timestamp(),")
		fd.append("					'ScriptIndex': self.index,")
		fd.append("					'VUser': self.vuser,")
		fd.append("					'Iteration': self.iter,")
		fd.append("					'Sequence': self.seq")
		fd.append("				}")
		fd.append("				self.debugmsg(8, 'payload: ', payload)")
		fd.append("				self.send_result(payload)")
		# fd.append("				self.msg = None")
		fd.append("		self.msg = None")
		fd.append("")
		fd.append("	def debugmsg(self, lvl, *msg):")
		fd.append("		msglst = []")
		fd.append("		prefix = \"\"")
		fd.append("		if self.debuglevel >= lvl:")
		fd.append("			try:")
		fd.append("				if self.debuglevel >= 4:")
		fd.append("					stack = inspect.stack()")
		fd.append("					the_class = stack[1][0].f_locals[\"self\"].__class__.__name__")
		fd.append("					the_method = stack[1][0].f_code.co_name")
		fd.append("					prefix = \"{}: {}: [{}:{}]	\".format(str(the_class), the_method, self.debuglevel, lvl)")
		fd.append("					if len(prefix.strip())<32:")
		fd.append("						prefix = \"{}	\".format(prefix)")
		fd.append("					if len(prefix.strip())<24:")
		fd.append("						prefix = \"{}	\".format(prefix)")
		fd.append("					msglst.append(str(prefix))")
		fd.append("				for itm in msg:")
		fd.append("					msglst.append(str(itm))")
		fd.append("				print(\" \".join(msglst))")
		fd.append("			except:")
		fd.append("				pass")
		fd.append("")
		fd.append("	def send_result(self, payload):")
		fd.append("		uri = self.swarmserver + 'Result'")
		fd.append("		try:")
		fd.append("			r = requests.post(uri, json=payload)")
		fd.append("			self.debugmsg(7, 'send_result: ',r.status_code, r.text)")
		fd.append("			if (r.status_code != requests.codes.ok):")
		fd.append("				self.isconnected = False")
		fd.append("		except Exception as e:")
		fd.append("			self.debugmsg(7, 'send_result: ',r.status_code, r.text)")
		fd.append("			self.debugmsg(7, 'send_result: Exception:', e)")
		fd.append("			pass")
		fd.append("")


		# print("RFSwarmAgent: create_listner_file: listenerfile: ", self.listenerfile)
		with open(self.listenerfile, 'w+') as lf:
			# lf.writelines(fd)
			lf.write('\n'.join(fd))

rfsa = RFSwarmAgent()
try:
	rfsa.mainloop()
except KeyboardInterrupt:
	pass
except Exception as e:
	self.debugmsg(1, "rfsa.Exception:", e)
	pass
