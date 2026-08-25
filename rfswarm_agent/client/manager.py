import requests
from datetime import datetime
import time
from typing import Optional

from rfswarm_common.debug import debug
from rfswarm_common.config import config


class ManagerClient:
	"""
	Client class for managing communication with the Robot Framework Swarm Manager.
	"""
	def __init__(self):
		self.isconnected: bool = False

	@property
	def swarmmanager(self) -> str:
		mgr = "http://localhost:8138/"
		if 'Agent' in config.data and 'swarmmanager' in config.data['Agent']:
			mgr = config.data['Agent']['swarmmanager']
		if not mgr.endswith('/'):
			mgr += '/'
		return mgr

	def connectmanager(self, timeout: int = 600) -> bool:
		debug.debugmsg(6, "connectmanager")
		uri = self.swarmmanager
		if uri:
			debug.debugmsg(2, "Try connecting to", uri)
			debug.debugmsg(6, "self.swarmmanager:", uri)
			try:
				r = requests.get(uri, timeout=timeout)
				debug.debugmsg(8, r.status_code, r.text)
				if r.status_code == requests.codes.ok:
					debug.debugmsg(7, "r.status_code:", r.status_code, requests.codes.ok, r.text)
					self.isconnected = True
					debug.debugmsg(0, "Manager Connected", uri, datetime.now().isoformat(sep=' ', timespec='seconds'), "(", int(time.time()), ")")
				else:
					self.isconnected = False
			except Exception as e:
				debug.debugmsg(7, "connectmanager exception:", e)
				self.isconnected = False

		return self.isconnected
