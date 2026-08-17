import inspect
from datetime import datetime

def debugmsg(lvl: int, *msg) -> None:
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
				suffix = "\t[{} @{}]".format(self.version, str(datetime.now().isoformat(sep=' ', timespec='seconds')))

			for itm in msg:
				msglst.append(str(itm))
			msglst.append(str(suffix))
			print(" ".join(msglst), flush=True)
		except Exception:
			pass
