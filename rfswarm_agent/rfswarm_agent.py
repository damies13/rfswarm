
# Robot Framework Swarm

# https://stackoverflow.com/questions/48090535/csv-file-reading-and-find-the-value-from-nth-column-using-robot-framework

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime
from typing import Any

import requests
from rfswarm_common.__version__ import __version__
from rfswarm_common.config import config
from rfswarm_common.debug import debug
from rfswarm_common.filestransfers import FilesTransfers
from rfswarm_common.icons import IconManager
from rfswarm_common.utils import Utils

from rfswarm_agent.agent.files import FilesManager
from rfswarm_agent.agent.listners import AgentListeners
from rfswarm_agent.client.manager import ManagerClient
from rfswarm_agent.properties import collect_agent_properties
from rfswarm_agent.telemetry import SystemTelemetry


class RFSwarmAgent:
	"""
	Orchestrator class for Robot Framework Swarm Agent.
	"""
	version = __version__
	manager: ManagerClient
	filemanager: FilesManager
	agentlisteners: AgentListeners
	telemetry: SystemTelemetry
	isrunning = False
	isstopping = False
	runagent = True
	run_name: str = ""
	logdir: str = ""

	agentname = None
	mainloopinterval = 10
	jobs: dict = {}
	corethreads: dict[str, threading.Thread] = {}
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
			sys.exit()

		self.agentname = config.data['Agent']['agentname']

		self.manager = ManagerClient()

		FilesTransfers.ensuredir(config.data['Agent']['agentdir'])

		scriptdir = os.path.join(config.data['Agent']['agentdir'], "scripts")
		self.filemanager = FilesManager(self.manager, self.timeout, self.agentname, scriptdir)
		FilesTransfers.ensuredir(self.filemanager.scriptdir)

		self.logdir = os.path.join(config.data['Agent']['agentdir'], "logs")
		FilesTransfers.ensuredir(self.logdir)

		self.excludelibraries = config.data['Agent']['excludelibraries'].split(",")
		debug.debugmsg(6, "self.excludelibraries:", self.excludelibraries)

		if not self.args.create:
			IconManager.check_icons("RFSwarm Agent")

		self.agentproperties = collect_agent_properties(self.args, self.version)
		self.agentlisteners = AgentListeners(self.filemanager.scriptdir)
		self.agentlisteners.ensure_listener_file(self.agentproperties)
		self.agentlisteners.ensure_repeater_listener_file()

		self.telemetry = SystemTelemetry()

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
				self.corethreads["status"] = threading.Thread(target=self.updatestatus)
				self.corethreads["status"].start()

				if self.agentlisteners.listenerfile:
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
					if len(self.filemanager.upload_queue) > 0:
						self.status = f"Uploading ({len(self.filemanager.upload_queue)})"
						debug.debugmsg(5, "self.status:", self.status, "len(self.filemanager.upload_queue):", len(self.filemanager.upload_queue))
						self.corethreads["uploadqueue"] = threading.Thread(target=self.filemanager.process_file_upload_queue)
						self.corethreads["uploadqueue"].start()
					else:
						self.status = "Ready"
						self.corethreads["getscripts"] = threading.Thread(target=self.getscripts)
						self.corethreads["getscripts"].start()

						if len(self.filemanager.download_queue):
							self.status = f"Downloading ({len(self.filemanager.download_queue)})"

			if (prev_status == "Stopping" or "Uploading" in prev_status) and self.status == "Ready":
				# neet to reset something
				# I guess we can just reset the jobs disctionary?
				self.jobs = {}
				# pass

			time.sleep(self.mainloopinterval)

	def updatestatus(self):
		self.telemetry.start_background_updates()

		payload = {
			"AgentName": self.agentname,
			"AgentFQDN": socket.getfqdn(),
			"AgentIPs": self.telemetry.ipaddresslist,
			"CPU%": self.telemetry.get_cpu_percent(),
			"MEM%": self.telemetry.get_mem_percent(),
			"NET%": self.telemetry.netpct,
			"Robots": self.robotcount,
			"Monitor": self.monitorcount,
			"Status": self.status,
			"Properties": self.agentproperties,
			"FileCount": len(list(self.filemanager.scriptlist.keys()))
		}
		self.manager.post_agent_status(payload, timeout=self.timeout)

	def getscripts(self):
		debug.debugmsg(6, "getscripts")

		if len(list(self.filemanager.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			debug.debugmsg(5, "already processing the queue, don't double up")
			return

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
				self.manager.mark_disconnected()

		except Exception as e:
			debug.debugmsg(5, "Exception:", e)
			self.manager.mark_disconnected()

		if not self.manager.isconnected:
			return

		try:
			jsonresp = {}
			# self.filemanager.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(6, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

		if "Scripts" in jsonresp:
			for s in jsonresp["Scripts"]:
				hash = s['Hash']
				debug.debugmsg(6, "hash:", hash)
				if hash not in self.filemanager.scriptlist:
					debug.debugmsg(6, "getfile")
					self.filemanager.scriptlist[hash] = {'id': hash}
					if hash not in self.filemanager.download_queue:
						self.filemanager.download_queue.append(hash)
				else:
					debug.debugmsg(6, "Check file")
					if 'localfile' in self.filemanager.scriptlist[hash]:
						if (
							not os.path.isfile(self.filemanager.scriptlist[hash]['localfile'])
							and hash not in self.filemanager.download_queue
						):
							self.filemanager.download_queue.append(hash)
					else:
						debug.debugmsg(6, "getfile")
						self.filemanager.scriptlist[hash] = {'id': hash}
						if hash not in self.filemanager.download_queue:
							self.filemanager.download_queue.append(hash)

			if len(self.filemanager.download_queue):
				self.filemanager.process_file_download_queue()

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
				self.manager.mark_disconnected()

		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			self.manager.mark_disconnected()

		if not self.manager.isconnected:
			return

		try:
			jsonresp = {}
			# self.filemanager.scriptlist
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
						localval = os.path.abspath(os.path.join(self.filemanager.scriptdir, jsonresp["EnvironmentVariables"][envvar]["value"]))
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
				for s in jsonresp["Schedule"]:
					debug.debugmsg(6, "getjobs: s:", s)
					if s not in self.jobs:
						self.jobs[s] = {}
					for k in jsonresp["Schedule"][s]:
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

			debug.debugmsg(5, "getjobs: isrunning:", self.isrunning, "\tisstopping:", self.isstopping)
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
				if jobid in self.jobs:
					debug.debugmsg(6, "runjobs: jobid:", jobid)
					run_t = True
					if "Thread" in self.jobs[jobid]:
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

		self.agentlisteners.ensure_listener_file(self.agentproperties)
		self.agentlisteners.ensure_repeater_listener_file()

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

		# jobfile = os.path.join(self.filemanager.scriptdir, "job_{}.json".format(jobid))
		jobfile = os.path.join(self.filemanager.scriptdir, f"RFS_Job_{self.jobs[jobid]['ScriptIndex']}_{self.jobs[jobid]['Robot']}.json")

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

		if hash not in self.filemanager.scriptlist:
			self.filemanager.getfile(hash)

		if 'localfile' not in self.filemanager.scriptlist[hash]:
			if self.corethreads["getscripts"].is_alive():
				self.corethreads["getscripts"].join()
			else:
				self.corethreads["getscripts"] = threading.Thread(target=self.getscripts)
				self.corethreads["getscripts"].start()
				self.corethreads["getscripts"].join()
		# while 'localfile' not in self.filemanager.scriptlist[hash]:
		# 	time.sleep(1)

		localfile = self.filemanager.scriptlist[hash]['localfile']
		debug.debugmsg(6, "runthread: localfile:", localfile)

		file = self.filemanager.scriptlist[hash]['file']
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
		threaddirname = FilesTransfers.make_safe_filename(f"{farr[0]}_{jobid}_{self.jobs[jobid]['Iteration']}_{now}")
		odir = os.path.join(self.logdir, self.run_name, threaddirname)
		debug.debugmsg(6, "runthread: odir:", odir)
		try:
			if not os.path.exists(odir):
				os.makedirs(odir)
		except Exception:
			pass

		oprefix = FilesTransfers.make_safe_filename(test)
		debug.debugmsg(6, "runthread: oprefix:", oprefix)
		logFileName = os.path.join(odir, f"{oprefix}.log")
		debug.debugmsg(6, "runthread: logFileName:", logFileName)
		outputFileName = f"{oprefix}_output.xml"
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
		metavars.append(f"RFS_AGENTNAME:{self.agentname}")
		metavars.append(f"RFS_AGENTVERSION:{self.version}")
		metavars.append(f"RFS_DEBUGLEVEL:{debug.debuglvl}")
		metavars.append(f"RFS_INDEX:{self.jobs[jobid]['ScriptIndex']}")
		metavars.append(f"RFS_ROBOT:{self.jobs[jobid]['Robot']}")
		metavars.append(f"RFS_ITERATION:{self.jobs[jobid]['Iteration']}")
		metavars.append(f"RFS_SWARMMANAGER:{self.manager.swarmmanager}")
		metavars.append(f"RFS_EXCLUDELIBRARIES:{excludelibraries}")
		metavars.append(f"RFS_ROBOTTYPE:{self.jobs[jobid]['RobotType']}")

		if "excludesleep" in self.jobs[jobid]:
			metavars.append(f"RFS_EXCLUDESLEEP:{self.jobs[jobid]['excludesleep']}")

		if "includetesttime" in self.jobs[jobid]:
			metavars.append(f"RFS_INCLUDETESTTIME:{self.jobs[jobid]['includetesttime']}")

		if "applypacingtime" in self.jobs[jobid]:
			metavars.append(f"RFS_APPLYPACINGTIME:{self.jobs[jobid]['applypacingtime']}")

		if "applypacingstart" in self.jobs[jobid]:
			metavars.append(f"RFS_APPLYPACINGSTART:{self.jobs[jobid]['applypacingstart']}")

		if "injectsleepenabled" in self.jobs[jobid]:
			metavars.append(f"RFS_INJECTSLEEP:{self.jobs[jobid]['injectsleepenabled']}")
			if Utils.str2bool(self.jobs[jobid]["injectsleepenabled"]):
				# injectsleepminimum
				if "injectsleepminimum" in self.jobs[jobid]:
					metavars.append(f"RFS_SLEEPMINIMUM:{self.jobs[jobid]['injectsleepminimum']}")
				# injectsleepmaximum
				if "injectsleepmaximum" in self.jobs[jobid]:
					metavars.append(f"RFS_SLEEPMAXIMUM:{self.jobs[jobid]['injectsleepmaximum']}")

		if "resultnamemode" in self.jobs[jobid]:
			metavars.append(f"RFS_RESULTNAMEMODE:{self.jobs[jobid]['resultnamemode']}")

		for metavar in metavars:
			cmd.append(f"-M {metavar}")
			cmd.append(f"-v {metavar}")

		cmd.append(f'--listener "{self.agentlisteners.listenerfile}"')

		debug.debugmsg(9, "runthread: cmd:", cmd)

		debug.debugmsg(9, "Check for runthread: robotexe")
		if "testrepeater" in self.jobs[jobid]:
			debug.debugmsg(7, "runthread: self.jobs[jobid][testrepeater]:", self.jobs[jobid]["testrepeater"])
			debug.debugmsg(9, "runthread: self.jobs[jobid][testrepeater]:", Utils.str2bool(self.jobs[jobid]["testrepeater"]), type(Utils.str2bool(self.jobs[jobid]["testrepeater"])))
			if Utils.str2bool(self.jobs[jobid]["testrepeater"]):
				cmd.append(f'--listener "{self.agentlisteners.repeaterfile}"')

		debug.debugmsg(9, "runthread: cmd:", cmd)

		# disableloglog': 'True',
		if (
			"disableloglog" in self.jobs[jobid]
			and Utils.str2bool(self.jobs[jobid]["disableloglog"])
		):
			cmd.append("-l NONE")
		# 'disablelogreport': 'True',
		if (
			"disablelogreport" in self.jobs[jobid]
			and Utils.str2bool(self.jobs[jobid]["disablelogreport"])
		):
			cmd.append("-r NONE")
		# 'disablelogoutput': 'True',
		disablelogoutput = False
		if "disablelogoutput" in self.jobs[jobid]:
			disablelogoutput = Utils.str2bool(self.jobs[jobid]["disablelogoutput"])
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
				os.chdir(self.filemanager.scriptdir)
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
			rundir = os.path.join(self.logdir, self.run_name)
			self.filemanager.queue_file_upload(uploadmode, result, odir, rundir)

			if self.jobs[jobid]["RobotType"] in ["Monitor"]:
				self.monitorcount += -1
			else:
				self.robotcount += -1

		else:
			debug.debugmsg(1, "Could not find robot executeable:", robotexe)

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
					raise

			except Exception as e:
				debug.debugmsg(3, "Failed to exit with error:", e)
				os._exit(1)
		sys.stdout.flush()
		sys.stderr.flush()
