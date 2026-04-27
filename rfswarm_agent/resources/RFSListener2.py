
import os
import tempfile
import sys
import socket
from datetime import datetime
import time
import random
import requests
import inspect
import threading
from robot.libraries.BuiltIn import BuiltIn

class RFSListener2:
	ROBOT_LISTENER_API_VERSION = 2

	msg = None
	agentname = socket.gethostname()
	swarmmanager = "http://localhost:8138/"
	excludelibraries = ["BuiltIn","String","OperatingSystem","perftest"]
	resultnamemode = "dflt"
	excludesleep = "dis"
	debuglevel = 0
	index = 0
	robot = 0
	iter = 0
	seq = 0
	injectsleep = False
	injectsleepmsg = 'Sleep added by RFSwarm'
	sleepminimum = 15
	sleepmaximum = 45
	includetesttime = False

	activekeywords = {}

	def start_suite(self, name, attrs):
		if 'RFS_DEBUGLEVEL' in attrs['metadata']:
			self.debuglevel = int(attrs['metadata']['RFS_DEBUGLEVEL'])
			self.debugmsg(6, 'debuglevel: ', self.debuglevel)
		if 'RFS_INDEX' in attrs['metadata']:
			self.index = attrs['metadata']['RFS_INDEX']
			self.debugmsg(6, 'index: ', self.index)
		if 'RFS_ITERATION' in attrs['metadata']:
			self.iter = attrs['metadata']['RFS_ITERATION']
			self.debugmsg(6, 'iter: ', self.iter)
		if 'RFS_ROBOT' in attrs['metadata']:
			self.robot = attrs['metadata']['RFS_ROBOT']
			self.debugmsg(6, 'robot: ', self.robot)
		if 'RFS_AGENTNAME' in attrs['metadata']:
			self.agentname = attrs['metadata']['RFS_AGENTNAME']
			self.debugmsg(6, 'agentname: ', self.agentname)
		if 'RFS_SWARMMANAGER' in attrs['metadata']:
			self.swarmmanager = attrs['metadata']['RFS_SWARMMANAGER']
			self.debugmsg(6, 'swarmmanager: ', self.swarmmanager)
		if 'RFS_EXCLUDELIBRARIES' in attrs['metadata']:
			self.excludelibraries = attrs['metadata']['RFS_EXCLUDELIBRARIES'].split(",")
			self.debugmsg(6, 'excludelibraries: ', self.excludelibraries)
		if 'RFS_INCLUDETESTTIME' in attrs['metadata']:
			self.includetesttime = attrs['metadata']['RFS_INCLUDETESTTIME']
			self.debugmsg(6, 'includetesttime: ', self.includetesttime)
		if 'RFS_INJECTSLEEP' in attrs['metadata']:
			self.injectsleep = attrs['metadata']['RFS_INJECTSLEEP']
			self.debugmsg(6, 'injectsleep: ', self.injectsleep)
		if 'RFS_SLEEPMINIMUM' in attrs['metadata']:
			self.sleepminimum = attrs['metadata']['RFS_SLEEPMINIMUM']
			self.debugmsg(6, 'sleepminimum: ', self.sleepminimum)
		if 'RFS_SLEEPMAXIMUM' in attrs['metadata']:
			self.sleepmaximum = attrs['metadata']['RFS_SLEEPMAXIMUM']
			self.debugmsg(6, 'sleepmaximum: ', self.sleepmaximum)
		if 'RFS_RESULTNAMEMODE' in attrs['metadata']:
			self.resultnamemode = attrs['metadata']['RFS_RESULTNAMEMODE']
			self.debugmsg(6, 'resultnamemode: ', self.resultnamemode)
		# RFS_EXCLUDESLEEP
		if 'RFS_EXCLUDESLEEP' in attrs['metadata']:
			self.excludesleep = attrs['metadata']['RFS_EXCLUDESLEEP']
			self.debugmsg(6, 'excludesleep: ', self.excludesleep)
		self.seedseed()

	def seedseed(self):
		random.seed()
		r1 = random.random()%1000
		random.seed(r1)
		r2 = random.random()%10000
		random.seed(r2)

	def log_message(self, message):
		if message['message'][0:2] != '${':
			self.msg = None
			self.msg = message

	def start_test(self, name, attrs):
		# as this is the start of the test there should be no active keywords, reset to empty (just in case)
		self.activekeywords = {}
		if name not in self.activekeywords:
			self.activekeywords[name] = []
		self.activekeywords[name].append({"total": 0, "injected": 0})

	def start_keyword(self, name, attrs):
		if name not in self.activekeywords:
			self.activekeywords[name] = []
		self.activekeywords[name].append({"total": 0, "injected": 0})

	def end_test(self, name, attrs):
		self.debugmsg(5, 'includetesttime: ', self.includetesttime)
		if str(self.includetesttime).lower() in ('true', 't', 'yes', '1'):
			self.debugmsg(5, 'Test name: ', name)
			self.debugmsg(8, 'attrs: ', attrs)
			self.debugmsg(8, 'Test status: ', attrs['status'])
			self.debugmsg(8, 'Test elapsed_time: ', (attrs['elapsedtime']/1000))

			elapsed_time = (attrs['elapsedtime']/1000)
			# calculate time spent sleeping
			sleeps = self.calculate_sleeps(name, attrs)
			self.debugmsg(6, 'sleeps: ', sleeps)
			if self.excludesleep == "inj":
				self.debugmsg(6, 'elapsed_time: ', elapsed_time, "-", sleeps["injected"], "=", elapsed_time - sleeps["injected"])
				elapsed_time = elapsed_time - sleeps["injected"]
			if self.excludesleep == "all":
				self.debugmsg(6, 'elapsed_time: ', elapsed_time, "-", sleeps["total"], "=", elapsed_time - sleeps["total"])
				elapsed_time = elapsed_time - sleeps["total"]
			self.debugmsg(6, 'elapsed_time: ', elapsed_time)

			iter = BuiltIn().get_variable_value("${RFS_ITERATION}")
			tstname = name
			if tstname.endswith(iter):
				tstname = tstname[:(len(iter)*-1)].strip()
			self.debugmsg(5, 'tstname: ', tstname)
			startdate = datetime.strptime(attrs['starttime'], '%Y%m%d %H:%M:%S.%f')
			enddate = datetime.strptime(attrs['endtime'], '%Y%m%d %H:%M:%S.%f')
			payload = {
				'AgentName': self.agentname,
				'ResultName': tstname,
				'Result': attrs['status'],
				'ElapsedTime': elapsed_time,
				'StartTime': startdate.timestamp(),
				'EndTime': enddate.timestamp(),
				'ScriptIndex': self.index,
				'Robot': self.robot,
				'Iteration': iter,
				'Sequence': 0
			}
			self.debugmsg(7, 'payload: ', payload)
			t = threading.Thread(target=self.send_result, args=(payload,))
			t.start()

	def end_keyword(self, name, attrs):
		self.debugmsg(3, 'Keyword name: ', name)
		self.debugmsg(8, 'attrs: ', attrs)
		self.debugmsg(5, 'attrs[doc]: ', attrs['doc'])
		self.debugmsg(5, 'self.msg: ', self.msg)

		if attrs['kwname'] == "Sleep":
			if 'args' in attrs and len(attrs['args']) > 0:
				self.debugmsg(6, 'attrs[args]: ', attrs['args'], 'len:', len(attrs['args']))
				if len(attrs['args']) > 1:
					if attrs['args'][1] != self.injectsleepmsg:
						self.addsleeepto_activekeywords("total", attrs['args'][0])
				else:
					self.addsleeepto_activekeywords("total", attrs['args'][0])

		ResultName = ''
		istrace = False
		if self.msg is not None and 'level' in self.msg and self.msg['level'] == 'TRACE':
			istrace = True
		
		iter = BuiltIn().get_variable_value("${RFS_ITERATION}")
		if self.resultnamemode == 'dflt':
			if self.msg is not None and 'message' in self.msg and not istrace:
				ResultName = self.msg['message']
			elif 'doc' in attrs and len(attrs['doc'])>0:
				ResultName = attrs['doc']
		if self.resultnamemode == 'doco':
			if 'doc' in attrs and len(attrs['doc'])>0:
				ResultName = attrs['doc']
		if self.resultnamemode == 'info':
			if self.msg is not None and 'message' in self.msg:
				ResultName = self.msg['message']
		if self.resultnamemode == 'kywrd':
			self.debugmsg(8, self.resultnamemode, 'kwname: ', attrs['kwname'])
			ResultName = attrs['kwname']
		if self.resultnamemode == 'kywrdargs':
			self.debugmsg(8, self.resultnamemode, 'kwname: ', attrs['kwname'])
			lResultName = [attrs['kwname']]
			self.debugmsg(3, 'lResultName: ', lResultName)
			if 'args' in attrs:
				for arg in attrs['args']:
					lResultName.append(arg)
			self.debugmsg(8, 'lResultName: ', lResultName)
			ResultName = ' '.join(lResultName)
		self.debugmsg(3, 'ResultName: ', ResultName, '	:', len(ResultName))

		elapsed_time = (attrs['elapsedtime']/1000)
		# calculate time spent sleeping
		sleeps = self.calculate_sleeps(name, attrs)
		self.debugmsg(6, 'sleeps: ', sleeps)
		if self.excludesleep == "inj":
			self.debugmsg(6, 'elapsed_time: ', elapsed_time, "-", sleeps["injected"], "=", elapsed_time - sleeps["injected"])
			elapsed_time = elapsed_time - sleeps["injected"]
		if self.excludesleep == "all":
			self.debugmsg(6, 'elapsed_time: ', elapsed_time, "-", sleeps["total"], "=", elapsed_time - sleeps["total"])
			elapsed_time = elapsed_time - sleeps["total"]
		self.debugmsg(6, 'elapsed_time: ', elapsed_time)

		if len(ResultName)>0:
			self.debugmsg(8, 'self.msg: attrs[libname]: ', attrs['libname'], '	excludelibraries:', self.excludelibraries)
			if attrs['libname'] not in self.excludelibraries:
				self.debugmsg(5, attrs['libname'], 'library OK')
				self.seq += 1
				self.debugmsg(8, 'self.seq: ', self.seq)
				startdate = datetime.strptime(attrs['starttime'], '%Y%m%d %H:%M:%S.%f')
				enddate = datetime.strptime(attrs['endtime'], '%Y%m%d %H:%M:%S.%f')
				self.debugmsg(5, 'Send ResultName: ', ResultName)
				payload = {
					'AgentName': self.agentname,
					'ResultName': ResultName,
					'Result': attrs['status'],
					'ElapsedTime': elapsed_time,
					'StartTime': startdate.timestamp(),
					'EndTime': enddate.timestamp(),
					'ScriptIndex': self.index,
					'Robot': self.robot,
					'Iteration': iter,
					'Sequence': self.seq
				}
				self.debugmsg(7, 'payload: ', payload)
				t = threading.Thread(target=self.send_result, args=(payload,))
				t.start()

				self.debugmsg(7, 'injectsleep: ', self.injectsleep)
				if str(self.injectsleep).lower() in ('true', 't', 'yes', '1'):
					tmeslp = self.randsleep(self.sleepminimum, self.sleepmaximum)
					self.debugmsg(7, 'tmeslp: ', tmeslp)
					self.addsleeepto_activekeywords("injected", tmeslp)
					BuiltIn().run_keyword('Sleep', tmeslp, self.injectsleepmsg)

			else:
				self.debugmsg(5, attrs['libname'], 'is an excluded library')
		
		self.msg = None

	def addsleeepto_activekeywords(self, sleeptype, ammount):
		self.debugmsg(6, 'sleeptype: ', sleeptype, '	ammount:', ammount)
		self.debugmsg(8, 'self.activekeywords: ', self.activekeywords)
		try:
			numammount = float(ammount)
		except:
			numammount = 0.0

		for kw in self.activekeywords:
			self.debugmsg(8, 'kw: ', kw, self.activekeywords[kw])
			for idx, item in enumerate(self.activekeywords[kw]):
				self.debugmsg(8, 'idx:', idx, 'kw:', kw)
				self.debugmsg(8, self.activekeywords[kw][idx])
				self.activekeywords[kw][idx]["total"] += numammount
				if sleeptype == "injected":
					self.activekeywords[kw][idx]["injected"] += numammount
		self.debugmsg(8, 'self.activekeywords: ', self.activekeywords)

	def calculate_sleeps(self, name, attrs):
		sleepsforkw = {"total": 0, "injected": 0}
		self.debugmsg(6, 'name: ', name)
		if name in self.activekeywords:
			self.debugmsg(7, 'self.activekeywords[name]: ', self.activekeywords[name])
			sleepsforkw = self.activekeywords[name].pop()
			if len(self.activekeywords[name]) < 1:
				del self.activekeywords[name]
			self.debugmsg(8, 'self.activekeywords: ', self.activekeywords)
		return sleepsforkw

	def randsleep(self, min, max):
		isfloat = False
		if '.' in str(min) or '.' in str(max):
			isfloat = True
		if isfloat:
			return random.uniform(float(min), float(max))
		else:
			return random.randint(int(min), int(max))

	def debugmsg(self, lvl, *msg):
		msglst = []
		prefix = ""
		if self.debuglevel >= lvl:
			try:
				if self.debuglevel >= 4:
					stack = inspect.stack()
					the_class = stack[1][0].f_locals["self"].__class__.__name__
					the_method = stack[1][0].f_code.co_name
					prefix = "{}: {}: [{}:{}]	".format(str(the_class), the_method, self.debuglevel, lvl)
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

	def send_result(self, payload):
		exceptn = None
		retry = True
		count = 100
		uri = self.swarmmanager + 'Result'
		while retry and count>0:
			try:
				r = requests.post(uri, json=payload, timeout=600)
				self.debugmsg(7, 'send_result: ',r.status_code, r.text)
				if (r.status_code != requests.codes.ok):
					exceptn = r.status_code
				else:
					retry = False
			except Exception as e:
				exceptn = e
			time.sleep(1)
			count -= 1
		if retry:
			self.debugmsg(0, 'send_result: while attempting to send result to', uri)
			self.debugmsg(0, 'send_result: with payload:', payload)
			self.debugmsg(0, 'send_result: Exception:', exceptn)
