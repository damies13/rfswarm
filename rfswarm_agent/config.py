import os
import socket
import tempfile
from argparse import Namespace

from rfswarm_common.debug import debug


class AgentConfig:
	@staticmethod
	def read_agent_default_config() -> dict:
		"""
		STAGE 1: Returns the default configuration for the agent as a dictionary.
		"""
		default_config = {
			"Agent": {
				"agentname": socket.gethostname(),
				"agentdir": os.path.join(tempfile.gettempdir(), "rfswarmagent"),
				# deprecate xml mode fully
				"excludelibraries": "BuiltIn,String,OperatingSystem,perftest",
				"properties": "",
				"swarmmanager": "http://localhost:8138/",
				"robotcmd": "robot"
			},
		}
		return default_config

	@staticmethod
	def read_agent_args_config(args: Namespace) -> dict:
		"""
		STAGE 3: Reads configuration from command-line arguments and return a dictionary.
		"""
		args_config = {
			"Agent": {}
		}

		if getattr(args, "agentname", None):
			debug.debugmsg(1, "args.agentname: ", args.agentname)
			args_config["Agent"]["agentname"] = args.agentname

		if getattr(args, "agentdir", None):
			debug.debugmsg(1, "args.agentdir: ", args.agentdir)
			args_config['Agent']['agentdir'] = args.agentdir

		if getattr(args, "manager", None):
			debug.debugmsg(1, "args.manager: ", args.manager)
			if args.manager[-1] != '/':
				args_config['Agent']['swarmmanager'] = f"{args.manager}/"
			else:
				args_config['Agent']['swarmmanager'] = args.manager

		if getattr(args, "robot", None):
			debug.debugmsg(1, "args.robot: ", args.robot)
			args_config['Agent']['robotcmd'] = args.robot

		return args_config
