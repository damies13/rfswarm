#!/usr/bin/python
#
#	Robot Framework Swarm
#
#   V0.1    20190912.DA     Initial Version
#
#
#
#
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

import random
import time
from datetime import datetime
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

	def on_closing(self):

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
		file_menu.add_command(label = "New", command = self.mnu_file_New, accelerator="Command-N") # it adds a option to the sub menu 'command' parameter is used to do some action
		file_menu.add_command(label = "Open", command = self.mnu_file_Open, accelerator="Command-O")
		file_menu.add_command(label = "Save", command = self.mnu_file_Save, accelerator="Command-S")
		file_menu.add_command(label = "Save As", command = self.mnu_file_SaveAs, accelerator="Command-A")
		file_menu.add_command(label = "Close", command = self.mnu_file_Close, accelerator="Command-L")

		# file_menu.add_separator() # it adds a line after the 'Open files' option
		# file_menu.add_command(label = "Exit", command = self.on_closing, accelerator="Command-N")
		file_menu.add_command(label = "Quit", command = self.on_closing, accelerator="Command-Q")

		# # creting another sub menu
		# edit_menu = tk.Menu(root_menu)
		# root_menu.add_cascade(label = "Edit", menu = edit_menu)
		# edit_menu.add_command(label = "Undo", command = function)
		# edit_menu.add_command(label = "Redo", command = function)

		window.protocol("WM_DELETE_WINDOW", self.on_closing)
		window.protocol("WM_QUERYENDSESSION", self.on_closing)
		window.protocol("WM_ENDSESSION", self.on_closing)
		window.protocol("WM_QUIT", self.on_closing)
		window.protocol("WM_DESTROY", self.on_closing)
		window.protocol("WM_CLOSE", self.on_closing)
		window.protocol("CTRL_SHUTDOWN_EVENT", self.on_closing)
		window.protocol("HWND_MESSAGE", self.on_closing)

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

		p.columnconfigure(0, weight=2)
		p.rowconfigure(0, weight=1)
		# p.rowconfigure(1, weight=1)
		self.pln_graph = tk.Canvas(p)
		self.pln_graph.pack(fill="both", expand=True)
		self.pln_graph.grid(column=0, row=0, sticky="nsew") # sticky="wens"

		sg = ttk.Frame(p)
		sg.grid(column=0, row=1, sticky="nsew")
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

		self.addScriptRow()

		ply = ttk.Button(p, text='Play', command=self.ClickPlay)
		ply.grid(column=0, row=99) # , sticky="nsew")


	def BuildRun(self, r):

		if 'Run' not in self.config:
			self.config['Run'] = {}
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


		stp = ttk.Button(rgbar, text='Stop', command=self.ClickStop)
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
			if self.datadb is None:
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
		if len(self.run_name)>0:
			# check if dir exists
			# print("ensure_db: dir_path:", self.dir_path)
			self.resultsdir = os.path.join(self.dir_path, "results")
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

			if createschema and self.datadb is not None:
				print("ensure_db: Disconnect and close DB")
				self.datadb.commit()
				self.datadb.close()
				self.datadb = None

			if self.datadb is None:
				self.datadb = sqlite3.connect(self.dbfile)

			if createschema:
				c = self.datadb.cursor()
				# create tables
				c.execute('''CREATE TABLE Agents
					(agent text, status text, last_seen date, robots int, load num, cpu num, mem num, net num)''')

				c.execute('''CREATE TABLE Results
					(script_index int, virtual_user int, iteration int, agent text, sequence int, result_name text, result text, elapsed_time num, start_time num, end_time num)''')

				# create indexes?

 				# create views?
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
			robottpl.append([agnt, self.Agents[agnt]['Robots']])

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

		time_elapsed = int(time.time()) - self.rungridupdate
		if (time_elapsed>5):
			ut = threading.Thread(target=self.delayed_UpdateRunStats)
			ut.start()

	def delayed_UpdateRunStats(self):
		time_elapsed = int(time.time()) - self.rungridupdate
		if (time_elapsed>5):
			# queue sqls so UpdateRunStats should have the results

			# TODO: to query the percentile value we'll need to create an aggregate class
				# https://docs.python.org/2/library/sqlite3.html#sqlite3.Connection.create_aggregate

			gblist = []
			display_index = self.display_run['display_index'].get()
			# print("delayed_UpdateRunStats: display_index:", display_index, "	config[Run][display_index]:", self.config['Run']['display_index'], "	bool(config[Run][display_index]):", self.str2bool(self.config['Run']['display_index']))
			if display_index != self.str2bool(self.config['Run']['display_index']):
				self.config['Run']['display_index'] = str(display_index)
				self.saveini()
			if display_index:
				gblist.append("script_index")

			display_iteration = self.display_run['display_iteration'].get()
			if display_iteration != self.str2bool(self.config['Run']['display_iteration']):
				self.config['Run']['display_iteration'] = str(display_iteration)
				self.saveini()
			if display_iteration:
				gblist.append("iteration")

			display_sequence = self.display_run['display_sequence'].get()
			if display_sequence != self.str2bool(self.config['Run']['display_sequence']):
				self.config['Run']['display_sequence'] = str(display_sequence)
				self.saveini()
			if display_sequence:
				gblist.append("sequence")

			gblist.append("result_name")
			# print("delayed_UpdateRunStats:	gblist:", gblist)
			# gblist = ["result_name"]
			# gblist = ["sequence", "result_name"]
			# gblist = ["script_index", "result_name"]
			# gblist = ["script_index", "iteration", "sequence", "result_name"]
			gbcols = ", ".join(gblist)

			# print("delayed_UpdateRunStats:	gbcols:", gbcols)


			sql = "SELECT "
			if len(gblist)>0:
				sql += 	gbcols
				sql += 	", "
			sql += 		"result_name, "
			sql += 		"result, "
			sql += 		"count(*) 'count', "
			sql += 		"round(min(elapsed_time),3) 'min', "
			sql += 		"round(avg(elapsed_time),3) 'avg', "
			sql += 		"round(max(elapsed_time),3) 'max' "
			sql += "FROM Results "
			sql += "WHERE result = 'PASS' "
			if len(gblist)>0:
				sql += "GROUP BY  "
				sql += 		gbcols

			# round(-4.535,2);

			# sql = """SELECT
			# 			script_index,
			# 			sequence,
			# 			result_name,
			# 			result,
			# 			count(*) 'count',
			# 			min(elapsed_time) 'min',
			# 			avg(elapsed_time) 'avg',
			# 			max(elapsed_time) 'max'
			# 		FROM Results
			# 		WHERE result = 'PASS'
			# 		GROUP BY script_index, sequence, result_name"""

			# print("delayed_UpdateRunStats:	sql:", sql)

			self.dbqueue["Read"].append({"SQL": sql, "KEY": "RunStats_Pass"})

			sql = "SELECT "
			if len(gblist)>0:
				sql += 	gbcols
				sql += 	", "
			sql += 		"result_name, "
			sql += 		"result, "
			sql += 		"count(*) 'count' "
			sql += "FROM Results "
			sql += "WHERE result <> 'PASS' "
			sql += "GROUP BY  "
			sql += 		gbcols

			# sql = """SELECT
			# 			script_index,
			# 			sequence,
			# 			result_name,
			# 			result,
			# 			count(*) 'count'
			# 		FROM Results
			# 		WHERE result <> 'PASS'
			# 		GROUP BY 	script_index,
			# 					sequence,
			# 					result_name"""

			# print("delayed_UpdateRunStats:	sql:", sql)

			self.dbqueue["Read"].append({"SQL": sql, "KEY": "RunStats_NotPass"})

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

			# if "RunStats_Pass" in self.dbqueue["ReadResult"]:
			# 	print("UpdateRunStats: RunStats_Pass:", self.dbqueue["ReadResult"]["RunStats_Pass"])

			# if "RunStats_NotPass" in self.dbqueue["ReadResult"]:
			# 	print("UpdateRunStats: RunStats_NotPass:", self.dbqueue["ReadResult"]["RunStats_NotPass"])

			colno = 0
			if "RunStats_Pass" in self.dbqueue["ReadResult"] and len(self.dbqueue["ReadResult"]["RunStats_Pass"])>0:
				for col in self.dbqueue["ReadResult"]["RunStats_Pass"][0].keys():
					# print("UpdateRunStats: colno:", colno, "col:", col)
					# print("UpdateRunStats: display_run:", self.display_run)
					if colno in self.display_run["columns"]:
						currcol = self.display_run["columns"][colno].get()
						if col != currcol:
							self.display_run["columns"][colno].set("  {}  ".format(col))
					else:
						self.display_run["columns"][colno] = tk.StringVar()
						self.display_run["columns"][colno].set("  {}  ".format(col))

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


				datarows = len(self.dbqueue["ReadResult"]["RunStats_Pass"])
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
				for row in self.dbqueue["ReadResult"]["RunStats_Pass"]:
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


	def ClickPlay(self):
		self.sr_validate()
		# print(self.tabs.tabs())
		self.tabs.select(1)

		print("ClickPlay:", int(time.time()))

		# self.tabs.select('Run')
		# print(self.scriptlist)
		# Start a thread to start the threads
		# https://realpython.com/intro-to-python-threading/
		# self.run_start_threads()
		# x = threading.Thread(target=thread_function, args=(1,))
		self.run_start = 0
		self.run_end = 0
		self.run_paused = False
		self.robot_schedule = {"RunName": "", "Agents": {}, "Scripts": {}}
		t = threading.Thread(target=self.run_start_threads)
		t.start()


	def ClickStop(self):
		self.run_end = int(time.time()) #time now
		print("ClickStop: run_end", self.run_end)
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
		# print(args)
		if args:
			r = args[0]
			usrs = self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].get()
			# print("Row:", r, "Users:", usrs)
			self.scriptlist[r]["Users"] = int(usrs)
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				usrs = self.scriptgrid.grid_slaves(column=self.plancolusr, row=r)[0].get()
				# print("Row:", r, "Users:", usrs)
				self.scriptlist[r]["Users"] = int(usrs)
		self.pln_update_graph()
		return True

	def sr_delay_validate(self, *args):
		# print(args)
		if args:
			r = args[0]
			dly = self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].get()
			# print("Row:", r, "Delay:", dly)
			self.scriptlist[r]["Delay"] = int(dly)
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				dly = self.scriptgrid.grid_slaves(column=self.plancoldly, row=r)[0].get()
				# print("Row:", r, "Delay:", dly)
				self.scriptlist[r]["Delay"] = int(dly)
		self.pln_update_graph()
		return True

	def sr_rampup_validate(self, *args):
		# print(args)
		if args:
			r = args[0]
			rmp = self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].get()
			# print("Row:", r, "RampUp:", rmp)
			self.scriptlist[r]["RampUp"] = int(rmp)
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				rmp = self.scriptgrid.grid_slaves(column=self.plancolrmp, row=r)[0].get()
				# print("Row:", r, "RampUp:", rmp)
				self.scriptlist[r]["RampUp"] = int(rmp)
		self.pln_update_graph()
		return True

	def sr_run_validate(self, *args):
		# print(args)
		if args:
			r = args[0]
			run = self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].get()
			# print("Row:", r, "Run:", run)
			self.scriptlist[r]["Run"] = int(run)
			self.pln_update_graph()
			return True
		# print(self.scriptgrid.grid_size())
		for r in range(self.scriptgrid.grid_size()[1]):
			# print(r)
			if r>0:
				run = self.scriptgrid.grid_slaves(column=self.plancolrun, row=r)[0].get()
				# print("Row:", r, "Run:", run)
				self.scriptlist[r]["Run"] = int(run)
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
		print(file, hasher.hexdigest())
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
							if 'Resource' in line or 'Variables' in line or 'Metadata	File' in line:
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
											print("find_dependancies: file", file)
											relpath = file.replace(localdir, "")[1:]
											print("find_dependancies: relpath", relpath)
											newhash = self.hash_file(file)
											print("find_dependancies: newhash", newhash)
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


	def sr_file_validate(self, r):
		# print(r)
		fg = self.scriptgrid.grid_slaves(column=self.plancolscr, row=r)[0].grid_slaves()
		# print(fg)
		# print(fg[1].get())
		# root.filename = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
		scriptfile = str(tkf.askopenfilename(initialdir=self.config['Plan']['ScriptDir'], title = "Select Robot Framework File", filetypes = (("Robot Framework","*.robot"),("all files","*.*"))))
		# print("scriptfile:", scriptfile)
		if len(scriptfile)>0:
			fg[1].configure(state='normal')
			fg[1].select_clear()
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
		# print(tol)
		self.scriptlist[r]["Test"] = self.scriptlist[r]["TestVar"].get()
		# print(self.scriptlist[r])
		self.pln_update_graph()
		return True

	def sr_test_genlist(self, r):
		# print("Script File:",self.scriptlist[r]["Script"])
		tcsection = False
		tclist = [""]
		with open(self.scriptlist[r]["Script"]) as f:
			for line in f:
				# print(tcsection, line)
				if tcsection and line[0:3] == "***":
					tcsection = False
				if line[0:18] == "*** Test Cases ***":
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
		while curusrs < totusrs and not self.run_paused:
			# print("run_start_threads: while totusrs", totusrs, " 	curusrs:", curusrs)
			# totusrs = 0
			for grp in self.scriptlist:
				# print("run_start_threads: grp", grp)
				if "Test" in grp.keys() and len(grp["Test"])>0:
					# print("run_start_threads: while totusrs", totusrs, " 	curusrs:", curusrs)
					# print("run_start_threads: grp[Index]", grp['Index'])

					nxtagent = self.get_next_agent()
					# print('run_start_threads: next_agent', nxtagent)

					if nxtagent is None:
						print('No Agents available to run Robots!')
						print('No Agents available to run Robots!')
						print('No Agents available to run Robots!')
						self.run_paused = True

					colour = self.line_colour(grp["Index"])
					# print("run_start_threads: Line colour", colour)

					if self.run_start < 1:
						self.run_start = int(time.time()) #time now
						self.run_name = "{}_{}".format("Scenario", self.run_start)
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
		server_address = ('', 8138)
		self.agenthttpserver = ThreadingHTTPServer(server_address, AgentServer)
		print("Starting Agent Server", server_address)
		self.agenthttpserver.serve_forever()

	def register_agent(self, agentdata):
		# print("register_agent: agentdata:", agentdata)
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
	def mnu_file_New(self):
		print("mnu_file_New")
		if len(self.config['Plan']['ScenarioFile'])>0:
			self.mnu_file_Close()

		self.updateTitle()
		while self.scriptcount > 0:
			self.sr_remove_row(self.scriptcount)
			self.scriptcount += -1
		self.scriptlist = [{}]
		self.addScriptRow()


	def mnu_file_Open(self):
		print("mnu_file_Open")
		ScenarioFile = str(tkf.askopenfilename(initialdir=self.config['Plan']['ScriptDir'], title = "Select RFSwarm Scenario File", filetypes = (("RFSwarm","*.rfs"),("all files","*.*"))))
		print("mnu_file_Open: ScenarioFile:", ScenarioFile)


	def mnu_file_Save(self):
		print("mnu_file_Save")
		if len(self.config['Plan']['ScenarioFile'])<1:
			self.mnu_file_SaveAs()
		else:

			print("mnu_file_Save: ScenarioFile:", self.config['Plan']['ScenarioFile'])
			print("mnu_file_Save: scriptlist:", self.scriptlist)
			filedata = configparser.ConfigParser()

			if 'Scenario' not in filedata:
				filedata['Scenario'] = {}

			scriptidx = str(0)
			if 'ScriptCount' not in filedata['Scenario']:
				# filedata['Scenario']['ScriptCount'] = str(len(self.scriptlist)-1)
				filedata['Scenario']['ScriptCount'] = scriptidx

			for scrp in self.scriptlist:
				if 'Index' in scrp:
					scriptidx = str(scrp['Index'])

					if scriptidx not in filedata:
						filedata[scriptidx] = {}
					for key in scrp.keys():
						if key not in ['Index', 'TestVar', 'ScriptHash']:
							filedata[scriptidx][key] = str(scrp[key])

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

	def mnu_file_SaveAs(self):
		print("mnu_file_SaveAs")
		# asksaveasfilename
		ScenarioFile = str(tkf.asksaveasfilename(\
						initialdir=self.config['Plan']['ScenarioDir'], \
						title = "Save RFSwarm Scenario File", \
						filetypes = (("RFSwarm","*.rfs"),("all files","*.*"))\
						))
		print("mnu_file_SaveAs: ScenarioFile:", ScenarioFile)
		if ScenarioFile is not None and len(ScenarioFile)>0:
			# ScenarioFile
			filetupl = os.path.splitext(ScenarioFile)
			print("mnu_file_SaveAs: filetupl:", filetupl)
			if filetupl != ".rfs":
				ScenarioFile += ".rfs"
				print("mnu_file_SaveAs: ScenarioFile:", ScenarioFile)
			self.config['Plan']['ScenarioFile'] = ScenarioFile
			self.mnu_file_Save()

	def mnu_file_Close(self):
		print("mnu_file_Close")
		MsgBox = tkm.askyesno('Save Scenario','Do you want to save the current scenario?')
		print("mnu_file_Close: MsgBox:", MsgBox)
		if MsgBox:
			self.mnu_file_Save()

		self.config['Plan']['ScenarioFile'] = ""
		self.mnu_file_New()

	#
	# End class RFSwarmGUI
	#


rfs = RFSwarmGUI()
print("Robot Framework Swarm: Run GUI")
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
