from bottle import Bottle, request, response

class ApiV1Component:
	def __init__(self, core, base):
		self.core = core
		self.base = base
		
		# Create an isolated sub-app for version 1
		self.app = Bottle()
		self._setup_routes()

	def _setup_routes(self):
		# @self.app.route('/status', method='GET')
		# def legacy_status():
		#	 # Returns data format expected by legacy clients
		#	 return {
		#		 "v1_response": True,
		#		 "app_counter": self.core.shared_dict.get("counter")
		#	 }

		# @self.app.route('/update', method='POST')
		# def legacy_update():
		#	 data = request.json
		#	 if not data or "old_key" not in data:
		#		 response.status = 400
		#		 return {"error": "Malformed legacy request"}
				
		#	 self.core.shared_dict["last_received"] = f"v1: {data['old_key']}"
		#	 response.status = 201
		#	 return {"status": "success"}

		@self.app.route('/', method='GET')
		def get_index():
			# Returns data format expected by legacy clients
			self.base.debugmsg(5, "get_index:")
			res = self.base.qhandler._index()
			self.base.debugmsg(5, "res:", res)

			# "status": httpcode,
			# "message": dindexdata

			if "status" not in res:
				 response.status = 500
				 return {"error": f"Malformed legacy response: {res}"}

			if "message" not in res:
				 response.status = 500
				 return {"error": f"Malformed legacy response: {res}"}

			response.status = int(res["status"])
			return res["message"]

