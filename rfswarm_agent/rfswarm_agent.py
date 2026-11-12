
# Robot Framework Swarm

# https://stackoverflow.com/questions/48090535/csv-file-reading-and-find-the-value-from-nth-column-using-robot-framework

import os
import socket
import sys
import threading
import time
from datetime import datetime
from typing import Any

from rfswarm_common.__version__ import __version__
from rfswarm_common.config import config
from rfswarm_common.debug import debug
from rfswarm_common.filestransfers import FilesTransfers
from rfswarm_common.icons import IconManager

from rfswarm_agent.agent.agent_listeners import AgentListeners
from rfswarm_agent.agent.files_manager import FilesManager
from rfswarm_agent.agent.jobs_manager import JobsManager
from rfswarm_agent.client.manager_client import ManagerClient
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
	jobsmanager: JobsManager
	runagent = True
	logdir: str = ""

	agentname = None
	mainloopinterval = 10
	corethreads: dict[str, threading.Thread] = {}
	status = "Ready"
	excludelibraries: Any = []
	args = None
	timeout = 600

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

		self.jobsmanager = JobsManager(
			self.manager,
			self.filemanager,
			self.agentlisteners,
			timeout=self.timeout,
			agentname=self.agentname,
			logdir=self.logdir,
			agentproperties=self.agentproperties,
			corethreads=self.corethreads,
		)

	def mainloop(self):
		debug.debugmsg(6, "mainloop")
		prev_status = self.status
		while self.runagent:
			debug.debugmsg(
				2, self.status, datetime.now().isoformat(sep=' ', timespec='seconds'),
				"(", int(time.time()), ")",
				"isconnected:", self.manager.isconnected,
				"isrunning:", self.jobsmanager.isrunning,
				"isstopping:", self.jobsmanager.isstopping,
				"robotcount:", self.jobsmanager.robotcount,
				"monitorcount:", self.jobsmanager.monitorcount,
				"\n"
			)

			if not self.manager.isconnected:
				# self.isrunning = False # Not sure if I need this?
				# self.connectmanager()
				t = threading.Thread(target=self.manager.connectmanager, name="connectmanager", args=(self.timeout,))
				t.start()
				self.jobsmanager.isrunning = False

			debug.debugmsg(5, "self.isconnected", self.manager.isconnected)
			if self.manager.isconnected:
				self.corethreads["status"] = threading.Thread(target=self.updatestatus)
				self.corethreads["status"].start()

				if self.agentlisteners.listenerfile:
					self.corethreads["getjobs"] = threading.Thread(target=self.jobsmanager.getjobs, args=(self.filemanager.scriptdir,))
					self.corethreads["getjobs"].start()

				if self.jobsmanager.isrunning:
					self.mainloopinterval = 2
					self.status = "Running"
					if self.jobsmanager.isstopping:
						self.status = "Stopping"
					# else:
					self.corethreads["runjobs"] = threading.Thread(target=self.jobsmanager.runjobs)
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
						self.corethreads["getscripts"] = threading.Thread(target=self.filemanager.getscripts)
						self.corethreads["getscripts"].start()

						if len(self.filemanager.download_queue):
							self.status = f"Downloading ({len(self.filemanager.download_queue)})"

			if (prev_status == "Stopping" or "Uploading" in prev_status) and self.status == "Ready":
				# neet to reset something
				# I guess we can just reset the jobs disctionary?
				self.jobsmanager.jobs = {}

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
			"Robots": self.jobsmanager.robotcount,
			"Monitor": self.jobsmanager.monitorcount,
			"Status": self.status,
			"Properties": self.agentproperties,
			"FileCount": len(list(self.filemanager.scriptlist.keys()))
		}
		self.manager.post_agent_status(payload, timeout=self.timeout)

	def on_closing(self, _event=None, *args):
		self.runagent = False
		debug.debugmsg(0, "Shutting down agent")

		for thread in self.corethreads:
			debug.debugmsg(3, "Join Agent Thread:", thread)
			self.corethreads[thread].join()

		for jobid in self.jobsmanager.jobs:
			debug.debugmsg(3, "Join Agent Thread:", jobid)
			if "Thread" in self.jobsmanager.jobs[jobid]:
				self.jobsmanager.jobs[jobid]["Thread"].join()

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
