#

# import importlib
import importlib.metadata
import os
import platform
import shutil

def main():
	print("Create shortcuts for RFSwarm Manager")
	print("platform:", platform.system())
	pipdata = importlib.metadata.distribution('rfswarm-manager')
	# print("files:", pipdata.files)
	# print("file0:", pipdata.files[0])
	manager_executable = os.path.abspath(str(pipdata.locate_file(pipdata.files[0])))
	print("manager_executable:", manager_executable)

	script_dir = os.path.dirname(os.path.abspath(__file__))
	print("script_dir:", script_dir)

	# pipdata = importlib.metadata.distribution('rfswarm-agent')
	# print("files:", pipdata.files)
	# print("file0:", pipdata.files[0])
	# agent_executable = os.path.abspath(str(pipdata.locate_file(pipdata.files[0])))
	# print("agent_executable:", agent_executable)

	if platform.system() == 'Linux':
		# https://forums.linuxmint.com/viewtopic.php?p=2269391#p2269391

		# ~~~ cat ~/.local/share/desktop-directories/file.directory ~~~
		# [Desktop Entry]
		# Type=Directory
		# Name=Electronics
		# Icon=applications-electronics
		# ~~~ end cat ~~~

		# ~~~ cat ~/.local/share/applications/test.desktop ~~~
		# [Desktop Entry]
		# Name=Test
		# Comment=New item should be in electronics directory
		# Type=Application
		# Exec=/path/to/my/app
		# Icon=/path/to/my/app.png
		# Categories=Electronics
		# Keywords=electronics;
		# ~~~ end cat ~~~

		print("Create .directory file")
		directorydata = []
		directorydata.append('[Desktop Entry]\n')
		directorydata.append('Type=Directory\n')
		directorydata.append('Name=RFSwarm\n')
		directorydata.append('Icon=rfswarm\n')

		try:
			directoryfilename = os.path.join(os.path.expanduser("~/.local/share/desktop-directories"), "rfswarm.desktop")
			directorydir = os.path.dirname(directoryfilename)
			if not os.path.exists(directorydir):
				os.mkdir(directorydir)

			print("directoryfilename:", directoryfilename)
			with open(directoryfilename, 'w') as df:
				df.writelines(directorydata)
		except:
			pass

		print("Create .desktop file")
		desktopdata = []
		desktopdata.append('[Desktop Entry]\n')
		desktopdata.append('Name=RFSwarm Manager\n')
		desktopdata.append('Exec=' + manager_executable + '\n')
		desktopdata.append('Terminal=false\n')
		desktopdata.append('Type=Application\n')
		desktopdata.append('Icon=rfswarm-manager\n')
		desktopdata.append('Categories=RFSwarm\n')
		desktopdata.append('Keywords=rfswarm;\n')
		# desktopdata.append('Icon=rfswarm-manager.png\n')
		# desktopdata.append('\n')

		# /usr/share/applications/
		# or
		# ~/.local/share/applications
		# dektopfilename = os.path.join(os.path.abspath("~/.local/share/applications"), "rfswarm-manager.desktop")
		dektopfilename = os.path.join(os.path.expanduser("~/.local/share/applications"), "rfswarm-manager.desktop")

		print("dektopfilename:", dektopfilename)
		with open(dektopfilename, 'w') as df:
			df.writelines(desktopdata)

		print("Copy icons")
		# /usr/share/icons/hicolor/128x128/apps/
		# 	1024x1024  128x128  16x16  192x192  22x22  24x24  256x256  32x32  36x36  42x42  48x48  512x512  64x64  72x72  8x8  96x96
		# or
		#  ~/.local/share/icons/hicolor/256x256/apps/
		src_iconx128 = os.path.join(script_dir, "rfswarm-manager-128.png")
		print("src_iconx128:", src_iconx128)

		# dst_iconx128 = os.path.join(os.path.abspath("~/.local/share/icons/hicolor/128x128/apps"), "rfswarm-manager.png")
		dst_iconx128 = os.path.join(os.path.expanduser("~/.local/share/icons/hicolor/128x128/apps"), "rfswarm-manager.png")
		print("dst_iconx128:", dst_iconx128)
		shutil.copy(src_iconx128, dst_iconx128)

		src_iconx128 = os.path.join(script_dir, "rfswarm-logo-128.png")
		print("src_iconx128:", src_iconx128)

		dst_iconx128 = os.path.join(os.path.expanduser("~/.local/share/icons/hicolor/128x128/apps"), "rfswarm-logo.png")
		print("dst_iconx128:", dst_iconx128)
		shutil.copy(src_iconx128, dst_iconx128)


	if platform.system() == 'Darwin':
		print("Create folder structure in /Applications")

	if platform.system() == 'Windows':
		print("Create Startmenu shorcuts")


if __name__ == '__main__':
	main()
