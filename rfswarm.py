#!/usr/bin/python
#
#	Robot Framework Swarm
#
#    Version v0.4.3-alpha
#

# 	Helpful links
#
# 	making things resize with the window	https://stackoverflow.com/questions/7591294/how-to-create-a-self-resizing-grid-of-buttons-in-tkinter
#


import sys
import signal
import os
import glob
import configparser
import hashlib
import lzma
import base64
import sqlite3

# import robot

import socket
import random
import time
from datetime import datetime
import re
import threading
import subprocess
from operator import itemgetter

import xml.etree.ElementTree as ET


# import Tkinter as tk				#python2
import tkinter as tk				#python3
# import ttk						#python2
import tkinter.ttk as ttk			#python3
# import tkFileDialog as tkf		#python2
import tkinter.filedialog as tkf	#python3
import tkinter.messagebox as tkm	#python3


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
import urllib.parse
import json



__name__ = "rfswarm"

class percentile:
	def __init__(self):
		self.count = 0
		self.percent = 90
		self.values = []

	def step(self, value, percent):
		self.count += 1
		self.values.append(value)
		self.percent = percent

	def finalize(self):
		try:
			if self.count <10:
				# Need at least 10 samples to get a useful percentile
				return None
			# print("percentile: finalize: self.count:", self.count, "	self.percent:", self.percent, "	self.values:", self.values)
			nth = self.count * (self.percent/100)
			# print("percentile: finalize: nth:", nth)
			nthi = int(nth)
			# nthi = int(math.ceil(self.count * (self.percent/100)))
			self.values.sort()
			# print("percentile: finalize: nthi:", nthi, "	self.values[nthi]:", self.values[nthi], "	self.values:", self.values)
			return self.values[nthi]
			# return self.count
		except:
			return None

