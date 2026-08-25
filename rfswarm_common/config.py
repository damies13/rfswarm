import configparser
import json
import os
import tempfile
from typing import Any, Optional
import yaml

from rfswarm_common.debug import debug


class Config:
	"""
	Class to handle configuration for RFSwarm components (Agent, Manager, Reporter).
	"""

	def __init__(self):
		self.args = None
		self.inifilename: Optional[str] = None
		self.srcdir: Optional[str] = None
		self.ini_file: Optional[str] = None
		self.save_ini: bool = True
		self.data: configparser.ConfigParser = configparser.ConfigParser()

	def load_config(self, inifilename: str, srcdir: str, args) -> str:
		"""
		Finds and loads configuration from .ini, .yaml, or .json file into self.data.
		"""
		debug.debugmsg(5, "agentini: ", self.ini_file)
		self.args = args
		self.inifilename = inifilename
		self.srcdir = srcdir or os.path.dirname(os.path.abspath(__file__))
		self.ini_file = self.findinilocation()

		if self.ini_file and os.path.isfile(self.ini_file):
			debug.debugmsg(5, "Loading configuration file: ", self.ini_file)
			ext = os.path.splitext(self.ini_file)[1].lower()

			loaders = {
				".ini": self._load_ini,
				".yml": self._load_yaml,
				".yaml": self._load_yaml,
				".json": self._load_json,
			}

			if ext in loaders:
				loaders[ext](self.ini_file)
			else:
				debug.debugmsg(0, "Configuration file ", self.ini_file, " has an invalid extention, unable to determine supported format. Plesae use extentions .ini, .yaml or .json")
				exit()
		else:
			self.saveini()
			debug.debugmsg(5, "Configuration file does not exist yet; will be created on save:", self.ini_file)

		return self.ini_file

	def _load_ini(self, filepath: str) -> None:
		debug.debugmsg(5, "read ini file")
		self.data.read(filepath, encoding="utf-8")

	def _load_yaml(self, filepath: str) -> None:
		debug.debugmsg(5, "read yaml file")
		with open(filepath, "r", encoding="utf-8") as f:
			configdict = yaml.safe_load(f) or {}
		configdict = self.configparser_safe_dict(configdict)
		self.data.read_dict(configdict)

	def _load_json(self, filepath: str) -> None:
		debug.debugmsg(5, "read json file")
		with open(filepath, "r", encoding="utf-8") as f:
			configdict = json.load(f) or {}
		configdict = self.configparser_safe_dict(configdict)
		self.data.read_dict(configdict)

	def findinilocation(self) -> Optional[str]:
		if self.args and hasattr(self.args, "ini") and self.args.ini:
			debug.debugmsg(5, "self.args.ini: ", self.args.ini)
			self.ini_file = self.args.ini
			return self.ini_file

		inilocations = []

		srcdir = self.srcdir or ""
		if srcdir.endswith("/."):
			srcdir = srcdir[:-2]

		inilocations.append(os.path.join(srcdir, self.inifilename or "RFSwarmAgent.ini"))
		inilocations.append(os.path.join(os.path.expanduser("~"), ".rfswarm", self.inifilename or "RFSwarmAgent.ini"))
		inilocations.append(os.path.join(tempfile.gettempdir(), self.inifilename or "RFSwarmAgent.ini"))

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
					pass

		return None

	def configparser_safe_dict(self, dictin: Any) -> Any:
		"""Convert nested dictionaries and types into ConfigParser-compatible format."""
		if not isinstance(dictin, dict):
			return dictin
		dictout = {}
		for k, v in dictin.items():
			if isinstance(v, dict):
				dictout[k] = self.configparser_safe_dict(v)
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
		debug.debugmsg(6, "save_ini:", self.save_ini)
		if self.save_ini and self.ini_file:
			with open(self.ini_file, "w", encoding="utf-8") as configfile:
				self.data.write(configfile)
				debug.debugmsg(6, "File Saved:", self.ini_file)


config = Config()

