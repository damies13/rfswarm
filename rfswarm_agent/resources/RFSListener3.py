
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
from robot import result, running

class RFSListener3:
	ROBOT_LISTENER_API_VERSION = 3

	msg = None
	agentname = socket.gethostname()
	swarmmanager = "http://localhost:8138/"
	excludelibraries = ["BuiltIn","String","OperatingSystem","perftest"]
	resultnamemode = "dflt"
	debuglevel = 0
	index = 0
	robot = 0
	iter = 0
	seq = 0
	injectsleep = False
	sleepminimum = 15
	sleepmaximum = 45
	includetesttime = False

	def start_suite(self, suite: running.TestSuite, result: result.TestSuite):
		if 'RFS_DEBUGLEVEL' in result.metadata:
			self.debuglevel = int(result.metadata['RFS_DEBUGLEVEL'])
			self.debugmsg(6, 'debuglevel: ', self.debuglevel)
		if 'RFS_INDEX' in result.metadata:
			self.index = result.metadata['RFS_INDEX']
			self.debugmsg(6, 'index: ', self.index)
		if 'RFS_ITERATION' in result.metadata:
			self.iter = result.metadata['RFS_ITERATION']
			self.debugmsg(6, 'iter: ', self.iter)
		if 'RFS_ROBOT' in result.metadata:
			self.robot = result.metadata['RFS_ROBOT']
			self.debugmsg(6, 'robot: ', self.robot)
		if 'RFS_AGENTNAME' in result.metadata:
			self.agentname = result.metadata['RFS_AGENTNAME']
			self.debugmsg(6, 'agentname: ', self.agentname)
		if 'RFS_SWARMMANAGER' in result.metadata:
			self.swarmmanager = result.metadata['RFS_SWARMMANAGER']
			self.debugmsg(6, 'swarmmanager: ', self.swarmmanager)
		if 'RFS_EXCLUDELIBRARIES' in result.metadata:
			self.excludelibraries = result.metadata['RFS_EXCLUDELIBRARIES'].split(",")
			self.debugmsg(6, 'excludelibraries: ', self.excludelibraries)
		if 'RFS_INCLUDETESTTIME' in result.metadata:
			self.includetesttime = result.metadata['RFS_INCLUDETESTTIME']
			self.debugmsg(6, 'includetesttime: ', self.includetesttime)
		if 'RFS_INJECTSLEEP' in result.metadata:
			self.injectsleep = result.metadata['RFS_INJECTSLEEP']
			self.debugmsg(6, 'injectsleep: ', self.injectsleep)
		if 'RFS_SLEEPMINIMUM' in result.metadata:
			self.sleepminimum = result.metadata['RFS_SLEEPMINIMUM']
			self.debugmsg(6, 'sleepminimum: ', self.sleepminimum)
		if 'RFS_SLEEPMAXIMUM' in result.metadata:
			self.sleepmaximum = result.metadata['RFS_SLEEPMAXIMUM']
			self.debugmsg(6, 'sleepmaximum: ', self.sleepmaximum)
		if 'RFS_RESULTNAMEMODE' in result.metadata:
			self.resultnamemode = result.metadata['RFS_RESULTNAMEMODE']
			self.debugmsg(6, 'resultnamemode: ', self.resultnamemode)
		self.seedseed()

	def seedseed(self):
		random.seed()
		r1 = random.random()%1000
		random.seed(r1)
		r2 = random.random()%10000
		random.seed(r2)

	def log_message(self, message: result.Message):
		if message.message[0:2] != '${':
			self.msg = None
			self.msg = message

	def end_test(self, data: running.TestCase, result: result.TestCase):
		self.debugmsg(5, 'includetesttime: ', self.includetesttime)
		if str(self.includetesttime).lower() in ('true', 't', 'yes', '1'):
			self.debugmsg(8, 'data: ', data, data.to_dict())
			self.debugmsg(8, 'result: ', result, result.to_dict())
			self.debugmsg(5, 'Test name: ', result.name)
			self.debugmsg(8, 'Test status: ', result.status)
			self.debugmsg(8, 'Test elapsed_time: ', result.elapsed_time)
			iter = BuiltIn().get_variable_value("${RFS_ITERATION}")
			tstname = result.name
			if tstname.endswith(iter):
				tstname = tstname[:(len(iter)*-1)].strip()
			self.debugmsg(5, 'tstname: ', tstname)
			startdate = result.start_time
			enddate = datetime.fromtimestamp(startdate.timestamp() + result.elapsed_time.total_seconds())
			payload = {
				'AgentName': self.agentname,
				'ResultName': tstname,
				'Result': result.status,
				'ElapsedTime': result.elapsed_time.total_seconds(),
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

	def end_keyword(self, data: running.Keyword, result: result.Keyword):
		self.debugmsg(8, 'data: ', data, data.to_dict())
		self.debugmsg(8, 'result: ', result, result.to_dict())
		self.debugmsg(3, 'Keyword name: ', data.name)
		attrs = result.to_dict()
		self.debugmsg(6, 'attrs: ', attrs)
		self.debugmsg(5, 'self.msg: ', self.msg)
		
		ResultName = ''
		istrace = False
		if self.msg is not None and self.msg.level == 'TRACE':
			istrace = True
		
		iter = BuiltIn().get_variable_value("${RFS_ITERATION}")
		if self.resultnamemode == 'dflt':
			if self.msg is not None and not istrace:
				ResultName = self.msg.message
			elif 'doc' in attrs and len(attrs['doc'])>0:
				self.debugmsg(5, 'attrs[doc]: ', attrs['doc'])
				ResultName = attrs['doc']
		if self.resultnamemode == 'doco':
			if 'doc' in attrs and len(attrs['doc'])>0:
				self.debugmsg(5, 'attrs[doc]: ', attrs['doc'])
				ResultName = attrs['doc']
		if self.resultnamemode == 'info':
			if self.msg is not None:
				ResultName = self.msg.message
		if self.resultnamemode == 'kywrd':
			ResultName = data.name
		if self.resultnamemode == 'kywrdargs':
			lResultName = [data.name]
			if 'args' in attrs:
				for arg in attrs['args']:
					lResultName.append(str(arg))
			ResultName = ' '.join(lResultName)
		self.debugmsg(3, 'ResultName: ', ResultName, '	:', len(ResultName))
		
		if 'owner' not in attrs:
			attrs['owner'] = 'None'
		
		if len(ResultName)>0:
			self.debugmsg(8, 'self.msg: attrs[owner]: ', attrs['owner'], '	excludelibraries:', self.excludelibraries)
			if attrs['owner'] not in self.excludelibraries:
				self.debugmsg(5, attrs['owner'], 'library OK')
				self.seq += 1
				self.debugmsg(8, 'self.seq: ', self.seq)
				self.debugmsg(8, 'elapsed_time: ', attrs['elapsed_time'])
				self.debugmsg(8, 'start_time: ', attrs['start_time'])
				startdate = datetime.strptime(attrs['start_time'], '%Y-%m-%dT%H:%M:%S.%f')
				enddate = datetime.fromtimestamp(startdate.timestamp() + attrs['elapsed_time'])
				self.debugmsg(8, 'startdate: ', enddate, enddate.timestamp())
				self.debugmsg(5, 'Send ResultName: ', ResultName)
				payload = {
					'AgentName': self.agentname,
					'ResultName': ResultName,
					'Result': attrs['status'],
					'ElapsedTime': attrs['elapsed_time'],
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
					self.debugmsg(8, 'data.to_dict(): ', data.to_dict())
					if 'lineno' in data.to_dict() and 'body' in data.parent.to_dict() and data.to_dict() in data.parent.to_dict()['body']:
						tmeslp = self.randsleep(self.sleepminimum, self.sleepmaximum)
						self.debugmsg(7, 'tmeslp: ', tmeslp)
						self.debugmsg(7, 'data.parent.to_dict(): ', data.parent.to_dict())
						index = data.parent.to_dict()['body'].index(data.to_dict())
						self.debugmsg(7, 'index: ', index)
						data.parent.body.insert(index + 1, running.Keyword('Sleep', [tmeslp, 'Sleep added by RFSwarm']))

			else:
				self.debugmsg(5, attrs['owner'], 'is an excluded library')
		
		self.msg = None

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
