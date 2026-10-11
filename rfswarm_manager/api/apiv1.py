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

		# V1 API
		# GET
		# "/", 
		@self.app.route('/', method='GET')
		def legacy_get_index():
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

		# POST
		# "/AgentStatus", 
		@self.app.route('/AgentStatus', method='POST')
		def legacy_AgentStatus():
			self.base.debugmsg(5, "legacy_AgentStatus:")
			data = request.json
			self.base.debugmsg(5, "data:", data)

			res = self.base.qhandler._AgentStatus(data)
			self.base.debugmsg(5, "res:", res)

			if "status" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			if "message" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			response.status = int(res["status"])
			return res["message"]


		# "/Jobs", 
		@self.app.route('/Jobs', method='POST')
		def legacy_Jobs():
			self.base.debugmsg(5, "legacy_Jobs:")
			data = request.json
			self.base.debugmsg(5, "data:", data)

			res = self.base.qhandler._Jobs(data)
			self.base.debugmsg(5, "res:", res)

			if "status" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			if "message" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			response.status = int(res["status"])
			return res["message"]


		# "/Scripts", 
		@self.app.route('/Scripts', method='POST')
		def legacy_Scripts():
			self.base.debugmsg(5, "legacy_Scripts:")
			data = request.json
			self.base.debugmsg(5, "data:", data)

			res = self.base.qhandler._Scripts(data)
			self.base.debugmsg(5, "res:", res)

			if "status" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			if "message" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			response.status = int(res["status"])
			return res["message"]


		# "/File", 
		@self.app.route('/File', method='POST')
		def legacy_File():
			self.base.debugmsg(5, "legacy_File:")
			data = request.json
			self.base.debugmsg(5, "data:", data)

			res = self.base.qhandler._File(data)
			self.base.debugmsg(5, "res:", res)

			if "status" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			if "message" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			response.status = int(res["status"])
			return res["message"]


		# "/Result", 
		@self.app.route('/Result', method='POST')
		def legacy_Result():
			self.base.debugmsg(5, "legacy_Result:")
			data = request.json
			self.base.debugmsg(5, "data:", data)

			res = self.base.qhandler._Result(data)
			self.base.debugmsg(5, "res:", res)

			if "status" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			if "message" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			response.status = int(res["status"])
			return res["message"]


		# "/Metric"
		@self.app.route('/Metric', method='POST')
		def legacy_Metric():
			self.base.debugmsg(5, "legacy_Metric:")
			data = request.json
			self.base.debugmsg(5, "data:", data)

			res = self.base.qhandler._Metric(data)
			self.base.debugmsg(5, "res:", res)

			if "status" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			if "message" not in res:
					response.status = 500
					return {"error": f"Malformed legacy response: {res}"}

			response.status = int(res["status"])
			return res["message"]



