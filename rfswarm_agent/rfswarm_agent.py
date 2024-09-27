#!/usr/bin/python
#
# 	Robot Framework Swarm
#
#    Version 1.4.0
#


# https://stackoverflow.com/questions/48090535/csv-file-reading-and-find-the-value-from-nth-column-using-robot-framework

import argparse
import base64
import configparser
import gc
import hashlib
import importlib.metadata
import inspect
import json
import lzma
import os
import platform
import random
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


class RFSwarmAgent():

	version = "1.4.0"
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
	repeaterfile = None
	ipaddresslist: Any = []
	agentname = None
	agentproperties: Any = {}
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
	status = "Ready"
	excludelibraries: Any = []
	args = None
	xmlmode = False
	timeout = 600
	uploadmode = "err"
	managedenvvars: Any = []

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
		parser.add_argument('-c', '--create', help='ICON : Create application icon / shortcut')
		self.args = parser.parse_args()

		self.debugmsg(6, "self.args: ", self.args)

		if self.args.debug:
			self.debuglvl = int(self.args.debug)

		if self.args.version:
			exit()

		if self.args.create:
			if self.args.create.upper() in ["ICON", "ICONS"]:
				self.create_icons()
			else:
				self.debugmsg(0, "create with option ", self.args.create.upper(), "not supported.")
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

		self.findlibraries() 	# Need to wait for findlibraries() to finish before calling ensure_listner_file() for RF version check
		self.ensure_listner_file()
		self.ensure_repeater_listner_file()

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

	def create_icons(self):
		self.debugmsg(0, "Creating application icons for RFSwarm Agent")
		appname = "RFSwarm Agent"
		namelst = appname.split()
		self.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		self.debugmsg(6, "projname:", projname)
		pipdata = importlib.metadata.distribution(projname)
		# print("files:", pipdata.files)
		# print("file0:", pipdata.files[0])
		agent_executable = os.path.abspath(str(pipdata.locate_file(pipdata.files[0])))
		self.debugmsg(5, "agent_executable:", agent_executable)

		script_dir = os.path.dirname(os.path.abspath(__file__))
		self.debugmsg(5, "script_dir:", script_dir)
		icon_dir = os.path.join(pipdata.locate_file('rfswarm_agent'), "icons")
		self.debugmsg(5, "icon_dir:", icon_dir)

		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				fileprefix = "/usr/share"

			fileprefix = os.path.expanduser(fileprefix)

			self.debugmsg(5, "Create .directory file")
			directorydata = []
			directorydata.append('[Desktop Entry]\n')
			directorydata.append('Type=Directory\n')
			directorydata.append('Name=RFSwarm\n')
			directorydata.append('Icon=rfswarm-logo\n')

			directoryfilename = os.path.join(fileprefix, "desktop-directories", "rfswarm.directory")
			directorydir = os.path.dirname(directoryfilename)
			self.ensuredir(directorydir)

			self.debugmsg(5, "directoryfilename:", directoryfilename)
			with open(directoryfilename, 'w') as df:
				df.writelines(directorydata)

			directoryfilename = os.path.join(fileprefix, "applications", "rfswarm.directory")
			directorydir = os.path.dirname(directoryfilename)
			self.ensuredir(directorydir)
			self.debugmsg(5, "directoryfilename:", directoryfilename)
			with open(directoryfilename, 'w') as df:
				df.writelines(directorydata)

			self.debugmsg(5, "Create .desktop file")
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

			dektopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
			dektopdir = os.path.dirname(dektopfilename)
			self.ensuredir(dektopdir)

			self.debugmsg(5, "dektopfilename:", dektopfilename)
			with open(dektopfilename, 'w') as df:
				df.writelines(desktopdata)

			self.debugmsg(5, "Copy icons")
			# /usr/share/icons/hicolor/128x128/apps/
			# 	1024x1024  128x128  16x16  192x192  22x22  24x24  256x256  32x32  36x36  42x42  48x48  512x512  64x64  72x72  8x8  96x96
			# or
			#  ~/.local/share/icons/hicolor/256x256/apps/
			src_iconx128 = os.path.join(icon_dir, projname + "-128.png")
			self.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", projname + ".png")
			dst_icondir = os.path.dirname(dst_iconx128)
			self.ensuredir(dst_icondir)
			self.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

			src_iconx128 = os.path.join(icon_dir, "rfswarm-logo-128.png")
			self.debugmsg(5, "src_iconx128:", src_iconx128)
			dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", "rfswarm-logo.png")
			self.debugmsg(5, "dst_iconx128:", dst_iconx128)
			shutil.copy(src_iconx128, dst_iconx128)

		if platform.system() == 'Darwin':
			self.debugmsg(5, "Create folder structure in /Applications")
			src_iconx1024 = os.path.join(icon_dir, projname + "-1024.png")

			self.create_macos_app_bundle(appname, pipdata.version, agent_executable, src_iconx1024)

		if platform.system() == 'Windows':
			self.debugmsg(5, "Create Startmenu shorcuts")
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
		self.debugmsg(6, "psscript:", psscript)

		response = os.popen('powershell.exe -command ' + psscript).read()

		self.debugmsg(6, "response:", response)

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
		self.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		self.debugmsg(6, "projname:", projname)
		signature = "RFS{0}".format(namelst[1].upper())
		self.debugmsg(6, "signature:", signature)

		ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
		iconset = os.path.join(ResourcesFolder, projname + ".iconset")
		icnsfile = os.path.join(ResourcesFolder, projname + ".icns")
		self.ensuredir(iconset)

		# Normal screen icons
		self.debugmsg(6, "Normal screen icons")
		for size in [16, 32, 64, 128, 256, 512]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{0}x{0}.png'".format(size, icosrc, iconset)
			self.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			self.debugmsg(6, "response:", response)

		# Retina display icons
		self.debugmsg(6, "Retina display icons")
		for size in [32, 64, 128, 256, 512, 1024]:
			cmd = "sips -z {0} {0} {1} --out '{2}/icon_{3}x{3}x2.png'".format(size, icosrc, iconset, int(size / 2))
			self.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			self.debugmsg(6, "response:", response)

		# Make a multi-resolution Icon
		self.debugmsg(6, "Make a multi-resolution Icon")
		cmd = "iconutil -c icns -o '{0}' '{1}'".format(icnsfile, iconset)
		self.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		self.debugmsg(6, "response:", response)

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
		self.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		self.debugmsg(6, "response:", response)

		# # Try re-registering your application with Launch Services:
		# # /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f /Applications/MyTool.app
		# lsregister = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
		# cmd = "{0} -f '{1}'".format(lsregister, apppath)
		# self.debugmsg(6, "cmd:", cmd)
		# response = os.popen(cmd).read()
		# self.debugmsg(6, "response:", response)

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
						self.debugmsg(5, "self.status:", self.status, "len(self.upload_queue):", len(self.upload_queue))
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
				bytes_speed = nicstats[nic].speed * 1024 * 1024 / 8
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
			"Properties": self.agentproperties,
			"FileCount": len(list(self.scriptlist.keys()))
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			self.debugmsg(8, r.status_code, r.text)
			if r.status_code != requests.codes.ok:
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
				if r.status_code == requests.codes.ok:
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
		# post python 3.8 method
		# This method works for python 3.8 and higher
		found = 0
		liblst = []

		installed_packages = importlib.metadata.distributions()
		for i in installed_packages:
			# if "robot" in i.metadata["Name"]:
			# print(dist.metadata["Name"], dist.version)
			if i.metadata["Name"].strip() == "robotframework":
				found = 1
				if "RobotFramework" in self.agentproperties:
					ver = self.higher_version(i.version, self.agentproperties["RobotFramework"])
					self.agentproperties["RobotFramework"] = ver
					self.debugmsg(6, i.metadata["Name"].strip(), i.version, "-->", ver)
				else:
					self.agentproperties["RobotFramework"] = i.version
					self.debugmsg(6, i.metadata["Name"].strip(), i.version)
			if i.metadata["Name"].startswith("robotframework-"):
				# print(i.key)
				keyarr = i.metadata["Name"].strip().split("-")
				self.debugmsg(7, keyarr, i.version)
				#  next overwrites previous
				if "RobotFramework: Library: " + keyarr[1] in self.agentproperties:
					ver = self.higher_version(i.version, self.agentproperties["RobotFramework: Library: " + keyarr[1]])
					self.agentproperties["RobotFramework: Library: " + keyarr[1]] = ver
				else:
					self.agentproperties["RobotFramework: Library: " + keyarr[1]] = i.version
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

	def higher_version(self, versiona, versionb):
		lversiona = [int(v) for v in versiona.split(".")]
		lversionb = [int(v) for v in versionb.split(".")]
		for i in range(max(len(lversiona), len(lversionb))):
			v1 = lversiona[i] if i < len(lversiona) else 0
			v2 = lversionb[i] if i < len(lversionb) else 0
			if v1 > v2:
				return versiona
			elif v1 < v2:
				return versionb
		return versiona

	def getscripts(self):
		self.debugmsg(6, "getscripts")

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			self.debugmsg(5, "already processing the queue, don't double up")
			return None

		uri = self.swarmmanager + "Scripts"
		payload = {
			"AgentName": self.agentname
		}
		self.debugmsg(6, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			self.debugmsg(6, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
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
				if hash not in self.download_queue:
					self.download_queue.append(hash)
			else:
				self.debugmsg(6, "Check file")
				if 'localfile' in self.scriptlist[hash]:
					if not os.path.isfile(self.scriptlist[hash]['localfile']):
						if hash not in self.download_queue:
							self.download_queue.append(hash)
				else:
					self.debugmsg(6, "getfile")
					self.scriptlist[hash] = {'id': hash}
					if hash not in self.download_queue:
						self.download_queue.append(hash)

		if len(self.download_queue):
			self.process_file_download_queue()

	def process_file_download_queue(self):

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			self.debugmsg(5, "already processing the queue, don't double up")
			return None

		corecount = psutil.cpu_count()
		threadcount = corecount * 32
		self.debugmsg(7, "download_queue", self.download_queue)
		self.debugmsg(5, "corecount", corecount, "	threadcount:", threadcount)
		# for hash in self.download_queue:
		while len(self.download_queue) > 0:
			# limit the number of upload threads so we don't max out the agent and cause it
			# to go into critical/offline? mode

			hash = self.download_queue.pop(0)

			self.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
			while len(list(self.download_threads.keys())) > threadcount - 1:
				self.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
				# key = list(self.upload_threads.keys())[0]
				key = random.choice(list(self.download_threads.keys()))
				self.debugmsg(5, "key:", key)
				if key in self.download_threads and self.download_threads[key].is_alive():
					self.download_threads[key].join()
				if key in self.download_threads:
					del self.download_threads[key]
			key = str(uuid.uuid4())
			self.debugmsg(5, "key:", key)
			while hash in self.download_queue:
				self.download_queue.remove(hash)
			self.download_threads[key] = threading.Thread(target=self.getfile, args=(hash,))
			self.download_threads[key].start()
			time.sleep(0.02)
		for key in list(self.download_threads.keys()):
			self.debugmsg(5, "key:", key)
			if key in self.download_threads and self.download_threads[key].is_alive():
				self.download_threads[key].join()
			if key in self.download_threads:
				del self.download_threads[key]
		gc.collect()

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
			self.debugmsg(8, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				self.debugmsg(5, "resp: ", r.status_code, r.text)
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
			self.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			self.debugmsg(1, "Exception:", e)

		try:
			self.debugmsg(7, 'scriptdir', self.scriptdir)
			localfile = os.path.abspath(os.path.join(self.scriptdir, jsonresp['File']))
			self.debugmsg(5, 'localfile', localfile)

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
			self.debugmsg(1, 'Downloaded:', localfile)

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
			if r.status_code != requests.codes.ok:
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

			# RFSwarmAgent: getjobs(821): [7:7]	 getjobs: r.text: {"AgentName": "hp-elite-desk-800-g3", "StartTime": 0, "EndTime": 0, "RunName": "", "Abort": false, "UploadMode": "err", "EnvironmentVariables": {"RF_DIRECTORY": {"vartype": "path", "value": "rf_dir"}, "RF_MAGICNUM": {"vartype": "value", "value": "TWELVE"}}, "Schedule": {}}
			# "EnvironmentVariables": {"RF_DIRECTORY": {"vartype": "path", "value": "rf_dir"}, "RF_MAGICNUM": {"vartype": "value", "value": "TWELVE"}},
			if "EnvironmentVariables" in jsonresp:
				for envvar in list(jsonresp["EnvironmentVariables"].keys()):
					self.debugmsg(7, "envvar:", envvar, ":", jsonresp["EnvironmentVariables"][envvar])
					localval = ""
					if "vartype" in jsonresp["EnvironmentVariables"][envvar] and jsonresp["EnvironmentVariables"][envvar]["vartype"] == "path":
						localval = os.path.abspath(os.path.join(self.scriptdir, jsonresp["EnvironmentVariables"][envvar]["value"]))
						self.debugmsg(5, 'localval:', localval)
					else:
						if "value" in jsonresp["EnvironmentVariables"][envvar]:
							localval = jsonresp["EnvironmentVariables"][envvar]["value"]
					if envvar in list(os.environ.keys()):
						# envvalue = os.environ[envvar]
						if envvar in self.managedenvvars and os.environ[envvar] != localval:
							os.environ[envvar] = localval
							self.debugmsg(1, "Setting Environment Variable:", envvar, "=", localval)
					else:
						self.managedenvvars.append(envvar)
						os.environ[envvar] = localval
						self.debugmsg(1, "Setting Environment Variable:", envvar, "=", localval)

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
		self.ensure_repeater_listner_file()

		if "ScriptIndex" not in self.jobs[jobid]:
			self.debugmsg(6, "runthread: jobid:", jobid)
			self.debugmsg(6, "runthread: job data:", self.jobs[jobid])
			jobarr = jobid.split("_")
			self.jobs[jobid]["ScriptIndex"] = jobarr[0]
			self.jobs[jobid]["Robot"] = jobarr[1]
			self.jobs[jobid]["Iteration"] = 0
			self.debugmsg(6, "runthread: job data:", self.jobs[jobid])

		self.jobs[jobid]["Iteration"] += 1

		self.debugmsg(5, "self.jobs[jobid]:", self.jobs[jobid])

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
		self.debugmsg(6, "runthread: hash:", hash)
		test = self.jobs[jobid]['Test']
		self.debugmsg(6, "runthread: test:", test)
		if platform.system() != 'Windows':
			test = test.replace(r'${', r'\${')
			self.debugmsg(6, "runthread: test:", test)
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

		self.debugmsg(6, "excludelibraries:", excludelibraries)
		excludelibrarielst = excludelibraries.split(",")
		excludelibrarielst = map(str.strip, excludelibrarielst)
		excludelibraries = ",".join(excludelibrarielst)
		self.debugmsg(6, "excludelibraries:", excludelibraries)

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
				self.debugmsg(7, "Use legacyoutput mode for RF7+")
				cmd.append("--legacyoutput")

		if not self.xmlmode:
			cmd.append("--listener {}".format('"' + self.listenerfile + '"'))

		self.debugmsg(9, "runthread: cmd:", cmd)

		self.debugmsg(9, "Check for runthread: robotexe")
		if "testrepeater" in self.jobs[jobid]:
			self.debugmsg(7, "runthread: self.jobs[jobid][testrepeater]:", self.jobs[jobid]["testrepeater"])
			self.debugmsg(9, "runthread: self.jobs[jobid][testrepeater]:", self.str2bool(self.jobs[jobid]["testrepeater"]), type(self.str2bool(self.jobs[jobid]["testrepeater"])))
			if self.str2bool(self.jobs[jobid]["testrepeater"]):
				cmd.append("--listener {}".format('"' + self.repeaterfile + '"'))

		self.debugmsg(9, "runthread: cmd:", cmd)

		if "robotoptions" in self.jobs[jobid]:
			cmd.append("{}".format(self.jobs[jobid]['robotoptions']))

		self.debugmsg(9, "runthread: cmd:", cmd)

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
		self.debugmsg(6, "runthread: robotexe:", robotexe)
		if robotexe is not None:
			self.robotcount += 1

			result = 0
			try:
				os.chdir(self.scriptdir)
				# https://stackoverflow.com/questions/4856583/how-do-i-pipe-a-subprocess-call-to-a-text-file
				with open(logFileName, "w", encoding="utf-8") as f:
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

				if os.path.exists(jobfile):
					os.remove(jobfile)

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
			if r.status_code != requests.codes.ok:
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
				if r.status_code != requests.codes.ok:
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
		corecount = psutil.cpu_count()
		threadcount = corecount * 3
		self.debugmsg(7, "upload_queue", self.upload_queue)
		self.debugmsg(5, "corecount", corecount, "	threadcount:", threadcount)
		# self.process_file_upload_queue
		for fobj in self.upload_queue:
			# limit the number of upload threads so we don't max out the agent and cause it
			# to go into critical/offline? mode
			self.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
			while len(list(self.upload_threads.keys())) > threadcount - 1:
				self.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
				# key = list(self.upload_threads.keys())[0]
				key = random.choice(list(self.upload_threads.keys()))
				self.debugmsg(5, "key:", key)
				if key in self.upload_threads and self.upload_threads[key].is_alive():
					self.upload_threads[key].join()
				if key in self.upload_threads:
					del self.upload_threads[key]
			key = str(uuid.uuid4())
			self.debugmsg(5, "key:", key)
			self.upload_threads[key] = threading.Thread(target=self.file_upload, args=(fobj,))
			self.upload_threads[key].start()
			time.sleep(0.5)
		for key in list(self.upload_threads.keys()):
			self.debugmsg(5, "key:", key)
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
					if r.status_code != requests.codes.ok:
						self.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
						self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
						self.isconnected = False
				except Exception as e:
					self.debugmsg(8, "Exception:", e)
					self.debugmsg(0, "Manager Disconnected", self.swarmmanager, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
					self.isconnected = False

		for result in root.findall(".//kw/doc/.."):
			self.debugmsg(6, "run_process_output: result: ", result)
			library = result.get('library')
			# if library not in ["BuiltIn", "String", "OperatingSystem", "perftest"]:
			if library not in self.excludelibraries:
				self.debugmsg(6, "run_process_output: library: ", library)
				seq += 1
				self.debugmsg(6, "result: library:", library)
				txn = result.find('doc').text
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
					if r.status_code != requests.codes.ok:
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
		with open(self.agentini, 'w', encoding="utf-8") as configfile:    # save
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

	def ensure_repeater_listner_file(self):
		if self.repeaterfile is None:
			self.create_repeater_listner_file()

	def create_listner_file(self):

		while "RobotFramework" not in self.agentproperties:
			time.sleep(0.1)
		rfver = self.agentproperties["RobotFramework"]
		self.debugmsg(5, "RobotFramework version:", rfver, " RobotFramework major version:", int(rfver[0]))
		# lrfver = rfver.split(".")
		if int(rfver[0]) >= 7:
			self.create_V3_listner_file()
		else:
			self.create_V2_listner_file()

	def create_V3_listner_file(self):

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener3.py")
		self.debugmsg(5, "listenerfile", self.listenerfile)

		fd = []
		fd.append("")
		fd.append("import os")
		fd.append("import tempfile")
		fd.append("import sys")
		fd.append("import socket")
		fd.append("from datetime import datetime")
		fd.append("import time")
		fd.append("import random")
		fd.append("import requests")
		fd.append("import inspect")
		fd.append("import threading")
		fd.append("from robot.libraries.BuiltIn import BuiltIn")
		fd.append("from robot import result, running")
		fd.append("")
		fd.append("class RFSListener3:")
		fd.append("	ROBOT_LISTENER_API_VERSION = 3")
		fd.append("")
		fd.append("	msg = None")
		fd.append("	swarmmanager = \"http://localhost:8138/\"")
		fd.append("	excludelibraries = [\"BuiltIn\",\"String\",\"OperatingSystem\",\"perftest\"]")
		fd.append("	resultnamemode = \"dflt\"")
		fd.append("	debuglevel = 0")
		fd.append("	index = 0")
		fd.append("	robot = 0")
		fd.append("	iter = 0")
		fd.append("	seq = 0")
		fd.append("	injectsleep = False")
		fd.append("	sleepminimum = 15")
		fd.append("	sleepmaximum = 45")
		fd.append("")
		fd.append("	def start_suite(self, suite: running.TestSuite, result: result.TestSuite):")
		fd.append("		if 'RFS_DEBUGLEVEL' in result.metadata:")
		fd.append("			self.debuglevel = int(result.metadata['RFS_DEBUGLEVEL'])")
		fd.append("			self.debugmsg(6, 'debuglevel: ', self.debuglevel)")
		fd.append("		if 'RFS_INDEX' in result.metadata:")
		fd.append("			self.index = result.metadata['RFS_INDEX']")
		fd.append("			self.debugmsg(6, 'index: ', self.index)")
		fd.append("		if 'RFS_ITERATION' in result.metadata:")
		fd.append("			self.iter = result.metadata['RFS_ITERATION']")
		fd.append("			self.debugmsg(6, 'iter: ', self.iter)")
		fd.append("		if 'RFS_ROBOT' in result.metadata:")
		fd.append("			self.robot = result.metadata['RFS_ROBOT']")
		fd.append("			self.debugmsg(6, 'robot: ', self.robot)")
		fd.append("		if 'RFS_SWARMMANAGER' in result.metadata:")
		fd.append("			self.swarmmanager = result.metadata['RFS_SWARMMANAGER']")
		fd.append("			self.debugmsg(6, 'swarmmanager: ', self.swarmmanager)")
		fd.append("		if 'RFS_EXCLUDELIBRARIES' in result.metadata:")
		fd.append("			self.excludelibraries = result.metadata['RFS_EXCLUDELIBRARIES'].split(\",\")")
		fd.append("			self.debugmsg(6, 'excludelibraries: ', self.excludelibraries)")
		fd.append("		if 'RFS_INJECTSLEEP' in result.metadata:")
		fd.append("			self.injectsleep = result.metadata['RFS_INJECTSLEEP']")
		fd.append("			self.debugmsg(6, 'injectsleep: ', self.injectsleep)")
		fd.append("		if 'RFS_SLEEPMINIMUM' in result.metadata:")
		fd.append("			self.sleepminimum = result.metadata['RFS_SLEEPMINIMUM']")
		fd.append("			self.debugmsg(6, 'sleepminimum: ', self.sleepminimum)")
		fd.append("		if 'RFS_SLEEPMAXIMUM' in result.metadata:")
		fd.append("			self.sleepmaximum = result.metadata['RFS_SLEEPMAXIMUM']")
		fd.append("			self.debugmsg(6, 'sleepmaximum: ', self.sleepmaximum)")
		fd.append("		if 'RFS_RESULTNAMEMODE' in result.metadata:")
		fd.append("			self.resultnamemode = result.metadata['RFS_RESULTNAMEMODE']")
		fd.append("			self.debugmsg(6, 'resultnamemode: ', self.resultnamemode)")
		fd.append("		self.seedseed()")
		fd.append("")
		fd.append("	def seedseed(self):")
		fd.append("		random.seed()")
		fd.append("		r1 = random.random()%1000")
		fd.append("		random.seed(r1)")
		fd.append("		r2 = random.random()%10000")
		fd.append("		random.seed(r2)")
		fd.append("")
		fd.append("	def log_message(self, message: result.Message):")
		# fd.append("		self.debugmsg(8, 'message[\\'message\\']: ', message['message'])")
		# fd.append("		self.debugmsg(8, 'message[\\'message\\'][0:2]: ', message['message'][0:2])")
		fd.append("		if message.message[0:2] != '${':")
		fd.append("			self.msg = None")
		fd.append("			self.msg = message")
		# fd.append("			self.debugmsg(6, 'message: ', message)")
		# fd.append("			self.debugmsg(6, 'self.msg: ', self.msg)")
		fd.append("")
		fd.append("	def end_keyword(self, data: running.Keyword, result: result.Keyword):")
		fd.append("		self.debugmsg(8, 'data: ', data, data.to_dict())")
		fd.append("		self.debugmsg(8, 'result: ', result, result.to_dict())")
		fd.append("		self.debugmsg(3, 'Keyword name: ', data.name)")
		fd.append("		attrs = result.to_dict()")
		fd.append("		self.debugmsg(6, 'attrs: ', attrs)")
		fd.append("		self.debugmsg(5, 'self.msg: ', self.msg)")
		fd.append("		")
		fd.append("		ResultName = ''")
		# fd.append("		#	'level': 'TRACE'")
		fd.append("		istrace = False")
		fd.append("		if self.msg is not None and self.msg.level == 'TRACE':")
		fd.append("			istrace = True")
		fd.append("		")
		fd.append("		iter = BuiltIn().get_variable_value(\"${RFS_ITERATION}\")")

		# 'dflt': "Default",
		fd.append("		if self.resultnamemode == 'dflt':")
		fd.append("			if self.msg is not None and not istrace:")
		fd.append("				ResultName = self.msg.message")
		fd.append("			elif 'doc' in attrs and len(attrs['doc'])>0:")
		fd.append("				self.debugmsg(5, 'attrs[doc]: ', attrs['doc'])")
		fd.append("				ResultName = attrs['doc']")
		# 'doco': "Documentation",
		fd.append("		if self.resultnamemode == 'doco':")
		fd.append("			if 'doc' in attrs and len(attrs['doc'])>0:")
		fd.append("				self.debugmsg(5, 'attrs[doc]: ', attrs['doc'])")
		fd.append("				ResultName = attrs['doc']")
		# 'info': "Information",
		fd.append("		if self.resultnamemode == 'info':")
		fd.append("			if self.msg is not None:")
		fd.append("				ResultName = self.msg.message")
		# 'kywrd': "Keyword",
		fd.append("		if self.resultnamemode == 'kywrd':")
		fd.append("			ResultName = data.name")
		# "kywrdargs": "Keyword & Arguments"
		fd.append("		if self.resultnamemode == 'kywrdargs':")
		fd.append("			lResultName = [data.name]")
		fd.append("			if 'args' in attrs:")
		fd.append("				for arg in attrs['args']:")
		fd.append("					lResultName.append(arg)")
		fd.append("			ResultName = ' '.join(lResultName)")

		fd.append("		self.debugmsg(3, 'ResultName: ', ResultName, '	:', len(ResultName))")
		fd.append("		")
		fd.append("		if 'owner' not in attrs:")
		fd.append("			attrs['owner'] = 'None'")
		fd.append("		")
		fd.append("		if len(ResultName)>0:")
		fd.append("			self.debugmsg(8, 'self.msg: attrs[owner]: ', attrs['owner'], '	excludelibraries:', self.excludelibraries)")
		fd.append("			if attrs['owner'] not in self.excludelibraries:")
		fd.append("				self.debugmsg(5, attrs['owner'], 'library OK')")
		fd.append("				self.seq += 1")
		fd.append("				self.debugmsg(8, 'self.seq: ', self.seq)")
		fd.append("				self.debugmsg(8, 'elapsed_time: ', attrs['elapsed_time'])")
		fd.append("				self.debugmsg(8, 'start_time: ', attrs['start_time'])")
		fd.append("				startdate = datetime.strptime(attrs['start_time'], '%Y-%m-%dT%H:%M:%S.%f')")
		fd.append("				enddate = datetime.fromtimestamp(startdate.timestamp() + attrs['elapsed_time'])")
		fd.append("				self.debugmsg(8, 'startdate: ', enddate, enddate.timestamp())")
		fd.append("				self.debugmsg(5, 'Send ResultName: ', ResultName)")
		fd.append("				payload = {")
		fd.append("					'AgentName': '" + self.agentname + "',")
		fd.append("					'ResultName': ResultName,")
		fd.append("					'Result': attrs['status'],")
		fd.append("					'ElapsedTime': attrs['elapsed_time'],")
		fd.append("					'StartTime': startdate.timestamp(),")
		fd.append("					'EndTime': enddate.timestamp(),")
		fd.append("					'ScriptIndex': self.index,")
		fd.append("					'Robot': self.robot,")
		fd.append("					'Iteration': iter,")
		fd.append("					'Sequence': self.seq")
		fd.append("				}")
		fd.append("				self.debugmsg(7, 'payload: ', payload)")
		# fd.append("				self.send_result(payload)")
		fd.append("				t = threading.Thread(target=self.send_result, args=(payload,))")
		fd.append("				t.start()")
		fd.append("")
		fd.append("				self.debugmsg(7, 'injectsleep: ', self.injectsleep)")
		fd.append("				if str(self.injectsleep).lower() in ('true', 't', 'yes', '1'):")
		fd.append("					self.debugmsg(8, 'data.to_dict(): ', data.to_dict())")
		fd.append("					if 'lineno' in data.to_dict():")
		fd.append("						tmeslp = self.randsleep(self.sleepminimum, self.sleepmaximum)")
		fd.append("						self.debugmsg(7, 'tmeslp: ', tmeslp)")
		fd.append("						index = data.parent.to_dict()['body'].index(data.to_dict())")
		fd.append("						self.debugmsg(7, 'index: ', index)")
		fd.append("						data.parent.body.insert(index + 1, running.Keyword('Sleep', [tmeslp, 'Sleep added by RFSwarm']))")
		fd.append("")
		fd.append("			else:")
		fd.append("				self.debugmsg(5, attrs['owner'], 'is an excluded library')")
		fd.append("		")
		fd.append("		self.msg = None")
		fd.append("")
		fd.append("	def randsleep(self, min, max):")
		fd.append("		isfloat = False")
		fd.append("		if '.' in str(min) or '.' in str(max):")
		fd.append("			isfloat = True")
		fd.append("		if isfloat:")
		fd.append("			return random.uniform(float(min), float(max))")
		fd.append("		else:")
		fd.append("			return random.randint(int(min), int(max))")
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
		with open(self.listenerfile, 'w+', encoding="utf-8") as lf:
			# lf.writelines(fd)
			lf.write('\n'.join(fd))

	def create_V2_listner_file(self):

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener2.py")
		self.debugmsg(5, "listenerfile", self.listenerfile)

		fd = []
		fd.append("")
		fd.append("import os")
		fd.append("import tempfile")
		fd.append("import sys")
		fd.append("import socket")
		fd.append("from datetime import datetime")
		fd.append("import time")
		fd.append("import random")
		fd.append("import requests")
		fd.append("import inspect")
		fd.append("import threading")
		fd.append("from robot.libraries.BuiltIn import BuiltIn")
		fd.append("")
		fd.append("class RFSListener2:")
		fd.append("	ROBOT_LISTENER_API_VERSION = 2")
		fd.append("")
		fd.append("	msg = None")
		fd.append("	swarmmanager = \"http://localhost:8138/\"")
		fd.append("	excludelibraries = [\"BuiltIn\",\"String\",\"OperatingSystem\",\"perftest\"]")
		fd.append("	resultnamemode = \"dflt\"")
		fd.append("	debuglevel = 0")
		fd.append("	index = 0")
		fd.append("	robot = 0")
		fd.append("	iter = 0")
		fd.append("	seq = 0")
		fd.append("	injectsleep = False")
		fd.append("	sleepminimum = 15")
		fd.append("	sleepmaximum = 45")
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
		fd.append("		if 'RFS_INJECTSLEEP' in attrs['metadata']:")
		fd.append("			self.injectsleep = attrs['metadata']['RFS_INJECTSLEEP']")
		fd.append("			self.debugmsg(6, 'injectsleep: ', self.injectsleep)")
		fd.append("		if 'RFS_SLEEPMINIMUM' in attrs['metadata']:")
		fd.append("			self.sleepminimum = attrs['metadata']['RFS_SLEEPMINIMUM']")
		fd.append("			self.debugmsg(6, 'sleepminimum: ', self.sleepminimum)")
		fd.append("		if 'RFS_SLEEPMAXIMUM' in attrs['metadata']:")
		fd.append("			self.sleepmaximum = attrs['metadata']['RFS_SLEEPMAXIMUM']")
		fd.append("			self.debugmsg(6, 'sleepmaximum: ', self.sleepmaximum)")
		fd.append("		if 'RFS_RESULTNAMEMODE' in attrs['metadata']:")
		fd.append("			self.resultnamemode = attrs['metadata']['RFS_RESULTNAMEMODE']")
		fd.append("			self.debugmsg(6, 'resultnamemode: ', self.resultnamemode)")
		fd.append("		self.seedseed()")
		fd.append("")
		fd.append("	def seedseed(self):")
		fd.append("		random.seed()")
		fd.append("		r1 = random.random()%1000")
		fd.append("		random.seed(r1)")
		fd.append("		r2 = random.random()%10000")
		fd.append("		random.seed(r2)")
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
		fd.append("		self.debugmsg(8, 'attrs: ', attrs)")
		fd.append("		self.debugmsg(5, 'attrs[doc]: ', attrs['doc'])")
		fd.append("		self.debugmsg(5, 'self.msg: ', self.msg)")
		fd.append("		")
		fd.append("		ResultName = ''")
		# fd.append("		#	'level': 'TRACE'")
		fd.append("		istrace = False")
		fd.append("		if self.msg is not None and 'level' in self.msg and self.msg['level'] == 'TRACE':")
		fd.append("			istrace = True")
		fd.append("		")
		fd.append("		iter = BuiltIn().get_variable_value(\"${RFS_ITERATION}\")")

		# 'dflt': "Default",
		fd.append("		if self.resultnamemode == 'dflt':")
		fd.append("			if self.msg is not None and 'message' in self.msg and not istrace:")
		fd.append("				ResultName = self.msg['message']")
		fd.append("			elif 'doc' in attrs and len(attrs['doc'])>0:")
		fd.append("				ResultName = attrs['doc']")
		# 'doco': "Documentation",
		fd.append("		if self.resultnamemode == 'doco':")
		fd.append("			if 'doc' in attrs and len(attrs['doc'])>0:")
		fd.append("				ResultName = attrs['doc']")
		# 'info': "Information",
		fd.append("		if self.resultnamemode == 'info':")
		fd.append("			if self.msg is not None and 'message' in self.msg:")
		fd.append("				ResultName = self.msg['message']")
		# 'kywrd': "Keyword",
		fd.append("		if self.resultnamemode == 'kywrd':")
		# fd.append("			ResultName = name")		# returns library.keyword
		fd.append("			self.debugmsg(8, self.resultnamemode, 'kwname: ', attrs['kwname'])")
		fd.append("			ResultName = attrs['kwname']")
		# "kywrdargs": "Keyword & Arguments"
		fd.append("		if self.resultnamemode == 'kywrdargs':")
		# fd.append("			lResultName = [name]")		# returns library.keyword
		fd.append("			self.debugmsg(8, self.resultnamemode, 'kwname: ', attrs['kwname'])")
		fd.append("			lResultName = [attrs['kwname']]")
		fd.append("			self.debugmsg(3, 'lResultName: ', lResultName)")
		fd.append("			if 'args' in attrs:")
		fd.append("				for arg in attrs['args']:")
		fd.append("					lResultName.append(arg)")
		fd.append("			self.debugmsg(8, 'lResultName: ', lResultName)")
		fd.append("			ResultName = ' '.join(lResultName)")

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
		fd.append("					'Iteration': iter,")
		fd.append("					'Sequence': self.seq")
		fd.append("				}")
		fd.append("				self.debugmsg(7, 'payload: ', payload)")
		# fd.append("				self.send_result(payload)")
		fd.append("				t = threading.Thread(target=self.send_result, args=(payload,))")
		fd.append("				t.start()")
		fd.append("")
		fd.append("				self.debugmsg(7, 'injectsleep: ', self.injectsleep)")
		fd.append("				if str(self.injectsleep).lower() in ('true', 't', 'yes', '1'):")
		fd.append("					tmeslp = self.randsleep(self.sleepminimum, self.sleepmaximum)")
		fd.append("					self.debugmsg(7, 'tmeslp: ', tmeslp)")
		fd.append("					BuiltIn().run_keyword('Sleep', tmeslp, 'Sleep added by RFSwarm')")
		fd.append("")
		fd.append("			else:")
		fd.append("				self.debugmsg(5, attrs['libname'], 'is an excluded library')")
		fd.append("		")
		fd.append("		self.msg = None")
		fd.append("")
		fd.append("	def randsleep(self, min, max):")
		fd.append("		isfloat = False")
		fd.append("		if '.' in str(min) or '.' in str(max):")
		fd.append("			isfloat = True")
		fd.append("		if isfloat:")
		fd.append("			return random.uniform(float(min), float(max))")
		fd.append("		else:")
		fd.append("			return random.randint(int(min), int(max))")
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
		with open(self.listenerfile, 'w+', encoding="utf-8") as lf:
			# lf.writelines(fd)
			lf.write('\n'.join(fd))

	def create_repeater_listner_file(self):
		self.repeaterfile = os.path.join(self.scriptdir, "RFSTestRepeater.py")

		fd = []
		fd.append("")
		fd.append("from robot.libraries.BuiltIn import BuiltIn")
		fd.append("")
		fd.append("import time")
		fd.append("import os")
		fd.append("import json")
		fd.append("")
		fd.append("class RFSTestRepeater:")
		fd.append("	ROBOT_LISTENER_API_VERSION = 3")
		fd.append("")
		fd.append("	testname = None")
		fd.append("	count = 0")
		fd.append("")
		fd.append("	def end_test(self, test, result):")
		fd.append("")
		fd.append("		jobdata = {}")
		fd.append("		index = test.parent.metadata['RFS_INDEX']")
		fd.append("		robot = test.parent.metadata['RFS_ROBOT']")
		fd.append("		scriptdir = os.path.dirname(__file__)")
		fd.append("		jobfile = os.path.join(scriptdir, \"RFS_Job_{}_{}.json\".format(index, robot))")
		fd.append("")
		fd.append("		if os.path.exists(jobfile):")
		fd.append("			with open(jobfile, 'r') as f:")
		fd.append("				jobdata = json.load(f)")
		fd.append("")
		fd.append("		self.count += 1")
		fd.append("		newiteration = \"{}_{}\".format(test.parent.metadata['RFS_ITERATION'], self.count)")
		fd.append("		BuiltIn().set_suite_variable(\"${RFS_ITERATION}\", newiteration)")
		fd.append("")
		fd.append("		if int(time.time()) < jobdata[\"EndTime\"]:")
		fd.append("			if self.testname is None:")
		fd.append("				self.testname = test.name")
		fd.append("			newname = \"{} {}\".format(self.testname, newiteration)")
		fd.append("			copy = test.copy(name=newname)")
		fd.append("			test.parent.tests.append(copy)")
		fd.append("")

		rfver = self.agentproperties["RobotFramework"]
		if int(rfver[0]) >= 7:
			fd.append("	def start_keyword(self, data, result):")
			fd.append("		# This prevents the error:")
			fd.append("		# [ ERROR ] Calling method 'start_keyword' of listener 'TestRepeater.py' failed: TypeError: end_suite() takes 2 positional arguments but 3 were given")
			fd.append("		pass")
			fd.append("")
			fd.append("	def end_keyword(self, data, result):")
			fd.append("		# This prevents the error:")
			fd.append("		# [ ERROR ] Calling method 'end_keyword' of listener 'TestRepeater.py' failed: TypeError: end_suite() takes 2 positional arguments but 3 were given")
			fd.append("		pass")
			fd.append("")

		# print("RFSwarmAgent: create_listner_file: listenerfile: ", self.listenerfile)
		with open(self.repeaterfile, 'w+', encoding="utf-8") as lf:
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
			# self.debugmsg(3, "Join Agent Manager Thread")
			# self.Agentserver.join()

			self.debugmsg(3, "Join Agent Thread:", jobid)
			self.jobs[jobid]["Thread"].join()

		time.sleep(1)
		self.debugmsg(2, "Exit")
		try:
			sys.exit(0)
		except SystemExit as e:
			try:
				remaining_threads = [t for t in threading.enumerate() if t is not threading.main_thread() and t.is_alive()]
				if remaining_threads:
					self.debugmsg(5, "Failed to gracefully exit RFSwarm-Agent. Forcing immediate exit.")
					for thread in remaining_threads:
						self.debugmsg(9, "Thread name:", thread.name)
					os._exit(0)
				else:
					raise e

			except Exception as e:
				self.debugmsg(3, "Failed to exit with error:", e)
				os._exit(1)


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
