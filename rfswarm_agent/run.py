from rfswarm_agent.rfswarm_agent import RFSwarmAgent


def run_agent(args):
	rfsa = RFSwarmAgent(args)
	try:
		rfsa.mainloop()
	except KeyboardInterrupt:
		rfsa.on_closing()
	except Exception as e:
		rfsa.debug.debugmsg(1, "rfsa.Exception:", e)
