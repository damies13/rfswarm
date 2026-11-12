import os
import shutil
import sys

from rfswarm_common.config import config
from rfswarm_common.debug import debug


class AgentListeners:
	def __init__(self, scriptdir: str) -> None:
		self.scriptdir = scriptdir
		self.listenerfile: str = ""
		self.repeaterfile: str = ""

	def ensure_listener_file(self, agentproperties: dict) -> None:
		if not self.listenerfile:
			self.create_listener_file(agentproperties)
		else:
			if not os.path.isfile(self.listenerfile):
				self.create_listener_file(agentproperties)

	def ensure_repeater_listener_file(self) -> None:
		if not self.repeaterfile:
			self.create_repeater_listener_file()

	def create_listener_file(self, agentproperties: dict) -> None:
		rfver = agentproperties["RobotFramework"]
		debug.debugmsg(5, "RobotFramework version:", rfver, " RobotFramework major version:", int(rfver[0]))
		if int(rfver[0]) >= 7:
			self.create_V3_listener_file()
		else:
			self.create_V2_listener_file()

	def create_V3_listener_file(self) -> None:

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener3.py")
		debug.debugmsg(5, "listenerfile", self.listenerfile)

		if config.srcdir is None:
			debug.debugmsg(0, "config.srcdir is None")
			sys.exit(1)
		listenersrc = os.path.join(config.srcdir, "resources", "RFSListener3.py")
		debug.debugmsg(5, "listenersrc", listenersrc)
		shutil.copy(listenersrc, self.listenerfile)

	def create_V2_listener_file(self) -> None:

		self.listenerfile = os.path.join(self.scriptdir, "RFSListener2.py")
		debug.debugmsg(5, "listenerfile", self.listenerfile)

		if config.srcdir is None:
			debug.debugmsg(0, "config.srcdir is None")
			sys.exit(1)
		listenersrc = os.path.join(config.srcdir, "resources", "RFSListener2.py")
		debug.debugmsg(5, "listenersrc", listenersrc)
		shutil.copy(listenersrc, self.listenerfile)

	def create_repeater_listener_file(self) -> None:
		self.repeaterfile = os.path.join(self.scriptdir, "RFSTestRepeater.py")
		debug.debugmsg(5, "repeaterfile", self.repeaterfile)

		if config.srcdir is None:
			debug.debugmsg(0, "config.srcdir is None")
			sys.exit(1)
		repeatersrc = os.path.join(config.srcdir, "resources", "RFSTestRepeater.py")
		debug.debugmsg(5, "repeatersrc", repeatersrc)
		shutil.copy(repeatersrc, self.repeaterfile)
