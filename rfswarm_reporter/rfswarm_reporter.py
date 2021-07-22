#!/usr/bin/python
#
#	Robot Framework Swarm
#		Reporter
#    Version 0.9.0
#

import sys
import os
import signal


import sqlite3

import time
from datetime import datetime, timezone
import threading

import inspect

import tkinter as tk				#python3
import tkinter.ttk as ttk			#python3
import tkinter.filedialog as tkf	#python3
import tkinter.messagebox as tkm	#python3

# required for matplot graphs
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
# required for matplot graphs

class ReporterBase():
	version="0.9.0"
	debuglvl = 9

	running = True
	displaygui = True
	gui = None

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
					if len(prefix.strip())<32:
						prefix = "{}	".format(prefix)
					# <28 + 1 tab
					# if len(prefix.strip())<28:
					# 	prefix = "{}	".format(prefix)
					# <24 + 1 tab
					if len(prefix.strip())<24:
						prefix = "{}	".format(prefix)

					msglst.append(str(prefix))

					# suffix = "	[{} @{}]".format(self.version, str(datetime.now().replace(microsecond=0).isoformat(sep=' ')))
					suffix = "	[{} @{}]".format(self.version, str(datetime.now().isoformat(sep=' ', timespec='seconds')))
					# suffix = "	[{} @{}]".format(self.version, "HH:mm:SS")

				for itm in msg:
					msglst.append(str(itm))
				msglst.append(str(suffix))
				print(" ".join(msglst))
			except:
				pass



class ReporterCore:


	def __init__(self, master=None):
		base.debugmsg(0, "Robot Framework Swarm: Reporter")
		base.debugmsg(0, "	Version", base.version)
		signal.signal(signal.SIGINT, self.on_closing)

		if base.displaygui:
			base.gui = ReporterGUI()

	def mainloop(self):

		base.debugmsg(5, "mainloop start")

		if base.displaygui:
			base.gui.mainloop()

		# while base.running:
		# 	time.sleep(300)


	def on_closing(self, _event=None, *extras):
		base.running = False
		base.debugmsg(5, "base.running:", base.running)


		base.debugmsg(2, "Exit")
		try:
			sys.exit(0)
		except SystemExit:
			try:
				os._exit(0)
			except:
				pass


class ReporterGUI(tk.Frame):

	def __init__(self, master=None):

		self.root = tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		tk.Frame.__init__(self, self.root)
		self.grid(sticky="news", ipadx=0, pady=0)
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		self.root.geometry("640" + "x" + "800")

		self.root.resizable(True, True)

		self.root.title("rfswarm Reporter")

		base.debugmsg(5, "self.root", self.root)
		base.debugmsg(5, "self.root[background]", self.root["background"])
		self.rootBackground = self.root["background"]

		self.load_icons()


		base.debugmsg(5, "BuildUI")
		self.BuildUI()


	def load_icons(self):
		pass

	def BuildUI(self):

		self.bbar = tk.Frame(self)
		self.bbar.grid(column=0, row=0, sticky="nsew")
		self.bbar.config(bg="red")

		self.mainframe = tk.Frame(self)
		self.mainframe.grid(column=0, row=1, sticky="nsew")
		self.mainframe.config(bg="green")

		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)





	def on_closing(self, _event=None, *extras):
		try:
			base.debugmsg(5, "close window")
			self.destroy()
		except:
			# were closing the application anyway, ignore any error
			pass
		base.debugmsg(5, "core.on_closing")
		core.on_closing()


class RFSwarm_Reporter():

	running = True

	def __init__(self):
		while base.running:
			# time.sleep(300)
			time.sleep(1)


base = ReporterBase()

core = ReporterCore()

core.mainloop()

# r = RFSwarm_Reporter()
