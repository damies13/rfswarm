from rfswarm_agent.rfswarm_agent import RFSwarmAgent
from rfswarm_common.__version__ import __version__
from rfswarm_common.debug import debug


def run_agent(args):
	if args.debug:
		debug.debuglvl = int(args.debug)

	debug.debugmsg(0, "Robot Framework Swarm: Run Agent")
	debug.debugmsg(0, "	Version", __version__)
	# display version, help message ...
	# load config, and asess the arguments
	# load config instance of a class the same way as the debug everywhere when needed

	rfsa = RFSwarmAgent(args)
	try:
		rfsa.mainloop()
	except KeyboardInterrupt:
		rfsa.on_closing()
	except Exception as e:
		debug.debugmsg(1, "rfsa.Exception:", e)
