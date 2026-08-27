
# Robot Framework Swarm

# https://stackoverflow.com/questions/48090535/csv-file-reading-and-find-the-value-from-nth-column-using-robot-framework

import base64
import gc
import importlib.metadata
import json
import lzma
import os
import platform
import random
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import psutil
import requests

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
	sys.path.insert(0, parent_dir)

from rfswarm_common.__version__ import __version__
from rfswarm_common.debug import debug
from rfswarm_common.filestransfers import FilesTransfers
from rfswarm_agent.client.manager import ManagerClient
from rfswarm_common.config import config
from rfswarm_agent.properties import collect_agent_properties


class RFSwarmAgent():
	"""
	Orchestrator class for Robot Framework Swarm Agent.
	"""
	version = __version__
	config = None
	manager = None
	isrunning = False
	isstopping = False
	runagent = True
	run_name = None
	agentdir = None
	scriptdir = None
	logdir = None
	agentini = None
	listenerfile = None
	repeaterfile = None

	ipaddresslist: Any = []
	agentname = None
	netpct = 0
	mainloopinterval = 10
	scriptlist: Any = {}
	jobs: Any = {}
	corethreads: Any = {}
	upload_queue: Any = []
	upload_threads: Any = {}
	download_queue: Any = []
	download_threads: Any = {}
	robotcount = 0
	monitorcount = 0
	status = "Ready"
	excludelibraries: Any = []
	args = None
	xmlmode = False
	timeout = 600
	uploadmode = "err"
	managedenvvars: Any = []
	srcdir = os.path.join(os.path.dirname(__file__))

	def __init__(self, args, master=None):
		debug.debugmsg(6, "__init__")
		debug.debugmsg(6, "gettempdir", tempfile.gettempdir())
		debug.debugmsg(6, "tempdir", tempfile.tempdir)

		self.srcdir = os.path.join(os.path.dirname(__file__))
		if self.srcdir[-2:] == "/.":
			debug.debugmsg(7, "self.srcdir[-2]: ", self.srcdir[-2:])
			self.srcdir = self.srcdir[0:-2]
		debug.debugmsg(7, "self.srcdir: ", self.srcdir)

		self.args = args

		debug.debugmsg(6, "args: ", args)

		config.load_config(inifilename="RFSwarmAgent.ini", srcdir=self.srcdir, args=self.args)
		self.agentproperties = collect_agent_properties(self.args, self.version)

		if self.args.version:
			self.show_additional_versions()
			exit()

		if self.args.create:
			if self.args.create.upper() in ["ICON", "ICONS"]:
				self.create_icons()
			else:
				debug.debugmsg(0, "create with option ", self.args.create.upper(), "not supported.")
			exit()

		debug.debugmsg(0, "	Configuration File: ", config.ini_file)
		debug.debugmsg(5, "config.data: ", config.data)

		if self.args.agentname:
			self.agentname = self.args.agentname

		if 'Agent' not in config.data:
			config.data['Agent'] = {}
			config.saveini()

		if 'agentname' not in config.data['Agent']:
			config.data['Agent']['agentname'] = socket.gethostname()
			config.saveini()

		if not self.args.agentname:
			self.agentname = config.data['Agent']['agentname']

		if 'agentdir' not in config.data['Agent']:
			config.data['Agent']['agentdir'] = os.path.join(tempfile.gettempdir(), "rfswarmagent")
			config.saveini()

		if 'xmlmode' not in config.data['Agent']:
			config.data['Agent']['xmlmode'] = str(self.xmlmode)
			config.saveini()

		self.xmlmode = self.str2bool(config.data['Agent']['xmlmode'])
		if self.args.xmlmode:
			debug.debugmsg(0, "Warning! RFSwarm Agent is running with XML mode enabled")
			debug.debugmsg(0, "This feature will soon be deprecated due to changes related to output.xml file in Robot Framework 7.0")
			debug.debugmsg(0, "Future versions of Robot framework are expected to completely abandon legacy XML output file format")
			debug.debugmsg(6, "self.args.xmlmode: ", self.args.xmlmode)
			self.xmlmode = self.str2bool(self.args.xmlmode)

		self.agentdir = config.data['Agent']['agentdir']
		if self.args.agentdir:
			debug.debugmsg(1, "self.args.agentdir: ", self.args.agentdir)
			self.agentdir = self.args.agentdir
		self.ensuredir(self.agentdir)

		self.scriptdir = os.path.join(self.agentdir, "scripts")
		self.ensuredir(self.scriptdir)

		self.logdir = os.path.join(self.agentdir, "logs")
		self.ensuredir(self.logdir)

		if 'excludelibraries' not in config.data['Agent']:
			config.data['Agent']['excludelibraries'] = "BuiltIn,String,OperatingSystem,perftest"
			config.saveini()

		# self.excludelibraries = ["BuiltIn", "String", "OperatingSystem", "perftest"]
		self.excludelibraries = config.data['Agent']['excludelibraries'].split(",")
		debug.debugmsg(6, "self.excludelibraries:", self.excludelibraries)

		if 'properties' not in config.data['Agent']:
			config.data['Agent']['properties'] = ""
			config.saveini()

		if not self.args.create:
			self.check_icons("RFSwarm Agent")

		self.ensure_listner_file()
		self.ensure_repeater_listner_file()

		if 'swarmserver' in config.data['Agent']:
			if 'swarmmanager' not in config.data['Agent']:
				config.data['Agent']['swarmmanager'] = config.data['Agent']['swarmserver']
			del config.data['Agent']['swarmserver']
			config.saveini()

		if 'swarmmanager' not in config.data['Agent']:
			config.data['Agent']['swarmmanager'] = "http://localhost:8138/"
			config.saveini()

		if self.args and hasattr(self.args, "manager") and self.args.manager:
			debug.debugmsg(7, "self.args.manager: ", self.args.manager)
			if self.args.manager[-1] != '/':
				config.data['Agent']['swarmmanager'] = "{}/".format(self.args.manager)
			else:
				config.data['Agent']['swarmmanager'] = self.args.manager

		self.manager = ManagerClient()

	def show_additional_versions(self):

		debug.debugmsg(0, "	Dependancy Versions")
		try:
			debug.debugmsg(0, "		Python Version", sys.version)
		except Exception:
			pass

		try:
			debug.debugmsg(0, "		RobotFramework:", self.agentproperties["RobotFramework"])
			liblist = self.agentproperties["RobotFramework: Libraries"].split(", ")
			for lib in liblist:
				debug.debugmsg(0, "		RobotFramework Library: " + lib, self.agentproperties["RobotFramework: Library: " + lib])
		except Exception:
			pass

	def create_icons(self):
		debug.debugmsg(0, "Creating application icons for RFSwarm Agent")
		appname = "RFSwarm Agent"
		namelst = appname.split()
		debug.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		debug.debugmsg(6, "projname:", projname)
		pipdata = importlib.metadata.distribution(projname)
		# print("files:", pipdata.files)
		# print("file0:", pipdata.files[0])
		agent_executable = os.path.abspath(str(pipdata.locate_file(pipdata.files[0])))
		debug.debugmsg(5, "agent_executable:", agent_executable)

		script_dir = os.path.dirname(os.path.abspath(__file__))
		debug.debugmsg(5, "script_dir:", script_dir)
		icon_dir = os.path.join(pipdata.locate_file('rfswarm_agent'), "icons")
		debug.debugmsg(5, "icon_dir:", icon_dir)

		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				fileprefix = "/usr/share"

			fileprefix = os.path.expanduser(fileprefix)

			debug.debugmsg(5, "Create .directory file")
			directorydata = []
			directorydata.append('[Desktop Entry]\n')
			directorydata.append('Type=Directory\n')
			directorydata.append('Name=RFSwarm\n')
			directorydata.append('Icon=rfswarm-logo\n')

			directoryfilename = os.path.join(fileprefix, "desktop-directories", "rfswarm.directory")
			directorydir = os.path.dirname(directoryfilename)
			self.ensuredir(directorydir)

			debug.debugmsg(5, "directoryfilename:", directoryfilename)
			with open(directoryfilename, 'w') as df:
				df.writelines(directorydata)

			directoryfilename = os.path.join(fileprefix, "applications", "rfswarm.directory")
			directorydir = os.path.dirname(directoryfilename)
			self.ensuredir(directorydir)
			debug.debugmsg(5, "directoryfilename:", directoryfilename)
			with open(directoryfilename, 'w') as df:
				df.writelines(directorydata)

			debug.debugmsg(5, "Create .desktop file")
			desktopdata = []
			desktopdata.append('[Desktop Entry]\n')
			desktopdata.append('Name=' + appname + '\n')
			desktopdata.append('Exec=' + agent_executable + '\n')
			desktopdata.append('Terminal=true\n')
			desktopdata.append('Type=Application\n')
			desktopdata.append('Icon=' + projname + '\n')
			desktopdata.append('Categories=RFSwarm;Development;\n')
			desktopdata.append('Keywords=rfswarm;agent;\n')
			# desktopdata.append('\n')

			desktopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
			desktopdir = os.path.dirname(desktopfilename)
			self.ensuredir(desktopdir)

			debug.debugmsg(5, "desktopfilename:", desktopfilename)
			with open(desktopfilename, 'w') as df:
				df.writelines(desktopdata)

			debug.debugmsg(5, "Copy icons")
			# /usr/share/icons/hicolor/128x128/apps/
			# 	1024x1024  128x128  16x16  192x192  22x22  24x24  256x256  32x32  36x36  42x42  48x48  512x512  64x64  72x72  8x8  96x96
			# or
			#  ~/.local/share/icons/hicolor/256x256/apps/
			src_iconx128 = os.path.join(icon_dir, projname + "-128.png")
			debug.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", projname + ".png")
			dst_icondir = os.path.dirname(dst_iconx128)
			self.ensuredir(dst_icondir)
			debug.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

			src_iconx128 = os.path.join(icon_dir, "rfswarm-logo-128.png")
			debug.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", "rfswarm-logo.png")
			debug.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

		if platform.system() == 'Darwin':
			debug.debugmsg(5, "Create folder structure in /Applications")
			src_iconx1024 = os.path.join(icon_dir, projname + "-1024.png")

			self.create_macos_app_bundle(appname, pipdata.version, agent_executable, src_iconx1024)

		if platform.system() == 'Windows':
			debug.debugmsg(5, "Create Startmenu shorcuts")
			roam_appdata = os.environ["APPDATA"]
			scutpath = os.path.join(roam_appdata, "Microsoft", "Windows", "Start Menu", appname + ".lnk")
			src_iconx128 = os.path.join(icon_dir, projname + "-128.ico")

			self.create_windows_shortcut(scutpath, agent_executable, src_iconx128, "Connects to Manager and runs robots", True)

	def create_windows_shortcut(self, scutpath, targetpath, iconpath, desc, minimised=False):
		pslst = []

		directorydir = os.path.dirname(scutpath)
		self.ensuredir(directorydir)

		pslst.append("$wshshell = New-Object -COMObject wscript.shell")
		pslst.append('$scut = $wshshell.CreateShortcut("""' + scutpath + '""")')
		pslst.append('$scut.TargetPath = """' + targetpath + '"""')
		pslst.append('$scut.IconLocation = """' + iconpath + '"""')
		if minimised:
			pslst.append("$scut.WindowStyle = 7")
		pslst.append("$scut.Description = '" + desc + "'")
		pslst.append("$scut.Save()")

		psscript = '; '.join(pslst)
		debug.debugmsg(6, "psscript:", psscript)

		response = os.popen('powershell.exe -command ' + psscript).read()

		debug.debugmsg(6, "response:", response)

	def create_macos_app_bundle(self, name, version, exesrc, icosrc):

		appspath = "~/Applications"
		if os.access("/Applications", os.W_OK):
			appspath = "/Applications"

		appspath = os.path.expanduser(appspath)

		# https://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

		apppath = os.path.join(appspath, name + ".app")
		MacOSFolder = os.path.join(apppath, "Contents", "MacOS")
		self.ensuredir(MacOSFolder)

		# need to create the icon file:
		# https://stackoverflow.com/questions/646671/how-do-i-set-the-icon-for-my-applications-mac-os-x-app-bundle
		namelst = name.split()
		debug.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		debug.debugmsg(6, "projname:", projname)
		signature = "RFS{0}".format(namelst[1].upper())
		debug.debugmsg(6, "signature:", signature)

		ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
		iconset = os.path.join(ResourcesFolder, projname + ".iconset")
		icnsfile = os.path.join(ResourcesFolder, projname + ".icns")
		self.ensuredir(iconset)

		# Normal screen icons
		debug.debugmsg(6, "Normal screen icons")
		for size in [16, 32, 64, 128, 256, 512]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{0}x{0}.png'".format(size, icosrc, iconset)
			debug.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			debug.debugmsg(6, "response:", response)

		# Retina display icons
		debug.debugmsg(6, "Retina display icons")
		for size in [32, 64, 128, 256, 512, 1024]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{3}x{3}x2.png'".format(size, icosrc, iconset, int(size / 2))
			debug.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			debug.debugmsg(6, "response:", response)

		# Make a multi-resolution Icon
		debug.debugmsg(6, "Make a multi-resolution Icon")
		cmd = "iconutil -c icns -o '{0}' '{1}'".format(icnsfile, iconset)
		debug.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		debug.debugmsg(6, "response:", response)

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

		# touch '/Applications/RFSwarm Manager.app' to update .app icon
		cmd = "touch '{0}'".format(apppath)
		debug.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		debug.debugmsg(6, "response:", response)

		# # Try re-registering your application with Launch Services:
		# # /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f /Applications/MyTool.app
		# lsregister = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
		# cmd = "{0} -f '{1}'".format(lsregister, apppath)
		# debug.debugmsg(6, "cmd:", cmd)
		# response = os.popen(cmd).read()
		# debug.debugmsg(6, "response:", response)

	def check_icons(self, appname):
		projname = "-".join(appname.split()).lower()
		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				fileprefix = "/usr/share"
			fileprefix = os.path.expanduser(fileprefix)
			desktopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
			if not os.path.exists(desktopfilename):
				debug.debugmsg(1, f"{appname} icon / shortcut is not installed. You can create it using the -c or --create flags.")

		elif platform.system() == 'Darwin':
			appspath = "~/Applications"
			if os.access("/Applications", os.W_OK):
				appspath = "/Applications"
			appspath = os.path.expanduser(appspath)
			apppath = os.path.join(appspath, appname + ".app")
			ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
			iconset = os.path.join(ResourcesFolder, projname + ".iconset")
			if not os.path.exists(iconset):
				debug.debugmsg(1, f"{appname} icon / shortcut is not installed. You can create it using the -c or --create flags.")

		elif platform.system() == 'Windows':
			roam_appdata = os.environ["APPDATA"]
			scutpath = os.path.join(roam_appdata, "Microsoft", "Windows", "Start Menu", appname + ".lnk")
			# directorydir = os.path.dirname(scutpath)
			if not os.path.exists(scutpath):
				debug.debugmsg(1, f"{appname} icon / shortcut is not installed. You can create it using the -c or --create flags.")

	def str2bool(self, instr):
		return str(instr).lower() in ("yes", "true", "t", "1")

	def mainloop(self):
		debug.debugmsg(6, "mainloop")
		prev_status = self.status
		while self.runagent:
			debug.debugmsg(
				2, self.status, datetime.now().isoformat(sep=' ', timespec='seconds'),
				"(", int(time.time()), ")",
				"isconnected:", self.manager.isconnected,
				"isrunning:", self.isrunning,
				"isstopping:", self.isstopping,
				"robotcount:", self.robotcount,
				"monitorcount:", self.monitorcount,
				"\n"
			)

			if not self.manager.isconnected:
				# self.isrunning = False # Not sure if I need this?
				# self.connectmanager()
				t = threading.Thread(target=self.manager.connectmanager, name="connectmanager", args=(self.timeout,))
				t.start()
				self.isrunning = False

			debug.debugmsg(5, "self.isconnected", self.manager.isconnected)
			if self.manager.isconnected:
				# self.updatestatus()
				self.corethreads["status"] = threading.Thread(target=self.updatestatus)
				self.corethreads["status"].start()

				if self.listenerfile is not None or self.xmlmode:
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
						debug.debugmsg(5, "self.status:", self.status, "len(self.upload_queue):", len(self.upload_queue))
						self.corethreads["uploadqueue"] = threading.Thread(target=self.process_file_upload_queue)
						self.corethreads["uploadqueue"].start()
					else:
						self.status = "Ready"
						self.corethreads["getscripts"] = threading.Thread(target=self.getscripts)
						self.corethreads["getscripts"].start()

						if len(self.download_queue):
							self.status = "Downloading ({})".format(len(self.download_queue))

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
				debug.debugmsg(6, "nic", nic)
				for addr in iflst[nic]:
					# '127.0.0.1', '::1', 'fe80::1%lo0'
					debug.debugmsg(6, "addr", addr.address)
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
				debug.debugmsg(6, "Speed:", nicstats[nic].speed)
				bytes_speed = nicstats[nic].speed * 1024 * 1024 / 8
				bytes_sent_sec = niccounters1[nic].bytes_sent - niccounters0[nic].bytes_sent
				bytes_recv_sec = niccounters1[nic].bytes_recv - niccounters0[nic].bytes_recv
				debug.debugmsg(6, "bytes_speed:	", bytes_speed)
				debug.debugmsg(6, "bytes_sent_sec:	", bytes_sent_sec)
				debug.debugmsg(6, "bytes_recv:	", bytes_recv_sec)
				bytes_max_sec = max([bytes_sent_sec, bytes_recv_sec])
				debug.debugmsg(6, "bytes_max_sec:	", bytes_max_sec)
				if bytes_max_sec > 0:
					netpctlist.append((bytes_max_sec / bytes_speed) * 100)
				else:
					netpctlist.append(0)

		if len(netpctlist) > 0:
			debug.debugmsg(6, "netpctlist:	", netpctlist)
			self.netpct = max(netpctlist)
			debug.debugmsg(6, "self.netpct:	", self.netpct)
		else:
			self.netpct = 0

	def updatestatus(self):
		debug.debugmsg(6, "self.manager.swarmmanager:", self.manager.swarmmanager)
		uri = self.manager.swarmmanager + "AgentStatus"

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
			"Monitor": self.monitorcount,
			"Status": self.status,
			"Properties": self.agentproperties,
			"FileCount": len(list(self.scriptlist.keys()))
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(8, r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok, r.text)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False
				debug.debugmsg(7, "self.manager.isconnected", self.manager.isconnected)
		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False
			debug.debugmsg(5, "self.manager.isconnected", self.manager.isconnected)

	def getscripts(self):
		debug.debugmsg(6, "getscripts")

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			debug.debugmsg(5, "already processing the queue, don't double up")
			return None

		uri = self.manager.swarmmanager + "Scripts"
		payload = {
			"AgentName": self.agentname
		}
		debug.debugmsg(6, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(6, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(5, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(6, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

		if "Scripts" in jsonresp:
			for s in jsonresp["Scripts"]:
				hash = s['Hash']
				debug.debugmsg(6, "hash:", hash)
				if hash not in self.scriptlist:
					debug.debugmsg(6, "getfile")
					self.scriptlist[hash] = {'id': hash}
					if hash not in self.download_queue:
						self.download_queue.append(hash)
				else:
					debug.debugmsg(6, "Check file")
					if 'localfile' in self.scriptlist[hash]:
						if not os.path.isfile(self.scriptlist[hash]['localfile']):
							if hash not in self.download_queue:
								self.download_queue.append(hash)
					else:
						debug.debugmsg(6, "getfile")
						self.scriptlist[hash] = {'id': hash}
						if hash not in self.download_queue:
							self.download_queue.append(hash)

			if len(self.download_queue):
				self.process_file_download_queue()

	def process_file_download_queue(self):

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			debug.debugmsg(5, "already processing the queue, don't double up")
			return None

		corecount = psutil.cpu_count()
		threadcount = corecount * 32
		debug.debugmsg(7, "download_queue", self.download_queue)
		debug.debugmsg(5, "corecount", corecount, "	threadcount:", threadcount)
		# for hash in self.download_queue:
		while len(self.download_queue) > 0:
			# limit the number of upload threads so we don't max out the agent and cause it
			# to go into critical/offline? mode

			hash = self.download_queue.pop(0)

			debug.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
			while len(list(self.download_threads.keys())) > threadcount - 1:
				debug.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
				# key = list(self.upload_threads.keys())[0]
				key = random.choice(list(self.download_threads.keys()))
				debug.debugmsg(5, "key:", key)
				if key in self.download_threads and self.download_threads[key].is_alive():
					self.download_threads[key].join()
				if key in self.download_threads:
					del self.download_threads[key]
			key = str(uuid.uuid4())
			debug.debugmsg(6, "New download thread key:", key)
			while hash in self.download_queue:
				self.download_queue.remove(hash)
			self.download_threads[key] = threading.Thread(target=self.getfile, args=(hash,))
			self.download_threads[key].start()
			time.sleep(0.02)
		for key in list(self.download_threads.keys()):
			debug.debugmsg(6, "download thread key:", key)
			if key in self.download_threads and self.download_threads[key].is_alive():
				self.download_threads[key].join()
			if key in self.download_threads:
				del self.download_threads[key]
			debug.debugmsg(6, "Finished download thread key:", key)
		gc.collect()

	def getfile(self, hash):
		debug.debugmsg(6, "hash: ", hash)
		uri = self.manager.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Download",
			"Hash": hash
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(8, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(5, "resp: ", r.status_code, r.text)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(5, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

		try:
			relpath = jsonresp['File']
			if '\\' in relpath:
				relpatharr = relpath.split('\\')
			else:
				relpatharr = relpath.split('/')
			debug.debugmsg(7, 'scriptdir', self.scriptdir)
			localfile = os.path.abspath(os.path.join(self.scriptdir, *relpatharr))
			debug.debugmsg(5, 'localfile', localfile)

		except Exception as e:
			debug.debugmsg(0, "Exception:", e)

		try:
			self.scriptlist[hash]['localfile'] = localfile
			self.scriptlist[hash]['file'] = jsonresp['File']

			# self.scriptlist[hash][]

			filedata = jsonresp['FileData']
			debug.debugmsg(6, "filedata:", filedata)
			debug.debugmsg(6, "filedata:")

			decoded = base64.b64decode(filedata)
			debug.debugmsg(6, "b64decode: decoded:", decoded)
			debug.debugmsg(6, "b64decode:")

			uncompressed = lzma.decompress(decoded)
			debug.debugmsg(6, "uncompressed:", uncompressed)
			debug.debugmsg(6, "uncompressed:")

			localfiledir = os.path.dirname(localfile)
			debug.debugmsg(6, "localfiledir:", localfiledir)
			self.ensuredir(localfiledir)
			debug.debugmsg(6, "ensuredir:")

			with open(localfile, 'wb') as afile:
				debug.debugmsg(6, "afile:")
				afile.write(uncompressed)
				debug.debugmsg(6, "write:")
			debug.debugmsg(1, 'Downloaded:', localfile)

		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

	def getjobs(self):
		debug.debugmsg(6, "getjobs")
		uri = self.manager.swarmmanager + "Jobs"
		payload = {
			"AgentName": self.agentname
		}
		debug.debugmsg(9, "getjobs: payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(7, "getjobs: resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(7, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		try:
			jsonresp = {}
			# self.scriptlist
			debug.debugmsg(7, "getjobs: r.text:", r.text)
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "getjobs: jsonresp:", jsonresp)

			# RFSwarmAgent: getjobs(821): [7:7]	 getjobs: r.text: {"AgentName": "hp-elite-desk-800-g3", "StartTime": 0, "EndTime": 0, "RunName": "", "Abort": false, "UploadMode": "err", "EnvironmentVariables": {"RF_DIRECTORY": {"vartype": "path", "value": "rf_dir"}, "RF_MAGICNUM": {"vartype": "value", "value": "TWELVE"}}, "Schedule": {}}
			# "EnvironmentVariables": {"RF_DIRECTORY": {"vartype": "path", "value": "rf_dir"}, "RF_MAGICNUM": {"vartype": "value", "value": "TWELVE"}},
			if "EnvironmentVariables" in jsonresp:
				for envvar in list(jsonresp["EnvironmentVariables"].keys()):
					debug.debugmsg(7, "envvar:", envvar, ":", jsonresp["EnvironmentVariables"][envvar])
					localval = ""
					if "vartype" in jsonresp["EnvironmentVariables"][envvar] and jsonresp["EnvironmentVariables"][envvar]["vartype"] == "path":
						localval = os.path.abspath(os.path.join(self.scriptdir, jsonresp["EnvironmentVariables"][envvar]["value"]))
						debug.debugmsg(5, 'localval:', localval)
					else:
						if "value" in jsonresp["EnvironmentVariables"][envvar]:
							localval = jsonresp["EnvironmentVariables"][envvar]["value"]
					if envvar in list(os.environ.keys()):
						# envvalue = os.environ[envvar]
						if envvar in self.managedenvvars and os.environ[envvar] != localval:
							os.environ[envvar] = localval
							debug.debugmsg(1, "Setting Environment Variable:", envvar, "=", localval)
					else:
						self.managedenvvars.append(envvar)
						os.environ[envvar] = localval
						debug.debugmsg(1, "Setting Environment Variable:", envvar, "=", localval)

			if jsonresp["StartTime"] < int(time.time()) < (jsonresp["EndTime"] + 300):
				self.isrunning = True
				self.run_name = jsonresp["RunName"]
				for s in jsonresp["Schedule"].keys():
					debug.debugmsg(6, "getjobs: s:", s)
					if s not in self.jobs.keys():
						self.jobs[s] = {}
					for k in jsonresp["Schedule"][s].keys():
						debug.debugmsg(6, "getjobs: self.jobs[", s, "][", k, "]", jsonresp["Schedule"][s][k])
						self.jobs[s][k] = jsonresp["Schedule"][s][k]
					if "UploadMode" in jsonresp:
						self.jobs[s]["UploadMode"] = jsonresp["UploadMode"]

				if int(time.time()) > jsonresp["EndTime"]:
					self.isstopping = True
				if self.isstopping and self.robotcount < 1 and self.monitorcount < 1:
					self.jobs = {}
					self.isrunning = False
					self.isstopping = False
			else:
				if self.robotcount < 1:
					self.isrunning = False
					self.isstopping = False
				else:
					self.isstopping = True

			debug.debugmsg(7, "jsonresp[Abort]", jsonresp["Abort"])
			if jsonresp["Abort"]:
				self.isstopping = True
				debug.debugmsg(5, "!!! Abort !!!")
				self.abortjobs()

			debug.debugmsg(5, "getjobs: isrunning:", self.isrunning, "	isstopping:", self.isstopping)
			debug.debugmsg(7, "getjobs: self.jobs:", self.jobs)

		except Exception as e:
			debug.debugmsg(1, "getjobs: Exception:", e)

	def abortjobs(self):
		debug.debugmsg(6, "self.jobs:", self.jobs)
		for job in self.jobs:
			try:
				debug.debugmsg(6, "job:", job, self.jobs[job])
				debug.debugmsg(5, "job[PID]:", self.jobs[job]["PID"])
				debug.debugmsg(6, "job[Process]:", self.jobs[job]["Process"])
				p = self.jobs[job]["Process"]
				p.terminate()

			except Exception as e:
				debug.debugmsg(1, "getjobs: Exception:", e)

	def runjobs(self):
		debug.debugmsg(6, "runjobs: self.jobs:", self.jobs)
		workingkeys = list(self.jobs.keys())
		if not self.isstopping:
			for jobid in workingkeys:
				if jobid in self.jobs.keys():
					debug.debugmsg(6, "runjobs: jobid:", jobid)
					run_t = True
					if "Thread" in self.jobs[jobid].keys():
						debug.debugmsg(7, "jobid:", self.jobs[jobid])
						try:
							# if self.jobs[jobid]["Thread"].isAlive():
							# The isAlive syntax above was perviously working in python < 3.7
							# but appears to have been removed in 3.9.1? it was depricated in 2.x?
							# and the is_alive syntax below has been available since python version 2.6
							if self.jobs[jobid]["Thread"].is_alive():
								run_t = False
								debug.debugmsg(7, "Thread already running run_t:", run_t)
						except Exception as e:
							run_t = False
							debug.debugmsg(5, "Thread running check failed run_t:", run_t, e)

					debug.debugmsg(6, "run_t:", run_t)

					if run_t:
						debug.debugmsg(5, "jobid:", jobid, "run_t:", run_t, "StartTime:", self.jobs[jobid]["StartTime"], "< Now:", int(time.time()), "< EndTime:", self.jobs[jobid]["EndTime"])
						if self.jobs[jobid]["StartTime"] < int(time.time()) < self.jobs[jobid]["EndTime"]:
							t = threading.Thread(target=self.runthread, args=(jobid, ))
							t.start()
							self.jobs[jobid]["Thread"] = t
							debug.debugmsg(5, "Thread started for jobid:", jobid)
						else:
							debug.debugmsg(5, "Thread not started for jobid:", jobid)
				time.sleep(0.1)

	def runthread(self, jobid):
		now = int(time.time())

		self.ensure_listner_file()
		self.ensure_repeater_listner_file()

		if "ScriptIndex" not in self.jobs[jobid]:
			debug.debugmsg(5, "runthread: jobid:", jobid)
			debug.debugmsg(5, "runthread: job data:", self.jobs[jobid])
			jobarr = jobid.split("_")
			self.jobs[jobid]["ScriptIndex"] = jobarr[0]
			self.jobs[jobid]["Robot"] = jobarr[1]
			self.jobs[jobid]["Iteration"] = 0
			self.jobs[jobid]["RobotType"] = "Plan"
			if jobarr[0].lower()[0] == "m":
				self.jobs[jobid]["RobotType"] = "Monitor"
			debug.debugmsg(5, "runthread: job data:", self.jobs[jobid])

		self.jobs[jobid]["Iteration"] += 1

		debug.debugmsg(5, "self.jobs[jobid]:", self.jobs[jobid])

		# jobfile = os.path.join(self.scriptdir, "job_{}.json".format(jobid))
		jobfile = os.path.join(self.scriptdir, "RFS_Job_{}_{}.json".format(self.jobs[jobid]["ScriptIndex"], self.jobs[jobid]["Robot"]))

		jobdata = {}
		jobdata["StartTime"] = self.jobs[jobid]["StartTime"]
		jobdata["EndTime"] = self.jobs[jobid]["EndTime"]
		jobdata["Iteration"] = self.jobs[jobid]["Iteration"]
		jobdata["Index"] = self.jobs[jobid]["ScriptIndex"]
		jobdata["Robot"] = self.jobs[jobid]["Robot"]
		jobdata["jobid"] = jobid
		jobdata["Test"] = self.jobs[jobid]["Test"]

		with open(jobfile, 'w', encoding="utf-8") as jfile:
			jfile.write(json.dumps(jobdata))

		hash = self.jobs[jobid]['ScriptHash']
		debug.debugmsg(6, "runthread: hash:", hash)
		test = self.jobs[jobid]['Test']
		debug.debugmsg(6, "runthread: test:", test)
		if platform.system() != 'Windows':
			test = test.replace(r'${', r'\${')
			debug.debugmsg(6, "runthread: test:", test)
		test = test.replace(r'"', r'\"')

		if hash not in self.scriptlist:
			self.getfile(hash)

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
		debug.debugmsg(6, "runthread: localfile:", localfile)

		file = self.scriptlist[hash]['file']
		debug.debugmsg(6, "runthread: file:", file)

		farr = os.path.splitext(file)
		debug.debugmsg(6, "runthread: farr:", farr)

		excludelibraries = ",".join(self.excludelibraries)
		if "excludelibraries" in self.jobs[jobid]:
			# not sure if we need to do this???
			# for safety split and join string
			# ellst = self.jobs[jobid]['excludelibraries'].split(",")
			# excludelibraries = ",".join(ellst)
			excludelibraries = self.jobs[jobid]['excludelibraries']

		debug.debugmsg(6, "excludelibraries:", excludelibraries)
		excludelibrarielst = excludelibraries.split(",")
		excludelibrarielst = map(str.strip, excludelibrarielst)
		excludelibraries = ",".join(excludelibrarielst)
		debug.debugmsg(6, "excludelibraries:", excludelibraries)

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
		debug.debugmsg(6, "runthread: odir:", odir)
		try:
			if not os.path.exists(odir):
				os.makedirs(odir)
		except Exception:
			pass

		oprefix = self.make_safe_filename(test)
		debug.debugmsg(6, "runthread: oprefix:", oprefix)
		logFileName = os.path.join(odir, "{}.log".format(oprefix))
		debug.debugmsg(6, "runthread: logFileName:", logFileName)
		outputFileName = "{}_output.xml".format(oprefix)
		outputFile = os.path.join(odir, outputFileName)
		debug.debugmsg(6, "runthread: outputFile:", outputFile)

		if 'Agent' not in config.data:
			config.data['Agent'] = {}
			config.saveini()

		if 'robotcmd' not in config.data['Agent']:
			config.data['Agent']['robotcmd'] = "robot"
			config.saveini()

		robotcmd = config.data['Agent']['robotcmd']
		if self.args.robot:
			debug.debugmsg(1, "runthread: self.args.robot: ", self.args.robot)
			robotcmd = self.args.robot

		debug.debugmsg(6, "runthread: robotcmd:", robotcmd)

		cmd = [robotcmd]

		if "robotoptions" in self.jobs[jobid]:
			cmd.append("{}".format(self.jobs[jobid]['robotoptions']))

		debug.debugmsg(9, "runthread: cmd:", cmd)

		cmd.append("-t")
		cmd.append('"' + test + '"')
		cmd.append("-d")
		cmd.append('"' + odir + '"')

		metavars = []
		metavars.append("RFS_AGENTNAME:{}".format(self.agentname))
		metavars.append("RFS_AGENTVERSION:{}".format(self.version))
		metavars.append("RFS_DEBUGLEVEL:{}".format(debug.debuglvl))
		metavars.append("RFS_INDEX:{}".format(self.jobs[jobid]["ScriptIndex"]))
		metavars.append("RFS_ROBOT:{}".format(self.jobs[jobid]["Robot"]))
		metavars.append("RFS_ITERATION:{}".format(self.jobs[jobid]["Iteration"]))
		metavars.append("RFS_SWARMMANAGER:{}".format(self.manager.swarmmanager))
		metavars.append("RFS_EXCLUDELIBRARIES:{}".format(excludelibraries))
		metavars.append("RFS_ROBOTTYPE:{}".format(self.jobs[jobid]["RobotType"]))

		if "excludesleep" in self.jobs[jobid]:
			metavars.append("RFS_EXCLUDESLEEP:{}".format(self.jobs[jobid]["excludesleep"]))

		if "includetesttime" in self.jobs[jobid]:
			metavars.append("RFS_INCLUDETESTTIME:{}".format(self.jobs[jobid]["includetesttime"]))

		if "applypacingtime" in self.jobs[jobid]:
			metavars.append("RFS_APPLYPACINGTIME:{}".format(self.jobs[jobid]["applypacingtime"]))

		if "applypacingstart" in self.jobs[jobid]:
			metavars.append("RFS_APPLYPACINGSTART:{}".format(self.jobs[jobid]["applypacingstart"]))

		if "injectsleepenabled" in self.jobs[jobid]:
			metavars.append("RFS_INJECTSLEEP:{}".format(self.jobs[jobid]["injectsleepenabled"]))
			if self.str2bool(self.jobs[jobid]["injectsleepenabled"]):
				# injectsleepminimum
				if "injectsleepminimum" in self.jobs[jobid]:
					metavars.append("RFS_SLEEPMINIMUM:{}".format(self.jobs[jobid]["injectsleepminimum"]))
				# injectsleepmaximum
				if "injectsleepmaximum" in self.jobs[jobid]:
					metavars.append("RFS_SLEEPMAXIMUM:{}".format(self.jobs[jobid]["injectsleepmaximum"]))

		if "resultnamemode" in self.jobs[jobid]:
			metavars.append("RFS_RESULTNAMEMODE:{}".format(self.jobs[jobid]["resultnamemode"]))

		for metavar in metavars:
			cmd.append("-M {}".format(metavar))
			cmd.append("-v {}".format(metavar))

		if self.xmlmode:
			# for now this is going to be the easiest way to deal with this for RF7+
			# Unlikely many people will use xmlmode with RF7 anyway, it's not the default
			# and was only left in for compatability with early beta's and alphas of RFSwarm
			# so I expect everyone has already moved on to the listener mode by now, only putting
			# this in just in case someone is still using xmlmode.
			rfver = self.agentproperties["RobotFramework"]
			if int(rfver[0]) >= 7:
				debug.debugmsg(7, "Use legacyoutput mode for RF7+")
				cmd.append("--legacyoutput")

		if not self.xmlmode:
			cmd.append("--listener {}".format('"' + self.listenerfile + '"'))

		debug.debugmsg(9, "runthread: cmd:", cmd)

		debug.debugmsg(9, "Check for runthread: robotexe")
		if "testrepeater" in self.jobs[jobid]:
			debug.debugmsg(7, "runthread: self.jobs[jobid][testrepeater]:", self.jobs[jobid]["testrepeater"])
			debug.debugmsg(9, "runthread: self.jobs[jobid][testrepeater]:", self.str2bool(self.jobs[jobid]["testrepeater"]), type(self.str2bool(self.jobs[jobid]["testrepeater"])))
			if self.str2bool(self.jobs[jobid]["testrepeater"]):
				cmd.append("--listener {}".format('"' + self.repeaterfile + '"'))

		debug.debugmsg(9, "runthread: cmd:", cmd)

		# disableloglog': 'True',
		if "disableloglog" in self.jobs[jobid]:
			if self.str2bool(self.jobs[jobid]["disableloglog"]):
				cmd.append("-l NONE")
		# 'disablelogreport': 'True',
		if "disablelogreport" in self.jobs[jobid]:
			if self.str2bool(self.jobs[jobid]["disablelogreport"]):
				cmd.append("-r NONE")
		# 'disablelogoutput': 'True',
		disablelogoutput = False
		if "disablelogoutput" in self.jobs[jobid]:
			disablelogoutput = self.str2bool(self.jobs[jobid]["disablelogoutput"])
		if self.xmlmode:
			disablelogoutput = False
		if disablelogoutput:
			cmd.append("-o NONE")
		else:
			cmd.append("-o")
			cmd.append('"' + outputFile + '"')

		cmd.append('"' + localfile + '"')

		robotexe = shutil.which(robotcmd)
		debug.debugmsg(6, "runthread: robotexe:", robotexe)
		if robotexe is not None:

			if self.jobs[jobid]["RobotType"] in ["Monitor"]:
				self.monitorcount += 1
			else:
				self.robotcount += 1

			result = 0
			try:
				os.chdir(self.scriptdir)
				# https://stackoverflow.com/questions/4856583/how-do-i-pipe-a-subprocess-call-to-a-text-file
				with open(logFileName, "w", encoding="utf-8") as f:
					debug.debugmsg(3, "Robot run with command: '", " ".join(cmd), "'")
					# result = subprocess.call(" ".join(cmd), shell=True, stdout=f, stderr=f)
					try:
						proc = subprocess.Popen(" ".join(cmd), shell=True, stdout=f, stderr=subprocess.STDOUT)
						debug.debugmsg(5, "runthread: proc:", proc)
						self.jobs[jobid]["Process"] = proc
						self.jobs[jobid]["PID"] = proc.pid
						debug.debugmsg(5, "runthread: proc.pid:", proc.pid)
						result = proc.wait()
						debug.debugmsg(5, "runthread: result:", result)
						if result != 0:
							debug.debugmsg(1, "Robot returned an error (", result, ") please check the log file:", logFileName)
					except Exception as e:
						debug.debugmsg(1, "Robot returned an error:", e, " \nplease check the log file:", logFileName)
						result = 1
					f.close()

				if os.path.exists(jobfile):
					os.remove(jobfile)

				if self.xmlmode:
					if os.path.exists(outputFile):
						if self.xmlmode:
							t = threading.Thread(target=self.run_process_output, args=(outputFile, self.jobs[jobid]["ScriptIndex"], self.jobs[jobid]["Robot"], self.jobs[jobid]["Iteration"]))
							t.start()
					else:
						debug.debugmsg(1, "Robot didn't create (", outputFile, ") please check the log file:", logFileName)

			except Exception as e:
				debug.debugmsg(5, "Robot returned an error:", e)
				result = 1

			uploadmode = self.uploadmode
			debug.debugmsg(5, "uploadmode:", uploadmode)
			debug.debugmsg(5, "self.jobs[", jobid, "]:", self.jobs[jobid])
			if "UploadMode" in self.jobs[jobid]:
				uploadmode = self.jobs[jobid]["UploadMode"]
				debug.debugmsg(5, "uploadmode:", uploadmode)

			# Uplad any files found
			self.queue_file_upload(uploadmode, result, odir)

			if self.jobs[jobid]["RobotType"] in ["Monitor"]:
				self.monitorcount += -1
			else:
				self.robotcount += -1

		else:
			debug.debugmsg(1, "Could not find robot executeable:", robotexe)

	def queue_file_upload(self, mode, retcode, filedir):
		reldir = os.path.basename(filedir)
		debug.debugmsg(7, mode, retcode, reldir, filedir)

		filelst = self.file_upload_list(filedir)
		debug.debugmsg(7, "filelst", filelst)
		# filelst
		# [
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1.log',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/log.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/report.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1_output.xml'
		# ]
		#

		rundir = os.path.join(self.logdir, self.run_name)

		debug.debugmsg(5, "mode:", mode, "	retcode:", retcode)
		# 	uploadmodes = {'imm':"Immediately", 'err':"On Error Only", 'def':"All Defered"}

		for file in filelst:
			fobj = {}
			fobj["LocalFilePath"] = file
			fobj["RelFilePath"] = os.path.relpath(file, start=rundir)
			self.upload_queue.append(fobj)
			debug.debugmsg(7, "added to upload_queue", fobj)
			if mode == "err" and retcode > 0:
				# upload now
				self.file_upload(fobj)
			if mode == "imm":
				# upload now
				self.file_upload(fobj)

	def file_upload_list(self, filedir):
		retlst = []
		dirlst = os.listdir(path=filedir)
		debug.debugmsg(7, "dirlst", dirlst)
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
		debug.debugmsg(7, "fileobj", fileobj)

		# Hash file

		hash = FilesTransfers.hash_file(fileobj['LocalFilePath'], fileobj['RelFilePath'])
		debug.debugmsg(7, "hash", hash)

		# 	check file exists on manager?

		uri = self.manager.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Status",
			"Hash": hash
		}
		debug.debugmsg(9, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(7, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
			self.manager.isconnected = False

		if not self.manager.isconnected:
			return None

		jsonresp = {}
		try:
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)
			return None

		# 	If file not exists upload the file
		if jsonresp["Exists"] == "False":
			debug.debugmsg(6, "file not there, so lets upload")

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
			debug.debugmsg(9, "buf:", buf)
			compressed = lzma.compress(buf)
			debug.debugmsg(9, "compressed:", compressed)
			encoded = base64.b64encode(compressed)
			debug.debugmsg(9, "encoded:", encoded)

			payload["FileData"] = encoded.decode('ASCII')

			debug.debugmsg(8, "payload: ", payload)

			try:
				r = requests.post(uri, json=payload, timeout=self.timeout)
				debug.debugmsg(7, "resp: ", r.status_code, r.text)
				if r.status_code != requests.codes.ok:
					debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
					debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
					self.manager.isconnected = False

			except Exception as e:
				debug.debugmsg(8, "Exception:", e)
				debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				self.manager.isconnected = False

			if not self.manager.isconnected:
				return None

			jsonresp = {}
			try:
				# self.scriptlist
				jsonresp = json.loads(r.text)
				debug.debugmsg(7, "jsonresp:", jsonresp)
			except Exception as e:
				debug.debugmsg(1, "Exception:", e)
				return None

		# once sucessful remove from queue
		if fileobj in self.upload_queue:
			self.upload_queue.remove(fileobj)

	def process_file_upload_queue(self):
		corecount = psutil.cpu_count()
		threadcount = corecount * 3
		debug.debugmsg(7, "upload_queue", self.upload_queue)
		debug.debugmsg(5, "corecount", corecount, "	threadcount:", threadcount)
		# self.process_file_upload_queue
		for fobj in self.upload_queue:
			# limit the number of upload threads so we don't max out the agent and cause it
			# to go into critical/offline? mode
			debug.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
			while len(list(self.upload_threads.keys())) > threadcount - 1:
				debug.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
				# key = list(self.upload_threads.keys())[0]
				key = random.choice(list(self.upload_threads.keys()))
				debug.debugmsg(5, "key:", key)
				if key in self.upload_threads and self.upload_threads[key].is_alive():
					self.upload_threads[key].join()
				if key in self.upload_threads:
					del self.upload_threads[key]
			key = str(uuid.uuid4())
			debug.debugmsg(5, "key:", key)
			self.upload_threads[key] = threading.Thread(target=self.file_upload, args=(fobj,))
			self.upload_threads[key].start()
			time.sleep(0.5)
		for key in list(self.upload_threads.keys()):
			debug.debugmsg(5, "key:", key)
			if key in self.upload_threads and self.upload_threads[key].is_alive():
				self.upload_threads[key].join()
			if key in self.upload_threads:
				del self.upload_threads[key]
		gc.collect()

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
			debug.debugmsg(1, "Error parsing XML file:", outputFile)
		debug.debugmsg(6, "tree: '", tree)
		root = tree.getroot()
		debug.debugmsg(6, "root: '", root)
		# .//kw/msg/..[not(@library='BuiltIn')]
		for result in root.findall(".//kw/msg/..[@library]"):
			debug.debugmsg(6, "run_process_output: result: ", result)
			library = result.get('library')
			# if library not in ["BuiltIn", "String", "OperatingSystem", "perftest"]:
			if library not in self.excludelibraries:
				debug.debugmsg(6, "run_process_output: library: ", library)
				seq += 1
				debug.debugmsg(6, "result: library:", library)
				txn = result.find('msg').text
				debug.debugmsg(6, "result: txn:", txn)

				el_status = result.find('status')
				status = el_status.get('status')
				debug.debugmsg(6, "result: status:", status)
				starttime = el_status.get('starttime')
				debug.debugmsg(6, "result: starttime:", starttime)
				endtime = el_status.get('endtime')
				debug.debugmsg(6, "result: endtime:", endtime)

				# 20191026 09:34:23.044
				startdate = datetime.strptime(starttime, '%Y%m%d %H:%M:%S.%f')
				enddate = datetime.strptime(endtime, '%Y%m%d %H:%M:%S.%f')

				elapsedtime = enddate.timestamp() - startdate.timestamp()

				debug.debugmsg(
					6, "resultname: '", txn,
					"' result'", status,
					"' elapsedtime'", elapsedtime,
					"' starttime'", starttime,
					"' endtime'", endtime, "'"
				)

				# Send result to manager
				uri = self.manager.swarmmanager + "Result"

				debug.debugmsg(6, "run_proces_output: uri", uri)

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

				debug.debugmsg(6, "run_proces_output: payload", payload)
				try:
					r = requests.post(uri, json=payload, timeout=self.timeout)
					debug.debugmsg(6, "run_proces_output: ", r.status_code, r.text)
					if r.status_code != requests.codes.ok:
						debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
						debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
						self.manager.isconnected = False
				except Exception as e:
					debug.debugmsg(8, "Exception:", e)
					debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
					self.manager.isconnected = False

		for result in root.findall(".//kw/doc/.."):
			debug.debugmsg(6, "run_process_output: result: ", result)
			library = result.get('library')
			# if library not in ["BuiltIn", "String", "OperatingSystem", "perftest"]:
			if library not in self.excludelibraries:
				debug.debugmsg(6, "run_process_output: library: ", library)
				seq += 1
				debug.debugmsg(6, "result: library:", library)
				txn = result.find('doc').text
				debug.debugmsg(6, "result: txn:", txn)

				el_status = result.find('status')
				status = el_status.get('status')
				debug.debugmsg(6, "result: status:", status)
				starttime = el_status.get('starttime')
				debug.debugmsg(6, "result: starttime:", starttime)
				endtime = el_status.get('endtime')
				debug.debugmsg(6, "result: endtime:", endtime)

				# 20191026 09:34:23.044
				startdate = datetime.strptime(starttime, '%Y%m%d %H:%M:%S.%f')
				enddate = datetime.strptime(endtime, '%Y%m%d %H:%M:%S.%f')

				elapsedtime = enddate.timestamp() - startdate.timestamp()

				debug.debugmsg(
					6, "resultname: '", txn,
					"' result'", status,
					"' elapsedtime'", elapsedtime,
					"' starttime'", starttime,
					"' endtime'", endtime, "'"
				)

				# Send result to manager
				uri = self.manager.swarmmanager + "Result"

				debug.debugmsg(6, "run_proces_output: uri", uri)

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

				debug.debugmsg(6, "run_proces_output: payload", payload)
				try:
					r = requests.post(uri, json=payload, timeout=self.timeout)
					debug.debugmsg(6, "run_proces_output: ", r.status_code, r.text)
					if r.status_code != requests.codes.ok:
						debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
						debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
						self.manager.isconnected = False
				except Exception as e:
					debug.debugmsg(8, "Exception:", e)
					debug.debugmsg(0, "Manager Disconnected", self.manager.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
					self.manager.isconnected = False

	def configparser_safe_dict(self, dictin):
		debug.debugmsg(7, "dictin: ", dictin)
		dictout = dictin
		for k in dictout.keys():
			debug.debugmsg(7, "value type: ", type(dictout[k]))
			if isinstance(dictout[k], dict):
				dictout[k] = config.configparser_safe_dict(dictout[k])
			if dictout[k] is None:
				dictout[k] = ""
		debug.debugmsg(7, "dictout: ", dictout)
		return dictout

	def make_safe_filename(self, s):
		def safe_string(s):
			return re.sub(r'[<>:"/\\|?*\n\t]', "_", s)
		return "".join(safe_string(s)).rstrip("_")

	def ensuredir(self, dir):
		if os.path.exists(dir):
			return True
		try:
			patharr = os.path.split(dir)
			debug.debugmsg(6, "patharr: ", patharr)
			self.ensuredir(patharr[0])
			os.mkdir(dir, mode=0o777)
			debug.debugmsg(5, "Directory Created: ", dir)
			return True
		except FileExistsError:
			debug.debugmsg(5, "Directory Exists: ", dir)
			return False
		except Exception as e:
			debug.debugmsg(1, "Directory Create failed: ", dir)
			debug.debugmsg(1, "with error: ", e)
			return False

	def ensure_listner_file(self):
		if not self.xmlmode:
			debug.debugmsg(6, "self.xmlmode: ", self.xmlmode)
			if self.listenerfile is None:
				self.create_listner_file()
			else:
				if not os.path.isfile(self.listenerfile):
					self.create_listner_file()

	def ensure_repeater_listner_file(self):
		if self.repeaterfile is None:
			self.create_repeater_listner_file()

	def create_listner_file(self):

		while "RobotFramework" not in self.agentproperties:
			time.sleep(0.1)
		rfver = self.agentproperties["RobotFramework"]
		debug.debugmsg(5, "RobotFramework version:", rfver, " RobotFramework major version:", int(rfver[0]))
		# lrfver = rfver.split(".")
		if int(rfver[0]) >= 7:
			self.create_V3_listner_file()
		else:
			self.create_V2_listner_file()

	def create_V3_listner_file(self):

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener3.py")
		debug.debugmsg(5, "listenerfile", self.listenerfile)

		# srcdir
		listenersrc = os.path.join(self.srcdir, "resources", "RFSListener3.py")
		debug.debugmsg(5, "listenersrc", listenersrc)
		shutil.copy(listenersrc, self.listenerfile)


	def create_V2_listner_file(self):

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener2.py")
		debug.debugmsg(5, "listenerfile", self.listenerfile)

		# srcdir
		listenersrc = os.path.join(self.srcdir, "resources", "RFSListener2.py")
		debug.debugmsg(5, "listenersrc", listenersrc)
		shutil.copy(listenersrc, self.listenerfile)

	def create_repeater_listner_file(self):
		self.repeaterfile = os.path.join(self.scriptdir, "RFSTestRepeater.py")
		debug.debugmsg(5, "repeaterfile", self.repeaterfile)

		# srcdir
		repeatersrc = os.path.join(self.srcdir, "resources", "RFSTestRepeater.py")
		debug.debugmsg(5, "repeatersrc", repeatersrc)
		shutil.copy(repeatersrc, self.repeaterfile)

	def on_closing(self, _event=None, *args):
		self.runagent = False
		debug.debugmsg(0, "Shutting down agent")

		for thread in self.corethreads:
			debug.debugmsg(3, "Join Agent Thread:", thread)
			self.corethreads[thread].join()

		for jobid in self.jobs:
			# self.jobs[jobid]["Thread"]
			# debug.debugmsg(3, "Join Agent Manager Thread")
			# self.Agentserver.join()

			debug.debugmsg(3, "Join Agent Thread:", jobid)
			if "Thread" in self.jobs[jobid]:
				self.jobs[jobid]["Thread"].join()

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
					raise e

			except Exception as e:
				debug.debugmsg(3, "Failed to exit with error:", e)
				os._exit(1)
		sys.stdout.flush()
		sys.stderr.flush()
