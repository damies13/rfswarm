import psutil


def get_ip_addresses():
	ipaddresslist = []
	iflst = psutil.net_if_addrs()
	for nic in iflst.keys():
		for addr in iflst[nic]:
			if addr.address not in ['127.0.0.1', '::1', 'fe80::1%lo0']:
				ipaddresslist.append(addr.address)

	return ipaddresslist