"""Module providing a function that returns the
ipv4 and ipv6 addresses of the device interfaces."""

import psutil


def get_ip_addresses():
	"""Return lists containing ipv4 and ipv6 addreses."""
	ipv4addresslist = []
	ipv6addresslist = []
	iflst = psutil.net_if_addrs()
	for nic in iflst.keys():
		for addr in iflst[nic]:
			if addr.address not in ['127.0.0.1', '::1', 'fe80::1%lo0']:
				if "." in list(addr.address):
					ipv4addresslist.append(addr.address)
				elif ":" in list(addr.address):
					ipv6addresslist.append(addr.address)

	return ipv4addresslist, ipv6addresslist
