import threading
import time
import psutil

from rfswarm_common import debug


class SystemTelemetry:
	"""Collects host machine system telemetry and network metrics for rfswarm agent."""

	def __init__(self) -> None:
		self.ipaddresslist: list[str] = []
		self.netpct: float = 0.0
		self._ip_thread: threading.Thread | None = None
		self._net_thread: threading.Thread | None = None

	def start_background_updates(self) -> None:
		"""Start background threads only if updates are needed or previous run finished."""
		if self._ip_thread is None or not self._ip_thread.is_alive():
			self._ip_thread = threading.Thread(target=self.update_ip_addresses, name="telemetry_ips", daemon=True)
			self._ip_thread.start()

		if self._net_thread is None or not self._net_thread.is_alive():
			self._net_thread = threading.Thread(target=self.update_net_percent, name="telemetry_net", daemon=True)
			self._net_thread.start()

	def update_ip_addresses(self) -> None:
		"""Discover and cache non-loopback IP addresses of the local host."""
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

	def update_net_percent(self) -> None:
		"""Calculate network utilization percentage over a 1-second sample window."""
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

	@staticmethod
	def get_cpu_percent() -> float:
		"""Return current system-wide CPU utilization percentage."""
		return psutil.cpu_percent()

	@staticmethod
	def get_mem_percent() -> float:
		"""Return current system virtual memory utilization percentage."""
		return float(dict(psutil.virtual_memory()._asdict())["percent"])
