#

import os
import platform


def main():
	print("Create shortcuts for RFSwarm Manager")
	print("platform:", platform.system())
	if platform.system() == 'Linux':
		print("Create .desktop file")
		# /usr/share/applications/
		# or
		# ~/.local/share/applications

		print("Copy icons")
		# /usr/share/icons/hicolor/128x128/apps/
		# 	1024x1024  128x128  16x16  192x192  22x22  24x24  256x256  32x32  36x36  42x42  48x48  512x512  64x64  72x72  8x8  96x96
		# or
		#  ~/.local/share/icons/hicolor/256x256/apps/


	if platform.system() == 'Darwin':
		print("Create folder structure in /Applications")

	if platform.system() == 'Windows':
		print("Create Startmenu shorcuts")


if __name__ == '__main__':
	main()
