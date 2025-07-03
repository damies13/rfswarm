

import configparser
import glob
import inspect
import json
import math
import os
import random
import re
import sqlite3
import sys
import tempfile
import threading
import time
import tkinter.font as tkFont
import zoneinfo  # says Requires python 3.9
from datetime import datetime  # , timezone
from typing import Any
import tzlocal
import yaml
from lxml import etree  # used for xhtml export

if True:  # noqa: E402
	sys.path.append(os.path.abspath(os.path.dirname(__file__)))
	from percentile import percentile
	from stdevclass import stdevclass


class ReporterBase:
	version = "1.6.0"
	debuglvl = 0

	save_ini = True
	running = True
	displaygui = True
	core = None
	gui = None
	darkmode = False

	report = None
	save_template = True

	dir_path = os.path.dirname(os.path.realpath(__file__))

	run_dbthread = True
	dbthread = None
	# datapath = ""
	# dbfile = ""
	datadb = None
	dbqueue: Any = {"Write": [], "Read": [], "ReadResult": {}, "Results": [], "Metric": [], "Metrics": []}
	db_compile_options: Any = []

	defaultlabels = {"lbl_Result": "Result", "lbl_Test": "Test", "lbl_Script": "Script", "lbl_Error": "Error", "lbl_Count": "Count", "lbl_Screenshot": "Screenshot", "lbl_NoScreenshot": "No Screenshot"}

	settings: Any = {}
	reportdata: Any = {}

	settings["DBTable"] = {}
	settings["DBTable"]["Metrics"] = {}
	settings["DBTable"]["Metrics"]["DataSource"] = 0

	settings["ContentTypes"] = {"head": "Heading", "contents": "Contents", "note": "Note", "graph": "Data Graph", "table": "Data Table", "errors": "Error Details"}

	defcolours = ['#000000', '#008450', '#B81D13', '#EFB700', '#888888']
	namecolours = ['total', 'pass', 'fail', 'warning', 'not run']

	illegal_xml_chars_re = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]', re.UNICODE)

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

		inifilename = "RFSwarmReporter.ini"
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

	def saveini(self):
		self.debugmsg(6, "save_ini:", self.save_ini)
		if self.save_ini:
			with open(self.reporter_ini, 'w', encoding="utf8") as configfile:    # save
				self.config.write(configfile)
				self.debugmsg(6, "File Saved:", self.reporter_ini)

	def whitespace_set_ini_value(self, valin):
		self.debugmsg(9, "valin:", valin)
		valout = str(valin)
		if len(valout) > 0:
			valout = valout.replace('\n', 'x12')
			valout = valout.replace('\r', 'x15')
			valout = valout.replace('\t', 'x11')
			valout = valout.replace('[', 'x91')
			valout = valout.replace(']', 'x93')
			valout = valout.replace('%', 'x37')
			# valout = valout.replace('%', '%%')
			valout = valout.replace('#', 'x35')
			self.debugmsg(9, "valout:", valout)
		return valout

	def whitespace_get_ini_value(self, valin):
		self.debugmsg(9, "valin:", valin)
		valout = str(valin)
		if len(valout) > 0:
			valout = valout.replace('x12', '\n')
			valout = valout.replace('x15', '\r')
			valout = valout.replace('x11', '\t')
			valout = valout.replace('x91', '[')
			valout = valout.replace('x93', ']')
			valout = valout.replace('x37', '%')
			valout = valout.replace('x35', '#')
			self.debugmsg(9, "valout:", valout)
		return valout

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

	def configparser_safe_dict(self, dictin):
		self.debugmsg(7, "dictin: ", dictin)
		dictout = dictin
		for k in dictout.keys():
			self.debugmsg(7, "value type: ", type(dictout[k]))
			if isinstance(dictout[k], dict):
				dictout[k] = self.configparser_safe_dict(dictout[k])
			if isinstance(dictout[k], str):
				dictout[k] = self.whitespace_set_ini_value(dictout[k])
			if dictout[k] is None:
				dictout[k] = ""
		self.debugmsg(7, "dictout: ", dictout)
		return dictout

	#
	# Template Functions
	#

	def template_create(self):
		# self.report_create()
		self.report = configparser.ConfigParser()
		self.config['Reporter']['Template'] = ""
		if "Report" not in self.report:
			self.report["Report"] = {}
		self.report["Report"]["Order"] = ""
		# self.debugmsg(5, "template order:", self.report["Report"]["Order"])

		self.debugmsg(5, "self.report: ", self.report._sections)

		#
		# 	Information
		#
		es = self.report_new_section("TOP", "Information")
		self.report_item_set_type(es, 'note')
		notetxt = "Define your template by adding sections and configuring the section settings\n"
		notetxt += "Each section can be:\n"
		notetxt += " -  Note (like this) section, free text\n"
		notetxt += " -  Heading, usefull for grouping sections\n"
		notetxt += " -  Contents like a table of contents or figures\n"
		notetxt += " -  Data Table, with data from test results\n"
		notetxt += " -  Data Graph, for graphical representation of test results\n"
		notetxt += " -  Errors, gather error details and screenshots (if applicable) from robot logs\n\n"
		notetxt += "Each section can also have sub sections.\n\n"
		notetxt += "Use the arrows buttons to move sections up and down within the report.\n\n"
		notetxt += "The cover page and overall report settings can be found on the settings pane of the Report item above.\n\n"
		notetxt += "When you have your report how you like it, save it as a report template, so your future test results can use the same report format.\n\n"
		self.rt_note_set(es, notetxt)

		#
		# 	Table of Contents
		#
		# name = Contents
		# parent = TOP
		toc = self.report_new_section("TOP", "Table of Contents")
		# type = contents
		self.report_item_set_type(toc, 'contents')
		# mode = Table Of Contents
		self.rt_contents_set_mode(toc, 'Table Of Contents')
		# level = 2
		self.rt_contents_set_level(toc, '2')

		#
		# 	Scenario Plan
		#
		plng = self.report_new_section("TOP", "Scenario Plan")
		self.report_item_set_type(plng, 'graph')

		# [FB9082D01BCL]
		plngl = plng + "L"
		self.report_add_subsection(plngl)
		# datatype = Plan
		self.rt_table_set_dt(plngl, 'Plan')
		# changed = 1728738092.5689259
		# sql = SELECT md1.* , md0.SecondaryMetric as x91Filex93 , fp0.SecondaryMetric as x91FilePathx93 FROM MetricData as md0 LEFT JOIN MetricData as fp0 ON fp0.MetricValue = md0.MetricValue AND fp0.MetricType = 'Scenario' AND fp0.PrimaryMetric like 'Local_Path_x37' LEFT JOIN MetricData as md1 ON md1.SecondaryMetric = md0.MetricValue AND md1.MetricType = 'Scenario' WHERE md0.MetricType = 'Scenario' AND md0.PrimaryMetric like 'Test_x37'
		# showtotal = 1
		self.report_item_set_int(plngl, "ShowTotal", 1)

		# [FB9082D01BCR]
		plngr = plng + "R"
		self.report_add_subsection(plngr)
		# datatype = None
		self.rt_table_set_dt(plngr, 'None')

		#
		# 	-	Scenario Detail
		#
		# name = Scenario Detail
		# parent = FB9082D01BC
		plnt = self.report_new_section(plng, "Scenario Detail")
		# type = table
		self.report_item_set_type(plnt, 'table')
		# colours = 1
		self.rt_table_set_colours(plnt, 1)
		# datatype = Plan
		self.rt_table_set_dt(plnt, "Plan")
		# col_index_show = 1
		self.report_item_set_bool(plnt, self.rt_table_ini_colname("index Show"), 1)
		# col_robots_show = 1
		self.report_item_set_bool(plnt, self.rt_table_ini_colname("robots Show"), 1)
		# col_delay_show = 1
		self.report_item_set_bool(plnt, self.rt_table_ini_colname("delay Show"), 1)
		# col_ramp_up_show = 1
		self.report_item_set_bool(plnt, self.rt_table_ini_colname("ramp up Show"), 1)
		# col_run_show = 1
		self.report_item_set_bool(plnt, self.rt_table_ini_colname("run Show"), 1)
		# col_script_show = 1
		self.report_item_set_bool(plnt, self.rt_table_ini_colname("script Show"), 1)
		# col_script_opt = File
		self.report_item_set_value(plnt, self.rt_table_ini_colname("script Opt"), "File")
		# col_test_show = 1
		self.report_item_set_bool(plnt, self.rt_table_ini_colname("test Show"), 1)
		#
		# 	-	Monitoring Detail
		#
		# name = Monitoring Detail
		mtrt = self.report_new_section(plng, "Monitoring Detail")
		# type = table
		self.report_item_set_type(mtrt, 'table')
		# colours = 1
		self.rt_table_set_colours(mtrt, 0)
		# datatype = Monitoring
		self.rt_table_set_dt(mtrt, "Monitoring")
		# col_index_show = 1
		self.report_item_set_bool(mtrt, self.rt_table_ini_colname("index Show"), 1)
		# col_robots_show = 1
		self.report_item_set_bool(mtrt, self.rt_table_ini_colname("robots Show"), 1)
		# col_delay_show = 1
		self.report_item_set_bool(mtrt, self.rt_table_ini_colname("run Show"), 1)
		# col_script_show = 1
		self.report_item_set_bool(mtrt, self.rt_table_ini_colname("script Show"), 1)
		# col_script_opt = File
		self.report_item_set_value(mtrt, self.rt_table_ini_colname("script Opt"), "File")
		# col_test_show = 1
		self.report_item_set_bool(mtrt, self.rt_table_ini_colname("test Show"), 1)

		#
		# 	Test Result Summary
		#
		# name = Test Result Summary
		# parent = TOP
		trs = self.report_new_section("TOP", "Test Result Summary")
		# type = table
		self.report_item_set_type(trs, 'table')

		# colours = 0
		self.rt_table_set_colours(trs, 0)
		# datatype = ResultSummary
		self.rt_table_set_dt(trs, "ResultSummary")
		# filteragent =
		# filtertype = None
		# col_result_name_show = 1
		self.report_item_set_bool(trs, self.rt_table_ini_colname("Result Name Show"), 1)
		# col_minimum_show = 0
		self.report_item_set_bool(trs, self.rt_table_ini_colname("minimum Show"), 0)
		# col_average_show = 1
		self.report_item_set_bool(trs, self.rt_table_ini_colname("average Show"), 1)
		# col_90x37ile_show = 1
		self.report_item_set_bool(trs, self.rt_table_ini_colname("90%ile Show"), 1)
		# col_maximum_show = 1
		self.report_item_set_bool(trs, self.rt_table_ini_colname("maximum Show"), 1)
		# col_std_dev_show = 1
		self.report_item_set_bool(trs, self.rt_table_ini_colname("Std Dev Show"), 1)
		# col_pass_show = 1
		self.report_item_set_bool(trs, self.rt_table_ini_colname("pass Show"), 1)
		# col_fail_show = 1
		self.report_item_set_bool(trs, self.rt_table_ini_colname("fail Show"), 1)
		# col_other_show = 0
		self.report_item_set_bool(trs, self.rt_table_ini_colname("other Show"), 0)

		#
		# 	Robots vs Response Time
		#
		rrt = self.report_new_section("TOP", "Robots vs Response Time")
		self.report_item_set_type(rrt, 'graph')

		# [FA37C950802L]idl
		rttl = rrt + "L"
		self.report_add_subsection(rttl)
		# resulttype = Response Time
		self.report_item_set_value(rttl, "resulttype", "Response Time")
		# changed = 1728738059.779502
		# filterresult = None
		# filteragent = None
		# datatype = Result
		self.rt_table_set_dt(rttl, 'Result')

		# [FA37C950802R]
		rttr = rrt + "R"
		self.report_add_subsection(rttr)
		# datatype = Metric
		self.rt_table_set_dt(rttr, 'Metric')
		# changed = 1728738059.7891614
		# axisen = 1
		self.report_item_set_bool(rttr, "axisen", 1)
		# metrictype = Scenario
		self.report_item_set_value(rttr, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		self.report_item_set_value(rttr, "secondarymetric", "total_robots")

		#
		# 	-	Response Times
		#
		# name = Response Times
		rt = self.report_new_section(rrt, "Response Times")
		# parent = FA37C950802
		self.report_item_set_type(rt, 'table')
		# type = table
		self.report_item_set_value(rt, "type", "table")
		# changed = 1728738060.9264157
		# colours = 1
		self.report_item_set_bool(rt, "colours", 1)
		# datatype = Result
		self.report_item_set_value(rt, "datatype", "Result")
		# resulttype = Response Time
		self.report_item_set_value(rt, "resulttype", "Response Time")
		# filterresult = None
		# filteragent = None

		#
		# 	-	Robots
		#
		# name = Robots
		rb = self.report_new_section(rrt, "Robots")
		# type = table
		self.report_item_set_type(rb, 'table')
		# parent = FA37C950802
		# changed = 1728744845.4971852
		# colours = 1
		self.report_item_set_bool(rb, "colours", 1)
		# datatype = Metric
		self.report_item_set_value(rb, "datatype", "Metric")
		# metrictype = Scenario
		self.report_item_set_value(rb, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		# secondarymetric = total_robots
		self.report_item_set_value(rb, "secondarymetric", "total_robots")
		# isnumeric = 1
		self.report_item_set_bool(rb, "isnumeric", 1)
		# showcount = 0
		self.report_item_set_bool(rb, "showcount", 1)
		# col_primarymetric_show = 1
		self.report_item_set_bool(rb, "col_primarymetric_show", 1)
		# col_minimum_show = 0
		self.report_item_set_bool(rb, "col_minimum_show", 0)
		# col_average_show = 0
		self.report_item_set_bool(rb, "col_average_show", 0)
		# col_90x37ile_show = 0
		self.report_item_set_bool(rb, "col_90x37ile_show", 0)
		# col_maximum_show = 1
		self.report_item_set_bool(rb, "col_maximum_show", 1)
		# col_std_dev_show = 0
		self.report_item_set_bool(rb, "col_std_dev_show", 0)
		# col_maximum = Robots
		self.report_item_set_value(rb, "col_maximum", "Robots")

		#
		# 	Agents
		#
		# name = Agents
		agnt = self.report_new_section("TOP", "Agents")
		# type = head
		self.report_item_set_type(agnt, 'head')
		# parent = TOP

		#
		# 	-	CPU
		#
		cpu = self.report_new_section(agnt, "Agent CPU Usage")
		self.report_item_set_type(cpu, 'graph')
		# name = CPU
		# parent = FB90C705569
		# type = graph

		# [FB90C728C87L]
		cpul = cpu + "L"
		self.report_add_subsection(cpul)
		# metrictype = Agent
		self.report_item_set_value(cpul, "metrictype", "Agent")
		# changed = 1728745351.1353724
		self.report_item_set_bool(cpul, "axisen", 1)
		# filteragent = None
		# filtertype = None
		# datatype = Metric
		self.report_item_set_value(cpul, "datatype", "Metric")
		# secondarymetric = CPU
		self.report_item_set_value(cpul, "secondarymetric", "CPU")
		# enablefilteragent = 1
		self.report_item_set_bool(cpul, "enablefilteragent", 1)
		#
		# [FB90C728C87R]
		cpur = cpu + "R"
		self.report_add_subsection(cpur)
		# datatype = Metric
		self.report_item_set_value(cpur, "datatype", "Metric")
		# changed = 1728745351.027923
		# axisen = 1
		self.report_item_set_bool(cpur, "axisen", 1)
		# metrictype = Scenario
		self.report_item_set_value(cpur, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		# secondarymetric = total_robots
		self.report_item_set_value(cpur, "secondarymetric", "total_robots")

		#
		# 	-	Memory
		#
		# name = Memory
		mem = self.report_new_section(agnt, "Agent Memory (RAM) Usage")
		# type = graph
		self.report_item_set_type(mem, 'graph')

		# [FB90C73DBB6L]
		meml = mem + "L"
		self.report_add_subsection(meml)
		# metrictype = Agent
		self.report_item_set_value(meml, "metrictype", "Agent")
		# changed = 1728745342.77505
		self.report_item_set_bool(meml, "axisen", 1)
		# filteragent = None
		# filtertype = None
		# datatype = Metric
		self.report_item_set_value(meml, "datatype", "Metric")
		# secondarymetric = MEM
		self.report_item_set_value(meml, "secondarymetric", "MEM")
		# enablefilteragent = 1
		self.report_item_set_bool(meml, "enablefilteragent", 1)
		#
		# [FB90C73DBB6R]
		memr = mem + "R"
		self.report_add_subsection(memr)
		# datatype = Metric
		self.report_item_set_value(memr, "datatype", "Metric")
		# changed = 1728745342.6672406
		# axisen = 1
		self.report_item_set_bool(memr, "axisen", 1)
		# filteragent = None
		# filtertype = None
		# metrictype = Scenario
		self.report_item_set_value(memr, "metrictype", "Scenario")
		# secondarymetric = total_robots
		self.report_item_set_value(memr, "secondarymetric", "total_robots")

		#
		# 	-	Agent Names
		#
		# name = Agent Names
		an = self.report_new_section(agnt, "Agent Names")
		# type = table
		self.report_item_set_type(an, 'table')
		# colours = 1
		self.report_item_set_bool(an, "colours", 1)
		# datatype = Metric
		self.report_item_set_value(an, "datatype", "Metric")
		# metrictype = Agent
		self.report_item_set_value(an, "metrictype", "Agent")
		# filteragent = None
		# filtertype = None
		# col_primarymetric_show = 0
		self.report_item_set_bool(an, "col_primarymetric_show", 0)
		# col_metrictype_show = 1
		self.report_item_set_bool(an, "col_metrictype_show", 1)
		# col_secondarymetric_show = 1
		self.report_item_set_bool(an, "col_secondarymetric_show", 1)
		# col_metricvalue_show = 0
		self.report_item_set_bool(an, "col_metricvalue_show", 0)
		# enablefilteragent = 1
		self.report_item_set_bool(an, "enablefilteragent", 1)
		# secondarymetric = CPU
		self.report_item_set_value(an, "secondarymetric", "CPU")
		# col_agent_show = 1
		self.report_item_set_bool(an, "col_agent_show", 1)

		#
		# 	-	Agent Details
		#
		# name = Agent Details
		ad = self.report_new_section(agnt, "Agent Details")
		# type = table
		self.report_item_set_type(ad, 'table')
		# parent = FB90C705569
		# changed = 1728745707.049637
		# colours = 0
		self.report_item_set_bool(ad, "colours", 0)
		# datatype = Metric
		self.report_item_set_value(ad, "datatype", "Metric")
		# metrictype = Agent
		self.report_item_set_value(ad, "metrictype", "Agent")
		# filteragent = None
		# filtertype = None
		# col_primarymetric_show = 1
		self.report_item_set_bool(ad, "col_primarymetric_show", 1)
		# col_metrictype_show = 1
		self.report_item_set_bool(ad, "col_metrictype_show", 1)
		# col_secondarymetric_show = 1
		self.report_item_set_bool(ad, "col_secondarymetric_show", 1)
		# col_metricvalue_show = 1
		self.report_item_set_bool(ad, "col_metricvalue_show", 1)
		# enablefilteragent = 1
		self.report_item_set_bool(ad, "enablefilteragent", 1)
		# col_agent_show = 0
		self.report_item_set_bool(ad, "col_agent_show", 0)
		# col_primarymetric = Agent Name
		self.report_item_set_value(ad, "col_primarymetric", "Agent Name")
		# col_secondarymetric = Metric Name
		self.report_item_set_value(ad, "col_secondarymetric", "Metric Name")
		# col_metricvalue = Metric Value
		self.report_item_set_value(ad, "col_metricvalue", "Metric Value")

		# 	Errors
		#
		# name = Errors
		# parent = TOP
		err = self.report_new_section("TOP", "Errors")
		# type = head
		self.report_item_set_type(err, 'head')

		#
		# 	-	Failed Keywords Graph
		#
		# name = Failed Keywords Graph
		fkg = self.report_new_section(err, "Failed Keywords Graph")
		# type = graph
		self.report_item_set_type(fkg, 'graph')

		# [FB90CDCCFC9L]
		fkgl = fkg + "L"
		self.report_add_subsection(fkgl)
		self.report_item_set_bool(fkgl, "axisen", 1)
		# resulttype = TPS
		self.report_item_set_value(fkgl, "resulttype", "TPS")
		# changed = 1728746053.26743
		# filterresult = Fail
		self.report_item_set_value(fkgl, "filterresult", "Fail")
		# filteragent = None
		# datatype = Result
		self.report_item_set_value(fkgl, "datatype", "Result")
		# enablefilterresult = 1
		self.report_item_set_bool(fkgl, "enablefilterresult", 1)

		#
		# [FB90CDCCFC9R]
		fkgr = fkg + "R"
		self.report_add_subsection(fkgr)
		# datatype = Metric
		self.report_item_set_value(fkgr, "datatype", "Metric")
		# changed = 1728746053.2828546
		# axisen = 1
		self.report_item_set_bool(fkgr, "axisen", 1)
		# metrictype = Scenario
		self.report_item_set_value(fkgr, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		# secondarymetric = total_robots
		self.report_item_set_value(fkgr, "secondarymetric", "total_robots")

		#
		# 	-	Failed Keywords Names
		#
		# name = Failed Keywords Names
		fkn = self.report_new_section(err, "Failed Keywords Names")
		# type = table
		self.report_item_set_type(fkn, 'table')
		# parent = FB90CD6ECAE
		# changed = 1728746043.623058
		# colours = 1
		self.report_item_set_bool(fkn, "colours", 1)
		# datatype = Result
		self.report_item_set_value(fkn, "datatype", "Result")
		# resulttype = TPS
		self.report_item_set_value(fkn, "resulttype", "TPS")
		# filterresult = Fail
		self.report_item_set_value(fkn, "filterresult", "Fail")
		# filteragent = None
		# enablefilterresult = 1
		self.report_item_set_bool(fkn, "enablefilterresult", 1)
		# col_result_name_show = 1
		self.report_item_set_bool(fkn, "col_result_name_show", 1)
		# col_result_show = 1
		self.report_item_set_bool(fkn, "col_result_show", 1)
		# col_count_show = 1
		self.report_item_set_bool(fkn, "col_count_show", 1)

		#
		# 	-	Error Details
		#
		# name = Error Details
		ed = self.report_new_section(err, "Error Details")
		# type = errors
		self.report_item_set_type(ed, 'errors')
		# parent = FB90CD6ECAE
		# changed = 1728746092.6821463
		# images = 1
		self.report_item_set_bool(ed, "images", 1)
		# grouprn = 1
		self.report_item_set_bool(ed, "grouprn", 1)
		# groupet = 1
		self.report_item_set_bool(ed, "groupet", 1)

	def template_save(self, filename):
		saved = False
		if filename is None or len(filename) < 1:
			filename = self.config['Reporter']['Template']

		arrfile = os.path.splitext(filename)
		self.debugmsg(5, "arrfile: ", arrfile)

		if arrfile[1].lower() not in [".template", ".yml", ".yaml", ".json"]:
			msg = "Unsupported file type: " + arrfile[1].lower()
			self.core.display_message(msg)
			return 1

		templatedata = configparser.ConfigParser()
		templatedata.read_dict(self.report._sections)
		if "Report" in templatedata:
			if "starttime" in templatedata["Report"]:
				# templatedata["Report"]["starttime"]
				templatedata.remove_option('Report', 'starttime')
			if "endtime" in templatedata["Report"]:
				# templatedata["Report"]["endtime"]
				templatedata.remove_option('Report', 'endtime')

		with open(filename, 'w', encoding="utf8") as templatefile:    # save
			if arrfile[1].lower() == ".template":
				templatedata.write(templatefile)
				saved = True
			if arrfile[1].lower() in [".yml", ".yaml"]:
				yaml.dump(templatedata._sections, templatefile, default_flow_style=False, sort_keys=False, allow_unicode=True, encoding='utf-8')
				saved = True
			if arrfile[1].lower() == ".json":
				json.dump(templatedata._sections, templatefile, indent="\t")
				saved = True

		if saved:
			self.debugmsg(6, "Template Saved:", filename)
			self.core.display_message("Template Saved:", filename)

			self.config['Reporter']['Template'] = self.whitespace_set_ini_value(filename)
			path = os.path.split(self.config['Reporter']['Template'])[0]
			self.config['Reporter']['TemplateDir'] = self.whitespace_set_ini_value(path)
			self.saveini()

	def template_open(self, filename):
		if len(filename) > 0 and os.path.isfile(filename):
			self.debugmsg(7, "filename: ", filename)
			arrfile = os.path.splitext(filename)
			self.debugmsg(5, "arrfile: ", arrfile)

			if len(arrfile) < 2:
				msg = "Template file ", filename, " missing extention, unable to determine supported format. Plesae use extentions .template, .yaml or .json"
				self.core.display_message(msg)
				self.template_create()
				return 1
			if arrfile[1].lower() not in [".template", ".yml", ".yaml", ".json"]:
				msg = "Template file ", filename, " has an invalid extention, unable to determine supported format. Plesae use extentions .template, .yaml or .json"
				self.core.display_message(msg)
				self.template_create()
				return 1

			self.config['Reporter']['Template'] = self.whitespace_set_ini_value(filename)
			path = os.path.split(self.config['Reporter']['Template'])[0]
			self.config['Reporter']['TemplateDir'] = self.whitespace_set_ini_value(path)
			self.saveini()

			self.report = None
			self.reportdata = {}
			self.report = configparser.ConfigParser()

			if arrfile[1].lower() == ".template":
				self.report.read(filename, encoding="utf8")
			else:
				filedict = {}
				if arrfile[1].lower() in [".yml", ".yaml"]:
					# read yaml file
					self.debugmsg(5, "read yaml file")
					with open(filename, 'r', encoding="utf-8") as f:
						filedict = yaml.safe_load(f)
					self.debugmsg(5, "filedict: ", filedict)
					filedict = self.configparser_safe_dict(filedict)
					self.debugmsg(5, "filedict: ", filedict)
				if arrfile[1].lower() == ".json":
					# read json file
					self.debugmsg(5, "read json file")
					with open(filename, 'r', encoding="utf-8") as f:
						filedict = json.load(f)
					self.debugmsg(5, "filedict: ", filedict)
					filedict = self.configparser_safe_dict(filedict)
					self.debugmsg(5, "filedict: ", filedict)
				self.debugmsg(5, "filedict: ", filedict)
				self.report.read_dict(filedict)

			self.debugmsg(7, "self.report: ", self.report)
			if "Colours" in self.report:
				self.debugmsg(7, "self.report[Colours]: ", self.report["Colours"])
				if "defcolours" in self.report["Colours"]:
					self.defcolours = self.whitespace_get_ini_value(self.report["Colours"]["defcolours"]).split(",")
					self.debugmsg(7, "self.defcolours: ", self.defcolours)
				if "namecolours" in self.report["Colours"]:
					self.namecolours = self.whitespace_get_ini_value(self.report["Colours"]["namecolours"]).split(",")
					self.debugmsg(7, "self.namecolours: ", self.namecolours)

			self.report_item_set_changed_all("TOP")

		else:
			self.template_create()

	#
	# Report Functions
	#

	def report_save(self):
		saved = False
		if 'Reporter' in self.config:
			if "Colours" not in self.report:
				self.report["Colours"] = {}
			self.report["Colours"]["defcolours"] = self.whitespace_set_ini_value(",".join(self.defcolours))
			self.report["Colours"]["namecolours"] = self.whitespace_set_ini_value(",".join(self.namecolours))

			if 'Report' in self.config['Reporter'] and len(self.config['Reporter']['Report']) > 0:
				filename = self.config['Reporter']['Report']
				filedir = os.path.dirname(filename)
				if os.path.isdir(filedir):
					with open(filename, 'w', encoding="utf8") as reportfile:    # save
						self.report.write(reportfile)
						self.debugmsg(6, "Report Saved:", filename)
						saved = True
		return saved

	def report_open(self):
		filename = self.config['Reporter']['Report']
		self.debugmsg(7, "filename: ", filename)
		self.reportdata = {}
		self.report = None
		if len(filename) > 0 and os.path.isfile(filename):
			self.debugmsg(7, "filename: ", filename, " exists, open")
			self.report = configparser.ConfigParser()
			self.report.read(filename, encoding="utf8")
		else:
			templatefile = self.whitespace_get_ini_value(self.config['Reporter']['Template'])
			self.debugmsg(7, "Template: ", templatefile)
			if len(templatefile) > 0:
				self.template_open(templatefile)
			else:
				self.debugmsg(7, "template_create")
				self.template_create()
			self.debugmsg(7, "report_save")
			self.report_save()

		self.debugmsg(7, "self.report: ", self.report)
		if "Colours" in self.report:
			self.debugmsg(7, "self.report[Colours]: ", self.report["Colours"])
			if "defcolours" in self.report["Colours"]:
				self.defcolours = self.whitespace_get_ini_value(self.report["Colours"]["defcolours"]).split(",")
				self.debugmsg(7, "self.defcolours: ", self.defcolours)
			if "namecolours" in self.report["Colours"]:
				self.namecolours = self.whitespace_get_ini_value(self.report["Colours"]["namecolours"]).split(",")
				self.debugmsg(7, "self.namecolours: ", self.namecolours)

	def report_starttime(self):
		if "starttime" in self.reportdata and self.reportdata["starttime"] > 0:
			self.debugmsg(5, "starttime:", self.reportdata["starttime"])
			return self.reportdata["starttime"]
		else:
			self.reportdata["starttime"] = 0
			if self.datadb is not None:
				sql = "SELECT MetricTime "
				sql += "FROM MetricData "
				sql += "WHERE MetricType = 'Scenario' "
				sql += "AND PrimaryMetric <> 'PreRun' "
				sql += "ORDER BY MetricTime ASC "
				sql += "LIMIT 1 "

				key = "report starttime"
				self.debugmsg(9, "sql:", sql)
				self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
				while key not in self.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = self.dbqueue["ReadResult"][key]
				self.debugmsg(9, "gdata:", gdata)

				self.reportdata["starttime"] = int(gdata[0]["MetricTime"])

				self.debugmsg(5, "starttime:", self.reportdata["starttime"])

				return self.reportdata["starttime"]
			else:
				self.debugmsg(5, "starttime:", int(time.time()) - 1)
				return int(time.time()) - 1

	def report_endtime(self):
		if "endtime" in self.reportdata and self.reportdata["endtime"] > 0:
			self.debugmsg(5, "endtime:", self.reportdata["endtime"])
			return self.reportdata["endtime"]
		else:
			self.reportdata["endtime"] = 0
			if self.datadb is not None:

				sql = "SELECT MetricTime "
				sql += "FROM MetricData "
				sql += "WHERE MetricType = 'Scenario' "
				sql += "AND PrimaryMetric <> 'PreRun' "
				sql += "ORDER BY MetricTime DESC "
				sql += "LIMIT 1 "

				key = "report endtime"
				self.debugmsg(9, "sql:", sql)
				self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
				while key not in self.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = self.dbqueue["ReadResult"][key]
				self.debugmsg(9, "gdata:", gdata)

				self.reportdata["endtime"] = int(gdata[0]["MetricTime"])

				self.debugmsg(5, "endtime:", self.reportdata["endtime"])

				return self.reportdata["endtime"]
			else:
				self.debugmsg(5, "starttime:", int(time.time()))
				return int(time.time())

	def report_formatdate(self, itime):
		self.debugmsg(9, "itime:", itime)
		format = self.rs_setting_get_dateformat()
		format = format.replace("yyyy", "%Y")
		format = format.replace("yy", "%y")
		format = format.replace("mm", "%m")
		format = format.replace("dd", "%d")
		self.debugmsg(9, "format:", format)
		# fdate = datetime.fromtimestamp(itime, timezone.utc).strftime(format)
		tz = zoneinfo.ZoneInfo(self.rs_setting_get_timezone())
		fdate = datetime.fromtimestamp(itime, tz).strftime(format)
		self.debugmsg(9, "fdate:", fdate)
		return fdate

	def report_formattime(self, itime):
		self.debugmsg(9, "itime:", itime)
		format = self.rs_setting_get_timeformat()
		format = format.replace("HH", "%H")
		format = format.replace("h", "%I")
		format = format.replace("MM", "%M")
		format = format.replace("SS", "%S")
		format = format.replace("AMPM", "%p")

		self.debugmsg(9, "format:", format)
		tz = zoneinfo.ZoneInfo(self.rs_setting_get_timezone())
		ftime = datetime.fromtimestamp(itime, tz).strftime(format)
		self.debugmsg(9, "ftime:", ftime)
		return ftime

	def report_formateddatetimetosec(self, stime):
		self.debugmsg(5, "stime:", stime)
		try:
			if len(stime) == 10 and stime.isdecimal():
				return int(stime)

			if len(stime) == 13 and stime.isdecimal():
				return int(stime) / 1000

			dformat = self.rs_setting_get_dateformat()
			dformat = dformat.replace("yyyy", "%Y")
			dformat = dformat.replace("yy", "%y")
			dformat = dformat.replace("mm", "%m")
			dformat = dformat.replace("dd", "%d")

			tformat = self.rs_setting_get_timeformat()
			tformat = tformat.replace("HH", "%H")
			tformat = tformat.replace("h", "%I")
			tformat = tformat.replace("MM", "%M")
			tformat = tformat.replace("SS", "%S")
			tformat = tformat.replace("AMPM", "%p")

			tz = zoneinfo.ZoneInfo(self.rs_setting_get_timezone())

			datetime_object = datetime.strptime(stime, "{} {}".format(dformat, tformat)).replace(tzinfo=tz)
			self.debugmsg(5, "datetime_object:", datetime_object, datetime_object.timestamp())
			return int(datetime_object.timestamp())
		except Exception as e:
			self.debugmsg(8, "e:", e)
			return -1

	#
	# Report Settings
	#
	def rs_setting_get(self, name):
		self.debugmsg(9, "name:", name)
		if name in self.report["Report"]:
			return self.whitespace_get_ini_value(self.report["Report"][name])
		else:
			return None

	def rs_setting_set(self, name, value):
		self.debugmsg(9, "name:", name, "	value:", value)
		currvalue = ""
		if name in self.report["Report"]:
			currvalue = self.report["Report"][name]

		if currvalue != value:
			self.report["Report"][name] = self.whitespace_set_ini_value(value)
			# self.report_item_set_changed("Report")
			self.report_save()
			return 1
		else:
			return 0

	def rs_setting_get_int(self, name):
		value = self.rs_setting_get(name)
		if value is None:
			return -1
		else:
			return int(value)

	def rs_setting_set_int(self, name, value):
		changes = self.rs_setting_set(name, str(value))
		return changes

	def rs_setting_get_file(self, name):
		value = self.rs_setting_get(name)
		localpath = ""
		if value is not None and len(value) > 0:
			localpath = os.path.join(self.config['Reporter']['ResultDir'], value)
		return localpath

	def rs_setting_set_file(self, name, value):
		# determine relative path
		# self.config['Reporter']['Report']	self.config['Reporter']['ResultDir']
		if os.path.exists(value):
			relpath = os.path.relpath(value, start=self.config['Reporter']['ResultDir'])
			changes = self.rs_setting_set(name, relpath)
			return changes
		return 0

	def rs_setting_get_title(self):
		value = self.rs_setting_get('title')
		if value is None:
			reportname = 'Report Title'

			if 'Reporter' in self.config and 'Results' in self.config['Reporter']:
				results = self.config['Reporter']['Results']
				self.debugmsg(8, "results: ", results)
				if len(results) > 0:
					filename = os.path.basename(results)
					self.debugmsg(9, "filename: ", filename)
					basename = os.path.splitext(filename)[0]
					self.debugmsg(9, "basename: ", basename)
					basearr = basename.split('_')
					self.debugmsg(9, "basearr: ", basearr)
					basearr.pop(0)
					basearr.pop(0)
					reportname = " ".join(basearr)
					self.debugmsg(7, "reportname: ", reportname)
					self.rs_setting_set('title', reportname)

			return reportname
		else:
			return value

	def rs_setting_get_hcolour(self):
		value = self.rs_setting_get('hcolour')
		if value is None:
			return "#0000FF"  # Blue
		else:
			return value

	def rs_setting_get_font(self):
		value = self.rs_setting_get('font')
		self.debugmsg(6, "value", value)
		if not self.displaygui:
			self.debugmsg(6, "value", value)
			return value
		else:
			fontlst = list(tkFont.families())
			self.debugmsg(9, "fontlst", fontlst)
			if value not in fontlst:
				value = None
				self.debugmsg(6, "value", value)
			if value is None:
				# Verdana, Tahoma, Arial, Helvetica, sans-serif
				fontorder = ['Helvetica', 'Verdana', 'Tahoma', 'Arial', 'FreeSans']
				self.debugmsg(6, "fontorder", fontorder)
				for fnt in fontorder:
					if fnt in fontlst:
						self.debugmsg(6, "fnt", fnt)
						return fnt
				for fnt in fontlst:
					if 'Sans' in fnt or 'sans' in fnt:
						self.debugmsg(6, "fnt", fnt)
						return fnt
				self.debugmsg(6, "sans-serif")
				return 'sans-serif'
			else:
				self.debugmsg(6, "value", value)
				return value

	def rs_setting_get_fontsize(self):
		value = self.rs_setting_get_int('fontsize')
		if value < 1:
			return 12
		else:
			return int(value)

	def rs_setting_get_pctile(self):
		value = self.rs_setting_get_int('percentile')
		if value < 1:
			return 90
		else:
			return int(value)

	def rs_setting_get_dateformat(self):
		value = self.rs_setting_get('dateformat')
		if value is None:
			return "yyyy-mm-dd"
		else:
			return value

	def rs_setting_get_timeformat(self):
		value = self.rs_setting_get('timeformat')
		if value is None:
			return "HH:MM"
		else:
			return value

	def rs_setting_get_timezone(self):
		value = self.rs_setting_get('timezone')
		if value is None:
			LOCAL_TIMEZONE = tzlocal.get_localzone_name()
			return LOCAL_TIMEZONE
		else:
			return value

	def rs_setting_get_timezone_list(self):
		# ZI = zoneinfo.ZoneInfo(self.rs_setting_get_timezone())
		return zoneinfo.available_timezones()

	def rs_setting_get_starttime(self):
		value = self.rs_setting_get_int('startoffset')
		self.debugmsg(5, "value:", value)
		if value < 1:
			return self.report_starttime()
		else:
			return self.report_starttime() + int(value)

	def rs_setting_get_endtime(self):
		value = self.rs_setting_get_int('endoffset')
		self.debugmsg(5, "value:", value)
		if value < 1:
			return self.report_endtime()
		else:
			return self.report_endtime() - int(value)

	#
	# Report Sections
	#

	def report_get_order(self, parent):
		if parent == "TOP":
			self.debugmsg(7, "template order:", self.report["Report"]["Order"])
			if len(self.report["Report"]["Order"]) > 0:
				return self.report["Report"]["Order"].split(',')
			else:
				return []
		else:
			self.debugmsg(7, "parent order:", self.report[parent])
			if "Order" in self.report[parent] and len(self.report[parent]["Order"]) > 0:
				return self.report[parent]["Order"].split(',')
			else:
				return []

	def report_set_order(self, parent, orderlst):
		self.debugmsg(7, "parent:", parent, "	orderlst: ", orderlst)
		if parent == "TOP":
			self.report["Report"]["Order"] = ",".join(orderlst)
		else:
			self.report[parent]["Order"] = ",".join(orderlst)
		self.report_save()
		return 1

	def report_new_section(self, parent, name):
		id = "{:02X}".format(int(time.time() * 10000))
		while id in self.report:
			time.sleep(0.1)
			id = "{:02X}".format(int(time.time() * 10000))

		self.debugmsg(7, "id:", id)
		self.report_add_section(parent, id, name)
		return id

	def report_add_subsection(self, id):
		if id not in self.report:
			self.report[id] = {}
			self.report_save()

	def report_subsection_parent(self, id):
		pid = id
		last = id[-1:]
		if last in ['G', 'H', 'I', 'J', 'k', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
			pid = id[0:-1]
			self.report_add_subsection(id)
		self.debugmsg(8, "id:", id, "	pid:", pid)
		return pid

	def report_add_section(self, parent, id, name):
		self.debugmsg(7, "parent: ", parent)
		if id not in self.report:
			self.report[id] = {}
		self.report[id]['Name'] = self.whitespace_set_ini_value(name)
		self.report[id]['Parent'] = self.whitespace_set_ini_value(parent)
		order = self.report_get_order(parent)
		self.debugmsg(8, "order: ", order)
		order.append(id)
		self.report_set_order(parent, order)
		self.debugmsg(8, "self.report: ", self.report._sections)

	def report_item_parent(self, id):
		if id in self.report and 'Parent' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['Parent'])
		else:
			return "TOP"

	def report_remove_section(self, id):
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		self.debugmsg(8, "order: ", order)
		pos = order.index(id)
		self.debugmsg(9, "pos: ", pos)
		order.pop(pos)
		self.debugmsg(9, "order: ", order)
		self.report_set_order(parent, order)
		self.debugmsg(9, "self.report: ", self.report._sections)
		subitems = self.report_get_order(id)
		for item in subitems:
			self.report_remove_section(item)
		del self.report[id]
		idl = id + 'L'
		if idl in self.report:
			del self.report[idl]
		idr = id + 'R'
		if idr in self.report:
			del self.report[idr]

		self.debugmsg(9, "self.report: ", self.report._sections)
		self.report_save()

	def report_move_section_up(self, id):
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		self.debugmsg(5, "order: ", order)
		pos = order.index(id)
		self.debugmsg(5, "pos: ", pos)
		order.pop(pos)
		order.insert(pos - 1, id)
		self.debugmsg(5, "order: ", order)
		self.report_set_order(parent, order)

	def report_move_section_down(self, id):
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		self.debugmsg(5, "order: ", order)
		pos = order.index(id)
		self.debugmsg(5, "pos: ", pos)
		order.pop(pos)
		order.insert(pos + 1, id)
		self.debugmsg(5, "order: ", order)
		self.report_set_order(parent, order)

	def report_item_get_changed(self, id):
		self.debugmsg(8, "id:", id)
		if id == 'TOP':
			return time.time()
		if 'Changed' not in self.report[id]:
			self.report_item_set_changed(id)
		self.debugmsg(8, "Changed:", self.report[id]['Changed'], "	", float(self.report[id]['Changed']))
		return float(self.report[id]['Changed'])

	def report_item_set_changed(self, id):
		self.report[id]['Changed'] = self.whitespace_set_ini_value(str(time.time()))
		return 1

	def report_item_set_changed_all(self, id):
		if id != "TOP":
			self.report_item_set_changed(id)

		sections = self.report_get_order(id)
		for sect in sections:
			self.report_item_set_changed_all(sect)

		self.report_save()

	def report_item_get_name(self, id):
		if id == "TOP":
			return "Report"
		if id in self.report:
			return self.whitespace_get_ini_value(self.report[id]['Name'])
		else:
			return None

	def report_item_set_name(self, id, newname):
		self.report[id]['Name'] = self.whitespace_set_ini_value(newname)
		self.report_item_set_changed(id)
		self.report_save()
		return 1

	def report_sect_level(self, id):
		self.debugmsg(9, "id:", id)
		parent = self.report_item_parent(id)
		if parent == "TOP":
			return 1
		else:
			parentlvl = self.report_sect_level(parent)
			return parentlvl + 1

	def report_sect_number(self, id):
		self.debugmsg(9, "id:", id)
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		num = order.index(id) + 1
		self.debugmsg(9, "parent:", parent, "	num:", num)
		if parent == "TOP":
			self.debugmsg(9, "return:", num)
			return "{}".format(num)
		else:
			parentnum = self.report_sect_number(parent)
			self.debugmsg(9, "parentnum:", parentnum)
			self.debugmsg(9, "return:", parentnum, num)
			return "{}.{}".format(parentnum, num)

	def report_item_get_type_lbl(self, id):
		self.debugmsg(9, "id:", id)
		type = self.report_item_get_type(id)
		self.debugmsg(5, "type:", type)
		return self.settings["ContentTypes"][type]

	def report_item_get_type(self, id):
		self.debugmsg(9, "id:", id)
		default = list(self.settings["ContentTypes"].keys())[0]
		self.debugmsg(9, "default:", default)
		if id == "TOP":
			return default
		if 'Type' not in self.report[id]:
			self.debugmsg(5, "Set to default:", default)
			self.report_item_set_type(id, default)

		self.debugmsg(9, "Type:", self.report[id]['Type'])
		return self.whitespace_get_ini_value(self.report[id]['Type'])

	def report_item_set_type(self, id, newType):
		self.debugmsg(5, "id:", id, "	newType:", newType)
		self.report[id]['Type'] = self.whitespace_set_ini_value(newType)
		self.report_item_set_changed(id)
		self.report_save()

	#
	# Report Sections values
	#

	def report_item_get_value(self, id, name):
		self.debugmsg(9, "id:", id, "name:", name)
		if id in self.report and name in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id][name])
		else:
			return None

	def report_item_set_value(self, id, name, value):
		self.debugmsg(9, "id:", id, "name:", name, "	value:", value)
		currvalue = ""
		if name in self.report[id]:
			currvalue = self.report[id][name]
		if currvalue != value:
			self.report[id][name] = self.whitespace_set_ini_value(value)
			# self.report_item_set_changed("Report")
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		else:
			return 0

	def report_item_get_int(self, id, name):
		value = self.report_item_get_value(id, name)
		if value is None:
			return -1
		else:
			return int(value)

	def report_item_set_int(self, id, name, value):
		changes = self.report_item_set_value(id, name, str(value))
		return changes

	def report_item_get_float(self, id, name):
		value = self.report_item_get_value(id, name)
		if value is None:
			return -1.0
		else:
			return float(value)

	def report_item_set_float(self, id, name, value):
		changes = self.report_item_set_value(id, name, str(value))
		return changes

	def report_item_get_bool_def0(self, id, name):
		value = self.report_item_get_int(id, name)
		if value < 0:
			return 0
		else:
			return int(value)

	def report_item_get_bool_def1(self, id, name):
		value = self.report_item_get_int(id, name)
		if value < 0:
			return 1
		else:
			return int(value)

	def report_item_set_bool(self, id, name, value):
		changes = self.report_item_set_int(id, name, value)
		return changes

	#
	# Report Item Type: contents
	#

	def rt_contents_get_mode(self, id):
		self.debugmsg(8, "id:", id)
		if 'mode' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['mode'])
		else:
			return "Table Of Contents"

	def rt_contents_set_mode(self, id, mode):
		self.debugmsg(5, "id:", id, "	mode:", mode)
		changes = self.report_item_set_value(id, 'mode', mode)
		return changes

	def rt_contents_get_level(self, id):
		self.debugmsg(8, "id:", id)
		if id == "TOP":
			return 0
		if 'level' in self.report[id]:
			return int(self.report[id]['level'])
		else:
			return 1

	def rt_contents_set_level(self, id, level):
		self.debugmsg(5, "id:", id, "	level:", level)
		changes = self.report_item_set_value(id, 'level', str(level))
		return changes

	#
	# Report Item Type: note
	#

	def rt_note_get(self, id):
		self.debugmsg(9, "id:", id)
		if 'note' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['note'])
		else:
			return ""

	def rt_note_set(self, id, noteText):
		self.debugmsg(5, "id:", id, "	noteText:", noteText)
		prev = self.rt_note_get(id)
		if noteText != prev:
			self.report[id]['note'] = self.whitespace_set_ini_value(noteText)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0
		# changes = self.report_item_set_value(id, 'note', noteText)
		# return changes
	#
	# Report Item Type: graph
	#

	# 		pid, idl, idr = self.rt_graph_LR_Ids(id)
	def rt_graph_LR_Ids(self, id):
		if id != 'TOP':
			self.debugmsg(5, "id:", id)
			pid = self.report_subsection_parent(id)
			idl = pid + 'L'
			self.report_item_parent(idl)
			idr = pid + 'R'
			self.report_item_parent(idr)
			return pid, idl, idr
		else:
			return id, id + 'L', id + 'R'

	def rt_graph_get_sql(self, id):
		self.debugmsg(9, "id:", id)
		if 'SQL' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['SQL']).strip()
		else:
			return ""

	def rt_graph_set_sql(self, id, graphSQL):
		self.debugmsg(9, "id:", id, "	graphSQL:", graphSQL.strip())
		prev = self.rt_graph_get_sql(id)
		if graphSQL.strip() != prev:
			self.report[id]['SQL'] = self.whitespace_set_ini_value(graphSQL.strip())
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_graph_get_axisen(self, id):
		self.debugmsg(9, "id:", id)
		if id in self.report and 'AxisEn' in self.report[id]:
			return int(self.report[id]['AxisEn'])
		else:
			if id[-1:] == 'L':
				return 1
			else:
				return 0

	def rt_graph_set_axisen(self, id, value):
		self.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_graph_get_axisen(id)
		if value != prev and value is not None:
			self.report[id]['AxisEn'] = str(value)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_graph_get_dt(self, id):
		self.debugmsg(9, "id:", id)
		pid = self.report_subsection_parent(id)
		if 'DataType' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['DataType'])
		elif pid in self.report and 'DataType' in self.report[pid]:
			return self.whitespace_get_ini_value(self.report[pid]['DataType'])
		else:
			return None

	def rt_graph_set_dt(self, id, datatype):
		self.debugmsg(5, "id:", id, "	datatype:", datatype)
		prev = self.rt_table_get_dt(id)
		if datatype != prev and datatype is not None:
			self.report[id]['DataType'] = self.whitespace_set_ini_value(datatype)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_graph_generate_sql(self, id):
		self.debugmsg(8, "id:", id)
		sql = ""
		DataType = self.rt_table_get_dt(id)

		pid = self.report_subsection_parent(id)
		starttime = self.rt_setting_get_starttime(pid)
		self.debugmsg(5, "starttime:", starttime)
		endtime = self.rt_setting_get_endtime(pid)
		self.debugmsg(5, "endtime:", endtime)

		if DataType == "Result":
			RType = self.rt_table_get_rt(id)
			EnFR = self.rt_table_get_enfr(id)
			FRType = self.rt_table_get_fr(id)
			EnFA = self.rt_table_get_enfa(id)
			FAType = self.rt_table_get_fa(id)
			FNType = self.rt_table_get_fn(id)
			inpFP = self.rt_table_get_fp(id)
			GSeconds = self.rt_graph_get_gseconds(id)
			fltGW = self.rt_graph_get_gw(id)

			colname = "Name"

			sql = "SELECT "

			self.debugmsg(8, "RType:", RType, "sql:", sql)

			if RType == "Response Time":
				if GSeconds > 0:
					sql += "max(end_time) as 'Time' "
					if fltGW.lower() == "maximum":
						sql += ", max(elapsed_time) as 'Value' "
					elif fltGW.lower() == "minimum":
						sql += ", min(elapsed_time) as 'Value' "
					elif fltGW.lower() == "average":
						sql += ", avg(elapsed_time) as 'Value' "
					else:
						sql += ", avg(elapsed_time) as 'Value' "
				else:
					sql += "end_time as 'Time' "
					sql += ", elapsed_time as 'Value' "
				# sql += ", result_name as 'Name' "
				sql += ", result_name"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "
				# sql += 		", round(min(elapsed_time),3) 'minium' "
				# sql += 		", round(avg(elapsed_time),3) 'average' "
				# sql += 		", round(percentile(elapsed_time, {}),3) '{}%ile' ".format(display_percentile, display_percentile)
				# sql += 		", round(max(elapsed_time),3) 'maxium' "
				# sql += 		", round(stdev(elapsed_time),3) 'stdev' "
				# sql += 		", count(result) as 'count' "

				# sql += 		"round(min(rp.elapsed_time),3) 'min', "
				# sql += 		"round(avg(rp.elapsed_time),3) 'avg', "
				# sql += 		"round(percentile(rp.elapsed_time, {}),3) '{}%ile', ".format(display_percentile, display_percentile)
				# sql += 		"round(max(rp.elapsed_time),3) 'max', "
				# sql += 		"round(stdev(rp.elapsed_time),3) 'stDev', "
				# sql += 		"count(rp.result) as _pass, "
				# sql += 		"count(rf.result) as _fail, "
				# sql += 		"count(ro.result) as _other "
				# sql += "FROM Results as r "
				# sql += 		"LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == 'PASS' "
				# sql += 		"LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == 'FAIL' "
				# sql += 		"LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> 'PASS' AND ro.result <> 'FAIL' "

			if RType == "TPS":
				sql += "floor(max(end_time)) as 'Time' "
				sql += ", count(result) as 'Value' "
				# sql += ", result_name as 'Name' "
				sql += ", result_name"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "
			if RType == "Total TPS":
				sql += "floor(max(end_time)) as 'Time'"
				sql += ", count(result) as 'Value' "
				# sql += ", result as 'Name' "
				sql += ", result"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "

			if RType in [None, "", "None"]:
				self.debugmsg(8, "RType:", RType, "sql:", sql)
				sql += "end_time as 'Time'"
				sql += ", count(result) as 'Value' "
				# sql += ", result_name as 'Name' "
				sql += ", result_name"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "

			self.debugmsg(8, "RType:", RType, "sql:", sql)

			sql += "FROM Results "

			lwhere = []
			if FRType == "Pass":
				# sql += "WHERE result == 'PASS' "
				lwhere.append("result == 'PASS'")
			if FRType == "Fail":
				# sql += "WHERE result == 'FAIL' "
				lwhere.append("result == 'FAIL'")

			if EnFA and FAType not in [None, "", "None"]:
				lwhere.append("agent == '" + FAType + "'")

			if RType == "Response Time":
				# sql +=  	"AND result_name NOT LIKE 'Exception in thread%' "
				lwhere.append("[" + colname + "] NOT LIKE 'Exception in thread%'")
			if RType == "TPS":
				# sql +=  "WHERE result_name NOT LIKE 'Exception in thread%' "
				lwhere.append("[" + colname + "] NOT LIKE 'Exception in thread%'")

			if FNType not in [None, "", "None"] and len(inpFP) > 0:
				# construct pattern
				# "Wildcard (Unix Glob)",
				if FNType == "Wildcard (Unix Glob)":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] GLOB '{}'".format(inpFP))
				# "Regex",
				if FNType == "Regex":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] REGEXP '{}'".format(inpFP))
				# "Not Wildcard (Unix Glob)",
				if FNType == "Not Wildcard (Unix Glob)":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] NOT GLOB '{}'".format(inpFP))
				# "Not Regex"
				if FNType == "Not Regex":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] NOT REGEXP '{}'".format(inpFP))

			# Start Time
			if starttime > 0:
				lwhere.append("end_time >= {}".format(starttime))

			# End Time
			if endtime > 0:
				lwhere.append("end_time <= {}".format(endtime))

			i = 0
			for iwhere in lwhere:
				if i == 0:
					sql += "WHERE {} ".format(iwhere)
				else:
					sql += "AND {} ".format(iwhere)
				i += 1

			if RType not in [None, "", "None"]:
				# sql += "GROUP by "
				# sql += 		", result "
				pass
			if RType == "Response Time":
				# sql += 		"result_name "
				if GSeconds > 0:
					sql += f"GROUP BY [Name], floor(end_time/{GSeconds})"
				sql += "ORDER BY end_time"

			if RType == "TPS":
				sql += "GROUP by "
				if GSeconds > 0:
					sql += f"floor(end_time/{GSeconds}) "
				else:
					sql += "floor(end_time) "
				sql += ", result_name "
				sql += ", result "
				sql += "ORDER by "
				sql += "floor(end_time)"
				sql += ", result DESC"
				sql += ", count(result) DESC "
			if RType == "Total TPS":
				sql += "GROUP by "
				if GSeconds > 0:
					sql += f"floor(end_time/{GSeconds}) "
				else:
					sql += "floor(end_time) "
				sql += ", result "
				sql += "ORDER by "
				sql += "floor(end_time)"
				sql += ", count(result) DESC "

		if DataType == "Metric":
			MType = self.rt_table_get_mt(id)
			PM = self.rt_table_get_pm(id)
			SM = self.rt_table_get_sm(id)
			# isnum = self.rt_table_get_isnumeric(id)
			# sc = self.rt_table_get_showcount(id)
			EnFA = self.rt_table_get_enfa(id)
			FAType = self.rt_table_get_fa(id)
			FNType = self.rt_table_get_fn(id)
			inpFP = self.rt_table_get_fp(id)
			GSeconds = self.rt_graph_get_gseconds(id)
			fltGW = self.rt_graph_get_gw(id)

			colname = "Name"

			self.debugmsg(6, "MType:", MType, "	PM:", PM, "	SM:", SM)

			mnamecolumns = []
			# mcolumns = ["MetricTime as 'Time'", "MetricValue as 'Value'", "PrimaryMetric as 'Name'", "MetricType as 'Name'", "SecondaryMetric as 'Name'"]
			if GSeconds > 0:
				mcolumns = ["max(MetricTime) as 'Time'"]
				if fltGW.lower() == "maximum":
					mcolumns.append("max(MetricValue) as 'Value'")
				elif fltGW.lower() == "minimum":
					mcolumns.append("min(MetricValue) as 'Value'")
				elif fltGW.lower() == "average":
					mcolumns.append("avg(MetricValue) as 'Value'")
				else:
					mcolumns.append("avg(MetricValue) as 'Value'")

			else:
				mcolumns = ["MetricTime as 'Time'", "MetricValue as 'Value'"]
			wherelst = []
			# grouplst = ["PrimaryMetric", "MetricType", "SecondaryMetric"]
			grouplst = []

			if GSeconds > 0:
				# [Name], floor(end_time/{GSeconds})
				grouplst.append(f"[{colname}]")
				grouplst.append(f"floor(MetricTime/{GSeconds})")

			if PM not in [None, "", "None"] and len(PM) > 0:
				# if "PrimaryMetric as 'Name'" in mcolumns:
				# 	mcolumns.remove("PrimaryMetric as 'Name'")
				wherelst.append("PrimaryMetric == '{}'".format(PM.replace("'", "''")))
				if "PrimaryMetric" in grouplst:
					grouplst.remove("PrimaryMetric")
			else:
				mnamecolumns.append("PrimaryMetric")
			if MType not in [None, "", "None"] and len(MType) > 0:
				# if "MetricType as 'Name'" in mcolumns:
				# 	mcolumns.remove("MetricType as 'Name'")
				wherelst.append("MetricType == '{}'".format(MType.replace("'", "''")))
				if "MetricType" in grouplst:
					grouplst.remove("MetricType")
			else:
				mnamecolumns.append("MetricType")
			if SM not in [None, "", "None"] and len(SM) > 0:
				# if "SecondaryMetric as 'Name'" in mcolumns:
				# 	mcolumns.remove("SecondaryMetric as 'Name'")
				wherelst.append("SecondaryMetric == '{}'".format(SM.replace("'", "''")))
				if "SecondaryMetric" in grouplst:
					grouplst.remove("SecondaryMetric")
			else:
				mnamecolumns.append("SecondaryMetric")

			if EnFA:
				if FAType in [None, "", "None"]:
					mnamecolumns.append("DataSource")
				else:
					wherelst.append("DataSource == '{}'".format(FAType))

			if len(mnamecolumns) < 1:
				mnamecolumns.append("'" + SM + "'")

			# Construct Name Column
			mnamecolumn = " || ' - ' || ".join(mnamecolumns)
			mnamecolumn += " as [" + colname + "] "
			mcolumns.append(mnamecolumn)

			if FNType not in [None, "", "None"] and len(inpFP) > 0:
				# construct pattern
				# "Wildcard (Unix Glob)",
				if FNType == "Wildcard (Unix Glob)":
					# AND PrimaryMetric GLOB '*_1*' OR SecondaryMetric GLOB '*_1*' OR DataSource GLOB '*_1*' OR MetricValue GLOB '*_1*'
					self.debugmsg(5, "mnamecolumns:", mnamecolumns)
					fpwhere = "("
					for dispcol in mnamecolumns:
						if len(fpwhere) > 1:
							fpwhere += "OR "
						fpwhere += "{} GLOB '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)
				# "Regex",
				if FNType == "Regex":
					fpwhere = "("
					for dispcol in mnamecolumns:
						if len(fpwhere) > 1:
							fpwhere += "OR "
						fpwhere += "{} REGEXP '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)
				# "Not Wildcard (Unix Glob)",
				if FNType == "Not Wildcard (Unix Glob)":
					fpwhere = "("
					for dispcol in mnamecolumns:
						if len(fpwhere) > 1:
							fpwhere += "AND "
						fpwhere += "{} NOT GLOB '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)
				# "Not Regex"
				if FNType == "Not Regex":
					fpwhere = "("
					for dispcol in mnamecolumns:
						if len(fpwhere) > 1:
							fpwhere += "AND "
						fpwhere += "{} NOT REGEXP '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)

			# Start Time
			if starttime > 0:
				wherelst.append("MetricTime >= {}".format(starttime))

			# End Time
			if endtime > 0:
				wherelst.append("MetricTime <= {}".format(endtime))

			# if isnum<1:
			# 	mcolumns.append("MetricValue")
			# 	if sc>0:
			# 		mcolumns.append("count(MetricTime) as 'Count'")
			# 		if "MetricValue" in grouplst:
			# 			grouplst.remove("MetricValue")
			# else:
			# 	mcolumns.append("min(CAST(MetricValue AS NUMERIC)) AS 'Minimum'")
			# 	mcolumns.append("round(avg(CAST(MetricValue AS NUMERIC)),3) AS 'Average'")
			# 	mcolumns.append("round(percentile(CAST(MetricValue AS NUMERIC), {}),3) AS '{}%ile'".format(display_percentile, display_percentile))
			# 	mcolumns.append("max(CAST(MetricValue AS NUMERIC)) AS 'Maximum'")
			# 	mcolumns.append("round(stdev(CAST(MetricValue AS NUMERIC)),3) AS 'StdDev'")

			sql = "SELECT "

			i = 0
			for col in mcolumns:
				if i < 1:
					sql += "{} ".format(col)
				else:
					sql += ", {} ".format(col)
				i += 1

			sql += "FROM MetricData "

			i = 0
			for iwhere in wherelst:
				if i == 0:
					sql += "WHERE {} ".format(iwhere)
				else:
					sql += "AND {} ".format(iwhere)
				i += 1

			if len(grouplst) > 0:
				sql += "GROUP by "
				i = 0
				for col in grouplst:
					if i < 1:
						sql += "{} ".format(col)
					else:
						sql += ", {} ".format(col)
					i += 1

			sql += "ORDER BY MetricTime "

		if DataType == "Plan":
			sql = "SELECT "
			sql += "md1.* "
			sql += ", md0.SecondaryMetric as [File] "
			sql += ", fp0.SecondaryMetric as [FilePath] "
			# sql += ", concat(fp0.SecondaryMetric, " ", md0.MetricValue ) as [ColourKey] "
			sql += "FROM MetricData as md0 "
			sql += "LEFT JOIN MetricData as fp0 "
			sql += "ON fp0.MetricValue = md0.MetricValue "
			sql += "AND fp0.MetricType = 'Scenario' "
			sql += "AND fp0.PrimaryMetric like 'Local_Path_%' "
			sql += "LEFT JOIN MetricData as md1 "
			sql += "ON md1.SecondaryMetric = md0.MetricValue "
			sql += "AND md1.MetricType = 'Scenario' "
			sql += "WHERE md0.MetricType = 'Scenario' "
			sql += "AND md0.PrimaryMetric like 'Test_%' "
			sql += "AND md0.PrimaryMetric not like 'Test_m%' "

		if DataType == "Monitoring":
			sql = "SELECT "
			sql += "md1.* "
			sql += ", md0.SecondaryMetric as [File] "
			sql += ", fp0.SecondaryMetric as [FilePath] "
			# sql += ", concat(fp0.SecondaryMetric, " ", md0.MetricValue ) as [ColourKey] "
			sql += "FROM MetricData as md0 "
			sql += "LEFT JOIN MetricData as fp0 "
			sql += "ON fp0.MetricValue = md0.MetricValue "
			sql += "AND fp0.MetricType = 'Scenario' "
			sql += "AND fp0.PrimaryMetric like 'Local_Path_%' "
			sql += "LEFT JOIN MetricData as md1 "
			sql += "ON md1.SecondaryMetric = md0.MetricValue "
			sql += "AND md1.MetricType = 'Scenario' "
			sql += "WHERE md0.MetricType = 'Scenario' "
			sql += "AND md0.PrimaryMetric like 'Test_m%' "

		self.debugmsg(5, "sql:", sql)
		self.rt_graph_set_sql(id, sql)
		return sql

	def rt_graph_floatval(self, value):
		try:
			return float(value)
		except Exception:
			return value

	# GSeconds Granularity Seconds
	def rt_graph_get_gseconds(self, id):
		value = self.report_item_get_float(id, "GSeconds")
		if value < 0:
			return 0
		else:
			return value

	def rt_graph_set_gseconds(self, id, value):
		changes = self.report_item_set_float(id, "GSeconds", float(value))
		return changes

	# GW Granularity shoW mode
	def rt_graph_get_gw(self, id):
		value = self.report_item_get_value(id, "GWType")
		if value is None:
			return "Average"
		else:
			return value

	def rt_graph_set_gw(self, id, value):
		changes = self.report_item_set_float(id, "GWType", value)
		return changes

	#
	# Report Item Type: table
	#

	def rt_table_get_sql(self, id):
		self.debugmsg(9, "id:", id)
		if 'SQL' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['SQL']).strip()
		else:
			return ""

	def rt_table_set_sql(self, id, tableSQL):
		self.debugmsg(8, "id:", id, "	tableSQL:", tableSQL.strip())
		prev = self.rt_table_get_sql(id)
		if tableSQL.strip() != prev:
			self.report[id]['SQL'] = self.whitespace_set_ini_value(tableSQL.strip())
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_generate_sql(self, id):
		self.debugmsg(8, "id:", id)
		display_percentile = self.rs_setting_get_pctile()
		sql = ""
		DataType = self.rt_table_get_dt(id)

		starttime = self.rt_setting_get_starttime(id)
		endtime = self.rt_setting_get_endtime(id)

		if DataType == "Monitoring":
			sql = "SELECT "
			sql += "md1.* "
			sql += ", md0.SecondaryMetric as [File] "
			sql += ", fp0.SecondaryMetric as [FilePath] "
			# sql += ", concat(fp0.SecondaryMetric, " ", md0.MetricValue ) as [ColourKey] "
			sql += "FROM MetricData as md0 "
			sql += "LEFT JOIN MetricData as fp0 "
			sql += "ON fp0.MetricValue = md0.MetricValue "
			sql += "AND fp0.MetricType = 'Scenario' "
			sql += "AND fp0.PrimaryMetric like 'Local_Path_%' "
			sql += "LEFT JOIN MetricData as md1 "
			sql += "ON md1.SecondaryMetric = md0.MetricValue "
			sql += "AND md1.MetricType = 'Scenario' "
			sql += "WHERE md0.MetricType = 'Scenario' "
			sql += "AND md0.PrimaryMetric like 'Test_m%' "

		if DataType == "Plan":
			sql = "SELECT "
			sql += "md1.* "
			sql += ", md0.SecondaryMetric as [File] "
			sql += ", fp0.SecondaryMetric as [FilePath] "
			# sql += ", concat(fp0.SecondaryMetric, " ", md0.MetricValue ) as [ColourKey] "
			sql += "FROM MetricData as md0 "
			sql += "LEFT JOIN MetricData as fp0 "
			sql += "ON fp0.MetricValue = md0.MetricValue "
			sql += "AND fp0.MetricType = 'Scenario' "
			sql += "AND fp0.PrimaryMetric like 'Local_Path_%' "
			sql += "LEFT JOIN MetricData as md1 "
			sql += "ON md1.SecondaryMetric = md0.MetricValue "
			sql += "AND md1.MetricType = 'Scenario' "
			sql += "WHERE md0.MetricType = 'Scenario' "
			sql += "AND md0.PrimaryMetric like 'Test_%' "
			sql += "AND md0.PrimaryMetric not like 'Test_m%' "

		if DataType == "Result":
			RType = self.rt_table_get_rt(id)
			EnFR = self.rt_table_get_enfr(id)
			FRType = self.rt_table_get_fr(id)
			EnFA = self.rt_table_get_enfa(id)
			FAType = self.rt_table_get_fa(id)
			FNType = self.rt_table_get_fn(id)
			inpFP = self.rt_table_get_fp(id)
			colname = "Result Name"

			sql = "SELECT "
			if RType == "Response Time":
				sql += "result_name"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "
				sql += ", round(min(elapsed_time),3) 'Minimum' "
				sql += ", round(avg(elapsed_time),3) 'Average' "
				sql += ", round(percentile(elapsed_time, {}),3) '{}%ile' ".format(display_percentile, display_percentile)
				sql += ", round(max(elapsed_time),3) 'Maximum' "
				sql += ", round(stdev(elapsed_time),3) 'Std. Dev.' "
				sql += ", count(result) as 'Count' "

				# sql += 		"round(min(rp.elapsed_time),3) 'min', "
				# sql += 		"round(avg(rp.elapsed_time),3) 'avg', "
				# sql += 		"round(percentile(rp.elapsed_time, {}),3) '{}%ile', ".format(display_percentile, display_percentile)
				# sql += 		"round(max(rp.elapsed_time),3) 'max', "
				# sql += 		"round(stdev(rp.elapsed_time),3) 'stDev', "
				# sql += 		"count(rp.result) as _pass, "
				# sql += 		"count(rf.result) as _fail, "
				# sql += 		"count(ro.result) as _other "
				# sql += "FROM Results as r "
				# sql += 		"LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == 'PASS' "
				# sql += 		"LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == 'FAIL' "
				# sql += 		"LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> 'PASS' AND ro.result <> 'FAIL' "

			if RType == "TPS":
				sql += "result_name"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "
				sql += ", result 'Result' "
				sql += ", count(result)  as 'Count' "
			if RType == "Total TPS":
				colname = "Result "
				sql += "result "
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "
				sql += ", count(result)  as 'Count' "
			if RType in [None, "", "None"]:
				sql = ""
				return sql

			sql += "FROM Results "

			lwhere = []
			if EnFR:
				if FRType == "Pass":
					# sql += "WHERE result == 'PASS' "
					lwhere.append("result == 'PASS'")
				if FRType == "Fail":
					# sql += "WHERE result == 'FAIL' "
					lwhere.append("result == 'FAIL'")

			if EnFA and FAType not in [None, "", "None"]:
				lwhere.append("agent == '" + FAType + "'")

			if RType == "Response Time":
				# sql +=  	"AND result_name NOT LIKE 'Exception in thread%' "
				lwhere.append("[" + colname + "] NOT LIKE 'Exception in thread%'")
			if RType == "TPS":
				# sql +=  "WHERE result_name NOT LIKE 'Exception in thread%' "
				lwhere.append("[" + colname + "] NOT LIKE 'Exception in thread%'")

			if FNType not in [None, "", "None"] and len(inpFP) > 0:
				# construct pattern
				# "Wildcard (Unix Glob)",
				if FNType == "Wildcard (Unix Glob)":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] GLOB '{}'".format(inpFP))
				# "Regex",
				if FNType == "Regex":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] REGEXP '{}'".format(inpFP))
				# "Not Wildcard (Unix Glob)",
				if FNType == "Not Wildcard (Unix Glob)":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] NOT GLOB '{}'".format(inpFP))
				# "Not Regex"
				if FNType == "Not Regex":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] NOT REGEXP '{}'".format(inpFP))

			# Start Time
			if starttime > 0:
				lwhere.append("end_time >= {}".format(starttime))

			# End Time
			if endtime > 0:
				lwhere.append("end_time <= {}".format(endtime))

			i = 0
			for iwhere in lwhere:
				if i == 0:
					sql += "WHERE {} ".format(iwhere)
				else:
					sql += "AND {} ".format(iwhere)
				i += 1

			if RType not in [None, "", "None"]:
				sql += "GROUP by "

			if RType == "Response Time":
				sql += "[" + colname + "] "
			if RType == "TPS":
				sql += "[" + colname + "] "
				sql += ", result "
				sql += "ORDER BY "
				sql += "result DESC"
				sql += ", count(result) DESC "
			if RType == "Total TPS":
				sql += " [" + colname + "] "
				sql += "ORDER BY "
				sql += "count([" + colname + "]) DESC "

		if DataType == "Metric":
			MType = self.rt_table_get_mt(id)
			PM = self.rt_table_get_pm(id)
			SM = self.rt_table_get_sm(id)
			isnum = self.rt_table_get_isnumeric(id)
			sc = self.rt_table_get_showcount(id)
			EnFA = self.rt_table_get_enfa(id)
			FAType = self.rt_table_get_fa(id)
			FNType = self.rt_table_get_fn(id)
			inpFP = self.rt_table_get_fp(id)

			colours = self.rt_table_get_colours(id)

			self.debugmsg(8, "MType:", MType, "	PM:", PM, "	SM:", SM)

			mcolumns = ["PrimaryMetric", "MetricType", "SecondaryMetric"]
			wherelst = []
			grouplst = ["PrimaryMetric", "MetricType", "SecondaryMetric"]

			if EnFA:
				if FAType in [None, "", "None"]:
					mcolumns.append("DataSource 'Agent'")
					grouplst.append("DataSource")
				else:
					wherelst.append("DataSource == '{}'".format(FAType))

			if MType not in [None, "", "None"] and len(MType) > 0:
				if "MetricType" in mcolumns:
					mcolumns.remove("MetricType")
				wherelst.append("MetricType == '{}'".format(MType))
				if "MetricType" in grouplst:
					grouplst.remove("MetricType")
			if PM not in [None, "", "None"] and len(PM) > 0:
				if "PrimaryMetric" in mcolumns:
					mcolumns.remove("PrimaryMetric")
				wherelst.append("PrimaryMetric == '{}'".format(PM))
				if "PrimaryMetric" in grouplst:
					grouplst.remove("PrimaryMetric")
			if SM not in [None, "", "None"] and len(SM) > 0:
				if "SecondaryMetric" in mcolumns:
					mcolumns.remove("SecondaryMetric")
				wherelst.append("SecondaryMetric == '{}'".format(SM))
				if "SecondaryMetric" in grouplst:
					grouplst.remove("SecondaryMetric")

			if len(mcolumns) < 1:
				# mcolumns.append("'" + SM + "'")
				mcolumns.append("SecondaryMetric")
				grouplst.append("SecondaryMetric")

			if colours:
				colourcolumn = " || ' - ' || ".join(grouplst)
				colourcolumn += " as [Colour] "
				mcolumns.append(colourcolumn)

			if FNType not in [None, "", "None"] and len(inpFP) > 0:
				# construct pattern
				# "Wildcard (Unix Glob)",
				if FNType == "Wildcard (Unix Glob)":
					# AND PrimaryMetric GLOB '*_1*' OR SecondaryMetric GLOB '*_1*' OR DataSource GLOB '*_1*' OR MetricValue GLOB '*_1*'
					fpwhere = "("
					for dispcol in grouplst:
						if len(fpwhere) > 1:
							fpwhere += "OR "
						fpwhere += "{} GLOB '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)
				# "Regex",
				if FNType == "Regex":
					fpwhere = "("
					for dispcol in grouplst:
						if len(fpwhere) > 1:
							fpwhere += "OR "
						fpwhere += "{} REGEXP '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)
				# "Not Wildcard (Unix Glob)",
				if FNType == "Not Wildcard (Unix Glob)":
					fpwhere = "("
					for dispcol in grouplst:
						if len(fpwhere) > 1:
							fpwhere += "AND "
						fpwhere += "{} NOT GLOB '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)
				# "Not Regex"
				if FNType == "Not Regex":
					fpwhere = "("
					for dispcol in grouplst:
						if len(fpwhere) > 1:
							fpwhere += "AND "
						fpwhere += "{} NOT REGEXP '{}'".format(dispcol, inpFP)
					fpwhere += ")"
					wherelst.append(fpwhere)

			if isnum < 1:
				mcolumns.append("MetricValue")
				if sc > 0:
					mcolumns.append("count(MetricTime) as 'Count'")
					if "MetricValue" in grouplst:
						grouplst.remove("MetricValue")
			else:
				mcolumns.append("min(CAST(MetricValue AS NUMERIC)) AS 'Minimum'")
				mcolumns.append("round(avg(CAST(MetricValue AS NUMERIC)),3) AS 'Average'")
				mcolumns.append("round(percentile(CAST(MetricValue AS NUMERIC), {}),3) AS '{}%ile'".format(display_percentile, display_percentile))
				mcolumns.append("max(CAST(MetricValue AS NUMERIC)) AS 'Maximum'")
				mcolumns.append("round(stdev(CAST(MetricValue AS NUMERIC)),3) AS 'Std. Dev.'")

			# Start Time
			if starttime > 0:
				wherelst.append("MetricTime >= {}".format(starttime))

			# End Time
			if endtime > 0:
				wherelst.append("MetricTime <= {}".format(endtime))

			sql = "SELECT "

			i = 0
			for col in mcolumns:
				if i < 1:
					sql += "{} ".format(col)
				else:
					sql += ", {} ".format(col)
				i += 1

			sql += "FROM MetricData "

			i = 0
			for iwhere in wherelst:
				if i == 0:
					sql += "WHERE {} ".format(iwhere)
				else:
					sql += "AND {} ".format(iwhere)
				i += 1

			if len(grouplst) > 0:
				sql += "GROUP by "
				i = 0
				for col in grouplst:
					if i < 1:
						sql += "{} ".format(col)
					else:
						sql += ", {} ".format(col)
					i += 1

		if DataType == "ResultSummary":
			EnFA = self.rt_table_get_enfa(id)
			FAType = self.rt_table_get_fa(id)
			FNType = self.rt_table_get_fn(id)
			inpFP = self.rt_table_get_fp(id)

			# sql = "SELECT "
			# sql += 		"Name "
			# sql += 		", Min "
			# sql += 		", Average "
			# sql += 		", StDev "
			# sql += 		", [%ile_Value] rs.[%ile_Key] "
			# sql += 		", Pass "
			# sql += 		", Fail "
			# sql += 		", Other "
			# sql += "FROM ResultSummary rs "

			sellist = []
			gblist = []
			colname = "Result Name"
			col0 = "r.result_name"
			if EnFA and FAType in [None, "", "None"]:
				col0 += " || ' - ' || r.agent"
			col0 += " as [" + colname + "] "

			sellist.append(col0)
			gblist.append("r.result_name")
			self.debugmsg(8, "gblist:", gblist)

			selcols = ", ".join(sellist)
			gbcols = ", ".join(gblist)

			self.debugmsg(8, "gbcols:", gbcols)

			sql = "SELECT "
			if len(selcols) > 0:
				sql += selcols
				sql += ", "
			sql += "round(min(rp.elapsed_time),3) 'Minimum', "
			sql += "round(avg(rp.elapsed_time),3) 'Average', "
			sql += "round(percentile(rp.elapsed_time, {}),3) '{}%ile', ".format(display_percentile, display_percentile)
			sql += "round(max(rp.elapsed_time),3) 'Maximum', "
			sql += "round(stdev(rp.elapsed_time),3) 'Std. Dev.', "
			sql += "count(rp.result) as 'Pass', "
			sql += "count(rf.result) as 'Fail', "
			sql += "count(ro.result) as 'Other' "
			sql += "FROM Results as r "
			sql += "LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == 'PASS' "
			sql += "LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == 'FAIL' "
			sql += "LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> 'PASS' AND ro.result <> 'FAIL' "

			lwhere = []
			if EnFA and FAType not in [None, "", "None"]:
				lwhere.append("r.agent == '{}'".format(FAType))

			if FNType != "None" and len(inpFP) > 0:
				# construct pattern
				# "Wildcard (Unix Glob)",
				if FNType == "Wildcard (Unix Glob)":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] GLOB '{}'".format(inpFP))
				# "Regex",
				if FNType == "Regex":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] REGEXP '{}'".format(inpFP))
				# "Not Wildcard (Unix Glob)",
				if FNType == "Not Wildcard (Unix Glob)":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] NOT GLOB '{}'".format(inpFP))
				# "Not Regex"
				if FNType == "Not Regex":
					# -- 		WHERE result_name GLOB 'OC3*'
					lwhere.append("[" + colname + "] NOT REGEXP '{}'".format(inpFP))

			# Start Time
			if starttime > 0:
				lwhere.append("r.end_time >= {}".format(starttime))

			# End Time
			if endtime > 0:
				lwhere.append("r.end_time <= {}".format(endtime))

			i = 0
			for iwhere in lwhere:
				if i == 0:
					sql += "WHERE {} ".format(iwhere)
				else:
					sql += "AND {} ".format(iwhere)
				i += 1

			if len(gblist) > 0:
				sql += "GROUP BY  "
				sql += gbcols

			sql += " ORDER BY [" + colname + "]"

		self.debugmsg(8, "sql:", sql)
		self.rt_table_set_sql(id, sql)
		return sql

	def rt_table_get_colours(self, id):
		self.debugmsg(9, "id:", id)
		if 'Colours' in self.report[id]:
			return int(self.report[id]['Colours'])
		else:
			self.rt_table_set_colours(id, 0)
			return 0

	def rt_table_set_colours(self, id, colours):
		self.debugmsg(5, "id:", id, "	colours:", colours)
		if 'Colours' not in self.report[id]:
			self.report[id]['Colours'] = self.whitespace_set_ini_value(str(colours))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		else:
			prev = self.rt_table_get_colours(id)
			if colours != prev:
				self.report[id]['Colours'] = self.whitespace_set_ini_value(str(colours))
				self.report_item_set_changed(id)
				self.report_save()
				return 1
		return 0

	# 	rt_setting_get_starttime
	def rt_setting_get_starttime(self, id):
		# value = self.rs_setting_get_int('startoffset')
		value = self.report_item_get_int(id, 'startoffset')
		self.debugmsg(5, "value:", value)
		if value < 1:
			return self.rs_setting_get_starttime()
		else:
			return self.rs_setting_get_starttime() + int(value)

	def rt_setting_get_endtime(self, id):
		# value = self.rs_setting_get_int('endoffset')
		value = self.report_item_get_int(id, 'endoffset')
		self.debugmsg(5, "value:", value)
		if value < 1:
			return self.rs_setting_get_endtime()
		else:
			return self.rs_setting_get_endtime() - int(value)

	def rt_table_get_dt(self, id):
		self.debugmsg(9, "id:", id)
		# report_subsection_parent
		if id in self.report and 'DataType' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['DataType'])
		else:
			return None

	def rt_table_set_dt(self, id, datatype):
		self.debugmsg(9, "id:", id, "	datatype:", datatype)
		prev = self.rt_table_get_dt(id)
		self.debugmsg(8, "prev:", prev)
		if datatype != prev and datatype is not None:
			self.report[id]['DataType'] = self.whitespace_set_ini_value(datatype)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_rt(self, id):
		self.debugmsg(9, "id:", id)
		if 'ResultType' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['ResultType'])
		else:
			return None

	def rt_table_set_rt(self, id, resulttype):
		self.debugmsg(9, "id:", id, "	resulttype:", resulttype)
		prev = self.rt_table_get_rt(id)
		if resulttype != prev and resulttype is not None:
			self.report[id]['ResultType'] = self.whitespace_set_ini_value(resulttype)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_ini_colname(self, name):
		self.debugmsg(5, "id:", id, "	name:", name)
		colname = "col_{}".format(self.whitespace_set_ini_value(name)).replace(" ", "_").replace(".", "")
		self.debugmsg(5, "colname:", colname)
		return colname

	def rt_table_get_colname(self, id, name):
		self.debugmsg(5, "id:", id, "	name:", name)
		colname = self.rt_table_ini_colname(name)
		if colname in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id][colname])
		else:
			return name

	def rt_table_set_colname(self, id, name, value):
		self.debugmsg(5, "id:", id, "	name:", name, "	value:", value)
		colname = self.rt_table_ini_colname(name)
		prev = self.rt_table_get_colname(id, name)
		if value != prev and value not in [None, ""]:
			self.report[id][colname] = self.whitespace_set_ini_value(value)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		if value in [None, ""]:
			self.report[id][colname] = self.whitespace_set_ini_value(name)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_fr(self, id):
		self.debugmsg(9, "id:", id)
		if 'FilterResult' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['FilterResult'])
		else:
			return None

	def rt_table_set_fr(self, id, filterresult):
		self.debugmsg(9, "id:", id, "	filterresult:", filterresult)
		prev = self.rt_table_get_fr(id)
		if filterresult != prev and filterresult is not None:
			self.report[id]['FilterResult'] = self.whitespace_set_ini_value(filterresult)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_enfr(self, id):
		self.debugmsg(5, "id:", id)
		pid = self.report_subsection_parent(id)
		if id in self.report and 'EnableFilterResult' in self.report[id]:
			return int(self.report[id]['EnableFilterResult'])
		elif pid in self.report and 'EnableFilterResult' in self.report[pid]:
			return int(self.report[pid]['EnableFilterResult'])
		else:
			frv = self.rt_table_get_fr(id)
			if frv in ["Pass", "Fail"]:
				return 1
			return 0

	def rt_table_set_enfr(self, id, value):
		self.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_enfr(id)
		if value != prev and value is not None:
			self.report[id]['EnableFilterResult'] = self.whitespace_set_ini_value(str(value))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	# FA FilterAgent
	def rt_table_get_fa(self, id):
		self.debugmsg(5, "id:", id)
		if 'FilterAgent' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['FilterAgent'])
		else:
			return None

	def rt_table_set_fa(self, id, value):
		self.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_fa(id)
		if value != prev and value is not None:
			self.report[id]['FilterAgent'] = self.whitespace_set_ini_value(value)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_alst(self, id):
		self.debugmsg(9, "id:", id)
		# SELECT agent
		# FROM Results
		# GROUP BY agent
		mtype = self.rt_table_get_mt(id)
		alst = [None, ""]
		sql = "SELECT agent 'Name' "
		sql += "FROM Results "
		sql += "GROUP BY agent "
		self.debugmsg(6, "sql:", sql)
		key = "{}_{}_AgentList".format(id, mtype)
		self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in self.dbqueue["ReadResult"]:
			time.sleep(0.1)

		adata = self.dbqueue["ReadResult"][key]
		self.debugmsg(8, "adata:", adata)
		for a in adata:
			alst.append(a["Name"])

		self.debugmsg(5, "alst:", alst)

		return alst

	def rt_table_get_malst(self, id):
		self.debugmsg(9, "id:", id)
		# SELECT agent
		# FROM Results
		# GROUP BY agent
		mtype = self.rt_table_get_mt(id)
		alst = [None, ""]

		sql = "SELECT ma.Name  'Name' "
		sql += "FROM Metrics m "
		sql += "	LEFT JOIN Metric ma ON m.DataSource = ma.ID "
		sql += "GROUP BY m.DataSource "

		self.debugmsg(6, "sql:", sql)
		key = "{}_{}_MetricAgentList".format(id, mtype)
		self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in self.dbqueue["ReadResult"]:
			time.sleep(0.1)

		adata = self.dbqueue["ReadResult"][key]
		self.debugmsg(8, "adata:", adata)
		for a in adata:
			alst.append(a["Name"])

		self.debugmsg(5, "alst:", alst)

		return alst

	def rt_table_get_enfa(self, id):
		self.debugmsg(5, "id:", id)
		pid = self.report_subsection_parent(id)
		if id in self.report and 'EnableFilterAgent' in self.report[id]:
			return int(self.report[id]['EnableFilterAgent'])
		elif pid in self.report and 'EnableFilterAgent' in self.report[pid]:
			return int(self.report[pid]['EnableFilterAgent'])
		else:
			return 0

	def rt_table_set_enfa(self, id, value):
		self.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_enfa(id)
		if value != prev and value is not None:
			self.report[id]['EnableFilterAgent'] = self.whitespace_set_ini_value(str(value))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	# FN FilterType
	def rt_table_get_fn(self, id):
		self.debugmsg(9, "id:", id)
		if 'FilterType' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['FilterType'])
		else:
			return None

	def rt_table_set_fn(self, id, filtertype):
		self.debugmsg(5, "id:", id, "	filtertype:", filtertype)
		prev = self.rt_table_get_fr(id)
		if filtertype != prev and filtertype not in [None, "None"]:
			self.report[id]['FilterType'] = self.whitespace_set_ini_value(filtertype)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		elif filtertype != prev and filtertype in [None, "None"] and prev in [None, "None"]:
			self.report[id]['FilterType'] = self.whitespace_set_ini_value(None)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	# FP FilterPattern
	def rt_table_get_fp(self, id):
		self.debugmsg(9, "id:", id)
		if 'FilterPattern' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['FilterPattern'])
		else:
			return ""

	def rt_table_set_fp(self, id, filterpattern):
		self.debugmsg(5, "id:", id, "	filterpattern:", filterpattern)
		prev = self.rt_table_get_fp(id)
		if filterpattern != prev and filterpattern is not None:
			self.report[id]['FilterPattern'] = self.whitespace_set_ini_value(filterpattern)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	# mt MetricType
	def rt_table_get_mt(self, id):
		self.debugmsg(9, "id:", id)
		pid = self.report_subsection_parent(id)
		if 'MetricType' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['MetricType'])
		elif pid in self.report and 'MetricType' in self.report[pid]:
			return self.whitespace_get_ini_value(self.report[pid]['MetricType'])
		else:
			return ""

	def rt_table_set_mt(self, id, metrictype):
		self.debugmsg(5, "id:", id, "	metrictype:", metrictype)
		prev = self.rt_table_get_mt(id)
		if metrictype != prev and metrictype is not None:
			self.report[id]['MetricType'] = self.whitespace_set_ini_value(metrictype)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_mlst(self, id):
		self.debugmsg(9, "id:", id)
		mlst = [None, ""]
		sql = "SELECT Type "
		sql += "FROM Metric "
		sql += "GROUP BY Type "
		self.debugmsg(6, "sql:", sql)
		key = "{}_Metrics".format(id)
		self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in self.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = self.dbqueue["ReadResult"][key]
		self.debugmsg(8, "tdata:", tdata)
		for m in tdata:
			mlst.append(m["Type"])

		return mlst

	# pm PrimaryMetric
	def rt_table_get_pm(self, id):
		self.debugmsg(9, "id:", id)
		pid = self.report_subsection_parent(id)
		if 'PrimaryMetric' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['PrimaryMetric'])
		elif pid in self.report and 'PrimaryMetric' in self.report[pid]:
			return self.whitespace_get_ini_value(self.report[pid]['PrimaryMetric'])
		else:
			return ""

	def rt_table_set_pm(self, id, primarymetric):
		self.debugmsg(5, "id:", id, "	primarymetric:", primarymetric)
		prev = self.rt_table_get_pm(id)
		if primarymetric != prev and primarymetric is not None:
			self.report[id]['PrimaryMetric'] = self.whitespace_set_ini_value(primarymetric)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_pmlst(self, id):
		self.debugmsg(9, "id:", id)
		# SELECT Name
		# FROM Metric
		# -- WHERE Type = 'Agent'
		# GROUP BY Name
		mtype = self.rt_table_get_mt(id)
		pmlst = [None, ""]
		sql = "SELECT Name "
		sql += "FROM Metric "
		if mtype is not None and len(mtype) > 0:
			sql += "WHERE Type = '{}' ".format(mtype)
		sql += "GROUP BY Name "
		self.debugmsg(6, "sql:", sql)
		key = "{}_{}_PMetrics".format(id, mtype)
		self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in self.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = self.dbqueue["ReadResult"][key]
		self.debugmsg(8, "tdata:", tdata)
		for m in tdata:
			pmlst.append(m["Name"])

		self.debugmsg(5, "pmlst:", pmlst)

		return pmlst

	# sm SecondaryMetric
	def rt_table_get_sm(self, id):
		self.debugmsg(9, "id:", id)
		pid = self.report_subsection_parent(id)
		if 'SecondaryMetric' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['SecondaryMetric'])
		elif pid in self.report and 'SecondaryMetric' in self.report[pid]:
			return self.whitespace_get_ini_value(self.report[pid]['SecondaryMetric'])
		else:
			return ""

	def rt_table_set_sm(self, id, secondarymetric):
		self.debugmsg(5, "id:", id, "	secondarymetric:", secondarymetric)
		prev = self.rt_table_get_sm(id)
		if secondarymetric != prev and secondarymetric is not None:
			self.report[id]['SecondaryMetric'] = self.whitespace_set_ini_value(secondarymetric)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_smlst(self, id):
		self.debugmsg(9, "id:", id)
		# SELECT SecondaryMetric
		# FROM MetricData
		# -- WHERE MetricType = 'Agent'
		# -- 	AND PrimaryMetric = 'DavesMBPSG'
		# GROUP BY SecondaryMetric
		wherelst = []
		mtype = self.rt_table_get_mt(id)
		if mtype is not None and len(mtype) > 0:
			wherelst.append({"key": "MetricType", "value": mtype})

		pmtype = self.rt_table_get_pm(id)
		if pmtype is not None and len(pmtype) > 0:
			wherelst.append({"key": "PrimaryMetric", "value": pmtype})

		smlst = [None, ""]
		sql = "SELECT SecondaryMetric "
		sql += "FROM MetricData "

		# if mtype is not None and len(mtype)>0:
		# 	sql += "WHERE Type = '{}' ".format("Agent")
		i = 0
		for itm in wherelst:
			if i < 1:
				sql += "WHERE {} = '{}' ".format(itm["key"], itm["value"])
				i += 1
			else:
				sql += "AND {} = '{}' ".format(itm["key"], itm["value"])

		sql += "GROUP BY SecondaryMetric "
		self.debugmsg(6, "sql:", sql)
		key = "{}_{}_{}_SMetrics".format(id, mtype, pmtype)
		self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in self.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = self.dbqueue["ReadResult"][key]
		self.debugmsg(8, "tdata:", tdata)
		for m in tdata:
			smlst.append(m["SecondaryMetric"])

		self.debugmsg(5, "smlst:", smlst)

		return smlst

	def rt_table_get_isnumeric(self, id):
		self.debugmsg(9, "id:", id)
		pid = self.report_subsection_parent(id)
		if id in self.report and 'IsNumeric' in self.report[id]:
			return int(self.report[id]['IsNumeric'])
		elif pid in self.report and 'IsNumeric' in self.report[pid]:
			return int(self.report[pid]['IsNumeric'])
		else:
			return 0

	def rt_table_set_isnumeric(self, id, value):
		self.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_isnumeric(id)
		if value != prev and value is not None:
			self.report[id]['IsNumeric'] = self.whitespace_set_ini_value(str(value))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_table_get_showcount(self, id):
		self.debugmsg(9, "id:", id)
		pid = self.report_subsection_parent(id)
		if id in self.report and 'ShowCount' in self.report[id]:
			return int(self.report[id]['ShowCount'])
		elif pid in self.report and 'ShowCount' in self.report[pid]:
			return int(self.report[pid]['ShowCount'])
		else:
			return 0

	def rt_table_set_showcount(self, id, value):
		self.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_showcount(id)
		if value != prev and value is not None:
			self.report[id]['ShowCount'] = self.whitespace_set_ini_value(str(value))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	#
	# Report Item Type: errors
	#

	def rt_errors_get_sql(self, id):
		self.debugmsg(9, "id:", id)
		if 'SQL' in self.report[id]:
			return self.whitespace_get_ini_value(self.report[id]['SQL']).strip()
		else:
			return ""

	def rt_errors_set_sql(self, id, tableSQL):
		self.debugmsg(8, "id:", id, "	tableSQL:", tableSQL.strip())
		prev = self.rt_table_get_sql(id)
		if tableSQL.strip() != prev:
			self.report[id]['SQL'] = self.whitespace_set_ini_value(tableSQL.strip())
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	def rt_errors_generate_sql(self, id):
		self.debugmsg(8, "id:", id)

		starttime = self.rt_setting_get_starttime(id)
		endtime = self.rt_setting_get_endtime(id)

		sql = ""

		sql += "SELECT "
		sql += "r.script_index || '_' || r.robot || '_' || r.iteration || '_' || r.sequence 'id' "
		sql += ", r.result_name "
		sql += ", r.script_index "
		sql += ", r.robot "
		sql += ", r.iteration "
		sql += ", r.sequence "
		# sql += ", r.* "
		sql += ", mt.SecondaryMetric 'script' "
		sql += ", mt.MetricValue 'test_name' "
		# sql += ", mt.* "
		sql += "FROM Results r "
		sql += "LEFT JOIN MetricData mt on mt.PrimaryMetric = r.script_index AND mt.MetricType = 'Scenario_Test' "
		sql += "WHERE r.result = 'FAIL' "

		# Start Time
		if starttime > 0:
			sql += "AND r.end_time >= {} ".format(starttime)
		# End Time
		if endtime > 0:
			sql += "AND r.end_time <= {} ".format(endtime)

		# sql += "ORDER BY r.script_index, r.sequence "
		sql += "ORDER BY [id] ASC "

		self.debugmsg(8, "sql:", sql)
		self.rt_errors_set_sql(id, sql)
		return sql

	def rt_errors_get_images(self, id):
		self.debugmsg(9, "id:", id)
		if 'Images' in self.report[id]:
			return int(self.report[id]['Images'])
		else:
			self.rt_errors_set_images(id, 1)
			return 1

	def rt_errors_set_images(self, id, images):
		self.debugmsg(5, "id:", id, "	images:", images)
		if 'Images' not in self.report[id]:
			self.report[id]['Images'] = self.whitespace_set_ini_value(str(images))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		else:
			prev = self.rt_errors_get_images(id)
			if images != prev:
				self.report[id]['Images'] = self.whitespace_set_ini_value(str(images))
				self.report_item_set_changed(id)
				self.report_save()
				return 1
		return 0

	def rt_errors_get_group_rn(self, id):
		self.debugmsg(9, "id:", id)
		if 'GroupRN' in self.report[id]:
			return int(self.report[id]['GroupRN'])
		else:
			self.rt_errors_set_group_rn(id, 1)
			return 1

	def rt_errors_set_group_rn(self, id, group):
		self.debugmsg(5, "id:", id, "	group:", group)
		if 'GroupRN' not in self.report[id]:
			self.report[id]['GroupRN'] = self.whitespace_set_ini_value(str(group))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		else:
			prev = self.rt_errors_get_group_rn(id)
			if group != prev:
				self.report[id]['GroupRN'] = self.whitespace_set_ini_value(str(group))
				self.report_item_set_changed(id)
				self.report_save()
				return 1
		return 0

	def rt_errors_get_group_et(self, id):
		self.debugmsg(9, "id:", id)
		if 'GroupET' in self.report[id]:
			return int(self.report[id]['GroupET'])
		else:
			self.rt_errors_set_group_et(id, 1)
			return 1

	def rt_errors_set_group_et(self, id, group):
		self.debugmsg(5, "id:", id, "	group:", group)
		if 'GroupET' not in self.report[id]:
			self.report[id]['GroupET'] = self.whitespace_set_ini_value(str(group))
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		else:
			prev = self.rt_errors_get_group_et(id)
			if group != prev:
				self.report[id]['GroupET'] = self.whitespace_set_ini_value(str(group))
				self.report_item_set_changed(id)
				self.report_save()
				return 1
		return 0

	def rt_errors_get_data(self, id):
		self.debugmsg(5, "id:", id)
		key = "{}_{}".format(id, self.report_item_get_changed(id))

		if id not in self.reportdata:
			self.reportdata[id] = {}

		if "key" in self.reportdata[id] and self.reportdata[id]["key"] != key:
			self.reportdata[id] = {}

		sql = self.rt_errors_generate_sql(id)
		self.debugmsg(5, "sql:", sql)
		# colours = self.rt_table_get_colours(id)
		if sql is not None and len(sql.strip()) > 0:
			self.debugmsg(5, "sql:", sql)
			self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
			self.reportdata[id]["key"] = key
			while key not in self.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = self.dbqueue["ReadResult"][key]
			self.debugmsg(5, "tdata:", tdata)

			if len(tdata) > 0:
				cols = list(tdata[0].keys())
				self.debugmsg(5, "cols:", cols)

				for rowi in tdata:
					self.debugmsg(9, "rowi:", rowi)
					rid = rowi['id']
					self.debugmsg(8, "rid:", rid)
					if rid not in self.reportdata[id]:
						self.reportdata[id][rid] = rowi
					if rid in self.reportdata[id] and "error" not in self.reportdata[id][rid]:
						self.rt_errors_parse_xml(id, rid)
				self.debugmsg(9, "self.reportdata[", id, "]:", self.reportdata[id])
		return self.reportdata[id]

	def rt_errors_parse_xml(self, id, rid):
		self.debugmsg(5, "id:", id, "	rid:", rid)

		def safe_string(s):
			return re.sub(r'[<>:"/\\|?*\n\t]', "_", s)
		if id in self.reportdata and rid in self.reportdata[id]:
			rdata = self.reportdata[id][rid]
			self.debugmsg(8, "rdata:", rdata)

			# rdir = self.config['Reporter']['ResultDir']
			# self.debugmsg(5, "rdir:", rdir)
			dbfile = self.config['Reporter']['Results']
			self.debugmsg(9, "dbfile:", dbfile)

			ldir = os.path.join(os.path.dirname(dbfile), "logs")
			self.debugmsg(8, "ldir:", ldir)
			# 		opencart_1_1_1690876686_1_1690876693/Opencart_Sales_output.xml
			gxpatt = os.path.join(ldir, "{}_{}_{}_*_{}_*".format(
				safe_string(rdata['script'].split('.')[0]).rstrip("_"),
				rdata['script_index'],
				rdata['robot'],
				rdata['iteration']
			), "*_output.xml")
			self.debugmsg(9, "gxpatt:", gxpatt)

			xmlf = "not_found"
			xmll = glob.glob(gxpatt, recursive=True)
			if len(xmll) > 0:
				xmlf = glob.glob(gxpatt, recursive=True)[0]
			self.debugmsg(5, "xmlf:", xmlf)

			if os.path.isfile(xmlf):
				self.reportdata[id][rid]['xml_file'] = xmlf

				# tree = etree.parse(xmlf)
				with open(xmlf, 'rb') as xml_file:
					tree = etree.parse(xml_file)
				root = tree.getroot()
				self.debugmsg(9, "root:", root)

				# //suite/@source	--> 	/tmp/rfswarmagent/scripts/opencart.robot
				suites = root.findall(".//suite")
				self.debugmsg(9, "suites:", suites)
				source = suites[0].get('source')
				self.debugmsg(8, "source:", source)

				# //kw/status[@status='FAIL']/../msg[@level='FAIL']

				failkws = root.findall(".//kw/status[@status='FAIL']/..")
				self.debugmsg(9, "failkws:", failkws)

				if len(failkws) > 0:
					failkw = failkws[-1]
					failmsg = failkw.find("msg[@level='FAIL']")
					self.debugmsg(5, "failmsg:", failmsg, failmsg.text)

					self.reportdata[id][rid]['error'] = failmsg.text

					# //kw/status[@status='FAIL']/../msg[@level='INFO'] --> html decode for img tag
					# //kw/status[@status='FAIL']/../msg[@level='INFO' and @html='true']
					# </td></tr><tr><td colspan="3"><a href="selenium-screenshot-1.png"><img src="selenium-screenshot-1.png" width="800px"></a>
					# infomsg = failkw.find("msg[@level='INFO' and @html='true']")

					infomsg = failkw.find("msg[@html='true']")
					if infomsg is not None:
						self.debugmsg(5, "infomsg:", infomsg, infomsg.text)

						# <a[^>]*href="([^"]*)
						# m = re.search(r'<a[^>]*href="([^"]*)', infomsg.text)
						m = re.search(r'<img[^>]*src="([^"]*)', infomsg.text)
						image = m.group(1)
						self.debugmsg(5, "image:", image)
						if image is not None:
							imgdir = os.path.dirname(xmlf)
							imagef = os.path.join(imgdir, image)

							if os.path.isfile(imagef):
								self.debugmsg(5, "imagef:", imagef)
								self.reportdata[id][rid]['image'] = image
								self.reportdata[id][rid]['image_file'] = imagef

	def rt_errors_get_label(self, id, lblname):
		self.debugmsg(5, "id:", id, "	lblname:", lblname)
		if lblname in self.report[id]:
			self.debugmsg(5, "id:", id, "	lblname:", lblname, "	retvalue:", self.whitespace_get_ini_value(self.report[id][lblname]))
			return self.whitespace_get_ini_value(self.report[id][lblname])
		else:
			self.debugmsg(5, "id:", id, "	lblname:", lblname, "	retvalue:", self.defaultlabels[lblname])
			return self.defaultlabels[lblname]

	def rt_errors_set_label(self, id, lblname, lblvalue):
		self.debugmsg(5, "id:", id, "	lblname:", lblname, "	lblvalue:", lblvalue)
		prev = self.rt_table_get_colname(id, lblname)
		if lblvalue != prev and lblvalue not in [None, ""]:
			self.report[id][lblname] = self.whitespace_set_ini_value(lblvalue)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		if lblvalue in [None, ""]:
			self.report[id][lblname] = self.whitespace_set_ini_value(lblname)
			self.report_item_set_changed(id)
			self.report_save()
			return 1
		return 0

	#
	# Result data db Functions
	#
	def column_in_table(self, table, column):
		sql = "SELECT 1 [HasColumn] FROM pragma_table_info('{}') WHERE Name = '{}'".format(table, column)
		self.debugmsg(8, "sql:", sql)
		key = "HasColumn_{}_{}".format(table, column)
		self.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in self.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = self.dbqueue["ReadResult"][key]
		self.debugmsg(8, "tdata:", tdata)
		hascol = 0
		if len(tdata) > 0:
			# table headers
			if "HasColumn" in tdata[0]:
				hascol = tdata[0]["HasColumn"]

		if "DBTable" not in self.settings:
			self.settings["DBTable"] = {}
		if table not in self.settings["DBTable"]:
			self.settings["DBTable"][table] = {}
		self.settings["DBTable"][table][column] = hascol
		# self.settings["DBTable"]['Metrics']['DataSource']

	def open_results_db(self, dbpath):
		self.close_results_db()
		if self.datadb is None:
			self.debugmsg(5, "Connect to DB")
			self.datadb = sqlite3.connect(dbpath)
			self.datadb.create_aggregate("percentile", 2, percentile)
			self.datadb.create_aggregate("stdev", 1, stdevclass)

			compopt = self.datadb.execute("PRAGMA compile_options;")
			self.db_compile_options = [x[0] for x in compopt.fetchall()]

			if "ENABLE_MATH_FUNCTIONS" not in self.db_compile_options:
				self.datadb.create_function('floor', 1, math.floor)
				# https://www.sqlite.org/lang_mathfunc.html
				# https://stackoverflow.com/questions/70451170/sqlite3-math-functions-python

			mds = threading.Thread(target=lambda: self.column_in_table("Metrics", "DataSource"))
			mds.start()

	def close_results_db(self):
		# self.config['Reporter']['Results']
		if self.datadb is not None:
			self.run_dbthread = False
			self.debugmsg(5, "Disconnect and close DB")
			self.datadb.commit()
			self.datadb.close()
			self.datadb = None

	def run_db_thread(self):
		while self.run_dbthread:
			if self.datadb is None:
				self.debugmsg(9, "open results database")
				if len(self.config['Reporter']['Results']) > 0:
					self.open_results_db(self.config['Reporter']['Results'])
				else:
					self.run_dbthread = False

			if self.datadb is not None:

				# process db queues

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
					self.debugmsg(9, "run_db_thread: dbqueue: Read")
					tmpq = list(self.dbqueue["Read"])
					self.dbqueue["Read"] = []
					self.debugmsg(9, "run_db_thread: dbqueue: Read: tmpq:", tmpq)
					for item in tmpq:
						if "SQL" in item:
							try:
								self.debugmsg(9, "run_db_thread: dbqueue: Read: SQL:", item["SQL"])
								self.datadb.row_factory = self.dict_factory
								cur = self.datadb.cursor()
								cur.execute(item["SQL"])
								result = cur.fetchall()
								self.debugmsg(9, "run_db_thread: dbqueue: Read: result:", result)
								cur.close()
								self.datadb.commit()

								self.debugmsg(9, "run_db_thread: dbqueue: Read: result:", result)
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
			# self.datadb.close()
			# self.datadb = None
			self.close_results_db()

	def dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def start_db(self):
		self.run_dbthread = True
		self.dbthread = threading.Thread(target=self.run_db_thread)
		self.dbthread.start()

	def stop_db(self):
		self.run_dbthread = False
		if self.dbthread is not None:
			self.dbthread.join()
			self.dbthread = None
			# clear queue cached results
			self.dbqueue = {"Write": [], "Read": [], "ReadResult": {}, "Results": [], "Metric": [], "Metrics": []}

	#
	# Colour Functions
	#

	def set_named_colour(self, name, incolour):
		safename = name.lower().replace(",", ";")
		if safename not in self.namecolours:
			self.namecolours.append(safename)
		self.set_line_colour(self.namecolours.index(safename), incolour)

	def named_colour(self, name):
		safename = name.lower().replace(",", ";")
		if safename not in self.namecolours:
			self.namecolours.append(safename)
		return self.line_colour(self.namecolours.index(safename))

	def set_line_colour(self, grp, incolour):
		if grp < len(self.defcolours):
			self.defcolours[grp] = incolour
		else:
			while grp < len(self.defcolours):
				self.debugmsg(9, self.defcolours)
				newcolour = self.get_colour()
				self.debugmsg(9, "newcolour:", newcolour)
				self.defcolours.append(newcolour)
			self.defcolours[grp] = incolour
			self.report_save()

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
			self.report_save()
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
		self.debugmsg(8, "score:", score)

		return score

	#
	# Data Post Processing Functions
	#

	def graph_postprocess_data_plan(self, id, datain):
		self.debugmsg(5, "datain:", datain)
		# [
		# 	{'PrimaryMetric': 'Delay_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '0', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Ramp_Up_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '20', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Robots_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '30', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Run_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '60', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'}
		# ]
		# 	 'Time' 	 'Value' 	 [Name]
		dataout = []
		data = {}
		totaldata = {}
		for rowin in datain:
			self.debugmsg(5, "rowin:", rowin)
			if 'PrimaryMetric' in rowin and "_" in rowin['PrimaryMetric']:
				key, index = rowin['PrimaryMetric'].rsplit("_", 1)
				self.debugmsg(5, "key:", key, "	index:", index)
				if index not in data:
					data[index] = {}
				if key == "Delay":
					data[index]["start"] = rowin['MetricTime']
					data[index]["delay"] = rowin['MetricValue']
					data[index]["colourkey"] = rowin['SecondaryMetric'] + " " + rowin['FilePath']

				if key == "Ramp_Up":
					data[index]["rampup"] = rowin['MetricValue']
				if key == "Robots":
					data[index]["robots"] = rowin['MetricValue']
				if key == "Run":
					data[index]["run"] = rowin['MetricValue']

			else:
				self.debugmsg(5, "Unexpected data in rowin:", rowin)

		for index in data.keys():
			self.debugmsg(5, "index:", index, data[index])

			eventtime = int(data[index]["start"])
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += 0
			else:
				totaldata[eventtime] = 0

			eventtime += int(data[index]["delay"]) + 0.001
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += 0
			else:
				totaldata[eventtime] = 0

			eventtime += int(data[index]["rampup"])
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = int(data[index]["robots"])
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += int(data[index]["robots"])
			else:
				totaldata[eventtime] = int(data[index]["robots"])

			eventtime += int(data[index]["run"])
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = int(data[index]["robots"])
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += 0
			else:
				totaldata[eventtime] = 0

			# estimated rampdown
			eventtime += int(data[index]["rampup"]) + 0.001
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += int(data[index]["robots"]) * -1
			else:
				totaldata[eventtime] = int(data[index]["robots"]) * -1

		stot = self.report_item_get_int(id, "ShowTotal")

		if stot > 0:
			robots = 0
			for key in totaldata.keys():
				self.debugmsg(5, "key:", key, totaldata[key])
				robots += totaldata[key]
				rowout = {}
				rowout["Time"] = key
				rowout["Value"] = robots
				rowout["Name"] = "Total"
				dataout.append(rowout)

		self.debugmsg(5, "dataout:", dataout)
		return dataout

	def graph_postprocess_data_monitoring(self, id, datain):
		self.debugmsg(5, "datain:", datain)
		# [
		# 	{'PrimaryMetric': 'Delay_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '0', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Ramp_Up_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '20', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Robots_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '30', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Run_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '60', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'}
		# ]
		# 	 'Time' 	 'Value' 	 [Name]
		dataout = []
		data = {}
		totaldata = {}
		for rowin in datain:
			self.debugmsg(5, "rowin:", rowin)
			if 'PrimaryMetric' in rowin and "_" in rowin['PrimaryMetric']:
				key, index = rowin['PrimaryMetric'].rsplit("_", 1)
				self.debugmsg(5, "key:", key, "	index:", index)
				if index not in data:
					data[index] = {}
				if key == "Delay":
					data[index]["start"] = rowin['MetricTime']
					data[index]["delay"] = rowin['MetricValue']
					data[index]["colourkey"] = rowin['SecondaryMetric'] + " " + rowin['FilePath']

				if key == "Ramp_Up":
					data[index]["rampup"] = rowin['MetricValue']
				if key == "Robots":
					data[index]["robots"] = rowin['MetricValue']
				if key == "Run":
					data[index]["run"] = rowin['MetricValue']

			else:
				self.debugmsg(5, "Unexpected data in rowin:", rowin)

		for index in data.keys():
			self.debugmsg(5, "index:", index, data[index])

			eventtime = int(data[index]["start"])
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += 0
			else:
				totaldata[eventtime] = 0

			eventtime += int(data[index]["delay"]) + 0.001
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += 0
			else:
				totaldata[eventtime] = 0

			eventtime += int(data[index]["rampup"])
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = int(data[index]["robots"])
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += int(data[index]["robots"])
			else:
				totaldata[eventtime] = int(data[index]["robots"])

			eventtime += int(data[index]["run"])
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = int(data[index]["robots"])
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += 0
			else:
				totaldata[eventtime] = 0

			# estimated rampdown
			eventtime += int(data[index]["rampup"]) + 0.001
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += int(data[index]["robots"]) * -1
			else:
				totaldata[eventtime] = int(data[index]["robots"]) * -1

		stot = self.report_item_get_int(id, "ShowTotal")

		if stot > 0:
			robots = 0
			for key in totaldata.keys():
				self.debugmsg(5, "key:", key, totaldata[key])
				robots += totaldata[key]
				rowout = {}
				rowout["Time"] = key
				rowout["Value"] = robots
				rowout["Name"] = "Total"
				dataout.append(rowout)

		self.debugmsg(5, "dataout:", dataout)
		return dataout

	def table_postprocess_data_plan(self, id, datain):
		self.debugmsg(5, "datain:", datain)
		# [
		# 	{'PrimaryMetric': 'Delay_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '0', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Ramp_Up_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '20', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Robots_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '30', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Run_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '60', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'}
		# ]
		# 	 Index		Robots		Delay  		RampUp 		Run		Script		Test	Settings
		dataout = []
		data = {}

		scriptopt = self.report_item_get_value(id, self.rt_table_ini_colname("Script Opt"))
		if scriptopt is None:
			scriptopt = "File"

		for rowin in datain:
			self.debugmsg(5, "rowin:", rowin)
			if 'PrimaryMetric' in rowin and "_" in rowin['PrimaryMetric']:
				key, index = rowin['PrimaryMetric'].rsplit("_", 1)
				self.debugmsg(5, "key:", key, "	index:", index)
				if index not in data:
					data[index] = {}
				if key == "Delay":
					data[index]["Index"] = index
					data[index]["Delay"] = int(rowin['MetricValue'])
					data[index]["Colour"] = rowin['SecondaryMetric'] + " " + rowin['FilePath']
					data[index]["Script"] = rowin['File']
					data[index]["ScriptPath"] = rowin['FilePath']
					data[index]["Test"] = rowin['SecondaryMetric']

				if key == "Ramp_Up":
					data[index]["Ramp Up"] = int(rowin['MetricValue'])
				if key == "Robots":
					data[index]["Robots"] = int(rowin['MetricValue'])
				if key == "Run":
					data[index]["Run"] = int(rowin['MetricValue'])

			else:
				self.debugmsg(5, "Unexpected data in rowin:", rowin)

		for index in data.keys():
			self.debugmsg(5, "index:", index, data[index])

			datarow = {}
			# 	 Index		Robots		Delay  		RampUp 		Run		Script		Test	Settings
			datarow["Colour"] = data[index]["Colour"]
			datarow["Index"] = data[index]["Index"]
			datarow["Robots"] = data[index]["Robots"]
			datarow["Delay"] = self.sec2hms(data[index]["Delay"])
			datarow["Ramp Up"] = self.sec2hms(data[index]["Ramp Up"])
			datarow["Run"] = self.sec2hms(data[index]["Run"])
			if scriptopt == "File":
				datarow["Script"] = data[index]["Script"]
			else:
				datarow["Script"] = data[index]["ScriptPath"]
			datarow["Test"] = data[index]["Test"]

			dataout.append(datarow)

		self.debugmsg(5, "dataout:", dataout)
		return dataout

	def table_postprocess_data_monitoring(self, id, datain):
		self.debugmsg(5, "datain:", datain)
		# [
		# 	{'PrimaryMetric': 'Delay_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '0', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Ramp_Up_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '20', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Robots_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '30', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Run_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '60', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'}
		# ]
		# 	 Index		Robots		Delay  		RampUp 		Run		Script		Test	Settings
		dataout = []
		data = {}

		scriptopt = self.report_item_get_value(id, self.rt_table_ini_colname("Script Opt"))
		if scriptopt is None:
			scriptopt = "File"

		for rowin in datain:
			self.debugmsg(5, "rowin:", rowin)
			if 'PrimaryMetric' in rowin and "_" in rowin['PrimaryMetric']:
				key, index = rowin['PrimaryMetric'].rsplit("_", 1)
				self.debugmsg(5, "key:", key, "	index:", index)
				if index not in data:
					data[index] = {}
				if key == "Delay":
					data[index]["Index"] = index
					data[index]["Delay"] = int(rowin['MetricValue'])
					data[index]["Colour"] = rowin['SecondaryMetric'] + " " + rowin['FilePath']
					data[index]["Script"] = rowin['File']
					data[index]["ScriptPath"] = rowin['FilePath']
					data[index]["Test"] = rowin['SecondaryMetric']

				if key == "Ramp_Up":
					data[index]["Ramp Up"] = int(rowin['MetricValue'])
				if key == "Robots":
					data[index]["Robots"] = int(rowin['MetricValue'])
				if key == "Run":
					data[index]["Run"] = int(rowin['MetricValue'])

			else:
				self.debugmsg(5, "Unexpected data in rowin:", rowin)

		for index in data.keys():
			self.debugmsg(5, "index:", index, data[index])

			datarow = {}
			# 	 Index		Robots		Delay  		RampUp 		Run		Script		Test	Settings
			datarow["Colour"] = data[index]["Colour"]
			datarow["Index"] = data[index]["Index"]
			datarow["Robots"] = data[index]["Robots"]
			# datarow["Delay"] = self.sec2hms(data[index]["Delay"])
			# datarow["Ramp Up"] = self.sec2hms(data[index]["Ramp Up"])
			datarow["Run"] = self.sec2hms(data[index]["Run"])
			if scriptopt == "File":
				datarow["Script"] = data[index]["Script"]
			else:
				datarow["Script"] = data[index]["ScriptPath"]
			datarow["Test"] = data[index]["Test"]

			dataout.append(datarow)

		self.debugmsg(5, "dataout:", dataout)
		return dataout
