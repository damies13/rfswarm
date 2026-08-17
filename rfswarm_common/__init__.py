# init file for pip setup.py packaging tool to find

from .__version__ import __version__
from .debug import Debug, debug

__all__ = ["__version__", "Debug", "debug"]

