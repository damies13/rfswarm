
# Robot Framework Swarm

# https://stackoverflow.com/questions/48090535/csv-file-reading-and-find-the-value-from-nth-column-using-robot-framework

import base64
import gc
import json
import lzma
import os
import platform
import random
import shutil
import socket
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from typing import Any

import psutil
import requests

from rfswarm_common.__version__ import __version__
from rfswarm_common.debug import debug
from rfswarm_common.filestransfers import FilesTransfers
from rfswarm_agent.client.manager import ManagerClient
from rfswarm_common.config import config
from rfswarm_agent.properties import collect_agent_properties
from rfswarm_common.utils import str2bool
from rfswarm_common.icons import IconManager


class RFSwarmAgent():
	"""
	Orchestrator class for Robot Framework Swarm Agent.
	"""
	version = __version__
	manager = None
	isrunning = False
	isstopping = False
	runagent = True
	run_name = None
	scriptdir = None
	logdir = None
	agentini = None
	listenerfile = None
	repeaterfile = None

	ipaddresslist: Any = []
	agentname = None
	netpct = 0
	mainloopinterval = 10
	scriptlist: Any = {}
	jobs: Any = {}
	corethreads: Any = {}
	upload_queue: Any = []
	upload_threads: Any = {}
	download_queue: Any = []
	download_threads: Any = {}
	robotcount = 0
	monitorcount = 0
	status = "Ready"
	excludelibraries: Any = []
	args = None
	timeout = 600
	uploadmode = "err"
	managedenvvars: Any = []

	def __init__(self, args, master=None):
		debug.debugmsg(6, "__init__")

		self.args = args

		if self.args.create:
			if self.args.create.upper() in ["ICON", "ICONS"]:
				IconManager.create_icons("RFSwarm Agent", os.path.dirname(__file__))
			else:
				debug.debugmsg(0, "create with option ", self.args.create.upper(), "not supported.")
			exit()

		self.agentname = config.data['Agent']['agentname']

		FilesTransfers.ensuredir(config.data['Agent']['agentdir'])

		self.scriptdir = os.path.join(config.data['Agent']['agentdir'], "scripts")
		FilesTransfers.ensuredir(self.scriptdir)

		self.logdir = os.path.join(config.data['Agent']['agentdir'], "logs")
		FilesTransfers.ensuredir(self.logdir)

		self.excludelibraries = config.data['Agent']['excludelibraries'].split(",")
		debug.debugmsg(6, "self.excludelibraries:", self.excludelibraries)

		if not self.args.create:
			IconManager.check_icons("RFSwarm Agent")

		self.agentproperties = collect_agent_properties(self.args, self.version)
		self.ensure_listner_file()
		self.ensure_repeater_listner_file()

		self.manager = ManagerClient()

	def mainloop(self):
		debug.debugmsg(6, "mainloop")
		prev_status = self.status
		while self.runagent:
			debug.debugmsg(
				2, self.status, datetime.now().isoformat(sep=' ', timespec='seconds'),
				"(", int(time.time()), ")",
				"isconnected:", self.manager.isconnected,
				"isrunning:", self.isrunning,
				"isstopping:", self.isstopping,
				"robotcount:", self.robotcount,
				"monitorcount:", self.monitorcount,
				"\n"
			)

			if not self.manager.isconnected:
				# self.isrunning = False # Not sure if I need this?
				# self.connectmanager()
				t = threading.Thread(target=self.manager.connectmanager, name="connectmanager", args=(self.timeout,))
				t.start()
				self.isrunning = False

			debug.debugmsg(5, "self.isconnected", self.manager.isconnected)
			if self.manager.isconnected:
				# self.updatestatus()
				self.corethreads["status"] = threading.Thread(target=self.updatestatus)
				self.corethreads["status"].start()

				if self.listenerfile is not None:
					self.corethreads["getjobs"] = threading.Thread(target=self.getjobs)
					self.corethreads["getjobs"].start()

				if self.isrunning:
					self.mainloopinterval = 2
					self.status = "Running"
					if self.isstopping:
						self.status = "Stopping"
					# else:
					self.corethreads["runjobs"] = threading.Thread(target=self.runjobs)
					self.corethreads["runjobs"].start()
				else:
					self.mainloopinterval = 10
					if len(self.upload_queue) > 0:
						self.status = "Uploading ({})".format(len(self.upload_queue))
						debug.debugmsg(5, "self.status:", self.status, "len(self.upload_queue):", len(self.upload_queue))
						self.corethreads["uploadqueue"] = threading.Thread(target=self.process_file_upload_queue)
						self.corethreads["uploadqueue"].start()
					else:
						self.status = "Ready"
						self.corethreads["getscripts"] = threading.Thread(target=self.getscripts)
						self.corethreads["getscripts"].start()

						if len(self.download_queue):
							self.status = "Downloading ({})".format(len(self.download_queue))

			if (prev_status == "Stopping" or "Uploading" in prev_status) and self.status == "Ready":
				# neet to reset something
				# I guess we can just reset the jobs disctionary?
				self.jobs = {}
				# pass

			time.sleep(self.mainloopinterval)

	def updateipaddresslist(self):
		if len(self.ipaddresslist) < 1:
			self.ipaddresslist = []
			iflst = psutil.net_if_addrs()
			for nic in iflst.keys():
				debug.debugmsg(6, "nic", nic)
				for addr in iflst[nic]:
					# '127.0.0.1', '::1', 'fe80::1%lo0'
					debug.debugmsg(6, "addr", addr.address)
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
			if nicstats[nic].speed > 0:
				debug.debugmsg(6, "Speed:", nicstats[nic].speed)
				bytes_speed = nicstats[nic].speed * 1024 * 1024 / 8
				bytes_sent_sec = niccounters1[nic].bytes_sent - niccounters0[nic].bytes_sent
				bytes_recv_sec = niccounters1[nic].bytes_recv - niccounters0[nic].bytes_recv
				debug.debugmsg(6, "bytes_speed:	", bytes_speed)
				debug.debugmsg(6, "bytes_sent_sec:	", bytes_sent_sec)
				debug.debugmsg(6, "bytes_recv:	", bytes_recv_sec)
				bytes_max_sec = max([bytes_sent_sec, bytes_recv_sec])
				debug.debugmsg(6, "bytes_max_sec:	", bytes_max_sec)
				if bytes_max_sec > 0:
					netpctlist.append((bytes_max_sec / bytes_speed) * 100)
				else:
					netpctlist.append(0)

		if len(netpctlist) > 0:
			debug.debugmsg(6, "netpctlist:	", netpctlist)
			self.netpct = max(netpctlist)
			debug.debugmsg(6, "self.netpct:	", self.netpct)
		else:
			self.netpct = 0

	def updatestatus(self):
		debug.debugmsg(6, "self.manager.swarmmanager:", self.manager.swarmmanager)
		uri = self.manager.swarmmanager + "AgentStatus"

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
			"Monitor": self.monitorcount,
			"Status": self.status,
			"Properties": self.agentproperties,
			"FileCount": len(list(self.scriptlist.keys()))
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(8, r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok, r.text)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False
				debug.debugmsg(7, "self.manager.isconnected", self.manager.isconnected)
		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False
			debug.debugmsg(5, "self.manager.isconnected", self.manager.isconnected)

	def getscripts(self):
		debug.debugmsg(6, "getscripts")

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			debug.debugmsg(5, "already processing the queue, don't double up")
			return None

		uri = self.manager.swarmmanager + "Scripts"
		payload = {
			"AgentName": self.agentname
		}
		debug.debugmsg(6, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(6, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(5, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(6, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

		if "Scripts" in jsonresp:
			for s in jsonresp["Scripts"]:
				hash = s['Hash']
				debug.debugmsg(6, "hash:", hash)
				if hash not in self.scriptlist:
					debug.debugmsg(6, "getfile")
					self.scriptlist[hash] = {'id': hash}
					if hash not in self.download_queue:
						self.download_queue.append(hash)
				else:
					debug.debugmsg(6, "Check file")
					if 'localfile' in self.scriptlist[hash]:
						if not os.path.isfile(self.scriptlist[hash]['localfile']):
							if hash not in self.download_queue:
								self.download_queue.append(hash)
					else:
						debug.debugmsg(6, "getfile")
						self.scriptlist[hash] = {'id': hash}
						if hash not in self.download_queue:
							self.download_queue.append(hash)

			if len(self.download_queue):
				self.process_file_download_queue()

	def process_file_download_queue(self):

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			debug.debugmsg(5, "already processing the queue, don't double up")
			return None

		corecount = psutil.cpu_count()
		threadcount = corecount * 32
		debug.debugmsg(7, "download_queue", self.download_queue)
		debug.debugmsg(5, "corecount", corecount, "	threadcount:", threadcount)
		# for hash in self.download_queue:
		while len(self.download_queue) > 0:
			# limit the number of upload threads so we don't max out the agent and cause it
			# to go into critical/offline? mode

			hash = self.download_queue.pop(0)

			debug.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
			while len(list(self.download_threads.keys())) > threadcount - 1:
				debug.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
				# key = list(self.upload_threads.keys())[0]
				key = random.choice(list(self.download_threads.keys()))
				debug.debugmsg(5, "key:", key)
				if key in self.download_threads and self.download_threads[key].is_alive():
					self.download_threads[key].join()
				if key in self.download_threads:
					del self.download_threads[key]
			key = str(uuid.uuid4())
			debug.debugmsg(6, "New download thread key:", key)
			while hash in self.download_queue:
				self.download_queue.remove(hash)
			self.download_threads[key] = threading.Thread(target=self.getfile, args=(hash,))
			self.download_threads[key].start()
			time.sleep(0.02)
		for key in list(self.download_threads.keys()):
			debug.debugmsg(6, "download thread key:", key)
			if key in self.download_threads and self.download_threads[key].is_alive():
				self.download_threads[key].join()
			if key in self.download_threads:
				del self.download_threads[key]
			debug.debugmsg(6, "Finished download thread key:", key)
		gc.collect()

	def getfile(self, hash):
		debug.debugmsg(6, "hash: ", hash)
		uri = self.manager.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Download",
			"Hash": hash
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(8, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(5, "resp: ", r.status_code, r.text)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(5, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

		try:
			relpath = jsonresp['File']
			if '\\' in relpath:
				relpatharr = relpath.split('\\')
			else:
				relpatharr = relpath.split('/')
			debug.debugmsg(7, 'scriptdir', self.scriptdir)
			localfile = os.path.abspath(os.path.join(self.scriptdir, *relpatharr))
			debug.debugmsg(5, 'localfile', localfile)

		except Exception as e:
			debug.debugmsg(0, "Exception:", e)

		try:
			self.scriptlist[hash]['localfile'] = localfile
			self.scriptlist[hash]['file'] = jsonresp['File']

			# self.scriptlist[hash][]

			filedata = jsonresp['FileData']
			debug.debugmsg(6, "filedata:", filedata)
			debug.debugmsg(6, "filedata:")

			decoded = base64.b64decode(filedata)
			debug.debugmsg(6, "b64decode: decoded:", decoded)
			debug.debugmsg(6, "b64decode:")

			uncompressed = lzma.decompress(decoded)
			debug.debugmsg(6, "uncompressed:", uncompressed)
			debug.debugmsg(6, "uncompressed:")

			localfiledir = os.path.dirname(localfile)
			debug.debugmsg(6, "localfiledir:", localfiledir)
			FilesTransfers.ensuredir(localfiledir)
			debug.debugmsg(6, "ensuredir:")

			with open(localfile, 'wb') as afile:
				debug.debugmsg(6, "afile:")
				afile.write(uncompressed)
				debug.debugmsg(6, "write:")
			debug.debugmsg(1, 'Downloaded:', localfile)

		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

	def getjobs(self):
		debug.debugmsg(6, "getjobs")
		uri = self.manager.swarmmanager + "Jobs"
		payload = {
			"AgentName": self.agentname
		}
		debug.debugmsg(9, "getjobs: payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(7, "getjobs: resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(7, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			debug.debugmsg(7, "getjobs: r.text:", r.text)
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "getjobs: jsonresp:", jsonresp)

			# RFSwarmAgent: getjobs(821): [7:7]	 getjobs: r.text: {"AgentName": "hp-elite-desk-800-g3", "StartTime": 0, "EndTime": 0, "RunName": "", "Abort": false, "UploadMode": "err", "EnvironmentVariables": {"RF_DIRECTORY": {"vartype": "path", "value": "rf_dir"}, "RF_MAGICNUM": {"vartype": "value", "value": "TWELVE"}}, "Schedule": {}}
			# "EnvironmentVariables": {"RF_DIRECTORY": {"vartype": "path", "value": "rf_dir"}, "RF_MAGICNUM": {"vartype": "value", "value": "TWELVE"}},
			if "EnvironmentVariables" in jsonresp:
				for envvar in list(jsonresp["EnvironmentVariables"].keys()):
					debug.debugmsg(7, "envvar:", envvar, ":", jsonresp["EnvironmentVariables"][envvar])
					localval = ""
					if "vartype" in jsonresp["EnvironmentVariables"][envvar] and jsonresp["EnvironmentVariables"][envvar]["vartype"] == "path":
						localval = os.path.abspath(os.path.join(self.scriptdir, jsonresp["EnvironmentVariables"][envvar]["value"]))
						debug.debugmsg(5, 'localval:', localval)
					else:
						if "value" in jsonresp["EnvironmentVariables"][envvar]:
							localval = jsonresp["EnvironmentVariables"][envvar]["value"]
					if envvar in list(os.environ.keys()):
						# envvalue = os.environ[envvar]
						if envvar in self.managedenvvars and os.environ[envvar] != localval:
							os.environ[envvar] = localval
							debug.debugmsg(1, "Setting Environment Variable:", envvar, "=", localval)
					else:
						self.managedenvvars.append(envvar)
						os.environ[envvar] = localval
						debug.debugmsg(1, "Setting Environment Variable:", envvar, "=", localval)

			if jsonresp["StartTime"] < int(time.time()) < (jsonresp["EndTime"] + 300):
				self.isrunning = True
				self.run_name = jsonresp["RunName"]
				for s in jsonresp["Schedule"].keys():
					debug.debugmsg(6, "getjobs: s:", s)
					if s not in self.jobs.keys():
						self.jobs[s] = {}
					for k in jsonresp["Schedule"][s].keys():
						debug.debugmsg(6, "getjobs: self.jobs[", s, "][", k, "]", jsonresp["Schedule"][s][k])
						self.jobs[s][k] = jsonresp["Schedule"][s][k]
					if "UploadMode" in jsonresp:
						self.jobs[s]["UploadMode"] = jsonresp["UploadMode"]

				if int(time.time()) > jsonresp["EndTime"]:
					self.isstopping = True
				if self.isstopping and self.robotcount < 1 and self.monitorcount < 1:
					self.jobs = {}
					self.isrunning = False
					self.isstopping = False
			else:
				if self.robotcount < 1:
					self.isrunning = False
					self.isstopping = False
				else:
					self.isstopping = True

			debug.debugmsg(7, "jsonresp[Abort]", jsonresp["Abort"])
			if jsonresp["Abort"]:
				self.isstopping = True
				debug.debugmsg(5, "!!! Abort !!!")
				self.abortjobs()

			debug.debugmsg(5, "getjobs: isrunning:", self.isrunning, "	isstopping:", self.isstopping)
			debug.debugmsg(7, "getjobs: self.jobs:", self.jobs)

		except Exception as e:
			debug.debugmsg(1, "getjobs: Exception:", e)

	def abortjobs(self):
		debug.debugmsg(6, "self.jobs:", self.jobs)
		for job in self.jobs:
			try:
				debug.debugmsg(6, "job:", job, self.jobs[job])
				debug.debugmsg(5, "job[PID]:", self.jobs[job]["PID"])
				debug.debugmsg(6, "job[Process]:", self.jobs[job]["Process"])
				p = self.jobs[job]["Process"]
				p.terminate()

			except Exception as e:
				debug.debugmsg(1, "getjobs: Exception:", e)

	def runjobs(self):
		debug.debugmsg(6, "runjobs: self.jobs:", self.jobs)
		workingkeys = list(self.jobs.keys())
		if not self.isstopping:
			for jobid in workingkeys:
				if jobid in self.jobs.keys():
					debug.debugmsg(6, "runjobs: jobid:", jobid)
					run_t = True
					if "Thread" in self.jobs[jobid].keys():
						debug.debugmsg(7, "jobid:", self.jobs[jobid])
						try:
							# if self.jobs[jobid]["Thread"].isAlive():
							# The isAlive syntax above was perviously working in python < 3.7
							# but appears to have been removed in 3.9.1? it was depricated in 2.x?
							# and the is_alive syntax below has been available since python version 2.6
							if self.jobs[jobid]["Thread"].is_alive():
								run_t = False
								debug.debugmsg(7, "Thread already running run_t:", run_t)
						except Exception as e:
							run_t = False
							debug.debugmsg(5, "Thread running check failed run_t:", run_t, e)

					debug.debugmsg(6, "run_t:", run_t)

					if run_t:
						debug.debugmsg(5, "jobid:", jobid, "run_t:", run_t, "StartTime:", self.jobs[jobid]["StartTime"], "< Now:", int(time.time()), "< EndTime:", self.jobs[jobid]["EndTime"])
						if self.jobs[jobid]["StartTime"] < int(time.time()) < self.jobs[jobid]["EndTime"]:
							t = threading.Thread(target=self.runthread, args=(jobid, ))
							t.start()
							self.jobs[jobid]["Thread"] = t
							debug.debugmsg(5, "Thread started for jobid:", jobid)
						else:
							debug.debugmsg(5, "Thread not started for jobid:", jobid)
				time.sleep(0.1)

	def runthread(self, jobid):
		now = int(time.time())

		self.ensure_listner_file()
		self.ensure_repeater_listner_file()

		if "ScriptIndex" not in self.jobs[jobid]:
			debug.debugmsg(5, "runthread: jobid:", jobid)
			debug.debugmsg(5, "runthread: job data:", self.jobs[jobid])
			jobarr = jobid.split("_")
			self.jobs[jobid]["ScriptIndex"] = jobarr[0]
			self.jobs[jobid]["Robot"] = jobarr[1]
			self.jobs[jobid]["Iteration"] = 0
			self.jobs[jobid]["RobotType"] = "Plan"
			if jobarr[0].lower()[0] == "m":
				self.jobs[jobid]["RobotType"] = "Monitor"
			debug.debugmsg(5, "runthread: job data:", self.jobs[jobid])

		self.jobs[jobid]["Iteration"] += 1

		debug.debugmsg(5, "self.jobs[jobid]:", self.jobs[jobid])

		# jobfile = os.path.join(self.scriptdir, "job_{}.json".format(jobid))
		jobfile = os.path.join(self.scriptdir, "RFS_Job_{}_{}.json".format(self.jobs[jobid]["ScriptIndex"], self.jobs[jobid]["Robot"]))

		jobdata = {}
		jobdata["StartTime"] = self.jobs[jobid]["StartTime"]
		jobdata["EndTime"] = self.jobs[jobid]["EndTime"]
		jobdata["Iteration"] = self.jobs[jobid]["Iteration"]
		jobdata["Index"] = self.jobs[jobid]["ScriptIndex"]
		jobdata["Robot"] = self.jobs[jobid]["Robot"]
		jobdata["jobid"] = jobid
		jobdata["Test"] = self.jobs[jobid]["Test"]

		with open(jobfile, 'w', encoding="utf-8") as jfile:
			jfile.write(json.dumps(jobdata))

		hash = self.jobs[jobid]['ScriptHash']
		debug.debugmsg(6, "runthread: hash:", hash)
		test = self.jobs[jobid]['Test']
		debug.debugmsg(6, "runthread: test:", test)
		if platform.system() != 'Windows':
			test = test.replace(r'${', r'\${')
			debug.debugmsg(6, "runthread: test:", test)
		test = test.replace(r'"', r'\"')

		if hash not in self.scriptlist:
			self.getfile(hash)

		if 'localfile' not in self.scriptlist[hash]:
			if self.corethreads["getscripts"].is_alive():
				self.corethreads["getscripts"].join()
			else:
				self.corethreads["getscripts"] = threading.Thread(target=self.getscripts)
				self.corethreads["getscripts"].start()
				self.corethreads["getscripts"].join()
		# while 'localfile' not in self.scriptlist[hash]:
		# 	time.sleep(1)

		localfile = self.scriptlist[hash]['localfile']
		debug.debugmsg(6, "runthread: localfile:", localfile)

		file = self.scriptlist[hash]['file']
		debug.debugmsg(6, "runthread: file:", file)

		farr = os.path.splitext(file)
		debug.debugmsg(6, "runthread: farr:", farr)

		excludelibraries = ",".join(self.excludelibraries)
		if "excludelibraries" in self.jobs[jobid]:
			# not sure if we need to do this???
			# for safety split and join string
			# ellst = self.jobs[jobid]['excludelibraries'].split(",")
			# excludelibraries = ",".join(ellst)
			excludelibraries = self.jobs[jobid]['excludelibraries']

		debug.debugmsg(6, "excludelibraries:", excludelibraries)
		excludelibrarielst = excludelibraries.split(",")
		excludelibrarielst = map(str.strip, excludelibrarielst)
		excludelibraries = ",".join(excludelibrarielst)
		debug.debugmsg(6, "excludelibraries:", excludelibraries)

		# self.run_name
		# scriptdir = None
		# logdir = None

		rundir = os.path.join(self.logdir, self.run_name)
		try:
			if not os.path.exists(rundir):
				os.makedirs(rundir)
		except Exception:
			pass
		threaddirname = FilesTransfers.make_safe_filename("{}_{}_{}_{}".format(farr[0], jobid, self.jobs[jobid]["Iteration"], now))
		odir = os.path.join(self.logdir, self.run_name, threaddirname)
		debug.debugmsg(6, "runthread: odir:", odir)
		try:
			if not os.path.exists(odir):
				os.makedirs(odir)
		except Exception:
			pass

		oprefix = FilesTransfers.make_safe_filename(test)
		debug.debugmsg(6, "runthread: oprefix:", oprefix)
		logFileName = os.path.join(odir, "{}.log".format(oprefix))
		debug.debugmsg(6, "runthread: logFileName:", logFileName)
		outputFileName = "{}_output.xml".format(oprefix)
		outputFile = os.path.join(odir, outputFileName)
		debug.debugmsg(6, "runthread: outputFile:", outputFile)

		robotcmd = config.data['Agent']['robotcmd']

		debug.debugmsg(6, "runthread: robotcmd:", robotcmd)

		cmd = [robotcmd]

		if "robotoptions" in self.jobs[jobid]:
			cmd.append("{}".format(self.jobs[jobid]['robotoptions']))

		debug.debugmsg(9, "runthread: cmd:", cmd)

		cmd.append("-t")
		cmd.append('"' + test + '"')
		cmd.append("-d")
		cmd.append('"' + odir + '"')

		metavars = []
		metavars.append("RFS_AGENTNAME:{}".format(self.agentname))
		metavars.append("RFS_AGENTVERSION:{}".format(self.version))
		metavars.append("RFS_DEBUGLEVEL:{}".format(debug.debuglvl))
		metavars.append("RFS_INDEX:{}".format(self.jobs[jobid]["ScriptIndex"]))
		metavars.append("RFS_ROBOT:{}".format(self.jobs[jobid]["Robot"]))
		metavars.append("RFS_ITERATION:{}".format(self.jobs[jobid]["Iteration"]))
		metavars.append("RFS_SWARMMANAGER:{}".format(self.manager.swarmmanager))
		metavars.append("RFS_EXCLUDELIBRARIES:{}".format(excludelibraries))
		metavars.append("RFS_ROBOTTYPE:{}".format(self.jobs[jobid]["RobotType"]))

		if "excludesleep" in self.jobs[jobid]:
			metavars.append("RFS_EXCLUDESLEEP:{}".format(self.jobs[jobid]["excludesleep"]))

		if "includetesttime" in self.jobs[jobid]:
			metavars.append("RFS_INCLUDETESTTIME:{}".format(self.jobs[jobid]["includetesttime"]))

		if "applypacingtime" in self.jobs[jobid]:
			metavars.append("RFS_APPLYPACINGTIME:{}".format(self.jobs[jobid]["applypacingtime"]))

		if "applypacingstart" in self.jobs[jobid]:
			metavars.append("RFS_APPLYPACINGSTART:{}".format(self.jobs[jobid]["applypacingstart"]))

		if "injectsleepenabled" in self.jobs[jobid]:
			metavars.append("RFS_INJECTSLEEP:{}".format(self.jobs[jobid]["injectsleepenabled"]))
			if str2bool(self.jobs[jobid]["injectsleepenabled"]):
				# injectsleepminimum
				if "injectsleepminimum" in self.jobs[jobid]:
					metavars.append("RFS_SLEEPMINIMUM:{}".format(self.jobs[jobid]["injectsleepminimum"]))
				# injectsleepmaximum
				if "injectsleepmaximum" in self.jobs[jobid]:
					metavars.append("RFS_SLEEPMAXIMUM:{}".format(self.jobs[jobid]["injectsleepmaximum"]))

		if "resultnamemode" in self.jobs[jobid]:
			metavars.append("RFS_RESULTNAMEMODE:{}".format(self.jobs[jobid]["resultnamemode"]))

		for metavar in metavars:
			cmd.append("-M {}".format(metavar))
			cmd.append("-v {}".format(metavar))

		cmd.append("--listener {}".format('"' + self.listenerfile + '"'))

		debug.debugmsg(9, "runthread: cmd:", cmd)

		debug.debugmsg(9, "Check for runthread: robotexe")
		if "testrepeater" in self.jobs[jobid]:
			debug.debugmsg(7, "runthread: self.jobs[jobid][testrepeater]:", self.jobs[jobid]["testrepeater"])
			debug.debugmsg(9, "runthread: self.jobs[jobid][testrepeater]:", str2bool(self.jobs[jobid]["testrepeater"]), type(str2bool(self.jobs[jobid]["testrepeater"])))
			if str2bool(self.jobs[jobid]["testrepeater"]):
				cmd.append("--listener {}".format('"' + self.repeaterfile + '"'))

		debug.debugmsg(9, "runthread: cmd:", cmd)

		# disableloglog': 'True',
		if "disableloglog" in self.jobs[jobid]:
			if str2bool(self.jobs[jobid]["disableloglog"]):
				cmd.append("-l NONE")
		# 'disablelogreport': 'True',
		if "disablelogreport" in self.jobs[jobid]:
			if str2bool(self.jobs[jobid]["disablelogreport"]):
				cmd.append("-r NONE")
		# 'disablelogoutput': 'True',
		disablelogoutput = False
		if "disablelogoutput" in self.jobs[jobid]:
			disablelogoutput = str2bool(self.jobs[jobid]["disablelogoutput"])
		if disablelogoutput:
			cmd.append("-o NONE")
		else:
			cmd.append("-o")
			cmd.append('"' + outputFile + '"')

		cmd.append('"' + localfile + '"')

		robotexe = shutil.which(robotcmd)
		debug.debugmsg(6, "runthread: robotexe:", robotexe)
		if robotexe is not None:

			if self.jobs[jobid]["RobotType"] in ["Monitor"]:
				self.monitorcount += 1
			else:
				self.robotcount += 1

			result = 0
			try:
				os.chdir(self.scriptdir)
				# https://stackoverflow.com/questions/4856583/how-do-i-pipe-a-subprocess-call-to-a-text-file
				with open(logFileName, "w", encoding="utf-8") as f:
					debug.debugmsg(3, "Robot run with command: '", " ".join(cmd), "'")
					# result = subprocess.call(" ".join(cmd), shell=True, stdout=f, stderr=f)
					try:
						proc = subprocess.Popen(" ".join(cmd), shell=True, stdout=f, stderr=subprocess.STDOUT)
						debug.debugmsg(5, "runthread: proc:", proc)
						self.jobs[jobid]["Process"] = proc
						self.jobs[jobid]["PID"] = proc.pid
						debug.debugmsg(5, "runthread: proc.pid:", proc.pid)
						result = proc.wait()
						debug.debugmsg(5, "runthread: result:", result)
						if result != 0:
							debug.debugmsg(1, "Robot returned an error (", result, ") please check the log file:", logFileName)
					except Exception as e:
						debug.debugmsg(1, "Robot returned an error:", e, " \nplease check the log file:", logFileName)
						result = 1
					f.close()

				if os.path.exists(jobfile):
					os.remove(jobfile)

			except Exception as e:
				debug.debugmsg(5, "Robot returned an error:", e)
				result = 1

			uploadmode = self.uploadmode
			debug.debugmsg(5, "uploadmode:", uploadmode)
			debug.debugmsg(5, "self.jobs[", jobid, "]:", self.jobs[jobid])
			if "UploadMode" in self.jobs[jobid]:
				uploadmode = self.jobs[jobid]["UploadMode"]
				debug.debugmsg(5, "uploadmode:", uploadmode)

			# Uplad any files found
			self.queue_file_upload(uploadmode, result, odir)

			if self.jobs[jobid]["RobotType"] in ["Monitor"]:
				self.monitorcount += -1
			else:
				self.robotcount += -1

		else:
			debug.debugmsg(1, "Could not find robot executeable:", robotexe)

	def queue_file_upload(self, mode, retcode, filedir):
		reldir = os.path.basename(filedir)
		debug.debugmsg(7, mode, retcode, reldir, filedir)

		filelst = self.file_upload_list(filedir)
		debug.debugmsg(7, "filelst", filelst)
		# filelst
		# [
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1.log',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/log.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/report.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1_output.xml'
		# ]
		#

		rundir = os.path.join(self.logdir, self.run_name)

		debug.debugmsg(5, "mode:", mode, "	retcode:", retcode)
		# 	uploadmodes = {'imm':"Immediately", 'err':"On Error Only", 'def':"All Defered"}

		for file in filelst:
			fobj = {}
			fobj["LocalFilePath"] = file
			fobj["RelFilePath"] = os.path.relpath(file, start=rundir)
			self.upload_queue.append(fobj)
			debug.debugmsg(7, "added to upload_queue", fobj)
			if mode == "err" and retcode > 0:
				# upload now
				self.file_upload(fobj)
			if mode == "imm":
				# upload now
				self.file_upload(fobj)

	def file_upload_list(self, filedir):
		retlst = []
		dirlst = os.listdir(path=filedir)
		debug.debugmsg(7, "dirlst", dirlst)
		for item in dirlst:
			fullpath = os.path.join(filedir, item)
			if os.path.isfile(fullpath):
				retlst.append(fullpath)
			else:
				files = self.file_upload_list(fullpath)
				for file in files:
					retlst.append(file)
		return retlst

	def file_upload(self, fileobj):
		debug.debugmsg(7, "fileobj", fileobj)

		# Hash file

		hash = FilesTransfers.hash_file(fileobj['LocalFilePath'], fileobj['RelFilePath'])
		debug.debugmsg(7, "hash", hash)

		# 	check file exists on manager?

		uri = self.manager.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Status",
			"Hash": hash
		}
		debug.debugmsg(9, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(7, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		jsonresp = {}
		try:
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)
			return None

		# 	If file not exists upload the file
		if jsonresp["Exists"] == "False":
			debug.debugmsg(6, "file not there, so lets upload")

			payload = {
				"AgentName": self.agentname,
				"Action": "Upload",
				"Hash": hash,
				"File": fileobj['RelFilePath']
			}

			localpath = fileobj['LocalFilePath']
			buf = "\n"
			with open(localpath, 'rb') as afile:
				buf = afile.read()
			debug.debugmsg(9, "buf:", buf)
			compressed = lzma.compress(buf)
			debug.debugmsg(9, "compressed:", compressed)
			encoded = base64.b64encode(compressed)
			debug.debugmsg(9, "encoded:", encoded)

			payload["FileData"] = encoded.decode('ASCII')

			debug.debugmsg(8, "payload: ", payload)

			try:
				r = requests.post(uri, json=payload, timeout=self.timeout)
				debug.debugmsg(7, "resp: ", r.status_code, r.text)
				if r.status_code != requests.codes.ok:
					debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
					debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
					self.manager.isconnected = False

			except Exception as e:
				debug.debugmsg(8, "Exception:", e)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

			if not self.manager.isconnected:
				return None

			jsonresp = {}
			try:
				# self.scriptlist
				jsonresp = json.loads(r.text)
				debug.debugmsg(7, "jsonresp:", jsonresp)
			except Exception as e:
				debug.debugmsg(1, "Exception:", e)
				return None

		# once sucessful remove from queue
		if fileobj in self.upload_queue:
			self.upload_queue.remove(fileobj)

	def process_file_upload_queue(self):
		corecount = psutil.cpu_count()
		threadcount = corecount * 3
		debug.debugmsg(7, "upload_queue", self.upload_queue)
		debug.debugmsg(5, "corecount", corecount, "	threadcount:", threadcount)
		# self.process_file_upload_queue
		for fobj in self.upload_queue:
			# limit the number of upload threads so we don't max out the agent and cause it
			# to go into critical/offline? mode
			debug.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
			while len(list(self.upload_threads.keys())) > threadcount - 1:
				debug.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
				# key = list(self.upload_threads.keys())[0]
				key = random.choice(list(self.upload_threads.keys()))
				debug.debugmsg(5, "key:", key)
				if key in self.upload_threads and self.upload_threads[key].is_alive():
					self.upload_threads[key].join()
				if key in self.upload_threads:
					del self.upload_threads[key]
			key = str(uuid.uuid4())
			debug.debugmsg(5, "key:", key)
			self.upload_threads[key] = threading.Thread(target=self.file_upload, args=(fobj,))
			self.upload_threads[key].start()
			time.sleep(0.5)
		for key in list(self.upload_threads.keys()):
			debug.debugmsg(5, "key:", key)
			if key in self.upload_threads and self.upload_threads[key].is_alive():
				self.upload_threads[key].join()
			if key in self.upload_threads:
				del self.upload_threads[key]
		gc.collect()

	def ensure_listner_file(self):
		if self.listenerfile is None:
			self.create_listner_file()
		else:
			if not os.path.isfile(self.listenerfile):
				self.create_listner_file()

	def ensure_repeater_listner_file(self):
		if self.repeaterfile is None:
			self.create_repeater_listner_file()

	def create_listner_file(self):

		while "RobotFramework" not in self.agentproperties:
			time.sleep(0.1)
		rfver = self.agentproperties["RobotFramework"]
		debug.debugmsg(5, "RobotFramework version:", rfver, " RobotFramework major version:", int(rfver[0]))
		# lrfver = rfver.split(".")
		if int(rfver[0]) >= 7:
			self.create_V3_listner_file()
		else:
			self.create_V2_listner_file()

	def create_V3_listner_file(self):

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener3.py")
		debug.debugmsg(5, "listenerfile", self.listenerfile)

		# srcdir
		listenersrc = os.path.join(config.srcdir, "resources", "RFSListener3.py")
		debug.debugmsg(5, "listenersrc", listenersrc)
		shutil.copy(listenersrc, self.listenerfile)


	def create_V2_listner_file(self):

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener2.py")
		debug.debugmsg(5, "listenerfile", self.listenerfile)

		# srcdir
		listenersrc = os.path.join(config.srcdir, "resources", "RFSListener2.py")
		debug.debugmsg(5, "listenersrc", listenersrc)
		shutil.copy(listenersrc, self.listenerfile)

	def create_repeater_listner_file(self):
		self.repeaterfile = os.path.join(self.scriptdir, "RFSTestRepeater.py")
		debug.debugmsg(5, "repeaterfile", self.repeaterfile)

		# srcdir
		repeatersrc = os.path.join(config.srcdir, "resources", "RFSTestRepeater.py")
		debug.debugmsg(5, "repeatersrc", repeatersrc)
		shutil.copy(repeatersrc, self.repeaterfile)

	def on_closing(self, _event=None, *args):
		self.runagent = False
		debug.debugmsg(0, "Shutting down agent")

		for thread in self.corethreads:
			debug.debugmsg(3, "Join Agent Thread:", thread)
			self.corethreads[thread].join()

		for jobid in self.jobs:
			# self.jobs[jobid]["Thread"]
			# debug.debugmsg(3, "Join Agent Manager Thread")
			# self.Agentserver.join()

			debug.debugmsg(3, "Join Agent Thread:", jobid)
			if "Thread" in self.jobs[jobid]:
				self.jobs[jobid]["Thread"].join()

		time.sleep(1)
		debug.debugmsg(2, "Exit")
		try:
			sys.exit(0)
		except SystemExit as e:
			try:
				remaining_threads = [t for t in threading.enumerate() if t is not threading.main_thread() and t.is_alive()]
				if remaining_threads:
					debug.debugmsg(5, "Failed to gracefully exit RFSwarm-Agent. Forcing immediate exit.")
					for thread in remaining_threads:
						debug.debugmsg(9, "Thread name:", thread.name)
					os._exit(0)
				else:
					raise e

			except Exception as e:
				debug.debugmsg(3, "Failed to exit with error:", e)
				os._exit(1)
		sys.stdout.flush()
		sys.stderr.flush()
