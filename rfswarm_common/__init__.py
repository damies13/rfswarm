# init file for pip setup.py packaging tool to find

from .__version__ import __version__
from .debug import Debug, debug
from .config import Config, config
from .filestransfers import FilesTransfers

__all__ = ["__version__", "Debug", "debug", "Config", "config", "FilesTransfers"]

