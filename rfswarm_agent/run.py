import sys
import os
import tempfile
from argparse import Namespace

from rfswarm_agent.rfswarm_agent import RFSwarmAgent
from rfswarm_common.__version__ import __version__
from rfswarm_common.debug import debug
from rfswarm_common.config import config
from rfswarm_agent.properties import collect_agent_properties


def define_srcdir() -> str:
	srcdir = os.path.join(os.path.dirname(__file__))
	if srcdir[-2:] == "/.":
		debug.debugmsg(7, "srcdir[-2]: ", srcdir[-2:])
		srcdir = srcdir[0:-2]
	debug.debugmsg(7, "srcdir: ", srcdir)
	return srcdir

def show_additional_versions(properties: dict) -> None:

	debug.debugmsg(0, "\tDependancy Versions")
	try:
		debug.debugmsg(0, "\t\tPython Version", sys.version)
	except Exception:
		pass

	try:
		debug.debugmsg(0, "\t\tRobotFramework:", properties["RobotFramework"])
		liblist = properties["RobotFramework: Libraries"].split(", ")
		for lib in liblist:
			debug.debugmsg(0, "\t\tRobotFramework Library: " + lib, properties["RobotFramework: Library: " + lib])
	except Exception:
		pass

def run_agent(args: Namespace) -> None:
	if args.debug:
		debug.debuglvl = int(args.debug)

	debug.debugmsg(0, "Robot Framework Swarm: Run Agent")
	debug.debugmsg(0, "\tVersion", __version__)
	debug.debugmsg(6, "args:", args)
	debug.debugmsg(6, "gettempdir", tempfile.gettempdir())
	debug.debugmsg(6, "tempdir", tempfile.tempdir)

	srcdir = define_srcdir()

	config.initialize()
	default_config = config.read_agent_default_config()
	config.load_config(default_config)

	inipath = config.findinilocation(args, srcdir, inifilename="RFSwarmAgent.ini")
	ini_dict = config.read_file_config(ini_file=inipath)
	config.update_config(ini_dict)
	config.saveini()

	args_dict = config.read_agent_args_config(args)
	config.update_config(args_dict)

	if hasattr(args, "version") and args.version:
		properties = collect_agent_properties(args, __version__)
		show_additional_versions(properties)
		exit()

	debug.debugmsg(0, "\tConfiguration File: ", config.ini_file)
	debug.debugmsg(5, "config.data: ", config.data)

	rfsa = RFSwarmAgent(args)
	try:
		rfsa.mainloop()
	except KeyboardInterrupt:
		rfsa.on_closing()
	except Exception as e:
		debug.debugmsg(1, "rfsa.Exception:", e)
