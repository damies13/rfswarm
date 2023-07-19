#!/usr/bin/python
#
# 	Robot Framework Swarm
#
#    Version 1.1.4
#


# https://stackoverflow.com/questions/48090535/csv-file-reading-and-find-the-value-from-nth-column-using-robot-framework

import argparse
import base64
import configparser
import hashlib
import inspect
import json
import lzma
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import pkg_resources
import psutil
import requests


class RFSwarmAgent():

	version = "1.1.4"
	config = None
	isconnected = False
	isrunning = False
	isstopping = False
	runagent = True
	run_name = None
	swarmmanager = None
	agentdir = None
	scriptdir = None
	logdir = None
	agentini = None
	listenerfile = None
	ipaddresslist: Any = []
	agentname = None
	agentproperties: Any = {}
	netpct = 0
	mainloopinterval = 10
	scriptlist: Any = {}
	jobs: Any = {}
	corethreads: Any = {}
	upload_queue: Any = []
	robotcount = 0
	status = "Ready"
	excludelibraries: Any = []
	args = None
	xmlmode = False
	timeout = 600
	uploadmode = "err"

	debuglvl = 0

	def __init__(self, master=None):
		self.debugmsg(0, "Robot Framework Swarm: Run Agent")
		self.debugmsg(0, "	Version", self.version)
		self.agentproperties["RFSwarmAgent: Version"] = self.version
		self.debugmsg(6, "__init__")
		self.debugmsg(6, "gettempdir", tempfile.gettempdir())
		self.debugmsg(6, "tempdir", tempfile.tempdir)

		parser = argparse.ArgumentParser()
		parser.add_argument('-g', '--debug', help='Set debug level, default level is 0')
		parser.add_argument('-v', '--version', help='Display the version and exit', action='store_true')
		parser.add_argument('-i', '--ini', help='path to alternate ini file')
		parser.add_argument('-m', '--manager', help='The manager to connect to e.g. http://localhost:8138/')
		parser.add_argument('-d', '--agentdir', help='The directory the agent should use for files')
		parser.add_argument('-r', '--robot', help='The robot framework executable')
		parser.add_argument('-x', '--xmlmode', help='XML Mode, fall back to pasing the output.xml after each iteration', action='store_true')
		parser.add_argument('-a', '--agentname', help='Set agent name')
		parser.add_argument('-p', '--property', help='Add a custom property, if multiple properties are required use this argument for each property e.g. -p property1 -p "Property 2"', action='append')
		self.args = parser.parse_args()

		self.debugmsg(6, "self.args: ", self.args)

		if self.args.debug:
			self.debuglvl = int(self.args.debug)

		if self.args.version:
			exit()

		self.config = configparser.ConfigParser()

		self.agentini = self.findiniloctaion()

		if os.path.isfile(self.agentini):
			self.debugmsg(6, "agentini: ", self.agentini)
			self.config.read(self.agentini)
		else:
			self.saveini()

		self.debugmsg(0, "	Configuration File: ", self.agentini)

		if self.args.agentname:
			self.agentname = self.args.agentname

		if 'Agent' not in self.config:
			self.config['Agent'] = {}
			self.saveini()

		if 'agentname' not in self.config['Agent']:
			self.config['Agent']['agentname'] = socket.gethostname()
			self.saveini()

		if not self.args.agentname:
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

		if 'properties' not in self.config['Agent']:
			self.config['Agent']['properties'] = ""
			self.saveini()

		self.ensure_listner_file()

		t = threading.Thread(target=self.tick_counter)
		t.start()

		t = threading.Thread(target=self.findlibraries)
		t.start()

		self.agentproperties["OS: Platform"] = platform.platform()  # 'Linux-3.3.0-8.fc16.x86_64-x86_64-with-fedora-16-Verne'
		self.agentproperties["OS: System"] = platform.system()  # 'Windows'		Returns the system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'
		self.agentproperties["OS: Release"] = platform.release()  # 'XP'
		self.agentproperties["OS: Version"] = platform.version()  # '5.1.2600'

		if platform.system() == 'Windows':
			vararr = platform.version().split(".")
		else:
			vararr = platform.release().split(".")

		if len(vararr) > 0:
			self.agentproperties["OS: Version: Major"] = "{}".format(int(vararr[0]))
		if len(vararr) > 1:
			self.agentproperties["OS: Version: Minor"] = "{}.{}".format(int(vararr[0]), int(vararr[1]))

		if 'properties' in self.config['Agent'] and len(self.config['Agent']['properties']) > 0:
			if "," in self.config['Agent']['properties']:
				proplist = self.config['Agent']['properties'].split(",")
				for prop in proplist:
					self.agentproperties["{}".format(prop.strip())] = True
			else:
				self.agentproperties["{}".format(self.config['Agent']['properties'].strip())] = True

		if self.args.property:
			self.debugmsg(7, "self.args.property: ", self.args.property)
			for prop in self.args.property:
				self.agentproperties["{}".format(prop.strip())] = True

		self.debugmsg(9, "self.agentproperties: ", self.agentproperties)

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

		inifilename = "RFSwarmAgent.ini"
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
				except Exception:
					pass
		# This should cause saveini to fail?
		return None

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
					the_line = stack[1][0].f_lineno
					prefix = "{}: {}({}): [{}:{}]	".format(str(the_class), the_method, the_line, self.debuglvl, lvl)
					if len(prefix.strip()) < 32:
						prefix = "{}	".format(prefix)
					if len(prefix.strip()) < 24:
						prefix = "{}	".format(prefix)

					msglst.append(str(prefix))

				for itm in msg:
					msglst.append(str(itm))
				print(" ".join(msglst))
			except Exception:
				pass

	def str2bool(self, instr):
		return str(instr).lower() in ("yes", "true", "t", "1")

	def mainloop(self):
		self.debugmsg(6, "mainloop")
		prev_status = self.status
		while self.runagent:
			self.debugmsg(
				2, self.status, datetime.now().isoformat(sep=' ', timespec='seconds'),
				"(", int(time.time()), ")",
				"isconnected:", self.isconnected,
				"isrunning:", self.isrunning,
				"isstopping:", self.isstopping,
				"robotcount:", self.robotcount,
				"\n"
			)

			if not self.isconnected:
				# self.isrunning = False # Not sure if I need this?
				# self.connectmanager()
				t = threading.Thread(target=self.connectmanager)
				t.start()
				self.isrunning = False

			self.debugmsg(5, "self.isconnected", self.isconnected)
			if self.isconnected:
				# self.updatestatus()
				self.corethreads["status"] = threading.Thread(target=self.updatestatus)
				self.corethreads["status"].start()

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
						self.debugmsg(5, "self.status:", self.status, "len(self.upload_queue):", len(self.upload_queue))
						self.corethreads["uploadqueue"] = threading.Thread(target=self.process_file_upload_queue)
						self.corethreads["uploadqueue"].start()
					else:
						self.status = "Ready"
						self.corethreads["getscripts"] = threading.Thread(target=self.getscripts)
						self.corethreads["getscripts"].start()

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
			if nicstats[nic].speed > 0:
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
					netpctlist.append((bytes_max_sec / bytes_speed) * 100)
				else:
					netpctlist.append(0)

		if len(netpctlist) > 0:
			self.debugmsg(6, "netpctlist:	", netpctlist)
			self.netpct = max(netpctlist)
			self.debugmsg(6, "self.netpct:	", self.netpct)
		else:
			self.netpct = 0

	def updatestatus(self):
		self.debugmsg(6, "self.swarmmanager:", self.swarmmanager)
		uri = self.swarmmanager + "AgentStatus"

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
			"Status": self.status,
			"Properties": self.agentproperties
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			self.debugmsg(8, r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok, r.text)
				self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.isconnected = False
				self.debugmsg(7, "self.isconnected", self.isconnected)
		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.isconnected = False
			self.debugmsg(5, "self.isconnected", self.isconnected)

	def connectmanager(self):
		self.debugmsg(6, "connectmanager")
		if self.swarmmanager is None:
			self.findmanager()
			if self.args.manager:
				self.debugmsg(7, "self.args.manager: ", self.args.manager)
				if self.args.manager[-1] != '/':
					self.swarmmanager = "{}/".format(self.args.manager)
				else:
					self.swarmmanager = self.args.manager

		if self.swarmmanager is not None:
			self.debugmsg(2, "Try connecting to", self.swarmmanager)
			self.debugmsg(6, "self.swarmmanager:", self.swarmmanager)
			try:
				r = requests.get(self.swarmmanager, timeout=self.timeout)
				self.debugmsg(8, r.status_code, r.text)
				if (r.status_code == requests.codes.ok):
					self.debugmsg(7, "r.status_code:", r.status_code, requests.codes.ok, r.text)
					self.isconnected = True
					self.debugmsg(0, "Manager Connected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			except Exception:
				pass

	def findmanager(self):
		self.debugmsg(6, "findmanager")
		self.debugmsg(6, "findmanager:", self.config)
		if 'Agent' in self.config:
			self.debugmsg(6, "findmanager:", self.config['Agent'])
			pass
		else:
			self.config['Agent'] = {}
			self.saveini()

		if 'swarmserver' in self.config['Agent']:
			if 'swarmmanager' not in self.config['Agent']:
				self.config['Agent']['swarmmanager'] = self.config['Agent']['swarmserver']
			del self.config['Agent']['swarmserver']
			self.saveini()

		if 'swarmmanager' in self.config['Agent']:
			self.debugmsg(6, "findmanager: Agent:swarmmanager =", self.config['Agent']['swarmmanager'])
			self.swarmmanager = self.config['Agent']['swarmmanager']
			if self.swarmmanager[-1] != '/':
				self.swarmmanager = "{}/".format(self.swarmmanager)
		else:
			self.config['Agent']['swarmmanager'] = "http://localhost:8138/"
			self.saveini()

	def findlibraries(self):
		found = 0
		liblst = []
		# import pkg_resources
		installed_packages = list(pkg_resources.working_set)
		# self.debugmsg(5, "installed_packages:", installed_packages)
		for i in installed_packages:
			# self.debugmsg(5, "i:", i)
			# self.debugmsg(5, "type(i):", type(i))

			# self.debugmsg(5, "i.key:", i.key)
			# self.debugmsg(5, "i.value:", installed_packages[i])
			# self.debugmsg(5, "i value:", str(i).split(" ")[1])

			if i.key.strip() == "robotframework":
				found = 1
			if i.key.startswith("robotframework-"):
				# print(i.key)
				keyarr = i.key.strip().split("-")
				#  next overwrites previous
				self.agentproperties["RobotFramework: Library: " + keyarr[1]] = str(i).split(" ")[1]
				liblst.append(keyarr[1])

		self.debugmsg(8, "liblst:", liblst, len(liblst))
		if len(liblst) > 0:
			self.debugmsg(7, "liblst:", ", ".join(liblst))
			self.agentproperties["RobotFramework: Libraries"] = ", ".join(liblst)

		if not found:
			self.debugmsg(0, "RobotFramework is not installed!!!")
			self.debugmsg(0, "RobotFramework is required for the agent to run scripts")
			self.debugmsg(0, "Perhaps try: 'pip install robotframework'")
			raise Exception("RobotFramework is not installed")

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

			# https://github.com/damies13/rfswarm/blob/v0.6.2/Doc/Images/z_agent.txt
			url = "https://github.com/damies13/rfswarm/blob/" + ver + "/Doc/Images/z_agent.txt"
			try:
				r = requests.get(url, timeout=self.timeout)
				self.debugmsg(9, "tick_counter:", r.status_code)
			except Exception:
				pass
			time.sleep(aday)

	def getscripts(self):
		self.debugmsg(6, "getscripts")
		uri = self.swarmmanager + "Scripts"
		payload = {
			"AgentName": self.agentname
		}
		self.debugmsg(6, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			self.debugmsg(6, "resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.isconnected = False

		except Exception as e:
			self.debugmsg(5, "Exception:", e)
			self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			self.debugmsg(6, "jsonresp:", jsonresp)
		except Exception as e:
			self.debugmsg(1, "Exception:", e)

		for s in jsonresp["Scripts"]:
			hash = s['Hash']
			self.debugmsg(6, "hash:", hash)
			if hash not in self.scriptlist:
				self.debugmsg(6, "getfile")
				self.scriptlist[hash] = {'id': hash}
				t = threading.Thread(target=self.getfile, args=(hash,))
				t.start()
			else:
				# self.scriptlist[hash]['localfile']
				self.debugmsg(6, "Check file")
				if 'localfile' in self.scriptlist[hash]:
					if not os.path.isfile(self.scriptlist[hash]['localfile']):
						t = threading.Thread(target=self.getfile, args=(hash,))
						t.start()
				else:
					self.debugmsg(6, "getfile")
					self.scriptlist[hash] = {'id': hash}
					t = threading.Thread(target=self.getfile, args=(hash,))
					t.start()

	def getfile(self, hash):
		self.debugmsg(6, "hash: ", hash)
		uri = self.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Download",
			"Hash": hash
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			self.debugmsg(6, "resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.isconnected = False

		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
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
		uri = self.swarmmanager + "Jobs"
		payload = {
			"AgentName": self.agentname
		}
		self.debugmsg(9, "getjobs: payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			self.debugmsg(7, "getjobs: resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.debugmsg(7, "r.status_code:", r.status_code, requests.codes.ok)
				self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.isconnected = False

		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.isconnected = False

		if not self.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			self.debugmsg(7, "getjobs: r.text:", r.text)
			jsonresp = json.loads(r.text)
			self.debugmsg(7, "getjobs: jsonresp:", jsonresp)

			if jsonresp["StartTime"] < int(time.time()) < (jsonresp["EndTime"] + 300):
				self.isrunning = True
				self.run_name = jsonresp["RunName"]
				for s in jsonresp["Schedule"].keys():
					self.debugmsg(6, "getjobs: s:", s)
					if s not in self.jobs.keys():
						self.jobs[s] = {}
					for k in jsonresp["Schedule"][s].keys():
						self.debugmsg(6, "getjobs: self.jobs[", s, "][", k, "]", jsonresp["Schedule"][s][k])
						self.jobs[s][k] = jsonresp["Schedule"][s][k]
					if "UploadMode" in jsonresp:
						self.jobs[s]["UploadMode"] = jsonresp["UploadMode"]

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

			self.debugmsg(7, "jsonresp[Abort]", jsonresp["Abort"])
			if jsonresp["Abort"]:
				self.isstopping = True
				self.debugmsg(5, "!!! Abort !!!")
				self.abortjobs()

			self.debugmsg(5, "getjobs: isrunning:", self.isrunning, "	isstopping:", self.isstopping)
			self.debugmsg(7, "getjobs: self.jobs:", self.jobs)

		except Exception as e:
			self.debugmsg(1, "getjobs: Exception:", e)

	def abortjobs(self):
		self.debugmsg(6, "self.jobs:", self.jobs)
		for job in self.jobs:
			try:
				self.debugmsg(6, "job:", job, self.jobs[job])
				self.debugmsg(5, "job[PID]:", self.jobs[job]["PID"])
				self.debugmsg(6, "job[Process]:", self.jobs[job]["Process"])
				p = self.jobs[job]["Process"]
				p.terminate()

			except Exception as e:
				self.debugmsg(1, "getjobs: Exception:", e)

	def runjobs(self):
		self.debugmsg(6, "runjobs: self.jobs:", self.jobs)
		workingkeys = list(self.jobs.keys())
		if not self.isstopping:
			for jobid in workingkeys:
				if jobid in self.jobs.keys():
					self.debugmsg(6, "runjobs: jobid:", jobid)
					run_t = True
					if "Thread" in self.jobs[jobid].keys():
						self.debugmsg(7, "jobid:", self.jobs[jobid])
						try:
							# if self.jobs[jobid]["Thread"].isAlive():
							# The isAlive syntax above was perviously working in python < 3.7
							# but appears to have been removed in 3.9.1? it was depricated in 2.x?
							# and the is_alive syntax below has been available since python version 2.6
							if self.jobs[jobid]["Thread"].is_alive():
								run_t = False
								self.debugmsg(7, "Thread already running run_t:", run_t)
						except Exception as e:
							run_t = False
							self.debugmsg(5, "Thread running check failed run_t:", run_t, e)

					self.debugmsg(6, "run_t:", run_t)

					if run_t:
						self.debugmsg(5, "jobid:", jobid, "run_t:", run_t, "StartTime:", self.jobs[jobid]["StartTime"], "< Now:", int(time.time()), "< EndTime:", self.jobs[jobid]["EndTime"])
						if self.jobs[jobid]["StartTime"] < int(time.time()) < self.jobs[jobid]["EndTime"]:
							t = threading.Thread(target=self.runthread, args=(jobid, ))
							t.start()
							self.jobs[jobid]["Thread"] = t
							self.debugmsg(5, "Thread started for jobid:", jobid)
						else:
							self.debugmsg(5, "Thread not started for jobid:", jobid)
				time.sleep(0.1)

	def runthread(self, jobid):
		now = int(time.time())

		self.ensure_listner_file()

		if "ScriptIndex" not in self.jobs[jobid]:
			self.debugmsg(6, "runthread: jobid:", jobid)
			self.debugmsg(6, "runthread: job data:", self.jobs[jobid])
			jobarr = jobid.split("_")
			self.jobs[jobid]["ScriptIndex"] = jobarr[0]
			self.jobs[jobid]["Robot"] = jobarr[1]
			self.jobs[jobid]["Iteration"] = 0
			self.debugmsg(6, "runthread: job data:", self.jobs[jobid])

		self.jobs[jobid]["Iteration"] += 1

		hash = self.jobs[jobid]['ScriptHash']
		self.debugmsg(6, "runthread: hash:", hash)
		test = self.jobs[jobid]['Test']
		self.debugmsg(6, "runthread: test:", test)
		if platform.system() != 'Windows':
			test = test.replace(r'${', r'\${')
			self.debugmsg(6, "runthread: test:", test)

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
		self.debugmsg(6, "runthread: localfile:", localfile)

		file = self.scriptlist[hash]['file']
		self.debugmsg(6, "runthread: file:", file)

		farr = os.path.splitext(file)
		self.debugmsg(6, "runthread: farr:", farr)

		excludelibraries = ",".join(self.excludelibraries)
		if "excludelibraries" in self.jobs[jobid]:
			# not sure if we need to do this???
			# for safety split and join string
			# ellst = self.jobs[jobid]['excludelibraries'].split(",")
			# excludelibraries = ",".join(ellst)
			excludelibraries = self.jobs[jobid]['excludelibraries']

		# self.run_name
		# scriptdir = None
		# logdir = None

		rundir = os.path.join(self.logdir, self.run_name)
		try:
			if not os.path.exists(rundir):
				os.makedirs(rundir)
		except Exception:
			pass

		threaddirname = self.make_safe_filename("{}_{}_{}_{}".format(farr[0], jobid, self.jobs[jobid]["Iteration"], now))
		odir = os.path.join(self.logdir, self.run_name, threaddirname)
		self.debugmsg(6, "runthread: odir:", odir)
		try:
			if not os.path.exists(odir):
				os.makedirs(odir)
		except Exception:
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
		cmd.append('"' + test + '"')
		cmd.append("-d")
		cmd.append('"' + odir + '"')

		metavars = []
		metavars.append("RFS_AGENTNAME:{}".format(self.agentname))
		metavars.append("RFS_AGENTVERSION:{}".format(self.version))
		metavars.append("RFS_DEBUGLEVEL:{}".format(self.debuglvl))
		metavars.append("RFS_INDEX:{}".format(self.jobs[jobid]["ScriptIndex"]))
		metavars.append("RFS_ROBOT:{}".format(self.jobs[jobid]["Robot"]))
		metavars.append("RFS_ITERATION:{}".format(self.jobs[jobid]["Iteration"]))
		metavars.append("RFS_SWARMMANAGER:{}".format(self.swarmmanager))
		metavars.append("RFS_EXCLUDELIBRARIES:{}".format(excludelibraries))

		for metavar in metavars:
			cmd.append("-M {}".format(metavar))
			cmd.append("-v {}".format(metavar))

		if not self.xmlmode:
			cmd.append("--listener {}".format('"' + self.listenerfile + '"'))

		if "robotoptions" in self.jobs[jobid]:
			cmd.append("{}".format(self.jobs[jobid]['robotoptions']))

		cmd.append("-o")
		cmd.append('"' + outputFile + '"')

		cmd.append('"' + localfile + '"')

		robotexe = shutil.which(robotcmd)
		self.debugmsg(6, "runthread: robotexe:", robotexe)
		if robotexe is not None:
			self.robotcount += 1

			result = 0
			try:
				# https://stackoverflow.com/questions/4856583/how-do-i-pipe-a-subprocess-call-to-a-text-file
				with open(logFileName, "w") as f:
					self.debugmsg(3, "Robot run with command: '", " ".join(cmd), "'")
					# result = subprocess.call(" ".join(cmd), shell=True, stdout=f, stderr=f)
					try:
						proc = subprocess.Popen(" ".join(cmd), shell=True, stdout=f, stderr=subprocess.STDOUT)
						self.debugmsg(5, "runthread: proc:", proc)
						self.jobs[jobid]["Process"] = proc
						self.jobs[jobid]["PID"] = proc.pid
						self.debugmsg(5, "runthread: proc.pid:", proc.pid)
						result = proc.wait()
						self.debugmsg(5, "runthread: result:", result)
						if result != 0:
							self.debugmsg(1, "Robot returned an error (", result, ") please check the log file:", logFileName)
					except Exception as e:
						self.debugmsg(1, "Robot returned an error:", e, " \nplease check the log file:", logFileName)
						result = 1
					f.close()

				if self.xmlmode:
					if os.path.exists(outputFile):
						if self.xmlmode:
							t = threading.Thread(target=self.run_process_output, args=(outputFile, self.jobs[jobid]["ScriptIndex"], self.jobs[jobid]["Robot"], self.jobs[jobid]["Iteration"]))
							t.start()
					else:
						self.debugmsg(1, "Robot didn't create (", outputFile, ") please check the log file:", logFileName)

			except Exception as e:
				self.debugmsg(5, "Robot returned an error:", e)
				result = 1

			uploadmode = self.uploadmode
			self.debugmsg(5, "uploadmode:", uploadmode)
			self.debugmsg(5, "self.jobs[", jobid, "]:", self.jobs[jobid])
			if "UploadMode" in self.jobs[jobid]:
				uploadmode = self.jobs[jobid]["UploadMode"]
				self.debugmsg(5, "uploadmode:", uploadmode)

			# Uplad any files found
			self.queue_file_upload(uploadmode, result, odir)

			self.robotcount += -1
		else:
			self.debugmsg(1, "Could not find robot executeable:", robotexe)

	def queue_file_upload(self, mode, retcode, filedir):
		reldir = os.path.basename(filedir)
		self.debugmsg(7, mode, retcode, reldir, filedir)

		filelst = self.file_upload_list(filedir)
		self.debugmsg(7, "filelst", filelst)
		# filelst
		# [
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1.log',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/log.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/report.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1_output.xml'
		# ]
		#

		rundir = os.path.join(self.logdir, self.run_name)

		self.debugmsg(5, "mode:", mode, "	retcode:", retcode)
		# 	uploadmodes = {'imm':"Immediately", 'err':"On Error Only", 'def':"All Defered"}

		for file in filelst:
			fobj = {}
			fobj["LocalFilePath"] = file
			fobj["RelFilePath"] = os.path.relpath(file, start=rundir)
			self.upload_queue.append(fobj)
			self.debugmsg(7, "added to upload_queue", fobj)
			if mode == "err" and retcode > 0:
				# upload now
				self.file_upload(fobj)
			if mode == "imm":
				# upload now
				self.file_upload(fobj)

	def file_upload_list(self, filedir):
		retlst = []
		dirlst = os.listdir(path=filedir)
		self.debugmsg(7, "dirlst", dirlst)
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
		self.debugmsg(7, "fileobj", fileobj)

		# Hash file

		hash = self.hash_file(fileobj['LocalFilePath'], fileobj['RelFilePath'])
		self.debugmsg(7, "hash", hash)

		# 	check file exists on manager?

		uri = self.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Status",
			"Hash": hash
		}
		self.debugmsg(9, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			self.debugmsg(7, "resp: ", r.status_code, r.text)
			if (r.status_code != requests.codes.ok):
				self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.isconnected = False

		except Exception as e:
			self.debugmsg(8, "Exception:", e)
			self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.isconnected = False

		if not self.isconnected:
			return None

		jsonresp = {}
		try:
			# self.scriptlist
			jsonresp = json.loads(r.text)
			self.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			self.debugmsg(1, "Exception:", e)
			return None

		# 	If file not exists upload the file
		if jsonresp["Exists"] == "False":
			self.debugmsg(6, "file not there, so lets upload")

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
			self.debugmsg(9, "buf:", buf)
			compressed = lzma.compress(buf)
			self.debugmsg(9, "compressed:", compressed)
			encoded = base64.b64encode(compressed)
			self.debugmsg(9, "encoded:", encoded)

			payload["FileData"] = encoded.decode('ASCII')

			self.debugmsg(8, "payload: ", payload)

			try:
				r = requests.post(uri, json=payload, timeout=self.timeout)
				self.debugmsg(7, "resp: ", r.status_code, r.text)
				if (r.status_code != requests.codes.ok):
					self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
					self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
					self.isconnected = False

			except Exception as e:
				self.debugmsg(8, "Exception:", e)
				self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.isconnected = False

			if not self.isconnected:
				return None

			jsonresp = {}
			try:
				# self.scriptlist
				jsonresp = json.loads(r.text)
				self.debugmsg(7, "jsonresp:", jsonresp)
			except Exception as e:
				self.debugmsg(1, "Exception:", e)
				return None

		# once sucessful remove from queue
		if fileobj in self.upload_queue:
			self.upload_queue.remove(fileobj)

	def hash_file(self, file, relpath):
		BLOCKSIZE = 65536
		hasher = hashlib.md5()
		hasher.update(str(os.path.getmtime(file)).encode('utf-8'))
		hasher.update(relpath.encode('utf-8'))
		with open(file, 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
		self.debugmsg(3, "file:", file, "	hash:", hasher.hexdigest())
		return hasher.hexdigest()

	def process_file_upload_queue(self):
		self.debugmsg(7, "upload_queue", self.upload_queue)
		# self.process_file_upload_queue
		for fobj in self.upload_queue:
			# probably need to make this multi-treaded
			# self.file_upload(fobj)
			t = threading.Thread(target=self.file_upload, args=(fobj,))
			t.start()
			time.sleep(0.5)

	def run_process_output(self, outputFile, index, robot, iter):
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
		except Exception:
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

				self.debugmsg(
					6, "resultname: '", txn,
					"' result'", status,
					"' elapsedtime'", elapsedtime,
					"' starttime'", starttime,
					"' endtime'", endtime, "'"
				)

				# Send result to manager
				uri = self.swarmmanager + "Result"

				self.debugmsg(6, "run_proces_output: uri", uri)

				# requiredfields = ["AgentName", "ResultName", "Result", "ElapsedTime", "StartTime", "EndTime"]

				payload = {
					"AgentName": self.agentname,
					"ResultName": txn,
					"Result": status,
					"ElapsedTime": elapsedtime,
					"StartTime": startdate.timestamp(),
					"EndTime": enddate.timestamp(),
					"ScriptIndex": index,
					"Robot": robot,
					"Iteration": iter,
					"Sequence": seq
				}

				self.debugmsg(6, "run_proces_output: payload", payload)
				try:
					r = requests.post(uri, json=payload, timeout=self.timeout)
					self.debugmsg(6, "run_proces_output: ", r.status_code, r.text)
					if (r.status_code != requests.codes.ok):
						self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
						self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
						self.isconnected = False
				except Exception as e:
					self.debugmsg(8, "Exception:", e)
					self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
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

	def ensure_listner_file(self):
		if not self.xmlmode:
			self.debugmsg(6, "self.xmlmode: ", self.xmlmode)
			if self.listenerfile is None:
				self.create_listner_file()
			else:
				if not os.path.isfile(self.listenerfile):
					self.create_listner_file()

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
		fd.append("import threading")
		fd.append("")
		fd.append("class RFSListener2:")
		fd.append("	ROBOT_LISTENER_API_VERSION = 2")
		fd.append("")
		fd.append("	msg = None")
		fd.append("	swarmmanager = \"http://localhost:8138/\"")
		fd.append("	excludelibraries = [\"BuiltIn\",\"String\",\"OperatingSystem\",\"perftest\"]")
		fd.append("	debuglevel = 0")
		fd.append("	index = 0")
		fd.append("	robot = 0")
		fd.append("	iter = 0")
		fd.append("	seq = 0")
		fd.append("")
		fd.append("	def start_suite(self, name, attrs):")
		fd.append("		if 'RFS_DEBUGLEVEL' in attrs['metadata']:")
		fd.append("			self.debuglevel = int(attrs['metadata']['RFS_DEBUGLEVEL'])")
		fd.append("			self.debugmsg(6, 'debuglevel: ', self.debuglevel)")
		fd.append("		if 'RFS_INDEX' in attrs['metadata']:")
		fd.append("			self.index = attrs['metadata']['RFS_INDEX']")
		fd.append("			self.debugmsg(6, 'index: ', self.index)")
		fd.append("		if 'RFS_ITERATION' in attrs['metadata']:")
		fd.append("			self.iter = attrs['metadata']['RFS_ITERATION']")
		fd.append("			self.debugmsg(6, 'iter: ', self.iter)")
		fd.append("		if 'RFS_ROBOT' in attrs['metadata']:")
		fd.append("			self.robot = attrs['metadata']['RFS_ROBOT']")
		fd.append("			self.debugmsg(6, 'robot: ', self.robot)")
		fd.append("		if 'RFS_SWARMMANAGER' in attrs['metadata']:")
		fd.append("			self.swarmmanager = attrs['metadata']['RFS_SWARMMANAGER']")
		fd.append("			self.debugmsg(6, 'swarmmanager: ', self.swarmmanager)")
		fd.append("		if 'RFS_EXCLUDELIBRARIES' in attrs['metadata']:")
		fd.append("			self.excludelibraries = attrs['metadata']['RFS_EXCLUDELIBRARIES'].split(\",\")")
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
		fd.append("		self.debugmsg(3, 'Keyword name: ', name)")
		fd.append("		self.debugmsg(6, 'attrs: ', attrs)")
		fd.append("		self.debugmsg(5, 'attrs[doc]: ', attrs['doc'])")
		fd.append("		self.debugmsg(5, 'self.msg: ', self.msg)")
		fd.append("		")
		fd.append("		ResultName = ''")
		# fd.append("		#	'level': 'TRACE'")
		fd.append("		istrace = False")
		fd.append("		if self.msg is not None and 'level' in self.msg and self.msg['level'] == 'TRACE':")
		fd.append("			istrace = True")
		fd.append("		")
		fd.append("		if self.msg is not None and 'message' in self.msg and not istrace:")
		fd.append("			ResultName = self.msg['message']")
		fd.append("		elif 'doc' in attrs and len(attrs['doc'])>0:")
		fd.append("			ResultName = attrs['doc']")
		# Quiet Keyword -> https://github.com/damies13/rfswarm/blob/master/Doc/Preparing_for_perf.md#keywords
		# fd.append("		elif '${' not in name:")
		# fd.append("			ResultName = name")
		fd.append("		self.debugmsg(3, 'ResultName: ', ResultName, '	:', len(ResultName))")
		fd.append("		")
		fd.append("		if len(ResultName)>0:")
		fd.append("			self.debugmsg(8, 'self.msg: attrs[libname]: ', attrs['libname'], '	excludelibraries:', self.excludelibraries)")
		fd.append("			if attrs['libname'] not in self.excludelibraries:")
		fd.append("				self.debugmsg(5, attrs['libname'], 'library OK')")
		fd.append("				self.seq += 1")
		fd.append("				self.debugmsg(8, 'self.seq: ', self.seq)")
		fd.append("				startdate = datetime.strptime(attrs['starttime'], '%Y%m%d %H:%M:%S.%f')")
		fd.append("				enddate = datetime.strptime(attrs['endtime'], '%Y%m%d %H:%M:%S.%f')")
		fd.append("				self.debugmsg(5, 'Send ResultName: ', ResultName)")
		fd.append("				payload = {")
		fd.append("					'AgentName': '" + self.agentname + "',")
		fd.append("					'ResultName': ResultName,")
		fd.append("					'Result': attrs['status'],")
		fd.append("					'ElapsedTime': (attrs['elapsedtime']/1000),")
		fd.append("					'StartTime': startdate.timestamp(),")
		fd.append("					'EndTime': enddate.timestamp(),")
		fd.append("					'ScriptIndex': self.index,")
		fd.append("					'Robot': self.robot,")
		fd.append("					'Iteration': self.iter,")
		fd.append("					'Sequence': self.seq")
		fd.append("				}")
		fd.append("				self.debugmsg(7, 'payload: ', payload)")
		# fd.append("				self.send_result(payload)")
		fd.append("				t = threading.Thread(target=self.send_result, args=(payload,))")
		fd.append("				t.start()")
		fd.append("			else:")
		fd.append("				self.debugmsg(5, attrs['libname'], 'is an excluded library')")
		fd.append("		")
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
		fd.append("		exceptn = None")
		fd.append("		retry = True")
		fd.append("		count = 100")
		fd.append("		uri = self.swarmmanager + 'Result'")
		fd.append("		while retry and count>0:")
		fd.append("			try:")
		fd.append("				r = requests.post(uri, json=payload, timeout=600)")
		fd.append("				self.debugmsg(7, 'send_result: ',r.status_code, r.text)")
		fd.append("				if (r.status_code != requests.codes.ok):")
		fd.append("					exceptn = r.status_code")
		fd.append("				else:")
		fd.append("					retry = False")
		fd.append("			except Exception as e:")
		fd.append("				exceptn = e")
		fd.append("			time.sleep(1)")
		fd.append("			count -= 1")
		fd.append("		if retry:")
		fd.append("			self.debugmsg(0, 'send_result: while attempting to send result to', uri)")
		fd.append("			self.debugmsg(0, 'send_result: with payload:', payload)")
		fd.append("			self.debugmsg(0, 'send_result: Exception:', exceptn)")
		fd.append("")

		# print("RFSwarmAgent: create_listner_file: listenerfile: ", self.listenerfile)
		with open(self.listenerfile, 'w+') as lf:
			# lf.writelines(fd)
			lf.write('\n'.join(fd))

	def on_closing(self, _event=None, *args):
		self.runagent = False
		self.debugmsg(0, "Shutting down agent")

		for thread in self.corethreads:
			self.debugmsg(3, "Join Agent Thread:", thread)
			self.corethreads[thread].join()

		for jobid in self.jobs:
			# self.jobs[jobid]["Thread"]
			# base.debugmsg(3, "Join Agent Manager Thread")
			# base.Agentserver.join()

			self.debugmsg(3, "Join Agent Thread:", jobid)
			self.jobs[jobid]["Thread"].join()

		self.debugmsg(3, "Exit")
		try:
			sys.exit(0)
		except SystemExit:
			try:
				os._exit(0)
			except Exception:
				pass


class RFSwarm():
	def __init__(self):
		while rfsa.runagent:
			time.sleep(300)


rfsa = RFSwarmAgent()
try:
	rfsa.mainloop()
except KeyboardInterrupt:
	rfsa.on_closing()

except Exception as e:
	rfsa.debugmsg(1, "rfsa.Exception:", e)
