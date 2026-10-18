# fastapiserver.py
import ipaddress
import os
import socket
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse

# Import the routers
from api import v1
from api import v2

class RFSwarmFastAPI:
	# def __init__(self, core, host="127.0.0.1", port=8000):
	def __init__(self, base, core):

		srvip = base.config['Server']['BindIP']
		srvport = int(base.config['Server']['BindPort'])
		if len(srvip) > 0:
			base.srvdisphost = srvip
			ip = ipaddress.ip_address(srvip)
			base.debugmsg(5, "ip.version:", ip.version)
			# 2026/10/16 - I think the lines below were for ThreadingHTTPServer and aren't needed now, but leaving them
			# 				here commented out incase we need them
			# if ip.version == 6 and sys.version_info < (3, 8):
			# 	self.base.debugmsg(0, "Python 3.8 or higher required to bind to IPv6 Addresses")
			# 	pyver = "{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
			# 	self.base.debugmsg(0, "Python Version:", pyver, "	IP Version:", ip.version, "	IP Address:", srvip)
			# 	srvip = '0.0.0.0'
			# 	# srvip = ''
			# 	self.base.srvdisphost = socket.gethostname()
		else:
			base.srvdisphost = socket.gethostname()

		self.disphost = base.srvdisphost
		self.host = srvip
		self.port = srvport
		self.thread = None
		self.server = None
		
		base.debugmsg(5, "FastAPI starting")

		# Create the underlying FastAPI instance
		self.app = FastAPI()

		# Crucial Step: Attach your parent application's core reference to the app state
		self.app.state.base = base
		self.app.state.core = core

		self.debuglvl = base.debuglvl

		# Setup static files and routers
		# Setup static files 
		webuidir = os.path.join(os.path.dirname(__file__), "webui", "v2")
		base.debugmsg(5, "webui:", webuidir)
		self.app.mount("/webui/v2", StaticFiles(directory=webuidir, html=True), name="webui")

		@self.app.get("/")
		@self.app.get("/webui")
		@self.app.get("/webui/v2")
		@self.app.get("/webui/v2/")
		async def root():
			return RedirectResponse(url="/webui/v2/index.html")

		# Define the absolute or relative path to your favicon file
		FAVICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "rfswarm-manager-128.ico")
		@self.app.get("/favicon.ico", include_in_schema=False)
		async def favicon():
			return FileResponse(FAVICON_PATH)


		# Setup routers
		self.app.include_router(v1.router)
		self.app.include_router(v2.router)

		base.debugmsg(5, "FastAPI started")

		base.appstarted = True
		base.debugmsg(5, "appstarted:", base.appstarted)


	def _run(self):
		# 1. Determine if access logs should be enabled
		# True only if debug_level is exactly 7
		show_access_logs = (self.debuglvl == 5)
		
		# 2. Pass access_log to the configuration block
		config = uvicorn.Config(
			self.app, 
			host=self.host, 
			port=self.port, 
			log_level="info" if show_access_logs else "warning", # Drops internal startup spam if not debug
			access_log=show_access_logs                          # Disables the HTTP request console prints
		)

		# config = uvicorn.Config(
		#     self.app, host=self.host, port=self.port, log_level="info"
		# )
		self.server = uvicorn.Server(config)
		self.server.run()

	def start(self):
		"""Starts the FastAPI server in a background thread."""
		self.thread = threading.Thread(target=self._run, daemon=True)
		self.thread.start()
		self.app.state.base.debugmsg(1, "Starting Agent Manager", f"http://{self.disphost}:{self.port}/")

	def stop(self):
		"""Cleanly stops the server."""
		if self.server is not None:
			self.app.state.base.debugmsg(1, "[FastApiServer] Triggering server shutdown...")
			self.server.should_exit = True
