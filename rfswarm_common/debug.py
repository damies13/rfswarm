import inspect
from datetime import datetime
from .__version__ import __version__

class Debug():
	def __init__(self):
		self._debuglvl = 0

	@property
	def debuglvl(self) -> int:
		return self._debuglvl

	@debuglvl.setter
	def debuglvl(self, value) -> None:
		if not isinstance(value, int) or value < 0:
			raise ValueError("debuglvl must be a positive number")
		self._debuglvl = value

	def debugmsg(self, lvl: int, *msg) -> None:
		msglst = []
		prefix = ""
		if self.debuglvl >= lvl:
			try:
				suffix = ""
				if self.debuglvl >= 4:
					stack = inspect.stack()
					the_class = stack[1][0].f_locals["self"].__class__.__name__
					the_method = stack[1][0].f_code.co_name
					the_line = stack[1][0].f_lineno
					prefix = "{}: {}({}): [{}:{}]\t".format(str(the_class), the_method, the_line, self.debuglvl, lvl)

					if len(prefix.strip()) < 32:
						prefix = "{}\t".format(prefix)
					if len(prefix.strip()) < 24:
						prefix = "{}\t".format(prefix)

					msglst.append(str(prefix))
					suffix = "\t[{} @{}]".format(__version__, str(datetime.now().isoformat(sep=' ', timespec='seconds')))

				for itm in msg:
					msglst.append(str(itm))
				msglst.append(str(suffix))
				print(" ".join(msglst), flush=True)
			except Exception:
				pass

debug = Debug()