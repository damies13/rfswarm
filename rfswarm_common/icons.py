import importlib.metadata
import os
import platform
import shutil
import sys

from rfswarm_common.debug import debug
from rfswarm_common.filestransfers import FilesTransfers


class IconManager:
	@classmethod
	def create_icons(cls, appname, srcdir):
		"""
		Creates application icons for the specified appname in the appropriate locations based on the operating system.
		:param appname: The name of the application for which to create icons.
		:param srcdir: The source directory where the icon files are located.
		"""
		debug.debugmsg(0, f"Creating application icons for {appname}")
		namelst = appname.split()
		debug.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		version = "dev"
		try:
			pipdata = importlib.metadata.distribution(projname)
			version = pipdata.version
		except Exception as e:
			debug.debugmsg(1, f"Package metadata for {projname} not found ({e})")

		executable = shutil.which(projname)
		if not executable:
			bin_dir = "Scripts" if platform.system() == "Windows" else "bin"
			candidate = os.path.join(sys.prefix, bin_dir, projname)
			if os.path.isfile(candidate):
				executable = os.path.abspath(candidate)
			else:
				executable = sys.executable

		debug.debugmsg(5, "executable:", executable)

		if os.path.isdir(os.path.join(srcdir, "icons")):
			icon_dir = os.path.join(srcdir, "icons")
		else:
			icon_dir = srcdir
		debug.debugmsg(5, "icon_dir:", icon_dir)

		if platform.system() == 'Linux':
			fileprefix = "~/.local/share"
			if os.access("/usr/share", os.W_OK):
				fileprefix = "/usr/share"

			fileprefix = os.path.expanduser(fileprefix)

			cls.create_linux_desktop_files(appname, projname, executable, icon_dir, fileprefix)

		if platform.system() == 'Darwin':
			debug.debugmsg(5, "Create folder structure in /Applications")
			src_iconx1024 = os.path.join(icon_dir, projname + "-1024.png")

			cls.create_macos_app_bundle(appname, version, executable, src_iconx1024)

		if platform.system() == 'Windows':
			debug.debugmsg(5, "Create Startmenu shorcuts")
			roam_appdata = os.environ["APPDATA"]
			scutpath = os.path.join(roam_appdata, "Microsoft", "Windows", "Start Menu", appname + ".lnk")
			src_iconx128 = os.path.join(icon_dir, projname + "-128.ico")

			if "agent" in projname:
				desc = "Connects to Manager and runs robots"
				minimised = True
			elif "reporter" in projname:
				desc = "Performance testing with robot test cases"
				minimised = False
			else:
				desc = "Runs Manager for Robot Framework Swarm"
				minimised = False

			cls.create_windows_shortcut(scutpath, executable, src_iconx128, desc, minimised)

	@classmethod
	def create_windows_shortcut(cls, scutpath, targetpath, iconpath, desc, minimised=False):
		pslst = []

		directorydir = os.path.dirname(scutpath)
		FilesTransfers.ensuredir(directorydir)

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

	@classmethod
	def create_macos_app_bundle(cls, name, version, exesrc, icosrc, is_gui=None):

		appspath = "~/Applications"
		if os.access("/Applications", os.W_OK):
			appspath = "/Applications"

		appspath = os.path.expanduser(appspath)

		# https://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

		apppath = os.path.join(appspath, name + ".app")
		MacOSFolder = os.path.join(apppath, "Contents", "MacOS")
		FilesTransfers.ensuredir(MacOSFolder)

		# need to create the icon file:
		# https://stackoverflow.com/questions/646671/how-do-i-set-the-icon-for-my-applications-mac-os-x-app-bundle
		namelst = name.split()
		debug.debugmsg(6, "namelst:", namelst)
		projname = "-".join(namelst).lower()
		debug.debugmsg(6, "projname:", projname)
		signature = "RFS{0}".format(namelst[1].upper())
		debug.debugmsg(6, "signature:", signature)

		if is_gui is None:
			is_gui = "agent" not in projname

		ResourcesFolder = os.path.join(apppath, "Contents", "Resources")
		iconset = os.path.join(ResourcesFolder, projname + ".iconset")
		icnsfile = os.path.join(ResourcesFolder, projname + ".icns")
		FilesTransfers.ensuredir(iconset)

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
			if is_gui:
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
			else:
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
				<key>LSUIElement</key>
				<true/>
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
		if os.path.islink(execbundle) or os.path.lexists(execbundle):
			os.remove(execbundle)
		elif os.path.exists(execbundle):
			if os.path.isdir(execbundle):
				shutil.rmtree(execbundle)
			else:
				os.remove(execbundle)
		os.symlink(exesrc, execbundle)

		# touch apppath to update .app icon
		cmd = "touch '{0}'".format(apppath)
		debug.debugmsg(6, "cmd:", cmd)
		response = os.popen(cmd).read()
		debug.debugmsg(6, "response:", response)

		# Try re-registering application with Launch Services:
		lsregister = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
		if os.path.exists(lsregister):
			cmd = '"{0}" -f "{1}"'.format(lsregister, apppath)
			debug.debugmsg(6, "cmd:", cmd)
			response = os.popen(cmd).read()
			debug.debugmsg(6, "response:", response)

	@classmethod
	def create_linux_desktop_files(cls, appname, projname, executable, icon_dir, fileprefix):
		debug.debugmsg(5, "Create .directory file")
		directorydata = []
		directorydata.append('[Desktop Entry]\n')
		directorydata.append('Type=Directory\n')
		directorydata.append('Name=RFSwarm\n')
		directorydata.append('Icon=rfswarm-logo\n')

		directoryfilename = os.path.join(fileprefix, "desktop-directories", "rfswarm.directory")
		directorydir = os.path.dirname(directoryfilename)
		FilesTransfers.ensuredir(directorydir)

		debug.debugmsg(5, "directoryfilename:", directoryfilename)
		with open(directoryfilename, 'w') as df:
			df.writelines(directorydata)

		directoryfilename = os.path.join(fileprefix, "applications", "rfswarm.directory")
		directorydir = os.path.dirname(directoryfilename)
		FilesTransfers.ensuredir(directorydir)
		debug.debugmsg(5, "directoryfilename:", directoryfilename)
		with open(directoryfilename, 'w') as df:
			df.writelines(directorydata)

		debug.debugmsg(5, "Create .desktop file")
		desktopdata = []
		desktopdata.append('[Desktop Entry]\n')
		desktopdata.append('Name=' + appname + '\n')
		desktopdata.append('Exec=' + executable + '\n')
		is_gui = "agent" not in projname
		desktopdata.append(f'Terminal={"false" if is_gui else "true"}\n')
		desktopdata.append('Type=Application\n')
		desktopdata.append('Icon=' + projname + '\n')
		desktopdata.append('Categories=RFSwarm;Development;\n')
		category = "agent" if "agent" in projname else ("reporter" if "reporter" in projname else "manager")
		desktopdata.append(f'Keywords=rfswarm;{category};\n')
		# desktopdata.append('\n')

		desktopfilename = os.path.join(fileprefix, "applications", projname + ".desktop")
		desktopdir = os.path.dirname(desktopfilename)
		FilesTransfers.ensuredir(desktopdir)

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
		FilesTransfers.ensuredir(dst_icondir)
		debug.debugmsg(5, "dst_iconx128:", dst_iconx128)
		shutil.copy(src_iconx128, dst_iconx128)

		src_iconx128 = os.path.join(icon_dir, "rfswarm-logo-128.png")
		debug.debugmsg(5, "src_iconx128:", src_iconx128)
		dst_iconx128 = os.path.join(fileprefix, "icons", "hicolor", "128x128", "apps", "rfswarm-logo.png")
		debug.debugmsg(5, "dst_iconx128:", dst_iconx128)
		shutil.copy(src_iconx128, dst_iconx128)

	@classmethod
	def check_icons(cls, appname):
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
