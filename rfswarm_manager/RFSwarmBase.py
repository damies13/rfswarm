
import base64
import configparser
import csv
import errno
import glob
import hashlib
import inspect
import lzma
import math
import os
import platform
import random
import re
import sqlite3
import sys
import tempfile
import threading
import time
from datetime import datetime, timedelta
from operator import itemgetter
from typing import Any

import psutil

if True:  # noqa: E402
	sys.path.append(os.path.abspath(os.path.dirname(__file__)))
	from percentile import percentile
	from stdevclass import stdevclass


class RFSwarmBase:
	version = "1.6.0"
	debuglvl = 0

	config = None
	manager_ini = None

	save_ini = True

	# https://github.com/damies13/rfswarm/blob/master/Doc/rfswarm_manager.md#exclude-libraries
	# default (BuiltIn,String,OperatingSystem,perftest)
	excludelibrariesdefault = "BuiltIn,String,OperatingSystem,perftest"
	testrepeaterdefault = False
	injectsleepenableddefault = False
	injectsleepminimumdefault = 15
	injectsleepmaximumdefault = 45
	disableloglogdefault = False
	disablelogreportdefault = False
	disablelogoutputdefault = False

	scriptcount = 0
	scriptlist: Any = [{}]
	scriptfiles: Any = {}
	scriptgrpend: Any = {}
	scriptdefaults: Any = {}

	mtimebefore = 0
	mtimeafter = 0
	mscriptcount = 0
	mscriptlist: Any = [{}]
	mscriptfiles: Any = {}
	mscriptgrpend: Any = {}
	mscriptdefaults: Any = {}

	uploadmodes = {'imm': "Immediately", 'err': "On Error Only", 'def': "All Deferred"}
	uploadmode = "err" 	# modes are imm, err, def
	uploadfiles: Any = {}

	resultnamemodes = {'dflt': "Default", 'doco': "Documentation", 'info': "Information", 'kywrd': "Keyword", "kywrdargs": "Keyword & Arguments"}
	resultnamemodedefault = "dflt" 	# modes are dflt, doco, kywrd, kywrdargs

	index = ""
	file = ""
	sheet = ""

	run_abort = False
	run_name = "PreRun"
	run_name_current = ""
	run_starttime = 0
	run_start = 0
	run_end = 0
	plan_end = 0
	mon_end = 0
	run_finish = 0
	run_paused = False
	run_threads: Any = {}
	total_robots = 0
	total_monitor = 0
	robot_schedule_template = {"RunName": "", "Agents": {}, "Scripts": {}, "Start": 0}
	robot_schedule = robot_schedule_template
	envvars: Any = {}
	agentserver = None
	agenthttpserver = None
	updatethread = None
	updateplanthread = None
	graph_refresher: dict[str, threading.Thread] = {}

	Agents: Any = {}
	agenttgridupdate = 0
	posttest = False

	dir_path = os.path.dirname(os.path.realpath(__file__))
	resultsdir = ""
	run_dbthread = True
	dbconnecttime = 0
	dbthread = None
	datapath = ""
	dbfile = ""
	datadb = None
	dbready = False
	dbqueue: Any = {"Write": [], "Read": [], "ReadResult": {}, "Results": [], "Metric": [], "Metrics": []}
	MetricIDs: Any = {}
	scriptfilters = [""]

	corecount = psutil.cpu_count()
	threadcount = corecount * 16

	# #000000 = Black
	# https://www.schemecolor.com/traffic-red-yellow-green.php
	defcolours = ['#000000', '#008450', '#B81D13', '#EFB700', '#888888']
	namecolours = ['total', 'pass', 'fail', 'warning', 'not run']

	darkmode = False

	appstarted = False
	keeprunning = True 		# this should only be changed by onclosing

	args = None

	core = None
	gui = None

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# base application
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def findiniloctaion(self):

		if self.args.ini:
			self.debugmsg(5, "self.args.ini: ", self.args.ini)
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
				except Exception:
					pass
		# This should cause saveini to fail?
		return None

	def debugmsg(self, lvl, *msg):
		msglst = []
		prefix = ""
		if self.debuglvl >= lvl:
			try:
				suffix = ""
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
					if len(prefix.strip()) < 32:
						prefix = "{}	".format(prefix)
					# <28 + 1 tab
					# if len(prefix.strip())<28:
					# 	prefix = "{}	".format(prefix)
					# <24 + 1 tab
					if len(prefix.strip()) < 24:
						prefix = "{}	".format(prefix)

					msglst.append(str(prefix))

					# suffix = "	[{} @{}]".format(self.version, str(datetime.now().replace(microsecond=0).isoformat(sep=' ')))
					suffix = "	[{} @{}]".format(self.version, str(datetime.now().isoformat(sep=' ', timespec='seconds')))
					# suffix = "	[{} @{}]".format(self.version, "HH:mm:SS")

				for itm in msg:
					msglst.append(str(itm))
				msglst.append(str(suffix))
				print(" ".join(msglst), flush=True)
			except Exception:
				pass

	def str2bool(self, instr):
		self.debugmsg(9, "instr:", instr)
		return str(instr).lower() in ("yes", "true", "t", "1")

	def dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def run_db_thread(self):
		while self.run_dbthread:
			if (self.datadb is None) or (self.run_name != self.run_name_current):
				self.debugmsg(9, "run_db_thread: ensure_db")
				self.ensure_db()

			if self.datadb is not None:

				# process db queues

				# Results
				if len(self.dbqueue["Results"]) > 0:
					self.debugmsg(9, "run_db_thread: dbqueue: Results")
					resdata = list(self.dbqueue["Results"])
					self.dbqueue["Results"] = []
					self.debugmsg(7, "dbqueue: Results: resdata:", resdata)
					try:
						sql = "INSERT INTO Results VALUES (?,?,?,?,?,?,?,?,?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, resdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						self.debugmsg(1, "run_db_thread: dbqueue: Results: Exception:", e)
						self.debugmsg(1, "run_db_thread: dbqueue: Results: ", sql, resdata)

				# Metric
				if len(self.dbqueue["Metric"]) > 0:
					self.debugmsg(9, "run_db_thread: dbqueue: Metric")
					resdata = list(self.dbqueue["Metric"])
					self.dbqueue["Metric"] = []
					self.debugmsg(9, "run_db_thread: dbqueue: Metric: resdata:", resdata)
					try:
						sql = "INSERT OR IGNORE INTO Metric VALUES (?,?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, resdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						self.debugmsg(1, "run_db_thread: dbqueue: Metric: Exception:", e)
						self.debugmsg(1, "run_db_thread: dbqueue: Metric: ", sql, resdata)

				# Metrics
				if len(self.dbqueue["Metrics"]) > 0:
					self.debugmsg(9, "run_db_thread: dbqueue: Metrics")
					resdata = list(self.dbqueue["Metrics"])
					self.dbqueue["Metrics"] = []
					self.debugmsg(9, "run_db_thread: dbqueue: Metrics: resdata:", resdata)
					try:
						sql = "INSERT INTO Metrics VALUES (?,?,?,?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, resdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						self.debugmsg(1, "run_db_thread: dbqueue: Metrics: Exception:", e)
						self.debugmsg(1, "run_db_thread: dbqueue: Metrics: ", sql, resdata)

				# General Write
				if len(self.dbqueue["Write"]) > 0:
					self.debugmsg(9, "run_db_thread: dbqueue: Write")
					tmpq = list(self.dbqueue["Write"])
					self.dbqueue["Write"] = []
					self.debugmsg(9, "run_db_thread: dbqueue: Write: tmpq:", tmpq)
					for item in tmpq:
						if item["SQL"] and item["VALUES"]:
							try:
								self.debugmsg(9, "run_db_thread: dbqueue: Write: SQL:", item["SQL"], " 	VALUES:", item["VALUES"])
								cur = self.datadb.cursor()
								cur.execute(item["SQL"], item["VALUES"])
								cur.close()
								self.datadb.commit()
							except Exception as e:
								self.debugmsg(1, "run_db_thread: dbqueue: Write: Exception:", e)
								self.debugmsg(1, "run_db_thread: dbqueue: Write: Item:", item)
						else:
							self.debugmsg(1, "run_db_thread: dbqueue: Write: Item not written, missing key SQL or VALUES")
							self.debugmsg(1, "run_db_thread: dbqueue: Write: Item:", item)

				# General Read
				if len(self.dbqueue["Read"]) > 0:
					self.debugmsg(7, "run_db_thread: dbqueue: Read")
					tmpq = list(self.dbqueue["Read"])
					self.dbqueue["Read"] = []
					self.debugmsg(7, "run_db_thread: dbqueue: Read: tmpq:", tmpq)
					for item in tmpq:
						if "SQL" in item:
							try:
								self.debugmsg(7, "run_db_thread: dbqueue: Read: SQL:", item["SQL"])
								self.datadb.row_factory = self.dict_factory
								cur = self.datadb.cursor()
								cur.execute(item["SQL"])
								result = cur.fetchall()
								self.debugmsg(7, "run_db_thread: dbqueue: Read: result:", result)
								cur.close()
								self.datadb.commit()

								self.debugmsg(7, "run_db_thread: dbqueue: Read: result:", result)
								if "KEY" in item:
									self.dbqueue["ReadResult"][item["KEY"]] = result

							except Exception as e:
								self.debugmsg(1, "run_db_thread: dbqueue: Read: Exception:", e)
								self.debugmsg(1, "run_db_thread: dbqueue: Read: Item:", item)
						else:
							self.debugmsg(1, "run_db_thread: dbqueue: Read: Item not written, missing key SQL or VALUES")
							self.debugmsg(1, "run_db_thread: dbqueue: Read: Item:", item)

			time.sleep(0.1)
			# end of while self.run_dbthread

		if self.datadb is not None:
			self.datadb.close()
			self.datadb = None

	def ensure_db(self):
		createschema = False
		self.debugmsg(9, "run_name:", self.run_name)
		if len(self.run_name) > 0:
			if self.run_name != self.run_name_current:
				self.run_name_current = self.run_name
				createschema = True
				self.dbready = False
				self.MetricIDs = {}

			if createschema and self.datadb is not None:
				self.debugmsg(5, "Disconnect and close DB")
				self.datadb.commit()
				self.datadb.close()
				self.datadb = None
				self.MetricIDs = {}

			# check if dir exists
			self.debugmsg(5, "dir_path:", self.dir_path)
			# self.resultsdir = os.path.join(self.dir_path, "results")
			if 'ResultsDir' not in self.config['Run']:
				self.config['Run']['ResultsDir'] = self.inisafevalue(os.path.join(self.dir_path, "results"))
				self.saveini()
			self.resultsdir = self.config['Run']['ResultsDir']

			if not os.path.exists(self.resultsdir):
				try:
					os.mkdir(self.resultsdir)
				except Exception as e:
					if not os.path.exists(self.resultsdir):
						self.debugmsg(0, "Unable to create resultsdir:", self.resultsdir, "\n", str(e))
						self.core.on_closing()

			self.datapath = os.path.join(self.resultsdir, self.run_name)
			self.debugmsg(3, "datapath:", self.datapath)
			if not os.path.exists(self.datapath):
				try:
					os.mkdir(self.datapath)
				except Exception as e:
					if not os.path.exists(self.datapath):
						self.debugmsg(0, "Unable to create datapath:", self.datapath, "\n", str(e))
						self.core.on_closing()

			# check if db exists
			self.dbfile = os.path.join(self.datapath, "{}.db".format(self.run_name))
			self.debugmsg(5, "dbfile:", self.dbfile)
			if not os.path.exists(self.dbfile):
				createschema = True
				self.dbready = False
			else:
				createschema = False

			if self.datadb is None:
				self.debugmsg(5, "Connect to DB")
				self.datadb = sqlite3.connect(self.dbfile)
				self.dbconnecttime = int(time.time())
				self.datadb.create_aggregate("percentile", 2, percentile)
				self.datadb.create_aggregate("stdev", 1, stdevclass)
				self.MetricIDs = {}

				compopt = self.datadb.execute("PRAGMA compile_options;")
				self.db_compile_options = [x[0] for x in compopt.fetchall()]

				if "ENABLE_MATH_FUNCTIONS" not in self.db_compile_options:
					self.datadb.create_function('floor', 1, math.floor)
					# https://www.sqlite.org/lang_mathfunc.html
					# https://stackoverflow.com/questions/70451170/sqlite3-math-functions-python

			if createschema:
				self.debugmsg(5, "Create Schema")
				c = self.datadb.cursor()
				# create tables

				c.execute('''CREATE TABLE Results
					(script_index int, robot int, iteration text, agent text, sequence int, result_name text, result text, elapsed_time num, start_time num, end_time num)''')

				c.execute('''CREATE TABLE Metric
					(ID INTEGER, Name TEXT NOT NULL, Type TEXT NOT NULL, PRIMARY KEY("ID"))''')

				c.execute('''CREATE TABLE Metrics
					(ParentID INTEGER NOT NULL, Time INTEGER NOT NULL, Key TEXT NOT NULL, Value TEXT, DataSource INTEGER NOT NULL)''')

				# create indexes?
				c.execute('''
				CREATE INDEX "idx_metric_name" ON "Metric" ("Name"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metric_type" ON "Metric" ("Type"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metric_name_type" ON "Metric" ("Name"	ASC, "Type"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metrics_parentid_key" ON "Metrics" ( "ParentID"	ASC, "Key"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metrics_parentid_time_key" ON "Metrics" ( "ParentID"	ASC, "Time"	ASC, "Key"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metrics_datasource_key" ON "Metrics" ( "DataSource"	ASC, "Key"	ASC)
				''')

				c.execute('''
				CREATE INDEX "idx_metrics_datasource" ON "Metrics" ( "DataSource"	ASC)
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
						, (Select ra.Value from Metrics ra where ra.ParentID = a.ID and ra.Key = "AssignedRobots"  and ra.Time = s.Time) "AgentAssigned"
						, (Select r.Value from Metrics r where r.ParentID = a.ID and r.Key = "Robots"  and r.Time = s.Time) "AgentRobots"
						, (Select max(l.Value) from Metrics l where l.ParentID = a.ID and l.Key = "Load"  and l.Time = s.Time) "AgentLoad"
						, (Select max(c.Value) from Metrics c where c.ParentID = a.ID and c.Key = "CPU"  and c.Time = s.Time) "AgentCPU"
						, (Select max(m.Value) from Metrics m where m.ParentID = a.ID and m.Key = "MEM"  and m.Time = s.Time) "AgentMEM"
						, (Select max(n.Value) from Metrics n where n.ParentID = a.ID and n.Key = "NET"  and n.Time = s.Time) "AgentNET"
				from Metric a
					left join Metrics s on s.ParentID = a.ID and s.Key = "Status"
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
						, (Select ra.Value from Metrics ra where ra.ParentID = a.ID and ra.Key = "AssignedRobots"  and ra.Time = s.Time) "AgentAssigned"
						, (Select r.Value from Metrics r where r.ParentID = a.ID and r.Key = "Robots"  and r.Time = s.Time) "AgentRobots"
						, (Select max(l.Value) from Metrics l where l.ParentID = a.ID and l.Key = "Load"  and l.Time = s.Time) "AgentLoad"
						, (Select max(c.Value) from Metrics c where c.ParentID = a.ID and c.Key = "CPU"  and c.Time = s.Time) "AgentCPU"
						, (Select max(m.Value) from Metrics m where m.ParentID = a.ID and m.Key = "MEM"  and m.Time = s.Time) "AgentMEM"
						, (Select max(n.Value) from Metrics n where n.ParentID = a.ID and n.Key = "NET"  and n.Time = s.Time) "AgentNET"
				from Metric a
					left join Metrics s on s.ParentID = a.ID and s.Key = "Status"
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
					, (Select mn.Value from Metrics mn where mn.ParentID = a.ID and mn.Key like "min%" and e.Time = mn.Time ) "Min"
					, (Select av.Value from Metrics av where av.ParentID = a.ID and av.Key = "avg" and e.Time = av.Time ) "Average"
					, (Select sd.Value from Metrics sd where sd.ParentID = a.ID and sd.Key like "stDev%" and e.Time = sd.Time ) "StDev"
					, (Select pct.Key from Metrics pct where pct.ParentID = a.ID and pct.Key like "%ile" and e.Time = pct.Time ) "%ile_Key"
					, (Select pct.Value from Metrics pct where pct.ParentID = a.ID and pct.Key like "%ile" and e.Time = pct.Time ) "%ile_Value"
					, (Select mx.Value from Metrics mx where mx.ParentID = a.ID and mx.Key like "max%" and e.Time = mx.Time ) "Max"
					, (Select ps.Value from Metrics ps where ps.ParentID = a.ID and ps.Key like "_pass%" and e.Time = ps.Time ) "Pass"
					, (Select fl.Value from Metrics fl where fl.ParentID = a.ID and fl.Key like "_fail%" and e.Time = fl.Time ) "Fail"
					, (Select ot.Value from Metrics ot where ot.ParentID = a.ID and ot.Key like "_other%" and e.Time = ot.Time ) "Other"
				from Metric a
					left join Metrics e on e.ParentID = a.ID and e.Key = "EntryTime"
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
					, ds.Name "DataSource"
				FROM Metric as m
				JOIN Metrics ms on m.ID = ms.ParentID
				JOIN Metric ds on ms.DataSource = ds.ID
				''')

				self.datadb.commit()
				self.dbready = True

	def PrettyColName(self, colname):
		self.debugmsg(8, "PrettyColName: colname:", colname)
		newcolname = colname
		# if newcolname[:1] == '_':
		# 	newcolname = newcolname[1:]
		# newcolname = newcolname.replace("_", " ")

		cnlst = colname.split("_")
		ncnlst = []
		self.debugmsg(9, "PrettyColName: cnlst:", cnlst)
		for word in cnlst:
			self.debugmsg(9, "PrettyColName: word:", word)
			if len(word) > 0:
				ncnlst.append(word.capitalize())
		self.debugmsg(9, "PrettyColName: ncnlst:", ncnlst)
		newcolname = " ".join(ncnlst)

		self.debugmsg(8, "PrettyColName: newcolname:", newcolname)

		return newcolname

	def named_colour(self, name):
		if name.lower() not in self.namecolours:
			self.namecolours.append(name.lower())
		return self.line_colour(self.namecolours.index(name.lower()))

	def line_colour(self, grp):
		if grp < len(self.defcolours):
			return self.defcolours[grp]
		else:
			newcolour = self.get_colour()
			self.debugmsg(9, "Initial newcolour:", newcolour)
			while newcolour in self.defcolours:
				self.debugmsg(9, self.defcolours)
				newcolour = self.get_colour()
				self.debugmsg(9, "newcolour:", newcolour)
			self.defcolours.append(newcolour)
			return newcolour

	def get_colour(self):
		newcolour = self.make_colour()
		if self.darkmode:
			while self.dl_score(newcolour) < -300:
				newcolour = self.make_colour()
			return newcolour
		else:
			while self.dl_score(newcolour) > 300:
				newcolour = self.make_colour()
			return newcolour

	def make_colour(self):
		hexchr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
		r1 = hexchr[random.randrange(len(hexchr))]
		r2 = hexchr[random.randrange(len(hexchr))]
		g1 = hexchr[random.randrange(len(hexchr))]
		g2 = hexchr[random.randrange(len(hexchr))]
		b1 = hexchr[random.randrange(len(hexchr))]
		b2 = hexchr[random.randrange(len(hexchr))]
		return "#{}{}{}{}{}{}".format(r1, r2, g1, g2, b1, b2)

	def dl_score(self, colour):
		# darkness / lightness score
		self.debugmsg(8, "colour:", colour)
		m = re.search(r'\#(.?.?)(.?.?)(.?.?)', colour)
		self.debugmsg(9, "m:", m)
		self.debugmsg(9, "m 1:", m[1], int(m[1], 16))
		self.debugmsg(9, "m 2:", m[2], int(m[2], 16))
		self.debugmsg(9, "m 3:", m[3], int(m[3], 16))
		r = int(m[1], 16) - 128
		g = int(m[2], 16) - 128
		b = int(m[3], 16) - 128

		self.debugmsg(8, "r:", r, " 	g:", g, " 	b:", b)
		score = r + g + b

		# if score>300:
		# 	self.debugmsg(7, "very light? score:", score)
		#
		# if score<-300:
		# 	self.debugmsg(7, "very dark? score:", score)

		return score

	def format_sec(self, sec_in):
		if sec_in > 3599:
			hrs = int(sec_in / 3600)
			mins = int(sec_in / 60) - (hrs * 60)
			# secs = sec_in - (((hrs*60) + mins) * 60)
			if mins > 0:
				return "{}:{}".format(hrs, mins)
			return "{}".format(hrs)
		if sec_in > 59:
			mins = int(sec_in / 60)
			secs = sec_in - (mins * 60)
			if secs > 0:
				return "{}:{}".format(mins, secs)
			return "{}".format(mins)
		return "{}".format(sec_in)

	def format_sec_remain(self, sec_in):
		if sec_in > 3599:
			hrs = int(sec_in / 3600)
			mins = int(sec_in / 60) - (hrs * 60)
			secs = sec_in - (((hrs * 60) + mins) * 60)
			return "{}:{:02}:{:02}".format(hrs, mins, secs)
		if sec_in > 59:
			mins = int(sec_in / 60)
			secs = sec_in - (mins * 60)
			return "{}:{:02}".format(mins, secs)
		return "0:{:02}".format(sec_in)

	def parse_time(self, stime_in):
		self.debugmsg(9, "stime_in:", stime_in)
		tarr = stime_in.split(":")
		self.debugmsg(9, "tarr:", tarr)
		n = datetime.now()
		st = datetime(n.year, n.month, n.day, int(tarr[0]))
		if len(tarr) == 2:
			st = datetime(n.year, n.month, n.day, int(tarr[0]), int(tarr[1]))
		if len(tarr) == 3:
			st = datetime(n.year, n.month, n.day, int(tarr[0]), int(tarr[1]), int(tarr[2]))

		if int(st.timestamp()) < int(n.timestamp()):
			st = datetime(n.year, n.month, n.day, int(tarr[0])) + timedelta(days=1)
			if len(tarr) == 2:
				st = datetime(n.year, n.month, n.day, int(tarr[0]), int(tarr[1])) + timedelta(days=1)
			if len(tarr) == 3:
				st = datetime(n.year, n.month, n.day, int(tarr[0]), int(tarr[1]), int(tarr[2])) + timedelta(days=1)

		self.debugmsg(8, "st:", st, "	", int(st.timestamp()))
		return int(st.timestamp())

	def hash_file(self, file, argrelpath=""):
		if not (os.path.exists(file) and os.path.isfile(file)):
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
		BLOCKSIZE = 65536

		# if len(argrelpath) > 0:
		self.debugmsg(7, "file:", file, "	ScriptDir:", self.config['Plan']['ScriptDir'])
		relpath = self.get_relative_path(self.config['Plan']['ScriptDir'], file)
		self.debugmsg(7, "file:", file, "	relpath:", relpath)

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
		#     script_hash = self.hash_file(file_data['localpath'], file_data['relpath'])
		#   File "./rfswarm.py", line 901, in hash_file
		#     with open(file, 'rb') as afile:
		# OSError: [Errno 24] Too many open files: '/Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot'

		afile = open(file, 'rb')
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
		afile.close()
		self.debugmsg(3, "file:", file, "	hash:", hasher.hexdigest())
		return hasher.hexdigest()

	def remove_hash(self, hash):
		remove = True
		# self.scriptlist[r]["ScriptHash"]
		self.debugmsg(8, "scriptlist:", self.scriptlist)
		for scr in range(len(self.scriptlist)):
			if "ScriptHash" in self.scriptlist[scr] and self.scriptlist[scr]["ScriptHash"] == hash:
				remove = False

		if remove:
			del self.scriptfiles[hash]

	def register_envvar(self, envvar):
		vartype = "value"
		self.debugmsg(5, "envvar:", envvar)
		self.debugmsg(9, "os.environ:", os.environ)
		self.debugmsg(7, "os.environ.keys():", list(os.environ.keys()))
		if envvar in list(os.environ.keys()):
			envvalue = os.environ[envvar]
			self.debugmsg(7, "envvar:", envvar, "	envvalue:", envvalue)
			if os.path.exists(envvalue):
				vartype = "path"
				envvalue = self.get_relative_path(self.config['Plan']['ScriptDir'], envvalue)
			self.debugmsg(5, "envvar:", envvar, "	vartype:", vartype, "	envvalue:", envvalue)
			self.envvars[envvar] = {}
			self.envvars[envvar]['vartype'] = vartype
			self.envvars[envvar]['value'] = envvalue
			self.debugmsg(9, "self.envvars:", self.envvars)
		else:
			envvalue = "<not found>"
		self.debugmsg(5, "envvar:", envvar, "	vartype:", vartype, "	envvalue:", envvalue)

	def replace_rf_path_variables(self, pathin, localdir):
		self.debugmsg(6, "pathin:", pathin)
		self.debugmsg(8, "localdir:", localdir)
		pathout = pathin
		self.debugmsg(8, "pathout:", pathout)

		# Issue #165 - Environment Variable Substitution
		envvars = re.findall("%{([^}]+)}", pathout)
		for envvar in envvars:
			self.debugmsg(5, "envvar:", envvar)
			self.debugmsg(9, "os.environ:", os.environ)
			self.debugmsg(7, "os.environ.keys():", list(os.environ.keys()))
			if envvar in list(os.environ.keys()):
				# Get local value
				envvalue = os.environ[envvar]
				self.debugmsg(7, "envvar:", envvar, "	envvalue:", envvalue)
				searchstr = "%{" + envvar + "}"
				self.debugmsg(9, "searchstr:", searchstr)
				pathout = pathout.replace(searchstr, envvalue)
				self.debugmsg(5, "pathout:", pathout)

		# Issue #129 Handle `${CURDIR}/`
		if pathout.find("${CURDIR}") > -1:
			pathmod = pathout.replace("${CURDIR}", "")
			self.debugmsg(8, "pathmod:", pathmod)
			# https://stackoverflow.com/questions/1945920/why-doesnt-os-path-join-work-in-this-case
			if platform.system() == "Windows":
				pathmod = pathmod.replace("/", os.path.sep)
				self.debugmsg(8, "pathmod:", pathmod)
				pathout = os.path.abspath(os.path.join(localdir, *pathmod.split(os.path.sep)))
				pathout = pathout.replace(r'${\}', r'${/}')
			else:
				pathout = os.path.abspath(os.path.join(os.path.sep, *localdir.split(os.path.sep), *pathmod.split(os.path.sep)))
			self.debugmsg(8, "pathout:", pathout)

		# Built-in variables - https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#built-in-variables

		# ${TEMPDIR}
		if pathout.find("${TEMPDIR}") > -1:
			tmpdir = tempfile.gettempdir()
			pathout = pathout.replace("${TEMPDIR}", tmpdir)
			self.debugmsg(8, "pathout:", pathout)

		# ${EXECDIR}
		# not sure how to handle this for now

		# ${/}
		self.debugmsg(8, "pathout.find:", pathout.find("${/}"))
		if pathout.find("${/}") > -1:
			self.debugmsg(8, "Found ${/} in", pathout)
			if pathout.find("${/}") == 0:
				pathlst = ["${rfpv}"] + pathout.split("${/}")
				self.debugmsg(8, "pathlst:", pathlst)
				pathjoin = os.path.join(*pathlst)
				self.debugmsg(8, "pathjoin:", pathjoin)
				pathjoin = pathjoin.replace("${rfpv}", "")
				self.debugmsg(8, "pathjoin:", pathjoin)
			else:
				pathlst = pathout.split("${/}")
				self.debugmsg(8, "pathlst:", pathlst)
				pathjoin = os.path.join(*pathlst)
				self.debugmsg(8, "pathjoin:", pathjoin)

			filelst = glob.glob(pathjoin)
			if os.path.isfile(pathjoin) or len(filelst) > 1:
				self.debugmsg(8, "pathjoin:", pathjoin)
				pathout = pathjoin
				self.debugmsg(8, "pathout:", pathout)
			else:
				self.debugmsg(8, "pathjoin:", pathjoin)
				pathout = self.localrespath(localdir, pathjoin)
				self.debugmsg(8, "pathout:", pathout)

		# ${:}
		# ${\n}
		# not sure whether to handle these for now
		self.debugmsg(6, "pathout:", pathout)

		return pathout

	def localrespath(self, localdir, resfile):
		self.debugmsg(5, "localdir:", localdir)
		self.debugmsg(5, "resfile:", resfile)
		llocaldir = re.findall(r"[^\/\\]+", localdir)
		lresfile = re.findall(r"[^\/\\]+", resfile)

		self.debugmsg(5, "llocaldir:", llocaldir)
		self.debugmsg(5, "lresfile:", lresfile)

		# i guess this could be affected too https://stackoverflow.com/questions/1945920/why-doesnt-os-path-join-work-in-this-case
		if platform.system() == "Windows":
			# joindpath = os.path.join(*llocaldir, *lresfile) # this doesn't work on windows, at least not on python 3.6+ (https://docs.python.org/3/library/os.path.html#os.path.join)
			lrespath = llocaldir + lresfile
			joindpath = os.path.sep.join(lrespath)
			self.debugmsg(8, "joindpath:", joindpath)
		else:
			joindpath = os.path.join(os.path.sep, *llocaldir, *lresfile)
			self.debugmsg(8, "joindpath:", joindpath)

		self.debugmsg(5, "joindpath:", joindpath)
		pathout = os.path.abspath(joindpath)
		self.debugmsg(5, "pathout:", pathout)

		return pathout

	def find_dependancies(self, hash):
		keep_going = True
		checking = False

		# determine if is a robot file
		self.debugmsg(8, "scriptfiles[", hash, "]", self.scriptfiles[hash])
		localpath = self.scriptfiles[hash]['localpath']
		localdir = os.path.dirname(localpath)

		if 'basedir' in self.scriptfiles[hash]:
			basedir = self.scriptfiles[hash]['basedir']
		else:
			basedir = localdir

		filequeue = []

		# look for __init__. files - Issue #90
		initfiles = os.path.abspath(os.path.join(localdir, "__init__.*"))
		self.debugmsg(8, "initfiles", initfiles)
		filelst = glob.glob(initfiles)
		for file in filelst:
			self.debugmsg(7, "file:", file)
			filequeue.append(file)

		self.debugmsg(8, "localdir", localdir)
		filename, fileext = os.path.splitext(localpath)

		self.debugmsg(8, "filename, fileext:", filename, fileext)

		# splitext leaves the . on the extention, the list below needs to have the extentions
		# starting with a . - Issue #94
		if (fileext.lower() in ['.robot', '.resource'] and keep_going):
			filedata = []
			with open(localpath, 'r', encoding="utf8") as afile:
				filedata = afile.read().splitlines()
				# close the file before processing the data - attempt fix for Issue #261
			for line in filedata:
				if checking and '*** ' in line:
					checking = False

				if checking:
					self.debugmsg(9, "line", line)
					try:
						if line.strip()[:1] != "#":
							# Identify environment variables the agents need
							envvars = re.findall("%{([^}]+)}", line.strip())
							for envvar in envvars:
								self.register_envvar(envvar)

							linearr = [s for s in re.split(r"( \s+|\t+|\s+\|\s+)", line.strip()) if len(s.strip()) > 0]
							self.debugmsg(8, "linearr", linearr)
							resfile = None
							# if len(linearr) > 1 and linearr[0].upper() in ['RESOURCE', 'VARIABLES', 'LIBRARY']:
							if len(linearr) > 1 and self.is_resfile_prefix(linearr[0]):
								self.debugmsg(7, "linearr[1]", linearr[1], "	linearr:", linearr)
								resfile = linearr[1]
							if not resfile and len(linearr) > 2 and self.is_resfile_prefix(linearr[0] + "_" + linearr[1]):
								self.debugmsg(7, "linearr[2]", linearr[2], "	linearr:", linearr)
								resfile = linearr[2]

							if resfile:
								self.debugmsg(7, "resfile", resfile)
								# here we are assuming the resfile is a relative path! should we also consider files with full local paths?
								# Issue #129 Handle ``${CURDIR}/``
								if resfile.find("${") > -1 or resfile.find("%{") > -1:
									localrespath = self.replace_rf_path_variables(resfile, localdir)
								else:
									localrespath = self.localrespath(localdir, resfile)

								self.debugmsg(8, "localrespath", localrespath)
								localrespath = os.path.abspath(localrespath)
								self.debugmsg(8, "localrespath", localrespath)
								if os.path.isfile(localrespath):

									filequeue.append(localrespath)

								else:
									self.debugmsg(6, "localrespath", localrespath)
									if os.path.isdir(localrespath):
										localrespath = os.path.join(localrespath, "**")
									filelst = glob.glob(localrespath, recursive=True)
									self.debugmsg(6, "filelst", filelst)
									for file in filelst:
										self.debugmsg(6, "file", file)
										if os.path.isfile(file):
											filequeue.append(file)

					except Exception as e:
						self.debugmsg(6, "line", line)
						self.debugmsg(6, "Exception", e)
						self.debugmsg(6, "linearr", linearr)

				# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#test-data-sections
				match = re.search(r'\*+([^*\v]+)', line)
				if match is not None:
					self.debugmsg(6, "match.group(0)", match.group(0), "match.group(1)", match.group(1))
					if self.is_section_to_check(match.group(1)):
						checking = True

		if len(filequeue) > 0:
			for file in filequeue:
				self.debugmsg(7, "file:", file)
				relfile = self.get_relative_path(self.config['Plan']['ScriptDir'], file)
				self.debugmsg(7, "relfile:", relfile)
				newhash = self.hash_file(file, relfile)
				self.debugmsg(7, "newhash:", newhash)
				if newhash not in self.scriptfiles:
					self.scriptfiles[newhash] = {
						'id': newhash,
						'basedir': basedir,
						'localpath': file,
						'relpath': relfile,
						'type': "Initialization"
					}
					filename, fileext = os.path.splitext(file)
					# splitext leaves the . on the extention, the list below needs to have the extentions
					# starting with a . - Issue #94
					if fileext.lower() in ['.robot', '.resource']:
						t = threading.Thread(target=self.find_dependancies, args=(newhash, ))
						t.start()

						self.debugmsg(9, "threading active count:", threading.active_count())
						while threading.active_count() > self.threadcount:
							self.debugmsg(9, "threading active count:", threading.active_count())
							time.sleep(0.1)

	def is_resfile_prefix(self, prefixname):
		self.debugmsg(5, "prefixname:", prefixname)
		prefixs = {
			"en": ['RESOURCE', 'VARIABLES', 'LIBRARY', 'METADATA_FILE', 'IMPORT_LIBRARY'],
			# Bulgarian		bg
			"bg": ['РЕСУРС', 'ПРОМЕНЛИВА', 'БИБЛИОТЕКА', 'МЕТАДАННИ_FILE', 'МЕТАДАННИ_ФАЙЛ', 'ВНОС_БИБЛИОТЕКА'],
			# Bosnian		bs
			"bs": ['RESURSI', 'VARIJABLE', 'BIBLIOTEKA', 'METADATA_FILE', 'METADATA_FILE', 'UVOZ_BIBLIOTEKA'],
			# Czech		cs
			"cs": ['ZDROJ', 'PROMĚNNÁ', 'KNIHOVNA', 'METADATA_FILE', 'METADATA_SOUBOR', 'IMPORT_KNIHOVNA'],
			# German		de
			"de": ['RESSOURCE', 'VARIABLEN', 'BIBLIOTHEK', 'METADATEN_FILE', 'METADATEN_DATEI', 'IMPORTIEREN_BIBLIOTHEK'],
			# Spanish		es
			"es": ['RECURSOS', 'VARIABLE', 'BIBLIOTECA', 'METADATOS_FILE', 'METADATOS_ARCHIVO', 'IMPORTAR_BIBLIOTECA'],
			# Finnish		fi
			"fi": ['RESURSSI', 'MUUTTUJAT', 'KIRJASTO', 'METATIEDOT_FILE', 'METATIEDOT_TIEDOSTO', 'TUONTI_KIRJASTO'],
			# French		fr
			"fr": ['RESSOURCE', 'VARIABLE', 'BIBLIOTHÈQUE', 'MÉTA-DONNÉE_FILE', 'MÉTA-DONNÉE_DÉPOSER', 'IMPORTER_BIBLIOTHÈQUE'],
			# Hindi		hi
			"hi": ['संसाधन', 'चर', 'कोड़ प्रतिबिंब संग्रह', 'अधि-आंकड़ा_FILE', 'अधि-आंकड़ा_फ़ाइल', 'आयात करें_कोड़ प्रतिबिंब संग्रह'],
			# Italian		it
			"it": ['RISORSA', 'VARIABILE', 'LIBRERIA', 'METADATI_FILE', 'METADATI_FILE', 'IMPORTARE_LIBRERIA'],
			# Japanese		ja
			"ja": ['リソース', '変数', 'ライブラリ', 'メタデータ_FILE', 'メタデータ_ファイル', 'インポート_ライブラリ'],
			# Dutch		nl
			"nl": ['RESOURCE', 'VARIABELE', 'BIBLIOTHEEK', 'METADATA_FILE', 'METADATA_BESTAND', 'IMPORTEREN_BIBLIOTHEEK'],
			# Polish		pl
			"pl": ['ZASÓB', 'ZMIENNE', 'BIBLIOTEKA', 'METADANE_FILE', 'METADANE_PLIK', 'IMPORT_BIBLIOTEKA'],
			# Portuguese		pt
			"pt": ['RECURSO', 'VARIÁVEL', 'BIBLIOTECA', 'METADADOS_FILE', 'METADADOS_FICHEIRO', 'IMPORTAÇÃO_BIBLIOTECA'],
			# Brazilian Portuguese		pt_br
			"pt_br": ['RECURSO', 'VARIÁVEL', 'BIBLIOTECA', 'METADADOS_FILE', 'METADADOS_ARQUIVO', 'IMPORTAR_BIBLIOTECA'],
			# Romanian		ro
			"ro": ['RESURSA', 'VARIABILA', 'LIBRARIE', 'METADATE_FILE', 'METADATE_FIŞIER', 'IMPORT_LIBRARIE'],
			# Russian		ru
			"ru": ['РЕСУРС', 'ПЕРЕМЕННЫЕ', 'БИБЛИОТЕКА', 'МЕТАДАННЫЕ_FILE', 'МЕТАДАННЫЕ_ФАЙЛ', 'ИМПОРТ_БИБЛИОТЕКА'],
			# Swedish		sv
			"sv": ['RESURS', 'VARIABEL', 'BIBLIOTEK', 'METADATA_FILE', 'METADATA_FIL', 'IMPORTERA_BIBLIOTEK'],
			# Thai		th
			"th": ['ไฟล์ที่ใช้', 'ชุดตัวแปร', 'ชุดคำสั่งที่ใช้', 'รายละเอียดเพิ่มเติม_FILE', 'รายละเอียดเพิ่มเติม_ไฟล์', 'นำเข้า_ชุดคำสั่งที่ใช้'],
			# Turkish		tr
			"tr": ['KAYNAK', 'DEĞIŞKENLER', 'KÜTÜPHANE', 'ÜSTVERI_FILE', 'ÜSTVERI_DOSYA', 'İÇE AKTARMAK_KÜTÜPHANE'],
			# Ukrainian		uk
			"uk": ['РЕСУРС', 'ЗМІННА', 'БІБЛІОТЕКА', 'МЕТАДАНІ_FILE', 'МЕТАДАНІ_ФАЙЛ', 'ІМПОРТ_БІБЛІОТЕКА'],
			# Vietnamese		vi
			"vi": ['TÀI NGUYÊN', 'BIẾN SỐ', 'THƯ VIỆN', 'DỮ LIỆU THAM CHIẾU_FILE', 'DỮ LIỆU THAM CHIẾU_TÀI LIỆU', 'NHẬP KHẨU_THƯ VIỆN'],
			# Chinese Simplified		zh_cn
			"zh_cn": ['资源文件', '变量文件', '程序库', '元数据_FILE', '元数据_文件', '导入_程序库'],
			# Chinese Traditional		zh_tw
			"zh_tw": ['資源文件', '變量文件', '函式庫', '元數據_FILE', '元數據_文件', '進口_函式庫'],
			# For future languages
			# "en": ['RESOURCE', 'VARIABLES', 'LIBRARY', 'METADATA_FILE', 'METADATA_FILE', 'IMPORT_LIBRARY'],
		}
		for prefix in list(prefixs.keys()):
			if prefixname.strip().upper() in prefixs[prefix]:
				self.debugmsg(5, "is_resfile_prefix:", prefixname, "	Lang:", prefix)
				return True
		return False

	def is_section_to_check(self, sectionname):
		if self.is_settings_section(sectionname):
			return True
		if self.is_testcases_section(sectionname):
			return True
		if self.is_keywords_section(sectionname):
			return True
		return False

	def is_settings_section(self, sectionname):
		sections = {
			"en": ['SETTINGS', 'SETTING'],
			# Bulgarian		bg
			"bg": ['НАСТРОЙКИ'],
			# Bosnian		bs
			"bs": ['POSTAVKE'],
			# Czech		cs
			"cs": ['NASTAVENÍ'],
			# German		de
			"de": ['EINSTELLUNGEN'],
			# Spanish		es
			"es": ['CONFIGURACIONES'],
			# Finnish		fi
			"fi": ['ASETUKSET'],
			# French		fr
			"fr": ['PARAMÈTRES'],
			# Hindi		hi
			"hi": ['स्थापना'],
			# Italian		it
			"it": ['IMPOSTAZIONI'],
			# Japanese		ja
			"ja": ['設定'],
			# Dutch		nl
			"nl": ['INSTELLINGEN'],
			# Polish		pl
			"pl": ['USTAWIENIA'],
			# Portuguese		pt
			"pt": ['DEFINIÇÕES'],
			# Brazilian Portuguese		pt_br
			"pt_br": ['CONFIGURAÇÕES'],
			# Romanian		ro
			"ro": ['SETARI'],
			# Russian		ru
			"ru": ['НАСТРОЙКИ'],
			# Swedish		sv
			"sv": ['INSTÄLLNINGAR'],
			# Thai		th
			"th": ['การตั้งค่า'],
			# Turkish		tr
			"tr": ['AYARLAR'],
			# Ukrainian		uk
			"uk": ['НАЛАШТУВАННЯ'],
			# Vietnamese		vi
			"vi": ['CÀI ĐẶT'],
			# Chinese Simplified		zh_cn
			"zh_cn": ['设置'],
			# Chinese Traditional		zh_tw
			"zh_tw": ['設置'],
			# For future languages
			# "en": ['SETTINGS', 'TEST CASES', 'TASKS', 'KEYWORDS'],
		}
		for section in list(sections.keys()):
			if sectionname.strip().upper() in sections[section]:
				self.debugmsg(5, "is_settings:", sectionname, "	Lang:", section)
				return True
		return False

	def is_testcases_section(self, sectionname):
		sections = {
			"en": ['TEST CASES', 'TEST CASE', 'TASKS', 'TASK'],
			# Bulgarian		bg
			"bg": ['ТЕСТОВИ СЛУЧАИ', 'ЗАДАЧИ'],
			# Bosnian		bs
			"bs": ['TEST CASES', 'TASKOVI'],
			# Czech		cs
			"cs": ['TESTOVACÍ PŘÍPADY', 'ÚLOHY'],
			# German		de
			"de": ['TESTFÄLLE', 'AUFGABEN'],
			# Spanish		es
			"es": ['CASOS DE PRUEBA', 'TAREAS'],
			# Finnish		fi
			"fi": ['TESTIT', 'TEHTÄVÄT'],
			# French		fr
			"fr": ['UNITÉS DE TEST', 'TÂCHES'],
			# Hindi		hi
			"hi": ['नियत कार्य प्रवेशिका', 'कार्य प्रवेशिका'],
			# Italian		it
			"it": ['CASI DI TEST', 'ATTIVITÀ'],
			# Japanese		ja
			"ja": ['テスト ケース', 'タスク'],
			# Dutch		nl
			"nl": ['TESTGEVALLEN', 'TAKEN'],
			# Polish		pl
			"pl": ['PRZYPADKI TESTOWE', 'ZADANIA'],
			# Portuguese		pt
			"pt": ['CASOS DE TESTE', 'TAREFAS'],
			# Brazilian Portuguese		pt_br
			"pt_br": ['CASOS DE TESTE', 'TAREFAS'],
			# Romanian		ro
			"ro": ['CAZURI DE TEST', 'SARCINI'],
			# Russian		ru
			"ru": ['ЗАГОЛОВКИ ТЕСТОВ', 'ЗАДАЧА'],
			# Swedish		sv
			"sv": ['TESTFALL', 'TASKAR'],
			# Thai		th
			"th": ['การทดสอบ', 'งาน'],
			# Turkish		tr
			"tr": ['TEST DURUMLARI', 'GÖREVLER'],
			# Ukrainian		uk
			"uk": ['ТЕСТ-КЕЙСИ', 'ЗАВДАНЬ'],
			# Vietnamese		vi
			"vi": ['CÁC KỊCH BẢN KIỂM THỬ', 'CÁC NGHIỆM VỤ'],
			# Chinese Simplified		zh_cn
			"zh_cn": ['用例', '任务'],
			# Chinese Traditional		zh_tw
			"zh_tw": ['案例', '任務'],
			# For future languages
			# "en": ['SETTINGS', 'TEST CASES', 'TASKS', 'KEYWORDS'],
		}
		for section in list(sections.keys()):
			if sectionname.strip().upper() in sections[section]:
				self.debugmsg(5, "is_testcases:", sectionname, "	Lang:", section)
				return True
		return False

	def is_keywords_section(self, sectionname):
		sections = {
			"en": ['KEYWORDS', 'KEYWORD'],
			# Bulgarian		bg
			"bg": ['КЛЮЧОВИ ДУМИ'],
			# Bosnian		bs
			"bs": ['KEYWORDS'],
			# Czech		cs
			"cs": ['KLÍČOVÁ SLOVA'],
			# German		de
			"de": ['SCHLÜSSELWÖRTER'],
			# Spanish		es
			"es": ['PALABRAS CLAVE'],
			# Finnish		fi
			"fi": ['AVAINSANAT'],
			# French		fr
			"fr": ['MOTS-CLÉS'],
			# Hindi		hi
			"hi": ['कुंजीशब्द'],
			# Italian		it
			"it": ['PAROLE CHIAVE'],
			# Japanese		ja
			"ja": ['キーワード'],
			# Dutch		nl
			"nl": ['SLEUTELWOORDEN'],
			# Polish		pl
			"pl": ['SŁOWA KLUCZOWE'],
			# Portuguese		pt
			"pt": ['PALAVRAS-CHAVE'],
			# Brazilian Portuguese		pt_br
			"pt_br": ['PALAVRAS-CHAVE'],
			# Romanian		ro
			"ro": ['CUVINTE CHEIE'],
			# Russian		ru
			"ru": ['КЛЮЧЕВЫЕ СЛОВА'],
			# Swedish		sv
			"sv": ['NYCKELORD'],
			# Thai		th
			"th": ['คำสั่งเพิ่มเติม'],
			# Turkish		tr
			"tr": ['ANAHTAR KELIMELER'],
			# Ukrainian		uk
			"uk": ['КЛЮЧОВИХ СЛОВА'],
			# Vietnamese		vi
			"vi": ['CÁC TỪ KHÓA'],
			# Chinese Simplified		zh_cn
			"zh_cn": ['关键字'],
			# Chinese Traditional		zh_tw
			"zh_tw": ['關鍵字'],
			# For future languages
			# "en": ['SETTINGS', 'TEST CASES', 'TASKS', 'KEYWORDS'],
		}
		for section in list(sections.keys()):
			if sectionname.strip().upper() in sections[section]:
				self.debugmsg(5, "is_keywords:", sectionname, "	Lang:", section)
				return True
		return False

	def check_files_changed(self):
		# self.scriptfiles[hash]
		checkhashes = list(self.scriptfiles.keys())
		self.debugmsg(6, "checkhashes:", checkhashes)
		for chkhash in checkhashes:
			file_data = self.scriptfiles[chkhash]
			script_hash = self.hash_file(file_data['localpath'], file_data['relpath'])
			if script_hash != chkhash:
				# file changed
				self.debugmsg(3, "File's hash has changed: chkhash:", chkhash, "	script_hash:", script_hash, "	localpath:", file_data['localpath'])

				# check if file is in script list and update it's hash
				# self.scriptlist[r]["ScriptHash"] = script_hash
				for iid in range(len(self.scriptlist)):
					self.debugmsg(3, "self.scriptlist[", iid, "]:", self.scriptlist[iid])
					if "ScriptHash" in self.scriptlist[iid] and chkhash == self.scriptlist[iid]["ScriptHash"]:
						self.scriptlist[iid]["ScriptHash"] = script_hash
						break

				if script_hash not in self.scriptfiles:
					file_data['id'] = script_hash
					self.scriptfiles[script_hash] = file_data

					t = threading.Thread(target=self.find_dependancies, args=(script_hash, ))
					t.start()

					self.remove_hash(chkhash)

	def get_relative_path(self, path1, path2):
		self.debugmsg(5, "path1:", path1)
		self.debugmsg(5, "path2:", path2)
		# commonpath = os.path.commonpath([path1, path2])

		self.debugmsg(8, "os.path.isdir(path1):", os.path.isdir(path1))
		self.debugmsg(8, "os.path.isfile(path1):", os.path.isfile(path1))
		# if not os.path.isdir(path1):
		if os.path.isfile(path1) or not os.path.exists(path1):
			path1 = os.path.dirname(path1)
			self.debugmsg(7, "path1:", path1)

		if platform.system() == "Windows":
			# os.path.splitroot is only available from python 3.12+ maybe we can use this
			# 	in the future when python 3.11 os EOL
			# if os.path.splitroot(path1)[0] != os.path.splitroot(path2)[0]:
			# os.path.splitdrive only works on windows, but supports Python 3.6+
			if os.path.splitdrive(path1)[0] != os.path.splitdrive(path2)[0]:
				path1 = os.path.dirname(path2)

		relpath = os.path.relpath(path2, start=path1)
		# https://www.geeksforgeeks.org/python-os-path-relpath-method/
		self.debugmsg(5, "relpath:", relpath)
		return relpath

	def save_upload_file(self, hash):
		self.debugmsg(7, "hash:", hash)
		# self.uploadfiles[jsonreq["Hash"]] = jsonreq
		self.debugmsg(7, "uploadfile:", self.uploadfiles[hash])

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
			self.debugmsg(3, "file:", localfile, "hash:", hash)

			# self.scriptlist[hash][]

			filedata = self.uploadfiles[hash]['FileData']

			self.debugmsg(8, "filedata:", filedata)
			self.debugmsg(6, "filedata:")

			decoded = base64.b64decode(filedata)
			self.debugmsg(8, "b64decode: decoded:", decoded)
			self.debugmsg(6, "b64decode:")

			uncompressed = lzma.decompress(decoded)
			self.debugmsg(8, "uncompressed:", uncompressed)
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
		if len(dir) < 1:
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

	def inisafevalue(self, value):
		self.debugmsg(6, "value:", value, type(value))
		if isinstance(value, dict):
			newval = {}
			for key in value.keys():
				newval[key] = self.inisafevalue(value[key])
			return newval
		elif isinstance(value, configparser.SectionProxy):
			newval = {}
			for key in value.keys():
				newval[key] = self.inisafevalue(value[key])
			return newval
		elif isinstance(value, str):
			return value.replace('%', '%%')
		else:
			return str(value)

	def inisafedir(self, path):
		# Ensured the path returned is a directory not a file
		self.debugmsg(5, "path in:", path)
		if os.path.isdir(path):
			return self.inisafevalue(path)
		if os.path.isfile(path):
			filedir = os.path.dirname(path)
			self.debugmsg(5, "path out:", filedir)
			return self.inisafevalue(filedir)
		# if path provided is not a file or directory return the default value
		self.debugmsg(5, "path out:", self.dir_path)
		return self.inisafevalue(self.dir_path)

	def saveini(self):
		self.debugmsg(6, "save_ini:", self.save_ini)
		if self.save_ini:
			with open(self.manager_ini, 'w', encoding="utf8") as configfile:    # save
				self.config.write(configfile)
				self.debugmsg(6, "File Saved:", self.manager_ini)

	def get_next_agent(self, filters):
		self.debugmsg(9, "get_next_agent")
		self.debugmsg(8, "get_next_agent: self.Agents:", self.Agents)
		if len(self.Agents) < 1:
			self.debugmsg(7, "Agents:", len(self.Agents))
			return None

		if self.args.agents:
			neededagents = int(self.args.agents)
			self.debugmsg(7, "Agents:", len(self.Agents), "	Agents Needed:", neededagents)
			if len(self.Agents) < neededagents:
				return None

		self.debugmsg(7, "filters:", filters)
		f_requre = []
		f_exclude = []
		for filt in filters:
			if filt['rule'] == 'Require':
				f_requre.append(filt['optn'])
			if filt['rule'] == 'Exclude':
				f_exclude.append(filt['optn'])

		loadtpl = []
		robottpl = []
		for agnt in self.Agents.keys():
			self.debugmsg(7, "agnt:", agnt)
			agntnamefilter = "Agent: {}".format(agnt)
			# check if this agent is specifically excluded
			self.debugmsg(7, "agntnamefilter:", agntnamefilter, "f_exclude:", f_exclude)
			if agntnamefilter not in f_exclude:
				# check if this agent is specifically required, if so no need for further evaluation
				if agntnamefilter in f_requre:
					self.debugmsg(7, "Agent Matched Require Filter:", agntnamefilter)
					return agnt

				# if we got this far, determine if agent meets requirements based on filter rules
				addagnt = False
				self.debugmsg(7, "addagnt:", addagnt)

				if len(filters) < 1:
					# there are no filters applied
					addagnt = True
					self.debugmsg(7, "no filters applied", "addagnt:", addagnt)

				# if agent has Properties, compare filters against these
				if "Properties" in self.Agents[agnt]:
					# if all requried filter items in properties
					requirematch = 0
					for fil in f_requre:
						if fil in self.Agents[agnt]["Properties"]:
							requirematch += 1
							self.debugmsg(7, "Matched Required Filter:", fil)
						else:
							# split filter removeing last item, then try compare again
							filarr = fil.rsplit(":", 1)
							if len(filarr) > 1:
								if filarr[0] in self.Agents[agnt]["Properties"]:
									if filarr[1].strip() == self.Agents[agnt]["Properties"][filarr[0]].strip():
										requirematch += 1
										self.debugmsg(7, "Matched Required Filter:", fil)

					if requirematch == len(f_requre):
						addagnt = True
						self.debugmsg(7, "requirematch:", requirematch, "required:", len(f_requre), "addagnt:", addagnt)

					# if any excluded filter items in properties
					for fil in f_exclude:
						if fil in self.Agents[agnt]["Properties"]:
							addagnt = False
							self.debugmsg(7, "Matched Excluded Filter:", fil, "addagnt:", addagnt)
						else:
							# split filter removeing last item, then try compare again
							filarr = fil.rsplit(":", 1)
							if len(filarr) > 1:
								if filarr[0] in self.Agents[agnt]["Properties"]:
									if filarr[1].strip() == self.Agents[agnt]["Properties"][filarr[0]].strip():
										addagnt = False
										self.debugmsg(7, "Matched Excluded Filter:", fil, "addagnt:", addagnt)

				self.debugmsg(7, "Final result: addagnt:", addagnt)
				if addagnt:
					loadtpl.append([agnt, self.Agents[agnt]['LOAD%']])
					robottpl.append([agnt, self.Agents[agnt]['AssignedRobots']])

			else:
				self.debugmsg(7, "Agent Matched Exclude Filter:", agntnamefilter)

		self.debugmsg(7, "robottpl:", robottpl)
		if len(robottpl) < 1:
			self.debugmsg(7, "robottpl empty, return None")
			return None

		# Start with agent with least robots
		robottpl.sort(key=itemgetter(1))
		self.debugmsg(9, "robottpl:", robottpl)
		if robottpl[0][1] < 10:
			return robottpl[0][0]
		else:
			# try for agent with least load
			self.debugmsg(7, "loadtpl:", loadtpl)
			if len(loadtpl) < 1:
				# this should never happen!!!
				return None
			loadtpl.sort(key=itemgetter(1))
			self.debugmsg(9, "loadtpl:", loadtpl)
			if loadtpl[0][1] < 95:
				return loadtpl[0][0]
			else:
				return None

	def addScriptRow(self, *args):
		self.scriptcount += 1

		row = int("{}".format(self.scriptcount))
		self.scriptlist.append({})

		self.scriptlist[self.scriptcount]["Index"] = self.scriptcount

		num = "10"
		self.scriptlist[self.scriptcount]["Robots"] = int(num)

		num = "0"
		self.scriptlist[self.scriptcount]["Delay"] = int(num)

		num = "1800"	 # 30 minutes
		self.scriptlist[self.scriptcount]["RampUp"] = int(num)

		# num = "18000"  # 18000 sec = 5 hours
		num = "7200"  # 3600 sec = 1hr, 7200 sec = 2 hours
		self.scriptlist[self.scriptcount]["Run"] = int(num)

		self.scriptlist[row]["Test"] = ""

		self.debugmsg(5, "self.scriptlist[", row, "]:", self.scriptlist[row])

		if not self.args.nogui and self.gui:
			self.gui.addScriptRow()

	def addMScriptRow(self, *args):
		self.mscriptcount += 1

		row = int("{}".format(self.mscriptcount))
		self.debugmsg(5, "row:", row)

		self.mscriptlist.append({})

		self.mscriptlist[row]["Index"] = f"m{self.mscriptcount}"

		num = "1"
		self.mscriptlist[row]["Robots"] = int(num)

		num = "0"
		self.mscriptlist[row]["Delay"] = int(num)

		num = "0"	 # 30 minutes
		self.mscriptlist[row]["RampUp"] = int(num)

		# num = "18000"  # 18000 sec = 5 hours
		num = "0"  # 3600 sec = 1hr, 7200 sec = 2 hours
		self.mscriptlist[row]["Run"] = int(num)

		self.mscriptlist[row]["Test"] = ""

		self.debugmsg(5, "self.mscriptlist[", row, "]:", self.mscriptlist[row])

		if not self.args.nogui and self.gui:
			self.gui.addMScriptRow(row)

	def UpdateRunStats_SQL(self):

		display_percentile = self.config['Run']['display_percentile']
		self.debugmsg(6, "display_percentile:", display_percentile)

		gblist = []
		display_index = self.str2bool(self.config['Run']['display_index'])
		self.debugmsg(6, "display_index:", display_index)
		if display_index:
			gblist.append("r.script_index")

		display_iteration = self.str2bool(self.config['Run']['display_iteration'])
		self.debugmsg(6, "display_iteration:", display_iteration)
		if display_iteration:
			gblist.append("r.iteration")

		display_sequence = self.str2bool(self.config['Run']['display_sequence'])
		self.debugmsg(6, "display_sequence:", display_sequence)
		if display_sequence:
			gblist.append("r.sequence")

		gblist.append("r.result_name")
		self.debugmsg(6, "gblist:", gblist)

		gbcols = ", ".join(gblist)

		self.debugmsg(6, "gbcols:", gbcols)

		sql = "SELECT "
		if len(gblist) > 0:
			sql += gbcols
			sql += ", "
		sql += "round(min(rp.elapsed_time),3) 'min', "
		sql += "round(avg(rp.elapsed_time),3) 'avg', "
		sql += "round(percentile(rp.elapsed_time, {}),3) '{}%ile', ".format(display_percentile, display_percentile)
		sql += "round(max(rp.elapsed_time),3) 'max', "
		sql += "round(stdev(rp.elapsed_time),3) 'stDev', "
		sql += "count(rp.result) as _pass, "
		sql += "count(rf.result) as _fail, "
		sql += "count(ro.result) as _other "
		sql += "FROM Results as r "
		sql += "LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == 'PASS' "
		sql += "LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == 'FAIL' "
		sql += "LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> 'PASS' AND ro.result <> 'FAIL' "
		sql += "WHERE r.start_time>{} ".format(self.robot_schedule["Start"])
		if len(gblist) > 0:
			sql += "GROUP BY  "
			sql += gbcols

		sql += " ORDER BY min(r.script_index), min(r.sequence)"

		self.debugmsg(6, "sql:", sql)

		self.dbqueue["Read"].append({"SQL": sql, "KEY": "RunStats"})

		t = threading.Thread(target=self.SaveRunStats_SQL)
		t.start()

	def UpdateAgents_SQL(self):

		# request agent data for agent report
		sql = "SELECT * "
		sql += "FROM AgentHistory as a "
		sql += "WHERE a.AgentLastSeen>{} ".format(self.robot_schedule["Start"])
		sql += " ORDER BY a.AgentLastSeen"

		self.debugmsg(6, "sql:", sql)

		self.dbqueue["Read"].append({"SQL": sql, "KEY": "Agents"})
		# request agent data for agent report

	def UpdateRawResults_SQL(self):
		# request raw data for agent report
		sql = "SELECT * "
		sql += "FROM Results as r "
		sql += "WHERE r.start_time>{} ".format(self.robot_schedule["Start"])
		sql += " ORDER BY r.start_time"

		self.debugmsg(6, "sql:", sql)

		self.dbqueue["Read"].append({"SQL": sql, "KEY": "RawResults"})
		# request raw data for agent report

	def SaveRunStats_SQL(self):

		self.debugmsg(7, "Wait for RunStats")
		while "RunStats" not in self.dbqueue["ReadResult"]:
			time.sleep(0.1)
			self.debugmsg(9, "Wait for RunStats")

		RunStats = self.dbqueue["ReadResult"]["RunStats"]
		self.debugmsg(7, "RunStats:", RunStats)

		m_Time = int(time.time())
		# Read Metric ID's
		for stat in RunStats:
			self.debugmsg(7, "stat:", stat)
			statname = stat["result_name"]

			self.save_metrics(statname, "Summary", m_Time, "EntryTime", m_Time, self.srvdisphost)

			for stati in stat:
				self.debugmsg(7, "stati:", stati, "	stat[stati]:", stat[stati])
				if stati != "result_name":
					self.save_metrics(statname, "Summary", m_Time, stati, stat[stati], self.srvdisphost)

	def report_text(self, _event=None):
		self.debugmsg(6, "report_text")
		colno = 0
		while_cnt = 0
		while_max = 100
		filecount = 0

		self.debugmsg(6, "RunStats")
		self.debugmsg(6, "UpdateRunStats_SQL")
		self.UpdateRunStats_SQL()
		self.UpdateAgents_SQL()
		self.UpdateRawResults_SQL()

		self.debugmsg(6, "RunStats self.args.nogui:", self.args.nogui, "	self.run_starttime:", self.run_starttime, "	self.run_start:", self.run_start, "	self.run_end:", self.run_end)
		if self.args.nogui or self.run_start > 0:
			if "RunStats" not in self.dbqueue["ReadResult"]:
				self.debugmsg(6, "Wait for RunStats")
				while_cnt = while_max
				while "RunStats" not in self.dbqueue["ReadResult"] and while_cnt > 0:
					time.sleep(0.1)
					while_cnt -= 1
				self.debugmsg(6, "Wait for RunStats>0")
				while_cnt = while_max
				while "RunStats" not in self.dbqueue["ReadResult"] \
					and len(self.dbqueue["ReadResult"]["RunStats"]) < 1 \
					and while_cnt > 0:
					time.sleep(0.1)
					while_cnt -= 1

		if "RunStats" in self.dbqueue["ReadResult"] and len(self.dbqueue["ReadResult"]["RunStats"]) > 0:
			self.debugmsg(7, "RunStats:", self.dbqueue["ReadResult"]["RunStats"])

			fileprefix = self.run_name
			self.debugmsg(8, "fileprefix:", fileprefix)
			if len(fileprefix) < 1:
				fileprefix = os.path.split(self.datapath)[-1]
				self.debugmsg(9, "fileprefix:", fileprefix)
			txtreport = os.path.join(self.datapath, "{}_summary.csv".format(fileprefix))
			self.debugmsg(7, "txtreport:", txtreport)
			self.debugmsg(1, "Summary File:", txtreport)
			self.debugmsg(6, "RunStats:", self.dbqueue["ReadResult"]["RunStats"])
			cols = []
			for col in self.dbqueue["ReadResult"]["RunStats"][0].keys():
				self.debugmsg(9, "colno:", colno, "col:", col)
				cols.append(self.PrettyColName(col))
			self.debugmsg(9, "cols:", cols)
			with open(txtreport, 'w', newline='', encoding="utf8") as csvfile:
				writer = csv.writer(csvfile, dialect='excel')
				writer.writerow(cols)
				for row in self.dbqueue["ReadResult"]["RunStats"]:
					rowdata = row.values()
					writer.writerow(rowdata)

			filecount += 1

		self.debugmsg(6, "Agents self.args.nogui:", self.args.nogui, "	self.run_starttime:", self.run_starttime, "	self.run_start:", self.run_start, "	self.run_end:", self.run_end)
		if self.args.nogui or self.run_start > 0:
			while_cnt = while_max
			self.debugmsg(6, "Wait for Agents")
			while "Agents" not in self.dbqueue["ReadResult"] and while_cnt > 0:
				time.sleep(0.1)
				while_cnt -= 1
			self.debugmsg(6, "Wait for Agents>0")
			while_cnt = while_max
			while "Agents" not in self.dbqueue["ReadResult"] \
				and while_cnt > 0:
				time.sleep(0.1)
				while_cnt -= 1
			while_cnt = while_max
			while len(self.dbqueue["ReadResult"]["Agents"]) < 1 \
				and while_cnt > 0:
				time.sleep(0.1)
				while_cnt -= 1

		if "Agents" in self.dbqueue["ReadResult"] and len(self.dbqueue["ReadResult"]["Agents"]) > 0:
			fileprefix = self.run_name
			self.debugmsg(9, "fileprefix:", fileprefix)
			if len(fileprefix) < 1:
				fileprefix = os.path.split(self.datapath)[-1]
				self.debugmsg(9, "fileprefix:", fileprefix)
			txtreport = os.path.join(self.datapath, "{}_agent_data.csv".format(fileprefix))
			self.debugmsg(6, "txtreport:", txtreport)
			self.debugmsg(1, "Agent Data:", txtreport)
			cols = []
			for col in self.dbqueue["ReadResult"]["Agents"][0].keys():
				self.debugmsg(9, "UpdateRunStats: colno:", colno, "col:", col)
				cols.append(self.PrettyColName(col))
			self.debugmsg(9, "cols:", cols)
			with open(txtreport, 'w', newline='', encoding="utf8") as csvfile:
				# writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				writer = csv.writer(csvfile, dialect='excel')
				writer.writerow(cols)
				for row in self.dbqueue["ReadResult"]["Agents"]:
					rowdata = row.values()
					writer.writerow(rowdata)

			filecount += 1

		self.debugmsg(6, "RawResults self.args.nogui:", self.args.nogui, "	self.run_starttime:", self.run_starttime, "	self.run_start:", self.run_start, "	self.run_end:", self.run_end)
		if self.args.nogui or self.run_start > 0:
			self.debugmsg(6, "Wait for RawResults")
			while_cnt = while_max
			while "RawResults" not in self.dbqueue["ReadResult"] and while_cnt > 0:
				time.sleep(0.1)
				while_cnt -= 1
			self.debugmsg(6, "Wait for RawResults>0")
			while_cnt = while_max
			while "RawResults" not in self.dbqueue["ReadResult"] \
				and len(self.dbqueue["ReadResult"]["RawResults"]) < 1 \
				and while_cnt > 0:
				time.sleep(0.1)
				while_cnt -= 1

		if "RawResults" in self.dbqueue["ReadResult"] and len(self.dbqueue["ReadResult"]["RawResults"]) > 0:
			fileprefix = self.run_name
			self.debugmsg(9, "fileprefix:", fileprefix)
			if len(fileprefix) < 1:
				fileprefix = os.path.split(self.datapath)[-1]
				self.debugmsg(9, "fileprefix:", fileprefix)
			txtreport = os.path.join(self.datapath, "{}_raw_result_data.csv".format(fileprefix))
			self.debugmsg(6, "txtreport:", txtreport)
			self.debugmsg(1, "Raw Result Data:", txtreport)
			cols = []
			for col in self.dbqueue["ReadResult"]["RawResults"][0].keys():
				self.debugmsg(9, "colno:", colno, "col:", col)
				cols.append(self.PrettyColName(col))
			self.debugmsg(9, "cols:", cols)
			with open(txtreport, 'w', newline='', encoding="utf8") as csvfile:
				# writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				writer = csv.writer(csvfile, dialect='excel')
				writer.writerow(cols)
				for row in self.dbqueue["ReadResult"]["RawResults"]:
					rowdata = row.values()
					writer.writerow(rowdata)

			filecount += 1

		self.debugmsg(6, "filecount:", filecount)
		if not self.args.nogui:
			if filecount > 0:
				# tkm.showinfo("RFSwarm - Info", "Report data saved to: {}".format(self.datapath))
				self.core.display_info("Report data saved to: {}".format(self.datapath))
			else:
				# tkm.showwarning("RFSwarm - Warning", "No report data to save.")
				self.core.display_warning("No report data to save.")

	def create_metric(self, MetricName, MetricType):
		# Save Metric Data
		# 	First ensure a metric for this agent exists
		if "MetricCount" not in self.MetricIDs:
			self.MetricIDs["MetricCount"] = 0
		if MetricType not in self.MetricIDs:
			self.MetricIDs[MetricType] = {}
		if MetricName not in self.MetricIDs[MetricType]:
			self.MetricIDs["MetricCount"] += 1
			MetricCount = int(self.MetricIDs["MetricCount"])
			self.MetricIDs[MetricType][MetricName] = {}
			MetricID = int(time.time()) + MetricCount
			self.MetricIDs[MetricType][MetricName]["ID"] = MetricID
			# create the agent metric
			if self.datadb is not None:
				self.dbqueue["Metric"].append((MetricID, MetricName, MetricType))

		return self.MetricIDs[MetricType][MetricName]["ID"]

	def save_metrics(self, PMetricName, MetricType, MetricTime, SMetricName, MetricValue, DataSource):
		self.debugmsg(7, PMetricName, MetricType, MetricTime, SMetricName, MetricValue)
		metricid = self.create_metric(PMetricName, MetricType)
		dsid = self.create_metric(DataSource, "DataSource")

		# store in memory
		if SMetricName not in self.MetricIDs[MetricType][PMetricName]:
			self.MetricIDs[MetricType][PMetricName][SMetricName] = {}
		# I don't want to store all the data in memory, this can be pulled from the DB
		# 	self.MetricIDs[MetricType][PMetricName][SMetricName]["Time"] = []
		# 	self.MetricIDs[MetricType][PMetricName][SMetricName]["objTime"] = []
		# 	self.MetricIDs[MetricType][PMetricName][SMetricName]["Values"] = []
		# # self.MetricIDs[MetricType][PMetricName][SMetricName][MetricTime] = MetricValue
		# self.MetricIDs[MetricType][PMetricName][SMetricName]["Time"].append(MetricTime)
		# self.MetricIDs[MetricType][PMetricName][SMetricName]["objTime"].append(datetime.fromtimestamp(MetricTime))
		# self.MetricIDs[MetricType][PMetricName][SMetricName]["Values"].append(MetricValue)

		# save to db
		if self.datadb is not None:
			self.debugmsg(7, "metricid:", metricid, MetricTime, SMetricName, MetricValue, DataSource)
			self.dbqueue["Metrics"].append((metricid, MetricTime, SMetricName, MetricValue, dsid))

	def add_scriptfilter(self, filtername):
		self.debugmsg(7, "filtername:", filtername, self.scriptfilters)
		if filtername not in self.scriptfilters:
			self.scriptfilters.append(filtername)
			self.scriptfilters.sort()
		self.debugmsg(9, "filtername:", filtername, self.scriptfilters)

	def sec2hms(self, sec):
		self.debugmsg(6, "type(sec):", type(sec), sec)
		if isinstance(sec, time.struct_time):
			sec = time.mktime(sec)
			self.debugmsg(6, "type(sec):", type(sec), sec)
		h = int(sec / 3600)
		m = int((sec - h * 3600) / 60)
		s = int((sec - h * 3600) - m * 60)
		hms = "{:02}:{:02}:{:02}".format(h, m, s)
		return hms

	def hms2sec(self, hms):
		sec = 0
		arrhms = str(hms).split(":")
		self.debugmsg(6, "arrhms:", arrhms)
		if len(arrhms) == 3:
			if len(arrhms[0]) > 0:
				h = int(arrhms[0])
			else:
				h = 0
			if len(arrhms[1]) > 0:
				m = int(arrhms[1])
			else:
				m = 0
			if len(arrhms[2]) > 0:
				s = int(arrhms[2])
			else:
				s = 0
			sec = (h * 3600) + (m * 60) + s
		if len(arrhms) == 2:
			h = 0
			if len(arrhms[0]) > 0:
				m = int(arrhms[0])
			else:
				m = 0
			if len(arrhms[1]) > 0:
				s = int(arrhms[1])
			else:
				s = 0
			sec = (h * 3600) + (m * 60) + s
		if len(arrhms) == 1:
			sec = int(arrhms[0])
		return sec

	def GetKey(self, mydict, myval):
		# for key, value in mydict.items():
		# 	self.debugmsg(5, "key:", key, "	value:", value)
		# 	if myval == value:
		# 		return key
		# 	return "Value not found"
		vals = list(mydict.values())
		try:
			id = vals.index(myval)
			return list(mydict.keys())[id]
		except Exception:
			return "Value, {} not found".format(myval)

	def localipaddresslist(self):
		ipaddresslist = []
		iflst = psutil.net_if_addrs()
		for nic in iflst.keys():
			self.debugmsg(6, "nic", nic)
			for addr in iflst[nic]:
				# '127.0.0.1', '::1', 'fe80::1%lo0'
				self.debugmsg(6, "addr", addr.address)
				if addr.address not in ['127.0.0.1', '::1', 'fe80::1%lo0']:
					ipaddresslist.append(addr.address)
		return ipaddresslist

	def agents_ready(self):
		readycount = 0
		for agent in self.Agents.keys():
			if "FileCount" in self.Agents[agent]:
				localfc = len(self.scriptfiles.keys())
				if int(self.Agents[agent]["FileCount"]) >= localfc:
					if "Status" in self.Agents[agent] and self.Agents[agent]["Status"]:
						readycount += 1
			else:
				if "Status" in self.Agents[agent] and self.Agents[agent]["Status"]:
					readycount += 1

		return readycount

	def configparser_safe_dict(self, dictin):
		self.debugmsg(8, "dictin: ", dictin)
		dictout = dictin
		for k in dictout.keys():
			self.debugmsg(8, "value type: ", type(dictout[k]))
			if isinstance(dictout[k], dict):
				dictout[k] = self.configparser_safe_dict(dictout[k])
			if isinstance(dictout[k], str):
				dictout[k] = self.inisafevalue(dictout[k])
			if dictout[k] is None:
				dictout[k] = ""
		self.debugmsg(7, "dictout: ", dictout)
		return dictout
