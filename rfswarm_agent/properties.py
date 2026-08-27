import platform

from rfswarm_common.debug import debug
from rfswarm_common.config import config


def collect_agent_properties(args, version: str):
	"""
	Collects properties of the agent and returns them as a dictionary.
	"""
	properties = dict()
	
	properties["RFSwarmAgent: Version"] = version

	properties["OS: Platform"] = platform.platform()  # 'Linux-3.3.0-8.fc16.x86_64-x86_64-with-fedora-16-Verne'
	properties["OS: System"] = platform.system()  # 'Windows'		Returns the system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'
	properties["OS: Release"] = platform.release()  # 'XP'
	properties["OS: Version"] = platform.version()  # '5.1.2600'

	if platform.system() == 'Windows':
		vararr = platform.version().split(".")
	else:
		vararr = platform.release().split(".")

	if len(vararr) > 0:
		properties["OS: Version: Major"] = "{}".format(int(vararr[0]))
	if len(vararr) > 1:
		properties["OS: Version: Minor"] = "{}.{}".format(int(vararr[0]), int(vararr[1]))

	if 'properties' in config.data['Agent'] and len(config.data['Agent']['properties']) > 0:
		if "," in config.data['Agent']['properties']:
			proplist = config.data['Agent']['properties'].split(",")
			for prop in proplist:
				properties["{}".format(prop.strip())] = True
		else:
			properties["{}".format(config.data['Agent']['properties'].strip())] = True

	if args and hasattr(args, "property") and args.property:
		debug.debugmsg(7, "args.property: ", args.property)
		for prop in args.property:
			properties["{}".format(prop.strip())] = True

	debug.debugmsg(9, "properties: ", properties)

	return properties
