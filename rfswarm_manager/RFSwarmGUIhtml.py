
import eel
# import RFSwarmV2API

class RFSwarmGUIhtml():

	base = None
	core = None

	def __init__(self, base, core):
		self.base = base
		self.core = core
		self.base.debugmsg(0, "init v2 GUI")

		self.base.v2startmode = 'chrome'
		self.base.v2path = "V2UI"
		self.base.v2starturl = "index.html"
		# self.base.v2startmode = None 				# `None` or `False` to not open a window. *Default:* :code:`'chrome'`.
		# if not base.args.nogui:
		# 	self.base.v2startmode = 'chrome'
		# self.base.v2starthost = base.config['Server']['BindIP']
		# self.base.v2startport = int(base.config['Server']['BindPort']) + 1
		# self.base.v2startapp = RFSwarmV2API.RFSwarmV2API().api_object()


	def addScriptRow(self):
		self.base.debugmsg(0, "v2 add script row")
