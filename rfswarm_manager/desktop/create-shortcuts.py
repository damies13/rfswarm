#

import os
import platform


def main():
	print("Create shortcuts for RFSwarm Manager")
	print("platform:", platform.system())
	if platform.system() == 'Linux':
		print("Create .desktop file")

		print("Copy icons")
	if platform.system() == 'Darwin':
		print("Create folder structure in /Applications")

	if platform.system() == 'Windows':
		print("Create Startmenu shorcuts")
