import logging
import threading
import werkzeug.serving
from flask import Flask

# Import the Blueprints from your api package
from api.v1 import v1_blueprint
# from api.v2 import v2_blueprint

class FlaskServerRunner:
	def __init__(self, host, port, core, base):
		self.host = host
		self.port = port
		self.core = core
		self.base = base

		# Handle Werkzeug HTTP Request Logs based on Debug Level
		# Werkzeug logs everything at INFO level. If debug level <= 7, we set it to WARNING
		# to completely hide the 200/404 HTTP request lines.
		werkzeug_logger = logging.getLogger('werkzeug')
		if self.base.debuglvl > 5:
			werkzeug_logger.setLevel(logging.INFO)
		else:
			werkzeug_logger.setLevel(logging.WARNING)

		# Setup Flask with a declared static file folder
		self.app = Flask(__name__, static_folder='webui', static_url_path='/webui')
		
		# Inject core and base into Flask's internal config dictionary
		# This makes them accessible globally across all routes and blueprints
		self.app.config['APP_CORE'] = core
		self.app.config['APP_BASE'] = base

		# Register Blueprints for API version routing separation
		self.app.register_blueprint(v1_blueprint, url_prefix='/api/v1')
		# self.app.register_blueprint(v2_blueprint, url_prefix='/api/v2')

		# Set up a native development WSGI server wrapper for controlled shutdown
		self.server = werkzeug.serving.make_server(self.host, self.port, self.app)
		self.thread = None

	def start(self):
		"""Starts the Flask server inside a background thread."""
		self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
		self.thread.start()
		# print(f"[Flask] Server started on http://{self.host}:{self.port}")
		self.base.debugmsg(3, f"[Flask] Server started on http://{self.host}:{self.port}")

	def shutdown(self):
		"""Shutdown function called cleanly by the parent application's on_closing wrapper."""
		self.base.debugmsg(5, f"[Flask] shutting down....")
		if self.server:
			self.server.shutdown()  # Tells the Werkzeug server to stop serving cleanly
		if self.thread:
			self.thread.join()      # Wait for the thread to fully exit
		self.base.debugmsg(3, f"[Flask] Stopped")
