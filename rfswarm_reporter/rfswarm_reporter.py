#!/usr/bin/python
#
# 	Robot Framework Swarm
# 		Reporter
#    Version 1.4.0
#

import argparse
import base64  # used for embedding images  # used for xhtml export
import configparser
import difflib
import glob
import importlib.metadata
import inspect
import math
import os
import platform
import random
import re
import shutil
import signal
import sqlite3
import sys
import tempfile
import threading
import time
import tkinter as tk  # python3
import tkinter.colorchooser as tkac
import tkinter.filedialog as tkf  # python3
import tkinter.font as tkFont

# import tkinter.messagebox as tkm  # python3
import tkinter.simpledialog as tksd
import tkinter.ttk as ttk  # python3
import webbrowser
import zoneinfo  # says Requires python 3.9
from copy import copy  # used for xlsx export
from datetime import datetime  # , timezone
from io import BytesIO  # used for embedding images  # used for xhtml export
from typing import Any

import matplotlib  # required for matplot graphs
import matplotlib.font_manager as font_manager
import openpyxl  # used for xlsx export
import tzlocal
from docx import Document  # used for docx export
from docx.enum.style import WD_STYLE_TYPE  # used for docx export
from docx.enum.text import WD_ALIGN_PARAGRAPH  # used for docx export
from docx.oxml.shared import OxmlElement, qn  # used for docx export
from docx.shared import Cm, Pt, RGBColor  # used for docx export
from lxml import etree  # used for xhtml export
from lxml.builder import E, ElementMaker  # used for xhtml export

# required for matplot graphs
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# required for matplot graphs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure  # required for matplot graphs

# required for company logo's (I beleive this is a depandancy of matplotlib anyway)
from PIL import Image, ImageTk

matplotlib.use("TkAgg") 	# required for matplot graphs


class percentile:
	def __init__(self):
		self.count = 0
		self.percent = 90
		self.values = []

	def step(self, value, percent):
		base.debugmsg(9, "value:", value, "	percent:", percent)
		if value is None:
			return
		self.count += 1
		self.values.append(value)
		self.percent = percent

	def finalize(self):
		try:
			mincount = 100 / (100 - self.percent)
			if self.count < mincount:
				# Need at least 10 samples to get a useful percentile
				return None
			base.debugmsg(9, "percentile: finalize: mincount:", mincount, "	self.count:", self.count, "	self.percent:", self.percent, "	self.values:", self.values)
			nth = self.count * (self.percent / 100)
			base.debugmsg(9, "percentile: finalize: nth:", nth)
			nthi = int(nth)
			# nthi = int(math.ceil(self.count * (self.percent/100)))
			self.values.sort()
			base.debugmsg(8, "percentile: finalize: nthi:", nthi, "	self.values[nthi]:", self.values[nthi], "	self.values:", self.values)
			return self.values[nthi]
			# return self.count
		except Exception as e:
			base.debugmsg(5, "Exception:", e)


class stdevclass:
	def __init__(self):
		self.M = 0.0
		self.S = 0.0
		self.k = 1

	def step(self, value):
		if value is None:
			return
		tM = self.M
		self.M += (value - tM) / self.k
		self.S += (value - tM) * (value - self.M)
		self.k += 1

	def finalize(self):
		base.debugmsg(9, "self.k:", self.k, "	self.S:", self.S, "	self.M:", self.M)
		if self.k < 3:
			return None
		try:
			res = math.sqrt(self.S / (self.k - 2))
			base.debugmsg(8, "res:", res)
			return res
		except Exception as e:
			base.debugmsg(5, "Exception:", e)


class ReporterBase():
	version = "1.4.0"
	debuglvl = 0

	save_ini = True
	running = True
	displaygui = True
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
				print(" ".join(msglst))
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
			with open(base.reporter_ini, 'w', encoding="utf8") as configfile:    # save
				base.config.write(configfile)
				self.debugmsg(6, "File Saved:", self.reporter_ini)

	def whitespace_set_ini_value(self, valin):
		base.debugmsg(9, "valin:", valin)
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
			base.debugmsg(9, "valout:", valout)
		return valout

	def whitespace_get_ini_value(self, valin):
		base.debugmsg(9, "valin:", valin)
		valout = str(valin)
		if len(valout) > 0:
			valout = valout.replace('x12', '\n')
			valout = valout.replace('x15', '\r')
			valout = valout.replace('x11', '\t')
			valout = valout.replace('x91', '[')
			valout = valout.replace('x93', ']')
			valout = valout.replace('x37', '%')
			valout = valout.replace('x35', '#')
			base.debugmsg(9, "valout:", valout)
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
		base.debugmsg(6, "type(sec):", type(sec), sec)
		if isinstance(sec, time.struct_time):
			sec = time.mktime(sec)
			base.debugmsg(6, "type(sec):", type(sec), sec)
		h = int(sec / 3600)
		m = int((sec - h * 3600) / 60)
		s = int((sec - h * 3600) - m * 60)
		hms = "{:02}:{:02}:{:02}".format(h, m, s)
		return hms

	def hms2sec(self, hms):
		sec = 0
		arrhms = str(hms).split(":")
		base.debugmsg(6, "arrhms:", arrhms)
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

	#
	# Template Functions
	#

	def template_create(self):
		# base.report_create()
		base.report = configparser.ConfigParser()
		base.config['Reporter']['Template'] = ""
		if "Report" not in base.report:
			base.report["Report"] = {}
		base.report["Report"]["Order"] = ""
		# base.debugmsg(5, "template order:", base.report["Report"]["Order"])

		base.debugmsg(5, "base.report: ", base.report._sections)

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
		base.report_add_subsection(plngl)
		# datatype = Plan
		self.rt_table_set_dt(plngl, 'Plan')
		# changed = 1728738092.5689259
		# sql = SELECT md1.* , md0.SecondaryMetric as x91Filex93 , fp0.SecondaryMetric as x91FilePathx93 FROM MetricData as md0 LEFT JOIN MetricData as fp0 ON fp0.MetricValue = md0.MetricValue AND fp0.MetricType = 'Scenario' AND fp0.PrimaryMetric like 'Local_Path_x37' LEFT JOIN MetricData as md1 ON md1.SecondaryMetric = md0.MetricValue AND md1.MetricType = 'Scenario' WHERE md0.MetricType = 'Scenario' AND md0.PrimaryMetric like 'Test_x37'
		# showtotal = 1
		base.report_item_set_int(plngl, "ShowTotal", 1)

		# [FB9082D01BCR]
		plngr = plng + "R"
		base.report_add_subsection(plngr)
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
		base.report_item_set_bool(plnt, base.rt_table_ini_colname("index Show"), 1)
		# col_robots_show = 1
		base.report_item_set_bool(plnt, base.rt_table_ini_colname("robots Show"), 1)
		# col_delay_show = 1
		base.report_item_set_bool(plnt, base.rt_table_ini_colname("delay Show"), 1)
		# col_ramp_up_show = 1
		base.report_item_set_bool(plnt, base.rt_table_ini_colname("ramp up Show"), 1)
		# col_run_show = 1
		base.report_item_set_bool(plnt, base.rt_table_ini_colname("run Show"), 1)
		# col_script_show = 1
		base.report_item_set_bool(plnt, base.rt_table_ini_colname("script Show"), 1)
		# col_script_opt = File
		base.report_item_set_value(plnt, base.rt_table_ini_colname("script Opt"), "File")
		# col_test_show = 1
		base.report_item_set_bool(plnt, base.rt_table_ini_colname("test Show"), 1)

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
		base.report_item_set_bool(trs, base.rt_table_ini_colname("Result Name Show"), 1)
		# col_minimum_show = 0
		base.report_item_set_bool(trs, base.rt_table_ini_colname("minimum Show"), 0)
		# col_average_show = 1
		base.report_item_set_bool(trs, base.rt_table_ini_colname("average Show"), 1)
		# col_90x37ile_show = 1
		base.report_item_set_bool(trs, base.rt_table_ini_colname("90%ile Show"), 1)
		# col_maximum_show = 1
		base.report_item_set_bool(trs, base.rt_table_ini_colname("maximum Show"), 1)
		# col_std_dev_show = 1
		base.report_item_set_bool(trs, base.rt_table_ini_colname("Std Dev Show"), 1)
		# col_pass_show = 1
		base.report_item_set_bool(trs, base.rt_table_ini_colname("pass Show"), 1)
		# col_fail_show = 1
		base.report_item_set_bool(trs, base.rt_table_ini_colname("fail Show"), 1)
		# col_other_show = 0
		base.report_item_set_bool(trs, base.rt_table_ini_colname("other Show"), 0)

		#
		# 	Robots vs Response Time
		#
		rrt = self.report_new_section("TOP", "Robots vs Response Time")
		self.report_item_set_type(rrt, 'graph')

		# [FA37C950802L]idl
		rttl = rrt + "L"
		base.report_add_subsection(rttl)
		# resulttype = Response Time
		base.report_item_set_value(rttl, "resulttype", "Response Time")
		# changed = 1728738059.779502
		# filterresult = None
		# filteragent = None
		# datatype = Result
		self.rt_table_set_dt(rttl, 'Result')

		# [FA37C950802R]
		rttr = rrt + "R"
		base.report_add_subsection(rttr)
		# datatype = Metric
		self.rt_table_set_dt(rttr, 'Metric')
		# changed = 1728738059.7891614
		# axisen = 1
		base.report_item_set_bool(rttr, "axisen", 1)
		# metrictype = Scenario
		base.report_item_set_value(rttr, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		base.report_item_set_value(rttr, "secondarymetric", "total_robots")

		#
		# 	-	Response Times
		#
		# name = Response Times
		rt = self.report_new_section(rrt, "Response Times")
		# parent = FA37C950802
		self.report_item_set_type(rt, 'table')
		# type = table
		base.report_item_set_value(rt, "type", "table")
		# changed = 1728738060.9264157
		# colours = 1
		base.report_item_set_bool(rt, "colours", 1)
		# datatype = Result
		base.report_item_set_value(rt, "datatype", "Result")
		# resulttype = Response Time
		base.report_item_set_value(rt, "resulttype", "Response Time")
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
		base.report_item_set_bool(rb, "colours", 1)
		# datatype = Metric
		base.report_item_set_value(rb, "datatype", "Metric")
		# metrictype = Scenario
		base.report_item_set_value(rb, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		# secondarymetric = total_robots
		base.report_item_set_value(rb, "secondarymetric", "total_robots")
		# isnumeric = 1
		base.report_item_set_bool(rb, "isnumeric", 1)
		# showcount = 0
		base.report_item_set_bool(rb, "showcount", 1)
		# col_primarymetric_show = 1
		base.report_item_set_bool(rb, "col_primarymetric_show", 1)
		# col_minimum_show = 0
		base.report_item_set_bool(rb, "col_minimum_show", 0)
		# col_average_show = 0
		base.report_item_set_bool(rb, "col_average_show", 0)
		# col_90x37ile_show = 0
		base.report_item_set_bool(rb, "col_90x37ile_show", 0)
		# col_maximum_show = 1
		base.report_item_set_bool(rb, "col_maximum_show", 1)
		# col_std_dev_show = 0
		base.report_item_set_bool(rb, "col_std_dev_show", 0)
		# col_maximum = Robots
		base.report_item_set_value(rb, "col_maximum", "Robots")

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
		base.report_add_subsection(cpul)
		# metrictype = Agent
		base.report_item_set_value(cpul, "metrictype", "Agent")
		# changed = 1728745351.1353724
		base.report_item_set_bool(cpul, "axisen", 1)
		# filteragent = None
		# filtertype = None
		# datatype = Metric
		base.report_item_set_value(cpul, "datatype", "Metric")
		# secondarymetric = CPU
		base.report_item_set_value(cpul, "secondarymetric", "CPU")
		# enablefilteragent = 1
		base.report_item_set_bool(cpul, "enablefilteragent", 1)
		#
		# [FB90C728C87R]
		cpur = cpu + "R"
		base.report_add_subsection(cpur)
		# datatype = Metric
		base.report_item_set_value(cpur, "datatype", "Metric")
		# changed = 1728745351.027923
		# axisen = 1
		base.report_item_set_bool(cpur, "axisen", 1)
		# metrictype = Scenario
		base.report_item_set_value(cpur, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		# secondarymetric = total_robots
		base.report_item_set_value(cpur, "secondarymetric", "total_robots")

		#
		# 	-	Memory
		#
		# name = Memory
		mem = self.report_new_section(agnt, "Agent Memory (RAM) Usage")
		# type = graph
		self.report_item_set_type(mem, 'graph')

		# [FB90C73DBB6L]
		meml = mem + "L"
		base.report_add_subsection(meml)
		# metrictype = Agent
		base.report_item_set_value(meml, "metrictype", "Agent")
		# changed = 1728745342.77505
		base.report_item_set_bool(meml, "axisen", 1)
		# filteragent = None
		# filtertype = None
		# datatype = Metric
		base.report_item_set_value(meml, "datatype", "Metric")
		# secondarymetric = MEM
		base.report_item_set_value(meml, "secondarymetric", "MEM")
		# enablefilteragent = 1
		base.report_item_set_bool(meml, "enablefilteragent", 1)
		#
		# [FB90C73DBB6R]
		memr = mem + "R"
		base.report_add_subsection(memr)
		# datatype = Metric
		base.report_item_set_value(memr, "datatype", "Metric")
		# changed = 1728745342.6672406
		# axisen = 1
		base.report_item_set_bool(memr, "axisen", 1)
		# filteragent = None
		# filtertype = None
		# metrictype = Scenario
		base.report_item_set_value(memr, "metrictype", "Scenario")
		# secondarymetric = total_robots
		base.report_item_set_value(memr, "secondarymetric", "total_robots")

		#
		# 	-	Agent Names
		#
		# name = Agent Names
		an = self.report_new_section(agnt, "Agent Names")
		# type = table
		self.report_item_set_type(an, 'table')
		# colours = 1
		base.report_item_set_bool(an, "colours", 1)
		# datatype = Metric
		base.report_item_set_value(an, "datatype", "Metric")
		# metrictype = Agent
		base.report_item_set_value(an, "metrictype", "Agent")
		# filteragent = None
		# filtertype = None
		# col_primarymetric_show = 0
		base.report_item_set_bool(an, "col_primarymetric_show", 0)
		# col_metrictype_show = 1
		base.report_item_set_bool(an, "col_metrictype_show", 1)
		# col_secondarymetric_show = 1
		base.report_item_set_bool(an, "col_secondarymetric_show", 1)
		# col_metricvalue_show = 0
		base.report_item_set_bool(an, "col_metricvalue_show", 0)
		# enablefilteragent = 1
		base.report_item_set_bool(an, "enablefilteragent", 1)
		# secondarymetric = CPU
		base.report_item_set_value(an, "secondarymetric", "CPU")
		# col_agent_show = 1
		base.report_item_set_bool(an, "col_agent_show", 1)

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
		base.report_item_set_bool(ad, "colours", 0)
		# datatype = Metric
		base.report_item_set_value(ad, "datatype", "Metric")
		# metrictype = Agent
		base.report_item_set_value(ad, "metrictype", "Metric")
		# filteragent = None
		# filtertype = None
		# col_primarymetric_show = 1
		base.report_item_set_bool(ad, "col_primarymetric_show", 1)
		# col_metrictype_show = 1
		base.report_item_set_bool(ad, "col_metrictype_show", 1)
		# col_secondarymetric_show = 1
		base.report_item_set_bool(ad, "col_secondarymetric_show", 1)
		# col_metricvalue_show = 1
		base.report_item_set_bool(ad, "col_metricvalue_show", 1)
		# enablefilteragent = 1
		base.report_item_set_bool(ad, "enablefilteragent", 1)
		# col_agent_show = 0
		base.report_item_set_bool(ad, "col_agent_show", 0)
		# col_primarymetric = Agent Name
		base.report_item_set_value(ad, "col_primarymetric", "Agent Name")
		# col_secondarymetric = Metric Name
		base.report_item_set_value(ad, "col_secondarymetric", "Metric Name")
		# col_metricvalue = Metric Value
		base.report_item_set_value(ad, "col_metricvalue", "Metric Value")

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
		base.report_add_subsection(fkgl)
		base.report_item_set_bool(fkgl, "axisen", 1)
		# resulttype = TPS
		base.report_item_set_value(fkgl, "resulttype", "TPS")
		# changed = 1728746053.26743
		# filterresult = Fail
		base.report_item_set_value(fkgl, "filterresult", "Fail")
		# filteragent = None
		# datatype = Result
		base.report_item_set_value(fkgl, "datatype", "Result")
		# enablefilterresult = 1
		base.report_item_set_bool(fkgl, "enablefilterresult", 1)

		#
		# [FB90CDCCFC9R]
		fkgr = fkg + "R"
		base.report_add_subsection(fkgr)
		# datatype = Metric
		base.report_item_set_value(fkgr, "datatype", "Metric")
		# changed = 1728746053.2828546
		# axisen = 1
		base.report_item_set_bool(fkgr, "axisen", 1)
		# metrictype = Scenario
		base.report_item_set_value(fkgr, "metrictype", "Scenario")
		# filteragent = None
		# filtertype = None
		# secondarymetric = total_robots
		base.report_item_set_value(fkgr, "secondarymetric", "total_robots")

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
		base.report_item_set_bool(fkn, "colours", 1)
		# datatype = Result
		base.report_item_set_value(fkn, "datatype", "Result")
		# resulttype = TPS
		base.report_item_set_value(fkn, "resulttype", "TPS")
		# filterresult = Fail
		base.report_item_set_value(fkn, "filterresult", "Fail")
		# filteragent = None
		# enablefilterresult = 1
		base.report_item_set_bool(fkn, "enablefilterresult", 1)
		# col_result_name_show = 1
		base.report_item_set_bool(fkn, "col_result_name_show", 1)
		# col_result_show = 1
		base.report_item_set_bool(fkn, "col_result_show", 1)
		# col_count_show = 1
		base.report_item_set_bool(fkn, "col_count_show", 1)

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
		base.report_item_set_bool(ed, "images", 1)
		# grouprn = 1
		base.report_item_set_bool(ed, "grouprn", 1)
		# groupet = 1
		base.report_item_set_bool(ed, "groupet", 1)

	def template_save(self, filename):
		saved = False
		if filename is None or len(filename) < 1:
			filename = base.config['Reporter']['Template']
		templatedata = configparser.ConfigParser()
		templatedata.read_dict(base.report._sections)
		if "Report" in templatedata:
			if "starttime" in templatedata["Report"]:
				# templatedata["Report"]["starttime"]
				templatedata.remove_option('Report', 'starttime')
			if "endtime" in templatedata["Report"]:
				# templatedata["Report"]["endtime"]
				templatedata.remove_option('Report', 'endtime')
		with open(filename, 'w', encoding="utf8") as templatefile:    # save
			# base.report.write(templatefile)
			templatedata.write(templatefile)
			self.debugmsg(6, "Template Saved:", filename)
			saved = True
		if saved:
			base.config['Reporter']['Template'] = base.whitespace_set_ini_value(filename)
			path, file = os.path.split(base.config['Reporter']['Template'])
			base.config['Reporter']['TemplateDir'] = base.whitespace_set_ini_value(path)
			base.saveini()

	def template_open(self, filename):
		if len(filename) > 0 and os.path.isfile(filename):
			base.debugmsg(7, "filename: ", filename)

			base.config['Reporter']['Template'] = base.whitespace_set_ini_value(filename)
			path, file = os.path.split(base.config['Reporter']['Template'])
			base.config['Reporter']['TemplateDir'] = base.whitespace_set_ini_value(path)
			base.saveini()

			base.report = None
			self.reportdata = {}
			base.report = configparser.ConfigParser()
			base.report.read(filename, encoding="utf8")

			base.report_item_set_changed_all("TOP")

		else:
			base.template_create()

	#
	# Report Functions
	#

	def report_save(self):
		saved = False
		if 'Reporter' in base.config:
			if 'Report' in base.config['Reporter'] and len(base.config['Reporter']['Report']) > 0:
				filename = base.config['Reporter']['Report']
				filedir = os.path.dirname(filename)
				if os.path.isdir(filedir):
					with open(filename, 'w', encoding="utf8") as reportfile:    # save
						base.report.write(reportfile)
						self.debugmsg(6, "Report Saved:", filename)
						saved = True
		return saved

	def report_open(self):
		filename = base.config['Reporter']['Report']
		base.debugmsg(7, "filename: ", filename)
		base.reportdata = {}
		base.report = None
		if len(filename) > 0 and os.path.isfile(filename):
			base.debugmsg(7, "filename: ", filename, " exists, open")
			base.report = configparser.ConfigParser()
			base.report.read(filename, encoding="utf8")
		else:
			templatefile = base.whitespace_get_ini_value(base.config['Reporter']['Template'])
			base.debugmsg(7, "Template: ", templatefile)
			if len(templatefile) > 0:
				base.template_open(templatefile)
			else:
				base.debugmsg(7, "template_create")
				base.template_create()
			base.debugmsg(7, "report_save")
			base.report_save()

	def report_starttime(self):
		if "starttime" in self.reportdata and self.reportdata["starttime"] > 0:
			base.debugmsg(5, "starttime:", self.reportdata["starttime"])
			return self.reportdata["starttime"]
		else:
			self.reportdata["starttime"] = 0
			if base.datadb is not None:
				sql = "SELECT MetricTime "
				sql += "FROM MetricData "
				sql += "WHERE MetricType = 'Scenario' "
				sql += "AND PrimaryMetric <> 'PreRun' "
				sql += "ORDER BY MetricTime ASC "
				sql += "LIMIT 1 "

				key = "report starttime"
				base.debugmsg(9, "sql:", sql)
				base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]
				base.debugmsg(9, "gdata:", gdata)

				self.reportdata["starttime"] = int(gdata[0]["MetricTime"])

				base.debugmsg(5, "starttime:", self.reportdata["starttime"])

				return self.reportdata["starttime"]
			else:
				base.debugmsg(5, "starttime:", int(time.time()) - 1)
				return int(time.time()) - 1

	def report_endtime(self):
		if "endtime" in self.reportdata and self.reportdata["endtime"] > 0:
			base.debugmsg(5, "endtime:", self.reportdata["endtime"])
			return self.reportdata["endtime"]
		else:
			self.reportdata["endtime"] = 0
			if base.datadb is not None:

				sql = "SELECT MetricTime "
				sql += "FROM MetricData "
				sql += "WHERE MetricType = 'Scenario' "
				sql += "AND PrimaryMetric <> 'PreRun' "
				sql += "ORDER BY MetricTime DESC "
				sql += "LIMIT 1 "

				key = "report endtime"
				base.debugmsg(9, "sql:", sql)
				base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]
				base.debugmsg(9, "gdata:", gdata)

				self.reportdata["endtime"] = int(gdata[0]["MetricTime"])

				base.debugmsg(5, "endtime:", self.reportdata["endtime"])

				return self.reportdata["endtime"]
			else:
				base.debugmsg(5, "starttime:", int(time.time()))
				return int(time.time())

	def report_formatdate(self, itime):
		base.debugmsg(9, "itime:", itime)
		format = base.rs_setting_get_dateformat()
		format = format.replace("yyyy", "%Y")
		format = format.replace("yy", "%y")
		format = format.replace("mm", "%m")
		format = format.replace("dd", "%d")
		base.debugmsg(9, "format:", format)
		# fdate = datetime.fromtimestamp(itime, timezone.utc).strftime(format)
		tz = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())
		fdate = datetime.fromtimestamp(itime, tz).strftime(format)
		base.debugmsg(9, "fdate:", fdate)
		return fdate

	def report_formattime(self, itime):
		base.debugmsg(9, "itime:", itime)
		format = base.rs_setting_get_timeformat()
		format = format.replace("HH", "%H")
		format = format.replace("h", "%I")
		format = format.replace("MM", "%M")
		format = format.replace("SS", "%S")
		format = format.replace("AMPM", "%p")

		base.debugmsg(9, "format:", format)
		tz = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())
		ftime = datetime.fromtimestamp(itime, tz).strftime(format)
		base.debugmsg(9, "ftime:", ftime)
		return ftime

	def report_formateddatetimetosec(self, stime):
		base.debugmsg(5, "stime:", stime)
		try:
			if len(stime) == 10 and stime.isdecimal():
				return int(stime)

			if len(stime) == 13 and stime.isdecimal():
				return int(stime) / 1000

			dformat = base.rs_setting_get_dateformat()
			dformat = dformat.replace("yyyy", "%Y")
			dformat = dformat.replace("yy", "%y")
			dformat = dformat.replace("mm", "%m")
			dformat = dformat.replace("dd", "%d")

			tformat = base.rs_setting_get_timeformat()
			tformat = tformat.replace("HH", "%H")
			tformat = tformat.replace("h", "%I")
			tformat = tformat.replace("MM", "%M")
			tformat = tformat.replace("SS", "%S")
			tformat = tformat.replace("AMPM", "%p")

			tz = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())

			datetime_object = datetime.strptime(stime, "{} {}".format(dformat, tformat)).replace(tzinfo=tz)
			base.debugmsg(5, "datetime_object:", datetime_object, datetime_object.timestamp())
			return int(datetime_object.timestamp())
		except Exception as e:
			base.debugmsg(8, "e:", e)
			return -1

	#
	# Report Settings
	#
	def rs_setting_get(self, name):
		base.debugmsg(9, "name:", name)
		if name in base.report["Report"]:
			return base.whitespace_get_ini_value(base.report["Report"][name])
		else:
			return None

	def rs_setting_set(self, name, value):
		base.debugmsg(9, "name:", name, "	value:", value)
		currvalue = ""
		if name in base.report["Report"]:
			currvalue = base.report["Report"][name]

		if currvalue != value:
			base.report["Report"][name] = base.whitespace_set_ini_value(value)
			# base.report_item_set_changed("Report")
			base.report_save()
			return 1
		else:
			return 0

	def rs_setting_get_int(self, name):
		value = base.rs_setting_get(name)
		if value is None:
			return -1
		else:
			return int(value)

	def rs_setting_set_int(self, name, value):
		changes = base.rs_setting_set(name, str(value))
		return changes

	def rs_setting_get_file(self, name):
		value = base.rs_setting_get(name)
		localpath = ""
		if value is not None and len(value) > 0:
			localpath = os.path.join(base.config['Reporter']['ResultDir'], value)
		return localpath

	def rs_setting_set_file(self, name, value):
		# determine relative path
		# base.config['Reporter']['Report']	base.config['Reporter']['ResultDir']
		if os.path.exists(value):
			relpath = os.path.relpath(value, start=base.config['Reporter']['ResultDir'])
			changes = base.rs_setting_set(name, relpath)
			return changes
		return 0

	def rs_setting_get_title(self):
		value = self.rs_setting_get('title')
		if value is None:
			reportname = 'Report Title'

			if 'Reporter' in base.config and 'Results' in base.config['Reporter']:
				results = base.config['Reporter']['Results']
				base.debugmsg(8, "results: ", results)
				if len(results) > 0:
					filename = os.path.basename(results)
					base.debugmsg(9, "filename: ", filename)
					basename, ext = os.path.splitext(filename)
					base.debugmsg(9, "basename: ", basename)
					basearr = basename.split('_')
					base.debugmsg(9, "basearr: ", basearr)
					basearr.pop(0)
					basearr.pop(0)
					reportname = " ".join(basearr)
					base.debugmsg(7, "reportname: ", reportname)
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
		base.debugmsg(6, "value", value)
		if not base.displaygui:
			base.debugmsg(6, "value", value)
			return value
		else:
			fontlst = list(tkFont.families())
			base.debugmsg(9, "fontlst", fontlst)
			if value not in fontlst:
				value = None
				base.debugmsg(6, "value", value)
			if value is None:
				# Verdana, Tahoma, Arial, Helvetica, sans-serif
				fontorder = ['Helvetica', 'Verdana', 'Tahoma', 'Arial', 'FreeSans']
				base.debugmsg(6, "fontorder", fontorder)
				for fnt in fontorder:
					if fnt in fontlst:
						base.debugmsg(6, "fnt", fnt)
						return fnt
				for fnt in fontlst:
					if 'Sans' in fnt or 'sans' in fnt:
						base.debugmsg(6, "fnt", fnt)
						return fnt
				base.debugmsg(6, "sans-serif")
				return 'sans-serif'
			else:
				base.debugmsg(6, "value", value)
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
		# ZI = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())
		return zoneinfo.available_timezones()

	def rs_setting_get_starttime(self):
		value = self.rs_setting_get_int('startoffset')
		base.debugmsg(5, "value:", value)
		if value < 1:
			return self.report_starttime()
		else:
			return self.report_starttime() + int(value)

	def rs_setting_get_endtime(self):
		value = self.rs_setting_get_int('endoffset')
		base.debugmsg(5, "value:", value)
		if value < 1:
			return self.report_endtime()
		else:
			return self.report_endtime() - int(value)

	#
	# Report Sections
	#

	def report_get_order(self, parent):
		if parent == "TOP":
			base.debugmsg(7, "template order:", base.report["Report"]["Order"])
			if len(base.report["Report"]["Order"]) > 0:
				return base.report["Report"]["Order"].split(',')
			else:
				return []
		else:
			base.debugmsg(7, "parent order:", base.report[parent])
			if "Order" in base.report[parent] and len(base.report[parent]["Order"]) > 0:
				return base.report[parent]["Order"].split(',')
			else:
				return []

	def report_set_order(self, parent, orderlst):
		base.debugmsg(7, "parent:", parent, "	orderlst: ", orderlst)
		if parent == "TOP":
			base.report["Report"]["Order"] = ",".join(orderlst)
		else:
			base.report[parent]["Order"] = ",".join(orderlst)
		base.report_save()
		return 1

	def report_new_section(self, parent, name):
		id = "{:02X}".format(int(time.time() * 10000))
		while id in base.report:
			time.sleep(0.1)
			id = "{:02X}".format(int(time.time() * 10000))

		base.debugmsg(7, "id:", id)
		self.report_add_section(parent, id, name)
		return id

	def report_add_subsection(self, id):
		if id not in base.report:
			base.report[id] = {}
			base.report_save()

	def report_subsection_parent(self, id):
		pid = id
		last = id[-1:]
		if last in ['G', 'H', 'I', 'J', 'k', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
			pid = id[0:-1]
			self.report_add_subsection(id)
		base.debugmsg(8, "id:", id, "	pid:", pid)
		return pid

	def report_add_section(self, parent, id, name):
		base.debugmsg(7, "parent: ", parent)
		if id not in base.report:
			base.report[id] = {}
		base.report[id]['Name'] = base.whitespace_set_ini_value(name)
		base.report[id]['Parent'] = base.whitespace_set_ini_value(parent)
		order = self.report_get_order(parent)
		base.debugmsg(8, "order: ", order)
		order.append(id)
		self.report_set_order(parent, order)
		base.debugmsg(8, "base.report: ", base.report._sections)

	def report_item_parent(self, id):
		if id in base.report and 'Parent' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['Parent'])
		else:
			return "TOP"

	def report_remove_section(self, id):
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		base.debugmsg(8, "order: ", order)
		pos = order.index(id)
		base.debugmsg(9, "pos: ", pos)
		order.pop(pos)
		base.debugmsg(9, "order: ", order)
		self.report_set_order(parent, order)
		base.debugmsg(9, "base.report: ", base.report._sections)
		subitems = self.report_get_order(id)
		for item in subitems:
			self.report_remove_section(item)
		del base.report[id]
		idl = id + 'L'
		if idl in base.report:
			del base.report[idl]
		idr = id + 'R'
		if idr in base.report:
			del base.report[idr]

		base.debugmsg(9, "base.report: ", base.report._sections)
		base.report_save()

	def report_move_section_up(self, id):
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		base.debugmsg(5, "order: ", order)
		pos = order.index(id)
		base.debugmsg(5, "pos: ", pos)
		order.pop(pos)
		order.insert(pos - 1, id)
		base.debugmsg(5, "order: ", order)
		self.report_set_order(parent, order)

	def report_move_section_down(self, id):
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		base.debugmsg(5, "order: ", order)
		pos = order.index(id)
		base.debugmsg(5, "pos: ", pos)
		order.pop(pos)
		order.insert(pos + 1, id)
		base.debugmsg(5, "order: ", order)
		self.report_set_order(parent, order)

	def report_item_get_changed(self, id):
		base.debugmsg(8, "id:", id)
		if id == 'TOP':
			return time.time()
		if 'Changed' not in base.report[id]:
			base.report_item_set_changed(id)
		base.debugmsg(8, "Changed:", base.report[id]['Changed'], "	", float(base.report[id]['Changed']))
		return float(base.report[id]['Changed'])

	def report_item_set_changed(self, id):
		base.report[id]['Changed'] = base.whitespace_set_ini_value(str(time.time()))
		return 1

	def report_item_set_changed_all(self, id):
		if id != "TOP":
			base.report_item_set_changed(id)

		sections = base.report_get_order(id)
		for sect in sections:
			base.report_item_set_changed_all(sect)

		base.report_save()

	def report_item_get_name(self, id):
		if id == "TOP":
			return "Report"
		if id in base.report:
			return base.whitespace_get_ini_value(base.report[id]['Name'])
		else:
			return None

	def report_item_set_name(self, id, newname):
		base.report[id]['Name'] = base.whitespace_set_ini_value(newname)
		base.report_item_set_changed(id)
		base.report_save()
		return 1

	def report_sect_level(self, id):
		base.debugmsg(9, "id:", id)
		parent = self.report_item_parent(id)
		if parent == "TOP":
			return 1
		else:
			parentlvl = self.report_sect_level(parent)
			return parentlvl + 1

	def report_sect_number(self, id):
		base.debugmsg(9, "id:", id)
		parent = self.report_item_parent(id)
		order = self.report_get_order(parent)
		num = order.index(id) + 1
		base.debugmsg(9, "parent:", parent, "	num:", num)
		if parent == "TOP":
			base.debugmsg(9, "return:", num)
			return "{}".format(num)
		else:
			parentnum = self.report_sect_number(parent)
			base.debugmsg(9, "parentnum:", parentnum)
			base.debugmsg(9, "return:", parentnum, num)
			return "{}.{}".format(parentnum, num)

	def report_item_get_type_lbl(self, id):
		base.debugmsg(9, "id:", id)
		type = base.report_item_get_type(id)
		base.debugmsg(5, "type:", type)
		return base.settings["ContentTypes"][type]

	def report_item_get_type(self, id):
		base.debugmsg(9, "id:", id)
		default = list(base.settings["ContentTypes"].keys())[0]
		base.debugmsg(9, "default:", default)
		if id == "TOP":
			return default
		if 'Type' not in base.report[id]:
			base.debugmsg(5, "Set to default:", default)
			base.report_item_set_type(id, default)

		base.debugmsg(9, "Type:", base.report[id]['Type'])
		return base.whitespace_get_ini_value(base.report[id]['Type'])

	def report_item_set_type(self, id, newType):
		base.debugmsg(5, "id:", id, "	newType:", newType)
		base.report[id]['Type'] = base.whitespace_set_ini_value(newType)
		base.report_item_set_changed(id)
		base.report_save()

	#
	# Report Sections values
	#

	def report_item_get_value(self, id, name):
		base.debugmsg(9, "id:", id, "name:", name)
		if id in base.report and name in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id][name])
		else:
			return None

	def report_item_set_value(self, id, name, value):
		base.debugmsg(9, "id:", id, "name:", name, "	value:", value)
		currvalue = ""
		if name in base.report[id]:
			currvalue = base.report[id][name]
		if currvalue != value:
			base.report[id][name] = base.whitespace_set_ini_value(value)
			# base.report_item_set_changed("Report")
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		else:
			return 0

	def report_item_get_int(self, id, name):
		value = base.report_item_get_value(id, name)
		if value is None:
			return -1
		else:
			return int(value)

	def report_item_set_int(self, id, name, value):
		changes = base.report_item_set_value(id, name, str(value))
		return changes

	def report_item_get_bool_def0(self, id, name):
		value = base.report_item_get_int(id, name)
		if value < 0:
			return 0
		else:
			return int(value)

	def report_item_get_bool_def1(self, id, name):
		value = base.report_item_get_int(id, name)
		if value < 0:
			return 1
		else:
			return int(value)

	def report_item_set_bool(self, id, name, value):
		changes = base.report_item_set_int(id, name, value)
		return changes

	#
	# Report Item Type: contents
	#

	def rt_contents_get_mode(self, id):
		base.debugmsg(8, "id:", id)
		if 'mode' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['mode'])
		else:
			return "Table Of Contents"

	def rt_contents_set_mode(self, id, mode):
		base.debugmsg(5, "id:", id, "	mode:", mode)
		changes = base.report_item_set_value(id, 'mode', mode)
		return changes

	def rt_contents_get_level(self, id):
		base.debugmsg(8, "id:", id)
		if id == "TOP":
			return 0
		if 'level' in base.report[id]:
			return int(base.report[id]['level'])
		else:
			return 1

	def rt_contents_set_level(self, id, level):
		base.debugmsg(5, "id:", id, "	level:", level)
		changes = base.report_item_set_value(id, 'level', str(level))
		return changes

	#
	# Report Item Type: note
	#

	def rt_note_get(self, id):
		base.debugmsg(9, "id:", id)
		if 'note' in base.report[id]:
			return self.whitespace_get_ini_value(base.report[id]['note'])
		else:
			return ""

	def rt_note_set(self, id, noteText):
		base.debugmsg(5, "id:", id, "	noteText:", noteText)
		prev = self.rt_note_get(id)
		if noteText != prev:
			base.report[id]['note'] = base.whitespace_set_ini_value(noteText)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0
		# changes = base.report_item_set_value(id, 'note', noteText)
		# return changes
	#
	# Report Item Type: graph
	#

	# 		pid, idl, idr = base.rt_graph_LR_Ids(id)
	def rt_graph_LR_Ids(self, id):
		if id != 'TOP':
			base.debugmsg(5, "id:", id)
			pid = base.report_subsection_parent(id)
			idl = pid + 'L'
			base.report_item_parent(idl)
			idr = pid + 'R'
			base.report_item_parent(idr)
			return pid, idl, idr
		else:
			return id, id + 'L', id + 'R'

	def rt_graph_get_sql(self, id):
		base.debugmsg(9, "id:", id)
		if 'SQL' in base.report[id]:
			return self.whitespace_get_ini_value(base.report[id]['SQL']).strip()
		else:
			return ""

	def rt_graph_set_sql(self, id, graphSQL):
		base.debugmsg(9, "id:", id, "	graphSQL:", graphSQL.strip())
		prev = self.rt_graph_get_sql(id)
		if graphSQL.strip() != prev:
			base.report[id]['SQL'] = base.whitespace_set_ini_value(graphSQL.strip())
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_graph_get_axisen(self, id):
		base.debugmsg(9, "id:", id)
		if id in base.report and 'AxisEn' in base.report[id]:
			return int(base.report[id]['AxisEn'])
		else:
			if id[-1:] == 'L':
				return 1
			else:
				return 0

	def rt_graph_set_axisen(self, id, value):
		base.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_graph_get_axisen(id)
		if value != prev and value is not None:
			base.report[id]['AxisEn'] = str(value)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_graph_get_dt(self, id):
		base.debugmsg(9, "id:", id)
		pid = base.report_subsection_parent(id)
		if 'DataType' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['DataType'])
		elif pid in base.report and 'DataType' in base.report[pid]:
			return base.whitespace_get_ini_value(base.report[pid]['DataType'])
		else:
			return None

	def rt_graph_set_dt(self, id, datatype):
		base.debugmsg(5, "id:", id, "	datatype:", datatype)
		prev = self.rt_table_get_dt(id)
		if datatype != prev and datatype is not None:
			base.report[id]['DataType'] = base.whitespace_set_ini_value(datatype)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_graph_generate_sql(self, id):
		base.debugmsg(8, "id:", id)
		sql = ""
		DataType = self.rt_table_get_dt(id)

		pid = base.report_subsection_parent(id)
		starttime = base.rt_setting_get_starttime(pid)
		base.debugmsg(5, "starttime:", starttime)
		endtime = base.rt_setting_get_endtime(pid)
		base.debugmsg(5, "endtime:", endtime)

		if DataType == "Result":
			RType = self.rt_table_get_rt(id)
			EnFR = self.rt_table_get_enfr(id)
			FRType = self.rt_table_get_fr(id)
			EnFA = self.rt_table_get_enfa(id)
			FAType = self.rt_table_get_fa(id)
			FNType = self.rt_table_get_fn(id)
			inpFP = self.rt_table_get_fp(id)
			colname = "Name"

			sql = "SELECT "

			base.debugmsg(8, "RType:", RType, "sql:", sql)

			if RType == "Response Time":
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
				sql += "floor(end_time) as 'Time' "
				sql += ", count(result) as 'Value' "
				# sql += ", result_name as 'Name' "
				sql += ", result_name"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "
			if RType == "Total TPS":
				sql += "floor(end_time) as 'Time'"
				sql += ", count(result) as 'Value' "
				# sql += ", result as 'Name' "
				sql += ", result"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "

			if RType in [None, "", "None"]:
				base.debugmsg(8, "RType:", RType, "sql:", sql)
				sql += "end_time as 'Time'"
				sql += ", count(result) as 'Value' "
				# sql += ", result_name as 'Name' "
				sql += ", result_name"
				if EnFR and FRType in [None, "", "None"]:
					sql += " || ' - ' || result"
				if EnFA and FAType in [None, "", "None"]:
					sql += " || ' - ' || agent"
				sql += " as [" + colname + "] "

			base.debugmsg(8, "RType:", RType, "sql:", sql)

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
				pass

			if RType == "TPS":
				sql += "GROUP by "
				sql += "floor(end_time) "
				sql += ", result_name "
				sql += ", result "
				sql += "ORDER by "
				sql += "floor(end_time)"
				sql += ", result DESC"
				sql += ", count(result) DESC "
			if RType == "Total TPS":
				sql += "GROUP by "
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
			colname = "Name"

			base.debugmsg(6, "MType:", MType, "	PM:", PM, "	SM:", SM)

			mnamecolumns = []
			# mcolumns = ["MetricTime as 'Time'", "MetricValue as 'Value'", "PrimaryMetric as 'Name'", "MetricType as 'Name'", "SecondaryMetric as 'Name'"]
			mcolumns = ["MetricTime as 'Time'", "MetricValue as 'Value'"]
			wherelst = []
			# grouplst = ["PrimaryMetric", "MetricType", "SecondaryMetric"]
			grouplst = []

			if MType not in [None, "", "None"] and len(MType) > 0:
				# if "MetricType as 'Name'" in mcolumns:
				# 	mcolumns.remove("MetricType as 'Name'")
				wherelst.append("MetricType == '{}'".format(MType.replace("'", "''")))
				if "MetricType" in grouplst:
					grouplst.remove("MetricType")
			else:
				mnamecolumns.append("MetricType")
			if PM not in [None, "", "None"] and len(PM) > 0:
				# if "PrimaryMetric as 'Name'" in mcolumns:
				# 	mcolumns.remove("PrimaryMetric as 'Name'")
				wherelst.append("PrimaryMetric == '{}'".format(PM.replace("'", "''")))
				if "PrimaryMetric" in grouplst:
					grouplst.remove("PrimaryMetric")
			else:
				mnamecolumns.append("PrimaryMetric")
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
					base.debugmsg(5, "mnamecolumns:", mnamecolumns)
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
			sql += "WHERE md0.MetricType = 'Scenario' AND md0.PrimaryMetric like 'Test_%' "

		base.debugmsg(5, "sql:", sql)
		self.rt_graph_set_sql(id, sql)
		return sql

	def rt_graph_floatval(self, value):
		try:
			return float(value)
		except Exception:
			return value

	#
	# Report Item Type: table
	#

	def rt_table_get_sql(self, id):
		base.debugmsg(9, "id:", id)
		if 'SQL' in base.report[id]:
			return self.whitespace_get_ini_value(base.report[id]['SQL']).strip()
		else:
			return ""

	def rt_table_set_sql(self, id, tableSQL):
		base.debugmsg(8, "id:", id, "	tableSQL:", tableSQL.strip())
		prev = self.rt_table_get_sql(id)
		if tableSQL.strip() != prev:
			base.report[id]['SQL'] = base.whitespace_set_ini_value(tableSQL.strip())
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_generate_sql(self, id):
		base.debugmsg(8, "id:", id)
		display_percentile = base.rs_setting_get_pctile()
		sql = ""
		DataType = self.rt_table_get_dt(id)

		starttime = base.rt_setting_get_starttime(id)
		endtime = base.rt_setting_get_endtime(id)

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
			sql += "WHERE md0.MetricType = 'Scenario' AND md0.PrimaryMetric like 'Test_%' "

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

			base.debugmsg(8, "MType:", MType, "	PM:", PM, "	SM:", SM)

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
			base.debugmsg(8, "gblist:", gblist)

			selcols = ", ".join(sellist)
			gbcols = ", ".join(gblist)

			base.debugmsg(8, "gbcols:", gbcols)

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

		base.debugmsg(8, "sql:", sql)
		self.rt_table_set_sql(id, sql)
		return sql

	def rt_table_get_colours(self, id):
		base.debugmsg(9, "id:", id)
		if 'Colours' in base.report[id]:
			return int(base.report[id]['Colours'])
		else:
			self.rt_table_set_colours(id, 0)
			return 0

	def rt_table_set_colours(self, id, colours):
		base.debugmsg(5, "id:", id, "	colours:", colours)
		if 'Colours' not in base.report[id]:
			base.report[id]['Colours'] = base.whitespace_set_ini_value(str(colours))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		else:
			prev = self.rt_table_get_colours(id)
			if colours != prev:
				base.report[id]['Colours'] = base.whitespace_set_ini_value(str(colours))
				base.report_item_set_changed(id)
				base.report_save()
				return 1
		return 0

	# 	rt_setting_get_starttime
	def rt_setting_get_starttime(self, id):
		# value = self.rs_setting_get_int('startoffset')
		value = base.report_item_get_int(id, 'startoffset')
		base.debugmsg(5, "value:", value)
		if value < 1:
			return self.rs_setting_get_starttime()
		else:
			return self.rs_setting_get_starttime() + int(value)

	def rt_setting_get_endtime(self, id):
		# value = self.rs_setting_get_int('endoffset')
		value = base.report_item_get_int(id, 'endoffset')
		base.debugmsg(5, "value:", value)
		if value < 1:
			return self.rs_setting_get_endtime()
		else:
			return self.rs_setting_get_endtime() - int(value)

	def rt_table_get_dt(self, id):
		base.debugmsg(9, "id:", id)
		if 'DataType' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['DataType'])
		else:
			return None

	def rt_table_set_dt(self, id, datatype):
		base.debugmsg(9, "id:", id, "	datatype:", datatype)
		prev = self.rt_table_get_dt(id)
		base.debugmsg(8, "prev:", prev)
		if datatype != prev and datatype is not None:
			base.report[id]['DataType'] = base.whitespace_set_ini_value(datatype)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_rt(self, id):
		base.debugmsg(9, "id:", id)
		if 'ResultType' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['ResultType'])
		else:
			return None

	def rt_table_set_rt(self, id, resulttype):
		base.debugmsg(9, "id:", id, "	resulttype:", resulttype)
		prev = self.rt_table_get_rt(id)
		if resulttype != prev and resulttype is not None:
			base.report[id]['ResultType'] = base.whitespace_set_ini_value(resulttype)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_ini_colname(self, name):
		base.debugmsg(5, "id:", id, "	name:", name)
		colname = "col_{}".format(base.whitespace_set_ini_value(name)).replace(" ", "_").replace(".", "")
		base.debugmsg(5, "colname:", colname)
		return colname

	def rt_table_get_colname(self, id, name):
		base.debugmsg(5, "id:", id, "	name:", name)
		colname = self.rt_table_ini_colname(name)
		if colname in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id][colname])
		else:
			return name

	def rt_table_set_colname(self, id, name, value):
		base.debugmsg(5, "id:", id, "	name:", name, "	value:", value)
		colname = self.rt_table_ini_colname(name)
		prev = self.rt_table_get_colname(id, name)
		if value != prev and value not in [None, ""]:
			base.report[id][colname] = base.whitespace_set_ini_value(value)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		if value in [None, ""]:
			base.report[id][colname] = base.whitespace_set_ini_value(name)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_fr(self, id):
		base.debugmsg(9, "id:", id)
		if 'FilterResult' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['FilterResult'])
		else:
			return None

	def rt_table_set_fr(self, id, filterresult):
		base.debugmsg(9, "id:", id, "	filterresult:", filterresult)
		prev = self.rt_table_get_fr(id)
		if filterresult != prev and filterresult is not None:
			base.report[id]['FilterResult'] = base.whitespace_set_ini_value(filterresult)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_enfr(self, id):
		base.debugmsg(5, "id:", id)
		pid = base.report_subsection_parent(id)
		if id in base.report and 'EnableFilterResult' in base.report[id]:
			return int(base.report[id]['EnableFilterResult'])
		elif pid in base.report and 'EnableFilterResult' in base.report[pid]:
			return int(base.report[pid]['EnableFilterResult'])
		else:
			frv = self.rt_table_get_fr(id)
			if frv in ["Pass", "Fail"]:
				return 1
			return 0

	def rt_table_set_enfr(self, id, value):
		base.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_enfr(id)
		if value != prev and value is not None:
			base.report[id]['EnableFilterResult'] = base.whitespace_set_ini_value(str(value))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	# FA FilterAgent
	def rt_table_get_fa(self, id):
		base.debugmsg(5, "id:", id)
		if 'FilterAgent' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['FilterAgent'])
		else:
			return None

	def rt_table_set_fa(self, id, value):
		base.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_fa(id)
		if value != prev and value is not None:
			base.report[id]['FilterAgent'] = base.whitespace_set_ini_value(value)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_alst(self, id):
		base.debugmsg(9, "id:", id)
		# SELECT agent
		# FROM Results
		# GROUP BY agent
		mtype = self.rt_table_get_mt(id)
		alst = [None, ""]
		sql = "SELECT agent 'Name' "
		sql += "FROM Results "
		sql += "GROUP BY agent "
		base.debugmsg(6, "sql:", sql)
		key = "{}_{}_AgentList".format(id, mtype)
		base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)

		adata = base.dbqueue["ReadResult"][key]
		base.debugmsg(8, "adata:", adata)
		for a in adata:
			alst.append(a["Name"])

		base.debugmsg(5, "alst:", alst)

		return alst

	def rt_table_get_malst(self, id):
		base.debugmsg(9, "id:", id)
		# SELECT agent
		# FROM Results
		# GROUP BY agent
		mtype = self.rt_table_get_mt(id)
		alst = [None, ""]

		sql = "SELECT ma.Name  'Name' "
		sql += "FROM Metrics m "
		sql += "	LEFT JOIN Metric ma ON m.DataSource = ma.ID "
		sql += "GROUP BY m.DataSource "

		base.debugmsg(6, "sql:", sql)
		key = "{}_{}_MetricAgentList".format(id, mtype)
		base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)

		adata = base.dbqueue["ReadResult"][key]
		base.debugmsg(8, "adata:", adata)
		for a in adata:
			alst.append(a["Name"])

		base.debugmsg(5, "alst:", alst)

		return alst

	def rt_table_get_enfa(self, id):
		base.debugmsg(5, "id:", id)
		pid = base.report_subsection_parent(id)
		if id in base.report and 'EnableFilterAgent' in base.report[id]:
			return int(base.report[id]['EnableFilterAgent'])
		elif pid in base.report and 'EnableFilterAgent' in base.report[pid]:
			return int(base.report[pid]['EnableFilterAgent'])
		else:
			return 0

	def rt_table_set_enfa(self, id, value):
		base.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_enfa(id)
		if value != prev and value is not None:
			base.report[id]['EnableFilterAgent'] = base.whitespace_set_ini_value(str(value))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	# FN FilterType
	def rt_table_get_fn(self, id):
		base.debugmsg(9, "id:", id)
		if 'FilterType' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['FilterType'])
		else:
			return None

	def rt_table_set_fn(self, id, filtertype):
		base.debugmsg(5, "id:", id, "	filtertype:", filtertype)
		prev = self.rt_table_get_fr(id)
		if filtertype != prev and filtertype not in [None, "None"]:
			base.report[id]['FilterType'] = base.whitespace_set_ini_value(filtertype)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		elif filtertype != prev and filtertype in [None, "None"] and prev in [None, "None"]:
			base.report[id]['FilterType'] = base.whitespace_set_ini_value(None)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	# FP FilterPattern
	def rt_table_get_fp(self, id):
		base.debugmsg(9, "id:", id)
		if 'FilterPattern' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['FilterPattern'])
		else:
			return ""

	def rt_table_set_fp(self, id, filterpattern):
		base.debugmsg(5, "id:", id, "	filterpattern:", filterpattern)
		prev = self.rt_table_get_fp(id)
		if filterpattern != prev and filterpattern is not None:
			base.report[id]['FilterPattern'] = base.whitespace_set_ini_value(filterpattern)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	# mt MetricType
	def rt_table_get_mt(self, id):
		base.debugmsg(9, "id:", id)
		pid = base.report_subsection_parent(id)
		if 'MetricType' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['MetricType'])
		elif pid in base.report and 'MetricType' in base.report[pid]:
			return base.whitespace_get_ini_value(base.report[pid]['MetricType'])
		else:
			return ""

	def rt_table_set_mt(self, id, metrictype):
		base.debugmsg(5, "id:", id, "	metrictype:", metrictype)
		prev = self.rt_table_get_mt(id)
		if metrictype != prev and metrictype is not None:
			base.report[id]['MetricType'] = base.whitespace_set_ini_value(metrictype)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_mlst(self, id):
		base.debugmsg(9, "id:", id)
		mlst = [None, ""]
		sql = "SELECT Type "
		sql += "FROM Metric "
		sql += "GROUP BY Type "
		base.debugmsg(6, "sql:", sql)
		key = "{}_Metrics".format(id)
		base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = base.dbqueue["ReadResult"][key]
		base.debugmsg(8, "tdata:", tdata)
		for m in tdata:
			mlst.append(m["Type"])

		return mlst

	# pm PrimaryMetric
	def rt_table_get_pm(self, id):
		base.debugmsg(9, "id:", id)
		pid = base.report_subsection_parent(id)
		if 'PrimaryMetric' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['PrimaryMetric'])
		elif pid in base.report and 'PrimaryMetric' in base.report[pid]:
			return base.whitespace_get_ini_value(base.report[pid]['PrimaryMetric'])
		else:
			return ""

	def rt_table_set_pm(self, id, primarymetric):
		base.debugmsg(5, "id:", id, "	primarymetric:", primarymetric)
		prev = self.rt_table_get_pm(id)
		if primarymetric != prev and primarymetric is not None:
			base.report[id]['PrimaryMetric'] = base.whitespace_set_ini_value(primarymetric)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_pmlst(self, id):
		base.debugmsg(9, "id:", id)
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
		base.debugmsg(6, "sql:", sql)
		key = "{}_{}_PMetrics".format(id, mtype)
		base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = base.dbqueue["ReadResult"][key]
		base.debugmsg(8, "tdata:", tdata)
		for m in tdata:
			pmlst.append(m["Name"])

		base.debugmsg(5, "pmlst:", pmlst)

		return pmlst

	# sm SecondaryMetric
	def rt_table_get_sm(self, id):
		base.debugmsg(9, "id:", id)
		pid = base.report_subsection_parent(id)
		if 'SecondaryMetric' in base.report[id]:
			return base.whitespace_get_ini_value(base.report[id]['SecondaryMetric'])
		elif pid in base.report and 'SecondaryMetric' in base.report[pid]:
			return base.whitespace_get_ini_value(base.report[pid]['SecondaryMetric'])
		else:
			return ""

	def rt_table_set_sm(self, id, secondarymetric):
		base.debugmsg(5, "id:", id, "	secondarymetric:", secondarymetric)
		prev = self.rt_table_get_sm(id)
		if secondarymetric != prev and secondarymetric is not None:
			base.report[id]['SecondaryMetric'] = base.whitespace_set_ini_value(secondarymetric)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_smlst(self, id):
		base.debugmsg(9, "id:", id)
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
		base.debugmsg(6, "sql:", sql)
		key = "{}_{}_{}_SMetrics".format(id, mtype, pmtype)
		base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = base.dbqueue["ReadResult"][key]
		base.debugmsg(8, "tdata:", tdata)
		for m in tdata:
			smlst.append(m["SecondaryMetric"])

		base.debugmsg(5, "smlst:", smlst)

		return smlst

	def rt_table_get_isnumeric(self, id):
		base.debugmsg(9, "id:", id)
		pid = base.report_subsection_parent(id)
		if id in base.report and 'IsNumeric' in base.report[id]:
			return int(base.report[id]['IsNumeric'])
		elif pid in base.report and 'IsNumeric' in base.report[pid]:
			return int(base.report[pid]['IsNumeric'])
		else:
			return 0

	def rt_table_set_isnumeric(self, id, value):
		base.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_isnumeric(id)
		if value != prev and value is not None:
			base.report[id]['IsNumeric'] = base.whitespace_set_ini_value(str(value))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_table_get_showcount(self, id):
		base.debugmsg(9, "id:", id)
		pid = base.report_subsection_parent(id)
		if id in base.report and 'ShowCount' in base.report[id]:
			return int(base.report[id]['ShowCount'])
		elif pid in base.report and 'ShowCount' in base.report[pid]:
			return int(base.report[pid]['ShowCount'])
		else:
			return 0

	def rt_table_set_showcount(self, id, value):
		base.debugmsg(5, "id:", id, "	value:", value)
		prev = self.rt_table_get_showcount(id)
		if value != prev and value is not None:
			base.report[id]['ShowCount'] = base.whitespace_set_ini_value(str(value))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	#
	# Report Item Type: errors
	#

	def rt_errors_get_sql(self, id):
		base.debugmsg(9, "id:", id)
		if 'SQL' in base.report[id]:
			return self.whitespace_get_ini_value(base.report[id]['SQL']).strip()
		else:
			return ""

	def rt_errors_set_sql(self, id, tableSQL):
		base.debugmsg(8, "id:", id, "	tableSQL:", tableSQL.strip())
		prev = self.rt_table_get_sql(id)
		if tableSQL.strip() != prev:
			base.report[id]['SQL'] = base.whitespace_set_ini_value(tableSQL.strip())
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	def rt_errors_generate_sql(self, id):
		base.debugmsg(8, "id:", id)

		starttime = base.rt_setting_get_starttime(id)
		endtime = base.rt_setting_get_endtime(id)

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

		base.debugmsg(8, "sql:", sql)
		self.rt_errors_set_sql(id, sql)
		return sql

	def rt_errors_get_images(self, id):
		base.debugmsg(9, "id:", id)
		if 'Images' in base.report[id]:
			return int(base.report[id]['Images'])
		else:
			self.rt_errors_set_images(id, 1)
			return 1

	def rt_errors_set_images(self, id, images):
		base.debugmsg(5, "id:", id, "	images:", images)
		if 'Images' not in base.report[id]:
			base.report[id]['Images'] = base.whitespace_set_ini_value(str(images))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		else:
			prev = self.rt_errors_get_images(id)
			if images != prev:
				base.report[id]['Images'] = base.whitespace_set_ini_value(str(images))
				base.report_item_set_changed(id)
				base.report_save()
				return 1
		return 0

	def rt_errors_get_group_rn(self, id):
		base.debugmsg(9, "id:", id)
		if 'GroupRN' in base.report[id]:
			return int(base.report[id]['GroupRN'])
		else:
			self.rt_errors_set_group_rn(id, 1)
			return 1

	def rt_errors_set_group_rn(self, id, group):
		base.debugmsg(5, "id:", id, "	group:", group)
		if 'GroupRN' not in base.report[id]:
			base.report[id]['GroupRN'] = base.whitespace_set_ini_value(str(group))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		else:
			prev = self.rt_errors_get_group_rn(id)
			if group != prev:
				base.report[id]['GroupRN'] = base.whitespace_set_ini_value(str(group))
				base.report_item_set_changed(id)
				base.report_save()
				return 1
		return 0

	def rt_errors_get_group_et(self, id):
		base.debugmsg(9, "id:", id)
		if 'GroupET' in base.report[id]:
			return int(base.report[id]['GroupET'])
		else:
			self.rt_errors_set_group_et(id, 1)
			return 1

	def rt_errors_set_group_et(self, id, group):
		base.debugmsg(5, "id:", id, "	group:", group)
		if 'GroupET' not in base.report[id]:
			base.report[id]['GroupET'] = base.whitespace_set_ini_value(str(group))
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		else:
			prev = self.rt_errors_get_group_et(id)
			if group != prev:
				base.report[id]['GroupET'] = base.whitespace_set_ini_value(str(group))
				base.report_item_set_changed(id)
				base.report_save()
				return 1
		return 0

	def rt_errors_get_data(self, id):
		base.debugmsg(5, "id:", id)
		key = "{}_{}".format(id, base.report_item_get_changed(id))

		if id not in base.reportdata:
			base.reportdata[id] = {}

		if "key" in base.reportdata[id] and base.reportdata[id]["key"] != key:
			base.reportdata[id] = {}

		sql = base.rt_errors_generate_sql(id)
		base.debugmsg(5, "sql:", sql)
		# colours = base.rt_table_get_colours(id)
		if sql is not None and len(sql.strip()) > 0:
			base.debugmsg(5, "sql:", sql)
			base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
			base.reportdata[id]["key"] = key
			while key not in base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = base.dbqueue["ReadResult"][key]
			base.debugmsg(5, "tdata:", tdata)

			if len(tdata) > 0:
				cols = list(tdata[0].keys())
				base.debugmsg(5, "cols:", cols)

				for rowi in tdata:
					base.debugmsg(9, "rowi:", rowi)
					rid = rowi['id']
					base.debugmsg(8, "rid:", rid)
					if rid not in base.reportdata[id]:
						base.reportdata[id][rid] = rowi
					if rid in base.reportdata[id] and "error" not in base.reportdata[id][rid]:
						base.rt_errors_parse_xml(id, rid)
				base.debugmsg(9, "base.reportdata[", id, "]:", base.reportdata[id])
		return base.reportdata[id]

	def rt_errors_parse_xml(self, id, rid):
		base.debugmsg(5, "id:", id, "	rid:", rid)
		if id in base.reportdata and rid in base.reportdata[id]:
			rdata = base.reportdata[id][rid]
			base.debugmsg(8, "rdata:", rdata)

			# rdir = base.config['Reporter']['ResultDir']
			# base.debugmsg(5, "rdir:", rdir)
			dbfile = base.config['Reporter']['Results']
			base.debugmsg(9, "dbfile:", dbfile)

			ldir = os.path.join(os.path.dirname(dbfile), "logs")
			base.debugmsg(8, "ldir:", ldir)

			# 		opencart_1_1_1690876686_1_1690876693/Opencart_Sales_output.xml
			gxpatt = os.path.join(ldir, "{}_{}_{}_*_{}_*".format(rdata['script'].split('.')[0], rdata['script_index'], rdata['robot'], rdata['iteration']), "*_output.xml")
			base.debugmsg(9, "gxpatt:", gxpatt)

			xmlf = "not_found"
			xmll = glob.glob(gxpatt, recursive=True)
			if len(xmll) > 0:
				xmlf = glob.glob(gxpatt, recursive=True)[0]
			base.debugmsg(5, "xmlf:", xmlf)

			if os.path.isfile(xmlf):
				base.reportdata[id][rid]['xml_file'] = xmlf

				# tree = etree.parse(xmlf)
				with open(xmlf, 'rb') as xml_file:
					tree = etree.parse(xml_file)
				root = tree.getroot()
				base.debugmsg(9, "root:", root)

				# //suite/@source	--> 	/tmp/rfswarmagent/scripts/opencart.robot
				suites = root.findall(".//suite")
				base.debugmsg(9, "suites:", suites)
				source = suites[0].get('source')
				base.debugmsg(8, "source:", source)

				# //kw/status[@status='FAIL']/../msg[@level='FAIL']

				failkws = root.findall(".//kw/status[@status='FAIL']/..")
				base.debugmsg(9, "failkws:", failkws)

				if len(failkws) > 0:
					failkw = failkws[-1]
					failmsg = failkw.find("msg[@level='FAIL']")
					base.debugmsg(5, "failmsg:", failmsg, failmsg.text)

					base.reportdata[id][rid]['error'] = failmsg.text

					# //kw/status[@status='FAIL']/../msg[@level='INFO'] --> html decode for img tag
					# //kw/status[@status='FAIL']/../msg[@level='INFO' and @html='true']
					# </td></tr><tr><td colspan="3"><a href="selenium-screenshot-1.png"><img src="selenium-screenshot-1.png" width="800px"></a>
					# infomsg = failkw.find("msg[@level='INFO' and @html='true']")

					infomsg = failkw.find("msg[@html='true']")
					if infomsg is not None:
						base.debugmsg(5, "infomsg:", infomsg, infomsg.text)

						# <a[^>]*href="([^"]*)
						# m = re.search(r'<a[^>]*href="([^"]*)', infomsg.text)
						m = re.search(r'<img[^>]*src="([^"]*)', infomsg.text)
						image = m.group(1)
						base.debugmsg(5, "image:", image)
						if image is not None:
							imgdir = os.path.dirname(xmlf)
							imagef = os.path.join(imgdir, image)

							if os.path.isfile(imagef):
								base.debugmsg(5, "imagef:", imagef)
								base.reportdata[id][rid]['image'] = image
								base.reportdata[id][rid]['image_file'] = imagef

	def rt_errors_get_label(self, id, lblname):
		base.debugmsg(5, "id:", id, "	lblname:", lblname)
		if lblname in base.report[id]:
			base.debugmsg(5, "id:", id, "	lblname:", lblname, "	retvalue:", base.whitespace_get_ini_value(base.report[id][lblname]))
			return base.whitespace_get_ini_value(base.report[id][lblname])
		else:
			base.debugmsg(5, "id:", id, "	lblname:", lblname, "	retvalue:", base.defaultlabels[lblname])
			return base.defaultlabels[lblname]

	def rt_errors_set_label(self, id, lblname, lblvalue):
		base.debugmsg(5, "id:", id, "	lblname:", lblname, "	lblvalue:", lblvalue)
		prev = self.rt_table_get_colname(id, lblname)
		if lblvalue != prev and lblvalue not in [None, ""]:
			base.report[id][lblname] = base.whitespace_set_ini_value(lblvalue)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		if lblvalue in [None, ""]:
			base.report[id][lblname] = base.whitespace_set_ini_value(lblname)
			base.report_item_set_changed(id)
			base.report_save()
			return 1
		return 0

	#
	# Result data db Functions
	#
	def column_in_table(self, table, column):
		sql = "SELECT 1 [HasColumn] FROM pragma_table_info('{}') WHERE Name = '{}'".format(table, column)
		base.debugmsg(8, "sql:", sql)
		key = "HasColumn_{}_{}".format(table, column)
		base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
		while key not in base.dbqueue["ReadResult"]:
			time.sleep(0.1)

		tdata = base.dbqueue["ReadResult"][key]
		base.debugmsg(8, "tdata:", tdata)
		hascol = 0
		if len(tdata) > 0:
			# table headers
			if "HasColumn" in tdata[0]:
				hascol = tdata[0]["HasColumn"]

		if "DBTable" not in base.settings:
			base.settings["DBTable"] = {}
		if table not in base.settings["DBTable"]:
			base.settings["DBTable"][table] = {}
		base.settings["DBTable"][table][column] = hascol
		# base.settings["DBTable"]['Metrics']['DataSource']

	def open_results_db(self, dbpath):
		self.close_results_db()
		if self.datadb is None:
			base.debugmsg(5, "Connect to DB")
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
		# base.config['Reporter']['Results']
		if self.datadb is not None:
			base.run_dbthread = False
			base.debugmsg(5, "Disconnect and close DB")
			self.datadb.commit()
			self.datadb.close()
			self.datadb = None

	def run_db_thread(self):
		while base.run_dbthread:
			if self.datadb is None:
				base.debugmsg(9, "open results database")
				if len(base.config['Reporter']['Results']) > 0:
					self.open_results_db(base.config['Reporter']['Results'])
				else:
					base.run_dbthread = False

			if self.datadb is not None:

				# process db queues

				# General Write
				if len(base.dbqueue["Write"]) > 0:
					base.debugmsg(9, "run_db_thread: dbqueue: Write")
					tmpq = list(base.dbqueue["Write"])
					base.dbqueue["Write"] = []
					base.debugmsg(9, "run_db_thread: dbqueue: Write: tmpq:", tmpq)
					for item in tmpq:
						if item["SQL"] and item["VALUES"]:
							try:
								base.debugmsg(9, "run_db_thread: dbqueue: Write: SQL:", item["SQL"], " 	VALUES:", item["VALUES"])
								cur = self.datadb.cursor()
								cur.execute(item["SQL"], item["VALUES"])
								cur.close()
								self.datadb.commit()
							except Exception as e:
								base.debugmsg(1, "run_db_thread: dbqueue: Write: Exception:", e)
								base.debugmsg(1, "run_db_thread: dbqueue: Write: Item:", item)
						else:
							base.debugmsg(1, "run_db_thread: dbqueue: Write: Item not written, missing key SQL or VALUES")
							base.debugmsg(1, "run_db_thread: dbqueue: Write: Item:", item)

				# General Read
				if len(base.dbqueue["Read"]) > 0:
					base.debugmsg(9, "run_db_thread: dbqueue: Read")
					tmpq = list(base.dbqueue["Read"])
					base.dbqueue["Read"] = []
					base.debugmsg(9, "run_db_thread: dbqueue: Read: tmpq:", tmpq)
					for item in tmpq:
						if "SQL" in item:
							try:
								base.debugmsg(9, "run_db_thread: dbqueue: Read: SQL:", item["SQL"])
								self.datadb.row_factory = self.dict_factory
								cur = self.datadb.cursor()
								cur.execute(item["SQL"])
								result = cur.fetchall()
								base.debugmsg(9, "run_db_thread: dbqueue: Read: result:", result)
								cur.close()
								self.datadb.commit()

								base.debugmsg(9, "run_db_thread: dbqueue: Read: result:", result)
								if "KEY" in item:
									base.dbqueue["ReadResult"][item["KEY"]] = result

							except Exception as e:
								base.debugmsg(1, "run_db_thread: dbqueue: Read: Exception:", e)
								base.debugmsg(1, "run_db_thread: dbqueue: Read: Item:", item)
						else:
							base.debugmsg(1, "run_db_thread: dbqueue: Read: Item not written, missing key SQL or VALUES")
							base.debugmsg(1, "run_db_thread: dbqueue: Read: Item:", item)

			time.sleep(0.1)
			# end of while base.run_dbthread

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
		base.run_dbthread = True
		base.dbthread = threading.Thread(target=base.run_db_thread)
		base.dbthread.start()

	def stop_db(self):
		base.run_dbthread = False
		if base.dbthread is not None:
			base.dbthread.join()
			base.dbthread = None
			# clear queue cached results
			base.dbqueue = {"Write": [], "Read": [], "ReadResult": {}, "Results": [], "Metric": [], "Metrics": []}

	#
	# Colour Functions
	#

	def named_colour(self, name):
		if name.lower() not in base.namecolours:
			base.namecolours.append(name.lower())
		return self.line_colour(base.namecolours.index(name.lower()))

	def line_colour(self, grp):
		if grp < len(base.defcolours):
			return base.defcolours[grp]
		else:
			newcolour = self.get_colour()
			base.debugmsg(9, "Initial newcolour:", newcolour)
			while newcolour in base.defcolours:
				base.debugmsg(9, base.defcolours)
				newcolour = self.get_colour()
				base.debugmsg(9, "newcolour:", newcolour)
			base.defcolours.append(newcolour)
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
		base.debugmsg(5, "datain:", datain)
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
			base.debugmsg(5, "rowin:", rowin)
			if 'PrimaryMetric' in rowin and "_" in rowin['PrimaryMetric']:
				key, index = rowin['PrimaryMetric'].rsplit("_", 1)
				base.debugmsg(5, "key:", key, "	index:", index)
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
				base.debugmsg(5, "Unexpected data in rowin:", rowin)

		for index in data.keys():
			base.debugmsg(5, "index:", index, data[index])

			eventtime = data[index]["start"]
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += 0
			else:
				totaldata[eventtime] = 0

			eventtime += int(data[index]["delay"])
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
			eventtime += int(data[index]["rampup"])
			rowout = {}
			rowout["Time"] = eventtime
			rowout["Value"] = 0
			rowout["Name"] = data[index]["colourkey"]
			dataout.append(rowout)

			if eventtime in totaldata:
				totaldata[eventtime] += int(data[index]["robots"]) * -1
			else:
				totaldata[eventtime] = int(data[index]["robots"]) * -1

		stot = base.report_item_get_int(id, "ShowTotal")

		if stot > 0:
			robots = 0
			for key in totaldata.keys():
				base.debugmsg(5, "key:", key, totaldata[key])
				robots += totaldata[key]
				rowout = {}
				rowout["Time"] = key
				rowout["Value"] = robots
				rowout["Name"] = "Total"
				dataout.append(rowout)

		base.debugmsg(5, "dataout:", dataout)
		return dataout

	def table_postprocess_data_plan(self, id, datain):
		base.debugmsg(5, "datain:", datain)
		# [
		# 	{'PrimaryMetric': 'Delay_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '0', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Ramp_Up_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '20', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Robots_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '30', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'},
		# 	{'PrimaryMetric': 'Run_1', 'MetricType': 'Scenario', 'MetricTime': 1719370859, 'SecondaryMetric': 'Jpetstore 01', 'MetricValue': '60', 'DataSource': 'hp-elite-desk-800-g3', 'File': 'jpetstore.robot', 'FilePath': '/home/dave/Documents/tmp/jpetstore/jpetstore.robot'}
		# ]
		# 	 Index		Robots		Delay  		RampUp 		Run		Script		Test	Settings
		dataout = []
		data = {}

		scriptopt = base.report_item_get_value(id, base.rt_table_ini_colname("Script Opt"))
		if scriptopt is None:
			scriptopt = "File"

		for rowin in datain:
			base.debugmsg(5, "rowin:", rowin)
			if 'PrimaryMetric' in rowin and "_" in rowin['PrimaryMetric']:
				key, index = rowin['PrimaryMetric'].rsplit("_", 1)
				base.debugmsg(5, "key:", key, "	index:", index)
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
				base.debugmsg(5, "Unexpected data in rowin:", rowin)

		for index in data.keys():
			base.debugmsg(5, "index:", index, data[index])

			datarow = {}
			# 	 Index		Robots		Delay  		RampUp 		Run		Script		Test	Settings
			datarow["Colour"] = data[index]["Colour"]
			datarow["Index"] = data[index]["Index"]
			datarow["Robots"] = data[index]["Robots"]
			datarow["Delay"] = base.sec2hms(data[index]["Delay"])
			datarow["Ramp Up"] = base.sec2hms(data[index]["Ramp Up"])
			datarow["Run"] = base.sec2hms(data[index]["Run"])
			if scriptopt == "File":
				datarow["Script"] = data[index]["Script"]
			else:
				datarow["Script"] = data[index]["ScriptPath"]
			datarow["Test"] = data[index]["Test"]

			dataout.append(datarow)

		base.debugmsg(5, "dataout:", dataout)
		return dataout


class ReporterCore:

	cg_data: Any = {}
	t_export: Any = {}

	def __init__(self, master=None):
		base.debugmsg(0, "Robot Framework Swarm: Reporter")
		base.debugmsg(0, "	Version", base.version)
		signal.signal(signal.SIGINT, self.on_closing)

		font_manager._get_fontconfig_fonts.cache_clear()

		base.debugmsg(9, "ArgumentParser")
		# Check for command line args
		parser = argparse.ArgumentParser()
		parser.add_argument('-g', '--debug', help='Set debug level, default level is 0')
		parser.add_argument('-v', '--version', help='Display the version and exit', action='store_true')
		parser.add_argument('-i', '--ini', help='path to alternate ini file')
		parser.add_argument('-n', '--nogui', help='Don\'t display the GUI', action='store_true')
		parser.add_argument('-d', '--dir', help='Results directory')
		parser.add_argument('-t', '--template', help='Specify the template')
		parser.add_argument('--html', help='Generate a HTML report', action='store_true')
		# parser.add_argument('--pdf', help='Generate a PDF report', action='store_true')
		parser.add_argument('--docx', help='Generate a MS Word report', action='store_true')
		parser.add_argument('--xlsx', help='Generate a MS Excel report', action='store_true')
		# parser.add_argument('--odt', help='Generate an OpenOffice/LibreOffice Writer report', action='store_true')
		# parser.add_argument('--ods', help='Generate an OpenOffice/LibreOffice Calc report', action='store_true')
		parser.add_argument('-c', '--create', help='ICON : Create application icon / shortcut')
		base.args = parser.parse_args()

		base.debugmsg(6, "base.args: ", base.args)

		if base.args.debug:
			base.debuglvl = int(base.args.debug)

		if base.args.version:
			exit()

		if base.args.create:
			if base.args.create.upper() in ["ICON", "ICONS"]:
				self.create_icons()
			else:
				base.debugmsg(0, "create with option ", base.args.create.upper(), "not supported.")
			exit()

		if base.args.nogui:
			base.displaygui = False

		base.debugmsg(6, "ConfigParser")
		base.config = configparser.ConfigParser()

		#
		# 	ensure ini file
		#
		base.reporter_ini = base.findiniloctaion()

		if base.args.ini:
			base.save_ini = False
			base.debugmsg(5, "base.args.ini: ", base.args.ini)
			base.reporter_ini = base.args.ini

		if os.path.isfile(base.reporter_ini):
			base.debugmsg(7, "reporter_ini: ", base.reporter_ini)
			base.config.read(base.reporter_ini, encoding="utf8")
		else:
			base.saveini()

		base.debugmsg(0, "	Configuration File: ", base.reporter_ini)

		base.debugmsg(9, "base.config: ", base.config._sections)

		#
		# GUI
		#
		if 'GUI' not in base.config:
			base.config['GUI'] = {}
			base.saveini()

		if 'win_width' not in base.config['GUI']:
			base.config['GUI']['win_width'] = "800"
			base.saveini()

		if 'win_height' not in base.config['GUI']:
			base.config['GUI']['win_height'] = "390"
			base.saveini()

		if 'donation_reminder' not in base.config['GUI']:
			base.config['GUI']['donation_reminder'] = "0"
			base.saveini()

		#
		# Reporter
		#

		if 'Reporter' not in base.config:
			base.config['Reporter'] = {}
			base.saveini()

		if 'ResultDir' not in base.config['Reporter']:
			base.config['Reporter']['ResultDir'] = base.dir_path
			base.saveini()
		else:
			if not os.path.isdir(base.config['Reporter']['ResultDir']):
				base.config['Reporter']['ResultDir'] = base.dir_path
				base.saveini()

		if 'Results' not in base.config['Reporter']:
			base.config['Reporter']['Results'] = ""
			base.saveini()
		else:
			if not os.path.isfile(base.config['Reporter']['Results']):
				base.config['Reporter']['Results'] = ""
				base.saveini()

		if 'Report' not in base.config['Reporter']:
			base.config['Reporter']['Report'] = ""
			base.saveini()
		else:
			if not os.path.isfile(base.config['Reporter']['Report']):
				base.config['Reporter']['Report'] = ""
				base.saveini()

		if 'Template' not in base.config['Reporter']:
			base.config['Reporter']['Template'] = ""
			base.saveini()
		else:
			if not os.path.isfile(base.config['Reporter']['Template']):
				base.config['Reporter']['Template'] = ""
				base.saveini()

		if 'TemplateDir' not in base.config['Reporter']:
			base.config['Reporter']['TemplateDir'] = ""
			base.saveini()
		else:
			if not os.path.isdir(base.config['Reporter']['TemplateDir']):
				base.config['Reporter']['TemplateDir'] = ""
				base.saveini()

		usetemplate = False
		if base.args.template:
			usetemplate = True
			base.config['Reporter']['Template'] = base.whitespace_set_ini_value(base.args.template)

		if base.args.dir:
			# do some sanity checks before blindly setting
			rdir = base.args.dir
			base.debugmsg(5, "rdir:", rdir)
			if os.path.exists(rdir):
				if os.path.isfile(rdir):
					rdir = os.path.dirname(rdir)
					base.debugmsg(5, "rdir:", rdir)
				dname = os.path.basename(rdir)
				dbfile = "{}.db".format(dname)
				dbpath = os.path.join(rdir, dbfile)
				base.debugmsg(5, "dbpath:", dbpath)
				if os.path.isfile(dbpath):
					base.config['Reporter']['Results'] = dbpath

		self.selectResults(base.config['Reporter']['Results'])

		if not usetemplate and "Report" in base.config['Reporter'] \
			and len(base.config['Reporter']['Report']) \
			and os.path.isfile(base.config['Reporter']['Report']):
			base.report_open()
		else:
			base.template_open(base.whitespace_get_ini_value(base.config['Reporter']['Template']))
			base.report_save()

		if base.args.html:
			# self.export_xhtml()
			self.t_export["xhtml"] = threading.Thread(target=self.export_xhtml)
			self.t_export["xhtml"].start()

		if base.args.docx:
			# self.export_word()
			self.t_export["docx"] = threading.Thread(target=self.export_word)
			self.t_export["docx"].start()

		if base.args.xlsx:
			# self.export_excel()
			self.t_export["xlsx"] = threading.Thread(target=self.export_excel)
			self.t_export["xlsx"].start()

		if base.displaygui:
			base.gui = ReporterGUI()
		else:
			# t_export
			for thd in self.t_export.keys():
				self.t_export[thd].join()
			self.on_closing()

	def mainloop(self):

		base.debugmsg(5, "mainloop start")

		if base.displaygui:
			base.gui.mainloop()

	def on_closing(self, _event=None, *extras):
		base.running = False
		base.debugmsg(5, "base.running:", base.running)

		base.debugmsg(5, "Close results db")
		# base.close_results_db()
		base.stop_db()

		time.sleep(1)
		base.debugmsg(2, "Exit")
		try:
			sys.exit(0)
		except SystemExit as e:
			try:
				remaining_threads = [t for t in threading.enumerate() if t is not threading.main_thread() and t.is_alive()]
				if remaining_threads:
					base.debugmsg(5, "Failed to gracefully exit RFSwarm-Reporter. Forcing immediate exit.")
					for thread in remaining_threads:
						base.debugmsg(9, "Thread name:", thread.name)
					os._exit(0)
				else:
					raise e

			except Exception as e:
				base.debugmsg(3, "Failed to exit with error:", e)
				os._exit(1)

	def create_icons(self):
		base.debugmsg(0, "Creating application icons for RFSwarm Reporter")
		appname = "RFSwarm Reporter"
		namelst = appname.split()
		base.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		base.debugmsg(6, "projname:", projname)
		pipdata = importlib.metadata.distribution(projname)
		# print("files:", pipdata.files)
		# print("file0:", pipdata.files[0])
		reporter_executable = os.path.abspath(str(pipdata.locate_file(pipdata.files[0])))
		base.debugmsg(5, "reporter_executable:", reporter_executable)

		script_dir = os.path.dirname(os.path.abspath(__file__))
		base.debugmsg(5, "script_dir:", script_dir)
		icon_dir = os.path.join(pipdata.locate_file('rfswarm_reporter'), "icons")
		base.debugmsg(5, "icon_dir:", icon_dir)

		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				try:
					base.ensuredir("/usr/share/applications")
					directoryfilename = os.path.join("/usr/share/applications", "rfswarm.directory")
					directorydata = ["test"]
					with open(directoryfilename, 'w') as df:
						df.writelines(directorydata)
					os.remove(directoryfilename)
					fileprefix = "/usr/share"
				except Exception:
					pass

			fileprefix = os.path.expanduser(fileprefix)

			# base.debugmsg(5, "Create .directory file")
			# directorydata = []
			# directorydata.append('[Desktop Entry]\n')
			# directorydata.append('Type=Directory\n')
			# directorydata.append('Name=RFSwarm\n')
			# directorydata.append('Icon=rfswarm-logo\n')
			#
			# directoryfilename = os.path.join(fileprefix, "desktop-directories", "rfswarm.directory")
			# directorydir = os.path.dirname(directoryfilename)
			# base.ensuredir(directorydir)
			#
			# base.debugmsg(5, "directoryfilename:", directoryfilename)
			# with open(directoryfilename, 'w') as df:
			# 	df.writelines(directorydata)
			#
			# directoryfilename = os.path.join(fileprefix, "applications", "rfswarm.directory")
			# directorydir = os.path.dirname(directoryfilename)
			# base.ensuredir(directorydir)
			# base.debugmsg(5, "directoryfilename:", directoryfilename)
			# with open(directoryfilename, 'w') as df:
			# 	df.writelines(directorydata)

			base.debugmsg(5, "Create .desktop file")
			desktopdata = []
			desktopdata.append('[Desktop Entry]\n')
			desktopdata.append('Name=' + appname + '\n')
			desktopdata.append('Exec=' + reporter_executable + '\n')
			desktopdata.append('Terminal=false\n')
			desktopdata.append('Type=Application\n')
			desktopdata.append('Icon=' + projname + '\n')
			desktopdata.append('Categories=RFSwarm;Development;\n')
			desktopdata.append('Keywords=rfswarm;reporter;\n')
			# desktopdata.append('\n')

			dektopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
			dektopdir = os.path.dirname(dektopfilename)
			base.ensuredir(dektopdir)

			base.debugmsg(5, "dektopfilename:", dektopfilename)
			with open(dektopfilename, 'w') as df:
				df.writelines(desktopdata)

			base.debugmsg(5, "Copy icons")
			# /usr/share/icons/hicolor/128x128/apps/
			# 	1024x1024  128x128  16x16  192x192  22x22  24x24  256x256  32x32  36x36  42x42  48x48  512x512  64x64  72x72  8x8  96x96
			# or
			#  ~/.local/share/icons/hicolor/256x256/apps/
			src_iconx128 = os.path.join(icon_dir, projname + "-128.png")
			base.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", projname + ".png")
			dst_icondir = os.path.dirname(dst_iconx128)
			base.ensuredir(dst_icondir)
			base.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

			src_iconx128 = os.path.join(icon_dir, "rfswarm-logo-128.png")
			base.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", "rfswarm-logo.png")
			base.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

		if platform.system() == 'Darwin':
			base.debugmsg(5, "Create folder structure in /Applications")

			src_iconx1024 = os.path.join(icon_dir, projname + "-1024.png")

			self.create_macos_app_bundle(appname, pipdata.version, reporter_executable, src_iconx1024)

		if platform.system() == 'Windows':
			base.debugmsg(5, "Create Startmenu shorcuts")
			roam_appdata = os.environ["APPDATA"]
			scutpath = os.path.join(roam_appdata, "Microsoft", "Windows", "Start Menu", appname + ".lnk")
			src_iconx128 = os.path.join(icon_dir, projname + "-128.ico")

			self.create_windows_shortcut(scutpath, reporter_executable, src_iconx128, "Performance testing with robot test cases", True)

	def create_windows_shortcut(self, scutpath, targetpath, iconpath, desc, minimised=False):
		pslst = []

		directorydir = os.path.dirname(scutpath)
		base.ensuredir(directorydir)

		pslst.append("$wshshell = New-Object -COMObject wscript.shell")
		pslst.append('$scut = $wshshell.CreateShortcut("""' + scutpath + '""")')
		pslst.append('$scut.TargetPath = """' + targetpath + '"""')
		pslst.append('$scut.IconLocation = """' + iconpath + '"""')
		if minimised:
			pslst.append("$scut.WindowStyle = 7")
		pslst.append("$scut.Description = '" + desc + "'")
		pslst.append("$scut.Save()")

		# psscript = '\n'.join(pslst)
		psscript = '; '.join(pslst)
		base.debugmsg(6, "psscript:", psscript)

		response = os.popen('powershell.exe -command ' + psscript).read()

		base.debugmsg(6, "response:", response)

	def create_macos_app_bundle(self, name, version, exesrc, icosrc):

		appspath = "~/Applications"
		if os.access("/Applications", os.W_OK):
			appspath = "/Applications"

		appspath = os.path.expanduser(appspath)

		# https://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

		apppath = os.path.join(appspath, name + ".app")
		MacOSFolder = os.path.join(apppath, "Contents", "MacOS")
		base.ensuredir(MacOSFolder)

		# need to create the icon file:
		# https://stackoverflow.com/questions/646671/how-do-i-set-the-icon-for-my-applications-mac-os-x-app-bundle
		namelst = name.split()
		base.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		base.debugmsg(6, "projname:", projname)
		signature = "RFS{0}".format(namelst[1].upper())
		base.debugmsg(6, "signature:", signature)

		ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
		iconset = os.path.join(ResourcesFolder, projname + ".iconset")
		icnsfile = os.path.join(ResourcesFolder, projname + ".icns")
		base.ensuredir(iconset)

		# Normal screen icons
		base.debugmsg(6, "Normal screen icons")
		for size in [16, 32, 64, 128, 256, 512]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{0}x{0}.png'".format(size, icosrc, iconset)
			base.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			base.debugmsg(6, "response:", response)

		# Retina display icons
		base.debugmsg(6, "Retina display icons")
		for size in [32, 64, 128, 256, 512, 1024]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{3}x{3}x2.png'".format(size, icosrc, iconset, int(size / 2))
			base.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			base.debugmsg(6, "response:", response)

		# Make a multi-resolution Icon
		base.debugmsg(6, "Make a multi-resolution Icon")
		cmd = "iconutil -c icns -o '{0}' '{1}'".format(icnsfile, iconset)
		base.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		base.debugmsg(6, "response:", response)

		#  create apppath + "/Contents/Info.plist"
		bundleName = name
		bundleIdentifier = "org.rfswarm." + projname

		# https://stackoverflow.com/questions/1596945/building-osx-app-bundle
		# Found 2 issues:
		# 	- <xml and <plist wasn't closed with > and xml was missing encoding
		# 	- APPL???? --> RFS<SIGNATURE_NAME>

		Infoplist = os.path.join(apppath, "Contents", "Info.plist")
		with open(Infoplist, "w") as f:
			f.write("""<?xml version="1.0" encoding="UTF-8"?>
			<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
			<plist version="1.0">
			<dict>
				<key>CFBundleDevelopmentRegion</key>
				<string>English</string>
				<key>CFBundleExecutable</key>
				<string>%s</string>
				<key>CFBundleGetInfoString</key>
				<string>%s</string>
				<key>CFBundleIconFile</key>
				<string>%s.icns</string>
				<key>CFBundleIdentifier</key>
				<string>%s</string>
				<key>CFBundleInfoDictionaryVersion</key>
				<string>6.0</string>
				<key>CFBundleName</key>
				<string>%s</string>
				<key>CFBundlePackageType</key>
				<string>APPL</string>
				<key>CFBundleShortVersionString</key>
				<string>%s</string>
				<key>CFBundleSignature</key>
				<string>%s</string>
				<key>CFBundleVersion</key>
				<string>%s</string>
				<key>NSAppleScriptEnabled</key>
				<string>YES</string>
				<key>NSMainNibFile</key>
				<string>MainMenu</string>
				<key>NSPrincipalClass</key>
				<string>NSApplication</string>
			</dict>
			</plist>
			""" % (projname, bundleName + " " + version, projname, bundleIdentifier, bundleName, version, signature, version))
			f.close()

		# create apppath + "/Contents/PkgInfo"
		PkgInfo = os.path.join(apppath, "Contents", "PkgInfo")
		with open(PkgInfo, "w") as f:
			f.write("APPL%s" % signature)
			f.close()

		# apppath + "/Contents/MacOS/main.py"
		execbundle = os.path.join(apppath, "Contents", "MacOS", projname)
		if os.path.exists(execbundle):
			os.remove(execbundle)
		os.symlink(exesrc, execbundle)

		# touch '/Applications/RFSwarm Reporter.app' to update .app icon
		cmd = "touch '{0}'".format(apppath)
		base.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		base.debugmsg(6, "response:", response)

		# # Try re-registering your application with Launch Services:
		# # /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f /Applications/MyTool.app
		# lsregister = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
		# cmd = "{0} -f '{1}'".format(lsregister, apppath)
		# base.debugmsg(6, "cmd:", cmd)
		# response = os.popen(cmd).read()
		# base.debugmsg(6, "response:", response)

	def selectResults(self, resultsfile):
		base.debugmsg(5, "resultsfile:", resultsfile)

		if len(resultsfile) > 0:

			base.stop_db()

			base.config['Reporter']['Results'] = resultsfile

			tplfres = os.path.splitext(resultsfile)
			freport = "{}.report".format(tplfres[0])
			base.debugmsg(9, "freport:", freport)
			base.config['Reporter']['Report'] = freport

			filedir = os.path.dirname(resultsfile)
			base.debugmsg(9, "filedir:", filedir)
			parent = os.path.dirname(filedir)
			base.debugmsg(9, "parent:", parent)
			base.config['Reporter']['ResultDir'] = parent
			base.saveini()
			# base.open_results_db(base.config['Reporter']['Results'])
			base.start_db()

	def display_message(self, *mesage):
		if base.displaygui:
			msglst = []
			for msg in mesage:
				msglst.append(msg)
			msgout = " ".join(msglst)
			while base.gui is None and base.running:
				time.sleep(0.5)
			base.gui.updateStatus(msgout)
		else:
			msglst = []
			for msg in mesage:
				msglst.append(msg)
			msgout = " ".join(msglst)
			base.debugmsg(1, msgout)

	def export_xhtml(self):
		self.display_message("Generating XHTML Report")

		sections = base.report_get_order("TOP")
		base.debugmsg(5, "sections:", sections)
		sectionpct = 1 / (len(sections) + 1)
		base.debugmsg(5, "sectionpct:", sectionpct)

		if "XHTML" in self.cg_data:
			if "progress" in self.cg_data["XHTML"] and self.cg_data["XHTML"]["progress"] < 1:
				self.display_message("Waiting for previous XHTML report to finish")
				while self.cg_data["XHTML"]["progress"] < 1:
					time.sleep(0.5)
			del self.cg_data["XHTML"]
		self.cg_data["XHTML"] = {}
		self.cg_data["XHTML"]["progress"] = 0.0

		self.cg_data["XHTML"]["html"] = self.xhtml_base_doc()

		# set HTML Title
		title = self.cg_data["XHTML"]["html"].xpath("//head/title")[0]
		title.text = base.rs_setting_get_title()

		head = self.cg_data["XHTML"]["html"].xpath("//head")[0]

		style = etree.SubElement(head, 'style')
		highlightcolour = base.rs_setting_get_hcolour()
		fontname = base.rs_setting_get_font()
		fontsize = base.rs_setting_get_fontsize()

		styledata = ""
		styledata += "div { font-size: " + str(fontsize) + "px; font-family: \"" + fontname + "\"; }"
		styledata += ".center { text-align: center; }"
		styledata += ".title { font-size: 200%;}"
		styledata += ".subtitle { font-size: 150%;}"

		styledata += "table, th, td { border: 1px solid #ccc; border-collapse: collapse; }"
		styledata += "th { color: " + highlightcolour + "; }"

		# pre	{white-space: pre-wrap;}
		styledata += "pre	{white-space: pre-wrap;}"

		for i in range(6):
			styledata += "h" + str(i + 1) + "	{ color: " + highlightcolour + "; margin-left: " + str(i * 5) + "px; }"

		bodyindent = 30
		styledata += ".body { margin-left: " + str(bodyindent) + "px; }"
		#   margin-left: 20px;
		for i in range(6):
			styledata += ".TOC" + str(i + 1) + "	{margin-left: " + str(i * 10) + "px;}"

		style.text = styledata

		body = self.cg_data["XHTML"]["html"].xpath("//body")[0]

		# self.cg_data["XHTML"]["html"] =
		self.xhtml_add_sections(body, "TOP", sectionpct)

		base.debugmsg(5, "Report:", base.config['Reporter']['Report'])
		reportbase, reportext = os.path.splitext(base.config['Reporter']['Report'])

		outfile = "{}.html".format(reportbase)
		self.xhtml_save(outfile, self.cg_data["XHTML"]["html"])

		base.debugmsg(5, "outfile:", outfile)
		self.display_message("Saved XHTML Report:", outfile)

		self.cg_data["XHTML"]["progress"] = 1

	def export_pdf(self):
		base.debugmsg(5, "Not implimented yet.....")

	def export_word(self):
		self.display_message("Generating Word Report")

		sections = base.report_get_order("TOP")
		base.debugmsg(5, "sections:", sections)
		sectionpct = 1 / (len(sections) + 1)
		base.debugmsg(5, "sectionpct:", sectionpct)

		if "docx" in self.cg_data:
			if "progress" in self.cg_data["docx"] and self.cg_data["docx"]["progress"] < 1:
				self.display_message("Waiting for previous Word report to finish")
				while self.cg_data["docx"]["progress"] < 1:
					time.sleep(0.5)
			del self.cg_data["docx"]
		self.cg_data["docx"] = {}
		self.cg_data["docx"]["progress"] = 0.0

		self.cg_data["docx"]["document"] = Document()

		self.docx_configure_style()

		self.docx_add_sections("TOP", sectionpct)

		base.debugmsg(5, "Report:", base.config['Reporter']['Report'])
		reportbase, reportext = os.path.splitext(base.config['Reporter']['Report'])
		outfile = "{}.docx".format(reportbase)
		self.cg_data["docx"]["document"].save(outfile)

		base.debugmsg(5, "outfile:", outfile)
		self.display_message("Saved Word Report:", outfile)

		self.cg_data["docx"]["progress"] = 1

	def export_writer(self):
		base.debugmsg(5, "Not implimented yet.....")

	def export_excel(self):
		self.display_message("Generating Excel Report")

		sections = base.report_get_order("TOP")
		base.debugmsg(5, "sections:", sections)
		sectionpct = 1 / (len(sections) + 1)
		base.debugmsg(5, "sectionpct:", sectionpct)

		if "xlsx" in self.cg_data:
			if "progress" in self.cg_data["xlsx"] and self.cg_data["xlsx"]["progress"] < 1:
				self.display_message("Waiting for previous Excel report to finish")
				while self.cg_data["xlsx"]["progress"] < 1:
					time.sleep(0.5)
			del self.cg_data["xlsx"]
		self.cg_data["xlsx"] = {}
		self.cg_data["xlsx"]["progress"] = 0.0

		self.cg_data["xlsx"]["Workbook"] = openpyxl.Workbook()

		self.xlsx_configure_style()

		self.xlsx_add_sections("TOP", sectionpct)

		self.cg_data["xlsx"]["Workbook"].active = self.cg_data["xlsx"]["Workbook"].worksheets[0]

		base.debugmsg(5, "Report:", base.config['Reporter']['Report'])
		reportbase, reportext = os.path.splitext(base.config['Reporter']['Report'])
		outfile = "{}.xlsx".format(reportbase)
		self.cg_data["xlsx"]["Workbook"].save(outfile)

		base.debugmsg(5, "outfile:", outfile)
		self.display_message("Saved Excel Report:", outfile)

		self.cg_data["xlsx"]["progress"] = 1

	def export_calc(self):
		base.debugmsg(5, "Not implimented yet.....")

	#
	# 	XHTML
	#

	def xhtml_save(self, filename, html):
		result = etree.tostring(
			html,
			xml_declaration=True,
			doctype='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
			encoding='utf-8',
			standalone=False,
			with_tail=False,
			method='html',
			pretty_print=True)

		with open(filename, "wb") as f:
			f.write(result)

	def xhtml_base_doc(self):
		# https://www.w3schools.com/html/html_xhtml.asp

		# <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
		# "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
		# <html xmlns="http://www.w3.org/1999/xhtml">
		# <head>
		#   <title>Title of document</title>
		# </head>
		# <body>
		#
		#   some content here...
		#
		# </body>
		# </html>

		M = ElementMaker(namespace=None, nsmap={None: "http://www.w3.org/1999/xhtml"})
		# html = M.html(E.head(E.title("Test page")), E.body(E.p("Hello world")))
		html = M.html(E.head(E.title("Test page"), E.meta(charset="utf-8")), E.body())

		return html

	def xhtml_add_sections(self, parent, id, sectionpct):
		base.debugmsg(8, "id:", id, "	sectionpct:", sectionpct)
		# SubElement(_parent, _tag, attrib=None, nsmap=None, **_extra)
		# thiselmt = E.SubElement(parent, 'div', attrib={'id':id})

		base.debugmsg(9, "parent:", parent)

		sections = base.report_get_order(id)
		base.debugmsg(9, "sections:", sections)

		thiselmt = etree.SubElement(parent, 'div')
		nextparent = thiselmt
		if id == "TOP":
			thiselmt.set("id", "TitlePage")
			nextparent = parent

			#
			# Title
			#
			maintitle = etree.SubElement(thiselmt, 'div')
			maintitle.set("class", "title center")
			maintitle.text = base.rs_setting_get_title()

			#
			# Logo
			#
			base.debugmsg(5, "showtlogo:", base.rs_setting_get_int("showtlogo"))
			if base.rs_setting_get_int("showtlogo"):
				imgtitle = etree.SubElement(thiselmt, 'div')
				imgtitle.set("class", "center")

				tlogo = base.rs_setting_get_file("tlogo")
				base.debugmsg(5, "tlogo:", tlogo)
				if len(tlogo) > 0:
					self.xhtml_sections_fileimg(imgtitle, id, tlogo)

			#
			# Execution Date range
			#
			subtitle = etree.SubElement(thiselmt, 'div')
			subtitle.set("class", "subtitle center")
			execdr = ""
			if base.rs_setting_get_int("showstarttime"):
				iST = base.rs_setting_get_starttime()
				fSD = "{}".format(base.report_formatdate(iST))
				fST = "{}".format(base.report_formattime(iST))

				execdr = "{} {}".format(fSD, fST)

			if base.rs_setting_get_int("showendtime"):
				iET = base.rs_setting_get_endtime()
				fED = "{}".format(base.report_formatdate(iET))
				fET = "{}".format(base.report_formattime(iET))

				if not base.rs_setting_get_int("showstarttime"):
					execdr = "{} {}".format(fED, fET)
				else:
					if fSD == fED:
						execdr = "{} - {}".format(execdr, fET)
					else:
						execdr = "{} - {} {}".format(execdr, fED, fET)

			subtitle.text = execdr

		else:
			thiselmt.set("id", id)
			newsectionpct = 1 / (len(sections) + 1)
			sectionpct = newsectionpct * sectionpct
			base.debugmsg(9, "sectionpct:", sectionpct)
			self.xhtml_sections_addheading(thiselmt, id)

			stype = base.report_item_get_type(id)
			base.debugmsg(9, "stype:", stype)
			if stype == "contents":
				self.xhtml_sections_contents(thiselmt, id)
			if stype == "note":
				self.xhtml_sections_note(thiselmt, id)
			if stype == "graph":
				self.xhtml_sections_graph(thiselmt, id)
			if stype == "table":
				self.xhtml_sections_table(thiselmt, id)
			if stype == "errors":
				self.xhtml_sections_errors(thiselmt, id)

		self.cg_data["XHTML"]["progress"] += sectionpct
		self.display_message("Generating XHTML Report {}%".format(int(round(self.cg_data["XHTML"]["progress"] * 100, 0))))

		if len(sections) > 0:
			for sect in sections:
				self.xhtml_add_sections(nextparent, sect, sectionpct)

	def xhtml_sections_addheading(self, elmt, id):
		base.debugmsg(8, "id:", id)
		level = base.report_sect_level(id)
		base.debugmsg(9, "level:", level)
		number = base.report_sect_number(id)
		base.debugmsg(9, "number:", number)
		name = base.report_item_get_name(id)
		base.debugmsg(9, "name:", name)

		tag = "h{}".format(level)

		h = etree.SubElement(elmt, tag)
		h.text = "{} {}".format(number, name)
		# a = etree.SubElement(h, 'a')
		# a.text = "{} {}".format(number, name)
		# a.set('href', "#{}".format(id))

	def xhtml_sections_fileimg(self, elmt, id, imgfile):
		base.debugmsg(5, "id:", id, "	imgfile:", imgfile)
		# img.set("src", imgfile)

		oimg = Image.open(imgfile)
		base.debugmsg(9, "oimg:", oimg)
		self.xhtml_sections_embedimg(elmt, id, oimg)

	def xhtml_sections_embedimg(self, elmt, id, oimg):
		base.debugmsg(8, "id:", id, "	oimg:", oimg)

		img = etree.SubElement(elmt, 'img')

		img.set("id", id + "_img")
		img.set("imgid", id)
		img.text = ""

		# <img src="data:image/png;base64,
		base.debugmsg(9, "oimg format:", oimg.format)
		# base.debugmsg(5, "oimg info:", oimg.info)

		# <img src="data:image/png;base64,
		srcdata = "data:image/" + oimg.format.lower() + ";base64,"

		# https://stackoverflow.com/questions/48229318/how-to-convert-image-pil-into-base64-without-saving
		# srcdata += str(base64.b64encode(oimg.tobytes()))
		# srcdata += base64.b64encode(oimg.tobytes()) # bytes
		# srcdata += base64.b64encode(oimg.tobytes()).decode()

		buffered = BytesIO()
		oimg.save(buffered, format=oimg.format)
		buffered.seek(0)
		img_byte = buffered.getvalue()

		srcdata += base64.b64encode(img_byte).decode()

		base.debugmsg(9, "srcdata:", srcdata)
		img.set("src", srcdata)

	def xhtml_sections_contents(self, elmt, id):
		base.debugmsg(8, "id:", id)
		mode = base.rt_contents_get_mode(id)
		level = base.rt_contents_get_level(id)

		base.debugmsg(9, "mode:", mode, "	level:", level)
		fmode = None
		if mode == "Table Of Contents":
			fmode = None
		if mode == "Table of Graphs":
			fmode = "graph"
		if mode == "Table Of Tables":
			fmode = "table"

		# tbl = etree.SubElement(elmt, 'table')
		body = etree.SubElement(elmt, 'div')
		body.set("class", "body")

		self.xhtml_sections_contents_row(body, "TOP", 1, fmode, level)
		# self.xhtml_sections_contents_row(tbl, "TOP", 1, fmode, level)

	def xhtml_sections_contents_row(self, elmt, id, rownum, fmode, flevel):
		base.debugmsg(8, "id:", id, "	rownum:", rownum, "	fmode:", fmode, "	flevel:", flevel)
		display = True

		level = base.report_sect_level(id)
		if id == "TOP":
			display = False
			level = 0
		base.debugmsg(9, "level:", level)

		if display and fmode is not None:
			display = False
			type = base.report_item_get_type(id)
			if fmode == type:
				display = True

		if display and level > flevel:
			display = False

		nextrow = rownum
		if display:
			type = base.report_item_get_type(id)
			titlenum = base.report_sect_number(id)
			titlename = base.report_item_get_name(id)
			# titlelevel = base.report_sect_level(id)

			p = etree.SubElement(elmt, 'p')
			a = etree.SubElement(p, 'a')
			a.set("class", "TOC{}".format(level))
			a.text = "{} {}".format(titlenum, titlename)
			if fmode is None:
				idpre = "toc"
			else:
				idpre = fmode
			a.set('id', "{}_{}".format(idpre, id))
			a.set('href', "#{}".format(id))

			nextrow = rownum + 1
		base.debugmsg(9, "nextrow:", nextrow)
		if level < flevel:
			children = base.report_get_order(id)
			for child in children:
				nextrow = self.xhtml_sections_contents_row(elmt, child, nextrow, fmode, flevel)
		return nextrow

	def xhtml_sections_note(self, elmt, id):
		base.debugmsg(8, "id:", id)
		notebody = base.rt_note_get(id)
		notebody = notebody.replace("\r\n", "\n")
		notebody = notebody.replace("\r", "\n")
		notelist = notebody.split("\n")
		base.debugmsg(9, "notebody:", notebody)
		body = etree.SubElement(elmt, 'div')
		body.set("class", "body")
		for line in notelist:
			p = etree.SubElement(body, "p")
			p.text = line

	def xhtml_sections_graph(self, elmt, id):
		base.debugmsg(8, "id:", id)
		pid, idl, idr = base.rt_graph_LR_Ids(id)
		base.debugmsg(5, "pid:", pid, "	idl:", idl, "	idr:", idr)

		body = etree.SubElement(elmt, 'div')
		body.set("class", "body")

		axisenl = base.rt_graph_get_axisen(idl)
		axisenr = base.rt_graph_get_axisen(idr)

		datatypel = base.rt_graph_get_dt(idl)
		datatyper = base.rt_graph_get_dt(idr)

		tz = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())

		if datatypel == "SQL":
			sqll = base.rt_graph_get_sql(idl)
		else:
			sqll = base.rt_graph_generate_sql(idl)

		if datatyper == "SQL":
			sqlr = base.rt_graph_get_sql(idr)
		else:
			sqlr = base.rt_graph_generate_sql(idr)

		gphdpi = 72
		# gphdpi = 100
		fig = Figure(dpi=gphdpi)
		axisl = fig.add_subplot(1, 1, 1)
		axisl.grid(True, 'major', 'x')
		axisr = axisl.twinx()

		fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')

		canvas = FigureCanvas(fig)

		# https://stackoverflow.com/questions/57316491/how-to-convert-matplotlib-figure-to-pil-image-object-without-saving-image
		axisl.tick_params(labelleft=False, length=0)
		axisr.tick_params(labelright=False, length=0)

		try:
			canvas.draw()
		except Exception as e:
			base.debugmsg(3, "canvas.draw() Exception:", e)
		fig.set_tight_layout(True)

		dodraw = False
		graphdata = {}

		if (sqll is not None and len(sqll.strip()) > 0) or (sqlr is not None and len(sqlr.strip()) > 0):

			if sqll is not None and len(sqll.strip()) > 0 and axisenl > 0:
				base.debugmsg(7, "sqll:", sqll)
				key = "{}_{}".format(idl, base.report_item_get_changed(idl))
				base.dbqueue["Read"].append({"SQL": sqll, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]

				if datatypel == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idl, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in graphdata:
							graphdata[name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							graphdata[name]["Colour"] = colour
							graphdata[name]["Axis"] = "axisL"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							graphdata[name]["objTime"] = []
							graphdata[name]["Values"] = []

						graphdata[name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						graphdata[name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			if sqlr is not None and len(sqlr.strip()) > 0 and axisenr > 0:
				base.debugmsg(7, "sqlr:", sqlr)
				key = "{}_{}".format(idr, base.report_item_get_changed(idr))
				base.dbqueue["Read"].append({"SQL": sqlr, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]

				if datatyper == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idr, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in graphdata:
							graphdata[name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							graphdata[name]["Colour"] = colour
							graphdata[name]["Axis"] = "axisR"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							graphdata[name]["objTime"] = []
							graphdata[name]["Values"] = []

						graphdata[name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						graphdata[name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			base.debugmsg(9, "graphdata:", graphdata)

			for name in graphdata:
				base.debugmsg(7, "name:", name)

				axis = "axisL"
				if "Axis" in graphdata[name]:
					axis = graphdata[name]["Axis"]

				if len(graphdata[name]["Values"]) > 1 and len(graphdata[name]["Values"]) == len(graphdata[name]["objTime"]):
					try:
						if axis == "axisL":
							axisl.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name)
						elif axis == "axisR":
							axisr.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name)
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

				if len(graphdata[name]["Values"]) == 1 and len(graphdata[name]["Values"]) == len(graphdata[name]["objTime"]):
					try:
						if axis == "axisL":
							axisl.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name, marker='o')
						elif axis == "axisR":
							axisr.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name, marker='o')
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

			if dodraw:

				# Left axis Limits
				if axisenl > 0:
					axisl.grid(True, 'major', 'y')
					axisl.tick_params(labelleft=True, length=5)

					SMetric = "Other"
					if datatypel == "Metric":
						SMetric = base.rt_table_get_sm(idl)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						axisl.set_ylim(0, 100)
					else:
						axisl.set_ylim(0)

				# Right axis Limits
				if axisenr > 0:
					axisr.grid(True, 'major', 'y')
					axisr.tick_params(labelright=True, length=5)

					SMetric = "Other"
					if datatyper == "Metric":
						SMetric = base.rt_table_get_sm(idr)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						axisr.set_ylim(0, 100)
					else:
						axisr.set_ylim(0)

				fig.set_tight_layout(True)
				fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
				try:
					canvas.draw()
				except Exception as e:
					base.debugmsg(3, "canvas.draw() Exception:", e)

				buf = BytesIO()
				fig.savefig(buf)
				buf.seek(0)
				oimg = Image.open(buf)
				self.xhtml_sections_embedimg(body, id, oimg)

	def xhtml_sections_table(self, elmt, id):
		base.debugmsg(8, "id:", id)
		body = etree.SubElement(elmt, 'div')
		body.set("class", "body")
		tbl = etree.SubElement(body, 'table')

		datatype = base.rt_table_get_dt(id)
		if datatype == "SQL":
			sql = base.rt_table_get_sql(id)
		else:
			sql = base.rt_table_generate_sql(id)
		colours = base.rt_table_get_colours(id)

		if sql is not None and len(sql.strip()) > 0:
			base.debugmsg(9, "sql:", sql)
			key = "{}_{}".format(id, base.report_item_get_changed(id))
			base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
			while key not in base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = base.dbqueue["ReadResult"][key]
			if datatype == "Plan":
				base.debugmsg(9, "tdata before:", tdata)
				tdata = base.table_postprocess_data_plan(id, tdata)
			base.debugmsg(9, "tdata:", tdata)

			if len(tdata) > 0:
				# table headers
				cols = list(tdata[0].keys())
				base.debugmsg(8, "cols:", cols)
				tr = etree.SubElement(tbl, 'tr')
				if colours:
					th = etree.SubElement(tr, 'th')
				for col in cols:
					if col not in ["Colour"]:
						show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
						if show:
							dispname = base.rt_table_get_colname(id, col)
							th = etree.SubElement(tr, 'th')
							th.text = dispname.strip()

				# table rows
				for row in tdata:
					vals = list(row.values())
					base.debugmsg(8, "vals:", vals)
					tr = etree.SubElement(tbl, 'tr')
					if colours:

						base.debugmsg(9, "row:", row)
						if "Colour" in row:
							label = row["Colour"]
						else:
							label = row[cols[0]]
						base.debugmsg(9, "label:", label)
						colour = base.named_colour(label)
						base.debugmsg(9, "colour:", colour)

						# <td style="background-color:#8888ff; color:#8888ff;">_</td>
						td = etree.SubElement(tr, 'td')
						td.text = "_"
						rstyle = "background-color:{}; color:{};".format(colour, colour)
						td.set("style", rstyle)

					# for val in vals:
					for col in cols:
						if col not in ["Colour"]:
							show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
							if show:
								td = etree.SubElement(tr, 'td')
								val = str(row[col]).strip()
								val = base.illegal_xml_chars_re.sub('', val)
								base.debugmsg(8, "val:", val)
								td.text = val

	def xhtml_sections_errors(self, elmt, id):
		base.debugmsg(8, "id:", id)
		body = etree.SubElement(elmt, 'div')
		body.set("class", "body")
		tbl = etree.SubElement(body, 'table')

		showimages = base.rt_errors_get_images(id)
		base.debugmsg(5, "showimages:", showimages)
		grouprn = base.rt_errors_get_group_rn(id)
		base.debugmsg(5, "grouprn:", grouprn)
		groupet = base.rt_errors_get_group_et(id)
		base.debugmsg(5, "groupet:", groupet)

		lbl_Result = base.rt_errors_get_label(id, "lbl_Result")
		lbl_Test = base.rt_errors_get_label(id, "lbl_Test")
		lbl_Script = base.rt_errors_get_label(id, "lbl_Script")
		lbl_Error = base.rt_errors_get_label(id, "lbl_Error")
		lbl_Count = base.rt_errors_get_label(id, "lbl_Count")
		lbl_Screenshot = base.rt_errors_get_label(id, "lbl_Screenshot")
		lbl_NoScreenshot = base.rt_errors_get_label(id, "lbl_NoScreenshot")

		pctalike = 0.80
		base.debugmsg(5, "pctalike:", pctalike)

		base.rt_errors_get_data(id)

		grpdata = {}
		if grouprn or groupet:
			grpdata = {}
			grpdata["resultnames"] = {}
			grpdata["errortexts"] = {}

			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = base.reportdata[id][key]

					if grouprn:
						result_name = rdata['result_name']
						matches = difflib.get_close_matches(result_name, list(grpdata["resultnames"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							result_name = matches[0]
							basekey = grpdata["resultnames"][result_name]["keys"][0]
							base.debugmsg(5, "basekey:", basekey)
							grpdata["resultnames"][result_name]["keys"].append(key)
						else:
							grpdata["resultnames"][result_name] = {}
							grpdata["resultnames"][result_name]["keys"] = []
							grpdata["resultnames"][result_name]["keys"].append(key)
							grpdata["resultnames"][result_name]["errortexts"] = {}

						if groupet and 'error' in rdata:
							errortext = rdata['error']
							# errortext_sub = errortext.split(r'\n')[0]
							errortext_sub = errortext.splitlines()[0]
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							matcheset = difflib.get_close_matches(errortext_sub, list(grpdata["resultnames"][result_name]["errortexts"].keys()), cutoff=pctalike)
							base.debugmsg(5, "matcheset:", matcheset)
							if len(matcheset) > 0:
								errortext = matcheset[0]
								errortext_sub = errortext.splitlines()[0]
								baseid = grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"][0]
								base.debugmsg(5, "baseid:", baseid)
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)
							else:
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub] = {}
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"] = []
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)

					if groupet and 'error' in rdata:
						errortext = rdata['error']
						errortext_sub = errortext.splitlines()[0]
						base.debugmsg(5, "errortext_sub:", errortext_sub)
						matches = difflib.get_close_matches(errortext_sub, list(grpdata["errortexts"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							errortext = matches[0]
							base.debugmsg(5, "errortext:", errortext)
							baseid = grpdata["errortexts"][errortext]["keys"][0]
							base.debugmsg(5, "baseid:", baseid)
							grpdata["errortexts"][errortext]["keys"].append(key)
						else:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							grpdata["errortexts"][errortext_sub] = {}
							grpdata["errortexts"][errortext_sub]["keys"] = []
							grpdata["errortexts"][errortext_sub]["keys"].append(key)

			resultnames = grpdata["resultnames"]
			base.debugmsg(5, "resultnames:", resultnames)
			errortexts = grpdata["errortexts"]
			base.debugmsg(5, "errortexts:", errortexts)

		if grouprn:
			for result_name in list(grpdata["resultnames"].keys()):
				basekey = grpdata["resultnames"][result_name]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]
				tr = etree.SubElement(tbl, 'tr')

				th = etree.SubElement(tr, 'th')
				th.text = "{}:".format(lbl_Result)
				td = etree.SubElement(tr, 'td')
				td.text = result_name

				th = etree.SubElement(tr, 'th')
				th.text = "{}:".format(lbl_Test)
				td = etree.SubElement(tr, 'td')
				td.text = rdata['test_name']

				th = etree.SubElement(tr, 'th')
				th.text = "{}:".format(lbl_Script)
				td = etree.SubElement(tr, 'td')
				td.text = rdata['script']

				th = etree.SubElement(tr, 'th')
				th.text = "{}:".format(lbl_Count)
				count = len(grpdata["resultnames"][result_name]["keys"])
				base.debugmsg(5, "count:", count)
				td = etree.SubElement(tr, 'td')
				td.text = str(count)

				if groupet:
					for errortext in list(grpdata["resultnames"][result_name]["errortexts"].keys()):
						basekey = grpdata["resultnames"][result_name]["errortexts"][errortext]["keys"][0]
						base.debugmsg(5, "basekey:", basekey)
						rdata = base.reportdata[id][basekey]

						tr = etree.SubElement(tbl, 'tr')

						th = etree.SubElement(tr, 'th')
						th.text = "{}:".format(lbl_Error)
						td = etree.SubElement(tr, 'td')
						pre = etree.SubElement(td, 'pre')
						if 'error' in rdata:
							pre.text = rdata['error']
							td.set('colspan', '5')

							th = etree.SubElement(tr, 'th')
							th.text = "{}:".format(lbl_Count)
							td = etree.SubElement(tr, 'td')
							count = len(grpdata["resultnames"][result_name]["errortexts"][errortext]["keys"])
							base.debugmsg(5, "count:", count)
							td.text = str(count)

							if showimages:
								tr = etree.SubElement(tbl, 'tr')

								th = etree.SubElement(tr, 'th')
								th.text = "{}:".format(lbl_Screenshot)

								td = etree.SubElement(tr, 'td')
								td.set('colspan', '7')
								if 'image_file' in rdata:
									# td.text = rdata['image_file']
									oimg = Image.open(rdata['image_file'])
									self.xhtml_sections_embedimg(td, basekey, oimg)
								else:
									td.text = lbl_NoScreenshot

				else:
					for keyi in grpdata["resultnames"][result_name]["keys"]:
						rdata = base.reportdata[id][keyi]

						tr = etree.SubElement(tbl, 'tr')

						th = etree.SubElement(tr, 'th')
						th.text = "{}:".format(lbl_Error)

						td = etree.SubElement(tr, 'td')
						pre = etree.SubElement(td, 'pre')
						if 'error' in rdata:
							pre.text = rdata['error']
							td.set('colspan', '7')

							if showimages:
								tr = etree.SubElement(tbl, 'tr')

								th = etree.SubElement(tr, 'th')
								th.text = "{}:".format(lbl_Screenshot)

								td = etree.SubElement(tr, 'td')
								td.set('colspan', '7')
								if 'image_file' in rdata:
									# td.text = rdata['image_file']
									oimg = Image.open(rdata['image_file'])
									self.xhtml_sections_embedimg(td, keyi, oimg)
								else:
									td.text = lbl_NoScreenshot

		if groupet and not grouprn:
			for errortext in list(grpdata["errortexts"].keys()):
				basekey = grpdata["errortexts"][errortext]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]

				tr = etree.SubElement(tbl, 'tr')

				th = etree.SubElement(tr, 'th')
				th.text = "{}:".format(lbl_Error)

				td = etree.SubElement(tr, 'td')
				pre = etree.SubElement(td, 'pre')
				if 'error' in rdata:
					pre.text = rdata['error']
					td.set('colspan', '5')

					th = etree.SubElement(tr, 'th')
					th.text = "{}:".format(lbl_Count)
					count = len(grpdata["errortexts"][errortext]["keys"])
					base.debugmsg(5, "count:", count)
					td = etree.SubElement(tr, 'td')
					td.text = str(count)

					if showimages:
						tr = etree.SubElement(tbl, 'tr')

						th = etree.SubElement(tr, 'th')
						th.text = "{}:".format(lbl_Screenshot)

						td = etree.SubElement(tr, 'td')
						td.set('colspan', '7')
						if 'image_file' in rdata:
							# td.text = rdata['image_file']
							oimg = Image.open(rdata['image_file'])
							self.xhtml_sections_embedimg(td, basekey, oimg)
						else:
							td.text = lbl_NoScreenshot

		if not grouprn and not groupet:
			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = base.reportdata[id][key]

					tr = etree.SubElement(tbl, 'tr')

					th = etree.SubElement(tr, 'th')
					th.text = "{}:".format(lbl_Result)
					td = etree.SubElement(tr, 'td')
					td.text = rdata['result_name']

					th = etree.SubElement(tr, 'th')
					th.text = "{}:".format(lbl_Test)
					td = etree.SubElement(tr, 'td')
					td.text = rdata['test_name']

					th = etree.SubElement(tr, 'th')
					th.text = "{}:".format(lbl_Script)
					td = etree.SubElement(tr, 'td')
					td.text = rdata['script']

					tr = etree.SubElement(tbl, 'tr')

					th = etree.SubElement(tr, 'th')
					th.text = "{}:".format(lbl_Error)
					td = etree.SubElement(tr, 'td')
					pre = etree.SubElement(td, 'pre')
					if 'error' in rdata:
						pre.text = rdata['error']
						td.set('colspan', '5')

						if showimages:
							tr = etree.SubElement(tbl, 'tr')

							th = etree.SubElement(tr, 'th')
							th.text = "{}:".format(lbl_Screenshot)

							td = etree.SubElement(tr, 'td')
							td.set('colspan', '5')
							if 'image_file' in rdata:
								# td.text = rdata['image_file']
								oimg = Image.open(rdata['image_file'])
								self.xhtml_sections_embedimg(td, key, oimg)
							else:
								td.text = lbl_NoScreenshot

	#
	# 	MS Word
	#
	# https://python-docx.readthedocs.io/en/latest/
	# https://github.com/python-openxml/python-docx

	def docx_configure_style(self):
		# set up document styles for this report
		highlightcolour = base.rs_setting_get_hcolour().replace("#", "")
		fontname = base.rs_setting_get_font()
		fontsize = base.rs_setting_get_fontsize()

		# rgb_basecolour = RGBColor.from_string('000000')
		rgb_highlightcolour = RGBColor.from_string(highlightcolour)
		base.debugmsg(5, "rgb_highlightcolour:", rgb_highlightcolour)

		base.debugmsg(5, "fontname:", fontname, "	fontsize:", fontsize, "	highlightcolour:", highlightcolour)

		# styles = self.cg_data["docx"]["document"].styles
		# for style in styles:
		# 	print(style.name)

		# Update Normal
		style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.name = fontname
		style.font.size = Pt(fontsize)
		base.debugmsg(5, "style.paragraph_format.left_indent:", style.paragraph_format.left_indent)
		style.paragraph_format.left_indent = Cm(0.5)
		base.debugmsg(5, "style.paragraph_format.left_indent:", style.paragraph_format.left_indent)

		# Update Cover Title
		self.cg_data["docx"]["document"].styles.add_style('Cover Title', WD_STYLE_TYPE.PARAGRAPH)
		style = self.cg_data["docx"]["document"].styles['Cover Title']
		style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.size = Pt(int(fontsize * 2))
		style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
		style.paragraph_format.left_indent = Cm(0)

		# Update Subtitle
		self.cg_data["docx"]["document"].styles.add_style('Cover Subtitle', WD_STYLE_TYPE.PARAGRAPH)
		style = self.cg_data["docx"]["document"].styles['Cover Subtitle']
		style.base_style = self.cg_data["docx"]["document"].styles['Cover Title']
		style.font.size = Pt(int(fontsize * 1.5))

		sizeup = int(fontsize * 0.1)
		if sizeup < 1:
			sizeup = int(1)
		base.debugmsg(8, "sizeup:", sizeup)

		# Update Heading 1
		style = self.cg_data["docx"]["document"].styles['Heading 1']
		# style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.name = fontname
		style.font.size = Pt(fontsize + (6 * sizeup))
		style.font.italic = False
		style.font.color.rgb = rgb_highlightcolour
		# style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
		style.paragraph_format.page_break_before = True
		style.paragraph_format.keep_with_next = True
		style.paragraph_format.left_indent = Cm(0)

		# Update Heading 2
		style = self.cg_data["docx"]["document"].styles['Heading 2']
		# style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.name = fontname
		style.font.size = Pt(fontsize + (5 * sizeup))
		style.font.italic = False
		style.font.color.rgb = rgb_highlightcolour
		style.paragraph_format.page_break_before = False
		style.paragraph_format.keep_with_next = True
		style.paragraph_format.left_indent = Cm(0)

		# Update Heading 3
		style = self.cg_data["docx"]["document"].styles['Heading 3']
		# style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.name = fontname
		style.font.size = Pt(fontsize + (4 * sizeup))
		style.font.italic = False
		style.font.color.rgb = rgb_highlightcolour
		style.paragraph_format.page_break_before = False
		style.paragraph_format.keep_with_next = True
		style.paragraph_format.left_indent = Cm(0)

		# Update Heading 4
		style = self.cg_data["docx"]["document"].styles['Heading 4']
		# style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.name = fontname
		style.font.size = Pt(fontsize + (3 * sizeup))
		style.font.italic = False
		style.font.color.rgb = rgb_highlightcolour
		style.paragraph_format.page_break_before = False
		style.paragraph_format.keep_with_next = True
		style.paragraph_format.left_indent = Cm(0)

		# Update Heading 5
		style = self.cg_data["docx"]["document"].styles['Heading 5']
		# style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.name = fontname
		style.font.size = Pt(fontsize + (2 * sizeup))
		style.font.italic = False
		style.font.color.rgb = rgb_highlightcolour
		style.paragraph_format.page_break_before = False
		style.paragraph_format.keep_with_next = True
		style.paragraph_format.left_indent = Cm(0)

		# Update Heading 6
		style = self.cg_data["docx"]["document"].styles['Heading 6']
		# style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.name = fontname
		style.font.size = Pt(fontsize + (1 * sizeup))
		style.font.italic = False
		style.font.color.rgb = rgb_highlightcolour
		style.paragraph_format.page_break_before = False
		style.paragraph_format.keep_with_next = True
		style.paragraph_format.left_indent = Cm(0)

		# Update Table Heading?

		# Table Cell
		self.cg_data["docx"]["document"].styles.add_style('Table Cell', WD_STYLE_TYPE.PARAGRAPH)
		style = self.cg_data["docx"]["document"].styles['Table Cell']
		style.base_style = self.cg_data["docx"]["document"].styles['Normal']
		style.font.size = Pt(int(fontsize * 0.8))
		style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
		# style.paragraph_format.left_indent = Cm(0)
		style.paragraph_format.left_indent = Cm(-0.15)
		# style.paragraph_format.right_indent = Cm(0)
		style.paragraph_format.right_indent = Cm(-0.15)
		style.paragraph_format.space_after = Cm(0.1)

		# Table Header
		self.cg_data["docx"]["document"].styles.add_style('Table Header', WD_STYLE_TYPE.PARAGRAPH)
		style = self.cg_data["docx"]["document"].styles['Table Header']
		style.base_style = self.cg_data["docx"]["document"].styles['Table Cell']
		style.font.bold = True
		style.font.color.rgb = rgb_highlightcolour

	def docx_add_sections(self, id, sectionpct):
		base.debugmsg(5, "id:", id, "	sectionpct:", sectionpct)

		sections = base.report_get_order(id)
		base.debugmsg(5, "sections:", sections)

		document = self.cg_data["docx"]["document"]

		if id == "TOP":

			#
			# Title
			#
			titletxt = base.rs_setting_get_title()
			# document.add_heading(titletxt, 0)
			document.add_paragraph("", style='Cover Title')
			document.add_paragraph(titletxt, style='Cover Title')
			document.add_paragraph("", style='Cover Title')

			#
			# Logo
			#
			base.debugmsg(5, "showtlogo:", base.rs_setting_get_int("showtlogo"))
			if base.rs_setting_get_int("showtlogo"):

				tlogo = base.rs_setting_get_file("tlogo")
				base.debugmsg(5, "tlogo:", tlogo)
				if len(tlogo) > 0:
					document.add_paragraph("", style='Cover Subtitle')
					# document.add_picture(tlogo)
					p = document.add_paragraph("", style='Cover Subtitle')
					r = p.add_run()
					r.add_picture(tlogo)
					document.add_paragraph("", style='Cover Subtitle')
			#
			# Execution Date range
			#
			execdr = ""
			if base.rs_setting_get_int("showstarttime"):
				iST = base.rs_setting_get_starttime()
				fSD = "{}".format(base.report_formatdate(iST))
				fST = "{}".format(base.report_formattime(iST))

				execdr = "{} {}".format(fSD, fST)

			if base.rs_setting_get_int("showendtime"):
				iET = base.rs_setting_get_endtime()
				fED = "{}".format(base.report_formatdate(iET))
				fET = "{}".format(base.report_formattime(iET))

				if not base.rs_setting_get_int("showstarttime"):
					execdr = "{} {}".format(fED, fET)
				else:
					if fSD == fED:
						execdr = "{} - {}".format(execdr, fET)
					else:
						execdr = "{} - {} {}".format(execdr, fED, fET)

			document.add_paragraph("", style='Cover Subtitle')
			document.add_paragraph(execdr, style='Cover Subtitle')
			document.add_paragraph("", style='Cover Subtitle')
		else:
			newsectionpct = 1 / (len(sections) + 1)
			sectionpct = newsectionpct * sectionpct
			base.debugmsg(5, "sectionpct:", sectionpct)
			self.docx_sections_addheading(id)

			stype = base.report_item_get_type(id)
			base.debugmsg(5, "stype:", stype)
			if stype == "contents":
				self.docx_sections_contents(id)
			if stype == "note":
				self.docx_sections_note(id)
			if stype == "graph":
				self.docx_sections_graph(id)
			if stype == "table":
				self.docx_sections_table(id)
			if stype == "errors":
				self.docx_sections_errors(id)

		self.cg_data["docx"]["progress"] += sectionpct
		self.display_message("Generating Word Report {}%".format(int(round(self.cg_data["docx"]["progress"] * 100, 0))))

		if len(sections) > 0:
			for sect in sections:
				self.docx_add_sections(sect, sectionpct)

	def docx_sections_addheading(self, id):
		base.debugmsg(5, "id:", id)
		document = self.cg_data["docx"]["document"]

		level = base.report_sect_level(id)
		base.debugmsg(5, "level:", level)
		number = base.report_sect_number(id)
		base.debugmsg(5, "number:", number)
		name = base.report_item_get_name(id)
		base.debugmsg(5, "name:", name)

		heading_text = "{} {}".format(number, name)

		base.debugmsg(5, "heading_text:", heading_text, "	level:", level)
		hdpg = document.add_heading(heading_text, level)
		stylename = "Heading {}".format(level)
		base.debugmsg(5, "stylename:", stylename)
		hdpg.style = stylename
		# document.add_paragraph("", style='Normal')

	def docx_sections_contents(self, id):
		base.debugmsg(5, "id:", id)

		mode = base.rt_contents_get_mode(id)
		level = base.rt_contents_get_level(id)

		base.debugmsg(5, "mode:", mode, "	level:", level)
		# fmode = None
		# if mode == "Table Of Contents":
		# 	fmode = None
		# if mode == "Table of Graphs":
		# 	fmode = "graph"
		# if mode == "Table Of Tables":
		# 	fmode = "table"

		document = self.cg_data["docx"]["document"]
		# document.add_paragraph("", style='Normal')

		paragraph = document.add_paragraph(style='Normal')
		run = paragraph.add_run()
		fldChar = OxmlElement('w:fldChar')  # creates a new element
		fldChar.set(qn('w:fldCharType'), 'begin')  # sets attribute on element
		instrText = OxmlElement('w:instrText')
		instrText.set(qn('xml:space'), 'preserve')  # sets attribute on element
		if mode == "Table Of Contents":
			instrText.text = 'TOC \\o "1-' + str(level) + '" \\h \\z \\u'   # change 1-3 depending on heading levels you need

		# \c "SEQIdentifier"
		# Lists figures, tables, charts, or other items that are numbered by a SEQ (Sequence) field. Word uses SEQ fields to number items captioned with the Caption command (References > Insert Caption). SEQIdentifier, which corresponds to the caption label, must match the identifier in the SEQ field. For example, { TOC \c "tables" } lists all numbered tables.

		if mode == "Table of Graphs":
			instrText.text = 'TOC \\o "1-' + str(level) + '" \\c "figures"'

		if mode == "Table Of Tables":
			instrText.text = 'TOC \\o "1-' + str(level) + '" \\c "tables"'

		fldChar2 = OxmlElement('w:fldChar')
		fldChar2.set(qn('w:fldCharType'), 'separate')
		fldChar3 = OxmlElement('w:t')
		fldChar3.text = "Right-click to update field."
		fldChar2.append(fldChar3)

		fldChar4 = OxmlElement('w:fldChar')
		fldChar4.set(qn('w:fldCharType'), 'end')

		r_element = run._r
		r_element.append(fldChar)
		r_element.append(instrText)
		r_element.append(fldChar2)
		r_element.append(fldChar4)

	def docx_sections_note(self, id):
		base.debugmsg(5, "id:", id)

		document = self.cg_data["docx"]["document"]

		notebody = base.rt_note_get(id)
		notebody = notebody.replace("\r\n", "\n")
		notebody = notebody.replace("\r", "\n")
		notelist = notebody.split("\n")
		for line in notelist:
			document.add_paragraph(line, style='Normal')

	def docx_sections_graph(self, id):
		base.debugmsg(5, "id:", id)
		pid, idl, idr = base.rt_graph_LR_Ids(id)
		base.debugmsg(5, "pid:", pid, "	idl:", idl, "	idr:", idr)

		document = self.cg_data["docx"]["document"]
		# document.add_paragraph("", style='Normal')

		axisenl = base.rt_graph_get_axisen(idl)
		axisenr = base.rt_graph_get_axisen(idr)

		datatypel = base.rt_graph_get_dt(idl)
		datatyper = base.rt_graph_get_dt(idr)

		tz = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())

		if datatypel == "SQL":
			sqll = base.rt_graph_get_sql(idl)
		else:
			sqll = base.rt_graph_generate_sql(idl)

		if datatyper == "SQL":
			sqlr = base.rt_graph_get_sql(idr)
		else:
			sqlr = base.rt_graph_generate_sql(idr)

		gphdpi = 72
		# gphdpi = 100
		fig = Figure(dpi=gphdpi)
		axisl = fig.add_subplot(1, 1, 1)
		axisl.grid(True, 'major', 'x')
		axisr = axisl.twinx()
		fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')

		canvas = FigureCanvas(fig)

		# https://stackoverflow.com/questions/57316491/how-to-convert-matplotlib-figure-to-pil-image-object-without-saving-image
		axisl.tick_params(labelleft=False, length=0)
		axisr.tick_params(labelright=False, length=0)

		try:
			canvas.draw()
		except Exception as e:
			base.debugmsg(5, "canvas.draw() Exception:", e)
		fig.set_tight_layout(True)

		dodraw = False
		graphdata = {}

		if (sqll is not None and len(sqll.strip()) > 0) or (sqlr is not None and len(sqlr.strip()) > 0):

			if sqll is not None and len(sqll.strip()) > 0 and axisenl > 0:
				base.debugmsg(7, "sqll:", sqll)
				key = "{}_{}".format(idl, base.report_item_get_changed(idl))
				base.dbqueue["Read"].append({"SQL": sqll, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]

				if datatypel == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idl, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in graphdata:
							graphdata[name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							graphdata[name]["Colour"] = colour
							graphdata[name]["Axis"] = "axisL"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							graphdata[name]["objTime"] = []
							graphdata[name]["Values"] = []

						graphdata[name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						graphdata[name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			if sqlr is not None and len(sqlr.strip()) > 0 and axisenr > 0:
				base.debugmsg(7, "sqlr:", sqlr)
				key = "{}_{}".format(idr, base.report_item_get_changed(idr))
				base.dbqueue["Read"].append({"SQL": sqlr, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]

				if datatyper == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idr, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in graphdata:
							graphdata[name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							graphdata[name]["Colour"] = colour
							graphdata[name]["Axis"] = "axisR"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							graphdata[name]["objTime"] = []
							graphdata[name]["Values"] = []

						graphdata[name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						graphdata[name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			base.debugmsg(9, "graphdata:", graphdata)

			for name in graphdata:
				base.debugmsg(7, "name:", name)

				axis = "axisL"
				if "Axis" in graphdata[name]:
					axis = graphdata[name]["Axis"]

				if len(graphdata[name]["Values"]) > 1 and len(graphdata[name]["Values"]) == len(graphdata[name]["objTime"]):
					try:
						if axis == "axisL":
							axisl.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name)
						elif axis == "axisR":
							axisr.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name)
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

				if len(graphdata[name]["Values"]) == 1 and len(graphdata[name]["Values"]) == len(graphdata[name]["objTime"]):
					try:
						if axis == "axisL":
							axisl.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name, marker='o')
						elif axis == "axisR":
							axisr.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name, marker='o')
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

			if dodraw:

				# Left axis Limits
				if axisenl > 0:
					axisl.grid(True, 'major', 'y')
					axisl.tick_params(labelleft=True, length=5)

					SMetric = "Other"
					if datatypel == "Metric":
						SMetric = base.rt_table_get_sm(idl)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						axisl.set_ylim(0, 100)
					else:
						axisl.set_ylim(0)

				# Right axis Limits
				if axisenr > 0:
					axisr.grid(True, 'major', 'y')
					axisr.tick_params(labelright=True, length=5)

					SMetric = "Other"
					if datatyper == "Metric":
						SMetric = base.rt_table_get_sm(idr)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						axisr.set_ylim(0, 100)
					else:
						axisr.set_ylim(0)

				fig.set_tight_layout(True)
				fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
				try:
					canvas.draw()
				except Exception as e:
					base.debugmsg(5, "canvas.draw() Exception:", e)

				# works but messy createing files we then need to delete
				# filename = "{}.png".format(id)
				# fig.savefig(filename)
				# self.xhtml_sections_fileimg(body, id, filename)

				buf = BytesIO()
				fig.savefig(buf)
				buf.seek(0)
				pic = document.add_picture(buf)
				base.debugmsg(5, "pic:", pic)
				# base.debugmsg(5, "pic.parent:", pic.parent)
				document.paragraphs[-1].paragraph_format.left_indent = Cm(-0.5)

	def docx_sections_table(self, id):
		base.debugmsg(5, "id:", id)

		document = self.cg_data["docx"]["document"]
		# document.add_paragraph("", style='Normal')

		datatype = base.rt_table_get_dt(id)
		if datatype == "SQL":
			sql = base.rt_table_get_sql(id)
		else:
			sql = base.rt_table_generate_sql(id)
		colours = base.rt_table_get_colours(id)

		if sql is not None and len(sql.strip()) > 0:
			base.debugmsg(8, "sql:", sql)
			key = "{}_{}".format(id, base.report_item_get_changed(id))
			base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
			while key not in base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = base.dbqueue["ReadResult"][key]
			if datatype == "Plan":
				base.debugmsg(9, "tdata before:", tdata)
				tdata = base.table_postprocess_data_plan(id, tdata)
			base.debugmsg(8, "tdata:", tdata)

			if len(tdata) > 0:
				# table headers
				cols = list(tdata[0].keys())
				base.debugmsg(7, "cols:", cols)

				# numcols = len(cols)
				numcols = 1
				cellcol = 0
				cellrow = 0
				if colours:
					# numcols += 1
					cellcol += 1
				# if "Colour" in cols:
				# 	numcols -= 1

				table = document.add_table(rows=1, cols=numcols)
				# Table Grid Light
				# Table Grid
				# table.style = "Table Grid Light"
				table.style = document.styles['Table Grid']

				if colours:
					table.columns[cellcol - 1].width = Cm(0.5)
					table.rows[cellrow].cells[cellcol - 1].paragraphs[0].style = "Table Header"

				cw = 5
				for col in cols:
					if col not in ["Colour"]:
						show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
						if show:
							if cellcol > 0:
								table.add_column(width=1)
							dispname = base.rt_table_get_colname(id, col)
							table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
							table.rows[cellrow].cells[cellcol].paragraphs[0].text = dispname.strip()
							table.columns[cellcol].width = Cm(cw)
							if cw > 2:
								cw = 1.7
							if cellcol > 5:
								cw = 1.1
							cellcol += 1

				# table rows
				for row in tdata:

					cellcol = 0
					cellrow += 1

					vals = list(row.values())
					base.debugmsg(7, "vals:", vals)
					table.add_row()
					if colours:

						base.debugmsg(9, "row:", row)
						if "Colour" in row:
							label = row["Colour"]
						else:
							label = row[cols[0]]
						base.debugmsg(9, "label:", label)
						colour = base.named_colour(label)
						base.debugmsg(9, "colour:", colour)

						swatch = Image.new(mode="RGB", size=(100, 100), color=colour)

						buffered = BytesIO()
						# swatch.save(buffered, format=swatch.format)
						swatch.save(buffered, format="PNG")
						buffered.seek(0)
						# img_byte = buffered.getvalue()
						#
						# srcdata += base64.b64encode(img_byte).decode()

						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

						# table.rows[cellrow].cells[cellcol].paragraphs[0].paragraph_format.space_before = Pt(0)
						table.rows[cellrow].cells[cellcol].paragraphs[0].paragraph_format.left_indent = Cm(-0.50)

						run = table.rows[cellrow].cells[cellcol].paragraphs[0].add_run()
						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"

						run.add_picture(buffered, width=Cm(0.5))

						cellcol += 1

					# for val in vals:
					for col in cols:
						if col not in ["Colour"]:
							show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
							if show:
								val = str(row[col]).strip()
								val = base.illegal_xml_chars_re.sub('', val)
								base.debugmsg(8, "val:", val)

								# table.rows[cellrow].cells[cellcol].text = str(val)
								# table.rows[cellrow].cells[cellcol].add_paragraph(text=str(val), style="Table Cell")
								table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
								table.rows[cellrow].cells[cellcol].paragraphs[0].text = val

								tcw = int(table.columns[cellcol].width.cm) + 1
								# base.debugmsg(5, "tcw:", tcw)
								if tcw > 5:
									table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

								cellcol += 1

				table.autofit = True
				# table.style.paragraph_format.left_indent = Cm(-0.50)
				# table.style.paragraph_format.right_indent = Cm(-0.50)

	def docx_sections_errors(self, id):
		base.debugmsg(8, "id:", id)

		document = self.cg_data["docx"]["document"]

		imgsizew = 1400000 * 3
		cellcol = 0
		cellrow = -1

		table = document.add_table(rows=1, cols=7)
		table.style = document.styles['Table Grid']
		# table.alignment = WD_TABLE_ALIGNMENT.LEFT
		table.allow_autofit = True

		showimages = base.rt_errors_get_images(id)
		base.debugmsg(5, "showimages:", showimages)
		grouprn = base.rt_errors_get_group_rn(id)
		base.debugmsg(5, "grouprn:", grouprn)
		groupet = base.rt_errors_get_group_et(id)
		base.debugmsg(5, "groupet:", groupet)

		lbl_Result = base.rt_errors_get_label(id, "lbl_Result")
		lbl_Test = base.rt_errors_get_label(id, "lbl_Test")
		lbl_Script = base.rt_errors_get_label(id, "lbl_Script")
		lbl_Error = base.rt_errors_get_label(id, "lbl_Error")
		lbl_Count = base.rt_errors_get_label(id, "lbl_Count")
		lbl_Screenshot = base.rt_errors_get_label(id, "lbl_Screenshot")
		lbl_NoScreenshot = base.rt_errors_get_label(id, "lbl_NoScreenshot")

		pctalike = 0.80
		base.debugmsg(5, "pctalike:", pctalike)

		base.rt_errors_get_data(id)

		grpdata = {}
		if grouprn or groupet:
			grpdata = {}
			grpdata["resultnames"] = {}
			grpdata["errortexts"] = {}

			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = base.reportdata[id][key]

					if grouprn:
						result_name = rdata['result_name']
						matches = difflib.get_close_matches(result_name, list(grpdata["resultnames"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							result_name = matches[0]
							basekey = grpdata["resultnames"][result_name]["keys"][0]
							base.debugmsg(5, "basekey:", basekey)
							grpdata["resultnames"][result_name]["keys"].append(key)
						else:
							grpdata["resultnames"][result_name] = {}
							grpdata["resultnames"][result_name]["keys"] = []
							grpdata["resultnames"][result_name]["keys"].append(key)
							grpdata["resultnames"][result_name]["errortexts"] = {}

						if groupet and 'error' in rdata:
							errortext = rdata['error']
							# errortext_sub = errortext.split(r'\n')[0]
							errortext_sub = errortext.splitlines()[0]
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							matcheset = difflib.get_close_matches(errortext_sub, list(grpdata["resultnames"][result_name]["errortexts"].keys()), cutoff=pctalike)
							base.debugmsg(5, "matcheset:", matcheset)
							if len(matcheset) > 0:
								errortext = matcheset[0]
								errortext_sub = errortext.splitlines()[0]
								baseid = grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"][0]
								base.debugmsg(5, "baseid:", baseid)
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)
							else:
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub] = {}
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"] = []
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)

					if groupet and 'error' in rdata:
						errortext = rdata['error']
						errortext_sub = errortext.splitlines()[0]
						base.debugmsg(5, "errortext_sub:", errortext_sub)
						matches = difflib.get_close_matches(errortext_sub, list(grpdata["errortexts"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							errortext = matches[0]
							base.debugmsg(5, "errortext:", errortext)
							baseid = grpdata["errortexts"][errortext]["keys"][0]
							base.debugmsg(5, "baseid:", baseid)
							grpdata["errortexts"][errortext]["keys"].append(key)
						else:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							grpdata["errortexts"][errortext_sub] = {}
							grpdata["errortexts"][errortext_sub]["keys"] = []
							grpdata["errortexts"][errortext_sub]["keys"].append(key)

			resultnames = grpdata["resultnames"]
			base.debugmsg(5, "resultnames:", resultnames)
			errortexts = grpdata["errortexts"]
			base.debugmsg(5, "errortexts:", errortexts)

		if grouprn:
			# add 2 columns for count
			table.add_column(Cm(1.8))
			table.add_column(Cm(0.8))

			for result_name in list(grpdata["resultnames"].keys()):
				basekey = grpdata["resultnames"][result_name]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]

				cellcol = 0
				cellrow += 1

				if cellrow > 0:
					table.add_row()

				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Result)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				cellcol += 1
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
				a = table.cell(cellrow, cellcol)
				b = table.cell(cellrow, cellcol + 1)
				a.merge(b)
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['result_name']
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
				table.rows[cellrow].cells[cellcol].paragraphs[0].FitText = True

				cellcol += 2
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Test)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				cellcol += 1
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['test_name']
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				cellcol += 1
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Script)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
				# table.columns[cellcol].width = Cm(1.8)

				cellcol += 1
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['script']
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				cellcol += 1
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Count)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
				# table.columns[cellcol].width = Cm(1.8)

				count = len(grpdata["resultnames"][result_name]["keys"])
				base.debugmsg(5, "count:", count)
				cellcol += 1
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = str(count)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				if groupet:
					for errortext in list(grpdata["resultnames"][result_name]["errortexts"].keys()):
						basekey = grpdata["resultnames"][result_name]["errortexts"][errortext]["keys"][0]
						base.debugmsg(5, "basekey:", basekey)
						rdata = base.reportdata[id][basekey]

						cellcol = 0
						cellrow += 1
						table.add_row()

						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
						table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Error)
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

						cellcol += 1
						a = table.cell(cellrow, cellcol)
						b = table.cell(cellrow, cellcol + 5)
						a.merge(b)

						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
						if 'error' in rdata:
							table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['error']
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

						cellcol += 6
						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
						table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Count)
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
						# table.columns[cellcol].width = Cm(1.8)

						count = len(grpdata["resultnames"][result_name]["errortexts"][errortext]["keys"])
						base.debugmsg(5, "count:", count)
						cellcol += 1
						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
						table.rows[cellrow].cells[cellcol].paragraphs[0].text = str(count)
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

						if showimages:
							cellcol = 0
							cellrow += 1
							table.add_row()

							table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
							table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Screenshot)
							table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

							cellcol += 1
							a = table.cell(cellrow, cellcol)
							b = table.cell(cellrow, cellcol + 7)
							a.merge(b)
							table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
							if 'image_file' in rdata:
								run = table.rows[cellrow].cells[cellcol].paragraphs[0].add_run()
								run.add_picture(rdata['image_file'], width=imgsizew)
							else:
								table.rows[cellrow].cells[cellcol].paragraphs[0].text = lbl_NoScreenshot
								table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				else:
					for keyi in grpdata["resultnames"][result_name]["keys"]:
						rdata = base.reportdata[id][keyi]

						cellcol = 0
						cellrow += 1
						table.add_row()

						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
						table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Error)
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

						cellcol += 1
						a = table.cell(cellrow, cellcol)
						b = table.cell(cellrow, cellcol + 7)
						a.merge(b)

						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
						if 'error' in rdata:
							table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['error']
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

						if showimages:
							cellcol = 0
							cellrow += 1
							table.add_row()

							table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
							table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Screenshot)
							table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

							cellcol += 1
							a = table.cell(cellrow, cellcol)
							b = table.cell(cellrow, cellcol + 7)
							a.merge(b)
							table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
							if 'image_file' in rdata:
								run = table.rows[cellrow].cells[cellcol].paragraphs[0].add_run()
								run.add_picture(rdata['image_file'], width=imgsizew)
							else:
								table.rows[cellrow].cells[cellcol].paragraphs[0].text = lbl_NoScreenshot
								table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

		if groupet and not grouprn:
			# add 2 columns for count
			table.add_column(Cm(1.8))
			table.add_column(Cm(0.8))

			for errortext in list(grpdata["errortexts"].keys()):
				basekey = grpdata["errortexts"][errortext]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]

				cellcol = 0
				cellrow += 1

				if cellrow > 0:
					table.add_row()

				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Error)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				cellcol += 1
				a = table.cell(cellrow, cellcol)
				b = table.cell(cellrow, cellcol + 5)
				a.merge(b)

				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
				if 'error' in rdata:
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['error']
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				cellcol += 6
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Count)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				count = len(grpdata["errortexts"][errortext]["keys"])
				base.debugmsg(5, "count:", count)
				cellcol += 1
				table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
				table.rows[cellrow].cells[cellcol].paragraphs[0].text = str(count)
				table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

				if showimages:
					cellcol = 0
					cellrow += 1
					table.add_row()

					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Screenshot)
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

					cellcol += 1
					a = table.cell(cellrow, cellcol)
					b = table.cell(cellrow, cellcol + 7)
					a.merge(b)
					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
					if 'image_file' in rdata:
						run = table.rows[cellrow].cells[cellcol].paragraphs[0].add_run()
						run.add_picture(rdata['image_file'], width=imgsizew)
					else:
						table.rows[cellrow].cells[cellcol].paragraphs[0].text = lbl_NoScreenshot
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

		if not grouprn and not groupet:
			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = base.reportdata[id][key]

					cellcol = 0
					cellrow += 1

					if cellrow > 0:
						table.add_row()

					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Result)
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
					# table.columns[cellcol].width = Cm(1.8)

					cellcol += 1
					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
					a = table.cell(cellrow, cellcol)
					b = table.cell(cellrow, cellcol + 1)
					a.merge(b)
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['result_name']
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
					table.rows[cellrow].cells[cellcol].paragraphs[0].FitText = True

					cellcol += 2
					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Test)
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
					# table.columns[cellcol].width = Cm(1.8)

					cellcol += 1
					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['test_name']
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

					cellcol += 1
					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Script)
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
					# table.columns[cellcol].width = Cm(1.8)

					cellcol += 1
					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['script']
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

					cellcol = 0
					cellrow += 1
					table.add_row()

					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
					table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Error)
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

					cellcol += 1
					a = table.cell(cellrow, cellcol)
					b = table.cell(cellrow, cellcol + 5)
					a.merge(b)

					table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
					if 'error' in rdata:
						table.rows[cellrow].cells[cellcol].paragraphs[0].text = rdata['error']
					table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

					if showimages:
						cellcol = 0
						cellrow += 1
						table.add_row()

						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Header"
						table.rows[cellrow].cells[cellcol].paragraphs[0].text = "{}:".format(lbl_Screenshot)
						table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

						cellcol += 1
						a = table.cell(cellrow, cellcol)
						b = table.cell(cellrow, cellcol + 5)
						a.merge(b)
						table.rows[cellrow].cells[cellcol].paragraphs[0].style = "Table Cell"
						if 'image_file' in rdata:
							run = table.rows[cellrow].cells[cellcol].paragraphs[0].add_run()
							run.add_picture(rdata['image_file'], width=imgsizew)
						else:
							table.rows[cellrow].cells[cellcol].paragraphs[0].text = lbl_NoScreenshot
							table.rows[cellrow].cells[cellcol].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

	#
	# 	MS Excel
	#
	# https://xlsxwriter.readthedocs.io/introduction.html
	# https://openpyxl.readthedocs.io/en/stable/index.html

	def xlsx_configure_style(self):

		basecolour = '000000'
		highlightcolour = base.rs_setting_get_hcolour().replace("#", "")
		fontname = base.rs_setting_get_font()
		fontsize = base.rs_setting_get_fontsize()

		wb = self.cg_data["xlsx"]["Workbook"]

		default = openpyxl.styles.NamedStyle(name="Default")
		default.font.name = fontname
		default.font.size = fontsize
		default.font.color = basecolour
		wb.add_named_style(default)

		# highlight = openpyxl.styles.NamedStyle(name="Highlight")
		highlight = copy(default)
		highlight.name = "Highlight"
		# highlight.font.name = fontname
		# highlight.font.size = fontsize
		highlight.font.color = highlightcolour
		wb.add_named_style(highlight)

		# title = openpyxl.styles.NamedStyle(name="CoverTitle")
		title = copy(default)
		title.name = "CoverTitle"
		# title.font.name = fontname
		title.font.size = fontsize * 2
		# title.font.color = basecolour
		title.alignment.horizontal = 'center'
		title.alignment.wrapText = True
		wb.add_named_style(title)
		base.debugmsg(9, "title:", title.name, title.font.name, title.font.size)

		# subtitle = openpyxl.styles.NamedStyle(name="CoverSubTitle")
		subtitle = copy(title)
		subtitle.name = "CoverSubTitle"
		# subtitle.font.name = fontname
		subtitle.font.size = fontsize * 1.5
		# subtitle.font.color = basecolour
		# subtitle.alignment.horizontal = 'center'
		# subtitle.alignment.wrapText = True
		wb.add_named_style(subtitle)
		base.debugmsg(9, "subtitle:", subtitle.name, subtitle.font.name, subtitle.font.size)
		base.debugmsg(9, "title:", title.name, title.font.name, title.font.size)
		base.debugmsg(9, "highlight:", highlight.name, highlight.font.name, highlight.font.size)
		base.debugmsg(9, "default:", default.name, default.font.name, default.font.size)

		headings = {}
		fm = 2
		for i in range(6):
			base.debugmsg(7, "i:", i, i + 1)
			hnum = i + 1
			headings[hnum] = copy(highlight)
			headings[hnum].name = "Heading " + str(hnum)
			headings[hnum].font.size = int(fontsize * fm)
			wb.add_named_style(headings[hnum])

			fm -= 0.2

		# Table Heading
		side = openpyxl.styles.borders.Side(style="tblside", color='CCCCCC', border_style='thin')  # 'thin' 'hair' 'medium'
		borders = openpyxl.styles.borders.Border(left=side, right=side, top=side, bottom=side)
		tableh = copy(highlight)
		tableh.name = "Table Heading"
		tableh.border = borders
		tableh.alignment.vertical = "top"
		wb.add_named_style(tableh)

		# Table Data
		tabled = copy(default)
		tabled.name = "Table Data"
		tabled.border = borders
		tabled.alignment.vertical = "top"
		wb.add_named_style(tabled)

	def xlsx_add_sections(self, id, sectionpct):
		base.debugmsg(7, "id:", id, "	sectionpct:", sectionpct)

		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active

		base.debugmsg(9, "ws:", ws)
		base.debugmsg(9, "ws.title:", ws.title)

		sections = base.report_get_order(id)
		base.debugmsg(9, "sections:", sections)

		if id == "TOP":

			ws.title = "Cover"

			rownum = 0

			#
			# Title
			#
			titletxt = base.rs_setting_get_title()
			rownum = 3
			colspan = 9

			ws.merge_cells(start_row=rownum, start_column=1, end_row=rownum, end_column=colspan)
			titlecell = ws.cell(column=1, row=rownum, value=titletxt)
			titlecell.style = "CoverTitle"

			fontsize = base.rs_setting_get_fontsize()
			rd = ws.row_dimensions[rownum]
			rd.height = fontsize * 5

			#
			# Logo
			#
			rownum = 5
			base.debugmsg(7, "showtlogo:", base.rs_setting_get_int("showtlogo"))
			if base.rs_setting_get_int("showtlogo"):

				tlogo = base.rs_setting_get_file("tlogo")
				base.debugmsg(7, "tlogo:", tlogo)
				if len(tlogo) > 0:
					img = openpyxl.drawing.image.Image(tlogo)
					cellname = ws.cell(row=rownum, column=1).coordinate
					ws.add_image(img, cellname)

			#
			# Execution Date range
			#
			rownum = 20

			execdr = ""
			if base.rs_setting_get_int("showstarttime"):
				iST = base.rs_setting_get_starttime()
				fSD = "{}".format(base.report_formatdate(iST))
				fST = "{}".format(base.report_formattime(iST))

				execdr = "{} {}".format(fSD, fST)

			if base.rs_setting_get_int("showendtime"):
				iET = base.rs_setting_get_endtime()
				fED = "{}".format(base.report_formatdate(iET))
				fET = "{}".format(base.report_formattime(iET))

				if not base.rs_setting_get_int("showstarttime"):
					execdr = "{} {}".format(fED, fET)
				else:
					if fSD == fED:
						execdr = "{} - {}".format(execdr, fET)
					else:
						execdr = "{} - {} {}".format(execdr, fED, fET)

			ws.merge_cells(start_row=rownum, start_column=1, end_row=rownum, end_column=colspan)
			subtitlecell = ws.cell(column=1, row=rownum, value=execdr)
			subtitlecell.style = "CoverSubTitle"

			rd = ws.row_dimensions[rownum]
			rd.height = fontsize * 2

		else:
			newsectionpct = 1 / (len(sections) + 1)
			sectionpct = newsectionpct * sectionpct
			base.debugmsg(8, "sectionpct:", sectionpct)
			self.xlsx_sections_addheading(id)

			stype = base.report_item_get_type(id)
			base.debugmsg(7, "stype:", stype)
			if stype == "contents":
				self.xlsx_sections_contents(id)
				pass
			if stype == "note":
				self.xlsx_sections_note(id)
				pass
			if stype == "graph":
				self.xlsx_sections_graph(id)
				pass
			if stype == "table":
				self.xlsx_sections_table(id)
				pass
			if stype == "errors":
				self.xlsx_sections_errors(id)
				pass

		self.cg_data["xlsx"]["progress"] += sectionpct
		self.display_message("Generating Excel Report {}%".format(int(round(self.cg_data["xlsx"]["progress"] * 100, 0))))

		if len(sections) > 0:
			for sect in sections:
				self.xlsx_add_sections(sect, sectionpct)

	def xlsx_sections_addheading(self, id):
		base.debugmsg(8, "id:", id)

		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active

		base.debugmsg(9, "ws:", ws)
		base.debugmsg(9, "ws.title:", ws.title)

		base.debugmsg(9, "ws.active_cell:", ws.active_cell, "	ws.selected_cell:", ws.selected_cell)

		# acell = ws.cell(ws.active_cell)
		acell = ws[ws.active_cell]
		rownum = acell.row

		level = base.report_sect_level(id)
		base.debugmsg(8, "level:", level)
		number = base.report_sect_number(id)
		base.debugmsg(9, "number:", number)
		name = base.report_item_get_name(id)
		base.debugmsg(9, "name:", name)

		heading_text = "{} {}".format(number, name)

		if level == 1:
			ws = wb.create_sheet(title=heading_text)
			for wsi in wb.worksheets:
				if wsi.title == heading_text:
					wb.active = wsi

			rownum = 1

		titlecell = ws.cell(column=1, row=rownum, value=heading_text)
		titlecell.style = "Heading " + str(level)

		if level < 5:
			fontsize = base.rs_setting_get_fontsize()
			rd = ws.row_dimensions[rownum]
			rd.height = fontsize * 2

		# base.debugmsg(5, "ws.active_cell:", ws.active_cell, "	ws.selected_cell:", ws.selected_cell)

		rownum += 1
		self.xlsx_select_cell(1, rownum)

		# base.debugmsg(5, "ws.active_cell:", ws.active_cell, "	ws.selected_cell:", ws.selected_cell)

	def xlsx_select_cell(self, col, row):

		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active
		nextcell = ws.cell(column=col, row=row)

		ws.sheet_view.selection[0].activeCell = nextcell.coordinate
		ws.sheet_view.selection[0].sqref = nextcell.coordinate

	def xlsx_sections_contents(self, id):
		base.debugmsg(8, "id:", id)

		mode = base.rt_contents_get_mode(id)
		maxlevel = base.rt_contents_get_level(id)
		fmode = None
		if mode == "Table Of Contents":
			fmode = None
		if mode == "Table of Graphs":
			fmode = "graph"
		if mode == "Table Of Tables":
			fmode = "table"

		self.xlsx_sections_contents_row("TOP", maxlevel, fmode)

	def xlsx_sections_contents_row(self, id, maxlevel, mode):

		display = True

		sections = base.report_get_order(id)
		base.debugmsg(9, "sections:", sections)
		level = base.report_sect_level(id)
		base.debugmsg(8, "level:", level)

		if id == "TOP":
			display = False

		if mode is not None:
			type = base.report_item_get_type(id)
			base.debugmsg(8, "type:", type)
			if mode != type:
				display = False

		if display:
			wb = self.cg_data["xlsx"]["Workbook"]
			ws = wb.active
			rownum = ws[ws.active_cell].row

			number = base.report_sect_number(id)
			base.debugmsg(9, "number:", number)
			name = base.report_item_get_name(id)
			base.debugmsg(9, "name:", name)
			type = base.report_item_get_type(id)
			base.debugmsg(9, "type:", type)

			heading_text = "{} {}".format(number, name)

			if level > 1:
				parentid = base.report_item_parent(id)
				parentlvl = base.report_sect_level(parentid)
				while parentlvl > 1:
					base.debugmsg(9, "parentid:", parentid)
					base.debugmsg(9, "parentlvl:", parentlvl)

					parentid = base.report_item_parent(parentid)
					parentlvl = base.report_sect_level(parentid)

				base.debugmsg(9, "parentid:", parentid)
				base.debugmsg(9, "parentlvl:", parentlvl)

				pnumber = base.report_sect_number(parentid)
				base.debugmsg(9, "pnumber:", pnumber)
				pname = base.report_item_get_name(parentid)
				base.debugmsg(9, "pname:", pname)

				parent_text = "{} {}".format(pnumber, pname)
			else:
				parent_text = heading_text

			rownum += 1
			self.xlsx_select_cell(1, rownum)
			c = ws[ws.active_cell]
			# =HYPERLINK(CONCAT("#'10 agents'!A",MATCH("10.8 selenium versions",'10 agents' A:A,0)),'10.8 selenium versions')
			match = "MATCH(\"" + heading_text + "\",'" + parent_text + "'!A:A,0)"
			base.debugmsg(9, "match:", match)
			concat = "CONCATENATE(\"#'" + parent_text + "'!A\"," + match + ")"
			base.debugmsg(9, "concat:", concat)
			hyper = "=HYPERLINK(" + concat + ",\"" + heading_text + "\")"
			base.debugmsg(8, "hyper:", hyper)
			c.style = "Default"
			c.value = hyper

		if level < maxlevel:
			if len(sections) > 0:
				for sect in sections:
					self.xlsx_sections_contents_row(sect, maxlevel, mode)

	def xlsx_sections_note(self, id):
		base.debugmsg(8, "id:", id)

		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active
		rownum = ws[ws.active_cell].row

		rownum += 1
		self.xlsx_select_cell(1, rownum)

		notebody = base.rt_note_get(id)
		notebody = notebody.replace("\r\n", "\n")
		notebody = notebody.replace("\r", "\n")
		notelist = notebody.split("\n")
		for line in notelist:
			linecell = ws.cell(column=1, row=rownum, value=line)
			linecell.style = "Default"
			rownum += 1
			self.xlsx_select_cell(1, rownum)

	def xlsx_sections_graph(self, id):
		base.debugmsg(5, "id:", id)
		pid, idl, idr = base.rt_graph_LR_Ids(id)
		base.debugmsg(5, "pid:", pid, "	idl:", idl, "	idr:", idr)

		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active
		rownum = ws[ws.active_cell].row

		rownum += 1
		self.xlsx_select_cell(1, rownum)

		axisenl = base.rt_graph_get_axisen(idl)
		axisenr = base.rt_graph_get_axisen(idr)

		datatypel = base.rt_graph_get_dt(idl)
		datatyper = base.rt_graph_get_dt(idr)

		tz = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())

		if datatypel == "SQL":
			sqll = base.rt_graph_get_sql(idl)
		else:
			sqll = base.rt_graph_generate_sql(idl)

		if datatyper == "SQL":
			sqlr = base.rt_graph_get_sql(idr)
		else:
			sqlr = base.rt_graph_generate_sql(idr)

		gphdpi = 72
		# gphdpi = 100
		fig = Figure(dpi=gphdpi)
		axisl = fig.add_subplot(1, 1, 1)
		axisl.grid(True, 'major', 'x')
		axisr = axisl.twinx()
		fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')

		canvas = FigureCanvas(fig)

		# https://stackoverflow.com/questions/57316491/how-to-convert-matplotlib-figure-to-pil-image-object-without-saving-image
		axisl.tick_params(labelleft=False, length=0)
		axisr.tick_params(labelright=False, length=0)

		try:
			canvas.draw()
		except Exception as e:
			base.debugmsg(5, "canvas.draw() Exception:", e)
		fig.set_tight_layout(True)

		dodraw = False
		graphdata = {}

		if (sqll is not None and len(sqll.strip()) > 0) or (sqlr is not None and len(sqlr.strip()) > 0):

			if sqll is not None and len(sqll.strip()) > 0 and axisenl > 0:
				base.debugmsg(7, "sqll:", sqll)
				key = "{}_{}".format(idl, base.report_item_get_changed(idl))
				base.dbqueue["Read"].append({"SQL": sqll, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]

				if datatypel == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idl, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in graphdata:
							graphdata[name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							graphdata[name]["Colour"] = colour
							graphdata[name]["Axis"] = "axisL"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							graphdata[name]["objTime"] = []
							graphdata[name]["Values"] = []

						graphdata[name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						graphdata[name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			if sqlr is not None and len(sqlr.strip()) > 0 and axisenr > 0:
				base.debugmsg(7, "sqlr:", sqlr)
				key = "{}_{}".format(idr, base.report_item_get_changed(idr))
				base.dbqueue["Read"].append({"SQL": sqlr, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)

				gdata = base.dbqueue["ReadResult"][key]

				if datatyper == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idr, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in graphdata:
							graphdata[name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							graphdata[name]["Colour"] = colour
							graphdata[name]["Axis"] = "axisR"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							graphdata[name]["objTime"] = []
							graphdata[name]["Values"] = []

						graphdata[name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						graphdata[name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			base.debugmsg(9, "graphdata:", graphdata)

			for name in graphdata:
				base.debugmsg(7, "name:", name)

				axis = "axisL"
				if "Axis" in graphdata[name]:
					axis = graphdata[name]["Axis"]

				if len(graphdata[name]["Values"]) > 1 and len(graphdata[name]["Values"]) == len(graphdata[name]["objTime"]):
					try:
						if axis == "axisL":
							axisl.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name)
						elif axis == "axisR":
							axisr.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name)
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

				if len(graphdata[name]["Values"]) == 1 and len(graphdata[name]["Values"]) == len(graphdata[name]["objTime"]):
					try:
						if axis == "axisL":
							axisl.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name, marker='o')
						elif axis == "axisR":
							axisr.plot(graphdata[name]["objTime"], graphdata[name]["Values"], graphdata[name]["Colour"], label=name, marker='o')
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

			if dodraw:

				# Left axis Limits
				if axisenl > 0:
					axisl.grid(True, 'major', 'y')
					axisl.tick_params(labelleft=True, length=5)

					SMetric = "Other"
					if datatypel == "Metric":
						SMetric = base.rt_table_get_sm(idl)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						axisl.set_ylim(0, 100)
					else:
						axisl.set_ylim(0)

				# Right axis Limits
				if axisenr > 0:
					axisr.grid(True, 'major', 'y')
					axisr.tick_params(labelright=True, length=5)

					SMetric = "Other"
					if datatyper == "Metric":
						SMetric = base.rt_table_get_sm(idr)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						axisr.set_ylim(0, 100)
					else:
						axisr.set_ylim(0)

				fig.set_tight_layout(True)
				fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
				try:
					canvas.draw()
				except Exception as e:
					base.debugmsg(5, "canvas.draw() Exception:", e)

				buf = BytesIO()
				fig.savefig(buf)
				buf.seek(0)

				# rownum += 1
				img = openpyxl.drawing.image.Image(buf)
				cellname = ws.cell(row=rownum, column=2).coordinate
				ws.add_image(img, cellname)

				rownum += 19
				self.xlsx_select_cell(1, rownum)

	def xlsx_sections_table(self, id):
		base.debugmsg(8, "id:", id)

		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active
		rownum = ws[ws.active_cell].row

		datatype = base.rt_table_get_dt(id)
		if datatype == "SQL":
			sql = base.rt_table_get_sql(id)
		else:
			sql = base.rt_table_generate_sql(id)
		colours = base.rt_table_get_colours(id)

		if sql is not None and len(sql.strip()) > 0:
			base.debugmsg(8, "sql:", sql)
			key = "{}_{}".format(id, base.report_item_get_changed(id))
			base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
			while key not in base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = base.dbqueue["ReadResult"][key]
			if datatype == "Plan":
				base.debugmsg(9, "tdata before:", tdata)
				tdata = base.table_postprocess_data_plan(id, tdata)
			base.debugmsg(8, "tdata:", tdata)

			if len(tdata) > 0:
				# table headers
				cols = list(tdata[0].keys())
				base.debugmsg(7, "cols:", cols)

				rownum += 1
				numcols = len(cols)
				cellcol = 1
				if colours:
					# set first column narrow for colour swatch
					# ws.columns[1].width = 10
					ws.column_dimensions["A"].width = 3

					numcols += 1
					cellcol += 1

				else:
					ws.column_dimensions["A"].width = 3
					numcols += 1
					cellcol += 1

				for col in cols:
					if col not in ["Colour"]:
						show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
						if show:
							dispname = base.rt_table_get_colname(id, col)

							base.debugmsg(8, "col:", col, "	cellcol:", cellcol, "	rownum:", rownum)
							hcell = ws.cell(column=cellcol, row=rownum, value=dispname.strip())
							hcell.style = "Table Heading"

							neww = len(str(col.strip())) * 1.3
							base.debugmsg(9, "neww:", neww)
							ws.column_dimensions[hcell.column_letter].width = neww

							cellcol += 1

				# table rows
				for row in tdata:

					cellcol = 1
					rownum += 1

					vals = list(row.values())
					base.debugmsg(7, "vals:", vals)

					if colours:

						base.debugmsg(9, "row:", row)
						if "Colour" in row:
							label = row["Colour"]
						else:
							label = row[cols[0]]
						base.debugmsg(9, "label:", label)
						colour = base.named_colour(label).replace("#", "")
						base.debugmsg(9, "colour:", colour)
						dcell = ws.cell(column=cellcol, row=rownum)
						dcell.style = "Table Data"
						dcell.fill = openpyxl.styles.PatternFill("solid", fgColor=colour)

						cellcol += 1
					else:
						cellcol += 1

					# for val in vals:
					for col in cols:
						if col not in ["Colour"]:
							show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
							if show:
								val = str(row[col]).strip()
								val = base.illegal_xml_chars_re.sub('', val)
								base.debugmsg(8, "val:", val)

								dcell = ws.cell(column=cellcol, row=rownum, value=val)
								dcell.style = "Table Data"

								currw = ws.column_dimensions[dcell.column_letter].width
								base.debugmsg(9, "currw:", currw, "	len(val):", len(str(val)))
								neww = max(currw, len(str(val)))
								base.debugmsg(8, "neww:", neww)
								ws.column_dimensions[dcell.column_letter].width = neww

								cellcol += 1

		rownum += 2
		self.xlsx_select_cell(1, rownum)

	def xlsx_sections_errors(self, id):
		base.debugmsg(5, "id:", id)

		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active
		rownum = ws[ws.active_cell].row
		base.debugmsg(5, "rownum:", rownum)

		cellcol = 1
		base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
		ws.column_dimensions["A"].width = 3

		cellcol += 1
		base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)

		showimages = base.rt_errors_get_images(id)
		base.debugmsg(5, "showimages:", showimages)
		grouprn = base.rt_errors_get_group_rn(id)
		base.debugmsg(5, "grouprn:", grouprn)
		groupet = base.rt_errors_get_group_et(id)
		base.debugmsg(5, "groupet:", groupet)

		lbl_Result = base.rt_errors_get_label(id, "lbl_Result")
		lbl_Test = base.rt_errors_get_label(id, "lbl_Test")
		lbl_Script = base.rt_errors_get_label(id, "lbl_Script")
		lbl_Error = base.rt_errors_get_label(id, "lbl_Error")
		lbl_Count = base.rt_errors_get_label(id, "lbl_Count")
		lbl_Screenshot = base.rt_errors_get_label(id, "lbl_Screenshot")
		lbl_NoScreenshot = base.rt_errors_get_label(id, "lbl_NoScreenshot")

		pctalike = 0.80
		base.debugmsg(5, "pctalike:", pctalike)

		base.rt_errors_get_data(id)

		grpdata = {}
		if grouprn or groupet:
			grpdata = {}
			grpdata["resultnames"] = {}
			grpdata["errortexts"] = {}

			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = base.reportdata[id][key]

					if grouprn:
						result_name = rdata['result_name']
						matches = difflib.get_close_matches(result_name, list(grpdata["resultnames"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							result_name = matches[0]
							basekey = grpdata["resultnames"][result_name]["keys"][0]
							base.debugmsg(5, "basekey:", basekey)
							grpdata["resultnames"][result_name]["keys"].append(key)
						else:
							grpdata["resultnames"][result_name] = {}
							grpdata["resultnames"][result_name]["keys"] = []
							grpdata["resultnames"][result_name]["keys"].append(key)
							grpdata["resultnames"][result_name]["errortexts"] = {}

						if groupet and 'error' in rdata:
							errortext = rdata['error']
							# errortext_sub = errortext.split(r'\n')[0]
							errortext_sub = errortext.splitlines()[0]
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							matcheset = difflib.get_close_matches(errortext_sub, list(grpdata["resultnames"][result_name]["errortexts"].keys()), cutoff=pctalike)
							base.debugmsg(5, "matcheset:", matcheset)
							if len(matcheset) > 0:
								errortext = matcheset[0]
								errortext_sub = errortext.splitlines()[0]
								baseid = grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"][0]
								base.debugmsg(5, "baseid:", baseid)
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)
							else:
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub] = {}
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"] = []
								grpdata["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)

					if groupet and 'error' in rdata:
						errortext = rdata['error']
						errortext_sub = errortext.splitlines()[0]
						base.debugmsg(5, "errortext_sub:", errortext_sub)
						matches = difflib.get_close_matches(errortext_sub, list(grpdata["errortexts"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							errortext = matches[0]
							base.debugmsg(5, "errortext:", errortext)
							baseid = grpdata["errortexts"][errortext]["keys"][0]
							base.debugmsg(5, "baseid:", baseid)
							grpdata["errortexts"][errortext]["keys"].append(key)
						else:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							grpdata["errortexts"][errortext_sub] = {}
							grpdata["errortexts"][errortext_sub]["keys"] = []
							grpdata["errortexts"][errortext_sub]["keys"].append(key)

			resultnames = grpdata["resultnames"]
			base.debugmsg(5, "resultnames:", resultnames)
			errortexts = grpdata["errortexts"]
			base.debugmsg(5, "errortexts:", errortexts)

		if grouprn:

			for result_name in list(grpdata["resultnames"].keys()):
				basekey = grpdata["resultnames"][result_name]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]

				rownum += 1
				cellcol = 0

				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Result), "Table Heading", 0)
				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['result_name'], "Table Data", 0)

				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Test), "Table Heading", 0)
				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['test_name'], "Table Data", 0)

				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Script), "Table Heading", 0)
				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['script'], "Table Data", 0)

				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Count), "Table Heading", 0)
				count = len(grpdata["resultnames"][result_name]["keys"])
				cellcol += 1
				base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum)
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, str(count), "Table Data", 0)

				if groupet:
					for errortext in list(grpdata["resultnames"][result_name]["errortexts"].keys()):
						basekey = grpdata["resultnames"][result_name]["errortexts"][errortext]["keys"][0]
						base.debugmsg(5, "basekey:", basekey)
						rdata = base.reportdata[id][basekey]

						cellcol = 1
						rownum += 1
						self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Error), "Table Heading", 0)
						cellcol += 1
						if 'error' in rdata:
							self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['error'], "Table Data", 4)

						cellcol += 5
						self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Count), "Table Heading", 0)
						count = len(grpdata["resultnames"][result_name]["errortexts"][errortext]["keys"])
						cellcol += 1
						self.xlsx_sections_errors_fill_cell(cellcol, rownum, str(count), "Table Data", 0)

						if showimages:
							cellcol = 1
							rownum += 1
							self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Screenshot), "Table Heading", 0)

							cellcol += 1

							if 'image_file' in rdata:
								self.xlsx_sections_errors_fill_cell(cellcol, rownum, " ", "Table Data", 4)
								img = openpyxl.drawing.image.Image(rdata['image_file'])
								cellname = ws.cell(row=rownum, column=cellcol).coordinate

								base.debugmsg(5, "img.width:", img.width, "	img.height:", img.height)
								# 								31.75					32.60
								# 								22.23					22.82	==> 70%
								newiw = 850
								ratio = newiw / img.width
								base.debugmsg(5, "ratio:", ratio)
								newih = img.height * ratio
								base.debugmsg(5, "newih:", newih)
								img.width = newiw
								img.height = newih

								newh = newih * 0.76
								# 43.44 cm ==> 32.95 cm	==>	76%
								base.debugmsg(5, "newh:", newh)
								ws.row_dimensions[rownum].height = newh

								ws.add_image(img, cellname)
							else:
								self.xlsx_sections_errors_fill_cell(cellcol, rownum, lbl_NoScreenshot, "Table Data", 4)

				else:
					for keyi in grpdata["resultnames"][result_name]["keys"]:
						rdata = base.reportdata[id][keyi]

						cellcol = 1
						rownum += 1

						self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Error), "Table Heading", 0)
						cellcol += 1
						if 'error' in rdata:
							self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['error'], "Table Data", 4)

						if showimages:
							cellcol = 1
							rownum += 1
							self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Screenshot), "Table Heading", 0)

							cellcol += 1

							if 'image_file' in rdata:
								self.xlsx_sections_errors_fill_cell(cellcol, rownum, " ", "Table Data", 4)
								img = openpyxl.drawing.image.Image(rdata['image_file'])
								cellname = ws.cell(row=rownum, column=cellcol).coordinate

								base.debugmsg(5, "img.width:", img.width, "	img.height:", img.height)
								# 								31.75					32.60
								# 								22.23					22.82	==> 70%
								newiw = 850
								ratio = newiw / img.width
								base.debugmsg(5, "ratio:", ratio)
								newih = img.height * ratio
								base.debugmsg(5, "newih:", newih)
								img.width = newiw
								img.height = newih

								newh = newih * 0.76
								# 43.44 cm ==> 32.95 cm	==>	76%
								base.debugmsg(5, "newh:", newh)
								ws.row_dimensions[rownum].height = newh

								ws.add_image(img, cellname)
							else:
								self.xlsx_sections_errors_fill_cell(cellcol, rownum, lbl_NoScreenshot, "Table Data", 4)

		if groupet and not grouprn:
			for errortext in list(grpdata["errortexts"].keys()):
				basekey = grpdata["errortexts"][errortext]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]

				colspan = 8

				cellcol = 1
				rownum += 1

				self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Error), "Table Heading", 0)
				cellcol += 1
				if 'error' in rdata:
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['error'], "Table Data", colspan)

				cellcol += colspan + 1
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Count), "Table Heading", 0)
				count = len(grpdata["errortexts"][errortext]["keys"])
				cellcol += 1
				self.xlsx_sections_errors_fill_cell(cellcol, rownum, str(count), "Table Data", 0)

				if showimages:
					cellcol = 1
					rownum += 1
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Screenshot), "Table Heading", 0)

					cellcol += 1

					if 'image_file' in rdata:
						self.xlsx_sections_errors_fill_cell(cellcol, rownum, " ", "Table Data", colspan)
						img = openpyxl.drawing.image.Image(rdata['image_file'])
						cellname = ws.cell(row=rownum, column=cellcol).coordinate

						base.debugmsg(5, "img.width:", img.width, "	img.height:", img.height)
						# 									31.75					32.60
						# 									22.23					22.82	==> 70%
						newiw = 850
						ratio = newiw / img.width
						base.debugmsg(5, "ratio:", ratio)
						newih = img.height * ratio
						base.debugmsg(5, "newih:", newih)
						img.width = newiw
						img.height = newih

						newh = newih * 0.76
						# 43.44 cm ==> 32.95 cm	==>	76%
						base.debugmsg(5, "newh:", newh)
						ws.row_dimensions[rownum].height = newh

						ws.add_image(img, cellname)
					else:
						self.xlsx_sections_errors_fill_cell(cellcol, rownum, lbl_NoScreenshot, "Table Data", colspan)

		if not grouprn and not groupet:
			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = base.reportdata[id][key]

					cellcol = 1
					rownum += 1

					self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Result), "Table Heading", 0)
					cellcol += 1
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['result_name'], "Table Data", 0)

					cellcol += 1
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Test), "Table Heading", 0)
					cellcol += 1
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['test_name'], "Table Data", 0)

					cellcol += 1
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Script), "Table Heading", 0)
					cellcol += 1
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['script'], "Table Data", 0)

					cellcol = 1
					rownum += 1
					self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Error), "Table Heading", 0)
					cellcol += 1
					if 'error' in rdata:
						self.xlsx_sections_errors_fill_cell(cellcol, rownum, rdata['error'], "Table Data", 4)

					if showimages:
						cellcol = 1
						rownum += 1
						self.xlsx_sections_errors_fill_cell(cellcol, rownum, "{}:".format(lbl_Screenshot), "Table Heading", 0)

						cellcol += 1

						if 'image_file' in rdata:
							self.xlsx_sections_errors_fill_cell(cellcol, rownum, " ", "Table Data", 4)
							img = openpyxl.drawing.image.Image(rdata['image_file'])
							cellname = ws.cell(row=rownum, column=cellcol).coordinate

							base.debugmsg(5, "img.width:", img.width, "	img.height:", img.height)
							# 								31.75					32.60
							# 								22.23					22.82	==> 70%
							newiw = 850
							ratio = newiw / img.width
							base.debugmsg(5, "ratio:", ratio)
							newih = img.height * ratio
							base.debugmsg(5, "newih:", newih)
							img.width = newiw
							img.height = newih

							newh = newih * 0.76
							# 43.44 cm ==> 32.95 cm	==>	76%
							base.debugmsg(5, "newh:", newh)
							ws.row_dimensions[rownum].height = newh

							ws.add_image(img, cellname)
						else:
							self.xlsx_sections_errors_fill_cell(cellcol, rownum, lbl_NoScreenshot, "Table Data", 4)

		rownum += 1
		rownum += 1
		self.xlsx_select_cell(1, rownum)

	def xlsx_sections_errors_fill_cell(self, cellcol, rownum, val, style, span):
		base.debugmsg(5, "cellcol:", cellcol, "	rownum:", rownum, "	val:", val, "	style:", style, "	span:", span)
		wb = self.cg_data["xlsx"]["Workbook"]
		ws = wb.active

		self.xlsx_select_cell(cellcol, rownum)

		base.debugmsg(5, "setting Cell value")
		val = base.illegal_xml_chars_re.sub('', val)
		base.debugmsg(8, "val:", val)
		cell = ws.cell(column=cellcol, row=rownum, value=val)
		base.debugmsg(5, "splitting val to lines")
		lines = str(val).splitlines()

		base.debugmsg(5, "lines:", lines)

		if span > 0:
			base.debugmsg(5, "span:", span)
			ws.merge_cells(start_row=rownum, start_column=cellcol, end_row=rownum, end_column=cellcol + span)
		else:
			base.debugmsg(5, "span:", span)
			currw = ws.column_dimensions[cell.column_letter].width
			valw = 0
			for line in lines:
				valw = max(valw, len(line))
			base.debugmsg(5, "currw:", currw, "	valw:", valw)
			neww = max(currw, valw)
			base.debugmsg(5, "neww:", neww)
			ws.column_dimensions[cell.column_letter].width = neww

		if len(lines) > 1:
			base.debugmsg(5, "len(lines):", len(lines))
			# currh = ws.row_dimensions[rownum].height
			# https://stackoverflow.com/questions/32855656/column-and-row-dimensions-in-openpyxl-are-always-none
			currh = 13
			base.debugmsg(5, "currh:", currh)
			newh = currh * len(lines)
			base.debugmsg(5, "newh:", newh)
			ws.row_dimensions[rownum].height = newh

		base.debugmsg(5, "style:", style)
		cell.style = style


class ReporterGUI(tk.Frame):

	style_reportbg_colour = "white"
	style_feild_colour = "white"
	style_text_colour = "#000"
	style_head_colour = "#00F"
	imgdata: Any = {}
	b64: Any = {}
	contentdata: Any = {}
	t_preview: Any = {}

	titleprefix = "RFSwarm Reporter"

	icon = None

	c_preview = False

	def __init__(self, master=None):

		self.root = tk.Tk(className="RFSwarm Reporter")
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		tk.Frame.__init__(self, self.root)
		self.grid(sticky="news", ipadx=0, pady=0)
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		self.root.geometry(base.config['GUI']['win_width'] + "x" + base.config['GUI']['win_height'])

		self.root.resizable(True, True)

		base.debugmsg(6, "updateTitle")
		self.updateTitle()

		base.debugmsg(5, "self.root", self.root)
		base.debugmsg(5, "self.root[background]", self.root["background"])
		self.rootBackground = self.root["background"]

		self.set_app_icon()
		self.load_icons()

		base.debugmsg(5, "BuildUI")
		self.BuildUI()
		self.BuildMenu()
		# self.dispaly_donation_reminder()
		dr = threading.Thread(target=self.dispaly_donation_reminder)
		dr.start()

	def load_icons(self):
		# 	"New Report Template"	page_add.png
		self.imgdata["New Report Template"] = self.get_icon("page_add.gif")
		# 	"Open Report Template"	folder_page.png
		self.imgdata["Open Report Template"] = self.get_icon("folder_page.gif")
		# 	"Save Report Template"	page_save.png
		self.imgdata["Save Report Template"] = self.get_icon("page_save.gif")
		# 	"Open Scenario Results"	folder_table.png
		self.imgdata["Open Scenario Results"] = self.get_icon("folder_table.gif")
		# 	"Apply Report Template"	page_go.png
		self.imgdata["Apply Report Template"] = self.get_icon("page_go.gif")

		# Export buttons
		# "Export HTML"		page_white_world.gif			HTML - Issue #36
		self.imgdata["Export HTML"] = self.get_icon("page_white_world.gif")
		# "Export Excel"		page_excel.png				Excel - Issue #37
		self.imgdata["Export Excel"] = self.get_icon("page_excel.gif")
		# "Export Word"		page_word.png					Word - Issue #38
		self.imgdata["Export Word"] = self.get_icon("page_word.gif")
		# "Export PDF"		page_white_acrobat.png
		self.imgdata["Export PDF"] = self.get_icon("page_white_acrobat.gif")
		# "Export Calc"		page_calc.gif
		self.imgdata["Export Calc"] = self.get_icon("page_calc.gif")
		# "Export Writer"		page_writer.gif
		self.imgdata["Export Writer"] = self.get_icon("page_writer.gif")

		# "New Section"	add.gif
		self.imgdata["New Section"] = self.get_icon("add.gif")
		# Remove Section	 delete.gif
		self.imgdata["Remove Section"] = self.get_icon("delete.gif")
		# Move Section Up	 resultset_up.gif
		self.imgdata["Section Up"] = self.get_icon("resultset_up.gif")
		# Move Section Down	 resultset_down.gif
		self.imgdata["Section Down"] = self.get_icon("resultset_down.gif")

		# Content pane buttons
		self.imgdata["Preview"] = self.get_icon("report.gif")
		self.imgdata["Settings"] = self.get_icon("cog.gif")

		# settings buttons
		# "Select Image"	picture.gif
		self.imgdata["Select Image"] = self.get_icon("picture.gif")
		# "Select Colour"	color_swatch.gif
		self.imgdata["Select Colour"] = self.get_icon("color_swatch.gif")

	def get_icon(self, imagefile):
		if len(self.b64) < 1:
			self.load_b64()

		# files["New"] = "famfamfam_silk_icons/icons/page_white.edt.gif"

		if imagefile not in self.b64:
			base.debugmsg(6, "imagefile:", imagefile)
			scrdir = os.path.dirname(__file__)
			base.debugmsg(6, "scrdir:", scrdir)
			imgfile = os.path.join(scrdir, "../famfamfam_silk_icons/icons", imagefile)
			base.debugmsg(6, "imgfile:", imgfile)
			if os.path.isfile(imgfile):
				base.debugmsg(0, "isfile: imgfile:", imgfile)
				with open(imgfile, "rb") as f:
					img_raw = f.read()
				# 		self.b64["page_writer.gif"] =
				base.debugmsg(0, "img_raw:	", "self.b64[\"{}\"] =".format(imagefile), img_raw)
				# b64 = base64.encodestring(img_raw)
				# img_text = 'img_b64 = \\\n"""{}"""'.format(b64)

				self.b64[imagefile] = img_raw  # tk.PhotoImage(file=imgfile)
				# base.debugmsg(0, "self.b64[",imagefile,"]:", self.imgdata[icontext])

			else:
				base.debugmsg(6, "File not found imgfile:", imgfile)

		if imagefile in self.b64:
			return tk.PhotoImage(data=self.b64[imagefile])
		else:
			base.debugmsg(6, "File not found imagefile:", imagefile)

	def load_b64(self):

		# gif's
		self.b64["page_add.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa*d\xbb.ga1h>.i\xbe0i\xba3j\x124l\x1aIm\xb64q\xc18v\xc3?y\xbe;z\xc4AzzJ{,B~\xc3?\x80\xc7D\x83\xc6F\x88\xc7\\\x88HI\x89\xc7M\x8c\xc9Q\x8c"c\x8cKU\x8f(d\x93\xdcs\x99_\x81\xac`\x8e\xae\x86}\xb2\xe3R\xb4\xf8R\xb5\xf7\x84\xb7\xe3\x9c\xb9\xa7\x87\xbb_\x8d\xbcd\x8f\xbci\xa0\xbd\xaec\xbf\xfcg\xc0\xfdm\xc3\xfd\xb3\xd4\x94\xb5\xd4\xf2\xb7\xd5\x9d\x97\xd7\xff\x9c\xd7\xff\xbb\xd7\xf5\x9c\xd8\xff\xa1\xd9\xff\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc7\xe0\xfa\xcb\xe3\xfb\xd1\xe6\xbb\xd4\xe6\xfd\xd8\xe6\xf2\xd8\xe7\xfe\xd7\xe8\xfe\xd9\xe8\xfe\xde\xea\xf6\xe1\xeb\xf6\xe9\xef\xf5\xe6\xf0\xf7\xec\xf2\xf7\xec\xf3\xf9\xf1\xf5\xf9\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00E\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb9\x80E\x10\x16\x84\x85\x84\x15\x0bE\x8a\x8a\x12AB\x8f\x90A9\x1e\x1a\x8bE\x15C6\x9a654/D2\x94\x8b\x98\x9b\x9a\x9eD\x9a!\x0c\x8a\x988\xae\xa63>AC?\x10\xacC\xae\xaf6\x9e++C\x12\xacB:\xb98\xb03B\xc0E\x13B<\xcd\xb9\xa64\xc8\x8cB;<\xc4\xc5\x9cB\x11\xd3\xd7\xae&\x1b\x18\x18\x0e\x8a\x11B\xdd"\x1c*7%\x19\x07E\r@\x1f  \x1f\xf2\x14**D$$\xee\r>)1`\xb8\x80\xd1\xe2\x01\x0b"\x08U\xb8S\xe0\x03\xc5\x89\x87\x0f\x11\x90\x18Ad\x04\xbf"\x05\x84\xf8\xe8\xc1\xb1\x87\x90\x0e\x17H\xa8 q\xc1\x9d\x01\x01(S\xa2\x1c\x80\xe0\x00\x02\x02E\x02\x01\x00;'

		self.b64["folder_page.gif"] = b"GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00@j\xaa9q\xaaAu\xc6C{\xc3Q\x7f\xcbS\x84\xccS\x84\xd0\xd9\x86'\xd9\x87(\xd9\x89)\xdb\x941^\x97\xcd\xdb\x9b2l\x9f\xd1k\xa1\xd2\xdb\xa53\xe1\xa6K\xe3\xabS\xdb\xac2\xdb\xb22\xda\xb5/\x88\xbc\xea\x93\xbc\xe5\xe7\xbdp\xe9\xbdc\x97\xc0\xe6\x93\xc2\xec\xc7\xc2\x86\x9e\xc4\xea\xe3\xc4^\xd0\xc9\x8c\xeb\xca\x91\xd8\xcf\x90\xf2\xd2=\xb3\xd3\xf4\xdd\xd3\x93\xf3\xd5r\xf3\xd6L\xe4\xd8\x93\xf3\xd8z\xbd\xd9\xf7\xd7\xd9\xca\xf4\xda\\\xf4\xdb\x83\xe9\xdc\x93\xf5\xdcf\xf6\xddk\xc4\xde\xfa\xf5\xde\x8c\xf5\xde\x93\xf6\xdft\xf6\xe1\x94\xf7\xe1}\xcc\xe2\xfc\xf6\xe2\xad\xc5\xe3\xfa\xf5\xe3\xa0\xf7\xe3\x84\xf6\xe5\x9c\xf8\xe5\x8c\xf8\xe5\x93\xd4\xe6\xfd\xd8\xe7\xff\xdb\xe9\xff\xde\xe9\xf5\xf8\xea\xc3\xe5\xef\xfa\xe7\xf2\xfc\xe8\xf2\xef\xf9\xf2\xdc\xfb\xf2\xcc\xeb\xf4\xfc\xfb\xf6\xe8\xf1\xf7\xff\xf3\xf9\xfd\xfe\xfa\xef\xfe\xfc\xf4\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00O\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xbe\x80O\x82\x83\x1d\x1a\x17\x17\x0f\x0e\x0c\x04\x83\x8dO\x17NH\x92CD\x16\x07\x8e\x82\x17H060#K8\x1b\x8c\x8e\x17J6\xa7)AHK\x06\x98\xa5>>\x9d)#C\x06\x15\x1e\xb8\xb8\xaf\xb0\xb2D\x06\x14N\xc1\xc1\xbb\xbc0H\xbfM<297\x06J@\xd0?\xb1J\x06\x13M22\x19\x0b\xdb\xdc\xdc\xc7\x13I\x18\x12\x11 H\xc2\xc2\x0bE\x06\x10\xc1M\xee;\xf0\xf09F\x0b\xc7\x10M=\xf9=-'$!\x1f\x1cT,\x18P\xa0\x01\xbe|<t\xd4\x98\xf1b\x85\x89#\x0b\x04-`\xd2\x83G\xc2\x85.\x1c\x8a\x80(H\x81\x91\x1d4h\xc4\x88\xc1\x82\x05\x8a\x12%\x84D|\x82@A\x02\x050c\xc2|\x89@P \x00;"

		self.b64["page_save.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa\x1cZ\xaf)^\xa7+d\xbb6h\xab/i\xbc0i\xba;i\xacAl\xacIm\xb6Ap\xb14q\xc18v\xc3?y\xbe;z\xc4B~\xc3U~\xbcO\x7f\xc4Q\x7f\xc2D\x83\xc6T\x83\xc5\\\x84\xc0Z\x86\xc8F\x88\xc7I\x89\xc7^\x89\xcag\x8b\xd4k\x8b\xcel\x8b\xdbM\x8c\xc9c\x8c\xcbp\x8f\xe2k\x92\xced\x93\xdcm\x98\xd5s\x9a\xd2z\x9e\xd6z\x9e\xdcw\x9f\xda{\xa2\xdc\x82\xa5\xd7\x83\xa5\xde\x81\xa8\xe3\x85\xa9\xde\x8c\xb0\xe5}\xb2\xe3R\xb4\xf8R\xb6\xf7\x92\xb6\xe6\x84\xb7\xe3\x9a\xb7\xed\x9a\xb9\xeac\xbf\xfcg\xc0\xfd\x84\xc0O\x84\xc0R\xa2\xc0\xed\x9f\xc1\xefm\xc3\xfd\xb4\xc8\xe4\x99\xcao\x9a\xcaq\xb1\xce\xf3\xbb\xcf\xef\xb5\xd4\xf2\x9c\xd7\xff\xbb\xd7\xf5\x9c\xd8\xff\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc6\xe0\xf9\xcb\xe3\xfb\xd5\xe6\xfd\xd8\xe6\xf2\xd8\xe7\xfe\xd7\xe8\xfe\xd9\xe8\xfe\xde\xea\xf6\xe1\xeb\xf6\xc8\xee\x87\xc8\xee\x8c\xe9\xef\xf5\xe6\xf0\xf7\xe6\xf1\xee\xe8\xf3\xea\xec\xf3\xf5\xed\xf3\xf8\xe9\xf4\xe5\xd8\xf5\xa3\xf1\xf5\xf9\xf4\xfa\xff\xff\xff\xde\xff\xff\xe1\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00`\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xcd\x80\x10\x1e\x83\x84\x1e\x19\r`\x89\x8a\x14WX\x8e\x8eWK."\x8a\x89\x19[I\x99HGC_E\x93\x95\x97\x99\x99\x9c_\x992\x0e\x8a\x97JJ\xa4FPW[S\x10\xaa[\xac\xadI\x9cAA[\x14\xaaXL\xb7#%$)\x1f!$$\x1f`\x18XNN\xac\x1f?_<_\xd6_9\x1a\x14XM\xb7\x17:_!\xd6\\\\-\x1f\xdb\xb7J\x1a9\xd7\xd7,\x13\x0fT/0//\x1f4(*(\xfb(&\x16\x0fPv\x10\x11B\xe4C\x8c\x15+\xf8\x9d \x11\x81\x01\x14\x1b5"V\x98q\xa5\x8a\xc5*WJ,0\x80\x05\xca\x93\x8f\x12fX\xb9\xd1\xc3\x07\x8e,&\n\x1c \xc0\x92e\x05 ]\xa2h\xd1"\xc5\x8b\n\x04\x95\x12\x19\xa8\xb0\x01D\x87\x9f\x1c\x12\x0c\x08\x04\x00;'

		self.b64["folder_table.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00@w\xbcR\x85\xc5\xda\x86\'\xd9\x87(\xd9\x89)W\x8a\xc9\\\x8a\xc6^\x8f\xccc\x93\xcf\xdb\x941l\x9a\xd4\xdb\x9b2t\xa1\xd8|\xa5\xdc\xdb\xa53\xe2\xa9O\x80\xaa\xde\x98\xaa\xc1\xdb\xac2\x84\xad\xe1\xe0\xae`\xe4\xafZ\xdb\xb22\x8c\xb3\xe4\xda\xb5/\x94\xb8\xe7\xb3\xb9\x92\x9c\xbd\xea\xb6\xbd\x9c|\xbfv\x9f\xc0\xec\xe5\xc2\x91\x82\xc3|\xa6\xc3\xeb\xbe\xc4\xa5\xe3\xc4_\xc1\xc6\xa7\xea\xc6~\x89\xc7\x82\xac\xc7\xe9\xad\xc8\xe8\xb3\xcb\xe8\xc6\xcb\xae\x93\xcc\x8b\xb8\xcc\xe2\xf0\xcc \xf1\xce)\xf1\xd1j\xf2\xd15\xf1\xd3r\xf3\xd4D\xa4\xd5\x9b\xf2\xd5|\xf2\xd6\x81\xf3\xd7R\xf3\xd8\x86\xf4\xd8T\xf3\xd9\x8e\xf5\xdba\xd2\xdc\xdf\xf4\xdc\x9f\xf4\xde\x94\xf4\xde\xa8\xf6\xden\xf6\xdfr\xf5\xe1\xa0\xf7\xe1z\xf7\xe2\x82\xdb\xe5\xf1\xf8\xe5\x8c\xf8\xe6\x94\xf9\xe9\xa4\xf8\xea\xc3\xed\xeb\xe5\xfa\xec\xad\xfa\xed\xb4\xf3\xef\xe7\xfb\xef\xba\xfa\xf0\xdd\xeb\xf1\xf7\xfc\xf2\xca\xef\xf3\xf8\xf7\xf6\xed\xfb\xf6\xe8\xf4\xf7\xfb\xfd\xf8\xe7\xfe\xfa\xec\xfe\xfc\xf5\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00Z\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc6\x80Z\x82\x82"\x85\x1c\x1a\x18\x18\x14\x11\x0e\x0e\x83\x84U\x91\x92\x92\r\x8fZ\x1fU44,\'!!\x1eU\x0b\x96\x1cUY\xa6\xa7Y\xa1\xa3U\x85\xad\x85U\t\x19$\xb3$\x1a\xacY)\xa8P\x08\x17\xa8\x18U(())*\xc5E\x06\x17XF>B\xbf\xb9\xb9\xa7E\x02\x13X>>6\x12 \n\xdb\xdc\n\xd2\x13T&\x16\x10\x15SSMJ\xe9R\xde\x07\x0f\xa6XX<+%#\x1d\x1d\x1b-\n\x02\x01\x0fXQNK\x8c\x18!2\x04\xc8\x8e\x1cV\x14\x08b\x80\x85\t\x92#D\x08\x1a\xbc1\xe3\x8aB-\n\xae<$\x12\xe4\xe0\x8c\x18/\\D\xb9X\xe0\xc9\x8f\x1e>t\xe0\xa8QC\x06\x0c\x18I\n\x08\x1aP\x80@\x81\x9b8o\xda\x1c (\x10\x00;'

		self.b64["page_go.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa$_\xb8)b\xb7\'d\xb4*d\xbb.i\xbe0i\xbaIm\xb6\x1cq\x004q\xc18v\xc3?y\xbe\x1dz\x16\x17{\x02\x1b{\x0b;{\xc4B~\xc3\x1f\x7f\x00?\x80\xc7D\x83\xc61\x87\x08F\x88\xc7I\x89\xc77\x8b\r6\x8c\x10M\x8c\xc9@\x8f\x11F\x91\x15d\x93\xdcC\x94)H\x94.O\x98\x1dU\x99"Z\x9c#b\x9f.]\xa06c\xa0,[\xa18^\xa2@k\xa44d\xa5Dm\xa6<r\xa9Ct\xacM|\xb0S}\xb2\xe3\x81\xb4YS\xb5\xf8S\xb6\xf7\x82\xb6d\x84\xb7\xe3\x85\xb7i\x8c\xbam\x90\xbdte\xbf\xfcg\xc0\xfd\x97\xc2\x80m\xc3\xfd\x99\xc3\x83\x9f\xc6\x88\xa2\xc7\x8a\xa4\xc9\x8c\xac\xcd\x92\xb1\xcf\x97\xb5\xd4\xf2\xbb\xd7\xf5\x9f\xd8\xff\xa1\xd9\xff\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc6\xe0\xf9\xcc\xe3\xfb\xd4\xe6\xfd\xd8\xe6\xf2\xd8\xe7\xfe\xd7\xe8\xfe\xd9\xe8\xfe\xde\xea\xf6\xe1\xeb\xf6\xe9\xef\xf5\xe6\xf0\xf7\xec\xf2\xf7\xec\xf3\xf9\xf1\xf5\xf9\x00\xff\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00X\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc5\x80X\x11\x1a\x84\x85\x84\x17\x0bX\x8a\x8a\x14ST\x8f\x90SK.\x1d\x8bX\x17UI\x9aIHGBWE\x94\x8b\x98\x9b\x9a\x9eW\x9a3\x0c\x8a\x98J\xae\xa6FPSUQ\x11\xacU\xae\xafI\x9eAAU\x14\xacTL\xb9J\xb0FT\xc0X\x16TN\xcd\xb9I+%G\xc8\x8cTMN\xc4J*/!T\x13\xd5\xb9*((#-?,\x1c\x10\x8a\x13T\xb9(@?\xf16>)\x15\x8a\x10R011%?552\x02\xee0!\x01\x0b\x04(:\x88\x0c\x11\xf1\xc3G\x0f\x1e4v\xa4h\xa0H\x01\x14\x1c7n\x80\xe0\xb0\x01\x03\x89\x1c)<\x10Pd\x80\n\x94\'(\x9f<\xcap\xe2\xc3\x15\x01\x8a\x0e\x14\x98Is\xe6\x03\x07\x05\x06\x0c\xc0\x12\x08\x00;'

		self.b64["add.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00,|\x1d+~"&\x80\x1e/\x81)0\x81\'3\x83)8\x87.=\x8a2A\x8e5E\x8f9K\x92?Q\x95CN\x9a>U\x9bE]\x9dLb\xa0Me\xa2Ri\xa5Zh\xa6Vj\xabVl\xab[f\xacRu\xacat\xad_z\xb2d~\xb3h\x83\xb5kn\xb6V\x88\xb8op\xb9W\x87\xbaqt\xbb\\}\xbbk\x8a\xbcr}\xbde\x8b\xbfzp\xc2by\xc2c\x8d\xc3{|\xc4i\x92\xc6\x80~\xc8o\x89\xc9\x7f\x86\xcbz\x99\xcc\x86\x81\xcdu\x8d\xcd\x83\x99\xcd\x8a\x93\xce\x88\xa5\xcf\x94\x8a\xd0}\xa7\xd1\x97\x8e\xd3\x83\x99\xd4\x8b\x96\xd5\x8a\xac\xd5\x9e\x9e\xd9\x92\xa1\xda\x97\xb5\xda\xa6\xb8\xdb\xab\xa6\xdc\x9c\xb5\xdd\xaa\xbb\xde\xb0\xb0\xe0\xa7\xb6\xe0\xad\xbc\xe3\xb5\xcc\xe6\xc4\xc6\xe8\xc1\xcf\xe9\xca\xd5\xeb\xd0\xd8\xee\xd3\xdd\xf1\xd9\xe1\xf2\xdd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00K\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb1\x80K\x82\x83\x84\x85\x86"\x1b\x1b\x19\x17\x17\x86\x82"\x1f2CFE?!\x13\x11\x85\x90?IB=:@D\'\x0f\x0f\x84\x1f<H91/775B!\x0e\x83\x1d-G:7+JJ,(*A\x0e\x0b\x82\x1b>@/,!\xba\x15  6)\n\x82\x1aB6,\xba\xd5J\x1e(8\x08\x82\x19>3.\xd6\xba\x1e#\xda\x82\x1807(%\x16\xe2\x1e -$\x06\x82\x15\x16>&\xcb\xe2\x1c ;\t\xf2\x82\x11!|,\xf3\xc0A\xdf\x8e\n\xfe\x04Ax\xd0\xad\xc5\x88\x11-vP( \xa0\x90\x03\x06\rN\xd0\xa0A\x02\x01EGK\x14$@p\xc0\x00\x01\x90(\t\x05\x02\x00;'

		self.b64["delete.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\xb9F$\xb5G"\xb9I&\xb5J\x1e\xbcK+\xc2K.\xd1M;\xbfN2\xc5N3\xcdP8\xbfR4\xc1R6\xc2S=\xc5TB\xdcTI\xe6UL\xcaVD\xceVJ\xe9WK\xce[L\xe7[T\xea[N\xd8\\O\xd5^T\xec^R\xd1aS\xdac]\xddcb\xf0cT\xd6d\\\xe1d[\xead[\xeeeP\xe3gg\xddie\xeei]\xe1jj\xe3kb\xe3pe\xf3s\\\xf2wb\xf3yb\xe4zs\xe9{s\xe9\x7fx\xf6\x82g\xf0\x83{\xed\x84}\xf6\x84k\xf0\x85p\xf8\x86p\xee\x8au\xee\x8c\x81\xf0\x8cw\xf8\x8cv\xf1\x8ez\xf4\x8e\x81\xee\x92\x8f\xf5\x92~\xf9\x93\x7f\xfa\x9b\x87\xf1\x9e\x97\xfa\x9e\x8b\xf4\xa2\x9f\xfa\xa4\x91\xf5\xa6\xa1\xf5\xab\xa3\xfb\xab\x9e\xf2\xae\xab\xf5\xb0\xa6\xf8\xb0\xa5\xf4\xb5\xab\xf8\xb7\xa9\xf9\xba\xb0\xfa\xbb\xaf\xf8\xc4\xbf\xfc\xc8\xbb\xf9\xcc\xc5\xfb\xd5\xce\xfd\xdc\xd5\xfd\xdd\xd9\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00S\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xaf\x80S\x82\x83\x84\x85\x86%#\x1c\x1b\x1b\x1e\x86\x82%%:LONH\'\x18\x14\x85\x90EQKA?DM,\x14\x11\x84%CP=;8<<7I&\xa5\x82"0O?;41\xba1*G\x07\r\x82&FD6\x19\xc6\xc7)9-\x0c\x82#J<2R\xd2\xd3\x13$>\x08\x82\x1bC3.\xd3\xd4 >\x05\xd95;(\x13\xe7\xe8\x16/+\xe2S\x18\x0fC\x1d!\xe8\x13\x10\x15B\t\x03\x83\x1a&C\x19\x16\xf5 @\x00\x82!\x00!\t\x11>\x08\x81\x01\xa2\x02\x0c \x17\x06\x08(\x14\xc1\x81\x02\x16:t\xac0 \xd1\xd1\x94\x04\x0b\x10\x14(\xa0\xcf\xa3\xc9A\x81\x00\x00;'

		self.b64["resultset_up.gif"] = b'GIF89a\x10\x00\x10\x00\xa5\x00\x00\x00\x00\x00\x14A\xb7\x15E\xb9\x16J\xbd\x16N\xc0\x17P\xbd\x18S\xc0\x19Y\xc5\x1ab\xc6\x1ab\xc9#n\xcd,r\xcd<s\xce5w\xd2=w\xd0?z\xd0C\x7f\xd3E\x84\xd6K\x88\xd6S\x8e\xdba\x96\xddb\x97\xe1n\xa0\xe2t\xa2\xdfu\xa3\xe1y\xa7\xe3}\xa9\xe1}\xa9\xe8\x80\xab\xe9\x82\xac\xe3\x87\xb0\xe8\x8a\xb1\xe4\x90\xb5\xe7\x92\xb7\xe8\x99\xbb\xea\xa2\xc2\xed\xa8\xc7\xee\xad\xc8\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\n\x00?\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06G\xc0\x9fpH,\x1a\x8f\xc8\xa4r\xc9L"\x0e\xcd\x85\x04bXF(\x9f\xce\xa3\x90\xa4`D\x1d\x8c\xc618b<\xa3P\xf8\x92a\x08\x8a\x9bM\x894\x12\x81:\x9a\x0b#@\xe4p2\x16\x15\x13\x11\r\n\t\x07\x04M\x8a\x8b\x8cHA\x00;'

		self.b64["resultset_down.gif"] = b'GIF89a\x10\x00\x10\x00\xa5\x00\x00\x00\x00\x00\x14A\xb7\x15E\xb9\x16J\xbd\x16N\xc0\x17P\xbd\x18S\xc0\x19Y\xc5\x1ab\xc6\x1ab\xc9#n\xcd,r\xcd<s\xce5w\xd2=w\xd0?z\xd0C\x7f\xd3E\x84\xd6K\x88\xd6S\x8e\xdba\x96\xddb\x97\xe1n\xa0\xe2t\xa2\xdfu\xa3\xe1y\xa7\xe3}\xa9\xe1}\xa9\xe8\x80\xab\xe9\x82\xac\xe3\x87\xb0\xe8\x8a\xb1\xe4\x90\xb5\xe7\x92\xb7\xe8\x99\xbb\xea\xa2\xc2\xed\xa8\xc7\xee\xad\xc8\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00?\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06G\xc0\x9fpH,\x1a\x8f\xc8\xa4rI8$\x14\x8d\xc8\xa4b\xc9p8\xc4\x00\xe3\xa2\xe9\x80D#Ri\xb3)\n\x18\x99\x0b\xa6\x13\x1ay0\xc7\x81C\xb3\x16a(\xc9\xc2\xa3\xf3\xa1D\x96\x06\x10\x12\x0bKB\x07\x08\x85\x89\x8a\x8b\x8c\x8dA\x00;'

		self.b64["report.gif"] = b'GIF89a\x10\x00\x10\x00\xc6\\\x00~1\x18\xabB!\xacC!\xaeF"\xaeI"\xa5K,\xafK#\xb1N#\xb2Q$\xb2R%\xb4U%\xb5V&\xb7Y&\xb7[&\xaf]5\xb8^\'\xb8_\'\xbaa(\xbexI\xb3yc\xb3|d\xb5\x7fe\xb5\x82f\xb7\x83gj\x93\xd4\xb9\x87gj\x98\xd9\xc2\x8bdk\x99\xdan\x9a\xdc\xbf\x8fao\x9b\xdcr\x9c\xdcq\x9d\xdd\xc1\x92cq\x9e\xdfs\x9e\xdf\xc2\x94ds\x9f\xe0t\xa0\xe0v\xa0\xe0\xc3\x96ev\xa2\xe0w\xa3\xe1x\xa3\xe1\xc4\x99f\xc5\x9agz\xa5\xe1\xa0\xbe\xea\xa1\xbf\xea\xa2\xc0\xea\xa3\xc0\xea\xca\xc6\xc4\xcc\xc6\xc0\xc7\xc7\xc7\xcd\xc6\xc0\xca\xc7\xc4\xcd\xc7\xc0\xcd\xc7\xc1\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd8\xd8\xd8\xdc\xdc\xdc\xe6\xe6\xe6\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xec\xec\xec\xed\xed\xed\xee\xee\xee\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\x7f\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xbf\x80\x7f\x7f\x1b\x12\x11\x82\x87\x88\x87>8:\x10Z\x8f\x90\x91\x87\x19.\x0fU\x97USR\x9bPY\x82\x8b9\r\x98\x97S\xa5QX\x87\x17-\x0cVV/,+*(\'R\xa8\x7f>49\x0bWW,3210#RU\x87\x16)\nXX\xb2\'$ \x1fPT\x9f\xb9\tYX\xadVUQPNM\x87\x15%\x08\xd7&!\x1d\x1c\x1a\x18JK\xd37\x07XW\xd9T\xcaXP@\x87\x14"\x06\xbcWT\xa7\xf4;H\xa6\xd5 \xa0\xcc\x8a\x94\'Y\xa0\xf08\xa2\xe5\xd0\x04\x0f\x03\x94\xf5k\x12ea\x96\x86\xb7h\xd4\x10\xb0%\x8bA&D\x92p\x19y\xa8\x80\x83\x00F\x8a\x0c\t\x02D\x08\x90\x1e?l \x02\x90\xa8\xe6\x9f@\x00;'

		self.b64["cog.gif"] = b'GIF87a\x10\x00\x10\x00\xc4\x00\x00\x00\x00\x00GGGMMMTTT[[[ccclllpppyyy\x82\x82\x82\x8d\x8d\x8d\x94\x94\x94\x9c\x9c\x9c\xa5\xa5\xa5\xac\xac\xac\xb4\xb4\xb4\xbc\xbc\xbc\xc4\xc4\xc4\xcb\xcb\xcb\xd4\xd4\xd4\xdc\xdc\xdc\xe5\xe5\xe5\xeb\xeb\xeb\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00\x18\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x05\x91 &\x8e\x92\x14Ac\xaaFU\xe5\xa8\xe3Tb\x11E=\x98\xd341eQ\xa7\xc9\xe4\xe1\x90T \n\x91\x892\xb1\t\x99%\xc4a\x14\x91I \x8cFd\x8bTn)\xd7\x04"\xa1\xd8J\x14\x89D\xc4bm$D\x0c\xc7\xa9f`M"\x92\xc7B\xb4\x90C\xaa\x05\r\x0b\rw\x12\x0c\x0c\x0be\x10\x10\x05\x03\x03"rf\x0e~D\x06#:\x85V&\x10\x12\x06\x05"\r\x10\x14nj\x11\x06\x06\x84\t\x8f"\t\x9e\x18\t%\x9f\x03\x02\x010\xac\x10\x0f\x04\xb6*\x06\xb3\xab)!\x00;'

		self.b64["page_white_world.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00=[0B\x89\xc1M\x91\xc1\x95\x95\x95d\x97SK\x99\xbd\x9b\x9b\x9bj\x9cVk\x9fZm\xa0Wl\xa1ZN\xa2\xd4T\xa2\x8ae\xa4\x83P\xa6cV\xa6\xd6f\xa6\xa3W\xa7\xce\x7f\xa8iT\xaa\xe2U\xac\xdc|\xactg\xad\xda\x80\xadk\x82\xadsb\xaf\xc9m\xaf\xcf\x85\xafy\x86\xb0x\x88\xb3|\x82\xb4\x84i\xb5\xcdi\xb6\xab\x8b\xb6\xa7\x8d\xb7\xbc\x8d\xb9xS\xba\x9d\x8a\xbal\x92\xbb\x91\x97\xbb{f\xbd\xb8p\xbd\xc1z\xc1\xd7\xa0\xc3\x88Z\xc4`\x84\xc4\xdb\x8c\xc4\xd2\x9b\xc4\x7f\x9c\xc4\x85\xa4\xc5\x91|\xc6t\xaa\xc6\xa0\x82\xc7\xcbw\xc9\xc6\xaa\xc9\x8f\xac\xc9\xa2\x8e\xcb\xb0\xa3\xcb\x9b\xa0\xcc\xbbk\xd0\xad\xa2\xd2\x8d\xc3\xd5\xbc\x83\xd6\xb1\x9b\xd6\xd9q\xd7\x93\xa4\xd8\x94y\xda\x96\xc8\xda\xc2B\xdb^\xbd\xdb\xbaZ\xdc}\xa0\xdc\x8f\xa4\xdc\xdc\xb6\xdd\xd5\xd3\xde\xce\x91\xe0\x8b\xd4\xe0\xd0\xc3\xe3\xaf\xbf\xe5\xd5\xdb\xe6\xd6\x8c\xe7\xa2\xe7\xe7\xe7\xbe\xea\xd6\xbb\xec\xca\xec\xec\xec\xac\xf1\xbc\xd0\xf2\xce\xf4\xf4\xf4\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00Z\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xa8\x80Z\x82\x83\x84\x85\x84Y\x88\x89\x89\x04\x86YX\x8f\x8fUUYR\x8c\x83\x018\x19\x0b\x194MX\x93\x8f\x07\x82\x08\x082FJ;\x1f\x1d>\x93\x89\x82\x0bNWOI./:\x19K\x92RYZ\n1VT@+)AL\x184\x9f\x93Z\x0bBQS 6GE-,\x19\x90\xbc\x0bHC5\x12*<%\x0f7\t\x8eX\xd8=?\x1a\x15\x0c\x02\x03\x0e(\x19\x8a\xcb$3!\x10\x14\x06\r\x1e\t8\xf1Z\x08096\\\x88`b\x02\x07(\xfd\x10\x14\xb0 b\xc4\x89\x04\x1c\x88(\xe2%\x08S\x86\x04\x19p \x9cxh\xa2GC \t\x05\x02\x00;'

		self.b64["page_excel.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa$_\xb8)b\xb7*d\xbb.i\xbe0i\xbaIm\xb62o\xc06t\xc2.u\x138v\xc33x\x18?y\xbe;{\xc4<~\x80B~\xc3?\x7f)?\x80\xc7D\x834D\x83\xc6F\x88\xc3I\x89\xc6Q\x8boM\x8c\xc9T\x8cSU\x8dAI\x92I[\x93E_\x93Sd\x93\xdc_\x95Ic\x97Sc\x98Oe\x98Wd\x9adj\x9c`q\x9fdm\xa1Zs\xa1km\xa2Wt\xa5\\i\xac`u\xaff\x83\xaf\x8d}\xb2\xe3\x90\xb5\x90q\xb7\\\x82\xb7q\x84\xb7\xe3\x96\xba\xa2\x84\xbcx\x87\xbds\x84\xc1i\x8a\xc2l\xa2\xc2\xb2\x96\xc9t\x98\xcav\xb5\xd2\xe9\xa4\xd4\x82\xb5\xd4\xf2\xbf\xd4\xb6\xba\xd7\xf5\xc4\xd7\xbc\xb5\xd9\xf6\xbd\xda\xf6\xc3\xda\xe5\xb6\xdb\x9d\xcb\xdc\xc4\xc3\xdd\xf8\xc4\xdd\xf4\xce\xde\xc8\xc7\xe0\xfa\xcd\xe1\xf5\xcb\xe3\xfb\xd2\xe5\xfc\xd8\xe6\xf2\xde\xea\xf6\xe1\xec\xf6\xe9\xef\xf5\xe6\xf0\xf7\xec\xf2\xf7\xec\xf3\xf9\xf2\xf6\xfa\xf5\xf9\xfc\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00V\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc5\x80V\x10\x18\x84\x85\x84\x16\x0bV\x8a\x8a\x14QR\x8f\x90QL-\x1e\x8bV\x16SJ\x9aJHE>U@\x94\x8b\x98\x9b\x9a\x9eU\x9a1\rV\x1a\x19  2,\x11\x11\x13\x13.QSO\x10\xac=C8 \x1f)(!#:<<S\x14\x8a\x17D;6\xc0\xc4FEAAR\xcaV\x15%D94\x1a\x1dI\xa6E\xd6\x8a\x0f\x0c\x1cG50\x1a7K\x9aHR\x12V\n\n&\x1c\xe7/+\x1a\n\x9bS\x0e\xf2\xf3\n4\x90\xf81C\x05\x88MT\x12(r\x00e\xc9\x12!%@\x888\xe1p\t\x15\x04\x0b\x9dT\xdcXq\n\x01E\t4r\xdcX\xe5\xa3\x95\x02R\x9c4Y\xd9\x04\xd2\x14*U\x04(2@\xa0\xa6\xcd\x9b\x04\x06\x0c\xb0\x12\x08\x00;'

		self.b64["page_word.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x1bN\xd3\x1dS\xd4+U\xaa ^\xd3$_\xb8)b\xb7*d\xbb\x1ee\xd3!g\xd4.i\xbe0i\xbaIm\xb62o\xc0%p\xd66t\xc28v\xc3=v\xd2?y\xbe:z\xc4=z\xd2I}\xd2A~\xd2B~\xc3?\x80\xc7C\x82\xd3D\x83\xc6L\x84\xd5]\x87\xe3I\x89\xc6M\x8c\xc9l\x8c\xe5H\x8d\xe4T\x8e\xe3a\x92\xe5d\x93\xdcN\x96\xe4o\x99\xe5T\x9a\xe5f\x9d\xe6v\x9d\xe7|\x9d\xe8Z\xa1\xe5\x88\xa1\xe9c\xa2\xe6l\xa2\xe8\x85\xa2\xe9i\xa5\xe7p\xa7\xe8\x84\xa7\xe6\x8a\xac\xebq\xad\xe8}\xb2\xe3\x8e\xb3\xed\x91\xb5\xed\x9c\xb5\xef\x84\xb7\xe3\xb6\xcb\xef\xb5\xd4\xf2\xbb\xd7\xf5\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc7\xe0\xfa\xd4\xe1\xf3\xcb\xe2\xfb\xd2\xe5\xfc\xd8\xe6\xf2\xd8\xe7\xfe\xde\xea\xf6\xe1\xeb\xf6\xe9\xef\xf5\xec\xf2\xf7\xec\xf3\xf9\xf2\xf6\xfa\xf5\xf9\xfc\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00M\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc5\x80M\x17\x1e\x84\x85\x84\x1d\x10M\x8a\x8a\x1aHI\x8f\x90HC4#\x8bM\x1dJA\x9aA?>;L<\x94\x8b\x98\x9b\x9a\x9eL\x9a8\x12M\x0e**56&52\x19!FHJG\x17M\t3,B&$B%\x19=;::J\x1a\x8a,9D\x19(B\x162A>==I\xcb\x08/1\x19/" \x16B\xa6>\xd9M\x04/0\x16)-\x1b7B\xe3\x9cI\x18M\x02,\x19A.\'\x14\xf0\xf1AJ\x13\xea\xbd\xa8 \x84\xc3\x86\x15\xf0J-y\xd0$\x80\x05 B>D\xe8GqI\x03E\x13\x8cP\xdc(D\xc9\x01E\x0f4r\xec\xc7\xe4c\x13\x05I\x8c\x14YY\x04\x92\x92%L\n(Zp\xa0\xa6\xcd\x9b\x07\x0c\x18h\x12\x08\x00;'

		self.b64["page_white_acrobat.gif"] = b'GIF87a\x10\x00\x10\x00\xd5\x00\x00\x00\x00\x00\x97\n\x08\x9b\x0e\n\xc1\x10\x0e\xcc\x10\x0c\xd0\x13\r\xc3\x1e\x0f\xdb4(\xe0NC\xdcSM\xe0SJ\xe6]Q\xe3d\\\xeag\\\xe5h_\xe8i_\xe4le\xe7ul\xedvj\xe5{u\xee\x7ft\xf1\x7fs\xe5\x81z\xf1\x84x\xe6\x87\x81\x95\x95\x95\x9b\x9b\x9b\xed\x9d\x98\xe9\xa1\x9c\xeb\xa4\xa0\xf2\xa7\x9f\xed\xac\xa8\xf3\xae\xa7\xef\xb9\xb5\xf3\xc0\xba\xf1\xc4\xc1\xf2\xcc\xca\xf5\xd1\xcd\xf6\xd7\xd5\xf7\xdd\xdb\xf8\xdf\xdd\xf8\xe5\xe5\xe7\xe7\xe7\xf7\xe9\xe8\xf9\xe9\xe7\xec\xec\xec\xf9\xee\xed\xf9\xf3\xf3\xf4\xf4\xf4\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x002\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06r@\x99pH,\x12c\xc8d2c\x8c\xc1."\x18\xac\xd5\x8a\xa9\x98GX\xa5$\x9d:a\x9acL\xe2\xe9V\x93b\n\x08)\xa5\xaab\xe2\x86$\xd9\xae\x1eQ\x8b\x87\x89.\x85\x0fc\x11\x1b\'\x0e\'|~B,\n)\'\x10\x07\x08\x0c\x13\x1fHD\x13\x16!\x1d#&\x18\x10\x13\x1c\x93B\x02\t.JH+/\x9f\x05\x03$\xa4\xac2\x04\x04\x01\xac\xad\x7f\xb2JF\xb7DA\x00;'

		self.b64["page_calc.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x00\x00>\x00\x00A\x00%O\x00\'P\x146S\x007\\\x19;X\t<[!Cb,Ge-He7Md.Nt\'Ol*On?Rs\x00S{1Sl\x00UUAUmUUUUU\xaa4\\y&^\x82:_}?_\x83fff;k\x8bEk\x8bFk\x86Jk\x86bo~ir\x89Zs\x8cVt\x95Ew\x9aVz\x94i}\x92\x80\x80\x80Y\x82\xa2{\x88\x95\x86\x98\xa9\x89\x99\xa5\x82\x9b\xb1\x9f\xa3\xaf\x9a\xa9\xb6U\xaa\xaa\x9e\xb0{\xa6\xb1\xbc\xa3\xb3t\xaa\xb3\xbb\x92\xb6\xb6\xb0\xb8\xc1\x80\xbf@\xb7\xbf\x8f\xbf\xbf@\xb0\xc2m\xaf\xc5?\xac\xc6\x1f\xaf\xc7%\xba\xc7\xd1\xae\xce\x00\xbc\xce\xda\xc4\xd1\xdc\xbc\xd2\x85\xd1\xd3\xd6\xc1\xd6g\xca\xd6\x91\xcc\xd6\xe0\xcf\xd6\xdb\xc5\xd7\xe4\xd2\xd7\xda\xcc\xd8\xb4\xcf\xda\xe1\xd3\xda\xd3\xd4\xda\xdf\xd2\xde\xa6\xd5\xde\xe4\xd7\xde\xe8\xd3\xdf\xaa\xd9\xdf\xd2\xcc\xe0\xef\xd6\xe0\xae\xd6\xe1\xea\xd8\xe1\xb6\xdb\xe1\xd4\xdc\xe3\xe7\xd1\xe4\x8a\xdc\xe4\xea\xdc\xe5\xba\xde\xe5\xc3\xe0\xe6\xc6\xe1\xe6\xdc\xe1\xe7\xc9\xe1\xe7\xeb\xdf\xe8\xbd\xe4\xe9\xed\xe5\xea\xcc\xe2\xeb\xc5\xe5\xec\xf3\xe6\xec\xe5\xe7\xec\xd0\xe0\xed\xf8\xe9\xed\xd3\xe9\xee\xf3\xeb\xef\xea\xe7\xf1\xc4\xe8\xf1\xc7\xec\xf1\xf9\xed\xf2\xe7\xed\xf2\xe8\xed\xf2\xf5\xf0\xf3\xec\xf3\xf5\xf9\xf7\xf7\xf7\xf3\xf9\xfb\xfa\xfc\xf6\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00w\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xbf\x80w\x82\x18\x11Hvd_rjD\x82\x8dwFE@gYJYttX<2\x8d53&*?LpiLOA>;\x8ew"1idNFNdI9C:\x8dYTNRGWp\xbf\xaemKw==+\x04 Navr\x97\x97\xcc\x8e\x06\x14sv\xd5\xd6\xd6\x8e\x0b\x02B\xd7uv\xdev\x8e\n\x01-uUcSb\xe9lq\x8e\t\x03!nZbPhMfkn\xee\x08\x10]\xf3\xf5M\xc4\xacy\xe3\xe8\x81\x83\x06Q\xc0\xd0\xb3\'P_\xa3\x0c\x174XQ\x08\x10M>G\x1d8\x8c\xf0\xb7\x05\x8a\x17(\\\xc6\x94q\x84\x82\x04\x0bg\xce\xe0\xd8\xf9\xe2\xa8\x04\x07\x17a\xb2\xc8\x9c\x99\xc5\xc9\x9d@\x00;'

		self.b64["page_writer.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x00\x00C\x00)R\x146S\x007\\\x19;X\x16?_\x00@d"Db,Ge-He7Md)On,Qo1Sl#Tu\x00UU\x00U|AUmUUUUU\xaa:^}&_\x83\x00c\x8ffff]j|Ck\x8cFk\x86Jk\x869m\x8cKo\x8cbo~ar\x84Zs\x8cOw\x96Ex\x9bVz\x94i}\x92@\x80\x80\x80\x80\x80Y\x83\xa3c\x85\x9e{\x88\x95y\x8a\x9a\x86\x98\xa9\x89\x99\xa5~\x9a\xb1\x85\x9c\xb1\x99\x9f\xa7\x8c\xa8\xbfU\xaa\xaa\x9d\xac\xb7\xa6\xb1\xbd\xaa\xb3\xbb\x92\xb6\xb6\xa0\xb6\xc8\xb1\xbb\xc4\xb9\xc6\xd1\xbe\xca\xd4\xc3\xcc\xd5\xbc\xce\xda\xc6\xd0\xdb\xcc\xd3\xda\xd1\xd3\xd6\xc5\xd7\xe4\xcc\xd7\xe0\xd1\xd7\xdc\xd2\xd9\xde\xcf\xda\xe1\xd5\xde\xe4\xcc\xe0\xef\xd6\xe1\xea\xdb\xe1\xe7\xda\xe4\xec\xe0\xe6\xea\xe3\xe9\xed\xe9\xec\xee\xe0\xed\xf8\xe7\xed\xf3\xeb\xee\xf1\xee\xf2\xf6\xf3\xf4\xf6\xf5\xf7\xf9\xf5\xfa\xfd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00U\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb8\x80U\x82\x16\x11BTNJQL8\x82\x8dU>A=MIDISS7)\x8e85%,<CPOCH/\x17"\x8eU!4ONE>EK9/1.\x8dIGEF@HP\xbe\xa2PCU99-\x02\x1f\xb1TRR\x97S\xca\x8e\x04\x12QT\xd4\xd5\xd5\x8e\n\x01?\xcaQ\xdd\xdd\xd4\x8e\t\x010TJ;>\xe8;\xe0\x8d\x08\x02\x19TL>C\xf3\xd7\xec\x06\x08\x8a>BB\xe8\xeb\x82\x0c\r\x0e0y\x82\x0e\x1d\x13\x7fU*Tx\xf0\x84\xe0\x90}\xd3\xa88\xd2\xa0\xc1\xc3\x13s>z\xf4\xd0A%\x8a#\x14#^4\x1bY\xce\x11\x89\x0e3\x96 Y\xc92I\x91*\x81\x00\x00;'

		self.b64["picture.gif"] = b"GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x9b{1v\x82]\x80\x83T\xb0\x86<\x87\x8b>\x86\x8eA^\x91\x8bc\x93\x91b\x978i\x97\xa4e\x9a<i\x9a\xa6s\x9e\xc4w\x9e\xd7h\x9f\x9b\xd3\xa0R|\xa2\xd9}\xa3\xc6\x81\xa5\xdbt\xa7H\x82\xa7\xc8\x8e\xa7\xce\x84\xa8\xdd\x8e\xa8\xcew\xa9Jx\xab\xa0z\xabL\x94\xab\xcf{\xacj\x8a\xac\xdf\x94\xac\xd0\x9a\xae\xce\x8e\xaf\xe1\x9b\xaf\xd0\xd2\xb0m|\xb1x\x9b\xb1\xce\x87\xb3o\xa0\xb3\xd0\x7f\xb4\xa2\x87\xb4\xb7\x8d\xb5\xd1\x96\xb5\xe4\xa3\xb5\xce\x80\xb6\xaa\x93\xb6\xd2\x98\xb6\xe4\x80\xb7\xa4\x87\xb8\xb9\x9c\xb9\xe5z\xbbM\x87\xbc`\x8b\xbc\x83\xa0\xbc\xe7\x7f\xbeS\x87\xbek\x8a\xbed\xa2\xbe\xe8\x81\xbfQ\x87\xc2U\x8b\xc3W\x8e\xc3q\x94\xc3\x8a\x8f\xc6b\x91\xc7]\xca\xc9\x9d\x99\xcai\x9a\xcad\xa2\xcd\x93\xa1\xce}\xa7\xd1\x82\xaa\xd2\x83\xa9\xd3t\xc6\xd4\xb0\xc4\xda\xbb\xc3\xdd\xc0\xeb\xec\xec\xe6\xee\xf6\xeb\xef\xf2\xed\xf2\xf7\xef\xf3\xf8\xf1\xf4\xf8\xf3\xf5\xf7\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00U\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb5\x80U\x82\x83\x84\x85\x82,'\x1c\x18\x8b\x8b\x16\x8e\x16\x1c%\x82'MS\x96\x97\x97PO \x82\x1cS+*-EHG?\x0f\r\x0eP\x1f\x82\x18S/1EIDDC5\x0c\x11\xaa\xacS20HDA=<>\x07\xb8\x1c\xba2(FA<;78\x07\x13N\xc6U\x18P2)?@;37$\n\x17\xd2\xacP6.\x1a&94\x1d\x08\x12\x1e\xe1\xd4P:\xe4\x02\x06\x05\x03\x15!\xed\xd3\xd5\x1b\x19\x14\x01\x10\x10\x08,X\x90\xc0\x9d\x05(L\x12*\x112bIB&\x06\x11>\x9c\x98\xd0\x1d\x87'S\xa4H\xb1\x04\xa5#\x94(OD\x08*!\x82\x83\xc9\x93(Ap2\xc4rP \x00;"

		self.b64["color_swatch.gif"] = b'GIF87a\x10\x00\x10\x00\xb3\x00\x00\x00\x00\x00\xfeoj\xffw\xb2Vz\xb1\xda\x9c\xde\xff\xabs_\xb1\xebN\xcdl\xf0\xd6f\xd1\xeb\xb3\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00\x0b\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x04@p\xc9I\xab\xbd6\xe8U\xfaB`\xa5\x05\x9c\x07"\xe2\xd6\x15_\x88\xbdS"/G\xbd\x18x%\'\xb4\x8d\x1b\xbaY\xedp\xcb\xc1`\x83\xe4\x82\xc0\\\x08\x9e\x95\xe4`\xd9|\n\xa2J&\xc1\t=z\xbf\xe0\x08\x00;'

	def set_app_icon(self):
		script_dir = os.path.dirname(os.path.abspath(__file__))
		icon_dir = os.path.join(script_dir, "icons")
		base.debugmsg(5, "icon_dir:", icon_dir)
		icon_file = os.path.join(icon_dir, "rfswarm-reporter-128.png")
		self.icon = tk.PhotoImage(file=icon_file)
		self.root.wm_iconphoto(False, self.icon)

	def updateTitle(self):
		titletext = "{} v{} - {}".format(self.titleprefix, base.version, "Please Select")
		# ['Reporter']['ResultDir']
		if 'Reporter' in base.config and 'Results' in base.config['Reporter']:
			if len(base.config['Reporter']['Results']) > 0:
				path, filename = os.path.split(base.config['Reporter']['Results'])
				basepath, dirname = os.path.split(path)
				titletext = "{} v{} - {}".format(self.titleprefix, base.version, dirname)

		self.master.title(titletext)

	def updateStatus(self, newstatus):
		# newstatus = "Template: Untitled"
		self.statusmsg.set(newstatus)

	def updateResults(self):
		# self.stsResults.set(base.config['Reporter']['Results'])
		if base.config['Reporter']['Results']:
			sres = "Results: {}".format(base.config['Reporter']['Results'])
			self.stsResults.set(sres)
		else:
			sres = "Results: Please select a result file"
			self.stsResults.set(sres)

	def updateTemplate(self):
		# self.stsTemplate.set(base.config['Reporter']['Results'])
		if base.whitespace_get_ini_value(base.config['Reporter']['Template']):
			stem = "Template: {}".format(base.whitespace_get_ini_value(base.config['Reporter']['Template']))
			self.stsTemplate.set(stem)
		else:
			stem = "Template: Untitled"
			self.stsTemplate.set(stem)

	def save_window_size(self, event):
		base.debugmsg(6, "save_window_size")
		try:
			base.debugmsg(6, "winfo_width:", self.winfo_width(), "	winfo_height:", self.winfo_height())
			base.config['GUI']['win_width'] = str(self.winfo_width())
			base.config['GUI']['win_height'] = str(self.winfo_height())
			base.saveini()
		except Exception as e:
			base.debugmsg(6, "save_window_size except:", e)
			return False

	def BuildMenu(self):
		window = self.master
		self.root.option_add('*tearOff', False)
		root_menu = tk.Menu(window)

		if sys.platform.startswith('darwin'):
			appmenu = tk.Menu(root_menu, name='apple')
			root_menu.add_cascade(menu=appmenu)
			appmenu.add_command(label='About rfswarm Reporter')
			appmenu.add_separator()
			base.debugmsg(5, "appmenu:", appmenu)

		window.config(menu=root_menu)
		results_menu = tk.Menu(root_menu)  # it intializes a new sub menu in the root menu
		root_menu.add_cascade(label="Results", menu=results_menu)  # it creates the name of the sub menu

		# accelkey = "Ctrl"
		accelkey = "Control"
		if sys.platform.startswith('darwin'):
			accelkey = "Command"
		shifkey = "Shift"

		results_menu.add_command(label="Open", command=self.mnu_results_Open, accelerator="{}-o".format(accelkey))
		window.bind("<{}-o>".format(accelkey), self.mnu_results_Open)
		results_menu.add_separator()  # it adds a line after the 'Open files' option

		if sys.platform.startswith('darwin'):
			# https://tkdocs.com/tutorial/menus.html
			# root.createcommand('tk::mac::ShowPreferences', showMyPreferencesDialog)
			self.root.createcommand('tk::mac::Quit', self.on_closing)
		else:
			results_menu.add_command(label="Exit", command=self.on_closing, accelerator="{}-x".format(accelkey))
			window.bind("<{}-x>".format(accelkey), self.on_closing)

		self.template_menu = tk.Menu(root_menu)
		root_menu.add_cascade(label="Template", menu=self.template_menu)

		self.template_menu.add_command(label="New", command=self.mnu_template_New, accelerator="{}-n".format(accelkey))  # it adds a option to the sub menu 'command' parameter is used to do some action
		window.bind("<{}-n>".format(accelkey), self.mnu_template_New)
		self.template_menu.add_command(label="Open", command=self.mnu_template_Open, accelerator="{}-t".format(accelkey))
		window.bind("<{}-t>".format(accelkey), self.mnu_template_Open)
		self.template_menu.add_command(label="Save", command=self.mnu_template_Save, accelerator="{}-s".format(accelkey))
		window.bind("<{}-s>".format(accelkey), self.mnu_template_Save)
		self.template_menu.add_command(label="Save As", command=self.mnu_template_SaveAs, accelerator="{}-{}-s".format(accelkey, shifkey))
		window.bind("<{}-S>".format(accelkey), self.mnu_template_SaveAs)

	def BuildUI(self):

		self.bind("<Configure>", self.save_window_size)

		self.ConfigureStyle()

		self.bbar = tk.Frame(self)
		self.bbar.grid(column=0, row=0, sticky="nsew")
		# self.bbar.config(bg="red")

		self.mainframe = tk.Frame(self)
		self.mainframe.grid(column=0, row=1, sticky="nsew")
		# self.mainframe.config(bg="green")

		self.stsbar = tk.Frame(self)
		self.stsbar.grid(column=0, row=9, sticky="nsew")
		# self.stsbar.config(bg="pink")

		# statusmsg
		self.stsTemplate = tk.StringVar()
		self.stsResults = tk.StringVar()
		self.statusmsg = tk.StringVar()

		self.ststmpl = ttk.Label(self.stsbar, textvariable=self.stsTemplate)
		self.ststmpl.grid(column=0, row=0, sticky="nsew")
		self.stsres = ttk.Label(self.stsbar, textvariable=self.stsResults)
		self.stsres.grid(column=0, row=1, sticky="nsew")
		self.stslbl = ttk.Label(self.stsbar, textvariable=self.statusmsg)
		self.stslbl.grid(column=0, row=3, sticky="nsew")

		self.stsbar.columnconfigure(0, weight=1)
		self.stsbar.rowconfigure(0, weight=1)
		self.updateStatus("")
		self.updateResults()
		self.updateTemplate()

		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		self.mainframe.rowconfigure(1, weight=1)

		self.sbbar = tk.Frame(self.mainframe)
		self.sbbar.grid(column=0, row=0, sticky="nsew")
		# self.sbbar.config(bg="blue")

		self.sections = tk.Frame(self.mainframe, relief=tk.SUNKEN, bd=3)
		self.sections.grid(column=0, row=1, sticky="nsew")
		# self.sections.config(bg="cyan")
		# self.mainframe.columnconfigure(0, weight=1)
		self.sections.columnconfigure(0, weight=1)
		self.sections.rowconfigure(0, weight=1)

		# self.btnShowHide = tk.StringVar()
		# btnShowHide = tk.Button(self.mainframe, textvariable=self.btnShowHide, command=self.sections_show_hide, width=1, padx=0, pady=0, bd=0, relief=tk.FLAT, fg=self.style_text_colour)
		# self.btnShowHide.set("<")
		# btnShowHide.grid(column=1, row=1, sticky="nsew")
		# btnShowHide.rowconfigure(1, weight=1)

		self.content = tk.Frame(self.mainframe, bd=0)
		self.content.grid(column=2, row=0, columnspan=2, rowspan=2, sticky="nsew")
		# self.content.config(bg="lightblue")
		self.content.columnconfigure(0, weight=1)
		self.content.rowconfigure(0, weight=1)

		self.mainframe.columnconfigure(2, weight=1)
		self.mainframe.columnconfigure(3, weight=1)

		self.ConfigureStyle()

		self.BuildToolBar()
		self.BuildSections()
		self.BuildContent()

	def ConfigureStyle(self):

		self.style_head_colour = base.rs_setting_get_hcolour()

		fontname = base.rs_setting_get_font()
		fontsize = base.rs_setting_get_fontsize()
		sizeup = int(fontsize * 0.1)
		if sizeup < 1:
			sizeup = int(1)
		base.debugmsg(8, "sizeup:", sizeup)

		# Theme settings for ttk
		self.style = ttk.Style()

		self.style.configure("TFrame", borderwidth=0)

		if sys.platform.startswith('darwin'):
			release, _, machine = platform.mac_ver()
			split_ver = release.split('.')
			if int(split_ver[0]) > 10:
				# we really only seem to need this for MacOS 11 and up for now
				# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-style-layer.html
				# https://tkdocs.com/tutorial/styles.html#usetheme

				self.style.configure("TLabel", foreground=self.style_text_colour)
				self.style.configure("TEntry", foreground="systemPlaceholderTextColor")
				self.style.configure("TEntry", insertcolor=self.style_text_colour)

				self.style.configure("TButton", foreground=self.style_text_colour)
				self.style.configure("TMenubutton", foreground=self.style_text_colour)

				self.style.configure("Canvas", fill=self.style_text_colour)
				self.style.configure("Canvas", activefill=self.style_text_colour)

				self.style.configure("TSpinbox", foreground=self.style_text_colour)

				self.style.configure("TRadiobutton", foreground=self.style_text_colour)

				self.style.configure("Treeview", foreground=self.style_text_colour)
				self.style.configure("Treeview", background=self.rootBackground)
				self.style.configure("Treeview", fieldbackground=self.rootBackground)

				base.debugmsg(9, "self.style_text_colour:	", self.style_text_colour)
				base.debugmsg(9, "self.rootBackground:		", self.rootBackground)

		layout = self.style.layout('TLabel')
		base.debugmsg(9, "TLabel 	layout:", layout)
		self.style.configure("Head.TLabel", foreground=self.style_head_colour)

		layout = self.style.layout('Head.TLabel')
		base.debugmsg(9, "Head.TLabel 	layout:", layout)

		matplotlib.rcParams['font.family'] = fontname

		self.style.configure('Report.TLabel', font=(fontname, fontsize))

		base.debugmsg(9, "fontsize:", fontsize, "	sizeup:", sizeup, "	5*sizeup:", 5 * sizeup, "	H1 size:", fontsize + (5 * sizeup))

		self.style.configure("Report.H1.TLabel", foreground=self.style_head_colour)
		# self.style.configure("Report.H1.TLabel", foreground=self.style_head_colour, background=self.style_reportbg_colour)
		self.style.configure('Report.H1.TLabel', font=(fontname, fontsize + (5 * sizeup)))
		# self.style.configure('Report.H1.TLabel', background=self.style_reportbg_colour)
		# self.style.configure('Report.H1.TLabel', activebackground=self.style_reportbg_colour)
		layout = self.style.layout('Report.H1.TLabel')
		base.debugmsg(9, "Report.H1.TLabel 	layout:", layout)

		self.style.configure("Report.H2.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H2.TLabel', font=(fontname, fontsize + (4 * sizeup)))

		self.style.configure("Report.H3.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H3.TLabel', font=(fontname, fontsize + (3 * sizeup)))

		self.style.configure("Report.H4.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H4.TLabel', font=(fontname, fontsize + (2 * sizeup)))

		self.style.configure("Report.H5.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H5.TLabel', font=(fontname, fontsize + (1 * sizeup)))

		self.style.configure("Report.H6.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H6.TLabel', font=(fontname, fontsize))

		self.style.configure('Report.Title1.TLabel', font=(fontname, fontsize + (10 * sizeup)))
		self.style.configure('Report.Title2.TLabel', font=(fontname, fontsize + (5 * sizeup)))

		self.style.configure("Report.THead.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.THead.TLabel', font=(fontname, fontsize + (1 * sizeup)))
		self.style.configure('Report.THead.TLabel', relief="raised")

		self.style.configure('Report.TBody.TLabel', font=(fontname, fontsize))
		# self.style.configure('Report.TBody.TLabel', relief="sunken")
		# self.style.configure('Report.TBody.TLabel', relief="ridge")
		self.style.configure('Report.TBody.TLabel', relief="groove")

		self.style.configure('Report.Settings.FileInput.TLabel', relief="sunken")

	def BuildToolBar(self):
		btnno = 0

		# Open Scenario Results
		# 	"Open Scenario Results"	folder_table.png
		icontext = "Open Scenario Results"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_results_Open)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		btnno += 1
		# New Report Template
		# 	"New Report Template"	page_add.png
		icontext = "New Report Template"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_template_New)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# Open Report Template
		# 	self.imgdata["Open Report Template"] = folder_page.png
		btnno += 1
		icontext = "Open Report Template"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_template_Open)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# Save Report Template
		# 	"Save Report Template"	page_save.png
		btnno += 1
		icontext = "Save Report Template"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_template_Save)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# # Apply Report Template
		# # 	"Apply Report Template"	page_go.png
		# btnno += 1
		# icontext = "Apply Report Template"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_do_nothing)
		# bnew.grid(column=btnno, row=0, sticky="nsew")

		btnno = 9
		self.bbar.columnconfigure(btnno, weight=1)

		# "Export HTML"		page_white_world.gif			HTML - Issue #36
		btnno += 1
		icontext = "Export HTML"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_html)
		bnew.grid(column=btnno, row=0, sticky="nsew")
		# https://github.com/eea/odfpy		MHT and HTML
		# https://docs.python.org/3/library/markup.html
		# https://github.com/CenterForOpenScience/pydocx

		# # "Export PDF"		page_white_acrobat.png
		# btnno += 1
		# icontext = "Export PDF"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_pdf)
		# bnew.grid(column=btnno, row=0, sticky="nsew")

		# # "Export Writer"		page_writer.gif
		# btnno += 1
		# icontext = "Export Writer"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_writer)
		# bnew.grid(column=btnno, row=0, sticky="nsew")
		# # https://github.com/eea/odfpy
		# # https://en.wikipedia.org/wiki/OpenDocument_technical_specification
		# # https://docs.python.org/3/library/zipfile.html

		# "Export Word"		page_word.png					Word - Issue #38
		btnno += 1
		icontext = "Export Word"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_word)
		bnew.grid(column=btnno, row=0, sticky="nsew")
		# https://python-docx.readthedocs.io/en/latest/
		# https://github.com/python-openxml/python-docx
		# http://officeopenxml.com/
		# https://docs.python.org/3/library/zipfile.html

		# # "Export Calc"		page_calc.gif
		# btnno += 1
		# icontext = "Export Calc"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_calc)
		# bnew.grid(column=btnno, row=0, sticky="nsew")
		# # https://github.com/pyexcel/pyexcel
		# # https://github.com/pyexcel/pyexcel-ods

		# "Export Excel"		page_excel.png				Excel - Issue #37
		btnno += 1
		icontext = "Export Excel"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_excel)
		bnew.grid(column=btnno, row=0, sticky="nsew")
		# https://xlsxwriter.readthedocs.io/introduction.html
		# https://openpyxl.readthedocs.io/en/stable/index.html
		# https://github.com/pyexcel/pyexcel
		# https://github.com/python-openxml/python-xlsx - seems doesn't exist

	def BuildSections(self):

		# self.sbbar
		btnno = 0
		# New Section
		# 	"New Section"	add.gif
		icontext = "New Section"
		bnew = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_new_rpt_sect)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# Remove Section
		# delete.gif
		btnno += 1
		icontext = "Remove Section"
		brem = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_rem_rpt_sect)
		brem.grid(column=btnno, row=0, sticky="nsew")

		# Move Section Up
		# resultset_up.gif
		btnno += 1
		icontext = "Section Up"
		bup = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_rpt_sect_up)
		bup.grid(column=btnno, row=0, sticky="nsew")

		# Move Section Down
		# resultset_down.gif
		btnno += 1
		icontext = "Section Down"
		bdwn = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_rpt_sect_down)
		bdwn.grid(column=btnno, row=0, sticky="nsew")

		# 	https://pythonguides.com/python-tkinter-treeview/
		self.sectionstree = ttk.Treeview(self.sections, selectmode='browse', show='tree')

		self.sectionstree.grid(column=0, row=0, sticky="nsew")
		# ttk.Style().configure("Treeview", background="pink")
		# ttk.Style().configure("Treeview", fieldbackground="orange")

		self.sections.vsb = ttk.Scrollbar(self.sections, orient="vertical", command=self.sectionstree.yview)
		self.sectionstree.configure(yscrollcommand=self.sections.vsb.set)
		self.sections.vsb.grid(column=1, row=0, sticky="nsew")

		self.sections.hsb = ttk.Scrollbar(self.sections, orient="horizontal", command=self.sectionstree.xview)
		self.sectionstree.configure(xscrollcommand=self.sections.hsb.set)
		self.sections.hsb.grid(column=0, row=1, sticky="nsew")

		self.sectionstree.bind("<Button-1>", self.sect_click_sect)

		self.LoadSections("TOP")

	def LoadSections(self, ParentID):
		if ParentID == "TOP":
			items = self.sectionstree.get_children("")
			base.debugmsg(9, "items:", items)
			if len(items) > 0:
				for itm in items:
					self.sectionstree.delete(itm)
			self.sectionstree.insert("", "end", ParentID, text="Report", open=True, tags=ParentID)
		else:
			items = self.sectionstree.get_children(ParentID)
			base.debugmsg(9, "items:", items)
			if len(items) > 0:
				for itm in items:
					self.sectionstree.delete(itm)

		sections = base.report_get_order(ParentID)
		base.debugmsg(9, "sections:", sections)
		for sect in sections:
			self.LoadSection(ParentID, sect)

		self.sectionstree.tag_bind("Sect", callback=self.sect_click_sect)

	def LoadSection(self, ParentID, sectionID):
		base.debugmsg(9, "ParentID:", ParentID, "	sectionID:", sectionID)
		sect_name = "{}".format(base.whitespace_get_ini_value(base.report[sectionID]["Name"]))
		base.debugmsg(9, "sect_name:", sect_name)
		items = list(self.sectionstree.get_children(ParentID))
		base.debugmsg(9, "items:", items)
		if sectionID not in items:
			self.sectionstree.insert(ParentID, "end", sectionID, text=sect_name, tags="Sect")
		if "Order" in base.report[sectionID]:
			self.LoadSections(sectionID)
		# self.sectionstree.see(sectionID)

	def on_closing(self, _event=None, *extras):
		base.running = False
		try:
			base.debugmsg(5, "close window")
			self.destroy()
		except Exception:
			# were closing the application anyway, ignore any error
			pass
		base.debugmsg(5, "core.on_closing")
		core.on_closing()

	def sect_click_top(self, *args):
		selected = self.sectionstree.focus()
		base.debugmsg(5, "selected:", selected)

	def sect_click_sect(self, *args):
		base.debugmsg(5, "args:", args, args[0].x, args[0].y)
		# base.debugmsg(5, "clicked:", clicked)
		clicked = self.sectionstree.identify_row(args[0].y)
		base.debugmsg(5, "clicked:", clicked, type(clicked), id(clicked))
		if len(clicked) < 1:
			# unselect
			clicked = "TOP"
			self.sectionstree.selection_set('')
			self.sectionstree.focus('')
			return

		# load section pane

		self.content_load(clicked)

	def BuildContent(self):

		# this removes a lot of wasted space and gives it back to the data in each tab
		# 	I think the system default is ~20 on macos 11
		self.tabs = ttk.Notebook(self.content, padding=0)

		# first page, which would get widgets gridded into it
		icontext = "Preview"
		base.debugmsg(8, icontext)

		self.contentframe = tk.Frame(self.tabs, padx=0, pady=0, bd=0)
		# self.contentframe.config(bg="salmon")
		self.contentframe.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)

		self.contentcanvas = tk.Canvas(self.contentframe)
		self.contentcanvas.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)
		self.contentframe.columnconfigure(0, weight=1)
		self.contentframe.rowconfigure(0, weight=1)
		self.contentcanvas.columnconfigure(0, weight=1)
		self.contentcanvas.rowconfigure(0, weight=1)

		self.contentpreview = tk.Frame(self.contentcanvas, padx=0, pady=0)
		# self.contentpreview.config(bg="cyan")
		self.contentpreview.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)
		self.contentpreview.columnconfigure(0, weight=1)
		self.contentpreview.rowconfigure(0, weight=1)

		self.contentcanvas.create_window((0, 0), window=self.contentpreview, anchor='nw')

		# Vertical Scroolbar
		self.content.vsb = ttk.Scrollbar(self.contentframe, orient="vertical", command=self.contentcanvas.yview)
		self.contentcanvas.configure(yscrollcommand=self.content.vsb.set)
		self.content.vsb.grid(column=1, row=0, sticky="ns")

		# Horizontal Scroolbar
		hsb = ttk.Scrollbar(self.contentframe, orient="horizontal", command=self.contentcanvas.xview)
		self.contentcanvas.configure(xscrollcommand=hsb.set)
		hsb.grid(column=0, row=1, sticky="ew")

		self.tabs.add(self.contentframe, image=self.imgdata[icontext], text=icontext, compound=tk.LEFT, padding=0, sticky="nsew")

		base.debugmsg(9, "self.tabs:", self.tabs)
		base.debugmsg(9, "self.tabs.tab(0):", self.tabs.tab(0))
		base.debugmsg(9, "self.contentpreview:", self.contentpreview)

		# second page
		icontext = "Settings"
		base.debugmsg(6, icontext)
		self.contentsettings = tk.Frame(self.tabs, padx=0, pady=0, bd=0)
		# self.contentsettings.config(bg="linen")
		self.contentsettings.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)
		self.contentsettings.columnconfigure(0, weight=1)
		self.contentsettings.rowconfigure(0, weight=1)
		self.tabs.add(self.contentsettings, image=self.imgdata[icontext], text=icontext, compound=tk.LEFT, padding=0, sticky="nsew")

		self.tabs.grid(column=0, row=0, sticky="nsew")
		self.tabs.select(1)
		# self.c_preview
		self.content_load("TOP")

	def content_load(self, id):
		base.debugmsg(8, "id:", id)
		# self.content_settings(id)
		cs = threading.Thread(target=lambda: self.content_settings(id))
		cs.start()

		# self.content_preview(id)
		cp = threading.Thread(target=lambda: self.content_preview(id))
		cp.start()

	def dispaly_donation_reminder(self):
		if 'donation_reminder' not in base.config['GUI']:
			base.config['GUI']['donation_reminder'] = "0"
			base.saveini()

		lastreminder = int(base.config['GUI']['donation_reminder'])
		timenow = int(datetime.now().timestamp())
		timesincereminder = timenow - lastreminder
		yearseconds = 60 * 60 * 24 * 365

		# display donation reminder on first launch and then once per year
		if timesincereminder > yearseconds:

			titlemsg = self.titleprefix + " - Donation Reminder"

			donatemsg = "RFSwarm's mission is to give you a an industry leading performance test tool, that is easy to use, "
			donatemsg += "quick to develop test scripts and free from limitations so that you can just get on with testing."
			donatemsg += "\n\n"
			donatemsg += "Accomplishing this mission costs us resources, and requires the time of many talented people to fix "
			donatemsg += "bugs and develop new features and generally improve RFSwarm."
			donatemsg += "\n\n"
			donatemsg += "RFSwarm is proud to be a completely open source application that is 100% community funded and "
			donatemsg += "does not harvest and sell your data in any way."
			donatemsg += "\n\n"
			donatemsg += "So today we're asking for you help to make RFSwarm better, please consider giving a donation "
			donatemsg += "to support RFSwarm."

			self.drWindow = tk.Toplevel(self.root)
			self.drWindow.wm_iconphoto(False, self.icon)
			self.drWindow.columnconfigure(0, weight=1)
			self.drWindow.columnconfigure(2, weight=1)
			self.drWindow.title(titlemsg)
			self.drWindow.attributes('-topmost', 'true')

			row = 0
			self.drWindow.rowconfigure(row, weight=1)

			self.drWindow.lblDR00 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR00.grid(column=0, row=row, sticky="nsew")

			self.drWindow.lblDR01 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR01.grid(column=1, row=row, sticky="nsew")

			self.drWindow.lblDR02 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR02.grid(column=2, row=row, sticky="nsew")

			row += 1
			self.drWindow.lblDR11 = ttk.Label(self.drWindow, text=donatemsg, wraplength=600)
			self.drWindow.lblDR11.grid(column=1, row=row, sticky="nsew")

			row += 1
			self.drWindow.rowconfigure(row, weight=1)
			self.drWindow.lblDR21 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR21.grid(column=1, row=row, sticky="nsew")

			row += 1

			self.drWindow.fmeBBar = tk.Frame(self.drWindow)
			self.drWindow.fmeBBar.grid(column=0, row=row, columnspan=5, sticky="nsew")

			self.drWindow.fmeBBar.columnconfigure(0, weight=1)

			self.drWindow.bind('<Return>', self.close_donation_reminder)
			self.drWindow.bind('<Key-Escape>', self.drWindow.destroy)

			bdonate = ttk.Button(self.drWindow.fmeBBar, text="Donate", padding='3 3 3 3', command=self.close_donation_reminder)
			bdonate.grid(column=9, row=0, sticky="nsew")

			blater = ttk.Button(self.drWindow.fmeBBar, text="Maybe Later", padding='3 3 3 3', command=self.drWindow.destroy)
			blater.grid(column=8, row=0, sticky="nsew")

			base.config['GUI']['donation_reminder'] = str(int(datetime.now().timestamp()))
			base.saveini()

	def close_donation_reminder(self, *args):
		base.debugmsg(5, "args:", args)
		self.drWindow.destroy()

		url = "https://github.com/sponsors/damies13"
		webbrowser.open(url, new=0, autoraise=True)

	#
	# Settings
	#

	def content_settings(self, id):
		base.debugmsg(9, "id:", id)
		# self.content
		if id not in self.contentdata:
			self.contentdata[id] = {}
		if id + 'L' not in self.contentdata:
			self.contentdata[id + 'L'] = {}
		if id + 'R' not in self.contentdata:
			self.contentdata[id + 'R'] = {}
		if "Settings" not in self.contentdata[id]:
			self.contentdata[id]["Settings"] = tk.Frame(self.contentsettings, padx=0, pady=0, bd=0)
			# self.contentdata[id]["Settings"].config(bg="rosy brown")
			if id == "TOP":
				self.cs_reportsettings()
			else:
				rownum = 0
				# Input field headding / name
				self.contentdata[id]["lblHeading"] = ttk.Label(self.contentdata[id]["Settings"], text="Heading:")
				self.contentdata[id]["lblHeading"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["Heading"] = tk.StringVar()
				self.contentdata[id]["Heading"].set(base.report_item_get_name(id))
				self.contentdata[id]["eHeading"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["Heading"])
				self.contentdata[id]["eHeading"].grid(column=1, row=rownum, sticky="nsew")
				# https://pysimplegui.readthedocs.io/en/latest/
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["eHeading"].bind('<Leave>', self.cs_rename_heading)
				self.contentdata[id]["eHeading"].bind('<FocusOut>', self.cs_rename_heading)

				rownum += 1
				# option list - heading / text / graph / table
				self.contentdata[id]["lblType"] = ttk.Label(self.contentdata[id]["Settings"], text="Type:")
				self.contentdata[id]["lblType"].grid(column=0, row=rownum, sticky="nsew")

				ContentTypes = [None] + list(base.settings["ContentTypes"].values())
				self.contentdata[id]["Type"] = tk.StringVar()
				self.contentdata[id]["Type"].set(base.report_item_get_type_lbl(id))
				self.contentdata[id]["omType"] = ttk.OptionMenu(
					self.contentdata[id]["Settings"],
					self.contentdata[id]["Type"],
					command=self.cs_change_type,
					*ContentTypes
				)
				self.contentdata[id]["omType"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# Left and right frames
				# Left frame
				self.contentdata[id]["LFrame"] = tk.Frame(self.contentdata[id]["Settings"], padx=0, pady=0, bd=0)
				self.contentdata[id]["LFrame"].grid(column=0, row=rownum, columnspan=10, sticky="nsew")

				# Left frame padding
				self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Settings"], text="")
				self.contentdata[id]["lblSpacer"].grid(column=9, row=rownum - 1, sticky="nsew")
				self.contentdata[id]["Settings"].columnconfigure(9, weight=1)

				# Right frame
				self.contentdata[id]["RFrame"] = tk.Frame(self.contentdata[id]["Settings"], padx=0, pady=0, bd=0)
				self.contentdata[id]["RFrame"].grid(column=10, row=rownum, columnspan=10, sticky="nsew")

				# Right frame padding
				self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Settings"], text="")
				self.contentdata[id]["lblSpacer"].grid(column=19, row=rownum - 1, sticky="nsew")
				self.contentdata[id]["Settings"].columnconfigure(19, weight=1)

				self.contentdata[id]["Settings"].rowconfigure(rownum, weight=1)

				# call function to load settings for option selected (heading doesn't need)
				type = base.report_item_get_type(id)
				base.debugmsg(5, "type:", type)
				if type == 'contents':
					self.cs_contents(id)
				if type == 'note':
					self.cs_note(id)
				if type == 'table':
					self.cs_datatable(id)
				if type == 'graph':
					self.cs_graph(id)
				if type == 'errors':
					self.cs_errors(id)

		curritem = self.contentsettings.grid_slaves(column=0, row=0)
		base.debugmsg(5, "curritem:", curritem)
		if len(curritem) > 0:
			curritem[0].grid_forget()
		base.debugmsg(5, "newitem:", self.contentdata[id]["Settings"])
		self.contentdata[id]["Settings"].grid(column=0, row=0, sticky="nsew")

	def cs_reportsettings(self):
		rownum = 0
		id = "TOP"

		if "Settings" in self.contentdata[id]:
			self.contentdata[id]["Settings"].grid_forget()
			del self.contentdata[id]["Settings"]
			self.contentdata[id]["Settings"] = tk.Frame(self.contentsettings, padx=0, pady=0, bd=0)
			self.contentdata[id]["Settings"].grid(column=0, row=0, sticky="nsew")

		self.contentdata[id]["lblRS"] = ttk.Label(self.contentdata[id]["Settings"], text="Report Settings:")
		self.contentdata[id]["lblRS"].grid(column=0, row=rownum, sticky="nsew")

		# Report Title
		rownum += 1
		self.contentdata[id]["lblTitle"] = ttk.Label(self.contentdata[id]["Settings"], text="Title:")
		self.contentdata[id]["lblTitle"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strTitle"] = tk.StringVar()
		self.contentdata[id]["strTitle"].set(base.rs_setting_get_title())
		self.contentdata[id]["eTitle"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strTitle"])
		self.contentdata[id]["eTitle"].grid(column=1, columnspan=9, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eTitle"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["eTitle"].bind('<FocusOut>', self.cs_report_settings_update)

		# chkbox display start and end time of test
		rownum += 1
		self.contentdata[id]["lblDF"] = ttk.Label(self.contentdata[id]["Settings"], text="Date Format")
		self.contentdata[id]["lblDF"].grid(column=0, row=rownum, sticky="nsew")

		DFormats = [None, "yyyy-mm-dd", "dd/mm/yyyy", "dd-mm-yyyy", "dd.mm.yyyy", "mm/dd/yyyy"]
		self.contentdata[id]["strDF"] = tk.StringVar()
		self.contentdata[id]["strDF"].set(base.rs_setting_get_dateformat())
		self.contentdata[id]["omDF"] = ttk.OptionMenu(self.contentdata[id]["Settings"], self.contentdata[id]["strDF"], command=self.cs_report_settings_update, *DFormats)
		self.contentdata[id]["omDF"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblTF"] = ttk.Label(self.contentdata[id]["Settings"], text="Time Format")
		self.contentdata[id]["lblTF"].grid(column=0, row=rownum, sticky="nsew")

		TFormats = [None, "HH:MM", "HH:MM:SS", "HH.MM", "HH.MM.SS", "h:MM AMPM", "h:MM:SS AMPM", "h.MM AMPM", "h.MM.SS AMPM"]
		self.contentdata[id]["strTF"] = tk.StringVar()
		self.contentdata[id]["strTF"].set(base.rs_setting_get_timeformat())
		self.contentdata[id]["omTF"] = ttk.OptionMenu(self.contentdata[id]["Settings"], self.contentdata[id]["strTF"], command=self.cs_report_settings_update, *TFormats)
		self.contentdata[id]["omTF"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblTZ"] = ttk.Label(self.contentdata[id]["Settings"], text="Time Zone")
		self.contentdata[id]["lblTZ"].grid(column=0, row=rownum, sticky="nsew")

		TZones = [""]
		ZL = list(base.rs_setting_get_timezone_list())
		LTZ = base.rs_setting_get_timezone()
		if LTZ not in ZL:
			TZones.append(LTZ)
		TZones = TZones + ZL
		TZones.sort()
		self.contentdata[id]["strTZ"] = tk.StringVar()
		self.contentdata[id]["strTZ"].set(LTZ)
		self.contentdata[id]["omTZ"] = ttk.Combobox(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strTZ"])
		self.contentdata[id]["omTZ"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["omTZ"]['values'] = TZones
		self.contentdata[id]["omTZ"].bind('<<ComboboxSelected>>', self.cs_report_settings_update)

		rownum += 1
		col_disp = 3
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["Settings"], text="Display")
		self.contentdata[id]["lblST"].grid(column=col_disp, row=rownum, sticky="nsew")

		# 		start time
		rownum += 1
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["Settings"], text="Start Time:")
		self.contentdata[id]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strST"] = tk.StringVar()
		iST = base.rs_setting_get_starttime()
		fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
		self.contentdata[id]["strST"].set(fST)

		self.contentdata[id]["eST"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strST"])
		self.contentdata[id]["eST"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eST"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["eST"].bind('<FocusOut>', self.cs_report_settings_update)

		self.contentdata[id]["intST"] = tk.IntVar()
		self.contentdata[id]["intST"].set(base.rs_setting_get_int("showstarttime"))
		self.contentdata[id]["chkST"] = ttk.Checkbutton(self.contentdata[id]["Settings"], variable=self.contentdata[id]["intST"], command=self.cs_report_settings_update)
		self.contentdata[id]["chkST"].grid(column=col_disp, row=rownum, sticky="nsew")

		# 		end time
		rownum += 1
		self.contentdata[id]["lblET"] = ttk.Label(self.contentdata[id]["Settings"], text="End Time:")
		self.contentdata[id]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strET"] = tk.StringVar()
		iET = base.rs_setting_get_endtime()
		fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
		self.contentdata[id]["strET"].set(fET)

		self.contentdata[id]["eET"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strET"])
		self.contentdata[id]["eET"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eET"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["eET"].bind('<FocusOut>', self.cs_report_settings_update)

		self.contentdata[id]["intET"] = tk.IntVar()
		self.contentdata[id]["intET"].set(base.rs_setting_get_int("showendtime"))
		self.contentdata[id]["chkET"] = ttk.Checkbutton(self.contentdata[id]["Settings"], variable=self.contentdata[id]["intET"], command=self.cs_report_settings_update)
		self.contentdata[id]["chkET"].grid(column=col_disp, row=rownum, sticky="nsew")

		# Logo image
		# picture.gif
		rownum += 1
		self.contentdata[id]["lblLI"] = ttk.Label(self.contentdata[id]["Settings"], text="Logo Image:")
		self.contentdata[id]["lblLI"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strLIPath"] = base.rs_setting_get_file("tlogo")
		base.debugmsg(5, "tlogo:", self.contentdata[id]["strLIPath"])

		self.contentdata[id]["strLIName"] = tk.StringVar()
		self.contentdata[id]["eLIName"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strLIName"], state="readonly", justify="right", style='TEntry')
		self.contentdata[id]["eLIName"].grid(column=1, row=rownum, sticky="nsew")

		icontext = "Select Image"
		# "Select Image"	picture.gif
		self.contentdata[id]["btnLIName"] = ttk.Button(self.contentdata[id]["Settings"], image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, width=1)
		self.contentdata[id]["btnLIName"].config(command=self.cs_select_logoimage)
		self.contentdata[id]["btnLIName"].grid(column=2, row=rownum, sticky="nsew")

		# flogo = base.rs_setting_get_file("tlogo")
		# if flogo is not None:
		if len(self.contentdata[id]["strLIPath"]) > 0:
			base.debugmsg(5, "strLIPath:", self.contentdata[id]["strLIPath"])
			path, filename = os.path.split(self.contentdata[id]["strLIPath"])
			base.debugmsg(5, "filename:", filename, type(filename))
			self.contentdata[id]["strLIName"].set(filename)

		self.contentdata[id]["intLI"] = tk.IntVar()
		self.contentdata[id]["intLI"].set(base.rs_setting_get_int("showtlogo"))
		self.contentdata[id]["chkLI"] = ttk.Checkbutton(self.contentdata[id]["Settings"], variable=self.contentdata[id]["intLI"], command=self.cs_report_settings_update)
		self.contentdata[id]["chkLI"].grid(column=col_disp, row=rownum, sticky="nsew")

		# wattermark image
		# rownum += 1
		# self.contentdata[id]["lblWM"] = ttk.Label(self.contentdata[id]["Settings"], text="Watermark Image:")
		# self.contentdata[id]["lblWM"].grid(column=0, row=rownum, sticky="nsew")

		# report font
		rownum += 1
		self.contentdata[id]["lblFont"] = ttk.Label(self.contentdata[id]["Settings"], text="Font:")
		self.contentdata[id]["lblFont"].grid(column=0, row=rownum, sticky="nsew")

		base.debugmsg(9, "tkFont.families()", tkFont.families())
		fontlst = list(tkFont.families())

		Fonts = [""] + fontlst
		Fonts.sort()
		self.contentdata[id]["strFont"] = tk.StringVar()
		self.contentdata[id]["omFont"] = ttk.Combobox(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strFont"])
		self.contentdata[id]["strFont"].set(base.rs_setting_get_font())
		self.contentdata[id]["omFont"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["omFont"]['values'] = Fonts
		self.contentdata[id]["omFont"].bind('<<ComboboxSelected>>', self.cs_report_settings_update)

		Fontsize = [None]
		fs = 6
		while fs < 70:
			Fontsize.append(fs)
			if fs > 1:
				fs += 1
			if fs > 10:
				fs += 1
			if fs > 50:
				fs += 2
		self.contentdata[id]["intFontSz"] = tk.IntVar()
		self.contentdata[id]["omFontSz"] = ttk.OptionMenu(self.contentdata[id]["Settings"], self.contentdata[id]["intFontSz"], command=self.cs_report_settings_update, *Fontsize)
		self.contentdata[id]["intFontSz"].set(base.rs_setting_get_fontsize())
		self.contentdata[id]["omFontSz"].grid(column=2, row=rownum, sticky="nsew")

		# highlight colour
		# color_swatch.gif
		# https://www.pythontutorial.net/tkinter/tkinter-color-chooser/
		rownum += 1
		self.contentdata[id]["lblHColour"] = ttk.Label(self.contentdata[id]["Settings"], text="Highlight Colour:")
		self.contentdata[id]["lblHColour"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblHColourPrev"] = tk.Label(self.contentdata[id]["Settings"], text=" ", bg=self.style_head_colour)
		self.contentdata[id]["lblHColourPrev"].grid(column=1, row=rownum, sticky="nsew")

		icontext = "Select Colour"
		# "Select Colour"	color_swatch.gif
		self.contentdata[id]["btnHColour"] = ttk.Button(self.contentdata[id]["Settings"], image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, width=1)
		self.contentdata[id]["btnHColour"].config(command=self.cs_select_hcolour)
		self.contentdata[id]["btnHColour"].grid(column=2, row=rownum, sticky="nsew")

		# report %ile

		rownum += 1
		self.contentdata[id]["lblPctile"] = ttk.Label(self.contentdata[id]["Settings"], text="Percentile:")
		self.contentdata[id]["lblPctile"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intPctile"] = tk.IntVar()
		self.contentdata[id]["intPctile"].set(base.rs_setting_get_pctile())
		self.contentdata[id]["ePctile"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["intPctile"])
		self.contentdata[id]["ePctile"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["ePctile"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["ePctile"].bind('<FocusOut>', self.cs_report_settings_update)

		self.contentdata[id]["lblPctile"] = ttk.Label(self.contentdata[id]["Settings"], text="%")
		self.contentdata[id]["lblPctile"].grid(column=2, row=rownum, sticky="nsew")

	def cs_report_settings_update(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		# id = self.sectionstree.focus()
		# base.debugmsg(9, "id:", id)
		changes = 0
		id = "TOP"

		if "strTitle" in self.contentdata[id]:
			changes += base.rs_setting_set("title", self.contentdata[id]["strTitle"].get())

		# base.rs_setting_set_file("tlogo", fpath)
		if "strLIPath" in self.contentdata[id]:
			changes += base.rs_setting_set_file("tlogo", self.contentdata[id]["strLIPath"])

		# showlogo
		if "intLI" in self.contentdata[id]:
			changes += base.rs_setting_set_int("showtlogo", self.contentdata[id]["intLI"].get())

		if "strDF" in self.contentdata[id]:
			changes += base.rs_setting_set("dateformat", self.contentdata[id]["strDF"].get())

		if "strTF" in self.contentdata[id]:
			changes += base.rs_setting_set("timeformat", self.contentdata[id]["strTF"].get())

		if "strTZ" in self.contentdata[id]:
			changed = base.rs_setting_set("timezone", self.contentdata[id]["strTZ"].get())
			changes += changed
			if changed:
				# update the start and end time fields for new timezone
				iST = base.rs_setting_get_starttime()
				fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
				self.contentdata[id]["strST"].set(fST)
				iET = base.rs_setting_get_endtime()
				fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
				self.contentdata[id]["strET"].set(fET)

				update_section_times = threading.Thread(target=self.cs_update_start_and_end_times(id, fST, fET))
				update_section_times.start()

		# strST
		if "strST" in self.contentdata[id]:
			st = self.contentdata[id]["strST"].get()
			base.debugmsg(8, "st:", st)
			ist = base.report_formateddatetimetosec(st)
			base.debugmsg(8, "ist:", ist)
			if ist > 0:
				ios = ist - base.report_starttime()
				changes += base.rs_setting_set_int("startoffset", ios)

		if "intST" in self.contentdata[id]:
			changes += base.rs_setting_set_int("showstarttime", self.contentdata[id]["intST"].get())

		# strET
		if "strET" in self.contentdata[id]:
			et = self.contentdata[id]["strET"].get()
			base.debugmsg(8, "et:", et)
			iet = base.report_formateddatetimetosec(et)
			base.debugmsg(8, "iet:", iet)
			if iet > 0:
				ios = base.report_endtime() - iet
				changes += base.rs_setting_set_int("endoffset", ios)

		if "intET" in self.contentdata[id]:
			changes += base.rs_setting_set_int("showendtime", self.contentdata[id]["intET"].get())

		if "strFont" in self.contentdata[id]:
			changes += base.rs_setting_set("font", self.contentdata[id]["strFont"].get())

		if "intFontSz" in self.contentdata[id]:
			fsz = self.contentdata[id]["intFontSz"].get()
			base.debugmsg(5, "fsz:", fsz, "	", type(fsz))
			changes += base.rs_setting_set_int("fontsize", fsz)

		if "intPctile" in self.contentdata[id]:
			pct = int(self.contentdata[id]["intPctile"].get())
			if pct > 0:
				base.debugmsg(5, "pct:", pct, "	", type(pct))
				changes += base.rs_setting_set_int("percentile", pct)

		if changes > 0:
			self.cs_reportsettings()

			self.ConfigureStyle()
			regen = threading.Thread(target=self.cp_regenerate_preview)
			regen.start()

	def cs_select_logoimage(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		id = "TOP"

		opendir = base.config['Reporter']['ResultDir']
		if len(self.contentdata[id]["strLIPath"]) > 0:
			opendir, filename = os.path.split(self.contentdata[id]["strLIPath"])

		imagefile = str(
			tkf.askopenfilename(
				initialdir=opendir,
				title="Select Logo Image",
				filetypes=(
					("JPEG", "*.jpg"),
					("JPEG", "*.jpeg"),
					("PNG", "*.png"),
					("GIF", "*.gif"),
					("Bitmap", "*.bmp"),
					("all files", "*.*")
				)
			)
		)
		base.debugmsg(5, "imagefile:", imagefile)

		if imagefile is not None and len(imagefile) > 0:
			self.contentdata[id]["strLIPath"] = imagefile
			base.debugmsg(5, "strLIPath:", self.contentdata[id]["strLIPath"])
			base.rs_setting_set_file("tlogo", self.contentdata[id]["strLIPath"])
			path, filename = os.path.split(self.contentdata[id]["strLIPath"])
			base.debugmsg(5, "filename:", filename, type(filename))
			self.contentdata[id]["strLIName"].set(filename)

			regen = threading.Thread(target=self.cp_regenerate_preview)
			regen.start()

	def cs_select_watermarkimage(self, _event=None):
		base.debugmsg(5, "_event:", _event)

	def cs_select_hfimage(self, _event=None):
		base.debugmsg(5, "_event:", _event)

	def cs_select_hcolour(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		# https://www.pythontutorial.net/tkinter/tkinter-color-chooser/
		newcolour = tkac.askcolor(self.style_head_colour, title="Tkinter Color Chooser")
		base.debugmsg(5, "newcolour:", newcolour)
		newcolourhx = newcolour[-1]
		base.debugmsg(5, "newcolourhx:", newcolourhx)
		if newcolourhx is not None:
			self.style_head_colour = newcolourhx
			base.rs_setting_set("hcolour", newcolourhx)

			# refresh
			self.cs_reportsettings()

			self.ConfigureStyle()
			# self.cp_regenerate_preview()
			regen = threading.Thread(target=self.cp_regenerate_preview)
			regen.start()

	def cs_rename_heading(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		base.debugmsg(9, "id:", id)
		curhead = base.report_item_get_name(id)
		newhead = curhead
		if id in self.contentdata:
			if "Heading" in self.contentdata[id]:
				newhead = self.contentdata[id]["Heading"].get()
		base.debugmsg(5, "curhead:", curhead, "	newhead:", newhead)
		if newhead != curhead:
			base.debugmsg(5, "rename :", curhead, "	to:", newhead)
			base.report_item_set_name(id, newhead)
			parent = base.report_item_parent(id)
			self.LoadSections(parent)
			self.sectionstree.selection_set(id)
			self.sectionstree.focus(id)
			self.content_preview(id)

	def cs_change_type(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		base.debugmsg(9, "id:", id)

		# I might need to remove this ? self.contentdata[id]["Settings"]
		# https://www.w3schools.com/python/gloss_python_remove_dictionary_items.asp
		del self.contentdata[id]["Settings"]

		keys = list(base.settings["ContentTypes"].keys())
		vals = list(base.settings["ContentTypes"].values())
		idx = 0
		if _event in vals:
			idx = vals.index(_event)

		type = keys[idx]
		base.report_item_set_type(id, type)
		self.content_load(id)

	#
	# Settings	-	Contents
	#

	def cs_contents(self, id):
		base.debugmsg(5, "id:", id)
		rownum = 0

		rownum += 1
		self.contentdata[id]["lblCM"] = ttk.Label(self.contentdata[id]["LFrame"], text="Mode:")
		self.contentdata[id]["lblCM"].grid(column=0, row=rownum, sticky="nsew")

		ContentsModes = [None, "Table Of Contents", "Table of Graphs", "Table Of Tables"]
		self.contentdata[id]["strCM"] = tk.StringVar()
		self.contentdata[id]["omCM"] = ttk.OptionMenu(self.contentdata[id]["LFrame"], self.contentdata[id]["strCM"], command=self.cs_contents_update, *ContentsModes)

		self.contentdata[id]["strCM"].set(base.rt_contents_get_mode(id))
		self.contentdata[id]["omCM"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblCL"] = ttk.Label(self.contentdata[id]["LFrame"], text="Level:")
		self.contentdata[id]["lblCL"].grid(column=0, row=rownum, sticky="nsew")

		Levels = [None]
		for i in range(6):
			Levels.append(i + 1)
		self.contentdata[id]["intCL"] = tk.IntVar()
		self.contentdata[id]["omCL"] = ttk.OptionMenu(self.contentdata[id]["LFrame"], self.contentdata[id]["intCL"], command=self.cs_contents_update, *Levels)
		self.contentdata[id]["intCL"].set(base.rt_contents_get_level(id))
		self.contentdata[id]["omCL"].grid(column=1, row=rownum, sticky="nsew")

	def cs_contents_update(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		base.debugmsg(9, "id:", id)
		changes = 0

		if "strCM" in self.contentdata[id]:
			value = self.contentdata[id]["strCM"].get()
			changes += base.rt_contents_set_mode(id, value)

		if "intCL" in self.contentdata[id]:
			value = self.contentdata[id]["intCL"].get()
			changes += base.rt_contents_set_level(id, value)

		if changes > 0:
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

	#
	# Settings	-	Note
	#

	def cs_note(self, id):
		base.debugmsg(9, "id:", id)
		# base.rt_note_get(id)
		self.contentdata[id]["tNote"] = tk.Text(self.contentdata[id]["LFrame"])
		# background="yellow", foreground="blue"
		# self.contentdata[id]["tNote"].config(bg="SlateBlue2")
		self.contentdata[id]["tNote"].config(background=self.style_feild_colour, foreground=self.style_text_colour, insertbackground=self.style_text_colour)

		self.contentdata[id]["tNote"].insert('0.0', base.rt_note_get(id))
		self.contentdata[id]["tNote"].grid(column=0, row=0, sticky="nsew")
		self.contentdata[id]["LFrame"].rowconfigure(0, weight=1)
		self.contentdata[id]["LFrame"].columnconfigure(0, weight=1)
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["tNote"].bind('<Leave>', self.cs_note_update)
		self.contentdata[id]["tNote"].bind('<FocusOut>', self.cs_note_update)

	def cs_note_update(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		base.debugmsg(9, "id:", id)
		if "tNote" in self.contentdata[id]:
			data = self.contentdata[id]["tNote"].get('0.0', tk.END)
			base.debugmsg(5, "data:", data)
			base.rt_note_set(id, data)
			# self.content_preview(id)
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

	#
	# Settings	-	DataTable
	#

	def cs_datatable(self, id):
		base.debugmsg(8, "id:", id)
		colours = base.rt_table_get_colours(id)
		datatype = base.rt_table_get_dt(id)
		self.contentdata[id]["LFrame"].columnconfigure(99, weight=1)
		rownum = 0

		rownum += 1
		self.contentdata[id]["lblColours"] = ttk.Label(self.contentdata[id]["LFrame"], text="Show graph colours:")
		self.contentdata[id]["lblColours"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intColours"] = tk.IntVar()
		self.contentdata[id]["chkColours"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intColours"], command=self.cs_datatable_update)
		self.contentdata[id]["intColours"].set(colours)
		self.contentdata[id]["chkColours"].grid(column=1, row=rownum, sticky="nsew")

		# 		start time
		rownum += 1
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["LFrame"], text="Start Time:")
		self.contentdata[id]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strST"] = tk.StringVar()
		iST = base.rt_setting_get_starttime(id)
		fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
		self.contentdata[id]["strST"].set(fST)
		self.contentdata[id]["fST"] = fST

		self.contentdata[id]["eST"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strST"])
		self.contentdata[id]["eST"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eST"].bind('<Leave>', self.cs_datatable_update)
		self.contentdata[id]["eST"].bind('<FocusOut>', self.cs_datatable_update)

		# 		end time
		rownum += 1
		self.contentdata[id]["lblET"] = ttk.Label(self.contentdata[id]["LFrame"], text="End Time:")
		self.contentdata[id]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strET"] = tk.StringVar()
		iET = base.rt_setting_get_endtime(id)
		fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
		self.contentdata[id]["strET"].set(fET)
		self.contentdata[id]["fET"] = fET

		self.contentdata[id]["eET"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strET"])
		self.contentdata[id]["eET"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eET"].bind('<Leave>', self.cs_datatable_update)
		self.contentdata[id]["eET"].bind('<FocusOut>', self.cs_datatable_update)

		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[id]["LFrame"], text="Data Type:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		DataTypes = [None, "Metric", "Result", "ResultSummary", "Plan", "SQL"]
		self.contentdata[id]["strDT"] = tk.StringVar()
		self.contentdata[id]["omDT"] = ttk.OptionMenu(self.contentdata[id]["LFrame"], self.contentdata[id]["strDT"], command=self.cs_datatable_switchdt, *DataTypes)
		self.contentdata[id]["strDT"].set(datatype)
		self.contentdata[id]["omDT"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["DTFrame"] = rownum
		self.cs_datatable_switchdt(id)

	def cs_datatable_update(self, _event=None, *args):
		base.debugmsg(5, "_event:", _event, "	args:", args)
		changes = 0
		# if len(args) > 0:
		# 	base.debugmsg(8, "args[0]:", args[0])
		# 	changes += args[0]
		id = self.sectionstree.focus()
		if _event is not None:
			name = base.report_item_get_name(_event)
			if name is not None:
				id = _event
		base.debugmsg(9, "id:", id)
		if "intColours" in self.contentdata[id]:
			colours = self.contentdata[id]["intColours"].get()
			changes += base.rt_table_set_colours(id, colours)

		# 		start time
		if "strST" in self.contentdata[id]:
			pass
			st = self.contentdata[id]["strST"].get()
			base.debugmsg(5, "st:", st)
			if st != self.contentdata[id]["fST"]:
				ist = base.report_formateddatetimetosec(st)
				base.debugmsg(5, "ist:", ist)
				if ist > 0:
					ios = ist - base.rs_setting_get_starttime()
					base.debugmsg(5, "ios:", ios)
					changes += base.report_item_set_int(id, "startoffset", ios)

			iST = base.rt_setting_get_starttime(id)
			fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
			self.contentdata[id]["strST"].set(fST)
			self.contentdata[id]["fST"] = fST

		# 		end time
		if "strET" in self.contentdata[id]:
			pass
			et = self.contentdata[id]["strET"].get()
			base.debugmsg(5, "et:", et)
			if et != self.contentdata[id]["fET"]:
				iet = base.report_formateddatetimetosec(et)
				base.debugmsg(5, "iet:", iet)
				if iet > 0:
					ios = base.rs_setting_get_endtime() - iet
					base.debugmsg(5, "ios:", ios)
					changes += base.report_item_set_int(id, "endoffset", ios)

			iET = base.rt_setting_get_endtime(id)
			fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
			self.contentdata[id]["strET"].set(fET)
			self.contentdata[id]["fET"] = fET

		base.debugmsg(5, "changes:", changes)
		if "intIsNum" in self.contentdata[id]:
			value = self.contentdata[id]["intIsNum"].get()
			changes += base.rt_table_set_isnumeric(id, value)
		if "intShCnt" in self.contentdata[id]:
			value = self.contentdata[id]["intShCnt"].get()
			changes += base.rt_table_set_showcount(id, value)
		# self.contentdata[id]["MType"].set(base.rt_table_get_mt(id))
		if "MType" in self.contentdata[id]:
			value = self.contentdata[id]["MType"].get()
			changes += base.rt_table_set_mt(id, value)
		# self.contentdata[id]["PMetric"].set(base.rt_table_get_pm(id))
		if "PMetric" in self.contentdata[id]:
			value = self.contentdata[id]["PMetric"].get()
			changes += base.rt_table_set_pm(id, value)
		# self.contentdata[id]["SMetric"].set(base.rt_table_get_sm(id))
		if "SMetric" in self.contentdata[id]:
			value = self.contentdata[id]["SMetric"].get()
			changes += base.rt_table_set_sm(id, value)

		base.debugmsg(5, "changes:", changes)
		# self.contentdata[id]["RType"].set(base.rt_table_get_rt(id))
		if "RType" in self.contentdata[id]:
			value = self.contentdata[id]["RType"].get()
			changes += base.rt_table_set_rt(id, value)
		# self.contentdata[id]["FRType"].set(base.rt_table_get_fr(id))
		if "FRType" in self.contentdata[id]:
			value = self.contentdata[id]["FRType"].get()
			changes += base.rt_table_set_fr(id, value)
		# self.contentdata[id]["intFR"] = tk.IntVar()
		if "intFR" in self.contentdata[id]:
			value = self.contentdata[id]["intFR"].get()
			changes += base.rt_table_set_enfr(id, value)

		if "intFA" in self.contentdata[id]:
			value = self.contentdata[id]["intFA"].get()
			changes += base.rt_table_set_enfa(id, value)
		# self.contentdata[id]["FAType"] = tk.StringVar()
		if "FAType" in self.contentdata[id]:
			value = self.contentdata[id]["FAType"].get()
			changes += base.rt_table_set_fa(id, value)

		base.debugmsg(5, "changes:", changes)
		# self.contentdata[id]["FNType"].set(base.rt_table_get_fn(id))
		if "FNType" in self.contentdata[id]:
			value = self.contentdata[id]["FNType"].get()
			changes += base.rt_table_set_fn(id, value)

		base.debugmsg(5, "changes:", changes)
		# self.contentdata[id]["FPattern"].set(base.rt_table_get_fp(id))
		if "FPattern" in self.contentdata[id]:
			value = self.contentdata[id]["FPattern"].get()
			changes += base.rt_table_set_fp(id, value)

		base.debugmsg(5, "changes:", changes)
		if "strDT" in self.contentdata[id]:
			datatype = self.contentdata[id]["strDT"].get()
			changes += base.rt_table_set_dt(id, datatype)

			base.debugmsg(8, "datatype:", datatype)

			if datatype == "Plan":
				self.cs_datatable_update_plan(id)

			if datatype == "Metric":
				self.cs_datatable_update_metrics(id)

			if datatype != "SQL":
				time.sleep(0.1)
				base.rt_table_generate_sql(id)

			# if changes > 0:
			# 	self.cs_datatable_switchdt(id)

		base.debugmsg(5, "changes:", changes)
		if "tSQL" in self.contentdata[id]:
			data = self.contentdata[id]["tSQL"].get('0.0', tk.END).strip()
			base.debugmsg(5, "data:", data)
			changes += base.rt_table_set_sql(id, data)
		else:
			time.sleep(0.1)
			base.rt_table_generate_sql(id)

		base.debugmsg(5, "changes:", changes)
		if "renamecolumns" in self.contentdata[id] and "colnames" in self.contentdata[id]["renamecolumns"]:
			for colname in self.contentdata[id]["renamecolumns"]["colnames"]:
				value = self.contentdata[id]["renamecolumns"][colname].get()
				changes += base.rt_table_set_colname(id, colname, value)

				value = self.contentdata[id]["renamecolumns"][f"{colname} Show"].get()
				changes += base.report_item_set_bool(id, base.rt_table_ini_colname(f"{colname} Show"), value)

				if f"{colname} Opt" in self.contentdata[id]["renamecolumns"]:
					value = self.contentdata[id]["renamecolumns"][f"{colname} Opt"].get()
					changes += base.report_item_set_value(id, base.rt_table_ini_colname(f"{colname} Opt"), value)

		base.debugmsg(5, "content_preview id:", id)
		# self.content_preview(id)
		base.debugmsg(5, "changes:", changes)
		if changes > 0:
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()
			self.cs_datatable_add_renamecols(id)

		# rt_table_get_alst

	def cs_datatable_update_result(self, id):
		base.debugmsg(5, "id:", id)
		tag = threading.Thread(target=lambda: self.cs_datatable_update_resultagents(id))
		tag.start()

	def cs_datatable_update_resultagents(self, id):
		base.debugmsg(5, "id:", id)
		self.contentdata[id]["FATypes"] = base.rt_table_get_alst(id)
		if "omFA" in self.contentdata[id]:
			try:
				self.contentdata[id]["omFA"].set_menu(*self.contentdata[id]["FATypes"])
			except Exception as e:
				base.debugmsg(5, "e:", e)

	def cs_datatable_update_metricagents(self, id):
		base.debugmsg(5, "id:", id)
		self.contentdata[id]["FATypes"] = base.rt_table_get_malst(id)
		if "omFA" in self.contentdata[id]:
			try:
				self.contentdata[id]["omFA"].set_menu(*self.contentdata[id]["FATypes"])
			except Exception as e:
				base.debugmsg(5, "e:", e)

	def cs_datatable_update_plan(self, id):
		pass

	def cs_datatable_update_metrics(self, id):
		base.debugmsg(5, "id:", id)
		tmt = threading.Thread(target=lambda: self.cs_datatable_update_metricstype(id))
		tmt.start()
		base.debugmsg(6, "tmt")
		tpm = threading.Thread(target=lambda: self.cs_datatable_update_pmetrics(id))
		tpm.start()
		base.debugmsg(6, "tpm")
		tsm = threading.Thread(target=lambda: self.cs_datatable_update_smetrics(id))
		tsm.start()
		base.debugmsg(6, "tsm")

		showmetricagents = 0
		if "DBTable" in base.settings and "Metrics" in base.settings["DBTable"] and "DataSource" in base.settings["DBTable"]["Metrics"]:
			showmetricagents = base.settings["DBTable"]["Metrics"]["DataSource"]
		if showmetricagents:
			tag = threading.Thread(target=lambda: self.cs_datatable_update_metricagents(id))
			tag.start()
			base.debugmsg(6, "tag")

	def cs_datatable_update_metricstype(self, id):
		base.debugmsg(5, "id:", id)
		self.contentdata[id]["Metrics"] = base.rt_table_get_mlst(id)
		if "omMT" in self.contentdata[id]:
			try:
				self.contentdata[id]["omMT"].set_menu(*self.contentdata[id]["Metrics"])
			except Exception as e:
				base.debugmsg(5, "e:", e)

	def cs_datatable_update_pmetrics(self, id):
		base.debugmsg(5, "id:", id)
		self.contentdata[id]["PMetrics"] = base.rt_table_get_pmlst(id)
		if "omPM" in self.contentdata[id]:
			try:
				self.contentdata[id]["omPM"].set_menu(*self.contentdata[id]["PMetrics"])
			except Exception as e:
				base.debugmsg(5, "e:", e)

	def cs_datatable_update_smetrics(self, id):
		base.debugmsg(5, "id:", id)
		self.contentdata[id]["SMetrics"] = base.rt_table_get_smlst(id)
		if "omSM" in self.contentdata[id]:
			try:
				self.contentdata[id]["omSM"].set_menu(*self.contentdata[id]["SMetrics"])
			except Exception as e:
				base.debugmsg(5, "e:", e)

	def cs_datatable_switchdt(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		rownum = 0
		id = self.sectionstree.focus()
		if _event is not None:
			name = base.report_item_get_name(_event)
			if name is not None:
				id = _event
		base.debugmsg(8, "id:", id)
		# self.cs_datatable_update(id, 1)
		self.cs_datatable_update(id)
		datatype = self.contentdata[id]["strDT"].get()
		base.debugmsg(5, "datatype:", datatype)
		if "Frames" not in self.contentdata[id]:
			self.contentdata[id]["Frames"] = {}

		# Forget
		for frame in self.contentdata[id]["Frames"].keys():
			self.contentdata[id]["Frames"][frame].grid_forget()
			# self.contentdata[id]["Frames"] = {}
			# del self.contentdata[id]["Frames"][frame]
		self.contentdata[id]["Frames"] = {}

		base.debugmsg(8, "id:", id, "Frames:", self.contentdata[id]["Frames"])

		base.debugmsg(8, "id:", id, "Construct")
		# Construct
		if datatype not in self.contentdata[id]["Frames"]:
			rownum = 0
			self.contentdata[id]["Frames"][datatype] = tk.Frame(self.contentdata[id]["LFrame"])
			# self.contentdata[id]["Frames"][datatype].config(bg="SlateBlue3")
			# self.contentdata[id]["Frames"][datatype].columnconfigure(0, weight=1)
			self.contentdata[id]["Frames"][datatype].columnconfigure(99, weight=1)

			base.debugmsg(8, "datatype:", datatype)

			if datatype == "Metric":

				showmetricagents = 0
				if "DBTable" in base.settings and "Metrics" in base.settings["DBTable"] and "DataSource" in base.settings["DBTable"]["Metrics"]:
					showmetricagents = base.settings["DBTable"]["Metrics"]["DataSource"]

				rownum += 1
				self.contentdata[id]["lblIsNum"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Number Value:")
				self.contentdata[id]["lblIsNum"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["intIsNum"] = tk.IntVar()
				self.contentdata[id]["chkIsNum"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intIsNum"], command=self.cs_datatable_update)
				self.contentdata[id]["chkIsNum"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["lblShCnt"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Show Counts:")
				self.contentdata[id]["lblShCnt"].grid(column=2, row=rownum, sticky="nsew")

				self.contentdata[id]["intShCnt"] = tk.IntVar()
				self.contentdata[id]["chkShCnt"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intShCnt"], command=self.cs_datatable_update)
				self.contentdata[id]["chkShCnt"].grid(column=3, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[id]["lblEnabled"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Enabled")
					self.contentdata[id]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblMT"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Metric Type:")
				self.contentdata[id]["lblMT"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["MTypes"] = [None, "", "Loading..."]
				self.contentdata[id]["MType"] = tk.StringVar()
				self.contentdata[id]["omMT"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["MType"], command=self.cs_datatable_update, *self.contentdata[id]["MTypes"])
				self.contentdata[id]["omMT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblPM"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Primrary Metric:")
				self.contentdata[id]["lblPM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["PMetrics"] = [None, "", "Loading..."]
				self.contentdata[id]["PMetric"] = tk.StringVar()
				self.contentdata[id]["omPM"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["PMetric"], command=self.cs_datatable_update, *self.contentdata[id]["PMetrics"])
				self.contentdata[id]["omPM"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblSM"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Secondary Metric:")
				self.contentdata[id]["lblSM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["SMetrics"] = [None, "", "Loading..."]
				self.contentdata[id]["SMetric"] = tk.StringVar()
				self.contentdata[id]["omSM"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["SMetric"], command=self.cs_datatable_update, *self.contentdata[id]["SMetrics"])
				self.contentdata[id]["omSM"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[id]["lblFA"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Agent:")
					self.contentdata[id]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

					self.contentdata[id]["FATypes"] = [None, "", "Loading..."]
					self.contentdata[id]["FAType"] = tk.StringVar()
					self.contentdata[id]["omFA"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FAType"], command=self.cs_datatable_update, *self.contentdata[id]["FATypes"])
					self.contentdata[id]["omFA"].grid(column=1, row=rownum, sticky="nsew")

					self.contentdata[id]["intFA"] = tk.IntVar()
					self.contentdata[id]["chkFA"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFA"], command=self.cs_datatable_update)
					self.contentdata[id]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFN"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Type:")
				self.contentdata[id]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[id]["FNType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FNType"], command=self.cs_datatable_update, *FNTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFP"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Pattern:")
				self.contentdata[id]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FPattern"] = tk.StringVar()
				self.contentdata[id]["inpFP"] = ttk.Entry(self.contentdata[id]["Frames"][datatype], textvariable=self.contentdata[id]["FPattern"])
				self.contentdata[id]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["inpFP"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["inpFP"].bind('<FocusOut>', self.cs_datatable_update)

			if datatype == "Result":
				rownum += 1
				self.contentdata[id]["lblEnabled"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Enabled")
				self.contentdata[id]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblRT"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Result Type:")
				self.contentdata[id]["lblRT"].grid(column=0, row=rownum, sticky="nsew")

				RTypes = [None, "Response Time", "TPS", "Total TPS"]
				self.contentdata[id]["RType"] = tk.StringVar()
				self.contentdata[id]["omRT"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["RType"], command=self.cs_datatable_update, *RTypes)
				self.contentdata[id]["omRT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# result filtered by PASS, FAIL, None
				self.contentdata[id]["lblFR"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Result:")
				self.contentdata[id]["lblFR"].grid(column=0, row=rownum, sticky="nsew")

				FRTypes = [None, "None", "Pass", "Fail"]
				self.contentdata[id]["FRType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FRType"], command=self.cs_datatable_update, *FRTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["intFR"] = tk.IntVar()
				self.contentdata[id]["chkFR"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFR"], command=self.cs_datatable_update)
				self.contentdata[id]["chkFR"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFA"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Agent:")
				self.contentdata[id]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[id]["FAType"] = tk.StringVar()
				self.contentdata[id]["omFA"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FAType"], command=self.cs_datatable_update, *self.contentdata[id]["FATypes"])
				self.contentdata[id]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["intFA"] = tk.IntVar()
				self.contentdata[id]["chkFA"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFA"], command=self.cs_datatable_update)
				self.contentdata[id]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFN"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Type:")
				self.contentdata[id]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[id]["FNType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FNType"], command=self.cs_datatable_update, *FNTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFP"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Pattern:")
				self.contentdata[id]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FPattern"] = tk.StringVar()
				self.contentdata[id]["inpFP"] = ttk.Entry(self.contentdata[id]["Frames"][datatype], textvariable=self.contentdata[id]["FPattern"])
				self.contentdata[id]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["inpFP"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["inpFP"].bind('<FocusOut>', self.cs_datatable_update)

			if datatype == "ResultSummary":
				rownum += 1
				self.contentdata[id]["lblEnabled"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Enabled")
				self.contentdata[id]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFA"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Agent:")
				self.contentdata[id]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[id]["FAType"] = tk.StringVar()
				self.contentdata[id]["omFA"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FAType"], command=self.cs_datatable_update, *self.contentdata[id]["FATypes"])
				self.contentdata[id]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["intFA"] = tk.IntVar()
				self.contentdata[id]["chkFA"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFA"], command=self.cs_datatable_update)
				self.contentdata[id]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFN"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Type:")
				self.contentdata[id]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[id]["FNType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FNType"], command=self.cs_datatable_update, *FNTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFP"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Pattern:")
				self.contentdata[id]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FPattern"] = tk.StringVar()
				self.contentdata[id]["inpFP"] = ttk.Entry(self.contentdata[id]["Frames"][datatype], textvariable=self.contentdata[id]["FPattern"])
				self.contentdata[id]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["inpFP"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["inpFP"].bind('<FocusOut>', self.cs_datatable_update)

			if datatype == "SQL":
				rownum += 1
				self.contentdata[id]["lblSQL"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="SQL:")
				self.contentdata[id]["lblSQL"].grid(column=0, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["tSQL"] = tk.Text(self.contentdata[id]["Frames"][datatype])
				self.contentdata[id]["tSQL"].grid(column=0, row=rownum, columnspan=100, sticky="nsew")
				# data = self.contentdata[id]["tSQL"].insert('0.0', sql)
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["tSQL"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["tSQL"].bind('<FocusOut>', self.cs_datatable_update)

		base.debugmsg(8, "id:", id, "renamecols 1")
		if "renamecols" not in self.contentdata[id]["Frames"] and datatype not in ["SQL"]:
			base.debugmsg(5, "create renamecols frame")
			rownum = 0
			self.contentdata[id]["Frames"]["renamecols"] = tk.Frame(self.contentdata[id]["LFrame"])
			self.contentdata[id]["Frames"]["renamecols"].columnconfigure(99, weight=1)

			self.contentdata[id]["lblspacer"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text=" ")
			self.contentdata[id]["lblspacer"].grid(column=0, row=rownum, sticky="nsew")

			rownum += 1
			self.contentdata[id]["lblcolren"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Rename Columns")
			self.contentdata[id]["lblcolren"].grid(column=0, row=rownum, sticky="nsew")

			rownum += 1
			self.contentdata[id]["lblcolnme"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Column Name")
			self.contentdata[id]["lblcolnme"].grid(column=0, row=rownum, sticky="nsew")

			self.contentdata[id]["lbldispnme"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Display Name")
			self.contentdata[id]["lbldispnme"].grid(column=1, row=rownum, sticky="nsew")

			self.contentdata[id]["lblshowcol"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Show Column")
			self.contentdata[id]["lblshowcol"].grid(column=2, row=rownum, sticky="nsew")

			if datatype == "Plan":
				self.contentdata[id]["lblcolopt"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Options")
				self.contentdata[id]["lblcolopt"].grid(column=3, row=rownum, sticky="nsew")

			self.contentdata[id]["renamecolumns"] = {}
			self.contentdata[id]["renamecolumns"]["startrow"] = rownum + 1
			self.contentdata[id]["renamecolumns"]["rownum"] = rownum + 1

		base.debugmsg(8, "id:", id, "renamecols 2")
		if datatype not in ["SQL"]:
			self.cs_datatable_add_renamecols(id)
			base.debugmsg(8, "id:", id, "renamecols 2 debug 1")
			# cp = threading.Thread(target=lambda: self.cs_datatable_add_renamecols(id))
			# cp.start()
			self.contentdata[id]["Frames"]["renamecols"].grid(column=0, row=self.contentdata[id]["DTFrame"] + 1, columnspan=100, sticky="nsew")
			base.debugmsg(8, "id:", id, "renamecols 2 debug 2")

		base.debugmsg(8, "id:", id, "Update")
		# Update
		if datatype == "SQL":
			sql = base.rt_table_get_sql(id)
			self.contentdata[id]["tSQL"].delete('0.0', tk.END)
			self.contentdata[id]["tSQL"].insert('0.0', sql)

		if datatype == "Result":
			self.cs_datatable_update_result(id)
			self.contentdata[id]["RType"].set(base.rt_table_get_rt(id))
			self.contentdata[id]["intFR"].set(base.rt_table_get_enfr(id))
			self.contentdata[id]["FRType"].set(base.rt_table_get_fr(id))
			self.contentdata[id]["intFA"].set(base.rt_table_get_enfa(id))
			self.contentdata[id]["FAType"].set(base.rt_table_get_fa(id))
			self.contentdata[id]["FNType"].set(base.rt_table_get_fn(id))
			self.contentdata[id]["FPattern"].set(base.rt_table_get_fp(id))

		if datatype == "ResultSummary":
			self.cs_datatable_update_result(id)
			self.contentdata[id]["FNType"].set(base.rt_table_get_fn(id))
			self.contentdata[id]["FPattern"].set(base.rt_table_get_fp(id))

		if datatype == "Metric":
			base.debugmsg(5, "Update Options")
			self.cs_datatable_update_metrics(id)
			base.debugmsg(5, "Set Options")
			while "SMetric" not in self.contentdata[id]:
				time.sleep(0.1)
			self.contentdata[id]["intIsNum"].set(base.rt_table_get_isnumeric(id))
			self.contentdata[id]["intShCnt"].set(base.rt_table_get_showcount(id))
			self.contentdata[id]["MType"].set(base.rt_table_get_mt(id))
			self.contentdata[id]["PMetric"].set(base.rt_table_get_pm(id))
			self.contentdata[id]["SMetric"].set(base.rt_table_get_sm(id))
			self.contentdata[id]["intFA"].set(base.rt_table_get_enfa(id))
			self.contentdata[id]["FAType"].set(base.rt_table_get_fa(id))
			self.contentdata[id]["FNType"].set(base.rt_table_get_fn(id))
			self.contentdata[id]["FPattern"].set(base.rt_table_get_fp(id))

		base.debugmsg(8, "id:", id, "Show")
		# Show
		self.contentdata[id]["Frames"][datatype].grid(column=0, row=self.contentdata[id]["DTFrame"], columnspan=100, sticky="nsew")

	def cs_datatable_add_renamecols(self, id):
		base.debugmsg(5, "id:", id)
		if "renamecolumns" in self.contentdata[id]:
			datatype = base.rt_table_get_dt(id)

			if datatype == "SQL":
				sql = base.rt_table_get_sql(id)
				if len(sql.strip()) < 1:
					return None
			else:
				sql = base.rt_table_generate_sql(id)
				if len(sql.strip()) < 1:
					return None
				if datatype not in ["Plan"]:
					sql += " LIMIT 1 "

			base.debugmsg(5, "sql:", sql)
			key = "{}_{}_{}".format(id, base.report_item_get_changed(id), datetime.now().timestamp())
			base.dbqueue["Read"].append({"SQL": sql, "KEY": key})

			if "colnames" not in self.contentdata[id]["renamecolumns"]:
				self.contentdata[id]["renamecolumns"]["colnames"] = []
			else:
				self.cs_datatable_reset_renamecols(id)
				self.contentdata[id]["renamecolumns"]["colnames"] = []
			self.contentdata[id]["renamecolumns"]["rownum"] = self.contentdata[id]["renamecolumns"]["startrow"]

			while key not in base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = base.dbqueue["ReadResult"][key]
			if datatype == "Plan":
				base.debugmsg(9, "tdata before:", tdata)
				tdata = base.table_postprocess_data_plan(id, tdata)
			base.debugmsg(8, "tdata:", tdata)

			if len(tdata) > 0:
				cols = list(tdata[0].keys())
				base.debugmsg(7, "cols:", cols)
				for col in cols:
					if col not in ["Colour"]:
						self.cs_datatable_add_renamecol(id, col)

	def cs_datatable_reset_renamecols(self, id):
		base.debugmsg(5, "id:", id)
		if "colnames" in self.contentdata[id]["renamecolumns"]:
			for colname in list(self.contentdata[id]["renamecolumns"]["colnames"]):
				base.debugmsg(5, "id:", id, "	colname:", colname)
				collabel = "lbl_{}".format(colname)
				colinput = "inp_{}".format(colname)
				try:
					self.contentdata[id]["renamecolumns"][collabel].grid_forget()
				except Exception as e:
					base.debugmsg(9, "e:", e)
				try:
					self.contentdata[id]["renamecolumns"][colinput].grid_forget()
				except Exception as e:
					base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"][collabel]
				except Exception as e:
					base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"][colinput]
				except Exception as e:
					base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"][colname]
				except Exception as e:
					base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"]["colnames"]
				except Exception as e:
					base.debugmsg(9, "e:", e)

	def cs_datatable_add_renamecol(self, id, colname):
		base.debugmsg(5, "id:", id, "	colname:", colname)
		datatype = base.rt_table_get_dt(id)

		if "renamecolumns" in self.contentdata[id] and "renamecols" in self.contentdata[id]["Frames"]:
			collabel = "lbl_{}".format(colname)
			colinput = "inp_{}".format(colname)
			colshow = "show_{}".format(colname)
			colopt = "opt_{}".format(colname)
			rownum = self.contentdata[id]["renamecolumns"]["rownum"]
			if colname not in self.contentdata[id]["renamecolumns"]["colnames"]:
				self.contentdata[id]["renamecolumns"]["rownum"] += 1
				colnum = 0
				self.contentdata[id]["renamecolumns"]["colnames"].append(colname)
				self.contentdata[id]["renamecolumns"][collabel] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text=" {} ".format(colname))
				self.contentdata[id]["renamecolumns"][collabel].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				self.contentdata[id]["renamecolumns"][colname] = tk.StringVar()
				self.contentdata[id]["renamecolumns"][colinput] = ttk.Entry(self.contentdata[id]["Frames"]["renamecols"], textvariable=self.contentdata[id]["renamecolumns"][colname])
				self.contentdata[id]["renamecolumns"][colinput].grid(column=colnum, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["renamecolumns"][colinput].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["renamecolumns"][colinput].bind('<FocusOut>', self.cs_datatable_update)
				self.contentdata[id]["renamecolumns"][colname].set(base.rt_table_get_colname(id, colname))

				colnum += 1
				self.contentdata[id]["renamecolumns"][f"{colname} Show"] = tk.IntVar()
				self.contentdata[id]["renamecolumns"][colshow] = ttk.Checkbutton(self.contentdata[id]["Frames"]["renamecols"], variable=self.contentdata[id]["renamecolumns"][f"{colname} Show"], command=self.cs_datatable_update)
				self.contentdata[id]["renamecolumns"][colshow].grid(column=colnum, row=rownum, sticky="nsew")
				self.contentdata[id]["renamecolumns"][f"{colname} Show"].set(base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{colname} Show")))
				base.debugmsg(5, "colnum:", colnum, "	rownum:", rownum)

				if datatype == "Plan":
					if colname == "Script":
						colnum += 1
						optval = base.report_item_get_value(id, base.rt_table_ini_colname(f"{colname} Opt"))
						if optval is None:
							optval = "File"

						base.debugmsg(5, "colnum:", colnum, "	rownum:", rownum, "	optval:", optval)

						DataTypes = [None, "File", "Path"]
						self.contentdata[id]["renamecolumns"][f"{colname} Opt"] = tk.StringVar()
						self.contentdata[id]["renamecolumns"][colopt] = ttk.OptionMenu(self.contentdata[id]["Frames"]["renamecols"], self.contentdata[id]["renamecolumns"][f"{colname} Opt"], command=self.cs_datatable_update, *DataTypes)
						self.contentdata[id]["renamecolumns"][colopt].grid(column=colnum, row=rownum, sticky="nsew")
						self.contentdata[id]["renamecolumns"][f"{colname} Opt"].set(optval)

	#
	# Settings	-	Graph
	#

	def cs_graph(self, id):
		base.debugmsg(9, "id:", id)
		pid, idl, idr = base.rt_graph_LR_Ids(id)

		iST = base.rt_setting_get_starttime(pid)
		iET = base.rt_setting_get_endtime(pid)

		axisenl = base.rt_graph_get_axisen(idl)
		axisenr = base.rt_graph_get_axisen(idr)
		datatypel = base.rt_graph_get_dt(idl)
		datatyper = base.rt_graph_get_dt(idr)
		self.contentdata[pid]["LFrame"].columnconfigure(99, weight=1)
		rownum = 0

		# 		start time
		rownum += 1
		self.contentdata[pid]["lblST"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Start Time:")
		self.contentdata[pid]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[pid]["strST"] = tk.StringVar()
		fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
		self.contentdata[pid]["strST"].set(fST)
		self.contentdata[pid]["fST"] = fST

		self.contentdata[pid]["eST"] = ttk.Entry(self.contentdata[pid]["LFrame"], textvariable=self.contentdata[pid]["strST"])
		self.contentdata[pid]["eST"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[pid]["eST"].bind('<Leave>', self.cs_graph_update)
		self.contentdata[pid]["eST"].bind('<FocusOut>', self.cs_graph_update)

		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["RFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		# 		end time
		rownum += 1
		self.contentdata[pid]["lblET"] = ttk.Label(self.contentdata[pid]["LFrame"], text="End Time:")
		self.contentdata[pid]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[pid]["strET"] = tk.StringVar()
		fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
		self.contentdata[pid]["strET"].set(fET)
		self.contentdata[pid]["fET"] = fET

		self.contentdata[pid]["eET"] = ttk.Entry(self.contentdata[pid]["LFrame"], textvariable=self.contentdata[pid]["strET"])
		self.contentdata[pid]["eET"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[pid]["eET"].bind('<Leave>', self.cs_graph_update)
		self.contentdata[pid]["eET"].bind('<FocusOut>', self.cs_graph_update)

		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["RFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		# 		blank row
		rownum += 1
		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["LFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["RFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		# 		Y-Axis
		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Y-Axis:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblLeft"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Left")
		self.contentdata[id]["lblLeft"].grid(column=1, row=rownum, sticky="nsew")

		# self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[pid]["RFrame"], text="                        ", style='Report.TLabel')
		# self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblRight"] = ttk.Label(self.contentdata[pid]["RFrame"], text="Right")
		self.contentdata[id]["lblRight"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Enable:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[idl]["intAxsEn"] = tk.IntVar()
		self.contentdata[idl]["chkAxsEn"] = ttk.Checkbutton(self.contentdata[pid]["LFrame"], variable=self.contentdata[idl]["intAxsEn"], command=self.cs_graph_update)
		self.contentdata[idl]["intAxsEn"].set(axisenl)
		self.contentdata[idl]["chkAxsEn"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[idr]["intAxsEn"] = tk.IntVar()
		self.contentdata[idr]["chkAxsEn"] = ttk.Checkbutton(self.contentdata[pid]["RFrame"], variable=self.contentdata[idr]["intAxsEn"], command=self.cs_graph_update)
		self.contentdata[idr]["intAxsEn"].set(axisenr)
		self.contentdata[idr]["chkAxsEn"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Data Type:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		DataTypes = [None, "Metric", "Result", "Plan", "SQL"]
		self.contentdata[idl]["strDT"] = tk.StringVar()
		self.contentdata[idl]["omDT"] = ttk.OptionMenu(self.contentdata[pid]["LFrame"], self.contentdata[idl]["strDT"], command=self.cs_graph_switchdt, *DataTypes)
		self.contentdata[idl]["strDT"].set(datatypel)
		self.contentdata[idl]["omDT"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[idr]["strDT"] = tk.StringVar()
		self.contentdata[idr]["omDT"] = ttk.OptionMenu(self.contentdata[pid]["RFrame"], self.contentdata[idr]["strDT"], command=self.cs_graph_switchdt, *DataTypes)
		self.contentdata[idr]["strDT"].set(datatyper)
		self.contentdata[idr]["omDT"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["DTFrame"] = rownum
		self.cs_graph_switchdt(id)

	def cs_graph_update(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		base.debugmsg(9, "id:", id)
		pid, idl, idr = base.rt_graph_LR_Ids(id)
		changes = 0

		# 		start time
		if "strST" in self.contentdata[pid] and "fST" in self.contentdata[pid]:
			st = self.contentdata[pid]["strST"].get()
			base.debugmsg(5, "st:", st)
			if st != self.contentdata[pid]["fST"]:
				ist = base.report_formateddatetimetosec(st)
				base.debugmsg(5, "ist:", ist)
				if ist > 0:
					ios = ist - base.rs_setting_get_starttime()
					base.debugmsg(5, "ios:", ios)
					changes += base.report_item_set_int(pid, "startoffset", ios)

			iST = base.rt_setting_get_starttime(pid)
			fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
			self.contentdata[id]["strST"].set(fST)
			self.contentdata[id]["fST"] = fST

		# 		end time
		if "strET" in self.contentdata[pid] and "fET" in self.contentdata[pid]:
			et = self.contentdata[pid]["strET"].get()
			base.debugmsg(5, "et:", et)
			if et != self.contentdata[pid]["fET"]:
				iet = base.report_formateddatetimetosec(et)
				base.debugmsg(5, "iet:", iet)
				if iet > 0:
					ios = base.rs_setting_get_endtime() - iet
					base.debugmsg(5, "ios:", ios)
					changes += base.report_item_set_int(pid, "endoffset", ios)

			iET = base.rt_setting_get_endtime(pid)
			fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
			self.contentdata[id]["strET"].set(fET)
			self.contentdata[id]["fET"] = fET

		# intIsNum
		if "intIsNum" in self.contentdata[idl]:
			value = self.contentdata[idl]["intIsNum"].get()
			changes += base.rt_table_set_isnumeric(idl, value)
		if "intIsNum" in self.contentdata[idr]:
			value = self.contentdata[idr]["intIsNum"].get()
			changes += base.rt_table_set_isnumeric(idr, value)

		# intShCnt
		if "intShCnt" in self.contentdata[idl]:
			value = self.contentdata[idl]["intShCnt"].get()
			changes += base.rt_table_set_showcount(idl, value)
		if "intShCnt" in self.contentdata[idr]:
			value = self.contentdata[idr]["intShCnt"].get()
			changes += base.rt_table_set_showcount(idr, value)

		if "MType" in self.contentdata[idl]:
			value = self.contentdata[idl]["MType"].get()
			changes += base.rt_table_set_mt(idl, value)
		if "MType" in self.contentdata[idr]:
			value = self.contentdata[idr]["MType"].get()
			changes += base.rt_table_set_mt(idr, value)

		if "PMetric" in self.contentdata[idl]:
			value = self.contentdata[idl]["PMetric"].get()
			changes += base.rt_table_set_pm(idl, value)
		if "PMetric" in self.contentdata[idr]:
			value = self.contentdata[idr]["PMetric"].get()
			changes += base.rt_table_set_pm(idr, value)

		if "SMetric" in self.contentdata[idl]:
			value = self.contentdata[idl]["SMetric"].get()
			changes += base.rt_table_set_sm(idl, value)
		if "SMetric" in self.contentdata[idr]:
			value = self.contentdata[idr]["SMetric"].get()
			changes += base.rt_table_set_sm(idr, value)

		if "RType" in self.contentdata[idl]:
			value = self.contentdata[idl]["RType"].get()
			changes += base.rt_table_set_rt(idl, value)
		if "RType" in self.contentdata[idr]:
			value = self.contentdata[idr]["RType"].get()
			changes += base.rt_table_set_rt(idr, value)

		if "FRType" in self.contentdata[idl]:
			value = self.contentdata[idl]["FRType"].get()
			changes += base.rt_table_set_fr(idl, value)
		if "FRType" in self.contentdata[idr]:
			value = self.contentdata[idr]["FRType"].get()
			changes += base.rt_table_set_fr(idr, value)

		if "intFR" in self.contentdata[idl]:
			value = self.contentdata[idl]["intFR"].get()
			changes += base.rt_table_set_enfr(idl, value)
		if "intFR" in self.contentdata[idr]:
			value = self.contentdata[idr]["intFR"].get()
			changes += base.rt_table_set_enfr(idr, value)

		if "intFA" in self.contentdata[idl]:
			value = self.contentdata[idl]["intFA"].get()
			changes += base.rt_table_set_enfa(idl, value)
		if "intFA" in self.contentdata[idr]:
			value = self.contentdata[idr]["intFA"].get()
			changes += base.rt_table_set_enfa(idr, value)

		if "FAType" in self.contentdata[idl]:
			value = self.contentdata[idl]["FAType"].get()
			changes += base.rt_table_set_fa(idl, value)
		if "FAType" in self.contentdata[idr]:
			value = self.contentdata[idr]["FAType"].get()
			changes += base.rt_table_set_fa(idr, value)

		if "FNType" in self.contentdata[idl]:
			value = self.contentdata[idl]["FNType"].get()
			changes += base.rt_table_set_fn(idl, value)
		if "FNType" in self.contentdata[idr]:
			value = self.contentdata[idr]["FNType"].get()
			changes += base.rt_table_set_fn(idr, value)

		if "FPattern" in self.contentdata[idl]:
			value = self.contentdata[idl]["FPattern"].get()
			changes += base.rt_table_set_fp(idl, value)
		if "FPattern" in self.contentdata[idr]:
			value = self.contentdata[idr]["FPattern"].get()
			changes += base.rt_table_set_fp(idr, value)

		if "strDT" in self.contentdata[idl]:
			datatype = self.contentdata[idl]["strDT"].get()
			changes += base.rt_table_set_dt(idl, datatype)
			if datatype == "Metric":
				self.cs_datatable_update_metrics(idl)
			if datatype != "SQL":
				time.sleep(0.1)
				base.rt_graph_generate_sql(idl)
		if "strDT" in self.contentdata[idr]:
			datatype = self.contentdata[idr]["strDT"].get()
			changes += base.rt_table_set_dt(idr, datatype)
			if datatype == "Metric":
				self.cs_datatable_update_metrics(idr)
			if datatype != "SQL":
				time.sleep(0.1)
				base.rt_graph_generate_sql(idr)

		# self.contentdata[idl]["intAxsEn"] = tk.IntVar()
		if "intAxsEn" in self.contentdata[idl]:
			value = self.contentdata[idl]["intAxsEn"].get()
			changes += base.rt_graph_set_axisen(idl, value)
		if "intAxsEn" in self.contentdata[idr]:
			value = self.contentdata[idr]["intAxsEn"].get()
			changes += base.rt_graph_set_axisen(idr, value)

		if "intSTot" in self.contentdata[idl]:
			value = self.contentdata[idl]["intSTot"].get()
			changes += base.report_item_set_int(idl, "ShowTotal", value)
		if "intSTot" in self.contentdata[idr]:
			value = self.contentdata[idr]["intSTot"].get()
			changes += base.report_item_set_int(idr, "ShowTotal", value)

		if "tSQL" in self.contentdata[idl]:
			data = self.contentdata[idl]["tSQL"].get('0.0', tk.END).strip()
			base.debugmsg(5, "data:", data)
			changes += base.rt_graph_set_sql(idl, data)
		else:
			time.sleep(0.1)
			base.rt_graph_generate_sql(idl)
			changes += 1

		if "tSQL" in self.contentdata[idr]:
			data = self.contentdata[idr]["tSQL"].get('0.0', tk.END).strip()
			base.debugmsg(5, "data:", data)
			changes += base.rt_graph_set_sql(idr, data)
		else:
			time.sleep(0.1)
			base.rt_graph_generate_sql(idr)
			changes += 1

		if changes > 0:
			base.debugmsg(5, "content_preview id:", id)
			# self.content_preview(id)
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

	def cs_graph_switchdt(self, _event=None):
		base.debugmsg(5, "self:", self, "	_event:", _event)
		rownum = 0
		id = self.sectionstree.focus()
		base.debugmsg(5, "id:", id)

		changes = 0

		if _event is not None:
			name = base.report_item_get_name(_event)
			if name is not None:
				id = _event
				base.debugmsg(5, "id:", id)

		pid, idl, idr = base.rt_graph_LR_Ids(id)
		base.debugmsg(5, "pid:", pid, "	idl:", idl, "	idr:", idr)

		# self.cs_datatable_update(id)
		datatypel = self.contentdata[idl]["strDT"].get()
		datatyper = self.contentdata[idr]["strDT"].get()
		base.debugmsg(5, "datatypel:", datatypel, "datatyper:", datatyper)
		if "Frames" not in self.contentdata[id]:
			self.contentdata[id]["Frames"] = {}
		if "Frames" not in self.contentdata[idl]:
			self.contentdata[idl]["Frames"] = {}
		if "Frames" not in self.contentdata[idr]:
			self.contentdata[idr]["Frames"] = {}
		# Forget
		for frame in self.contentdata[id]["Frames"].keys():
			if frame in self.contentdata[id]["Frames"]:
				self.contentdata[id]["Frames"][frame].grid_forget()
			self.contentdata[id]["Frames"] = {}
		for frame in self.contentdata[idl]["Frames"].keys():
			if frame in self.contentdata[id]["Frames"]:
				self.contentdata[idl]["Frames"][frame].grid_forget()
			self.contentdata[idl]["Frames"] = {}
		for frame in self.contentdata[idr]["Frames"].keys():
			if frame in self.contentdata[id]["Frames"]:
				self.contentdata[idr]["Frames"][frame].grid_forget()
			self.contentdata[idr]["Frames"] = {}

		# Construct
		if datatypel not in self.contentdata[id]["Frames"]:
			base.debugmsg(6, "datatypel:", datatypel)
			self.contentdata[idl]["Frames"][datatypel] = tk.Frame(self.contentdata[id]["LFrame"])
			# self.contentdata[id]["Frames"][datatypel].config(bg="SlateBlue3")
			# self.contentdata[id]["Frames"][datatypel].columnconfigure(0, weight=1)
			self.contentdata[idl]["Frames"][datatypel].columnconfigure(99, weight=1)

			# "Metric", "Result", "SQL"

			if datatypel == "Plan":
				rownum += 1
				self.contentdata[idl]["lblSTot"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Show Total:")
				self.contentdata[idl]["lblSTot"].grid(column=0, row=rownum, sticky="nsew")

				# self.contentdata[idl]["Frames"][datatypel].columnconfigure(1, weight=1)
				self.contentdata[idl]["Frames"][datatypel].columnconfigure(1, minsize=150)
				self.contentdata[idl]["intSTot"] = tk.IntVar()
				self.contentdata[idl]["chkSTot"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intSTot"], command=self.cs_graph_update)
				self.contentdata[idl]["chkSTot"].grid(column=1, row=rownum, sticky="nsew")

			if datatypel == "Metric":
				showmetricagents = 0
				if "DBTable" in base.settings and "Metrics" in base.settings["DBTable"] and "DataSource" in base.settings["DBTable"]["Metrics"]:
					showmetricagents = base.settings["DBTable"]["Metrics"]["DataSource"]

				base.debugmsg(6, "datatypel:", datatypel)
				rownum += 1
				self.contentdata[idl]["lblIsNum"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Number Value:")
				self.contentdata[idl]["lblIsNum"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["intIsNum"] = tk.IntVar()
				self.contentdata[idl]["chkIsNum"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intIsNum"], command=self.cs_graph_update)
				self.contentdata[idl]["chkIsNum"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					# rownum += 1
					self.contentdata[idl]["lblEnabled"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Enabled")
					self.contentdata[idl]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblMT"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Metric Type:")
				self.contentdata[idl]["lblMT"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["MTypes"] = [None, "", "Loading..."]
				self.contentdata[idl]["MType"] = tk.StringVar()
				self.contentdata[idl]["omMT"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["MType"], command=self.cs_graph_update, *self.contentdata[idl]["MTypes"])
				self.contentdata[idl]["omMT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblPM"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Primrary Metric:")
				self.contentdata[idl]["lblPM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["PMetrics"] = [None, "", "Loading..."]
				self.contentdata[idl]["PMetric"] = tk.StringVar()
				self.contentdata[idl]["omPM"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["PMetric"], command=self.cs_graph_update, *self.contentdata[idl]["PMetrics"])
				self.contentdata[idl]["omPM"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblSM"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Secondary Metric:")
				self.contentdata[idl]["lblSM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["SMetrics"] = [None, "", "Loading..."]
				self.contentdata[idl]["SMetric"] = tk.StringVar()
				self.contentdata[idl]["omSM"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["SMetric"], command=self.cs_graph_update, *self.contentdata[idl]["SMetrics"])
				self.contentdata[idl]["omSM"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[idl]["lblFA"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Agent:")
					self.contentdata[idl]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

					self.contentdata[idl]["FATypes"] = [None, "", "Loading..."]
					self.contentdata[idl]["FAType"] = tk.StringVar()
					self.contentdata[idl]["omFA"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FAType"], command=self.cs_graph_update, *self.contentdata[idl]["FATypes"])
					self.contentdata[idl]["omFA"].grid(column=1, row=rownum, sticky="nsew")

					self.contentdata[idl]["intFA"] = tk.IntVar()
					self.contentdata[idl]["chkFA"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intFA"], command=self.cs_graph_update)
					self.contentdata[idl]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFN"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Type:")
				self.contentdata[idl]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idl]["FNType"] = tk.StringVar()
				self.contentdata[idl]["omFR"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idl]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFP"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Pattern:")
				self.contentdata[idl]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["FPattern"] = tk.StringVar()
				self.contentdata[idl]["inpFP"] = ttk.Entry(self.contentdata[idl]["Frames"][datatypel], textvariable=self.contentdata[idl]["FPattern"])
				self.contentdata[idl]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idl]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idl]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

			if datatypel == "Result":
				rownum += 1
				self.contentdata[idl]["lblRT"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Result Type:")
				self.contentdata[idl]["lblRT"].grid(column=0, row=rownum, sticky="nsew")

				RTypes = [None, "Response Time", "TPS", "Total TPS"]
				self.contentdata[idl]["RType"] = tk.StringVar()
				self.contentdata[idl]["omRT"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["RType"], command=self.cs_graph_update, *RTypes)
				self.contentdata[idl]["omRT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# result filtered by PASS, FAIL, None
				self.contentdata[idl]["lblFR"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Result:")
				self.contentdata[idl]["lblFR"].grid(column=0, row=rownum, sticky="nsew")

				FRTypes = [None, "None", "Pass", "Fail"]
				self.contentdata[idl]["FRType"] = tk.StringVar()
				self.contentdata[idl]["omFR"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FRType"], command=self.cs_graph_update, *FRTypes)
				self.contentdata[idl]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idl]["intFR"] = tk.IntVar()
				self.contentdata[idl]["chkFR"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intFR"], command=self.cs_graph_update)
				self.contentdata[idl]["chkFR"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFA"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Agent:")
				self.contentdata[idl]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[idl]["FAType"] = tk.StringVar()
				self.contentdata[idl]["omFA"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FAType"], command=self.cs_graph_update, *self.contentdata[idl]["FATypes"])
				self.contentdata[idl]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idl]["intFA"] = tk.IntVar()
				self.contentdata[idl]["chkFA"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intFA"], command=self.cs_graph_update)
				self.contentdata[idl]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFN"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Type:")
				self.contentdata[idl]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idl]["FNType"] = tk.StringVar()
				self.contentdata[idl]["omFR"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idl]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFP"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Pattern:")
				self.contentdata[idl]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["FPattern"] = tk.StringVar()
				self.contentdata[idl]["inpFP"] = ttk.Entry(self.contentdata[idl]["Frames"][datatypel], textvariable=self.contentdata[idl]["FPattern"])
				self.contentdata[idl]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idl]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idl]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

			if datatypel == "SQL":
				rownum += 1
				# sql = base.rt_table_get_sql(id)
				self.contentdata[idl]["lblSQL"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="SQL:")
				self.contentdata[idl]["lblSQL"].grid(column=0, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["tSQL"] = tk.Text(self.contentdata[idl]["Frames"][datatypel])
				self.contentdata[idl]["tSQL"].grid(column=0, row=rownum, columnspan=100, sticky="nsew")
				# data = self.contentdata[id]["tSQL"].insert('0.0', sql)
				# <Leave> makes UI to jumpy
				# self.contentdata[idl]["tSQL"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idl]["tSQL"].bind('<FocusOut>', self.cs_graph_update)

		if datatyper not in self.contentdata[id]["Frames"]:
			base.debugmsg(6, "datatyper:", datatyper)
			self.contentdata[idr]["Frames"][datatyper] = tk.Frame(self.contentdata[id]["RFrame"])
			# self.contentdata[id]["Frames"][datatyper].config(bg="SlateBlue3")
			# self.contentdata[id]["Frames"][datatyper].columnconfigure(0, weight=1)
			self.contentdata[idr]["Frames"][datatyper].columnconfigure(99, weight=1)

			# "Metric", "Result", "SQL"

			if datatyper == "Plan":
				rownum += 1
				self.contentdata[idr]["lblSTot"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Show Total:")
				self.contentdata[idr]["lblSTot"].grid(column=0, row=rownum, sticky="nsew")

				# self.contentdata[idr]["Frames"][datatyper].columnconfigure(1, weight=1)
				self.contentdata[idr]["Frames"][datatyper].columnconfigure(1, minsize=150)
				self.contentdata[idr]["intSTot"] = tk.IntVar()
				self.contentdata[idr]["chkSTot"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intSTot"], command=self.cs_graph_update)
				self.contentdata[idr]["chkSTot"].grid(column=1, row=rownum, sticky="nsew")

			if datatyper == "Metric":
				showmetricagents = 0
				if "DBTable" in base.settings and "Metrics" in base.settings["DBTable"] and "DataSource" in base.settings["DBTable"]["Metrics"]:
					showmetricagents = base.settings["DBTable"]["Metrics"]["DataSource"]

				base.debugmsg(6, "datatyper:", datatyper)
				rownum += 1
				self.contentdata[idr]["lblIsNum"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Number Value:")
				self.contentdata[idr]["lblIsNum"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["intIsNum"] = tk.IntVar()
				self.contentdata[idr]["chkIsNum"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intIsNum"], command=self.cs_graph_update)
				self.contentdata[idr]["chkIsNum"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					# rownum += 1
					self.contentdata[idr]["lblEnabled"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Enabled")
					self.contentdata[idr]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblMT"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Metric Type:")
				self.contentdata[idr]["lblMT"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["MTypes"] = [None, "", "Loading..."]
				self.contentdata[idr]["MType"] = tk.StringVar()
				self.contentdata[idr]["omMT"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["MType"], command=self.cs_graph_update, *self.contentdata[idr]["MTypes"])
				self.contentdata[idr]["omMT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblPM"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Primrary Metric:")
				self.contentdata[idr]["lblPM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["PMetrics"] = [None, "", "Loading..."]
				self.contentdata[idr]["PMetric"] = tk.StringVar()
				self.contentdata[idr]["omPM"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["PMetric"], command=self.cs_graph_update, *self.contentdata[idr]["PMetrics"])
				self.contentdata[idr]["omPM"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblSM"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Secondary Metric:")
				self.contentdata[idr]["lblSM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["SMetrics"] = [None, "", "Loading..."]
				self.contentdata[idr]["SMetric"] = tk.StringVar()
				self.contentdata[idr]["omSM"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["SMetric"], command=self.cs_graph_update, *self.contentdata[idr]["SMetrics"])
				self.contentdata[idr]["omSM"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[idr]["lblFA"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Agent:")
					self.contentdata[idr]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

					self.contentdata[idr]["FATypes"] = [None, "", "Loading..."]
					self.contentdata[idr]["FAType"] = tk.StringVar()
					self.contentdata[idr]["omFA"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FAType"], command=self.cs_graph_update, *self.contentdata[idr]["FATypes"])
					self.contentdata[idr]["omFA"].grid(column=1, row=rownum, sticky="nsew")

					self.contentdata[idr]["intFA"] = tk.IntVar()
					self.contentdata[idr]["chkFA"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intFA"], command=self.cs_graph_update)
					self.contentdata[idr]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFN"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Type:")
				self.contentdata[idr]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idr]["FNType"] = tk.StringVar()
				self.contentdata[idr]["omFR"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idr]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFP"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Pattern:")
				self.contentdata[idr]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["FPattern"] = tk.StringVar()
				self.contentdata[idr]["inpFP"] = ttk.Entry(self.contentdata[idr]["Frames"][datatyper], textvariable=self.contentdata[idr]["FPattern"])
				self.contentdata[idr]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idr]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idr]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

			if datatyper == "Result":
				rownum += 1
				self.contentdata[idr]["lblRT"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Result Type:")
				self.contentdata[idr]["lblRT"].grid(column=0, row=rownum, sticky="nsew")

				RTypes = [None, "Response Time", "TPS", "Total TPS"]
				self.contentdata[idr]["RType"] = tk.StringVar()
				self.contentdata[idr]["omRT"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["RType"], command=self.cs_graph_update, *RTypes)
				self.contentdata[idr]["omRT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# result filtered by PASS, FAIL, None
				self.contentdata[idr]["lblFR"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Result:")
				self.contentdata[idr]["lblFR"].grid(column=0, row=rownum, sticky="nsew")

				FRTypes = [None, "None", "Pass", "Fail"]
				self.contentdata[idr]["FRType"] = tk.StringVar()
				self.contentdata[idr]["omFR"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FRType"], command=self.cs_graph_update, *FRTypes)
				self.contentdata[idr]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idr]["intFR"] = tk.IntVar()
				self.contentdata[idr]["chkFR"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intFR"], command=self.cs_graph_update)
				self.contentdata[idr]["chkFR"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFA"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Agent:")
				self.contentdata[idr]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[idr]["FAType"] = tk.StringVar()
				self.contentdata[idr]["omFA"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FAType"], command=self.cs_graph_update, *self.contentdata[idr]["FATypes"])
				self.contentdata[idr]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idr]["intFA"] = tk.IntVar()
				self.contentdata[idr]["chkFA"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intFA"], command=self.cs_graph_update)
				self.contentdata[idr]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFN"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Type:")
				self.contentdata[idr]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idr]["FNType"] = tk.StringVar()
				self.contentdata[idr]["omFR"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idr]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFP"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Pattern:")
				self.contentdata[idr]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["FPattern"] = tk.StringVar()
				self.contentdata[idr]["inpFP"] = ttk.Entry(self.contentdata[idr]["Frames"][datatyper], textvariable=self.contentdata[idr]["FPattern"])
				self.contentdata[idr]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idr]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idr]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

			if datatyper == "SQL":
				rownum += 1
				# sql = base.rt_table_get_sql(id)
				self.contentdata[idr]["lblSQL"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="SQL:")
				self.contentdata[idr]["lblSQL"].grid(column=0, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["tSQL"] = tk.Text(self.contentdata[idr]["Frames"][datatyper])
				self.contentdata[idr]["tSQL"].grid(column=0, row=rownum, columnspan=100, sticky="nsew")
				# data = self.contentdata[idr]["tSQL"].insert('0.0', sql)
				# <Leave> makes UI to jumpy
				# self.contentdata[idr]["tSQL"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idr]["tSQL"].bind('<FocusOut>', self.cs_graph_update)

		# Update
		if datatypel == "SQL":
			sql = base.rt_graph_get_sql(idl)
			self.contentdata[idl]["tSQL"].delete('0.0', tk.END)
			self.contentdata[idl]["tSQL"].insert('0.0', sql)

		if datatyper == "SQL":
			sql = base.rt_graph_get_sql(idr)
			self.contentdata[idr]["tSQL"].delete('0.0', tk.END)
			self.contentdata[idr]["tSQL"].insert('0.0', sql)

		if datatypel == "Result":
			self.cs_datatable_update_result(idl)
			self.contentdata[idl]["RType"].set(base.rt_table_get_rt(idl))
			self.contentdata[idl]["intFR"].set(base.rt_table_get_enfr(idl))
			self.contentdata[idl]["FRType"].set(base.rt_table_get_fr(idl))
			self.contentdata[idl]["intFA"].set(base.rt_table_get_enfa(idl))
			self.contentdata[idl]["FAType"].set(base.rt_table_get_fa(idl))
			self.contentdata[idl]["FNType"].set(base.rt_table_get_fn(idl))
			self.contentdata[idl]["FPattern"].set(base.rt_table_get_fp(idl))

		if datatyper == "Result":
			self.cs_datatable_update_result(idr)
			self.contentdata[idr]["RType"].set(base.rt_table_get_rt(idr))
			self.contentdata[idr]["intFR"].set(base.rt_table_get_enfr(idr))
			self.contentdata[idr]["FRType"].set(base.rt_table_get_fr(idr))
			self.contentdata[idr]["intFA"].set(base.rt_table_get_enfa(idr))
			self.contentdata[idr]["FAType"].set(base.rt_table_get_fa(idr))
			self.contentdata[idr]["FNType"].set(base.rt_table_get_fn(idr))
			self.contentdata[idr]["FPattern"].set(base.rt_table_get_fp(idr))

		if datatypel == "Metric":
			base.debugmsg(5, "Update Options")
			self.cs_datatable_update_metrics(idl)
			base.debugmsg(5, "Set Options")
			while "SMetric" not in self.contentdata[idl]:
				time.sleep(0.1)
			if "intIsNum" in self.contentdata[idl]:
				self.contentdata[idl]["intIsNum"].set(base.rt_table_get_isnumeric(idl))
			if "MType" in self.contentdata[idl]:
				self.contentdata[idl]["MType"].set(base.rt_table_get_mt(idl))
			if "PMetric" in self.contentdata[idl]:
				self.contentdata[idl]["PMetric"].set(base.rt_table_get_pm(idl))
			if "SMetric" in self.contentdata[idl]:
				self.contentdata[idl]["SMetric"].set(base.rt_table_get_sm(idl))
			if "intFA" in self.contentdata[idl]:
				self.contentdata[idl]["intFA"].set(base.rt_table_get_enfa(idl))
			if "FAType" in self.contentdata[idl]:
				self.contentdata[idl]["FAType"].set(base.rt_table_get_fa(idl))
			if "FNType" in self.contentdata[idl]:
				self.contentdata[idl]["FNType"].set(base.rt_table_get_fn(idl))
			if "FPattern" in self.contentdata[idl]:
				self.contentdata[idl]["FPattern"].set(base.rt_table_get_fp(idl))

		if datatyper == "Metric":
			base.debugmsg(5, "Update Options")
			self.cs_datatable_update_metrics(idr)
			base.debugmsg(5, "Set Options")
			while "SMetric" not in self.contentdata[idr]:
				time.sleep(0.1)
			if "intIsNum" in self.contentdata[idr]:
				self.contentdata[idr]["intIsNum"].set(base.rt_table_get_isnumeric(idr))
			if "MType" in self.contentdata[idr]:
				self.contentdata[idr]["MType"].set(base.rt_table_get_mt(idr))
			if "PMetric" in self.contentdata[idr]:
				self.contentdata[idr]["PMetric"].set(base.rt_table_get_pm(idr))
			if "SMetric" in self.contentdata[idr]:
				self.contentdata[idr]["SMetric"].set(base.rt_table_get_sm(idr))
			if "intFA" in self.contentdata[idr]:
				self.contentdata[idr]["intFA"].set(base.rt_table_get_enfa(idr))
			if "FAType" in self.contentdata[idr]:
				self.contentdata[idr]["FAType"].set(base.rt_table_get_fa(idr))
			if "FNType" in self.contentdata[idr]:
				self.contentdata[idr]["FNType"].set(base.rt_table_get_fn(idr))
			if "FPattern" in self.contentdata[idr]:
				self.contentdata[idr]["FPattern"].set(base.rt_table_get_fp(idr))

		if datatypel == "Plan":
			self.contentdata[idl]["intSTot"].set(base.report_item_get_int(idl, "ShowTotal"))
			changes += 1

		if datatyper == "Plan":
			self.contentdata[idr]["intSTot"].set(base.report_item_get_int(idr, "ShowTotal"))
			changes += 1

		# Show
		self.contentdata[idl]["Frames"][datatypel].grid(column=0, row=self.contentdata[id]["DTFrame"], columnspan=100, sticky="nsew")
		self.contentdata[idr]["Frames"][datatyper].grid(column=0, row=self.contentdata[id]["DTFrame"], columnspan=100, sticky="nsew")

		if changes > 0:
			self.cs_graph_update(_event)

	#
	# Settings	-	Error Details
	#

	def cs_errors(self, id):
		base.debugmsg(9, "id:", id)

		iST = base.rt_setting_get_starttime(id)
		base.debugmsg(5, "iST:", iST)
		iET = base.rt_setting_get_endtime(id)
		base.debugmsg(5, "iET:", iET)

		images = base.rt_errors_get_images(id)
		base.debugmsg(5, "images:", images)
		grouprn = base.rt_errors_get_group_rn(id)
		base.debugmsg(5, "grouprn:", grouprn)
		groupet = base.rt_errors_get_group_et(id)
		base.debugmsg(5, "groupet:", groupet)

		lbl_Result = base.rt_errors_get_label(id, "lbl_Result")
		lbl_Test = base.rt_errors_get_label(id, "lbl_Test")
		lbl_Script = base.rt_errors_get_label(id, "lbl_Script")
		lbl_Error = base.rt_errors_get_label(id, "lbl_Error")
		lbl_Count = base.rt_errors_get_label(id, "lbl_Count")
		lbl_Screenshot = base.rt_errors_get_label(id, "lbl_Screenshot")
		lbl_NoScreenshot = base.rt_errors_get_label(id, "lbl_NoScreenshot")

		self.contentdata[id]["LFrame"].columnconfigure(99, weight=1)
		rownum = 0

		# 		start time
		rownum += 1
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["LFrame"], text="Start Time:")
		self.contentdata[id]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strST"] = tk.StringVar()
		fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
		self.contentdata[id]["strST"].set(fST)
		self.contentdata[id]["fST"] = fST

		self.contentdata[id]["eST"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strST"])
		self.contentdata[id]["eST"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["eST"].bind('<FocusOut>', self.cs_errors_update)

		# 		end time
		rownum += 1
		self.contentdata[id]["lblET"] = ttk.Label(self.contentdata[id]["LFrame"], text="End Time:")
		self.contentdata[id]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strET"] = tk.StringVar()
		fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
		self.contentdata[id]["strET"].set(fET)
		self.contentdata[id]["fET"] = fET

		self.contentdata[id]["eET"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strET"])
		self.contentdata[id]["eET"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["eET"].bind('<FocusOut>', self.cs_errors_update)

		# 		Show Screenshots
		rownum += 1
		self.contentdata[id]["lblImages"] = ttk.Label(self.contentdata[id]["LFrame"], text="Show screenshots:")
		self.contentdata[id]["lblImages"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intImages"] = tk.IntVar()
		self.contentdata[id]["chkImages"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intImages"], command=self.cs_errors_update)
		self.contentdata[id]["intImages"].set(images)
		self.contentdata[id]["chkImages"].grid(column=1, row=rownum, sticky="nsew")

		# 		Group by result name
		rownum += 1
		self.contentdata[id]["lblGroupRN"] = ttk.Label(self.contentdata[id]["LFrame"], text="Group by result name:")
		self.contentdata[id]["lblGroupRN"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intGroupRN"] = tk.IntVar()
		self.contentdata[id]["chkGroupRN"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intGroupRN"], command=self.cs_errors_update)
		self.contentdata[id]["intGroupRN"].set(grouprn)
		self.contentdata[id]["chkGroupRN"].grid(column=1, row=rownum, sticky="nsew")

		# 		Group by error text
		rownum += 1
		self.contentdata[id]["lblGroupET"] = ttk.Label(self.contentdata[id]["LFrame"], text="Group by error text:")
		self.contentdata[id]["lblGroupET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intGroupET"] = tk.IntVar()
		self.contentdata[id]["chkGroupET"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intGroupET"], command=self.cs_errors_update)
		self.contentdata[id]["intGroupET"].set(groupet)
		self.contentdata[id]["chkGroupET"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["LFrame"], text=" ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblRename"] = ttk.Label(self.contentdata[id]["LFrame"], text="Rename Labels")
		self.contentdata[id]["lblRename"].grid(column=0, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblLabelName"] = ttk.Label(self.contentdata[id]["LFrame"], text="Label Name")
		self.contentdata[id]["lblLabelName"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblDispName"] = ttk.Label(self.contentdata[id]["LFrame"], text="Display Name")
		self.contentdata[id]["lblDispName"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblResult"] = ttk.Label(self.contentdata[id]["LFrame"], text="Result Name")
		self.contentdata[id]["lblResult"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varResult"] = tk.StringVar()
		self.contentdata[id]["varResult"].set(lbl_Result)
		self.contentdata[id]["inpResult"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varResult"])
		self.contentdata[id]["inpResult"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpResult"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpResult"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblTest"] = ttk.Label(self.contentdata[id]["LFrame"], text="Test")
		self.contentdata[id]["lblTest"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varTest"] = tk.StringVar()
		self.contentdata[id]["varTest"].set(lbl_Test)
		self.contentdata[id]["inpTest"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varTest"])
		self.contentdata[id]["inpTest"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpTest"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpTest"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblScript"] = ttk.Label(self.contentdata[id]["LFrame"], text="Script")
		self.contentdata[id]["lblScript"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varScript"] = tk.StringVar()
		self.contentdata[id]["varScript"].set(lbl_Script)
		self.contentdata[id]["inpScript"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varScript"])
		self.contentdata[id]["inpScript"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpScript"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpScript"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblError"] = ttk.Label(self.contentdata[id]["LFrame"], text="Error")
		self.contentdata[id]["lblError"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varError"] = tk.StringVar()
		self.contentdata[id]["varError"].set(lbl_Error)
		self.contentdata[id]["inpError"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varError"])
		self.contentdata[id]["inpError"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpError"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpError"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblCount"] = ttk.Label(self.contentdata[id]["LFrame"], text="Count")
		self.contentdata[id]["lblCount"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varCount"] = tk.StringVar()
		self.contentdata[id]["varCount"].set(lbl_Count)
		self.contentdata[id]["inpCount"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varCount"])
		self.contentdata[id]["inpCount"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpCount"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpCount"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblScreenshot"] = ttk.Label(self.contentdata[id]["LFrame"], text="Screenshot")
		self.contentdata[id]["lblScreenshot"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varScreenshot"] = tk.StringVar()
		self.contentdata[id]["varScreenshot"].set(lbl_Screenshot)
		self.contentdata[id]["inpScreenshot"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varScreenshot"])
		self.contentdata[id]["inpScreenshot"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpScreenshot"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpScreenshot"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblNoScreenshot"] = ttk.Label(self.contentdata[id]["LFrame"], text="No Screenshot")
		self.contentdata[id]["lblNoScreenshot"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varNoScreenshot"] = tk.StringVar()
		self.contentdata[id]["varNoScreenshot"].set(lbl_NoScreenshot)
		self.contentdata[id]["inpNoScreenshot"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varNoScreenshot"])
		self.contentdata[id]["inpNoScreenshot"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpNoScreenshot"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpNoScreenshot"].bind('<FocusOut>', self.cs_errors_update)

	def cs_errors_update(self, _event=None, *args):
		base.debugmsg(5, "_event:", _event, "	args:", args)
		changes = 0
		# if len(args) > 0:
		# 	base.debugmsg(8, "args[0]:", args[0])
		# 	changes += args[0]
		id = self.sectionstree.focus()
		if _event is not None:
			name = base.report_item_get_name(_event)
			if name is not None:
				id = _event
		base.debugmsg(9, "id:", id)

		# 		start time
		if "strST" in self.contentdata[id]:
			st = self.contentdata[id]["strST"].get()
			base.debugmsg(5, "st:", st)
			if st != self.contentdata[id]["fST"]:
				ist = base.report_formateddatetimetosec(st)
				base.debugmsg(5, "ist:", ist)
				if ist > 0:
					ios = ist - base.rs_setting_get_starttime()
					base.debugmsg(5, "ios:", ios)
					changes += base.report_item_set_int(id, "startoffset", ios)

			iST = base.rt_setting_get_starttime(id)
			fST = "{} {}".format(base.report_formatdate(iST), base.report_formattime(iST))
			self.contentdata[id]["strST"].set(fST)
			self.contentdata[id]["fST"] = fST

		# 		end time
		if "strET" in self.contentdata[id]:
			et = self.contentdata[id]["strET"].get()
			base.debugmsg(5, "et:", et)
			if et != self.contentdata[id]["fET"]:
				iet = base.report_formateddatetimetosec(et)
				base.debugmsg(5, "iet:", iet)
				if iet > 0:
					ios = base.rs_setting_get_endtime() - iet
					base.debugmsg(5, "ios:", ios)
					changes += base.report_item_set_int(id, "endoffset", ios)

			iET = base.rt_setting_get_endtime(id)
			fET = "{} {}".format(base.report_formatdate(iET), base.report_formattime(iET))
			self.contentdata[id]["strET"].set(fET)
			self.contentdata[id]["fET"] = fET

		if "intImages" in self.contentdata[id]:
			images = self.contentdata[id]["intImages"].get()
			changes += base.rt_errors_set_images(id, images)

		if "intGroupRN" in self.contentdata[id]:
			group = self.contentdata[id]["intGroupRN"].get()
			changes += base.rt_errors_set_group_rn(id, group)

		if "intGroupET" in self.contentdata[id]:
			group = self.contentdata[id]["intGroupET"].get()
			changes += base.rt_errors_set_group_et(id, group)

		if "varResult" in self.contentdata[id]:
			lbl_Result = self.contentdata[id]["varResult"].get()
			changes += base.rt_errors_set_label(id, "lbl_Result", lbl_Result)

		if "varTest" in self.contentdata[id]:
			lbl_Test = self.contentdata[id]["varTest"].get()
			changes += base.rt_errors_set_label(id, "lbl_Test", lbl_Test)

		if "varScript" in self.contentdata[id]:
			lbl_Script = self.contentdata[id]["varScript"].get()
			changes += base.rt_errors_set_label(id, "lbl_Script", lbl_Script)

		if "varError" in self.contentdata[id]:
			lbl_Error = self.contentdata[id]["varError"].get()
			changes += base.rt_errors_set_label(id, "lbl_Error", lbl_Error)

		if "varCount" in self.contentdata[id]:
			lbl_Count = self.contentdata[id]["varCount"].get()
			changes += base.rt_errors_set_label(id, "lbl_Count", lbl_Count)

		if "varScreenshot" in self.contentdata[id]:
			lbl_Screenshot = self.contentdata[id]["varScreenshot"].get()
			changes += base.rt_errors_set_label(id, "lbl_Screenshot", lbl_Screenshot)

		if "varNoScreenshot" in self.contentdata[id]:
			lbl_NoScreenshot = self.contentdata[id]["varNoScreenshot"].get()
			changes += base.rt_errors_set_label(id, "lbl_NoScreenshot", lbl_NoScreenshot)

		if changes > 0:
			base.debugmsg(5, "content_preview id:", id)
			# self.content_preview(id)
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

	def cs_update_start_and_end_times(self, id, fST, fET):
		children = base.report_get_order(id)

		for child in children:
			if child not in self.contentdata:
				break
			if "strST" in self.contentdata[child] and "strET" in self.contentdata[child]:
				base.debugmsg(5, "section id with strST and strET to update:", id)
				self.contentdata[child]["strST"].set(fST)
				self.contentdata[child]["strET"].set(fET)
			self.cs_update_start_and_end_times(child, fST, fET)

	#
	# Preview
	#

	def content_preview(self, id):
		base.debugmsg(9, "id:", id)

		if base.config['Reporter']['Results']:
			self.updateStatus("Preview Loading.....")
		else:
			sres = "Please select a result file"
			self.updateStatus(sres)
			return None
		try:
			self.cp_generate_preview(id)
		except Exception as e:
			base.debugmsg(5, "e:", e)

		# self.t_preview[id] = threading.Thread(target=lambda: self.cp_generate_preview(id))
		# self.t_preview[id].start()

		# curritem = self.contentpreview.grid_slaves(column=0, row=0)
		# base.debugmsg(5, "curritem:", curritem)
		# if len(curritem)>0:
		# 	curritem[0].grid_forget()
		curritems = self.contentpreview.grid_slaves()
		# count = len(curritems)
		for curritem in curritems:
			curritem.grid_forget()
		self.cp_display_preview(id, 0)
		self.contentcanvas.config(scrollregion=self.contentpreview.bbox("all"))
		# self.contentpreview.columnconfigure(0, weight=1)

		# self.contentpreview.columnconfigure(0, weight=1)
		self.updateStatus("Preview Loaded")

	def cp_regenerate_preview(self):
		# self.contentdata = {}
		for itm in self.contentdata.keys():
			# if "Preview" in self.contentdata[itm]:
			# 	del self.contentdata[itm]["Preview"]
			self.contentdata[itm]["Changed"] = 0
		self.content_preview("TOP")

	def cp_generate_preview(self, id):
		base.debugmsg(8, "id:", id)
		pid, idl, idr = base.rt_graph_LR_Ids(id)

		base.debugmsg(8, "pid:", pid, "	idl:", idl, "	idr:", idr)
		# if id not in self.contentdata:
		while id not in self.contentdata:
			time.sleep(0.1)
			self.contentdata[pid] = {}
		if "Changed" not in self.contentdata[pid]:
			self.contentdata[pid]["Changed"] = 0
		while idl not in self.contentdata:
			time.sleep(0.1)
			self.contentdata[idl] = {}
		if "Changed" not in self.contentdata[idl]:
			self.contentdata[idl]["Changed"] = 0
		while idr not in self.contentdata:
			time.sleep(0.1)
			self.contentdata[idr] = {}
		if "Changed" not in self.contentdata[idr]:
			self.contentdata[idr]["Changed"] = 0

		type = base.report_item_get_type(pid)
		base.debugmsg(8, "type:", type)
		changed = False

		base.debugmsg(9, "base.report_item_get_changed(pid):", base.report_item_get_changed(pid))
		base.debugmsg(9, "self.contentdata[pid]:", self.contentdata[pid])
		base.debugmsg(9, "self.contentdata[pid][Changed]:", self.contentdata[pid]["Changed"])
		if base.report_item_get_changed(pid) > self.contentdata[pid]["Changed"]:
			changed = True
		base.debugmsg(9, "changed:", changed)
		if type == 'graph':
			base.debugmsg(8, "type:", type)
			if base.report_item_get_changed(idl) > self.contentdata[idl]["Changed"]:
				changed = True
			if base.report_item_get_changed(idr) > self.contentdata[idr]["Changed"]:
				changed = True
		base.debugmsg(8, "changed:", changed)

		gen = False
		if "Preview" not in self.contentdata[pid]:
			gen = True
		# if "Changed" in self.contentdata[id] and base.report_item_get_changed(id) > self.contentdata[id]["Changed"]:
		elif changed:
			gen = True

			base.debugmsg(8, "report_item_get_changed pid:", base.report_item_get_changed(pid), "	contentdata Changed:", self.contentdata[pid]["Changed"])
			if type == 'graph':
				base.debugmsg(8, "report_item_get_changed idl:", base.report_item_get_changed(idl), "	contentdata Changed:", self.contentdata[idl]["Changed"])
				base.debugmsg(8, "report_item_get_changed idr:", base.report_item_get_changed(idr), "	contentdata Changed:", self.contentdata[idr]["Changed"])
		else:
			base.debugmsg(8, "report_item_get_changed pid:", base.report_item_get_changed(pid), "	contentdata Changed:", self.contentdata[pid]["Changed"])
			if type == 'graph':
				base.debugmsg(8, "report_item_get_changed idl:", base.report_item_get_changed(idl), "	contentdata Changed:", self.contentdata[idl]["Changed"])
				base.debugmsg(8, "report_item_get_changed idr:", base.report_item_get_changed(idr), "	contentdata Changed:", self.contentdata[idr]["Changed"])

		base.debugmsg(7, "gen:", gen)
		if gen:
			if "Preview" in self.contentdata[pid]:
				del self.contentdata[pid]["Preview"]
			while "Preview" not in self.contentdata[pid]:
				time.sleep(0.1)
				self.contentdata[pid]["Changed"] = base.report_item_get_changed(pid)
				if type == 'graph':
					self.contentdata[idl]["Changed"] = base.report_item_get_changed(idl)
					self.contentdata[idr]["Changed"] = base.report_item_get_changed(idr)
				self.contentdata[pid]["Preview"] = tk.Frame(self.contentpreview, padx=0, pady=0, bd=0)
			# self.contentdata[id]["Preview"].config(bg="gold")
			# self.contentdata[id]["Preview"].config(bg=self.style_reportbg_colour)
			if id == "TOP":
				try:
					self.cp_titlepage(id)
				except Exception:
					pass
			else:
				rownum = 0

				titlenum = base.report_sect_number(id)
				base.debugmsg(8, "titlenum:", titlenum)
				title = "{} {}".format(titlenum, base.report_item_get_name(id))
				level = base.report_sect_level(id)
				tstyle = 'Report.TLabel'
				if level == 1:

					self.contentdata[id]["lblpgbrk"] = tk.Label(self.contentdata[id]["Preview"], text="	--- page break --- ")
					self.contentdata[id]["lblpgbrk"].config(bg="#ddd")
					self.contentdata[id]["lblpgbrk"].config(fg="#bbb")
					self.contentdata[id]["lblpgbrk"].grid(column=0, row=rownum, columnspan=998, sticky="nsew")

					self.contentdata[id]["lblpgbrk"] = tk.Label(self.contentdata[id]["Preview"], text="	")
					self.contentdata[id]["lblpgbrk"].config(bg="#ddd")
					self.contentdata[id]["lblpgbrk"].grid(column=999, row=rownum, sticky="nsew")

					self.contentdata[id]["Preview"].columnconfigure(1, weight=1)
					# self.contentdata[id]["Preview"].columnconfigure(999, weight=1)

					rownum += 1

					tstyle = 'Report.H1.TLabel'
				if level == 2:
					tstyle = 'Report.H2.TLabel'
				if level == 3:
					tstyle = 'Report.H3.TLabel'
				if level == 4:
					tstyle = 'Report.H4.TLabel'
				if level == 5:
					tstyle = 'Report.H5.TLabel'
				if level == 6:
					tstyle = 'Report.H6.TLabel'

				self.contentdata[id]["lbltitle"] = ttk.Label(self.contentdata[id]["Preview"], text=title, style=tstyle)
				# self.contentdata[id]["lbltitle"] = ttk.Label(self.contentdata[id]["Preview"], text=title)
				# self.contentdata[id]["lbltitle"].config(background=self.style_reportbg_colour)
				self.contentdata[id]["lbltitle"].grid(column=0, row=rownum, columnspan=9, sticky="nsew")

				self.contentdata[id]["rownum"] = rownum + 1
				# type = base.report_item_get_type(id)
				base.debugmsg(8, "type:", type)
				if type == 'contents':
					self.cp_contents(id)
				if type == 'note':
					self.cp_note(id)
				if type == 'table':
					self.cp_table(id)
				if type == 'graph':
					self.cp_graph(id)
				if type == 'errors':
					self.cp_errors(id)

		children = base.report_get_order(id)
		for child in children:
			try:
				self.cp_generate_preview(child)
				# self.t_preview[child] = threading.Thread(target=lambda: self.cp_generate_preview(child))
				# self.t_preview[child].start()
			except Exception as e:
				base.debugmsg(5, "e:", e)

	def cp_display_preview(self, id, row):
		base.debugmsg(5, "id:", id)
		if id in self.t_preview:
			if self.t_preview[id].is_alive():
				self.t_preview[id].join()

		# wait for preview available
		while id not in self.contentdata:
			time.sleep(0.1)
		while "Preview" not in self.contentdata[id]:
			time.sleep(0.1)

		self.updateStatus("Preview Loading..... ({})".format(str(row)))

		self.contentdata[id]["Preview"].grid(column=0, row=row, sticky="nsew")
		nextrow = row + 1
		base.debugmsg(9, "nextrow:", nextrow)
		children = base.report_get_order(id)
		for child in children:
			nextrow = self.cp_display_preview(child, nextrow)
		return nextrow

	def cp_titlepage(self, id):
		base.debugmsg(9, "id:", id)

		self.contentdata[id]["Preview"].columnconfigure(0, weight=1)
		# self.contentdata[id]["Preview"].columnconfigure(1, weight=1)
		self.contentdata[id]["Preview"].columnconfigure(2, weight=1)
		# self.contentdata[id]["Preview"].columnconfigure(3, weight=1)
		self.contentdata[id]["Preview"].columnconfigure(4, weight=1)
		colcontent = 1
		colimg = 2

		# Title
		#  top: 1	centre: 11	bottom:	21
		rownum = 1

		title = "{}".format(base.rs_setting_get_title())
		self.contentdata[id]["lblTitle"] = ttk.Label(self.contentdata[id]["Preview"], text=title, style='Report.Title1.TLabel')
		self.contentdata[id]["lblTitle"].grid(column=colcontent, columnspan=3, row=rownum, sticky="nsew")

		# Logo
		#  top: 2	centre: 12	bottom:	22
		rownum = 12

		base.debugmsg(5, "showtlogo:", base.rs_setting_get_int("showtlogo"))
		if base.rs_setting_get_int("showtlogo"):
			while "strLIPath" not in self.contentdata[id]:
				time.sleep(0.1)
			base.debugmsg(5, "strLIPath:", self.contentdata[id]["strLIPath"])
			if self.contentdata[id]["strLIPath"] is not None and len(self.contentdata[id]["strLIPath"]) > 0:
				self.contentdata[id]["oimg"] = Image.open(self.contentdata[id]["strLIPath"])
				base.debugmsg(5, "oimg:", self.contentdata[id]["oimg"])

				self.contentdata[id]["ologo"] = ImageTk.PhotoImage(self.contentdata[id]["oimg"])
				base.debugmsg(5, "ologo:", self.contentdata[id]["ologo"])

				# display an image label
				# ologo = tk.PhotoImage(file=flogo)
				self.contentdata[id]["lblLogo"] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id]["ologo"])
				# , padding=5
				self.contentdata[id]["lblLogo"].grid(column=colimg, row=rownum, sticky="nsew")

		# Execution Date range
		#  top: 3	centre: 13	bottom:	23
		rownum = 23

		execdr = ""
		fSD = ""

		if base.rs_setting_get_int("showstarttime"):
			iST = base.rs_setting_get_starttime()
			fSD = "{}".format(base.report_formatdate(iST))
			fST = "{}".format(base.report_formattime(iST))

			execdr = "{} {}".format(fSD, fST)

		if base.rs_setting_get_int("showendtime"):
			iET = base.rs_setting_get_endtime()
			fED = "{}".format(base.report_formatdate(iET))
			fET = "{}".format(base.report_formattime(iET))

			if not base.rs_setting_get_int("showstarttime"):
				execdr = "{} {}".format(fED, fET)
			else:
				if fSD == fED:
					execdr = "{} - {}".format(execdr, fET)
				else:
					execdr = "{} - {} {}".format(execdr, fED, fET)

		self.contentdata[id]["lblTitle"] = ttk.Label(self.contentdata[id]["Preview"], text=execdr, style='Report.Title2.TLabel')
		self.contentdata[id]["lblTitle"].grid(column=colcontent, columnspan=3, row=rownum, sticky="nsew")

	def cp_contents(self, id):
		base.debugmsg(5, "id:", id)
		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ", style='Report.TLabel')
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["fmeTOC"] = tk.Frame(self.contentdata[id]["Preview"])
		# self.contentdata[id]["fmeGraph"].config(bg="green")
		self.contentdata[id]["fmeTOC"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["Preview"].columnconfigure(1, weight=1)

		mode = base.rt_contents_get_mode(id)
		level = base.rt_contents_get_level(id)

		base.debugmsg(5, "mode:", mode, "	level:", level)
		fmode = None
		if mode == "Table Of Contents":
			fmode = None
		if mode == "Table of Graphs":
			fmode = "graph"
		if mode == "Table Of Tables":
			fmode = "table"

		self.cp_contents_row("TOP", rownum, id, fmode, level)

	def cp_contents_row(self, id, rownum, fid, fmode, flevel):
		base.debugmsg(5, "id:", id, "	rownum:", rownum, "	fmode:", fmode, "	flevel:", flevel)
		display = True

		level = base.report_sect_level(id)
		if id == "TOP":
			display = False
			level = 0
		base.debugmsg(5, "level:", level)

		if display and fmode is not None:
			display = False
			type = base.report_item_get_type(id)
			if fmode == type:
				display = True

		if display and level > flevel:
			display = False

		nextrow = rownum
		if display:
			type = base.report_item_get_type(id)
			titlenum = base.report_sect_number(id)
			titlename = base.report_item_get_name(id)
			titlelevel = base.report_sect_level(id)
			base.debugmsg(6, "type:", type, "	titlenum:", titlenum, "	titlename:", titlename, "	titlelevel:", titlelevel)

			numarr = titlenum.split(".")
			base.debugmsg(5, "numarr:", numarr)
			pagenum = int(numarr[0]) + 1
			base.debugmsg(5, "pagenum:", pagenum)

			colnum = 1
			cellname = "{}_{}".format(id, colnum)
			self.contentdata[fid][cellname] = ttk.Label(self.contentdata[fid]["fmeTOC"], text=str(titlenum), style='Report.TLabel')
			self.contentdata[fid][cellname].grid(column=colnum, row=rownum, sticky="nsew")

			colnum += 1
			cellname = "{}_{}".format(id, colnum)
			self.contentdata[fid][cellname] = ttk.Label(self.contentdata[fid]["fmeTOC"], text=str(titlename), style='Report.TLabel')
			self.contentdata[fid][cellname].grid(column=colnum, row=rownum, sticky="nsew")

			colnum += 1
			self.contentdata[fid]["fmeTOC"].columnconfigure(colnum, weight=1)

			colnum += 1
			cellname = "{}_{}".format(id, colnum)
			self.contentdata[fid][cellname] = ttk.Label(self.contentdata[fid]["fmeTOC"], text=str(pagenum), style='Report.TLabel')
			self.contentdata[fid][cellname].grid(column=colnum, row=rownum, sticky="nsew")

			nextrow = rownum + 1

		base.debugmsg(9, "nextrow:", nextrow)
		if level < flevel:
			children = base.report_get_order(id)
			for child in children:
				nextrow = self.cp_contents_row(child, nextrow, fid, fmode, flevel)
		return nextrow

	def cp_note(self, id):
		base.debugmsg(9, "id:", id)
		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ", style='Report.TLabel')
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		notetxt = "{}".format(base.rt_note_get(id))
		self.contentdata[id]["lblNote"] = ttk.Label(self.contentdata[id]["Preview"], text=notetxt, style='Report.TLabel')
		self.contentdata[id]["lblNote"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[id]["Preview"].columnconfigure(1, weight=1)

	def cp_graph(self, id):
		pid, idl, idr = base.rt_graph_LR_Ids(id)
		base.debugmsg(5, "pid:", pid, "	idl:", idl, "	idr:", idr)

		axisenl = base.rt_graph_get_axisen(idl)
		axisenr = base.rt_graph_get_axisen(idr)

		datatypel = base.rt_graph_get_dt(idl)
		datatyper = base.rt_graph_get_dt(idr)

		tz = zoneinfo.ZoneInfo(base.rs_setting_get_timezone())

		if datatypel == "SQL":
			sqll = base.rt_graph_get_sql(idl)
		else:
			sqll = base.rt_graph_generate_sql(idl)
		base.debugmsg(9, "sqll:", sqll)

		if datatyper == "SQL":
			sqlr = base.rt_graph_get_sql(idr)
		else:
			sqlr = base.rt_graph_generate_sql(idr)
		base.debugmsg(9, "sqlr:", sqlr)

		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")
		# self.contentdata[id]["lblSpacer"].config(bg=self.style_reportbg_colour)

		self.contentdata[id]["Preview"].columnconfigure(1, weight=1)
		self.contentdata[id]["Preview"].rowconfigure(rownum, weight=1)

		self.contentdata[id]["fmeGraph"] = tk.Frame(self.contentdata[id]["Preview"])
		# self.contentdata[id]["fmeGraph"].config(bg="green")
		self.contentdata[id]["fmeGraph"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[id]["fmeGraph"].columnconfigure(0, weight=1)
		self.contentdata[id]["fmeGraph"].rowconfigure(0, weight=1)
		self.contentdata[id]["fig_dpi"] = 72
		self.contentdata[id]["fig"] = Figure(dpi=self.contentdata[id]["fig_dpi"])

		self.contentdata[id]["axisL"] = self.contentdata[id]["fig"].add_subplot(1, 1, 1)
		base.debugmsg(8, "axisL:", self.contentdata[id]["axisL"])
		# self.contentdata[id]["axisL"].grid(True, 'major', 'both')
		self.contentdata[id]["axisL"].grid(True, 'major', 'x')
		# base.debugmsg(8, "axisL:", self.contentdata[id]["axisL"])
		self.contentdata[id]["axisR"] = self.contentdata[id]["axisL"].twinx()
		base.debugmsg(8, "axisR:", self.contentdata[id]["axisR"])
		# self.contentdata[id]["axisR"].grid(True, 'major', 'both')
		# base.debugmsg(8, "axisR:", self.contentdata[id]["axisR"])
		self.contentdata[id]["fig"].autofmt_xdate(bottom=0.2, rotation=30, ha='right')

		self.contentdata[id]["canvas"] = FigureCanvasTkAgg(self.contentdata[id]["fig"], self.contentdata[id]["fmeGraph"])
		self.contentdata[id]["canvas"].get_tk_widget().grid(column=0, row=0, sticky="nsew")
		# self.contentdata[id]["canvas"].get_tk_widget().config(bg="blue")

		base.debugmsg(8, "canvas:", self.contentdata[id]["canvas"])
		# base.debugmsg(8, "axis:", self.contentdata[id]["axis"])

		# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tick_params.html
		# self.contentdata[id]["axisL"].grid(True, 'major', 'x')
		# https://matplotlib.org/stable/api/_as_gen/matplotlib.axis.Axis.get_ticklabels.html

		# tckprms = self.contentdata[id]["axisL"].get_tick_params(which='major')
		# base.debugmsg(5, "tckprms:", tckprms)

		self.contentdata[id]["axisL"].tick_params(labelleft=False, length=0)
		self.contentdata[id]["axisR"].tick_params(labelright=False, length=0)

		try:
			self.contentdata[id]["canvas"].draw()
			self.contentdata[id]["fig"].set_tight_layout(True)
		except Exception as e:
			base.debugmsg(5, "canvas.draw() Exception:", e)

		dodraw = False
		self.contentdata[id]["graphdata"] = {}

		if (sqll is not None and len(sqll.strip()) > 0) or (sqlr is not None and len(sqlr.strip()) > 0):
			# Populate Left Y Axis Data
			if sqll is not None and len(sqll.strip()) > 0 and axisenl > 0:
				base.debugmsg(7, "sqll:", sqll)
				key = "{}_{}".format(id, base.report_item_get_changed(idl))
				base.debugmsg(7, "key:", key)
				base.dbqueue["Read"].append({"SQL": sqll, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)
					# base.debugmsg(9, "Waiting for gdata for:", key)

				gdata = base.dbqueue["ReadResult"][key]

				if datatypel == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idl, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in self.contentdata[id]["graphdata"]:
							self.contentdata[id]["graphdata"][name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							self.contentdata[id]["graphdata"][name]["Colour"] = colour
							self.contentdata[id]["graphdata"][name]["Axis"] = "axisL"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							self.contentdata[id]["graphdata"][name]["objTime"] = []
							self.contentdata[id]["graphdata"][name]["Values"] = []

						self.contentdata[id]["graphdata"][name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						self.contentdata[id]["graphdata"][name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			# attempt to Populate right Y Axis Data
			if sqlr is not None and len(sqlr.strip()) > 0 and axisenr > 0:
				base.debugmsg(7, "sqlr:", sqlr)
				key = "{}_{}".format(id, base.report_item_get_changed(idr))
				base.debugmsg(7, "key:", key)
				base.dbqueue["Read"].append({"SQL": sqlr, "KEY": key})
				while key not in base.dbqueue["ReadResult"]:
					time.sleep(0.1)
					# base.debugmsg(9, "Waiting for gdata for:", key)

				gdata = base.dbqueue["ReadResult"][key]

				if datatyper == "Plan":
					base.debugmsg(9, "gdata before:", gdata)
					gdata = base.graph_postprocess_data_plan(idr, gdata)

				base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						base.debugmsg(9, "name:", name)
						if name not in self.contentdata[id]["graphdata"]:
							self.contentdata[id]["graphdata"][name] = {}

							colour = base.named_colour(name)
							base.debugmsg(8, "name:", name, "	colour:", colour)
							self.contentdata[id]["graphdata"][name]["Colour"] = colour
							self.contentdata[id]["graphdata"][name]["Axis"] = "axisR"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							self.contentdata[id]["graphdata"][name]["objTime"] = []
							self.contentdata[id]["graphdata"][name]["Values"] = []

						self.contentdata[id]["graphdata"][name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						self.contentdata[id]["graphdata"][name]["Values"].append(base.rt_graph_floatval(row["Value"]))
					else:
						break

			base.debugmsg(8, "self.contentdata[id][graphdata]:", self.contentdata[id]["graphdata"])

			for name in self.contentdata[id]["graphdata"]:
				base.debugmsg(7, "name:", name)
				axis = "axisL"
				if "Axis" in self.contentdata[id]["graphdata"][name]:
					axis = self.contentdata[id]["graphdata"][name]["Axis"]

				if len(self.contentdata[id]["graphdata"][name]["Values"]) > 1 and len(self.contentdata[id]["graphdata"][name]["Values"]) == len(self.contentdata[id]["graphdata"][name]["objTime"]):
					try:
						self.contentdata[id][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name)
						# self.contentdata[id]["axis"][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name)
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

				if len(self.contentdata[id]["graphdata"][name]["Values"]) == 1 and len(self.contentdata[id]["graphdata"][name]["Values"]) == len(self.contentdata[id]["graphdata"][name]["objTime"]):
					try:
						self.contentdata[id][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name, marker='o')
						# self.contentdata[id]["axis"][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name, marker='o')
						dodraw = True
					except Exception as e:
						base.debugmsg(7, "axis.plot() Exception:", e)

			if dodraw:

				# Left axis Limits
				if axisenl > 0:
					self.contentdata[id]["axisL"].grid(True, 'major', 'y')
					self.contentdata[id]["axisL"].tick_params(labelleft=True, length=5)

					SMetric = "Other"
					if datatypel == "Metric":
						SMetric = base.rt_table_get_sm(idl)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						self.contentdata[id]["axisL"].set_ylim(0, 100)
					else:
						self.contentdata[id]["axisL"].set_ylim(0)

				# Right axis Limits
				if axisenr > 0:
					self.contentdata[id]["axisR"].grid(True, 'major', 'y')
					self.contentdata[id]["axisR"].tick_params(labelright=True, length=5)

					SMetric = "Other"
					if datatyper == "Metric":
						SMetric = base.rt_table_get_sm(idr)
					base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						self.contentdata[id]["axisR"].set_ylim(0, 100)
					else:
						self.contentdata[id]["axisR"].set_ylim(0)

				self.contentdata[id]["fig"].set_tight_layout(True)
				self.contentdata[id]["fig"].autofmt_xdate(bottom=0.2, rotation=30, ha='right')
				try:
					self.contentdata[id]["canvas"].draw()
				except Exception as e:
					base.debugmsg(5, "canvas.draw() Exception:", e)

	def cp_table(self, id):
		base.debugmsg(9, "id:", id)
		datatype = base.rt_table_get_dt(id)
		if datatype == "SQL":
			sql = base.rt_table_get_sql(id)
		else:
			sql = base.rt_table_generate_sql(id)
			base.debugmsg(5, "sql:", sql)
		colours = base.rt_table_get_colours(id)
		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")
		if sql is not None and len(sql.strip()) > 0:
			base.debugmsg(8, "sql:", sql)
			key = "{}_{}".format(id, base.report_item_get_changed(id))
			base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
			while key not in base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = base.dbqueue["ReadResult"][key]
			# table_postprocess_data_plan
			if datatype == "Plan":
				base.debugmsg(9, "tdata before:", tdata)
				tdata = base.table_postprocess_data_plan(id, tdata)
			base.debugmsg(8, "tdata:", tdata)

			# self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text=notetxt)
			# self.contentdata[id]["lblSpacer"].grid(column=1, row=rownum, sticky="nsew")

			if len(tdata) > 0:
				cols = list(tdata[0].keys())
				base.debugmsg(7, "cols:", cols)

				if colours:
					cellname = "h_{}".format("colours")
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=" ", style='Report.THead.TLabel')
					self.contentdata[id][cellname].grid(column=1, row=rownum, sticky="nsew")

				colnum = 1 + colours
				for col in cols:
					if col not in ["Colour"]:
						show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
						if show:
							cellname = "h_{}".format(col)
							base.debugmsg(9, "cellname:", cellname)
							dispname = base.rt_table_get_colname(id, col)
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{} ".format(dispname.strip()), style='Report.THead.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")
							colnum += 1
				i = 0
				for row in tdata:
					i += 1
					rownum += 1
					colnum = 0
					if colours:
						colnum += 1
						cellname = "{}_{}".format(i, "colour")
						# self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="  ")
						self.contentdata[id][cellname] = tk.Label(self.contentdata[id]["Preview"], text="  ")
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						base.debugmsg(9, "row:", row)
						if "Colour" in row:
							label = row["Colour"]
						else:
							label = row[cols[0]]
						base.debugmsg(9, "label:", label)
						colour = base.named_colour(label)
						base.debugmsg(9, "colour:", colour)
						# self.contentdata[id][cellname].config(background=colour)
						self.contentdata[id][cellname].config(bg=colour)

					for col in cols:
						if col not in ["Colour"]:
							show = base.report_item_get_bool_def1(id, base.rt_table_ini_colname(f"{col} Show"))
							if show:
								colnum += 1
								cellname = "{}_{}".format(i, col)
								base.debugmsg(9, "cellname:", cellname)
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(row[col]), style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

	def cp_errors(self, id):
		base.debugmsg(5, "id:", id)
		showimages = base.rt_errors_get_images(id)
		base.debugmsg(5, "showimages:", showimages)
		grouprn = base.rt_errors_get_group_rn(id)
		base.debugmsg(5, "grouprn:", grouprn)
		groupet = base.rt_errors_get_group_et(id)
		base.debugmsg(5, "groupet:", groupet)

		lbl_Result = base.rt_errors_get_label(id, "lbl_Result")
		lbl_Test = base.rt_errors_get_label(id, "lbl_Test")
		lbl_Script = base.rt_errors_get_label(id, "lbl_Script")
		lbl_Error = base.rt_errors_get_label(id, "lbl_Error")
		lbl_Count = base.rt_errors_get_label(id, "lbl_Count")
		lbl_Screenshot = base.rt_errors_get_label(id, "lbl_Screenshot")
		lbl_NoScreenshot = base.rt_errors_get_label(id, "lbl_NoScreenshot")

		pctalike = 0.80
		base.debugmsg(5, "pctalike:", pctalike)

		base.rt_errors_get_data(id)
		if 'data' not in self.contentdata[id]:
			# edata = base.rt_errors_get_data(id)
			# self.contentdata[id]['data'] = edata
			self.contentdata[id]['data'] = {}

		base.debugmsg(5, "self.contentdata[", id, "]['data']:", self.contentdata[id]['data'])
		base.debugmsg(5, "base.reportdata[", id, "]:", base.reportdata[id])

		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		if grouprn or groupet:
			self.contentdata[id]["grpdata"] = {}
			self.contentdata[id]["grpdata"]["resultnames"] = {}
			self.contentdata[id]["grpdata"]["errortexts"] = {}

			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = base.reportdata[id][key]

					if grouprn:
						result_name = rdata['result_name']
						matches = difflib.get_close_matches(result_name, list(self.contentdata[id]["grpdata"]["resultnames"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							result_name = matches[0]
							basekey = self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"][0]
							base.debugmsg(5, "basekey:", basekey)
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"].append(key)
						else:
							self.contentdata[id]["grpdata"]["resultnames"][result_name] = {}
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"] = []
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"].append(key)
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"] = {}

						if groupet and 'error' in rdata:
							errortext = rdata['error']
							# errortext_sub = errortext.split(r'\n')[0]
							errortext_sub = errortext.splitlines()[0]
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							matcheset = difflib.get_close_matches(errortext_sub, list(self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"].keys()), cutoff=pctalike)
							base.debugmsg(5, "matcheset:", matcheset)
							if len(matcheset) > 0:
								errortext = matcheset[0]
								errortext_sub = errortext.splitlines()[0]
								base.debugmsg(5, "errortext:", errortext)
								baseid = self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"][0]
								base.debugmsg(5, "baseid:", baseid)
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)
							else:
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub] = {}
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"] = []
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)

					if groupet and 'error' in rdata:
						errortext = rdata['error']
						errortext_sub = errortext.splitlines()[0]
						base.debugmsg(5, "errortext_sub:", errortext_sub)
						matches = difflib.get_close_matches(errortext_sub, list(self.contentdata[id]["grpdata"]["errortexts"].keys()), cutoff=pctalike)
						base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							errortext = matches[0]
							base.debugmsg(5, "errortext:", errortext)
							baseid = self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"][0]
							base.debugmsg(5, "baseid:", baseid)
							self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"].append(key)
						else:
							base.debugmsg(5, "errortext_sub:", errortext_sub)
							self.contentdata[id]["grpdata"]["errortexts"][errortext_sub] = {}
							self.contentdata[id]["grpdata"]["errortexts"][errortext_sub]["keys"] = []
							self.contentdata[id]["grpdata"]["errortexts"][errortext_sub]["keys"].append(key)

			resultnames = self.contentdata[id]["grpdata"]["resultnames"]
			base.debugmsg(5, "resultnames:", resultnames)
			errortexts = self.contentdata[id]["grpdata"]["errortexts"]
			base.debugmsg(5, "errortexts:", errortexts)

		if grouprn:
			# self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"]
			for result_name in list(self.contentdata[id]["grpdata"]["resultnames"].keys()):
				basekey = self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]
				rownum += 1

				colnum = 0
				cellname = "{}_{}".format("result_name_lbl", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Result), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("result_name", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(result_name), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("test_name_lbl", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Test), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("test_name", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['test_name']), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("script_lbl", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Script), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("script", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['script']), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("count_lbl", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("countdisp", basekey)
				base.debugmsg(5, "cellname:", cellname)
				count = len(self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"])
				base.debugmsg(5, "count:", count)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				if groupet:
					# self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"]
					for errortext in list(self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"].keys()):
						basekey = self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"][0]
						base.debugmsg(5, "basekey:", basekey)
						rdata = base.reportdata[id][basekey]
						rownum += 1
						colnum = 0
						cellname = "{}_{}".format("error_lbl", basekey)
						base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("error", basekey)
						base.debugmsg(5, "cellname:", cellname)
						if 'error' in rdata:
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

						colnum += 5
						cellname = "{}_{}".format("ecount_lbl", basekey)
						base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Count), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("ecountdisp", basekey)
						base.debugmsg(5, "cellname:", cellname)
						count = len(self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"])
						base.debugmsg(5, "count:", count)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(count), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						if showimages:
							rownum += 1
							colnum = 0
							cellname = "{}_{}".format("screenshot_lbl", basekey)
							base.debugmsg(5, "cellname:", cellname)
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

							colnum += 1
							cellname = "{}_{}".format("screenshot", basekey)
							cellimg = "{}_{}".format("image", basekey)
							base.debugmsg(5, "cellname:", cellname)
							if 'image_file' in rdata:
								self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)
							else:
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

				else:
					for keyi in self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"]:
						rdata = base.reportdata[id][keyi]

						rownum += 1
						colnum = 0
						cellname = "{}_{}".format("error_lbl", keyi)
						base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("error", keyi)
						base.debugmsg(5, "cellname:", cellname)
						if 'error' in rdata:
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

						if showimages:
							rownum += 1
							colnum = 0
							cellname = "{}_{}".format("screenshot_lbl", keyi)
							base.debugmsg(5, "cellname:", cellname)
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

							colnum += 1
							cellname = "{}_{}".format("screenshot", keyi)
							cellimg = "{}_{}".format("image", keyi)
							base.debugmsg(5, "cellname:", cellname)
							if 'image_file' in rdata:
								self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)
							else:
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

		if groupet and not grouprn:

			# baseid = self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"][0]
			for errortext in list(self.contentdata[id]["grpdata"]["errortexts"].keys()):
				basekey = self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"][0]
				base.debugmsg(5, "basekey:", basekey)
				rdata = base.reportdata[id][basekey]
				rownum += 1
				colnum = 0
				cellname = "{}_{}".format("error_lbl", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("error", basekey)
				base.debugmsg(5, "cellname:", cellname)
				if 'error' in rdata:
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

				colnum += 5
				cellname = "{}_{}".format("ecount_lbl", basekey)
				base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("ecountdisp", basekey)
				base.debugmsg(5, "cellname:", cellname)
				count = len(self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"])
				base.debugmsg(5, "count:", count)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				if showimages:
					rownum += 1
					colnum = 0
					cellname = "{}_{}".format("screenshot_lbl", basekey)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("screenshot", basekey)
					cellimg = "{}_{}".format("image", basekey)
					base.debugmsg(5, "cellname:", cellname)
					if 'image_file' in rdata:
						self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)
					else:
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

		if not grouprn and not groupet:
			i = 0
			keys = list(base.reportdata[id].keys())
			for key in keys:
				base.debugmsg(5, "key:", key)
				if key != "key":
					i += 1
					rownum += 1
					rdata = base.reportdata[id][key]

					colnum = 0
					cellname = "{}_{}".format("lbl_result_name", key)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Result), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("result_name", key)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['result_name']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("lbl_test_name", key)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Test), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("test_name", key)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['test_name']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("lbl_script", key)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Script), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("script", key)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['script']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					rownum += 1
					colnum = 0
					cellname = "{}_{}".format("lbl_error", key)
					base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("error", key)
					base.debugmsg(5, "cellname:", cellname)
					if 'error' in rdata:
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

					if showimages:
						rownum += 1
						colnum = 0
						cellname = "{}_{}".format("lbl_image", key)
						base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("image_file", key)
						cellimg = "{}_{}".format("image", key)
						base.debugmsg(5, "cellname:", cellname)
						if 'image_file' in rdata:
							self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)
						else:
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

	#
	# Export content generation functions
	#

	def cg_export_xhtml(self):
		# base.debugmsg(5, "Not implimented yet.....")
		core.export_xhtml()

	def cg_export_pdf(self):
		base.debugmsg(5, "Not implimented yet.....")
		core.export_pdf()

	def cg_export_writer(self):
		base.debugmsg(5, "Not implimented yet.....")
		core.export_writer()

	def cg_export_word(self):
		# base.debugmsg(5, "Not implimented yet.....")
		core.export_word()

	def cg_export_calc(self):
		base.debugmsg(5, "Not implimented yet.....")
		core.export_calc()

	def cg_export_excel(self):
		base.debugmsg(5, "Not implimented yet.....")
		core.export_excel()

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# menu functions
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def mnu_do_nothing(self, _event=None):
		base.debugmsg(5, "Not implimented yet.....")

	def mnu_results_Open(self, _event=None):
		base.debugmsg(9, "mnu_file_Open: _event:", _event, "	Type:", type(_event))

		# E721 do not compare types, use 'isinstance()'
		# if type(_event) is not type(""):
		if not isinstance(_event, str):
			# self.mnu_file_Close()	# ensure any previous scenario is closed and saved if required
			ResultsFile = str(
				tkf.askopenfilename(
					initialdir=base.config['Reporter']['ResultDir'],
					title="Select RFSwarm Results File",
					filetypes=(("RFSwarm Results", "*.db"), ("all files", "*.*"))
				)
			)
		else:
			ResultsFile = _event

		base.debugmsg(5, "ResultsFile:", ResultsFile)

		# ['Reporter']['Results']
		if len(ResultsFile) > 0:

			base.report = None
			self.contentdata = {}
			core.selectResults(ResultsFile)
			base.report_open()
			self.updateTitle()
			self.updateResults()
			base.debugmsg(5, "LoadSections")
			self.LoadSections("TOP")
			base.debugmsg(5, "content_load")
			self.content_load("TOP")

	def mnu_template_New(self, _event=None):
		base.debugmsg(5, "New Report Template")

		base.template_create()

		self.LoadSections("TOP")

		self.updateTemplate()

	def mnu_template_Open(self, _event=None):
		TemplateFile = str(
			tkf.askopenfilename(
				initialdir=base.config['Reporter']['TemplateDir'],
				title="Select RFSwarm Reporter Template",
				filetypes=(("RFSwarm Reporter Template", "*.template"), ("all files", "*.*"))
			)
		)
		base.debugmsg(5, "TemplateFile:", TemplateFile)

		# ['Reporter']['Results']
		if len(TemplateFile) > 0:
			base.report = None
			self.contentdata = {}
			base.debugmsg(5, "template_open TemplateFile:", TemplateFile)
			base.template_open(TemplateFile)
			base.debugmsg(5, "report_save")
			base.report_save()
			base.debugmsg(5, "ConfigureStyle")
			self.ConfigureStyle()
			base.debugmsg(5, "LoadSections")
			self.LoadSections("TOP")
			base.debugmsg(5, "content_load")
			self.content_load("TOP")
			base.debugmsg(5, "updateTemplate")
			self.updateTemplate()
			# base.debugmsg(5, "cp_regenerate_preview")
			# self.cp_regenerate_preview()
			base.debugmsg(5, "done")

	def mnu_template_Save(self, _event=None):
		# base.debugmsg(5, "Not implimented yet.....")
		templatefile = base.whitespace_get_ini_value(base.config['Reporter']['Template'])
		base.debugmsg(5, "Filename:", templatefile)
		if len(templatefile) > 0:
			base.template_save(templatefile)
			self.updateTemplate()
		else:
			self.mnu_template_SaveAs()

	def mnu_template_SaveAs(self, _event=None):
		base.debugmsg(5, "Prompt for filename")
		templatefile = str(
			tkf.asksaveasfilename(
				initialdir=base.config['Reporter']['TemplateDir'],
				title="Save RFSwarm Reporter Template",
				filetypes=(("Template", "*.template"), ("all files", "*.*")),
				defaultextension=".template"
			)
		)
		base.debugmsg(5, "templatefile", templatefile)
		base.template_save(templatefile)
		self.updateTemplate()

	def mnu_new_rpt_sect(self):
		selected = self.sectionstree.focus()
		base.debugmsg(5, "selected:", selected)
		name = tksd.askstring(title="New Section", prompt="Section Name:")
		# , bg=self.style_feild_colour	, background='green'
		if name is not None and len(name) > 0:
			if selected is None or len(selected) < 1:
				selected = "TOP"
			id = base.report_new_section(selected, name)
			self.LoadSection(selected, id)

	def mnu_rem_rpt_sect(self):
		selected = self.sectionstree.focus()
		base.debugmsg(5, "selected:", selected)
		if selected:
			base.debugmsg(5, "Removing:", base.whitespace_get_ini_value(base.report[selected]["Name"]))
			base.report_remove_section(selected)
			parent = base.report_item_parent(selected)
			self.LoadSections(parent)

	def mnu_rpt_sect_up(self):
		selected = self.sectionstree.focus()
		base.debugmsg(5, "selected:", selected)
		if selected:
			base.debugmsg(5, "Moving", base.whitespace_get_ini_value(base.report[selected]["Name"]), "up")
			base.report_move_section_up(selected)
			parent = base.report_item_parent(selected)
			self.LoadSections(parent)
			self.sectionstree.selection_set(selected)
			self.sectionstree.focus(selected)

	def mnu_rpt_sect_down(self):
		selected = self.sectionstree.focus()
		base.debugmsg(5, "selected:", selected)
		if selected:
			base.debugmsg(5, "Moving", base.whitespace_get_ini_value(base.report[selected]["Name"]), "down")
			base.report_move_section_down(selected)
			parent = base.report_item_parent(selected)
			self.LoadSections(parent)
			self.sectionstree.selection_set(selected)
			self.sectionstree.focus(selected)

	def mnu_content_settings(self):
		base.debugmsg(5, "Not implimented yet.....")
		# self.button0.config(state=tk.DISABLED)
		# self.cbbar.bprev.config(state=tk.NORMAL)
		# self.cbbar.bsett.config(state=tk.ACTIVE)
		# self.cbbar.bprev.config(relief=tk.RAISED)
		# self.cbbar.bsett.config(relief=tk.FLAT)

	def mnu_content_preview(self):
		base.debugmsg(5, "Not implimented yet.....")
		# self.cbbar.bprev.config(relief=tk.FLAT)
		# self.cbbar.bsett.config(relief=tk.RAISED)
		# self.cbbar.bprev.config(state=tk.ACTIVE)
		# self.cbbar.bsett.config(state=tk.NORMAL)

	# Export Functions
	def mnu_export_html(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		cghtml = threading.Thread(target=self.cg_export_xhtml)
		cghtml.start()

	def mnu_export_pdf(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		cgpdf = threading.Thread(target=self.cg_export_pdf)
		cgpdf.start()

	def mnu_export_writer(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		cgwriter = threading.Thread(target=self.cg_export_writer)
		cgwriter.start()

	def mnu_export_word(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		cgword = threading.Thread(target=self.cg_export_word)
		cgword.start()

	def mnu_export_calc(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		cgcalc = threading.Thread(target=self.cg_export_calc)
		cgcalc.start()

	def mnu_export_excel(self, _event=None):
		base.debugmsg(5, "_event:", _event)
		cgxcel = threading.Thread(target=self.cg_export_excel)
		cgxcel.start()


class RFSwarm():

	running = True

	def __init__(self):
		while base.running:
			# time.sleep(300)
			time.sleep(1)


base = ReporterBase()

core = ReporterCore()

core.mainloop()

# r = RFSwarm_Reporter()
