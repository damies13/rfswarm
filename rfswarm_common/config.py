import configparser
import json
import os
import sys
import socket
import tempfile
import yaml
import multiprocessing
from typing import Any
from argparse import Namespace

from rfswarm_common.debug import debug


class Config:
	"""
	Class to handle configuration for RFSwarm components (Agent, Manager, Reporter).
	"""

	def __init__(self):
		self.inifilename: str | None = None
		self.srcdir: str | None = None
		self.ini_file: str | None = None
		self.save_ini: bool = True

		self._mp_manager: Any = None
		self._data: Any = None

	def initialize(self) -> None:
		"""Initializes the multiprocessing manager and data structure if not already initialized."""
		if self._mp_manager is None:
			self._mp_manager = multiprocessing.Manager()
		if self._data is None:
			self._data = self._mp_manager.dict()

	@property
	def data(self) -> Any:
		if self._data is None:
			self.initialize()
		return self._data

	def _to_mp_dict(self, data: dict) -> dict:
		"""Converts a dict to a multiprocessing dict, handling nested dictionaries."""
		if self._mp_manager is None:
			self.initialize()
		mp_d = self._mp_manager.dict()
		for k, v in data.items():
			if isinstance(v, dict):
				mp_d[k] = self._to_mp_dict(v)
			else:
				mp_d[k] = v
		return mp_d

	def _deep_update(self, target: dict, source: dict) -> None:
		"""Recursively updates the target dictionary with values from the source dictionary."""
		if self._mp_manager is None:
			self.initialize()
		for key, value in source.items():
			if isinstance(value, dict):
				if key not in target or not hasattr(target[key], "items"):
					target[key] = self._mp_manager.dict()
				self._deep_update(target[key], value)
			else:
				if key not in target or target[key] != value:
					target[key] = value

	def to_dict(self) -> dict:
		"""Recursively converts self.data (multiprocessing DictProxy) to a standard dict."""
		def _convert(data: Any) -> Any:
			if hasattr(data, "items"):
				return {k: _convert(v) for k, v in data.items()}
			return data

		return _convert(self.data)

	def load_config(self, config: dict) -> None:
		"""Loads self.data with the given configuration dictionary, converting nested dictionaries to multiprocessing dicts."""
		self.initialize()
		self.data.clear()
		for k, v in config.items():
			if isinstance(v, dict):
				self.data[k] = self._to_mp_dict(v)
			else:
				self.data[k] = v

	def update_config(self, config: dict) -> None:
		"""Updates self.data with the given configuration dictionary, merging it with existing data."""
		self.initialize()
		self._deep_update(self.data, config)

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
	def read_manager_default_config() -> dict:
		return {}

	@staticmethod
	def read_reporter_default_config() -> dict:
		return {}

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

	@staticmethod
	def read_manager_args_config(args: Namespace) -> dict:
		return {}

	@staticmethod
	def read_reporter_args_config(args: Namespace) -> dict:
		return {}

	def read_file_config(self, ini_file: str, srcdir: str | None = None) -> dict:
		"""
		STAGE 2: Finds and loads configuration from .ini, .yaml, or .json file into self.data.
		"""
		if not ini_file:
			debug.debugmsg(0, "Configuration file not specified or could not be determined. Using default config.")
			return {}
		self.inifilename = os.path.basename(ini_file)
		self.srcdir = srcdir or self.srcdir or ""
		self.ini_file = ini_file

		config_dict: dict = {} 
		if self.ini_file and os.path.isfile(self.ini_file):
			debug.debugmsg(5, "Loading configuration file: ", self.ini_file)
			ext = os.path.splitext(self.ini_file)[1].lower()

			loaders = {
				".ini": self._read_ini,
				".yml": self._read_yaml,
				".yaml": self._read_yaml,
				".json": self._read_json,
			}

			if ext in loaders:
				config_dict = loaders[ext](self.ini_file)
			else:
				debug.debugmsg(0, "Configuration file ", self.ini_file, " has an invalid extension, unable to determine supported format. Please use extensions .ini, .yaml or .json")
				sys.exit()
		else:
			self.saveini()
			debug.debugmsg(5, "Configuration file does not exist yet; will be created on save:", self.ini_file)

		if len(config_dict.keys()) == 0:
			debug.debugmsg(1, "Configuration file is empty or could not be loaded.")
		return config_dict

	@staticmethod
	def _read_ini(filepath: str) -> dict:
		debug.debugmsg(5, "read ini file")
		parser = configparser.ConfigParser()
		parser.read(filepath, encoding="utf-8")
		return {section: dict(parser[section]) for section in parser.sections()}

	@staticmethod
	def _read_yaml(filepath: str) -> dict:
		debug.debugmsg(5, "read yaml file")
		with open(filepath, "r", encoding="utf-8") as f:
			return yaml.safe_load(f) or {}

	@staticmethod
	def _read_json(filepath: str) -> dict:
		debug.debugmsg(5, "read json file")
		with open(filepath, "r", encoding="utf-8") as f:
			return json.load(f) or {}

	def findinilocation(self, args: Namespace, srcdir: str, inifilename: str) -> str | None:
		"""
		Return the path to the found or creatable ini file, or None if not found.
		"""
		self.srcdir = srcdir.removesuffix("/.")
		if getattr(args, "ini", None):
			debug.debugmsg(5, "args.ini: ", args.ini)
			self.ini_file = args.ini
			return self.ini_file

		filename = inifilename or self.inifilename
		inilocations = []

		inilocations.append(os.path.join(self.srcdir, filename))
		inilocations.append(os.path.join(os.path.expanduser("~"), ".rfswarm", filename))
		inilocations.append(os.path.join(tempfile.gettempdir(), filename))

		debug.debugmsg(6, "inilocations: ", inilocations)

		for iniloc in inilocations:
			debug.debugmsg(7, "iniloc: ", iniloc)
			if os.path.isfile(iniloc):
				debug.debugmsg(7, "iniloc exists")
				self.ini_file = iniloc
				return iniloc
			else:
				debug.debugmsg(7, "iniloc can be created?")
				try:
					loc = os.path.dirname(iniloc)
					if not os.path.isdir(loc):
						os.makedirs(loc, exist_ok=True)

					if os.access(loc, os.X_OK | os.W_OK):
						debug.debugmsg(7, "iniloc can be created!")
						self.ini_file = iniloc
						return iniloc
				except Exception:
					debug.debugmsg(5, f"Failed to create ini file location: {iniloc}")

		return None

	@classmethod
	def configparser_safe_dict(cls, dictin: Any) -> Any:
		"""Convert nested dictionaries and types into ConfigParser-compatible format."""
		if not hasattr(dictin, "items"):
			return dictin
		dictout = {}
		for k, v in dictin.items():
			if hasattr(v, "items"):
				dictout[k] = cls.configparser_safe_dict(v)
			elif isinstance(v, (list, tuple)):
				dictout[k] = ", ".join(str(x) for x in v)
			elif isinstance(v, bool):
				dictout[k] = str(v)
			elif v is None:
				dictout[k] = ""
			else:
				dictout[k] = str(v)
		return dictout

	def saveini(self) -> None:
		if not (self.save_ini and self.ini_file):
			return

		debug.debugmsg(6, "save_ini:", self.save_ini)
		ext = os.path.splitext(self.ini_file)[1].lower() 
		raw_data = self.to_dict() 

		if ext in ('.yml', '.yaml'):
			with open(self.ini_file, 'w', encoding='utf-8') as f:
				yaml.safe_dump(raw_data, f)
		elif ext == '.json':
			with open(self.ini_file, 'w', encoding='utf-8') as f:
				json.dump(raw_data, f, indent=4)
		else:
			parser = configparser.ConfigParser()
			safe_dict = self.configparser_safe_dict(raw_data)
			parser.read_dict(safe_dict)
			with open(self.ini_file, 'w', encoding='utf-8') as f:
				parser.write(f)

		debug.debugmsg(6, "File Saved:", self.ini_file)


config = Config()