class AgentServer(BaseHTTPRequestHandler):
	def do_HEAD(self):
		return
	def do_POST(self):
		httpcode = 200
		try:
			parsed_path = urllib.parse.urlparse(self.path)
			if (parsed_path.path in ["/AgentStatus", "/Jobs", "/Scripts", "/File", "/Result"]):

				jsonresp = {}
				rawData = (self.rfile.read(int(self.headers['content-length']))).decode('utf-8')
				# print("parsed_path.path", parsed_path.path)
				if (parsed_path.path == "/AgentStatus"):
					jsonreq = json.loads(rawData)

					requiredfields = ["AgentName", "Status", "Robots", "CPU%", "MEM%", "NET%"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							break

					if httpcode == 200:
						# print("jsonreq", jsonreq)
						rfs.register_agent(jsonreq)
						jsonresp["AgentName"] = jsonreq["AgentName"]
						jsonresp["Status"] = "Updated"

				if (parsed_path.path == "/Scripts"):
					jsonreq = json.loads(rawData)
					requiredfields = ["AgentName"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							break

					if httpcode == 200:
						jsonresp["AgentName"] = jsonreq["AgentName"]
						# print("rfs.scriptlist:", rfs.scriptlist)

						scripts = []
						# print("rfs.scriptfiles:", rfs.scriptfiles)
						for hash in rfs.scriptfiles:
							# print("hash:", hash, rfs.scriptfiles[hash])
							scripts.append({'File': rfs.scriptfiles[hash]['relpath'], "Hash": hash})
						# print("scripts:", scripts)
						jsonresp["Scripts"] = scripts

				if (parsed_path.path == "/File"):
					jsonreq = json.loads(rawData)

					requiredfields = ["AgentName", "Hash"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							break

					if httpcode == 200:

						jsonresp["AgentName"] = jsonreq["AgentName"]
						if "Hash" in jsonreq and len(jsonreq["Hash"])>0:
							hash = jsonreq["Hash"]
							jsonresp["Hash"] = jsonreq["Hash"]
							jsonresp["File"] = rfs.scriptfiles[hash]['relpath']
							localpath = rfs.scriptfiles[hash]['localpath']
							buf = "\n"
							with open(localpath, 'rb') as afile:
							    buf = afile.read()
							# print("buf:", buf)
							compressed = lzma.compress(buf)
							# print("compressed:", compressed)
							encoded = base64.b64encode(compressed)
							# print("encoded:", encoded)

							jsonresp["FileData"] = encoded.decode('ASCII')

						else:
							httpcode = 404
							jsonresp["Message"] = "Known File Hash required to download a file"

				if (parsed_path.path == "/Jobs"):
					jsonreq = json.loads(rawData)

					requiredfields = ["AgentName"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							break

					if httpcode == 200:

						jsonresp["AgentName"] = jsonreq["AgentName"]
						jsonresp["StartTime"] = rfs.run_start
						jsonresp["EndTime"] = rfs.run_end
						jsonresp["RunName"] = rfs.robot_schedule["RunName"]

						# self.robot_schedule["Agents"]
						if jsonresp["AgentName"] in rfs.robot_schedule["Agents"].keys():
							jsonresp["Schedule"] = rfs.robot_schedule["Agents"][jsonresp["AgentName"]]
						else:
							jsonresp["Schedule"] = {}


				# , "Result"
				if (parsed_path.path == "/Result"):
					jsonreq = json.loads(rawData)
					requiredfields = ["AgentName", "ResultName", "Result", "ElapsedTime", "StartTime", "EndTime", "ScriptIndex", "VUser", "Iteration", "Sequence"]
					for field in requiredfields:
						if field not in jsonreq:
							httpcode = 422
							message = "Missing required field: '{}', required fields are: {}".format(field, requiredfields)
							break

					if httpcode == 200:
						jsonresp["AgentName"] = jsonreq["AgentName"]

						rfs.register_result(jsonreq["AgentName"], jsonreq["ResultName"], jsonreq["Result"],
									jsonreq["ElapsedTime"], jsonreq["StartTime"], jsonreq["EndTime"],
									jsonreq["ScriptIndex"], jsonreq["VUser"], jsonreq["Iteration"],
									jsonreq["Sequence"])

						jsonresp["Result"] = "Queued"

				# print("do_POST: jsonresp:", jsonresp)
				message = json.dumps(jsonresp)
			else:
				httpcode = 404
				message = "Unrecognised request: '{}'".format(parsed_path)

		except Exception as e:
			httpcode = 500
			message = str(e)
		self.send_response(httpcode)
		self.end_headers()
		self.wfile.write(bytes(message,"utf-8"))
		return
	def do_GET(self):
		httpcode = 200
		try:
			parsed_path = urllib.parse.urlparse(self.path)
			if (parsed_path.path == '/'):
				jsonresp = {}

				jsonresp["POST"] = {}
				jsonresp["POST"]["AgentStatus"] = {}
				jsonresp["POST"]["AgentStatus"]["URI"] = "/AgentStatus"
				jsonresp["POST"]["AgentStatus"]["Body"] = {}
				jsonresp["POST"]["AgentStatus"]["Body"]["AgentName"] = "<Agent Host Name>"
				jsonresp["POST"]["AgentStatus"]["Body"]["Status"] = "<Agent Status>"
				jsonresp["POST"]["AgentStatus"]["Body"]["AgentIPs"] = ["<Agent IP Address>","<Agent IP Address>"]
				jsonresp["POST"]["AgentStatus"]["Body"]["Robots"] = "<sum>"
				jsonresp["POST"]["AgentStatus"]["Body"]["CPU%"] = "0-100"
				jsonresp["POST"]["AgentStatus"]["Body"]["MEM%"] = "0-100"
				jsonresp["POST"]["AgentStatus"]["Body"]["NET%"] = "0-100"

				jsonresp["POST"]["Jobs"] = {}
				jsonresp["POST"]["Jobs"]["URI"] = "/Jobs"
				jsonresp["POST"]["Jobs"]["Body"] = {}
				jsonresp["POST"]["Jobs"]["Body"]["AgentName"] = "<Agent Host Name>"

				jsonresp["POST"]["Scripts"] = {}
				jsonresp["POST"]["Scripts"]["URI"] = "/Scripts"
				jsonresp["POST"]["Scripts"]["Body"] = {}
				jsonresp["POST"]["Scripts"]["Body"]["AgentName"] = "<Agent Host Name>"

				jsonresp["POST"]["File"] = {}
				jsonresp["POST"]["File"]["URI"] = "/File"
				jsonresp["POST"]["File"]["Body"] = {}
				jsonresp["POST"]["File"]["Body"]["AgentName"] = "<Agent Host Name>"
				jsonresp["POST"]["File"]["Body"]["Hash"] = "<File Hash, provided by /Scripts>"

				jsonresp["POST"]["Result"] = {}
				jsonresp["POST"]["Result"]["URI"] = "/Result"
				jsonresp["POST"]["Result"]["Body"] = {}
				jsonresp["POST"]["Result"]["Body"]["AgentName"] = "<Agent Host Name>"
				jsonresp["POST"]["Result"]["Body"]["ResultName"] = "<A Text String>"
				jsonresp["POST"]["Result"]["Body"]["Result"] = "<PASS | FAIL>"
				jsonresp["POST"]["Result"]["Body"]["ElapsedTime"] = "<seconds as decimal number>"
				jsonresp["POST"]["Result"]["Body"]["StartTime"] = "<epoch seconds as decimal number>"
				jsonresp["POST"]["Result"]["Body"]["EndTime"] = "<epoch seconds as decimal number>"
				jsonresp["POST"]["Result"]["Body"]["ScriptIndex"] = "<Index>"
				jsonresp["POST"]["Result"]["Body"]["VUser"] = "<user number>"
				jsonresp["POST"]["Result"]["Body"]["Iteration"] = "<iteration number>"
				jsonresp["POST"]["Result"]["Body"]["Sequence"] = "<sequence number that ResultName occurred in test case>"

				message = json.dumps(jsonresp)
			else:
				httpcode = 404
				message = "Unrecognised request: '{}'".format(parsed_path)
		except Exception as e:
			httpcode = 500
			message = str(e)

		self.send_response(httpcode)
		self.end_headers()
		self.wfile.write(bytes(message,"utf-8"))
		return
	def handle_http(self):
		return
	def respond(self):
		return

	# 	log_request is here to stop BaseHTTPRequestHandler logging to the console
	# 		https://stackoverflow.com/questions/10651052/how-to-quiet-simplehttpserver/10651257#10651257
	def log_request(self, code='-', size='-'):
		pass


class RFSwarmGUI(tk.Frame):
	version = "v0.4.3-alpha"
	index = ""
	file = ""
	sheet = ""
	titleprefix = 'Robot Framework Swarm'

	tabs = None

	config = None
	gui_ini = None

	# #000000 = Black
	defcolours = ['#000000']

	pln_graph = None
	scriptgrid = None
	scriptcount = 0
	scriptlist = [{}]
	scriptfiles = {}
	agenttgrid = None
	agenttgridupdate = 0

	rungrid = None
	rungridupdate = 0

	run_name = ""
	run_name_current = ""
	run_start = 0
	run_end = 0
	run_paused = False
	run_threads = {}
	total_robots = 0
	robot_schedule = {"RunName": "", "Agents": {}, "Scripts": {}}
	agentserver = None
	agenthttpserver = None
	updatethread = None

	Agents = {}

	plan_scnro_chngd = False

	plancolidx = 0
	plancolusr = 1
	plancoldly = 2
	plancolrmp = 3
	plancolrun = 4
	plancolnme = 5
	plancolscr = 6
	plancoltst = 7
	plancoladd = 99

	display_agents = {}
	display_run = {}
	imgdata = {}


	imgdata = {}

	dir_path = os.path.dirname(os.path.realpath(__file__))
	resultsdir = ""
	run_dbthread = True
	dbthread = None
	datapath = ""
	dbfile = ""
	datadb = None
	dbqueue = {"Write": [], "Read": [], "ReadResult": {}, "Agents": [], "Results": []}

	def __init__(self, master=None):
		root = tk.Tk()
		# Grid.rowconfigure(root, 0, weight=1)
		# Grid.columnconfigure(root, 0, weight=1)
		root.protocol("WM_DELETE_WINDOW", self.on_closing)

		self.config = configparser.ConfigParser()
		scrdir = os.path.dirname(__file__)
		# print("RFSwarmGUI: __init__: scrdir: ", scrdir)
		self.gui_ini = os.path.join(scrdir, "RFSwarmGUI.ini")
		if os.path.isfile(self.gui_ini):
			# print("RFSwarmGUI: __init__: agentini: ", self.gui_ini)
			self.config.read(self.gui_ini)
		else:
			self.saveini()

		tk.Frame.__init__(self, root)
		self.grid(row=0, column=0, sticky="nsew")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.BuildUI()
		# self.pln_update_graph()
		self.agentserver = threading.Thread(target=self.run_agent_server)
		self.agentserver.start()
		self.run_dbthread = True
		self.dbthread = threading.Thread(target=self.run_db_thread)
		self.dbthread.start()

	def updateTitle(self):
		titletext = "{} - {}".format(self.titleprefix, "Untitled")
		if 'Plan' in self.config and 'ScenarioFile' in self.config['Plan']:
			if len(self.config['Plan']['ScenarioFile'])>0:
				titletext = "{} - {}".format(self.titleprefix, self.config['Plan']['ScenarioFile'])

		self.master.title(titletext)

	def saveini(self):
		with open(self.gui_ini, 'w') as configfile:    # save
		    self.config.write(configfile)

	# def mainloop(self):
	# 	pass

	def on_closing(self, _event=None):
		# , _event=None is required for any function that has a shortcut key bound to it

		print("on_closing: Close Scenario")
		sf = self.config['Plan']['ScenarioFile']
		self.mnu_file_Close()
		# mnu_file_Close clears this value, need to set it back so that it is saved
		# 		in the ini file so the next app open loads the file
		self.config['Plan']['ScenarioFile'] = sf

		print("on_closing: self.destroy")
		self.destroy()
		print("on_closing: Shutdown Agent Server")
		self.agenthttpserver.shutdown()
		# print("Join Update Agent Thread")
		# self.updatethread.join()
		print("on_closing: Join Agent Server Thread")
		self.agentserver.join()

		# if self.datadb is not None:
		# 	print("on_closing: Disconnect and close DB")
		# 	self.datadb.commit()
		# 	self.datadb.close()
		self.run_dbthread = False
		print("on_closing: Join DB Thread")
		self.dbthread.join()

		print("on_closing: Save ini File")
		self.saveini()

		print("on_closing: exit")
		exit()

	def BuildUI(self):
		minx = 500
		miny = 200
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		self.tabs = ttk.Notebook(self)
		p = ttk.Frame(self.tabs)   # first page, which would get widgets gridded into it
		p.grid(row=0, column=0, sticky="nsew")
		r = ttk.Frame(self.tabs)   # second page
		r.grid(row=0, column=0, sticky="nsew")
		a = ttk.Frame(self.tabs)   # 3rd page
		a.grid(row=0, column=0, sticky="nsew")
		self.tabs.add(p, text='Plan')
		self.tabs.add(r, text='Run')
		self.tabs.add(a, text='Agents')
		self.tabs.grid(column=0, row=0) # , sticky="nsew")

		self.BuildMenu()
		self.BuildPlan(p)
		self.BuildRun(r)
		self.BuildAgent(a)

	def BuildMenu(self):
		# creating a root menu to insert all the sub menus
		window = self.master
		root_menu = tk.Menu(window)
		window.config(menu = root_menu)

			# sub_menu.add_command(label="Print", command=self.print_, accelerator="Command-P")
			# https://stackoverflow.com/questions/16847584/how-do-i-get-the-mac-command-symbol-in-a-tkinter-menu

		# creating sub menus in the root menu
		file_menu = tk.Menu(root_menu) # it intializes a new su menu in the root menu
		root_menu.add_cascade(label = "File", menu = file_menu) # it creates the name of the sub menu

		accelkey = "Ctrl"
		if sys.platform.startswith('darwin'):
			accelkey = "Command"

		file_menu.add_command(label = "New", command = self.mnu_file_New, accelerator="{}-n".format(accelkey)) # it adds a option to the sub menu 'command' parameter is used to do some action
		window.bind('n', self.mnu_file_New)
		file_menu.add_command(label = "Open", command = self.mnu_file_Open, accelerator="{}-o".format(accelkey))
		window.bind('o', self.mnu_file_Open)
		file_menu.add_command(label = "Save", command = self.mnu_file_Save, accelerator="{}-s".format(accelkey))
		window.bind('s', self.mnu_file_Save)
		file_menu.add_command(label = "Save As", command = self.mnu_file_SaveAs, accelerator="{}-a".format(accelkey))
		window.bind('a', self.mnu_file_SaveAs)
		file_menu.add_command(label = "Close", command = self.mnu_file_Close, accelerator="{}-l".format(accelkey))
		window.bind('l', self.mnu_file_Close)

		file_menu.add_separator() # it adds a line after the 'Open files' option
		# if sys.platform.startswith('darwin'):
		# 	file_menu.add_command(label = "Quit", command = self.on_closing, accelerator="Command-q")
		# 	window.bind('q', self.on_closing)  # This doesn't work yet, the mac python overrides it ?
		# else:
		file_menu.add_command(label = "Exit", command = self.on_closing, accelerator="{}-x".format(accelkey))
		window.bind('x', self.on_closing)

		# # creting another sub menu
		# edit_menu = tk.Menu(root_menu)
		# root_menu.add_cascade(label = "Edit", menu = edit_menu)
		# edit_menu.add_command(label = "Undo", command = function)
		# edit_menu.add_command(label = "Redo", command = function)


		# creting another sub menu
		run_menu = tk.Menu(root_menu)
		root_menu.add_cascade(label = "Run", menu = run_menu)
		run_menu.add_command(label = "Play", command = self.ClickPlay, accelerator="{}-p".format(accelkey))
		window.bind('p', self.ClickPlay)
		run_menu.add_command(label = "Stop", command = self.ClickStop, accelerator="{}-t".format(accelkey))
		window.bind('t', self.ClickStop)


		window.protocol("WM_DELETE_WINDOW", self.on_closing)
		window.protocol("WM_QUERYENDSESSION", self.on_closing)
		window.protocol("WM_ENDSESSION", self.on_closing)
		window.protocol("WM_QUIT", self.on_closing)
		window.protocol("WM_DESTROY", self.on_closing)
		window.protocol("WM_CLOSE", self.on_closing)
		window.protocol("CTRL_SHUTDOWN_EVENT", self.on_closing)
		window.protocol("HWND_MESSAGE", self.on_closing)

		# self.get_icon("New")
		# self.get_icon("Save")
		# self.get_icon("SaveAs")
		# self.get_icon("Open")
		# self.get_icon("Play")
		# self.get_icon("Stop")

		signal.signal(signal.SIGTERM, self.on_closing)



	def BuildPlan(self, p):

		if 'Plan' not in self.config:
			self.config['Plan'] = {}
			self.saveini()

		if 'ScriptDir' not in self.config['Plan']:
			self.config['Plan']['ScriptDir'] = self.dir_path
			self.saveini()

		if 'ScenarioDir' not in self.config['Plan']:
			self.config['Plan']['ScenarioDir'] = self.dir_path
			self.saveini()

		if 'ScenarioFile' not in self.config['Plan']:
			self.config['Plan']['ScenarioFile'] = ""
			self.saveini()

		self.updateTitle()

		planrow = 0
		p.columnconfigure(planrow, weight=1)
		p.rowconfigure(planrow, weight=1)
		# Button Bar

		bbar = ttk.Frame(p)
		bbar.grid(column=0, row=planrow, sticky="nsew")
		bbargrid = ttk.Frame(bbar)
		bbargrid.grid(row=0, column=0, sticky="nsew")
		# new
		btnno = 0
		icontext = "New"
		self.iconew = self.get_icon(icontext)
		bnew = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', command=self.mnu_file_New)
		# bnew = ttk.Button(bbargrid, image=self.iconew, padding='3 3 3 3', command=self.mnu_file_New)
		# bnew = ttk.Button(bbargrid, text="New", command=self.mnu_file_New)
		bnew.grid(column=btnno, row=0, sticky="nsew")
		# open
		btnno += 1

		icontext = "Open"
		self.icoopen = self.get_icon(icontext)
		bopen = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', command=self.mnu_file_Open)
		# self.icoopen = self.get_icon("Open")
		# bopen = ttk.Button(bbargrid, image=self.icoopen, padding='3 3 3 3', command=self.mnu_file_Open)
		# bopen = ttk.Button(bbargrid, text="Open", command=self.mnu_file_Open)
		bopen.grid(column=btnno, row=0, sticky="nsew")
		# save
		btnno += 1
		icontext = "Save"
		self.icoSave = self.get_icon(icontext)
		bSave = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', command=self.mnu_file_Save)
		# bSave = ttk.Button(bbargrid, image=self.icoSave, padding='3 3 3 3', command=self.mnu_file_Save)
		# bSave = ttk.Button(bbargrid, text="Save", command=self.mnu_file_Save)
		bSave.grid(column=btnno, row=0, sticky="nsew")
		# play
		btnno += 1
		icontext = "Play"
		self.icoPlay = self.get_icon(icontext)
		bPlay = ttk.Button(bbargrid, image=self.imgdata[icontext], padding='3 3 3 3', text="Play", command=self.ClickPlay)
		# bPlay = ttk.Button(bbargrid, image=self.icoPlay, padding='3 3 3 3', command=self.ClickPlay)
		# bPlay = ttk.Button(bbargrid, text="Play", command=self.ClickPlay)
		bPlay.grid(column=btnno, row=0, sticky="nsew")


		planrow += 1
		p.columnconfigure(planrow, weight=2)
		p.rowconfigure(planrow, weight=1)
		# Plan Graph

		self.pln_graph = tk.Canvas(p)
		self.pln_graph.grid(column=0, row=planrow, sticky="nsew") # sticky="wens"

		planrow += 1
		# Plan scripts

		sg = ttk.Frame(p)
		sg.grid(column=0, row=planrow, sticky="nsew")
		self.scriptgrid = ttk.Frame(sg)
		self.scriptgrid.grid(row=0, column=0, sticky="nsew")

		# label row 0 of sg
		self.scriptgrid.columnconfigure(self.plancolidx, weight=1)
		idx = ttk.Label(self.scriptgrid, text="Index")
		idx.grid(column=self.plancolidx, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolusr, weight=2)
		usr = ttk.Label(self.scriptgrid, text="Users")
		usr.grid(column=self.plancolusr, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancoldly, weight=2)
		usr = ttk.Label(self.scriptgrid, text="Delay")
		usr.grid(column=self.plancoldly, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolrmp, weight=2)
		usr = ttk.Label(self.scriptgrid, text="Ramp Up")
		usr.grid(column=self.plancolrmp, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolrun, weight=2)
		usr = ttk.Label(self.scriptgrid, text="Run")
		usr.grid(column=self.plancolrun, row=0, sticky="nsew")

		# self.scriptgrid.columnconfigure(self.plancolnme, weight=5)
		# nme = ttk.Label(self.scriptgrid, text="Name")
		# nme.grid(column=self.plancolnme, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancolscr, weight=5)
		scr = ttk.Label(self.scriptgrid, text="Script")
		scr.grid(column=self.plancolscr, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancoltst, weight=5)
		tst = ttk.Label(self.scriptgrid, text="Test")
		tst.grid(column=self.plancoltst, row=0, sticky="nsew")

		self.scriptgrid.columnconfigure(self.plancoladd, weight=1)
		new = ttk.Button(self.scriptgrid, text="+", command=self.addScriptRow, width=1)
		new.grid(column=self.plancoladd, row=0, sticky="nsew")

		if len(self.config['Plan']['ScenarioFile'])>0:
			self.mnu_file_Open(self.config['Plan']['ScenarioFile'])
		else:
			self.addScriptRow()



	def BuildRun(self, r):

		if 'Run' not in self.config:
			self.config['Run'] = {}
			self.saveini()

		if 'ResultsDir' not in self.config['Run']:
			self.config['Run']['ResultsDir'] = os.path.join(self.dir_path, "results")
			self.saveini()

		if 'display_index' not in self.config['Run']:
			self.config['Run']['display_index'] = str(False)
			self.saveini()

		if 'display_iteration' not in self.config['Run']:
			self.config['Run']['display_iteration'] = str(False)
			self.saveini()

		if 'display_sequence' not in self.config['Run']:
			self.config['Run']['display_sequence'] = str(False)
			self.saveini()

		if 'display_percentile' not in self.config['Run']:
			self.config['Run']['display_percentile'] = str(90)
			self.saveini()


		rg = ttk.Frame(r)
		rg.grid(column=0, row=1, sticky="nsew")
		rgbar = ttk.Frame(rg)
		rgbar.grid(row=0, column=0, sticky="nsew")

		#
		# run info bar
		#
		usr = ttk.Label(rgbar, text="Unique by:") #, borderwidth=2, relief="raised")
		usr.grid(column=11, row=0, sticky="nsew") # , rowspan=2

		# gblist = ["script_index", "iteration", "sequence"]
		if "display_index" not in self.display_run:
			self.display_run['display_index'] = tk.BooleanVar()
			self.display_run['display_index'].set(self.str2bool(self.config['Run']['display_index']))
		usr = ttk.Label(rgbar, text="  Index  ") #, borderwidth=2, relief="raised")
		usr.grid(column=10, row=1, sticky="nsew")
		# chk = tk.Checkbutton(rgbar, text="Index", variable=self.display_run['display_index'], onvalue=1, offvalue=0) #, height = 2, width = 10)
		chk = tk.Checkbutton(rgbar, variable=self.display_run['display_index'], onvalue=True, offvalue=False, command=self.delayed_UpdateRunStats_bg) #, height = 2, width = 10)
		chk.grid(column=10, row=2, sticky="nsew")

		if "display_iteration" not in self.display_run:
			self.display_run['display_iteration'] = tk.BooleanVar()
			self.display_run['display_iteration'].set(self.str2bool(self.config['Run']['display_iteration']))
		usr = ttk.Label(rgbar, text="  Iteration  ") #, borderwidth=2, relief="raised")
		usr.grid(column=11, row=1, sticky="nsew")
		# chk = tk.Checkbutton(rgbar, text="Iteration", variable=self.display_run['display_iteration'], onvalue=1, offvalue=0) #, height = 2, width = 10)
		chk = tk.Checkbutton(rgbar, variable=self.display_run['display_iteration'], onvalue=True, offvalue=False, command=self.delayed_UpdateRunStats_bg) #, height = 2, width = 10)
		chk.grid(column=11, row=2, sticky="nsew")

		if "display_sequence" not in self.display_run:
			self.display_run['display_sequence'] = tk.BooleanVar()
			self.display_run['display_sequence'].set(self.str2bool(self.config['Run']['display_sequence']))
		usr = ttk.Label(rgbar, text="  Sequence  ") #, borderwidth=2, relief="raised")
		usr.grid(column=12, row=1, sticky="nsew")
		# chk = tk.Checkbutton(rgbar, text="Sequence", variable=self.display_run['display_sequence'], onvalue=1, offvalue=0) #, height = 2, width = 10)
		chk = tk.Checkbutton(rgbar, variable=self.display_run['display_sequence'], onvalue=True, offvalue=False, command=self.delayed_UpdateRunStats_bg) #, height = 2, width = 10)
		chk.grid(column=12, row=2, sticky="nsew")


		# display_percentile
		# if "display_percentile" not in self.display_run:
		# 	self.display_run['display_percentile'] = tk.IntVar()
		# 	self.display_run['display_percentile'].set(int(self.config['Run']['display_percentile']))
		usr = ttk.Label(rgbar, text="  %ile  ") #, borderwidth=2, relief="raised")
		usr.grid(column=13, row=1, sticky="nsew")

		pct = ttk.Spinbox(rgbar, from_=1, to=99, validate="focusout", width=5, justify="right", validatecommand=self.delayed_UpdateRunStats_bg, command=self.delayed_UpdateRunStats_bg)
		pct.grid(column=13, row=2, sticky="nsew")
		pct.selection_clear()
		pct.insert(0, int(self.config['Run']['display_percentile']))
		self.display_run['display_percentile'] = pct

		# # chk = tk.Checkbutton(rgbar, text="Sequence", variable=self.display_run['display_sequence'], onvalue=1, offvalue=0) #, height = 2, width = 10)
		# chk = tk.Checkbutton(rgbar, variable=self.display_run['display_sequence'], onvalue=True, offvalue=False, command=self.delayed_UpdateRunStats_bg) #, height = 2, width = 10)
		# chk.grid(column=12, row=2, sticky="nsew")
		# num = "10"
		# usr = ttk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout")
		# usr.config(validatecommand=lambda: self.sr_users_validate(row))
		# usr.grid(column=self.plancolusr, row=self.scriptcount, sticky="nsew")
		# usr.insert(0, num)
		# self.scriptlist[self.scriptcount]["Users"] = int(num)



		if "start_time" not in self.display_run:
			self.display_run['start_time'] = tk.StringVar()
			# self.display_run['start_time'].set("  {}  ".format(self.total_robots))
			self.display_run['start_time'].set("    ")
		usr = ttk.Label(rgbar, text="  Start Time  ") #, borderwidth=2, relief="raised")
		usr.grid(column=20, row=1, sticky="nsew")
		usr = ttk.Label(rgbar, textvariable=self.display_run['start_time']) #, borderwidth=2, relief="groove")
		usr.grid(column=20, row=2, sticky="nsew")

		if "elapsed_time" not in self.display_run:
			self.display_run['elapsed_time'] = tk.StringVar()
			# self.display_run['elapsed_time'].set("  {}  ".format(self.total_robots))
			self.display_run['elapsed_time'].set("    ")
		usr = ttk.Label(rgbar, text="  Elapsed Time  ") #, borderwidth=2, relief="raised")
		usr.grid(column=21, row=1, sticky="nsew")
		usr = ttk.Label(rgbar, textvariable=self.display_run['elapsed_time']) #, borderwidth=2, relief="groove")
		usr.grid(column=21, row=2, sticky="nsew")

		if "total_robots" not in self.display_run:
			self.display_run['total_robots'] = tk.StringVar()
			self.display_run['total_robots'].set("  {}  ".format(self.total_robots))
		usr = ttk.Label(rgbar, text="  Robots  ") #, borderwidth=2, relief="raised")
		usr.grid(column=26, row=1, sticky="nsew")
		usr = ttk.Label(rgbar, textvariable=self.display_run['total_robots']) #, borderwidth=2, relief="groove")
		usr.grid(column=26, row=2, sticky="nsew")


		icontext = "Stop"
		self.icoStop = self.get_icon(icontext)
		stp = ttk.Button(rgbar, image=self.imgdata[icontext], padding='3 3 3 3', text="Stop", command=self.ClickStop)
		# stp = ttk.Button(rgbar, text='Stop', command=self.ClickStop)
		stp.grid(column=39, row=1, sticky="nsew") # , rowspan=2



		#
		# run results table
		#

		self.rungrid = ttk.Frame(rg)
		self.rungrid.grid(row=1, column=0, sticky="nsew")

		# set initial columns for the results grid
		if "columns" not in self.display_run:
			self.display_run["columns"] = {}
		if "rows" not in self.display_run:
			self.display_run["rows"] = {}

		collst = ["result_name", "result", "count", "min", "avg", "max"]
		colno = 0
		for col in collst:
			# print("BuildRun: colno:", colno, "col:", col)
			# print("BuildRun: display_run:", self.display_run)
			if colno in self.display_run["columns"]:
				currcol = self.display_run["columns"][colno].get()
				if col != currcol:
					self.display_run["columns"][colno].set("  {}  ".format(col))
			else:
				self.display_run["columns"][colno] = tk.StringVar()
				self.display_run["columns"][colno].set("  {}  ".format(col))

			# print("BuildRun: display_run[columns][colno]:", self.display_run["columns"][colno])

			grdcols = self.rungrid.grid_size()[0]
			# print("BuildRun: grdcols:", grdcols)
			grdcols += -1
			# print("BuildRun: grdcols:", grdcols, " 	colno:", colno)
			if grdcols < colno:
				usr = ttk.Label(self.rungrid, textvariable=self.display_run["columns"][colno], borderwidth=2, relief="raised")
				usr.grid(column=colno, row=0, sticky="nsew")

			colno += 1




	def BuildAgent(self, a):
		ag = ttk.Frame(a)
		ag.grid(column=0, row=1, sticky="nsew")
		self.agenttgrid = ttk.Frame(ag)
		self.agenttgrid.grid(row=0, column=0, sticky="nsew")


		usr = ttk.Label(self.agenttgrid, text="  Status  ", borderwidth=2, relief="raised")
		usr.grid(column=0, row=0, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, text="  Agent  ", borderwidth=2, relief="raised")
		usr.grid(column=2, row=0, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, text="  Last Seen  ", borderwidth=2, relief="raised")
		usr.grid(column=4, row=0, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, text="  Robots  ", borderwidth=2, relief="raised")
		usr.grid(column=5, row=0, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, text="  Load  ", borderwidth=2, relief="raised")
		usr.grid(column=6, row=0, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, text="  CPU %  ", borderwidth=2, relief="raised")
		usr.grid(column=8, row=0, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, text="  MEM %  ", borderwidth=2, relief="raised")
		usr.grid(column=10, row=0, sticky="nsew")

		usr = ttk.Label(self.agenttgrid, text="  NET %  ", borderwidth=2, relief="raised")
		usr.grid(column=12, row=0, sticky="nsew")

	def dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def run_db_thread(self):
		while self.run_dbthread:
			if (self.datadb is None) or (self.run_name != self.run_name_current):
				# print("run_db_thread: ensure_db")
				self.ensure_db()

			if self.datadb is not None:

				if len(self.dbqueue["Write"])>0:
					# print("run_db_thread: dbqueue: Write")
					tmpq = list(self.dbqueue["Write"])
					self.dbqueue["Write"] = []
					# print("run_db_thread: dbqueue: Write: tmpq:", tmpq)
					for item in tmpq:
						if item["SQL"] and item["VALUES"]:
							try:
								# print("run_db_thread: dbqueue: Write: SQL:", item["SQL"], " 	VALUES:", item["VALUES"])
								cur = self.datadb.cursor()
								cur.execute(item["SQL"], item["VALUES"])
								cur.close()
								self.datadb.commit()
							except Exception as e:
								print("run_db_thread: dbqueue: Write: Exception:", e)
								print("run_db_thread: dbqueue: Write: Item:", item)
						else:
							print("run_db_thread: dbqueue: Write: Item not written, missing key SQL or VALUES")
							print("run_db_thread: dbqueue: Write: Item:", item)

				if len(self.dbqueue["Read"])>0:
					# print("run_db_thread: dbqueue: Read")
					tmpq = list(self.dbqueue["Read"])
					self.dbqueue["Read"] = []
					# print("run_db_thread: dbqueue: Read: tmpq:", tmpq)
					for item in tmpq:
						if "SQL" in item: # and item["VALUES"]:
							try:
								# print("run_db_thread: dbqueue: Read: SQL:", item["SQL"])
								self.datadb.row_factory = self.dict_factory
								cur = self.datadb.cursor()
								cur.execute(item["SQL"])
								result = cur.fetchall()
								# print("run_db_thread: dbqueue: Read: result:", result)
								cur.close()
								self.datadb.commit()

								# print("run_db_thread: dbqueue: Read: result:", result)
								if "KEY" in item:
									self.dbqueue["ReadResult"][item["KEY"]] = result

							except Exception as e:
								print("run_db_thread: dbqueue: Read: Exception:", e)
								print("run_db_thread: dbqueue: Read: Item:", item)
						else:
							print("run_db_thread: dbqueue: Read: Item not written, missing key SQL or VALUES")
							print("run_db_thread: dbqueue: Read: Item:", item)

				# Agents
				if len(self.dbqueue["Agents"])>0:
					# print("run_db_thread: dbqueue: Agents")
					agntdata = list(self.dbqueue["Agents"])
					self.dbqueue["Agents"] = []
					# print("run_db_thread: dbqueue: Agents: agntdata:", agntdata)
					try:
						sql = "INSERT INTO Agents VALUES (?,?,?,?,?,?,?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, agntdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						print("run_db_thread: dbqueue: Agents: Exception:", e)
						print("run_db_thread: dbqueue: Results: ", sql, agntdata)

				# Results
				if len(self.dbqueue["Results"])>0:
					# print("run_db_thread: dbqueue: Results")
					resdata = list(self.dbqueue["Results"])
					self.dbqueue["Results"] = []
					# print("run_db_thread: dbqueue: Results: resdata:", resdata)
					try:
						sql = "INSERT INTO Results VALUES (?,?,?,?,?,?,?,?,?,?)"
						cur = self.datadb.cursor()
						cur.executemany(sql, resdata)
						cur.close()
						self.datadb.commit()
					except Exception as e:
						print("run_db_thread: dbqueue: Results: Exception:", e)
						print("run_db_thread: dbqueue: Results: ", sql, resdata)

			time.sleep(0.1)
		if self.datadb is not None:
			self.datadb.close()
			self.datadb = None


	def ensure_db(self):
		createschema = False
		# print("ensure_db: run_name:", self.run_name)
		if len(self.run_name)>0:
			if self.run_name != self.run_name_current:
				self.run_name_current = self.run_name
				createschema = True

			if createschema and self.datadb is not None:
				print("ensure_db: Disconnect and close DB")
				self.datadb.commit()
				self.datadb.close()
				self.datadb = None

			# check if dir exists
			print("ensure_db: dir_path:", self.dir_path)
			# self.resultsdir = os.path.join(self.dir_path, "results")
			if 'ResultsDir' not in self.config['Run']:
				self.config['Run']['ResultsDir'] = os.path.join(self.dir_path, "results")
				self.saveini()
			self.resultsdir = self.config['Run']['ResultsDir']

			if not os.path.exists(self.resultsdir):
				os.mkdir(self.resultsdir)
			self.datapath = os.path.join(self.resultsdir, self.run_name)
			print("ensure_db: datapath:", self.datapath)
			if not os.path.exists(self.datapath):
				os.mkdir(self.datapath)

			# check if db exists
			self.dbfile = os.path.join(self.datapath, "{}.db".format(self.run_name))
			print("ensure_db: dbfile:", self.dbfile)
			if not os.path.exists(self.dbfile):
				createschema = True

			if self.datadb is None:
				print("ensure_db: Connect to DB")
				self.datadb = sqlite3.connect(self.dbfile)
				self.datadb.create_aggregate("percentile", 2, percentile)

			if createschema:
				c = self.datadb.cursor()
				# create tables
				c.execute('''CREATE TABLE Agents
					(agent text, status text, last_seen date, robots int, load num, cpu num, mem num, net num)''')

				c.execute('''CREATE TABLE Results
					(script_index int, virtual_user int, iteration int, agent text, sequence int, result_name text, result text, elapsed_time num, start_time num, end_time num)''')

				# create indexes?

 				# create views?

				# CREATE VIEW "summary" AS SELECT
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
				CREATE VIEW "Summary" AS SELECT
					r.result_name,
					min(rp.elapsed_time) "min", avg(rp.elapsed_time) "avg", max(rp.elapsed_time)  "max",
					count(rp.result) as _pass,
					count(rf.result) as _fail,
					count(ro.result) as _other

				FROM Results as r
					LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == "PASS"
					LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == "FAIL"
					LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> "PASS" AND ro.result <> "FAIL"
				GROUP BY
					r.result_name
				ORDER BY r.sequence
				''')


				self.datadb.commit()

	def delayed_UpdateAgents(self):
		time.sleep(10)
		self.UpdateAgents()

	def UpdateAgents(self):
		rnum = 0
		removeagents = []
		robot_count = 0
		displayagent = True
		time_elapsed = int(time.time()) - self.agenttgridupdate
		if (time_elapsed>5):

			self.agenttgridupdate = int(time.time())
			for agnt in self.Agents.keys():
				displayagent = True
				tm = self.Agents[agnt]["LastSeen"]
				agnt_elapsed = int(time.time()) - tm
				if agnt_elapsed>15:
					self.Agents[agnt]["Status"] = "Offline?"
				if agnt_elapsed>60:
					removeagents.append(agnt)
					# del self.Agents[agnt]
					displayagent = False

				if displayagent:
					rnum += 1
					dt = datetime.fromtimestamp(tm)
					workingkeys = self.display_agents.keys()
					if rnum not in workingkeys:
						self.display_agents[rnum] = {}
						self.display_agents[rnum]["Status"] = tk.StringVar()
						self.display_agents[rnum]["Agent"] = tk.StringVar()
						self.display_agents[rnum]["LastSeen"] = tk.StringVar()
						self.display_agents[rnum]["Robots"] = tk.StringVar()
						self.display_agents[rnum]["LOAD%"] = tk.StringVar()
						self.display_agents[rnum]["CPU%"] = tk.StringVar()
						self.display_agents[rnum]["MEM%"] = tk.StringVar()
						self.display_agents[rnum]["NET%"] = tk.StringVar()

					self.display_agents[rnum]["Status"].set("  {}  ".format(self.Agents[agnt]["Status"]))
					self.display_agents[rnum]["Agent"].set("  {}  ".format(agnt))
					self.display_agents[rnum]["LastSeen"].set("  {}  ".format(dt.isoformat(sep=' ',timespec='seconds')))
					self.display_agents[rnum]["Robots"].set("  {}  ".format(self.Agents[agnt]["Robots"]))
					self.display_agents[rnum]["LOAD%"].set("  {}  ".format(self.Agents[agnt]["LOAD%"]))
					self.display_agents[rnum]["CPU%"].set("  {}  ".format(self.Agents[agnt]["CPU%"]))
					self.display_agents[rnum]["MEM%"].set("  {}  ".format(self.Agents[agnt]["MEM%"]))
					self.display_agents[rnum]["NET%"].set("  {}  ".format(self.Agents[agnt]["NET%"]))
					# print("UpdateAgents: display_agents:", self.display_agents)

					robot_count += self.Agents[agnt]["Robots"]

					grdrows = self.agenttgrid.grid_size()[1]
					if grdrows>0:
						grdrows += -1
					# print("UpdateAgents: grdrows:", grdrows, "	rnum:", rnum)
					if grdrows<rnum:
						self.add_row(rnum)


			if self.total_robots>0 and robot_count <1:
				# run finished so clear run name
				self.run_name = ""
				self.robot_schedule["RunName"] = self.run_name

			self.total_robots = robot_count
			self.display_run['total_robots'].set("  {}  ".format(self.total_robots))
			# print("total_robots:", self.total_robots)
			if self.total_robots>0:
				etm = time.gmtime(int(time.time()) - self.robot_schedule["Start"])
				self.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))

			grdrows = self.agenttgrid.grid_size()[1]-1
			while grdrows>rnum:
				# print("UpdateAgents: grdrows",grdrows)
				try:
					self.UA_removerow(grdrows)
					self.display_agents[grdrows]
				except Exception as e:
					print("UpdateAgents: grdrows:", grdrows, "Exception:", e)
				grdrows += -1

			for agnt in removeagents:
				# this should prevent issue RuntimeError: dictionary changed size during iteration
				del self.Agents[agnt]

			if rnum>0:
				self.updatethread = threading.Thread(target=self.delayed_UpdateAgents)
				self.updatethread.start()


	def add_row(self, rnum):
		# print("add_row: rnum:", rnum)
		# print("add_row: Status:", self.display_agents[rnum]["Status"])
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Status"], borderwidth=2, relief="groove")
		usr.grid(column=0, row=rnum, sticky="nsew")
		# print("add_row: Agent:", self.display_agents[rnum]["Agent"])
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Agent"], borderwidth=2, relief="groove")
		usr.grid(column=2, row=rnum, sticky="nsew")
		# print("add_row: LastSeen:", self.display_agents[rnum]["LastSeen"])
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["LastSeen"], borderwidth=2, relief="groove")
		usr.grid(column=4, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["Robots"], borderwidth=2, relief="groove")
		usr.grid(column=5, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["LOAD%"], borderwidth=2, relief="groove")
		usr.grid(column=6, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["CPU%"], borderwidth=2, relief="groove")
		usr.grid(column=8, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["MEM%"], borderwidth=2, relief="groove")
		usr.grid(column=10, row=rnum, sticky="nsew")
		usr = ttk.Label(self.agenttgrid, textvariable=self.display_agents[rnum]["NET%"], borderwidth=2, relief="groove")
		usr.grid(column=12, row=rnum, sticky="nsew")


	def UpdateAgents_orig(self):
		# rnum = 0
		# removeagents = []
		# time_elapsed = int(time.time()) - self.agenttgridupdate
		# if (time_elapsed>5):
		# 	self.agenttgridupdate = int(time.time())
		# 	# print("Agents:", self.Agents)
		# 	for agnt in self.Agents.keys():
		# 		# print("Agent:", agnt)
		# 		tm = self.Agents[agnt]["LastSeen"]
		# 		agnt_elapsed = int(time.time()) - tm
		# 		if agnt_elapsed>15:
		# 			self.Agents[agnt]["Status"] = "Offline?"
		# 		if agnt_elapsed>60:
		# 			removeagents.append(agnt)
		# 			# del self.Agents[agnt]
		# 		else:
		# 			rnum += 1
		# 			dt = datetime.fromtimestamp(tm)
		# 			self.UA_removerow(rnum)
		# 			# style = ttk.Style()
		# 			# style.configure("Default", foreground='#000000', background='#40E0D0')
		# 			# style = ttk.Style()
		# 			# style.configure("Ready", foreground='#000000', background='#00AA00')
		# 			# style = ttk.Style()
		# 			# style.configure("Run", foreground='#000000', background='#008800')
		# 			# style = ttk.Style()
		# 			# style.configure("Warn", foreground='#000000', background='#555500')
		# 			# style = ttk.Style()
		# 			# style.configure("Critical", foreground='#FFFFFF', background='#FF0000')
		# 			# style = ttk.Style()
		# 			# style.configure("Offline", foreground='#F0F0F0', background='#40E0D0')
		# 			# row_style = "Default"
		# 			# if self.Agents[agnt]["Status"] == "Ready":
		# 			# 	row_style = "Ready"
		# 			# if self.Agents[agnt]["Status"] == "Running":
		# 			# 	row_style = "Run"
		# 			# if self.Agents[agnt]["Status"] == "Offline?":
		# 			# 	row_style = "Offline"
		# 			# if self.Agents[agnt]["Status"] == "Warning":
		# 			# 	row_style = "Warn"
		# 			# if self.Agents[agnt]["Status"] == "Critical":
		# 			# 	row_style = "Critical"
		#
		#
		#
		#
		# 			txt = "  {}  ".format(self.Agents[agnt]["Status"])
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=0, row=rnum, sticky="nsew")
		#
		# 			txt = "  {}  ".format(agnt)
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=2, row=rnum, sticky="nsew")
		#
		# 			txt = "  {}  ".format(dt.isoformat(sep=' ',timespec='seconds'))
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=4, row=rnum, sticky="nsew")
		#
		# 			txt = "  {}  ".format(self.Agents[agnt]["Robots"])
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=5, row=rnum, sticky="nsew")
		#
		# 			txt = "  {}  ".format(self.Agents[agnt]["LOAD%"])
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=6, row=rnum, sticky="nsew")
		#
		# 			txt = "  {}  ".format(self.Agents[agnt]["CPU%"])
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=8, row=rnum, sticky="nsew")
		#
		# 			txt = "  {}  ".format(self.Agents[agnt]["MEM%"])
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=10, row=rnum, sticky="nsew")
		#
		# 			txt = "  {}  ".format(self.Agents[agnt]["NET%"])
		# 			# usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove", style=row_style)
		# 			usr = ttk.Label(self.agenttgrid, text=txt, borderwidth=2, relief="groove")
		# 			usr.grid(column=12, row=rnum, sticky="nsew")
		#
		# 	# print("agenttgrid.grid_size (col, row)",self.agenttgrid.grid_size())
		#
		# 	grdrows = self.agenttgrid.grid_size()[1]
		# 	# print("grdrows",grdrows)
		# 	while grdrows>rnum:
		# 		# print("grdrows",grdrows)
		# 		self.UA_removerow(grdrows)
		# 		grdrows += -1
		#
		# 	for agnt in removeagents:
		# 		# this should prevent issue RuntimeError: dictionary changed size during iteration
		# 		del self.Agents[agnt]
		#
		# 	if rnum>0:
		# 		t = threading.Thread(target=self.delayed_UpdateAgents)
		# 		t.start()
		# 	# self.agenttgridupdate = int(time.time())
			pass

	def UA_removerow(self, r):
		relmts = self.agenttgrid.grid_slaves(row=r, column=None)
		# print(relmts)
		for elmt in relmts:
			elmt.destroy()

	def get_next_agent(self):
		# print("get_next_agent")
		# from operator import itemgetter
		# print("get_next_agent: self.Agents:", self.Agents)
		if len(self.Agents) <1:
			return None


		loadtpl = []
		robottpl = []
		for agnt in self.Agents.keys():
			# print("get_next_agent: agnt:", agnt)
			loadtpl.append([agnt, self.Agents[agnt]['LOAD%']])
			robottpl.append([agnt, self.Agents[agnt]['AssignedRobots']])

		# data.sort(key=itemgetter(1))
		# print("get_next_agent: robottpl:", robottpl)
		# Start with agent with least robots
		robottpl.sort(key=itemgetter(1))
		# print("get_next_agent: robottpl:", robottpl)
		if robottpl[0][1] < 10:
			return robottpl[0][0]
		else:
			# try for agent with least load
			# print("get_next_agent: loadtpl:", loadtpl)
			loadtpl.sort(key=itemgetter(1))
			# print("get_next_agent: loadtpl:", loadtpl)
			if loadtpl[0][1] < 95:
				return loadtpl[0][0]
			else:
				return None

	def delayed_UpdateRunStats_bg(self):

		display_index = self.display_run['display_index'].get()
		if display_index != self.str2bool(self.config['Run']['display_index']):
			self.config['Run']['display_index'] = str(display_index)
			self.saveini()

		display_iteration = self.display_run['display_iteration'].get()
		if display_iteration != self.str2bool(self.config['Run']['display_iteration']):
			self.config['Run']['display_iteration'] = str(display_iteration)
			self.saveini()

		display_sequence = self.display_run['display_sequence'].get()
		if display_sequence != self.str2bool(self.config['Run']['display_sequence']):
			self.config['Run']['display_sequence'] = str(display_sequence)
			self.saveini()

		# self.display_run['display_percentile']
		display_percentile = int(self.display_run['display_percentile'].get())
		if display_percentile != int(self.config['Run']['display_percentile']):
			self.config['Run']['display_percentile'] = str(display_percentile)
			self.saveini()

		# self.robot_schedule["Start"]
		if "Start" in self.robot_schedule:
			time_elapsed = int(time.time()) - self.rungridupdate
			if (time_elapsed>5):
				ut = threading.Thread(target=self.delayed_UpdateRunStats)
				ut.start()

	def delayed_UpdateRunStats(self):
		time_elapsed = int(time.time()) - self.rungridupdate
		if (time_elapsed>5):
			# queue sqls so UpdateRunStats should have the results


			display_percentile = int(self.display_run['display_percentile'].get())
			if display_percentile != int(self.config['Run']['display_percentile']):
				self.config['Run']['display_percentile'] = str(display_percentile)
				self.saveini()


			gblist = []
			display_index = self.display_run['display_index'].get()
			# print("delayed_UpdateRunStats: display_index:", display_index, "	config[Run][display_index]:", self.config['Run']['display_index'], "	bool(config[Run][display_index]):", self.str2bool(self.config['Run']['display_index']))
			if display_index != self.str2bool(self.config['Run']['display_index']):
				self.config['Run']['display_index'] = str(display_index)
				self.saveini()
			if display_index:
				gblist.append("r.script_index")

			display_iteration = self.display_run['display_iteration'].get()
			if display_iteration != self.str2bool(self.config['Run']['display_iteration']):
				self.config['Run']['display_iteration'] = str(display_iteration)
				self.saveini()
			if display_iteration:
				gblist.append("r.iteration")

			display_sequence = self.display_run['display_sequence'].get()
			if display_sequence != self.str2bool(self.config['Run']['display_sequence']):
				self.config['Run']['display_sequence'] = str(display_sequence)
				self.saveini()
			if display_sequence:
				gblist.append("r.sequence")

			gblist.append("r.result_name")
			# print("delayed_UpdateRunStats:	gblist:", gblist)
			gbcols = ", ".join(gblist)

			# print("delayed_UpdateRunStats:	gbcols:", gbcols)

			# SELECT
			# 	r.script_index, r.sequence, r.iteration,
			# 	r.result_name,
			# 	count(rp.result) as _pass,
			# 	count(rf.result) as _fail,
			# 	count(ro.result) as _other
			#
			# FROM Results as r
			# 	LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == "PASS"
			# 	LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == "FAIL"
			# 	LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> "PASS" AND ro.result <> "FAIL"
			#
			# GROUP BY
			# 	r.script_index, r.sequence, r.iteration,
			# 	r.result_name
			# ORDER BY r.sequence

			sql = "SELECT "
			if len(gblist)>0:
				sql += 	gbcols
				sql += 	", "
			sql += 		"round(min(rp.elapsed_time),3) 'min', "
			sql += 		"round(avg(rp.elapsed_time),3) 'avg', "
			sql += 		"round(percentile(rp.elapsed_time, {}),3) '{}%ile', ".format(display_percentile, display_percentile)
			sql += 		"round(max(rp.elapsed_time),3) 'max', "
			sql += 		"count(rp.result) as _pass, "
			sql += 		"count(rf.result) as _fail, "
			sql += 		"count(ro.result) as _other "
			sql += "FROM Results as r "
			sql += 		"LEFT JOIN Results as rp ON r.rowid == rp.rowid AND rp.result == 'PASS' "
			sql += 		"LEFT JOIN Results as rf ON r.rowid == rf.rowid AND rf.result == 'FAIL' "
			sql += 		"LEFT JOIN Results as ro ON r.rowid == ro.rowid AND ro.result <> 'PASS' AND ro.result <> 'FAIL' "
			sql += "WHERE r.start_time>{} ".format(self.robot_schedule["Start"])
			if len(gblist)>0:
				sql += "GROUP BY  "
				sql += 		gbcols

			sql += " ORDER BY r.sequence"


			self.dbqueue["Read"].append({"SQL": sql, "KEY": "RunStats"})


			time.sleep(1)
			self.UpdateRunStats()

	def UpdateRunStats(self):
		rnum = 0
		removestat = []

		if "Start" in self.robot_schedule:
			stm = time.localtime(self.robot_schedule["Start"])
			self.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))
			etm = time.gmtime(int(time.time()) - self.robot_schedule["Start"])
			self.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))

		time_elapsed = int(time.time()) - self.rungridupdate
		if (time_elapsed>5):
			self.rungridupdate = int(time.time())

			if "columns" not in self.display_run:
				self.display_run["columns"] = {}
			if "rows" not in self.display_run:
				self.display_run["rows"] = {}

			# if "RunStats" in self.dbqueue["ReadResult"] and len(self.dbqueue["ReadResult"]["RunStats"])>0:
			# 	print("UpdateRunStats: RunStats:", self.dbqueue["ReadResult"]["RunStats"])

			colno = 0
			if "RunStats" in self.dbqueue["ReadResult"] and len(self.dbqueue["ReadResult"]["RunStats"])>0:
				# print("UpdateRunStats: RunStats_Pass:", self.dbqueue["ReadResult"]["RunStats_Pass"])
				for col in self.dbqueue["ReadResult"]["RunStats"][0].keys():
					# print("UpdateRunStats: colno:", colno, "col:", col)
					colname = self.PrettyColName(col)
					# print("UpdateRunStats: colname:", colname)

					# print("UpdateRunStats: display_run:", self.display_run)
					if colno in self.display_run["columns"]:
						currcol = self.display_run["columns"][colno].get()
						if colname != currcol:
							self.display_run["columns"][colno].set("  {}  ".format(colname))
					else:
						self.display_run["columns"][colno] = tk.StringVar()
						self.display_run["columns"][colno].set("  {}  ".format(colname))

					# print("UpdateRunStats: display_run[columns][colno]:", self.display_run["columns"][colno])

					grdcols = self.rungrid.grid_size()[0]
					# print("UpdateRunStats: grdcols:", grdcols)
					grdcols += -1
					# print("UpdateRunStats: grdcols:", grdcols, " 	colno:", colno)
					if grdcols < colno:
						usr = ttk.Label(self.rungrid, textvariable=self.display_run["columns"][colno], borderwidth=2, relief="raised")
						usr.grid(column=colno, row=0, sticky="nsew")

					colno += 1

			colno += -1
			grdcols = self.rungrid.grid_size()[0]-1
			# print("UpdateRunStats: grdcols:", grdcols, "	colno:",colno)
			if grdcols>colno:
				# print("UpdateRunStats: need to remove columns grdcols:", grdcols, "	colno:",colno)
				c = grdcols
				while c>colno:
					# print("UpdateRunStats: need to remove rows c:", c, "	colno:",colno)
					relmts = self.rungrid.grid_slaves(row=None, column=c)
					# print(relmts)
					for elmt in relmts:
						elmt.destroy()
					c += -1


			datarows = len(self.dbqueue["ReadResult"]["RunStats"])
			# datarows = len(self.dbqueue["ReadResult"]["RunStats_Pass"])
			grdrows = self.rungrid.grid_size()[1]-1
			# print("UpdateRunStats: grdrows:", grdrows, " > datarows:",datarows)
			if grdrows>datarows:
				# print("UpdateRunStats: need to remove rows grdrows:", grdrows, " > datarows:",datarows)
				r = grdrows
				while r>datarows:
					# print("UpdateRunStats: need to remove rows r:", r, " > datarows:",datarows)
					relmts = self.rungrid.grid_slaves(row=r, column=None)
					# print(relmts)
					for elmt in relmts:
						elmt.destroy()
					r += -1

			rowno = 1
			for row in self.dbqueue["ReadResult"]["RunStats"]:
				newrow = False
				grdrows = self.rungrid.grid_size()[1]
				# print("UpdateRunStats: grdrows:", grdrows)

				if rowno not in self.display_run["rows"]:
					self.display_run["rows"][rowno] = {}

				colno = 0
				newcell = False
				for col in row.keys():
					# print("UpdateRunStats: colno:", colno, "col:", col)
					# print("UpdateRunStats: row[col]:", row[col])
					if colno>len(self.display_run["rows"][rowno])-1:
						self.display_run["rows"][rowno][colno] = tk.StringVar()

					self.display_run["rows"][rowno][colno].set("  {}  ".format(row[col]))

					relmts = self.rungrid.grid_slaves(row=rowno, column=colno)
					# print("UpdateRunStats: relmts:", relmts)

					# if newrow or newcell:
					if len(relmts) < 1:
						usr = ttk.Label(self.rungrid, textvariable=self.display_run["rows"][rowno][colno], borderwidth=2, relief="groove")
						usr.grid(column=colno, row=rowno, sticky="nsew")


					colno += 1

				rowno += 1


			ut = threading.Thread(target=self.delayed_UpdateRunStats)
			ut.start()

	def PrettyColName(self, colname):
		# print("PrettyColName: colname:", colname)
		newcolname = colname
		# if newcolname[:1] == '_':
		# 	newcolname = newcolname[1:]
		# newcolname = newcolname.replace("_", " ")

		cnlst = colname.split("_")
		ncnlst = []
		# print("PrettyColName: cnlst:", cnlst)
		for word in cnlst:
			# print("PrettyColName: word:", word)
			if len(word)>0:
				ncnlst.append(word.capitalize())
		# print("PrettyColName: ncnlst:", ncnlst)
		newcolname = " ".join(ncnlst)

		# print("PrettyColName: newcolname:", newcolname)

		return newcolname


	def ClickPlay(self, _event=None):
		self.sr_validate()
		# print(self.tabs.tabs())
		self.tabs.select(1)

		print("ClickPlay:", int(time.time()), "[",datetime.now().isoformat(sep=' ',timespec='seconds'),"]")

		# self.tabs.select('Run')
		# print(self.scriptlist)
		# Start a thread to start the threads
		# https://realpython.com/intro-to-python-threading/
		# self.run_start_threads()
		# x = threading.Thread(target=thread_function, args=(1,))

		datafiletime = datetime.now().strftime("%Y%m%d_%H%M%S")
		if len(self.config['Plan']['ScenarioFile'])>0:
			filename = os.path.basename(self.config['Plan']['ScenarioFile'])
			sname = os.path.splitext(filename)[0]
			self.run_name = "{}_{}".format(datafiletime, sname)
		else:
			self.run_name = "{}_{}".format(datafiletime, "Scenario")
		# print("run_start_threads: self.run_name:", self.run_name)


		self.run_start = 0
		self.run_end = 0
		self.run_paused = False
		self.robot_schedule = {"RunName": "", "Agents": {}, "Scripts": {}}
		t = threading.Thread(target=self.run_start_threads)
		t.start()
		ut = threading.Thread(target=self.delayed_UpdateRunStats)
		ut.start()


	def ClickStop(self, _event=None):
		self.run_end = int(time.time()) #time now
		print("ClickStop: run_end", self.run_end, "[",datetime.now().isoformat(sep=' ',timespec='seconds'),"]")
		self.robot_schedule["End"] = self.run_end

		for agnt in self.robot_schedule["Agents"].keys():
			for grurid in self.robot_schedule["Agents"][agnt].keys():
				self.robot_schedule["Agents"][agnt][grurid]["EndTime"] = self.run_end



	def addScriptRow(self):
		self.scriptcount += 1

		row = int("{}".format(self.scriptcount))
		self.scriptlist.append({})

		self.scriptlist[self.scriptcount]["Index"] = self.scriptcount

		idx = ttk.Label(self.scriptgrid, text=str(self.scriptcount))
		idx.grid(column=self.plancolidx, row=self.scriptcount, sticky="nsew")

		num = "10"
		usr = ttk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout")
		usr.config(validatecommand=lambda: self.sr_users_validate(row))
		usr.grid(column=self.plancolusr, row=self.scriptcount, sticky="nsew")
		usr.insert(0, num)
		self.scriptlist[self.scriptcount]["Users"] = int(num)

		num = "0"
		dly = ttk.Entry(self.scriptgrid, width=5, justify="right", validate="focusout")
		dly.config(validatecommand=lambda: self.sr_delay_validate(row))
		dly.grid(column=self.plancoldly, row=self.scriptcount, sticky="nsew")
		dly.insert(0, num)
		self.scriptlist[self.scriptcount]["Delay"] = int(num)

		num = "1800"	# 30 minutes
		rmp = ttk.Entry(self.scriptgrid, width=7, justify="right", validate="focusout")
		rmp.config(validatecommand=lambda: self.sr_rampup_validate(row))
		rmp.grid(column=self.plancolrmp, row=self.scriptcount, sticky="nsew")
		rmp.insert(0, num)
		self.scriptlist[self.scriptcount]["RampUp"] = int(num)

		# num = "18000"  # 18000 sec = 5 hours
		num = "7200" # 3600 sec = 1hr, 7200 sec = 2 hours
		run = ttk.Entry(self.scriptgrid, width=8, justify="right", validate="focusout")
		run.config(validatecommand=lambda: self.sr_run_validate(row))
		run.grid(column=self.plancolrun, row=self.scriptcount, sticky="nsew")
		run.insert(0, num)
		self.scriptlist[self.scriptcount]["Run"] = int(num)



		# nme = ttk.Label(self.scriptgrid, text="   ")
		# nme.grid(column=self.plancolnme, row=self.scriptcount, sticky="nsew")

		fgf = ttk.Frame(self.scriptgrid)
		fgf.grid(column=self.plancolscr, row=self.scriptcount, sticky="nsew")
		scr = ttk.Entry(fgf, state="readonly", justify="right")
		scr.grid(column=0, row=0, sticky="nsew")
		# scrf = ttk.Button(fgf, text="...", width=1, command=partial(self.sr_file_validate, self.scriptcount))
		# scrf = ttk.Button(fgf, text="...", width=1, command=lambda: self.sr_file_validate(self.scriptcount))
		scrf = ttk.Button(fgf, text="...", width=1)
		scrf.config(command=lambda: self.sr_file_validate(row))
		scrf.grid(column=1, row=0, sticky="nsew")

		# tst = ttk.Entry(self.scriptgrid, width=30)
		self.scriptlist[row]["Test"] = ""
		self.scriptlist[row]["TestVar"] = tk.StringVar(self.scriptlist[row]["Test"], name="row{}".format(row))
		# variable.set(None)
		# lambda: self.sr_test_validate(row)
		# variable.trace("w", lambda _: self.sr_test_validate(row))
		# variable.trace("w", lambda: self.sr_test_validate(row))
		self.scriptlist[row]["TestVar"].trace("w", self.sr_test_validate)
		tst = ttk.OptionMenu(self.scriptgrid, self.scriptlist[row]["TestVar"], None, "test")
		# tst.config(command=lambda: self.sr_test_validate(row))
		tst.config(width=20)
		tst.grid(column=self.plancoltst, row=self.scriptcount, sticky="nsew")


		self.scriptgrid.columnconfigure(self.plancoladd, weight=1)
		new = ttk.Button(self.scriptgrid, text="X", command=lambda: self.sr_remove_row(row), width=1)
		new.grid(column=self.plancoladd, row=self.scriptcount, sticky="nsew")

		self.pln_update_graph()


	def sr_validate(self):
		# self.sr_users_validate()
		pass

	def sr_users_validate(self, *args):
		# print("sr_users_validate: args:",args)
		if args:
			r = args[0]
			v = None
			if len(args)>1:
				v = args[1]
				# print("sr_users_validate: grid_slaves:",self.scriptgrid.grid_slaves(column=self.plancolusr, row=r))
				# print("sr_users_validate: grid_slaves[0]:",self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0])
				self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].delete(0,'end')
				self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].insert(0,v)

			usrs = self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].get()
			# print("Row:", r, "Users:", usrs)
			self.scriptlist[r]["Users"] = int(usrs)
			self.plan_scnro_chngd = True
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				usrs = self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].get()
				# print("Row:", r, "Users:", usrs)
				self.scriptlist[r]["Users"] = int(usrs)
				self.plan_scnro_chngd = True
		self.pln_update_graph()
		return True

	def sr_delay_validate(self, *args):
		# print(args)
		if args:
			r = args[0]
			v = None
			if len(args)>1:
				v = args[1]
				self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].delete(0,'end')
				self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].insert(0,v)
			dly = self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].get()
			# print("Row:", r, "Delay:", dly)
			if len(dly)>0:
				self.scriptlist[r]["Delay"] = int(dly)
				self.plan_scnro_chngd = True
			else:
				self.scriptlist[r]["Delay"] = 0
				self.plan_scnro_chngd = True
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				dly = self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].get()
				# print("Row:", r, "Delay:", dly)
				self.scriptlist[r]["Delay"] = int(dly)
				self.plan_scnro_chngd = True
		self.pln_update_graph()
		return True

	def sr_rampup_validate(self, *args):
		# print(args)
		if args:
			r = args[0]
			v = None
			if len(args)>1:
				v = args[1]
				self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].delete(0,'end')
				self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].insert(0,v)
			rmp = self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].get()
			# print("Row:", r, "RampUp:", rmp)
			self.scriptlist[r]["RampUp"] = int(rmp)
			self.plan_scnro_chngd = True
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				rmp = self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].get()
				# print("Row:", r, "RampUp:", rmp)
				self.scriptlist[r]["RampUp"] = int(rmp)
				self.plan_scnro_chngd = True
		self.pln_update_graph()
		return True

	def sr_run_validate(self, *args):
		# print(args)
		if args:
			r = args[0]
			v = None
			if len(args)>1:
				v = args[1]
				self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].delete(0,'end')
				self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].insert(0,v)
			run = self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].get()
			# print("Row:", r, "Run:", run)
			self.scriptlist[r]["Run"] = int(run)
			self.plan_scnro_chngd = True
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				run = self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].get()
				# print("Row:", r, "Run:", run)
				self.scriptlist[r]["Run"] = int(run)
				self.plan_scnro_chngd = True
		self.pln_update_graph()
		return True

	def hash_file(self, file):
		BLOCKSIZE = 65536
		hasher = hashlib.md5()
		with open(file, 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
		# print(file, hasher.hexdigest())
		return hasher.hexdigest()

	def remove_hash(self, hash):
		remove = True
		# self.scriptlist[r]["ScriptHash"]
		print("remove_hash: scriptlist:", self.scriptlist)
		for scr in self.scriptlist:
			if self.scriptlist[scr]["ScriptHash"] == hash:
				remove = False

		if remove:
			del self.scriptfiles[hash]

	def find_dependancies(self, hash):
		keep_going = True
		checking = False

		# determin if is a robot file
		# print("find_dependancies", self.scriptfiles[hash])
		localpath = self.scriptfiles[hash]['localpath']
		localdir = os.path.dirname(localpath)
		# print("find_dependancies: localdir", localdir)
		filename, fileext = os.path.splitext(localpath)

		# print("find_dependancies: filename, fileext:", filename, fileext)

		if (fileext in [".robot", ".Robot"] and keep_going):
			with open(localpath, 'rb') as afile:
				for fline in afile:
					line = fline.decode("utf-8")
					if checking and '*** ' in line:
						checking = False

					if checking:
						# print("find_dependancies: line", line)
						try:
							if line.strip()[:1] != "#" and ('Resource' in line or 'Variables' in line or 'Metadata	File' in line):
								linearr = line.strip().split()
								# print("find_dependancies: linearr", linearr)
								if len(linearr)>1:
									# print("find_dependancies: linearr[1]", linearr[1])
									resfile = linearr[-1]
									localrespath = os.path.join(localdir, resfile)
									# print("find_dependancies: localrespath", localrespath)
									if os.path.isfile(localrespath):
										newhash = self.hash_file(localrespath)
										# print("find_dependancies: newhash", newhash)
										self.scriptfiles[newhash] = {
												'id': newhash,
												'localpath': localrespath,
												'relpath': resfile,
												'type': linearr[0]
											}
									else:
										filelst = glob.glob(localrespath)
										for file in filelst:
											# print("find_dependancies: file", file)
											relpath = file.replace(localdir, "")[1:]
											# print("find_dependancies: relpath", relpath)
											newhash = self.hash_file(file)
											# print("find_dependancies: newhash", newhash)
											self.scriptfiles[newhash] = {
													'id': newhash,
													'localpath': file,
													'relpath': relpath,
													'type': linearr[0]
												}

						except Exception as e:
							print("find_dependancies: line", line)
							print("find_dependancies: Exception", e)
							print("find_dependancies: linearr", linearr)

					if '*** Settings' in line:
						checking = True


	def sr_file_validate(self, r, *args):
		# print(r)
		fg = self.scriptgrid.grid_slaves(column=self.plancolscr, row=r)[0].grid_slaves()
		# print(fg)
		# print(fg[1].get())
		if args:
			scriptfile = args[0]
		else:
			scriptfile = str(tkf.askopenfilename(initialdir=self.config['Plan']['ScriptDir'], title = "Select Robot Framework File", filetypes = (("Robot Framework","*.robot"),("all files","*.*"))))
		# print("scriptfile:", scriptfile)
		if len(scriptfile)>0:
			fg[1].configure(state='normal')
			fg[1].select_clear()
			fg[1].delete(0, 'end')
			fg[1].insert(0, os.path.basename(scriptfile))
			fg[1].configure(state='readonly')
			self.scriptlist[r]["Script"] = scriptfile
			# print("test: ", fg[1].get())
			script_hash = self.hash_file(scriptfile)
			self.scriptlist[r]["ScriptHash"] = script_hash

			self.scriptfiles[script_hash] = {
				"id": script_hash,
				"localpath": scriptfile,
				"relpath": os.path.basename(scriptfile),
				"type": "script"
			}

			t = threading.Thread(target=self.find_dependancies, args=(script_hash, ))
			t.start()

			self.config['Plan']['ScriptDir'] = os.path.dirname(scriptfile)
			self.saveini()
			self.sr_test_genlist(r)
		else:
			fg[1].configure(state='normal')
			fg[1].delete(0, 'end')
			# fg[1].select_clear()
			fg[1].configure(state='readonly')
			if "ScriptHash" in self.scriptlist[r]:
				oldhash = self.scriptlist[r]["ScriptHash"]
				t = threading.Thread(target=self.remove_hash, args=(oldhash, ))
				t.start()

			self.scriptlist[r]["Script"] = ''
			self.scriptlist[r]["ScriptHash"] = ''


		self.plan_scnro_chngd = True
		self.pln_update_graph()
		return True

	# def sr_test_validate(self, r, *args):
	def sr_test_validate(self, *args):
		# print("sr_test_validate: args:", args)
		# r = int(args[0][-1:])+1
		r = int(args[0][3:])
		# print("sr_test_validate: r:", r)

		# if 0 in self.scriptgrid.grid_slaves:
		# print("sr_test_validate: grid_slaves:", self.scriptgrid.grid_slaves(column=self.plancoltst, row=r))
		tol = self.scriptgrid.grid_slaves(column=self.plancoltst, row=r)[0]
		# print("sr_test_validate: tol:", tol)

		v = None
		if len(args)>1 and len(args[1])>1:
			v = args[1]
			# print("sr_test_validate: v:", v)
			self.scriptlist[r]["TestVar"].set(v)
			self.scriptlist[r]["Test"] = v
		else:
			# print("sr_test_validate: else")
			# print("sr_test_validate: scriptlist[r][TestVar].get():", self.scriptlist[r]["TestVar"].get())
			self.scriptlist[r]["Test"] = self.scriptlist[r]["TestVar"].get()

		# print("sr_test_validate: scriptlist[r]:", self.scriptlist[r])
		# print("sr_test_validate: scriptlist[r][TestVar].get():", self.scriptlist[r]["TestVar"].get())

		self.plan_scnro_chngd = True

		self.pln_update_graph()
		return True

	def sr_test_genlist(self, r):
		# print("Script File:",self.scriptlist[r]["Script"])
		tcsection = False
		tclist = [""]
		regex = "^\*{3}[\D](Test Case|Task)"
		with open(self.scriptlist[r]["Script"]) as f:
			for line in f:
				# print("sr_test_genlist: tcsection:",tcsection, "	line:", line)
				if tcsection and line[0:3] == "***":
					tcsection = False
				if re.search(regex, line):
					# print("sr_test_genlist: re.search(",regex, ",", line,")", re.search(regex, line))
					tcsection = True
				if tcsection:
					if line[0:1] not in ('\t', ' ', '*', '#', '\n', '\r'):
						# print("", line[0:1], "")
						tclist.append(line[0:-1])
		# print(tclist)
		tol = self.scriptgrid.grid_slaves(column=self.plancoltst, row=r)[0]
		# print(tol)
		tol.set_menu(*tclist)
		# print(tol)

	def sr_remove_row(self, r):
		# print("sr_remove_row:", r)
		# print(self.scriptgrid)
		# print(self.scriptgrid[r])
		relmts = self.scriptgrid.grid_slaves(row=r, column=None)
		# print(relmts)
		for elmt in relmts:
			elmt.destroy()
		self.scriptlist[r] = {}

		self.pln_update_graph()
		return True

	def pln_update_graph(self):
		# print("pln_update_graph")
		# print(self.pln_graph)
		# print(self.pln_graph.winfo_width(), self.pln_graph.winfo_height())
		# print(self.scriptlist)
		graphh = self.pln_graph.winfo_height()
		graphw = self.pln_graph.winfo_width()

		# print("graphh", graphh, "graphw", graphw)


		axissz = 10
		if graphw > graphh:
			axissz = int(graphh * 0.1)
		else:
			axissz = int(graphw * 0.1)

		#  work out max users
		mxuser = 0
		mxusero = 0
		for grp in self.scriptlist:
			if "Users" in grp.keys():
				mxuser += grp["Users"]
				mxusero += grp["Users"]
		# print("mxuser", mxuser)
		mxuser = int(mxuser*1.15)
		# print("mxuser", mxuser)


		#  work out max duration
		mxdur = 0
		for grp in self.scriptlist:
			if "Users" in grp.keys():
				dur = grp["Delay"] + (grp["RampUp"]*2) + grp["Run"]
				dur = int(dur * 1.03)
				if mxdur < dur:
					mxdur = dur
		# print("mxdur", mxdur)

		totcounts = {}
		totcounts[0] = 0
		# print('totcounts', totcounts)
		# print('totcounts.keys()', totcounts.keys())
		totinc = 1
		if mxdur > 60:
			totinc = 10
		if mxdur > 3600:
			totinc = 60

		self.pln_graph.delete("all")

		ym0 = graphh-int(axissz/2)	# point below x axis
		ym1 = graphh-axissz			# x axis line
		ym2 = 0						# top of graph

		xm1 = axissz			# y axis line
		if mxusero>99:
			xm1 = (axissz*2)
		if mxusero>9999:
			xm1 = (axissz*3)

		xm0 = int(xm1/2)			# point to left of y axis
		xm2 = graphw				# right hand site of x axis
		xmt = xm2-xm1				# total lenght of x axis

		# y-axis
		self.pln_graph.create_line(xm1, ym1, xm1, ym2)
		# x-axis
		# self.pln_graph.create_line(10, graphh-10, graphw, graphh-10, fill="blue")
		self.pln_graph.create_line(xm1, ym1, xm2, ym1)

		# draw zero
		self.pln_graph.create_line(xm1, ym0, xm1, ym1)
		self.pln_graph.create_line(xm0, ym1, xm1, ym1)
		self.pln_graph.create_text([xm0, ym0], text="0")

		# populate x axis	(time)
		# print("populate x axis	(time)")
		# print("mxdur", mxdur)
		durinc = 1
		if mxdur > 30:		# 30 sec
			durinc = 15		# 15 sec
		if mxdur > 120:		# 120 = 2 min
			durinc = 60		# 1 min
		if mxdur > 1800:	# 60 * 30 = 1800 sec = 1/2hr
			durinc = 300	# 5 min
		if mxdur > 3600:	# 60 * 60 = 3600 sec = 1hr
			durinc = 600	# 10 min
		if mxdur > 7200:	# 60 * 60 * 2 = 7200 sec = 2hr
			durinc = 3600	# 1 hr
		if mxdur > 36000:	# 60 * 60 * 10= 36000 sec = 10hr
			durinc = 7200	# 2 hr
		# print("durinc", durinc)

		if mxdur>0:
			mrkpct = durinc / (mxdur * 1.0)
		else:
			mrkpct = 0
		# print("mrkpct", mrkpct)
		# print("xm1", xm1, "xm2", xm2, "xm2-xm1", xm2-xm1)
		mrkinc = int(xmt * mrkpct)
		# print("mrkinc", mrkinc)
		if mrkinc < 1:
			mrkinc = 1

		tmmrk = xm1 + mrkinc
		# print("tmmrk", tmmrk)
		# print("durinc", durinc)
		durmrk = durinc
		# print("durmrk", durmrk)
		gridcolour = "#cfcfcf"
		while durmrk < mxdur+1:
			# print("x1", tmmrk, "y1", ym0, "x2", tmmrk, "y2", ym1)
			# self.pln_graph.create_line(tmmrk, ym0, tmmrk, ym1)
			self.pln_graph.create_line(tmmrk, ym1, tmmrk, ym2, fill=gridcolour)
			# print("format_sec({})".format(durmrk), self.format_sec(durmrk))
			# txmrk = tmmrk-int(mrkinc*0.25)
			# print("txmrk", txmrk)
			# self.pln_graph.create_text([txmrk, ym0], text=self.format_sec(durmrk))
			self.pln_graph.create_text([tmmrk, ym0], text=self.format_sec(durmrk))

			tmmrk += mrkinc
			# print("tmmrk", tmmrk)
			durmrk += durinc
			# print("durmrk", durmrk)



		# populate y axis	(Users)
		# print("populate y axis	(Users)")
		usrinc = 1
		if mxuser > 15:
			usrinc = int((mxusero/100)+0.9)*10
		# print("mxusero", mxusero)
		# print("usrinc", usrinc)
		# print("usrinc", usrinc)
		usrmrk = usrinc
		if mxuser>0:
			mrkpct = usrmrk / (mxuser * 1.0)
		else:
			mrkpct = 0
		# print("mrkpct", mrkpct)
		txtmrkoffset = int(int(ym1 * mrkpct)/2)
		# print("txtmrkoffset", txtmrkoffset)
		while usrmrk < mxuser:
			# print("usrmrk", usrmrk)
			mrkpct = usrmrk / (mxuser * 1.0)
			# print("mrkpct", mrkpct)
			mrk = ym1 - int(ym1 * mrkpct)
			# print("mrk", mrk)
			txtmrk = mrk + txtmrkoffset
			# self.pln_graph.create_line(xm0, mrk, xm1, mrk)
			self.pln_graph.create_line(xm1, mrk, xm2, mrk, fill=gridcolour)
			# self.pln_graph.create_text([xm0, txtmrk], text="{}".format(usrmrk))
			self.pln_graph.create_text([xm0, mrk], text="{}".format(usrmrk))

			usrmrk += usrinc


		xlen = xmt

		delx = 0
		for grp in self.scriptlist:
			if "Users" in grp.keys():
				colour = self.line_colour(grp["Index"])
				# print("Line colour", colour)
				# delay
				delaypct = grp["Delay"] / (mxdur * 1.0)
				delx = int(xlen * delaypct) + xm1
				# print("Delay", grp["Delay"], "delx", delx)
				# ramp-up
				rusx = delx
				rusy = graphh-axissz
				usrpct = grp["Users"] / (mxuser * 1.0)
				# print("RampUp:Users", grp["Users"], "/ mxuser", mxuser, " = usrpct", usrpct)
				rudpct = grp["RampUp"] / (mxdur * 1.0)
				ruex = int(xlen * rudpct) + delx
				# print("RampUp:RampUp", grp["RampUp"], "ruex", ruex)
				ruey = rusy - int(rusy * usrpct)
				# print("RampUp:rusx", rusx, "rusy", rusy, "ruex", ruex, "ruey", ruey)
				self.pln_graph.create_line(rusx, rusy, ruex, ruey, fill=colour)

				# Run
				rnpct = grp["Run"] / (mxdur * 1.0)
				rnex = int(xlen * rnpct) + ruex
				# print("rnex", rnex)
				self.pln_graph.create_line(ruex, ruey, rnex, ruey, fill=colour)

				# ramp-down
				rdex = rnex+(ruex-rusx)
				# print("rdex", rdex)
				self.pln_graph.create_line(rnex, ruey, rdex, rusy, fill=colour, dash=(4, 4))

				# totcounts = {}
				# totinc = 1
				# if mxdur > 60:
				totnxt = 0
				# print('totcounts', totcounts)
				# print('totcounts.keys()', totcounts.keys())
				while totnxt < mxdur:
					totnxt += totinc
					# print('totnxt', totnxt)
					if totnxt not in totcounts.keys():
						totcounts[totnxt] = 0
					# if totnxt < grp["Delay"]:
					# 	totcounts[totnxt] += 0
					if totnxt > grp["Delay"] and totnxt < (grp["RampUp"] + grp["Delay"]):
						# calculate users during RampUp
						rupct = (totnxt - grp["Delay"]) /grp["RampUp"]
						# print('rupct', rupct)
						ruusr = int(grp["Users"] * rupct)
						# print('ruusr', ruusr)
						# print('totcounts', totcounts)
						# print('totcounts[totnxt]', totcounts[totnxt])
						totcounts[totnxt] = int(totcounts[totnxt] + ruusr)
						# print('ruusr', ruusr)
						# print('totcounts[totnxt]', totcounts[totnxt])

					if totnxt > (grp["Delay"] + grp["RampUp"] - 1) \
						and totnxt < (grp["Delay"] + grp["RampUp"] + grp["Run"] + 1):
						# all users running
						# print('run:totnxt', totnxt)
						# print('run:grp["Users"]', grp["Users"])
						totcounts[totnxt] += grp["Users"]
					if totnxt > (grp["RampUp"] + grp["Delay"] + grp["Run"]) \
						and totnxt < (grp["Delay"] + (grp["RampUp"] *2 ) + grp["Run"]):
						# calculate users during RampDown
						# print('RampDown:totnxt', totnxt)
						drr = grp["Delay"] + grp["RampUp"] + grp["Run"]
						# print('RampDown:drr', drr)
						rdsec = totnxt - drr
						# print('RampDown:rdsec', rdsec)

						rdpct = rdsec /grp["RampUp"]
						# print('RampDown:rdpct', rdpct)
						ruusr = int(grp["Users"] * rdpct)
						# print('RampDown:ruusr', ruusr)
						totcounts[totnxt] += grp["Users"] - ruusr

		totcolour = "#000000"
		# totcolour = "#0459af"
		sy = graphh-axissz
		prevkey = 0
		prevx = delx
		prevy = sy
		prevval = 0
		rampdown = False
		for key in totcounts.keys():
			if rampdown == False and totcounts[key] < prevval:
				rampdown = True
				# print(prevkey, totcounts[prevkey])

				usrpct = prevval / (mxuser * 1.0)
				# print("Users", totcounts[key], "/ mxuser", mxuser, " = usrpct", usrpct)
				newy = sy - int(sy * usrpct)

				keypct = prevkey / (mxdur * 1.0)
				# print("key", key, "/ mxdur", mxdur, " = keypct", keypct)
				newx = int(xlen * keypct) + delx

				# print("prevx", prevx, "prevy", prevy, "newx", newx, "newy", newy)

				self.pln_graph.create_line(prevx, prevy, newx, newy, fill=totcolour)

				prevx = newx
				prevy = newy

			if totcounts[key] != prevval:
				# print(key, totcounts[key])
				prevval = totcounts[key]

				usrpct = totcounts[key] / (mxuser * 1.0)
				# print("Users", totcounts[key], "/ mxuser", mxuser, " = usrpct", usrpct)
				newy = sy - int(sy * usrpct)

				keypct = key / (mxdur * 1.0)
				# print("key", key, "/ mxdur", mxdur, " = keypct", keypct)
				newx = int(xlen * keypct) + delx

				# print("prevx", prevx, "prevy", prevy, "newx", newx, "newy", newy)

				if rampdown:
					self.pln_graph.create_line(prevx, prevy, newx, newy, fill=totcolour, dash=(4, 4))
				else:
					self.pln_graph.create_line(prevx, prevy, newx, newy, fill=totcolour)

				prevx = newx
				prevy = newy


			prevkey = key

	def run_start_threads(self):
		# print('run_start_threads')

		if self.run_end>0 and int(time.time())>self.run_end:
			self.run_paused = True

		totusrs = 0
		curusrs = 0

		# print("run_start_threads: self.scriptlist:", self.scriptlist)
		for grp in self.scriptlist:
			if "Users" in grp:
				# print("run_start_threads: totusrs", totusrs, " 	grp:", grp)
				totusrs += int(grp["Users"])
				# print("run_start_threads: totusrs", totusrs)


		# print('run_start_threads: curusrs:', curusrs, "	totusrs:", totusrs, "	run_paused:", self.run_paused)
		while curusrs < totusrs:
			# print("run_start_threads: while totusrs", totusrs, " 	curusrs:", curusrs)
			# totusrs = 0

			if "Start" not in self.robot_schedule:
				self.robot_schedule["Start"] = 0


			if self.run_end>0 and int(time.time())>self.run_end:
				break

			if self.run_paused and int(time.time())<self.run_end:
				nxtagent = self.get_next_agent()
				if nxtagent is None:
					self.run_paused = True
					# print('No Agents available to run Robots! (if)')
					print('No Agents available to run Robots!')
					time.sleep(10)
				else:
					self.run_paused = False
					tkm.showinfo("RFSwarm - Info", "Agents available to run Robots, test will now resume.")
					print('Agents available to run Robots, resuming.')
			else:
				for grp in self.scriptlist:
					# print("run_start_threads: grp", grp)
					if "Test" in grp.keys() and len(grp["Test"])>0:
						# print("run_start_threads: while totusrs", totusrs, " 	curusrs:", curusrs)
						# print("run_start_threads: grp[Index]", grp['Index'])

						nxtagent = self.get_next_agent()
						# print('run_start_threads: next_agent', nxtagent)

						if nxtagent is None:
							# MsgBox = tkm.askyesno('Save Scenario','Do you want to save the current scenario?')
							self.run_paused = True
							tkm.showwarning("RFSwarm - Warning", "No Agents available to run Robots!\nTest run is paused, please add agents to continue or click stop to abort.")

							# print('No Agents available to run Robots! (else)')
							print('No Agents available to run Robots!')
							# print('No Agents available to run Robots!')
							# break

						colour = self.line_colour(grp["Index"])
						# print("run_start_threads: Line colour", colour)

						if self.run_start < 1:
							self.run_start = int(time.time()) #time now
							self.robot_schedule = {}
							self.robot_schedule["RunName"] = self.run_name
							self.robot_schedule["Agents"] = {}
							self.robot_schedule["Scripts"] = {}
							self.robot_schedule["Start"] = self.run_start

							stm = time.localtime(self.robot_schedule["Start"])
							self.display_run['start_time'].set("  {}  ".format(time.strftime("%H:%M:%S", stm)))

							self.run_end = int(time.time()) + grp["Run"]
							self.robot_schedule["End"] = self.run_end

							# totusrs = 0

						gid = grp["Index"]
						# print("run_start_threads: gid", gid, " 	robot_schedule[Scripts].keys()", self.robot_schedule["Scripts"].keys())
						if gid not in self.robot_schedule["Scripts"].keys():
							self.robot_schedule["Scripts"][gid] = {}
							# print("run_start_threads: totusrs", totusrs)
							# totusrs += int(grp["Users"])
							# print("run_start_threads: totusrs", totusrs)

						time_elapsed = int(time.time()) - self.run_start
						# print('run_start_threads: time_elapsed', time_elapsed, "Delay", grp["Delay"])
						if time_elapsed > grp["Delay"] - 1:
							uid = 0
							nxtuid = len(self.robot_schedule["Scripts"][gid]) + 1
							# print('run_start_threads: nxtuid', nxtuid)
							# Determine if we should start another user?
							if nxtuid < grp["Users"]+1:
								rupct = (time_elapsed - grp["Delay"]) /grp["RampUp"]
								# print('run_start_threads: rupct', rupct)
								ruusr = int(grp["Users"] * rupct)
								# print('run_start_threads: nxtuid', nxtuid, 'ruusr', ruusr)
								if nxtuid < ruusr+1:
									uid = nxtuid
									grurid = "{}_{}".format(gid,uid)
									# print('run_start_threads: uid', uid)
									self.robot_schedule["Scripts"][gid][uid] = grurid

									if nxtagent not in self.robot_schedule["Agents"].keys():
										self.robot_schedule["Agents"][nxtagent] = {}

									self.robot_schedule["Agents"][nxtagent][grurid] = {
										"ScriptHash": grp["ScriptHash"],
										"Test": grp["Test"],
										"StartTime": int(time.time()),
										"EndTime": int(time.time()) + grp["Run"],
										"id": grurid
									}

									self.run_end = int(time.time()) + grp["Run"]
									self.robot_schedule["End"] = self.run_end

									self.Agents[nxtagent]["AssignedRobots"] += 1
									# print("self.Agents[",nxtagent,"][AssignedRobots]:", self.Agents[nxtagent]["AssignedRobots"])

									curusrs += 1
									# print("run_start_threads: robot_schedule", self.robot_schedule)

						if self.run_end>0 and int(time.time())>self.run_end:
							self.run_paused = True
							break

						time.sleep(0.1)
						etm = time.gmtime(int(time.time()) - self.robot_schedule["Start"])
						self.display_run['elapsed_time'].set("  {}  ".format(time.strftime("%H:%M:%S", etm)))


	def run_manage_user_thread(self, gid, uid):
		# # print("gid", gid, "uid", uid)
		# fnow = time.time()
		# now  = int(fnow)
		# endtm = self.run_threads[gid][uid]["RunUntill"]
		#
		# script = self.run_threads[gid][uid]["Script"]
		# scriptdir = os.path.dirname(script)
		# filename = os.path.basename(script)
		# testcs = self.run_threads[gid][uid]["Test"]
		#
		# # print("{}_{}: cur Time	{}	end time:{}".format(gid, uid, now, endtm))
		# while now < endtm:
		# 	secleft = endtm - now
		#
		# 	# print("{}_{}: cur Time	{}	end time:{}".format(gid, uid, now, endtm))
		# 	# print("{}_{}: Running	{}:{}	time left:{}".format(gid, uid, filename, testcs, secleft))
		# 	time.sleep(random.randint(1,10))
		#
		# 	farr = os.path.splitext(filename)
		#
		# 	odir = "{}/{}/{}_{}_{}_{}".format(scriptdir, self.run_start, farr[0], gid, uid, now)
		#
		# 	# print("{}_{}: odir:{}".format(gid, uid, odir))
		#
		# 	if not os.path.exists(odir):
		# 		os.makedirs(odir)
		#
		#
		# 	# logFileName = "{}_{}_{}_{}_{}.log".format(farr[0], testcs, gid, uid, int(time.time()))
		# 	logFileName = "{}/{}.log".format(odir, testcs)
		# 	# print("{}_{}: logFileName:{}".format(gid, uid, logFileName))
		#
		# 	cmd = ["robot"]
		# 	cmd.append("-t")
		# 	cmd.append("'"+testcs+"'")
		# 	# cmd.append(testcs)
		# 	cmd.append("-d")
		# 	cmd.append(odir)
		#
		# 	cmd.append(script)
		#
		# 	# print("{}_{}: cmd:{}".format(gid, uid, cmd))
		# 	# print("{}_{}: expected cmdline :{}".format(gid, uid, " ".join(cmd)))
		# 	result = subprocess.call(" ".join(cmd), shell=True)
		#
		# 	outputFile = "{}/{}".format(odir, "output.xml")
		# 	t = threading.Thread(target=self.run_proces_output, args=(gid, uid, outputFile))
		# 	t.start()
		#
		#
		# 	fnow = time.time()
		# 	now  = int(fnow)
		#
		# secleft = endtm - now
		# # print("{}_{}: cur Time	{}	end time:{}".format(gid, uid, now, endtm))
		# print("{}_{}: Finished	{}:{}	time left:{}".format(gid, uid, filename, testcs, secleft))
		pass


	def run_proces_output(self, gid, uid, output):
		# # print('run_proces_output', gid, uid, "output", output)
		# tree = ET.parse(output)
		# root = tree.getroot()
		# # print('run_proces_output', gid, uid, "root", root)
		# for kw in root.findall('suite/test/kw'):
		# 	# print(Variable.get('name'), Variable.text)
		# 	name = kw.get('name')
		# 	# print('run_proces_output', gid, uid, "name", name, "kw", kw)
		# 	# print('run_proces_output', gid, uid, "name", name, "list kw", list(kw))
		#
		# 	msgxpath = "suite/test/kw[@name='{}']//msg".format(name)
		# 	msg = root.find(msgxpath)
		# 	# print('run_proces_output', gid, uid, "msg", msg)
		# 	if msg is not None:
		# 		# print('run_proces_output', gid, uid, "msg.text", msg.text)
		# 		txname = msg.text
		# 	else:
		# 		txname = name
		# 	# print('run_proces_output', gid, uid, "txname", txname)
		#
		# 	statusxpath = "suite/test/kw[@name='{}']/status".format(name)
		# 	status = root.find(statusxpath)
		# 	# status = kw.status
		# 	if status is not None:
		# 		# print('run_proces_output', gid, uid, "status", status)
		# 		# print('run_proces_output', gid, uid, "status: status", status.get("status"))
		# 		# print('run_proces_output', gid, uid, "status: starttime", status.get("starttime"))
		# 		# print('run_proces_output', gid, uid, "status: endtime", status.get("endtime"))
		# 		# status.get("starttime")
		#
		# 		# run_proces_output 1 1 status: starttime 20190915 14:59:34.348
		# 		s_stime = datetime.strptime(status.get("starttime"), "%Y%m%d %H:%M:%S.%f")
		# 		s_etime = datetime.strptime(status.get("endtime"), "%Y%m%d %H:%M:%S.%f")
		#
		# 		elapsed = s_etime.timestamp() - s_stime.timestamp()
		#
		# 		# print('run_proces_output', gid, uid, txname, status.get("status"), elapsed)
		pass


	def line_colour(self, grp):
		if grp<len(self.defcolours):
			return self.defcolours[grp]
		else:
			newcolour = self.make_colour()
			# print("Initial newcolour:", newcolour)
			while newcolour in self.defcolours:
				# print(self.defcolours)
				newcolour = self.make_colour()
				# print("newcolour:", newcolour)
			self.defcolours.append(newcolour)
			return newcolour

	def make_colour(self):
		hexchr = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
		r1 = hexchr[random.randrange(len(hexchr))]
		r2 = hexchr[random.randrange(len(hexchr))]
		g1 = hexchr[random.randrange(len(hexchr))]
		g2 = hexchr[random.randrange(len(hexchr))]
		b1 = hexchr[random.randrange(len(hexchr))]
		b2 = hexchr[random.randrange(len(hexchr))]
		return "#{}{}{}{}{}{}".format(r1,r2,g1,g2,b1,b2)

	def format_sec(self, sec_in):
		if sec_in>3599:
			hrs = int(sec_in/3600)
			mins = int(sec_in/60) - (hrs*60)
			# secs = sec_in - (((hrs*60) + mins) * 60)
			if mins>0:
				return "{}:{}".format(hrs, mins)
			return "{}".format(hrs)
		if sec_in>59:
			mins = int(sec_in/60)
			secs = sec_in - (mins * 60)
			if secs>0:
				return "{}:{}".format(mins, secs)
			return "{}".format(mins)
		return "{}".format(sec_in)

	def run_agent_server(self):

		if 'Server' not in self.config:
			self.config['Server'] = {}
			self.saveini()

		if 'BindIP' not in self.config['Server']:
			self.config['Server']['BindIP'] = ''
			self.saveini()

		if 'BindPort' not in self.config['Server']:
			self.config['Server']['BindPort'] = "8138"
			self.saveini()

		srvip = self.config['Server']['BindIP']
		srvport = int(self.config['Server']['BindPort'])
		if len(srvip)>0:
			srvdisphost = srvip
		else:
			srvdisphost = socket.gethostname()


		server_address = (srvip, srvport)
		self.agenthttpserver = ThreadingHTTPServer(server_address, AgentServer)
		print("Starting Agent Server", "http://{}:{}/".format(srvdisphost, srvport))
		self.agenthttpserver.serve_forever()

	def register_agent(self, agentdata):
		# print("register_agent: agentdata:", agentdata)

		# if "AssignedRobots" not in self.Agents[agnt].keys():
		# 	print("get_next_agent: addinig AssignedRobots to ", agnt)
		# 	print("get_next_agent: self.Agents:", self.Agents)
		# 	self.Agents[agnt]["AssignedRobots"] = 0
		AssignedRobots = 0
		if agentdata["AgentName"] in self.Agents and "AssignedRobots" in self.Agents[agentdata["AgentName"]]:
			AssignedRobots = self.Agents[agentdata["AgentName"]]["AssignedRobots"]
		agentdata["AssignedRobots"] = AssignedRobots

		agentdata["LastSeen"] = int(time.time())
		if "Status" not in agentdata.keys():
			agentdata["Status"] = "Unknown"
			if agentdata["Robots"] == 0:
				agentdata["Status"] = "Ready"
			if agentdata["Robots"] > 0:
				agentdata["Status"] = "Running"

		load = max([agentdata["CPU%"], agentdata["MEM%"], agentdata["NET%"] ])
		agentdata["LOAD%"] = load
		if load>80:
			agentdata["Status"] = "Warning"
		if load>95:
			agentdata["Status"] = "Critical"

		self.Agents[agentdata["AgentName"]] = agentdata

		# print("register_agent: agentdata:", agentdata)

		# self.UpdateAgents()
		t = threading.Thread(target=self.UpdateAgents)
		t.start()

		# save data to db
		agnttbldata = (agentdata["AgentName"], agentdata["Status"], agentdata["LastSeen"],
						agentdata["Robots"], agentdata["LOAD%"], agentdata["CPU%"],
						agentdata["MEM%"], agentdata["NET%"])
		# sqlcmd = 'INSERT INTO Agents VALUES (?,?,?,?,?,?,?,?)'
		#
		# self.dbqueue["Write"].append({"SQL":sqlcmd, "VALUES": agnttbldata})
		self.dbqueue["Agents"].append(agnttbldata)

	def register_result(self, AgentName, result_name, result, elapsed_time, start_time, end_time, index, vuser, iter, sequence):
		# print("register_result")
		resdata = (index, vuser, iter, AgentName, sequence, result_name, result, elapsed_time, start_time, end_time)
		# print("register_result: resdata:", resdata)
		self.dbqueue["Results"].append(resdata)
		# print("register_result: dbqueue Results:", self.dbqueue["Results"])

		ut = threading.Thread(target=self.delayed_UpdateRunStats)
		ut.start()


	def str2bool(self, instr):
		# print("str2bool: instr:", instr)
		if instr in ["True", "true", "TRUE", "YES", "yes", "Yes", "1"]:
			return True
		return False

	#
	# menu functions
	#
	def mnu_file_New(self, _event=None):
		# print("mnu_file_New")
		if len(self.config['Plan']['ScenarioFile'])>0:
			self.mnu_file_Close()

		self.updateTitle()
		while self.scriptcount > 0:
			self.sr_remove_row(self.scriptcount)
			self.scriptcount += -1
		self.scriptlist = [{}]
		self.addScriptRow()


	def mnu_file_Open(self, _event=None):
		# print("mnu_file_Open")
		# print("mnu_file_Open: _event:", _event, "	Type:", type(_event))
		# if type(_event) is not "<class 'str'>":
		if type(_event) is not type(""):
			self.mnu_file_Close()	# ensure any previous scenario is closed and saved if required
			ScenarioFile = str(tkf.askopenfilename(initialdir=self.config['Plan']['ScenarioDir'], title = "Select RFSwarm Scenario File", filetypes = (("RFSwarm","*.rfs"),("all files","*.*"))))
		else:
			ScenarioFile = _event
		# print("mnu_file_Open: ScenarioFile:", ScenarioFile)
		self.config['Plan']['ScenarioDir'] = os.path.dirname(ScenarioFile)
		self.config['Plan']['ScenarioFile'] = ScenarioFile
		self.saveini()
		self.updateTitle()

		filedata = configparser.ConfigParser()
		# print("mnu_file_Open: filedata: ", filedata)

		if os.path.isfile(ScenarioFile):
			# print("mnu_file_Open: ScenarioFile: ", ScenarioFile)
			filedata.read(ScenarioFile)

		# print("mnu_file_Open: filedata: ", filedata)

		scriptcount = 0
		if "Scenario" in filedata:
			# print("mnu_file_Open: Scenario:", filedata["Scenario"])
			if "scriptcount" in filedata["Scenario"]:
				scriptcount = int(filedata["Scenario"]["scriptcount"])
				# print("mnu_file_Open: scriptcount:", scriptcount)


		# print("mnu_file_Open: self.scriptgrid:", self.scriptgrid)
		# print("mnu_file_Open: self.scriptgrid.grid_size():", self.scriptgrid.grid_size())
		# for r in range(self.scriptgrid.grid_size()[1]):

		for i in range(scriptcount):
			ii = i+1
			istr = str(ii)
			if istr in filedata:
				# if i not in self.scriptlist:
				# 	self.scriptlist.append({})
				# 	self.scriptlist[ii]["Index"] = ii
				if ii+1 > self.scriptgrid.grid_size()[1]:		# grid_size tupple: (cols, rows)
					self.addScriptRow()
				# users = 13
				# print("mnu_file_Open: filedata[", istr, "][users]:", filedata[istr]["users"])
				# self.scriptlist[ii]["users"] = filedata[istr]["users"]
				self.sr_users_validate(ii, int(filedata[istr]["users"]))
				# delay = 0
				# print("mnu_file_Open: filedata[", istr, "][delay]:", filedata[istr]["delay"])
				# self.scriptlist[ii]["delay"] = filedata[istr]["delay"]
				self.sr_delay_validate(ii, int(filedata[istr]["delay"]))
				# rampup = 60
				# print("mnu_file_Open: filedata[", istr, "][rampup]:", filedata[istr]["rampup"])
				# self.scriptlist[ii]["rampup"] = filedata[istr]["rampup"]
				self.sr_rampup_validate(ii, int(filedata[istr]["rampup"]))
				# run = 600
				# print("mnu_file_Open: filedata[", istr, "][run]:", filedata[istr]["run"])
				# self.scriptlist[ii]["run"] = filedata[istr]["run"]
				self.sr_run_validate(ii, int(filedata[istr]["run"]))
				# script = /Users/dave/Documents/GitHub/rfswarm/robots/OC_Demo_2.robot
				# print("mnu_file_Open: filedata[", istr, "][script]:", filedata[istr]["script"])
				# self.scriptlist[ii]["script"] = filedata[istr]["script"]
				self.sr_file_validate(ii, filedata[istr]["script"])
				# test = Browse Store Product 1
				# print("mnu_file_Open: filedata[", istr, "][test]:", filedata[istr]["test"])
				# self.scriptlist[ii]["test"] = filedata[istr]["test"]
				self.sr_test_validate("row{}".format(ii), filedata[istr]["test"])


		self.plan_scnro_chngd = False

	def mnu_file_Save(self, _event=None):
		# print("mnu_file_Save")
		if len(self.config['Plan']['ScenarioFile'])<1:
			self.mnu_file_SaveAs()
		else:

			# print("mnu_file_Save: ScenarioFile:", self.config['Plan']['ScenarioFile'])
			# print("mnu_file_Save: scriptlist:", self.scriptlist)
			filedata = configparser.ConfigParser()

			if 'Scenario' not in filedata:
				filedata['Scenario'] = {}

			scriptidx = str(0)
			if 'ScriptCount' not in filedata['Scenario']:
				# filedata['Scenario']['ScriptCount'] = str(len(self.scriptlist)-1)
				filedata['Scenario']['ScriptCount'] = scriptidx

			for scrp in self.scriptlist:
				# print("mnu_file_Save: scrp:", scrp)
				if 'Index' in scrp:
					scriptidx = str(scrp['Index'])

					if scriptidx not in filedata:
						filedata[scriptidx] = {}
					for key in scrp.keys():
						# print("mnu_file_Save: key:", key)
						if key not in ['Index', 'TestVar', 'ScriptHash']:
							filedata[scriptidx][key] = str(scrp[key])
							# print("mnu_file_Save: filedata[",scriptidx,"][",key,"]:", filedata[scriptidx][key])

			filedata['Scenario']['ScriptCount'] = scriptidx
			with open(self.config['Plan']['ScenarioFile'], 'w') as sf:    # save
			    filedata.write(sf)


			# self.config = configparser.ConfigParser()
			# scrdir = os.path.dirname(__file__)
			# # print("RFSwarmGUI: __init__: scrdir: ", scrdir)
			# self.gui_ini = os.path.join(scrdir, "RFSwarmGUI.ini")
			# if 'Plan' not in self.config:
			# 	self.config['Plan'] = {}
			# 	self.saveini()
			#
			# if 'ScriptDir' not in self.config['Plan']:
			# 	self.config['Plan']['ScriptDir'] = self.dir_path
			# 	self.saveini()

			# if os.path.isfile(self.gui_ini):
			# with open(self.gui_ini, 'w') as configfile:    # save
			#     self.config.write(configfile)

			self.updateTitle()

	def mnu_file_SaveAs(self, _event=None):
		# print("mnu_file_SaveAs")
		# asksaveasfilename
		ScenarioFile = str(tkf.asksaveasfilename(\
						initialdir=self.config['Plan']['ScenarioDir'], \
						title = "Save RFSwarm Scenario File", \
						filetypes = (("RFSwarm","*.rfs"),("all files","*.*"))\
						))
		# print("mnu_file_SaveAs: ScenarioFile:", ScenarioFile)
		if ScenarioFile is not None and len(ScenarioFile)>0:
			# ScenarioFile
			filetupl = os.path.splitext(ScenarioFile)
			# print("mnu_file_SaveAs: filetupl:", filetupl)
			if filetupl != ".rfs":
				ScenarioFile += ".rfs"
				# print("mnu_file_SaveAs: ScenarioFile:", ScenarioFile)
			self.config['Plan']['ScenarioFile'] = ScenarioFile
			self.mnu_file_Save()

	def mnu_file_Close(self, _event=None):
		# print("mnu_file_Close")
		if self.plan_scnro_chngd:
			MsgBox = tkm.askyesno('RFSwarm - Save Scenario','Do you want to save the current scenario?')
			# print("mnu_file_Close: MsgBox:", MsgBox)
			if MsgBox:
				self.mnu_file_Save()

		self.config['Plan']['ScenarioFile'] = ""
		self.mnu_file_New()

	# # https://www.daniweb.com/programming/software-development/code/216634/jpeg-image-embedded-in-python
	def get_icon(self, icontext):
		# print("get_icon: icontext:", icontext)
		# http://www.famfamfam.com/lab/icons/silk/
		files = {}
		# files["New"] = "famfamfam_silk_icons/icons/page_white.edt.gif"
		# files["Save"] = "famfamfam_silk_icons/icons/disk.gif"
		# files["SaveAs"] = "famfamfam_silk_icons/icons/disk_multiple.gif"
		# files["Open"] = "famfamfam_silk_icons/icons/folder_explore.gif"
		# files["Play"] = "famfamfam_silk_icons/icons/resultset_next.gif"
		# files["Stop"] = "famfamfam_silk_icons/icons/stop.gif"
		# files["New"] = "famfamfam_silk_icons/icons/_finder.png"
		# files["Play"] = "famfamfam_silk_icons/icons/_finder.png"
		# files["Play"] = "famfamfam_silk_icons/icons/disk_multiple.png"

		if icontext in files:
			print("get_icon: icontext:", icontext)
			scrdir = os.path.dirname(__file__)
			# print("get_icon: scrdir:", scrdir)
			imgfile = os.path.join(scrdir, files[icontext])
			# print("get_icon: pngfile:", pngfile)
			if os.path.isfile(imgfile):
				print("get_icon: isfile: imgfile:", imgfile)
				with open(imgfile,"rb") as f:
					png_raw = f.read()
				print("get_icon: img_raw:", img_raw)
				# b64 = base64.encodestring(img_raw)
				# img_text = 'img_b64 = \\\n"""{}"""'.format(b64)

				self.imgdata[icontext] = tk.PhotoImage(file=imgfile)
				print("get_icon: imgdata[icontext]:", self.imgdata[icontext])


				return self.imgdata[icontext]



		# png_b64 = """b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAC4SURBVCjPdZFbDsIgEEWnrsMm7oGGfZro\nhxvU+Iq1TyjU60Bf1pac4Yc5YS4ZAtGWBMk/drQBOVwJlZrWYkLhsB8UV9K0BUrPGy9cWbng2CtE\nEUmLGppPjRwpbixUKHBiZRS0p+ZGhvs4irNEvWD8heHpbsyDXznPhYFOyTjJc13olIqzZCHBouE0\nFRMUjA+s1gTjaRgVFpqRwC8mfoXPPEVPS7LbRaJL2y7bOifRCTEli3U7BMWgLzKlW/CuebZPAAAA\nAElFTkSuQmCC\n'"""

		b64 = {}
		# gif's
		b64["New"] = b'GIF89a\x10\x00\x10\x00\xe7\xfd\x00\x00\x00\x00\x01\x01\x01\x02\x02\x02\x03\x03\x03\x04\x04\x04\x05\x05\x05\x06\x06\x06\x07\x07\x07\x08\x08\x08\t\t\t\n\n\n\x0b\x0b\x0b\x0c\x0c\x0c\r\r\r\x0e\x0e\x0e\x0f\x0f\x0f\x10\x10\x10\x11\x11\x11\x12\x12\x12\x13\x13\x13\x14\x14\x14\x15\x15\x15\x16\x16\x16\x17\x17\x17\x18\x18\x18\x19\x19\x19\x1a\x1a\x1a\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!"""###$$$%%%&&&\'\'\'((()))***+++,,,---...///000111222333444555666777888999:::;;;<<<===>>>???@@@AAABBBCCCDDDEEEFFFGGGHHHIIIJJJKKKLLLMMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~\x7f\x7f\x7f\x80\x80\x80\x81\x81\x81\x82\x82\x82\x83\x83\x83\x84\x84\x84\x85\x85\x85\x86\x86\x86\x87\x87\x87\x88\x88\x88\x89\x89\x89\x8a\x8a\x8a\x8b\x8b\x8b\x8c\x8c\x8c\x8d\x8d\x8d\x8e\x8e\x8e\x8f\x8f\x8f\x90\x90\x90\x91\x91\x91\x92\x92\x92\x93\x93\x93\x94\x94\x94\x95\x95\x95\x96\x96\x96\x97\x97\x97\x98\x98\x98\x99\x99\x99\x9a\x9a\x9a\x9b\x9b\x9b\x9c\x9c\x9c\x9d\x9d\x9d\x9e\x9e\x9e\x9f\x9f\x9f\xa0\xa0\xa0\xa1\xa1\xa1\xa2\xa2\xa2\xa3\xa3\xa3\xa4\xa4\xa4\xa5\xa5\xa5\xa6\xa6\xa6\xa7\xa7\xa7\xa8\xa8\xa8\xa9\xa9\xa9\xaa\xaa\xaa\xab\xab\xab\xac\xac\xac\xad\xad\xad\xae\xae\xae\xaf\xaf\xaf\xb0\xb0\xb0\xb1\xb1\xb1\xb2\xb2\xb2\xb3\xb3\xb3\xb4\xb4\xb4\xb5\xb5\xb5\xb6\xb6\xb6\xb7\xb7\xb7\xb8\xb8\xb8\xb9\xb9\xb9\xba\xba\xba\xbb\xbb\xbb\xbc\xbc\xbc\xbd\xbd\xbd\xbe\xbe\xbe\xbf\xbf\xbf\xc0\xc0\xc0\xc1\xc1\xc1\xc2\xc2\xc2\xc3\xc3\xc3\xc4\xc4\xc4\xc5\xc5\xc5\xc6\xc6\xc6\xc7\xc7\xc7\xc8\xc8\xc8\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xce\xce\xce\xcf\xcf\xcf\xd0\xd0\xd0\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd6\xd6\xd6\xd7\xd7\xd7\xd8\xd8\xd8\xd9\xd9\xd9\xda\xda\xda\xdb\xdb\xdb\xdc\xdc\xdc\xdd\xdd\xdd\xde\xde\xde\xdf\xdf\xdf\xe0\xe0\xe0\xe1\xe1\xe1\xe2\xe2\xe2\xe3\xe3\xe3\xe4\xe4\xe4\xe5\xe5\xe5\xe6\xe6\xe6\xe7\xe7\xe7\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xeb\xeb\xeb\xec\xec\xec\xed\xed\xed\xee\xee\xee\xef\xef\xef\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\x8e\x00\xff\x89\x19H\xb0\xa0\x98\x7f\x08\x11\x8a\xc1\xb7\x8f\x9f\xc3\x87\xf8(\x1dL(f\x1f\xbdz\x18\xe3\xbdK\xc7\xef\\\xa5\x89\x02\xf9\xdd\xcbw\xef\xde<x\xea\xf8\xd9\xa3\x97i\xa2\x18~\xf9b\xde\xb3\'o\xddC~.\xf95\xd4\x89\xaf^<v\xea\xcc\xe1Tx\x93g=y\xef\xda\r\rYt\x1f>{\xf3\xe4-}Y\x94\x9f\xbe|\xf6\xecM\xad\xaa3&\xbe\xad\x0f\xf7\x89\xd5\xa7\x0f\xdf\xd7\x9ca\xf7\x91]\x0b6\xadX\xb1m\xb9:t\x99O\xae\xc3|.\r\xea\x1d\xf8/ \x00;'
		b64["Save"] = b'GIF89a\x10\x00\x10\x00\xe7\x98\x001`\xa61`\xa71`\xa81a\xa82a\xa82a\xa92a\xaa2b\xaa2b\xab2c\xac3c\xad3d\xae3d\xaf3e\xb04e\xb14f\xb24f\xb34g\xb45h\xb55h\xb65h\xb75i\xb75i\xb85i\xb95j\xba6j\xba6j\xbb6k\xbb6k\xbc7k\xba8k\xbb8l\xbb9l\xbc:m\xbb;n\xbd>p\xbb^\x89\xc9d\x8c\xc8e\x8c\xc8e\x8d\xc9e\x8d\xcaf\x8d\xc9g\x8e\xc9i\x90\xcah\x90\xcdl\x92\xcbm\x92\xcbj\x93\xcfm\x96\xd3p\x99\xd6y\x98\xc7q\x99\xd8r\x9b\xd9|\x9a\xc8s\x9b\xd9s\x9b\xdar\x9c\xdb|\x9b\xc9t\x9c\xdat\x9d\xdct\x9e\xddu\x9e\xdev\x9f\xddv\x9f\xdew\x9f\xde\x81\x9e\xccw\xa0\xdew\xa0\xdfx\xa1\xe0x\xa2\xe0y\xa2\xe1z\xa2\xe0z\xa2\xe1z\xa2\xe2z\xa3\xe1z\xa3\xe2z\xa3\xe3{\xa3\xe1{\xa3\xe2\x84\xa3\xcez\xa4\xe3{\xa4\xe2{\xa4\xe3}\xa6\xe6}\xa7\xe7~\xa8\xe7~\xa8\xe8\x8a\xa7\xd2\x80\xaa\xe9\x8e\xab\xd5\x95\xb0\xda\x88\xc0b\x9a\xb5\xdd\x9f\xba\xe1\xa4\xbe\xe4\xa9\xc2\xe7\xad\xc5\xea\xad\xc6\xeb\xb3\xca\xed\xb6\xcc\xee\xb8\xce\xef\xba\xd0\xee\xbb\xd0\xef\xbd\xd0\xec\xbe\xd2\xf0\xc3\xd5\xef\xc2\xd5\xf2\xc2\xdc\xbf\xc5\xd8\xf2\xc7\xd9\xf4\xc9\xdc\xf4\xcc\xdd\xf5\xd0\xdf\xf6\xd1\xdf\xf6\xd1\xe0\xf6\xd1\xe0\xf7\xd8\xe5\xf6\xd9\xe5\xf7\xdb\xe6\xf7\xdb\xe7\xf7\xdb\xe7\xf8\xdd\xe8\xf8\xdf\xe9\xf8\xdf\xe9\xf9\xe1\xec\xf9\xe2\xec\xf9\xe3\xed\xf9\xe5\xed\xfa\xe8\xf0\xfa\xe9\xf0\xfa\xea\xf0\xfa\xe9\xf1\xfa\xea\xf1\xfb\xeb\xf1\xfb\xed\xf2\xfb\xee\xf3\xfb\xee\xf4\xfb\xee\xf4\xfc\xef\xf4\xfc\xf0\xf5\xfc\xf1\xf6\xfc\xf2\xf6\xfc\xf3\xf7\xfd\xf3\xf8\xfd\xf6\xf9\xfd\xf6\xfa\xfd\xf6\xfa\xfe\xf7\xfa\xfd\xf7\xfa\xfe\xf8\xfa\xfe\xf7\xfb\xfe\xf8\xfb\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xfe\x00\xffq\x18\xc8a\xc3\x06\r\x1a@\x88\x08\xe1a\xc4?\x81r\xe6\\\xb2\x04i\x91 C\x90&\x15\xd2s\x86\x84\xc08X$E*q\x88P\xa3K\x8c\xfa\xe0)sf\x04\x078V\x181*1\x08\xd1$H\x80\xf2\xd8Q\x92\xa6\x02\x877U\x00\x01J\x11\xe8Q%E{\xee\xd4)\xf2e\xc2\x067T\xf8\xf0\xf1\x93h\x92\xa3?J\xe9\x08\xf1\x12aC\x9b)%N\xa8h\xe1b\x85\x89\x12hut\x81\xa0\x81\x8d\x14&P\xa28ibd\xc8\x0f\x1e8vpq\xa0A\r\x13&N\x9cD1BDH\x8f\x1d7lha\xa0\x01\xcd\x92%J\xe6\x12\x01\xe2c\x07\x8d\x191\xb2(\xc8`&\xc9\xa5\xcf\xa0C\xc3\xb8\x82\xc0\x03\x19#\x94\xb6\xa8^\xad\x1a\xd2\x8b\'\x06>\x8cABi\x8d\xed\xdb\xb6!\xb1\x08B\xa0\x83\x98#\xa9Y\xaf\x86\x84"G\x00\x0ca\xc0\x84^~\xa9\x86\x8c\x00\x19.X\xa0 !\xc2\x83\x06\x0b\x12\x1c(  \x00\x80\x01\x01\x01\x00;'
		b64["SaveAs"] = b'GIF89a\x10\x00\x10\x00\xc6u\x00._\xa63h\xba:i\xaa>j\xabDm\xabDp\xb0W~\xbbQ\x7f\xc3S\x7f\xc1S\x80\xc5T\x81\xc4U\x83\xc6X\x84\xc3]\x84\xbf[\x86\xc7]\x88\xc8_\x89\xc9`\x89\xc9a\x8a\xc7a\x8b\xc9b\x8b\xc8a\x8b\xcbh\x8b\xd3e\x8d\xcae\x8d\xccl\x8b\xcdn\x8a\xd7f\x8e\xc7m\x8b\xdah\x8e\xcdl\x8d\xdci\x90\xcdp\x8f\xe1n\x93\xcco\x96\xccn\x97\xd4q\x97\xd0q\x98\xd0s\x98\xces\x99\xd1u\x99\xd1s\x9a\xd4u\x9a\xd0w\x9a\xd2w\x9b\xd2w\x9c\xd2y\x9c\xd5z\x9d\xd3{\x9c\xddw\x9e\xd9x\x9e\xd8{\x9e\xd4x\x9f\xd8y\x9f\xdby\xa0\xd9z\xa0\xd9{\xa1\xdc}\xa2\xd9|\xa3\xdb\x80\xa3\xd5}\xa3\xde\x85\xa2\xdd\x82\xa4\xd6~\xa5\xdd\x80\xa6\xdd\x81\xa7\xe1\x81\xa7\xe2\x85\xa8\xdd\x84\xbfQ\x8f\xae\xda\x84\xbfT\x8c\xaf\xe4\x96\xb2\xee\x91\xb6\xd6\x92\xb5\xe6\x97\xb6\xea\x9a\xb6\xef\x99\xb8\xea\x9c\xbc\xe0\x98\xc9o\x99\xc9q\x9e\xbc\xee\x9b\xbd\xed\xa1\xbe\xea\xa1\xbf\xea\xa1\xbf\xef\x9e\xc0\xef\xb3\xc7\xe3\xb0\xcd\xf3\xbb\xcd\xe6\xba\xce\xef\xb8\xd2\xf4\xc7\xee\x87\xc7\xee\x8c\xd7\xf4\xa2\xd7\xf6\xa2\xe6\xf0\xef\xe5\xf1\xed\xe6\xf1\xed\xe6\xf1\xef\xe8\xf3\xea\xe9\xf4\xe4\xed\xf1\xf8\xea\xf3\xf3\xed\xf5\xf3\xf2\xf6\xfb\xf1\xf8\xff\xf7\xfb\xff\xfa\xfb\xfd\xfa\xfc\xfd\xfb\xfc\xfd\xfb\xfc\xfe\xff\xff\xdd\xff\xff\xe0\xfc\xfd\xfe\xfd\xfd\xfe\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\x7f\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb2\x80\x7f\x82\x83\x84\x85\x82#3%>\x1d\x1f*\'\x14\x86\x7f\x18XuWu\x97uT\x11\x86\x0eV9/;E+,-$\x90\x84\x0fU([uYtuif\x9a\x84\x17M\x10R\x88\x8a\x8c\x8e\xa7\x7f\x13J\x15Q\x93\x95\x98\x99\x9b\x7f\nK&S\x9du!\x97kjG\x12\x82\x07L"I\xa9mosrlnC\x08\x82\x0bZ\x1bN\xb5?@:7642\r\x82\x01\x0c\tH\xbfBA<851)\x06\x84\xe4\xc9\xce\x88\x19\x03&\x0c\x1a\x17\x05\x08\xc9\xb3F\x86\xc8\x13(F\xca\xc0\x10`\x88\x1c\x1c.^\xbet\x89\xd3c\x80!y\x16@x\xe0\xa0!\x03\x01\x00\x91R\n\n\x04\x00;'
		b64["Open"] = b'GIF89a\x10\x00\x10\x00\xe7\x87\x00\xb6\x83I\xba\x8aP\xd8\x87-\xbc\x8cT\xd8\x88-\xd9\x8e3\xc8\x95^\xda\x945\xc9\x98b\xda\x9a6\x97\xa3\xb6\x99\xa3\xb2\xda\xa16\xda\xa67\xd4\xa7G\xda\xaa6\xda\xab5\xda\xab6\xda\xae4\xda\xaf5\xda\xaf6\xb5\xaf\xa8\xb2\xb3\xa7\xda\xb36\x9a\xb6\xd9\xd9\xb44\xdb\xb6<\x9b\xba\xdf\x9e\xbd\xe0\xd3\xb8\x9c\xa4\xc1\xe4\xde\xb9\x92\xa8\xc2\xe0\xa7\xc4\xe5\xa8\xc4\xe5\xe1\xc2^\xa9\xc5\xe6\xb3\xc6\xc8\xaa\xc6\xe6\xe2\xc3_\xe2\xc3`\xab\xc6\xe6\xe9\xc1s\xe3\xc7k\xe4\xc7k\xe5\xcat\xb4\xcd\xe9\xed\xcaj\xea\xcbl\xba\xcf\xe2\xe6\xcdy\xb8\xd0\xeb\xb3\xd1\xf3\xd3\xd2\xa3\xee\xcfr\xee\xcfv\xee\xce\x88\xef\xd0z\xd4\xd4\xa9\xef\xd2\x80\xef\xd3\x85\xbd\xd8\xf3\xf2\xd5\x81\xef\xd4\x94\xc1\xda\xf4\xf3\xd7\x86\xf5\xdac\xf3\xd8\x8e\xc4\xdc\xf4\xc9\xdc\xf2\xc6\xdd\xf4\xc9\xdd\xf2\xc5\xde\xf5\xf3\xda\x96\xc6\xde\xf5\xf6\xder\xf6\xdev\xf4\xdc\x93\xf4\xdb\x9e\xc7\xe0\xf7\xca\xe0\xf6\xf5\xde\x91\xf5\xde\x94\xf4\xdd\xa7\xcb\xe2\xf8\xf7\xe1\x81\xcd\xe2\xf8\xcc\xe3\xf8\xf7\xe2\x85\xf5\xe0\x9f\xce\xe3\xf8\xf7\xe3\x8b\xf6\xe1\xac\xf8\xe4\x8e\xd6\xe4\xf3\xd6\xe5\xf5\xf8\xe5\x91\xd3\xe6\xf8\xf8\xe6\x95\xdb\xe7\xf5\xf9\xe8\x9c\xf9\xe9\xa1\xf9\xe9\xa4\xdc\xea\xf8\xf6\xe9\xc9\xdf\xec\xf8\xfa\xec\xac\xfa\xed\xb3\xfb\xef\xb9\xfa\xf0\xdc\xfc\xf2\xc8\xfc\xf6\xd8\xfb\xf6\xe8\xfb\xf7\xe9\xfb\xf7\xea\xfd\xfa\xf1\xfe\xfa\xef\xfd\xfa\xf2\xfe\xfb\xee\xfe\xfb\xef\xfe\xfc\xf0\xfe\xfc\xf1\xfe\xfc\xf2\xfe\xfc\xf3\xfe\xfc\xf6\xfe\xfc\xf7\xff\xfc\xf5\xfe\xfd\xf4\xff\xfd\xf6\xff\xfd\xf8\xff\xfd\xfa\xfe\xfe\xfd\xff\xfe\xfd\xff\xfe\xfe\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xca\x00\xff\t\x1cH\xb0\xe0\xbf\x0c#P(<\xa1\xc1\xe0\xc0\x0b\x83\x0c\x15"dH\x0e\x8b\x15\x18e\xb4\x188\xa1O\x97(Y\xb8\xdc\xf9\xb3\'\xcf\x1d;\x82(\x08|0GJ\x13\x1f/`\xf0\xd8\x91\xe3\x86\x8d8\x12\x04B\x80\xf3\x03\x87\n4z\xf6\xe8\xc1s\xd2P\x04\x81\r\x0c\x05\x02\xe4g\xcf\x1b1:Jp\x08\x11\xc3\x81@\x06|\xdc\xb0QCfK\r\x17c\xd2\x1c\x99aA`\x82:k\xcc\x88\xc1\xc2\xc4\x84\x17(J\x90\x84\x01!\xf0\x00\x9d2`\xaa,\x11\xc2\xe1\x8c\x11"=\xacx\x10X\xa0\xcd\x14\'I\x86\x04\x11\xf1\x05H\x8f\x1eW0\x0c$ \x80\x80e\x02\x15\x8ahyB\x85\xc6\x02\x87\x04S\x90\xd8\xa0\xa0\x83\x01\xd0\x06\x11|\x00\x80\xba\xe0\x80\x00\xad\r\x06\x04\x00;'
		b64["Play"] = b'GIF89a\x10\x00\x10\x00\xa56\x00\x14A\xb7\x15E\xb9\x16J\xbd\x16N\xc0\x17P\xbd\x18S\xc0\x18Y\xc4\x19Y\xc6\x1ab\xc6\x1ab\xc9#n\xcd,r\xcd;q\xcc<t\xcf5w\xd2=w\xd0?z\xd0C\x7f\xd3C\x84\xd6G\x84\xd6K\x88\xd6S\x8e\xdb`\x95\xdda\x97\xddb\x97\xe1n\xa0\xe2r\xa1\xdft\xa2\xe2t\xa3\xe0u\xa3\xdfu\xa4\xe3w\xa4\xe0y\xa6\xe0y\xa7\xe6~\xa8\xe1|\xa9\xe1|\xa9\xe8~\xa9\xe8\x80\xaa\xe3\x81\xab\xe2\x81\xab\xe3\x80\xab\xe8\x80\xab\xea\x87\xaf\xe4\x87\xb0\xe8\x8a\xb1\xe4\x90\xb5\xe7\x92\xb7\xe8\x99\xbb\xe9\x99\xbb\xea\xa1\xc1\xec\xa3\xc2\xed\xa8\xc7\xee\xad\xc8\xef\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00?\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06K\xc0\x9fpH,\x1a\x8f\xc8T\tiT\x916Lb\xa8\xc6\xb2D\x85\x19\xda\xcc3\xb9bd/\xd8e\x11\xad\xc4L\xa8\x16\x05\xc1\x94\xb88\x9fS\xe4\xc0t\xac4#H!\xaa\x10\x81\x1e\x04W\t\x1d\r\x02W?\x06\x0c\x01\x87?\x03\x00\x8c\x90\x91A\x00;'
		b64["Stop"] = b'GIF89a\x10\x00\x10\x00\xe7\x84\x00\xd5>5\xd8G>\xd7H@\xd8H@\xfaB%\xd9KC\xd9KD\xfdF(\xdaOG\xfeI,\xffK,\xdbUM\xffO0\xffO1\xffP2\xffP3\xddYQ\xdc[S\xffU7\xde^T\xffY;\xffY<\xffZ<\xdebZ\xff\\?\xff^@\xff^A\xf9`H\xffcF\xe0jc\xffdF\xfdeJ\xe0le\xe4lc\xffgH\xffgN\xffiK\xffnO\xffnP\xffoP\xe4ul\xffpO\xe3xq\xffsU\xfftU\xfftZ\xffxY\xffyZ\xe7\x81y\xff~_\xff~`\xff\x7f_\xe5\x84}\xff\x80`\xff\x81g\xff\x83e\xe6\x8a\x85\xe8\x8b\x83\xff\x89i\xf2\x8b}\xf7\x8d}\xe7\x91\x8b\xff\x8dm\xff\x8en\xfa\x8e}\xff\x8eo\xff\x8fs\xea\x93\x8c\xff\x90o\xfc\x90\x7f\xf4\x94\x86\xff\x93s\xff\x93t\xfa\x93\x84\xff\x93x\xe9\x97\x92\xe9\x98\x92\xf6\x96\x89\xff\x95\x84\xea\x9a\x95\xfa\x97\x89\xff\x98v\xff\x98x\xff\x99x\xff\x99\x87\xea\x9e\x98\xff\x9b\x8a\xed\x9f\x98\xff\x9d|\xeb\xa0\x9b\xff\x9e|\xeb\xa2\x9d\xff\xa0}\xff\xa0~\xeb\xa3\x9e\xff\xa1\x85\xff\xa2\x81\xec\xa5\xa0\xff\xa1\x90\xff\xa5\x81\xfa\xa5\x96\xff\xa7\x84\xff\xa7\x85\xff\xaa\x86\xef\xac\xa5\xee\xad\xa6\xff\xab\x89\xff\xaa\x98\xfb\xad\x9e\xfb\xad\x9f\xff\xae\x91\xff\xaf\x8b\xf0\xb1\xa9\xfc\xb2\xa2\xfb\xba\xac\xff\xbb\x9c\xff\xbb\xa6\xff\xbf\xa0\xff\xbe\xab\xff\xc2\xa3\xfb\xc3\xb4\xff\xc4\xb1\xfc\xc8\xb7\xfc\xcd\xbc\xff\xcd\xb8\xff\xce\xb9\xff\xcf\xbb\xfc\xd1\xc1\xff\xd1\xbd\xfc\xd3\xc2\xfc\xd4\xc4\xff\xd6\xc1\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\xff\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x08\xc6\x00\xff\t\x1cH\xb0\xa0A/a\xb6d\xa9\xb2\xc4\xe0@8\x81\x06\x01\xf2\xd3G\xcf\x15\x87i\x04\xddy\xa3\xa6L\x177x\x86\x14D\xf3\xa7\xce\x193`\xb0H!\xf2EN\x8e\x81O\xf6\xcc\x19\x03F\xcb\x14$At\xd4P\xc2\x06\x84@&|\xb8`\x99r\xe4\x87\x8e\x1b2\\\xa4X\xd3A`\x8f<Q\x8a\x1e\x8d\xf1bE\t\x11b.\x08\xc4a\xc7\xc7\xd4\x17,N\x90\xe0\x80\xc1J\x04\x814\xe8\xcc\xa0\xba\xc2\x04\t\x0f\x1a(4\xa0\xb2@\xa0\x8a8BR\x94x\xab\xc1\x82\x04\x05#\x92\x0c\x18\x08\xa3\x8d\x8d\x0c\x19*Hxp\xe0C\x93\t\x05Q\x90i\xe1\x80A\x02\x02\x1b\x8c@p\x18\x02\x8a\x93"@x\xec\xd8\xec\xf0\x9f\x01\x04\x05\x04\x04\x00P\xba5\xc1\x80\x00;'

		# png's
		# b64["New"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAC4SURBVCjPdZFbDsIgEEWnrsMm7oGGfZro\nhxvU+Iq1TyjU60Bf1pac4Yc5YS4ZAtGWBMk/drQBOVwJlZrWYkLhsB8UV9K0BUrPGy9cWbng2CtE\nEUmLGppPjRwpbixUKHBiZRS0p+ZGhvs4irNEvWD8heHpbsyDXznPhYFOyTjJc13olIqzZCHBouE0\nFRMUjA+s1gTjaRgVFpqRwC8mfoXPPEVPS7LbRaJL2y7bOifRCTEli3U7BMWgLzKlW/CuebZPAAAA\nAElFTkSuQmCC\n"""
		# b64["Save"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAH+SURBVBgZBcE9i11VGAbQtc/sO0OCkqhg\nhEREAwpWAWUg8aMVf4KFaJEqQtAipTZWViKiCGOh2Ap2gmJhlSIWFsFOxUK0EsUM3pl79n4f12qH\nb3z3Fh7D83gC95GOJsDe0ixLk5Qq/+xv/Lw9Xd+78/HLX3Y8fXTr2nWapy4eCFKxG7Fby97SnDlY\ntMbxthyfzHO//nl85fNvfvnk8MbX5xa8IHx1518Vkrj54Q+qQms2vVmWZjdiu5ZR2rT01166/NCZ\ng/2PFjwSVMU6yjoC1oq+x6Y3VbHdlXWExPd379nf7Nmejv2Os6OC2O4KLK0RNn3RNCdr2Z5GJSpU\n4o+/TkhaJ30mEk5HwNuvX7Hpi76wzvjvtIwqVUSkyjqmpHS0mki8+9mPWmuWxqYvGkbFGCUAOH/+\nQevYI9GFSqmaHr5wkUYTAlGhqiRRiaqiNes6SOkwJwnQEqBRRRJEgkRLJGVdm6R0GLMQENE0Ekmk\nSkQSVVMqopyuIaUTs0J455VLAAAAAODW0U/GiKT0pTWziEj44PZ1AAAAcPPqkTmH3QiJrlEVDXDt\n0qsAAAAAapa5BqUnyaw0Am7//gUAAAB49tEXzTmtM5KkV/y2G/X4M5fPao03n/sUAAAAwIX7y5yB\nv9vhjW/fT/IkuSp5gJKElKRISYoUiSRIyD1tufs/IXxui20QsKIAAAAASUVORK5CYII=\n"""
		# b64["SaveAs"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAJFSURBVDjLpZPNS1RhFMZ/5733zkzjR/ZB\nCUpoJdUiBCkll4m0CUKJIGpVSLjyL2gntDFop6shAolWbcSNIW0ircHBUHCloo3VjNY0jjP3831b\nWA5ai8Bnfc7vPOfhHDHGcBjZAENji7N1cSj7IcdqY2zkKoiC2qSFNsKPYoXpTPbBynj/4j8BlbLL\n9c4L3OqoZWLmM4/vXdpX9OJtHq0lBXQdBIgxhvtPZmZ7ui+yspZrjwKfWExxtMbh66YLAgj4geZn\nyd2YzmT7Vsb75/c5UEqwDLgVl55r57hxuYY3c18Y6mtDgO1KSBBETMwV0VpeA2f3ARKOwvUCcgWX\n9bzH0NhqvC4Okx9zBzNpPdGQ4OHIrJnOZLtWxvs/2AChNnhRiFIKy8j/ZjILiALYLgc4YnO8zsJS\nIWUv4Pt2CMBU+tteoxtC0YN8wUdEV1eItMHCIdSagru5l0kQaZ4OdqC1wQAWhqQNnudR3PGrANu2\naGmE9FJATSxJwinhegHDr1ZRAmGk0ZHGAMYYMJB0dh0ogOVs6VNqcoGtosYv1+9lYikHERvBQsQC\nozBGCMIQ3w+rDtKjvQMAd4bfL59vFqYzQasjNoM36wi1vzvHgBFNwo4x8nKNreJOFfBHy9nSXGpy\noSPSYOGgqZCae8TJ5BkERb68zsDVZygSlD3/b0B6tPf2byempRFO127T095JQ6wJFBTcJk7VhCRj\nYItUT/mgrgxOvWtrPtLdEG8gYdcT6gDRGjERWsosrS2TKwbMP78rcth3/gX/0SEvLZFG1QAAAABJ\nRU5ErkJggg==\n"""
		# b64["Open"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAI5SURBVBgZpcE9SFVhAMfh33vue49X85ih\n1tUI0cXbF7QkCA5BQVAtbU3VUC3O0dbHWHNQUxE0NQYREUU0BoHUYB9qVJRdLe/V+6HnnPe8/4xu\n5NIQPo+RxEbYdw/2Txa6du0yJuAvEddmPmeuOgbErGf4pTFy7LVjjTUKSjvGb+eNMSDWCIzBrX4f\nLk9e+SwQLbmwS8rS+frc0/PAPdZYnFbxSVv87QZZkoOgC2MiCgMHGRi9GiIBHuQBYYLO4vv74xeB\ne6yxpCaQT8iSEHnhVz6RNsrU55+RL/SDUvAJkgMcUelCiPwgLRajgncrJE1Q0iCtLROVTlHo2QkY\nQIAHCRDGdkMWWFosaYBt30r3zjOABwnh8ckXXPUJ04u9fFgeZGGlSHtbnp5NdQbcFkOLJZWUreKb\nr1C2hLIaclV8WmG6UuRjeoDSUCd78jnmlxIqtZjZztN2N78FxEje4dMFfLKAT8r4pIzSBabqBxne\n1kElNswtZziTY/vWiObmsRwtlkQyZMgtIldFroqyJeSWqK8khGEeFzu8IHaiYHM4Wf6wSnzFNX90\npPUwwkeBlAcfgXrpaMuTpBlpBs6LX2Sg2Wjwh9VqfG325vFRxCEMEetEI8P5WvFILmoPiTNhA8Pc\nYop+vNWjSxOnDl95fMdI4l+uP/w41GY5uaUzvOwFy43Yu/KUGe/7ahozz2uzUy/PGUn8j/uXj54t\n9hev9Q3t637z4mHTSOJ/3Z0onegf3nvLe9duJLERPwFUpzZM2BWatgAAAABJRU5ErkJggg==\n"""
		# b64["Play"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAEdSURBVDjLY/j//z8DJZiB6gY0rH7xpW7l\ni3YKDHj1v2bli38lix61k2VA5fJn/9eeeP+/fcOL/wlT7/aRbEDegkf/Vxx/93/xobf/S5c8/u/e\ncm0eSQYkTX/4f+HBN/8nbX/xf+bul/8Tp9/9r1N0dgnRBgT33QZqfPW/YdXj/42rH//v2vjkv3fH\ntf9SScceEWWAc8u1/xO2Pv9fsvjB//IlD4CGPPrvXH/5v2Tksc1EGWBaful/+/on/4sW3gfGxsP/\n9lUX/ksEH1gj6rqdhSgDlPPO/q9b8fB/5bIH/23LL/wXD9i7kqRAlEo6+b908f3/NiXn/4t57V1E\ncjRKRB75b1145r+o684FZCUkMb8D/0Uct88euMxEKgYA7Ojrv4CgE7EAAAAASUVORK5CYII=\n"""
		# b64["Stop"] = """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAJOSURBVDjLpZI9T1RBFIaf3buAoBgJ8rl6\nQVBJVNDCShMLOhBj6T+wNUaDjY0WmpBIgYpAjL/AShJ+gVYYYRPIony5IETkQxZ2770zc2fGYpfl\nQy2MJzk5J5M5z/vO5ESstfxPxA4erL4Zuh4pLnoaiUZdq7XAGKzRJVbIBZ3JPLJaD9c/eCj/CFgZ\nfNl5qK5q8EhTXdxxLKgQjAFr0NK0ppOpt9n51D2gd2cmsvOElVcvOoprKvuPtriNzsY8rH+H0ECo\nQEg4WklY1czP8akZby51p6G3b6QAWBl43llSVTlUfuZE3NmYh9Vl0HkHSuVq4ENFNWFdC+uJ5JI/\n9/V2Y//rkShA1HF6yk/VxJ0f07CcgkCB7+fSC8Dzcy7mp4l9/khlUzwecaI9hT+wRrsOISylcsph\nCFLl1RXIvBMpYDZJrKYRjHELACNEgC/KCQQofWBQ5nuV64UAP8AEfrDrQEiLlJD18+p7BguwfAoB\nUmKEsLsAGZSiFWxtgWWP4gGAkuB5YDRWylKAKIDJZBa1H8Kx47C1Cdls7qLnQTZffQ+20lB7EiU1\nent7sQBQ6+vdq2PJ5dC9ABW1sJnOQbL5Qc/HpNOYehf/4lW+jY4vh2tr3fsWafrWzRtlDW5f9aVz\njUVj72FmCqzBypBQCKzbjLp8jZUPo7OZyYm7bYkvw/sAAFMd7V3lp5sGqs+fjRcZhVYKY0xupwys\nfpogk0jcb5ucffbbKu9Esv1Kl1N2+Ekk5rg2DIXRmog1Jdr3F/Tm5mO0edc6MSP/CvjX+AV0DoH1\nZ+D54gAAAABJRU5ErkJggg==\n"""
		#
		#
		if icontext in b64:
			self.imgdata[icontext] = tk.PhotoImage(data=b64[icontext])
			# print("get_icon: self.imgdata[icontext]:", self.imgdata[icontext])
			return self.imgdata[icontext]

	#
	# End class RFSwarmGUI
	#


rfs = RFSwarmGUI()
print("Robot Framework Swarm: Run GUI")
print("	Version", rfs.version)

# rfs.master.title('Robot Framework Swarm')
# rfs.columnconfigure(0, weight=1)
# rfs.rowconfigure(0, weight=1)
try:
	rfs.mainloop()
except KeyboardInterrupt:
	rfs.on_closing()
except Exception as e:
	print("rfs.Exception:", e)
	rfs.on_closing()
