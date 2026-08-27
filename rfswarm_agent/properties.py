import platform
import importlib.metadata
from rfswarm_common.debug import debug
from rfswarm_common.config import config


def higher_version(versiona, versionb):
	lversiona = [int(v) for v in versiona.split(".")]
	lversionb = [int(v) for v in versionb.split(".")]
	for i in range(max(len(lversiona), len(lversionb))):
		v1 = lversiona[i] if i < len(lversiona) else 0
		v2 = lversionb[i] if i < len(lversionb) else 0
		if v1 > v2:
			return versiona
		elif v1 < v2:
			return versionb
	return versiona


def findlibraries(agentproperties: dict):
	"""
	Finds installed Robot Framework libraries and their versions, and updates the agent properties accordingly.
	- post python 3.8 method
	- This method works for python 3.8 and higher
	"""

	found = 0
	liblst = []

	installed_packages = importlib.metadata.distributions()
	for i in installed_packages:
		# if "robot" in i.metadata["Name"]:
		# print(dist.metadata["Name"], dist.version)
		if i.metadata["Name"].strip() == "robotframework":
			found = 1
			if "RobotFramework" in agentproperties:
				ver = higher_version(i.version, agentproperties["RobotFramework"])
				agentproperties["RobotFramework"] = ver
				debug.debugmsg(6, i.metadata["Name"].strip(), i.version, "-->", ver)
			else:
				agentproperties["RobotFramework"] = i.version
				debug.debugmsg(6, i.metadata["Name"].strip(), i.version)
		if i.metadata["Name"].startswith("robotframework-"):
			# print(i.key)
			keyarr = i.metadata["Name"].strip().split("-")
			debug.debugmsg(7, keyarr, i.version)
			#  next overwrites previous
			if "RobotFramework: Library: " + keyarr[1] in agentproperties:
				ver = higher_version(i.version, agentproperties["RobotFramework: Library: " + keyarr[1]])
				agentproperties["RobotFramework: Library: " + keyarr[1]] = ver
			else:
				agentproperties["RobotFramework: Library: " + keyarr[1]] = i.version
			liblst.append(keyarr[1])

	debug.debugmsg(8, "liblst:", liblst, len(liblst))
	if len(liblst) > 0:
		debug.debugmsg(7, "liblst:", ", ".join(liblst))
		agentproperties["RobotFramework: Libraries"] = ", ".join(liblst)

	if not found:
		debug.debugmsg(0, "RobotFramework is not installed!!!")
		debug.debugmsg(0, "RobotFramework is required for the agent to run scripts")
		debug.debugmsg(0, "Perhaps try: 'pip install robotframework'")
		raise Exception("RobotFramework is not installed")

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

	findlibraries(properties) 	# Need to wait for findlibraries() to finish before calling ensure_listner_file() for RF version check

	debug.debugmsg(9, "properties: ", properties)

	return properties
