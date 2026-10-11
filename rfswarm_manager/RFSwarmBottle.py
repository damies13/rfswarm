import os
import threading
import bottle
# from bottle import Bottle, static_file, WSGIRefServer
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler

# Import your newly structured sub-components
from api.apiv1 import ApiV1Component
# from api.apiv2 import ApiV2Component

class ShareableWSGIServer:
	"""A direct WSGI server adapter that respects a debug/quiet flag perfectly."""
	def __init__(self, host, port, quiet=True):
		self.host = host
		self.port = port
		self.quiet = quiet
		self.server = None

	def run(self, app):
		# Explicitly mute standard request logs if quiet is set to True
		if self.quiet:
			class QuietHandler(WSGIRequestHandler):
				def log_message(self, format, *args):
					pass # Completely drops request logs
			handler_cls = QuietHandler
		else:
			handler_cls = WSGIRequestHandler

		# Start the native wsgiref server loop directly (bypassing Bottle's banner printer)
		self.server = make_server(self.host, self.port, app, WSGIServer, handler_cls)
		self.server.serve_forever()

	def stop(self):
		if self.server:
			self.server.shutdown()
			self.server.server_close()

class EmbeddedBottleApp:
	def __init__(self, core, base, host='0.0.0.0', port=8139):
		self.core = core
		self.base = base
		self.host = host
		self.port = port

		# Determine quiet state based on your parent application's integer level
		# If debuglvl is 0, quiet is True (silent). If 1-9, quiet is False (verbose debug logs).
		is_quiet = (self.base.debuglvl < 5)

		# 1. Toggle Bottle's inner global configuration flags
		bottle.QUIET = is_quiet

		# Lifts the memory parsing threshold safely up to 1 GB
		bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024  

		# self.server_instance = ShareableWSGIServer(host=self.host, port=self.port, quiet=False, debug=True)
		self.server_instance = ShareableWSGIServer(host=self.host, port=self.port, quiet=is_quiet)
		self.server_thread = None
		
		# Primary Root application context
		self.app = bottle.Bottle()
		self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webui')
		self.base.debugmsg(5, "self.static_dir:", self.static_dir)

		self._build_and_mount_components()

	def _build_and_mount_components(self):
		# 1. Base static asset route on the main app router
		@self.app.route('/webui/<filepath:path>')
		def server_static(filepath):
			self.base.debugmsg(5, "filepath:", filepath)
			return bottle.static_file(filepath, root=self.static_dir)

		# 2. Instantiate isolated controllers and feed them core/base dependencies
		v1_controller = ApiV1Component(core=self.core, base=self.base)
		# v2_controller = ApiV2Component(core=self.core, base=self.base)

		# 3. Mount sub-apps onto structural url prefixes
		# Note: Paths inside apiv1/apiv2 are now relative to these prefixes.
		# e.g., apiv1's '/status' becomes accessible at '/api/v1/status'
		self.app.mount('/api/v1', v1_controller.app)
		# self.app.mount('/api/v2', v2_controller.app)

	def start(self):
		self.server_thread = threading.Thread(target=self._run_server, daemon=True)
		self.server_thread.start()
		self.base.debugmsg(5, f"[Web] Server running. V1 and V2 APIs mapped at http://{self.host}:{self.port}/api/...")

	def _run_server(self):
		self.server_instance.run(self.app)

	def on_closing(self):
		self.base.debugmsg(5, "[Web] Shutting down multi-version server API router...")
		self.server_instance.stop()
		if self.server_thread:
			self.server_thread.join(timeout=3)
		self.base.debugmsg(5, "[Web] Sub-apps cleanly unmounted and stopped.")
