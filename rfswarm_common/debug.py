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
					frame = stack[1][0]
					the_self = frame.f_locals.get("self")
					the_cls = frame.f_locals.get("cls")
					if the_self is not None:
						the_class = the_self.__class__.__name__
					elif the_cls is not None:
						the_class = the_cls.__name__ if hasattr(the_cls, "__name__") else str(the_cls)
					else:
						the_class = ""

					the_method = frame.f_code.co_name
					the_line = frame.f_lineno

					if the_class:
						prefix = "{}: {}({}): [{}:{}]\t".format(str(the_class), the_method, the_line, self.debuglvl, lvl)
					else:
						prefix = "{}({}): [{}:{}]\t".format(the_method, the_line, self.debuglvl, lvl)

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
