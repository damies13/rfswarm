from flask import Blueprint, current_app, jsonify, request


v1_blueprint = Blueprint('v1_blueprint', __name__)


		# V1 API
		# GET
		# "/", 
@v1_blueprint.route('/', methods=['GET'])
def get_v1_index():
	# Safely retrieve your injected dependencies from current_app
	core = current_app.config['APP_CORE']
	base = current_app.config['APP_BASE']
	
	# Read the data that is actively shared with your parent application
	resp = base.qhandler._index()

	return jsonify(resp['message']), int(resp['status'])


		# POST
		# "/AgentStatus", 
@v1_blueprint.route('/AgentStatus', methods=['POST'])
def post_v1_AgentStatus():
	core = current_app.config['APP_CORE']
	base = current_app.config['APP_BASE']
	
	# Convert incoming JSON POST body to a Python dictionary
	# force=True ensures parsing even if the Content-Type header isn't perfectly set
	data = request.get_json(force=True, silent=True)
	base.debugmsg(5, "Request data:", data)

	resp = base.qhandler._AgentStatus(data)

	return jsonify(resp['message']), int(resp['status'])

		# "/Jobs", 
@v1_blueprint.route('/Jobs', methods=['POST'])
def post_v1_Jobs():
	core = current_app.config['APP_CORE']
	base = current_app.config['APP_BASE']
	
	# Convert incoming JSON POST body to a Python dictionary
	# force=True ensures parsing even if the Content-Type header isn't perfectly set
	data = request.get_json(force=True, silent=True)
	base.debugmsg(5, "Request data:", data)

	resp = base.qhandler._Jobs(data)

	return jsonify(resp['message']), int(resp['status'])

		# "/Scripts", 
@v1_blueprint.route('/Scripts', methods=['POST'])
def post_v1_Scripts():
	core = current_app.config['APP_CORE']
	base = current_app.config['APP_BASE']
	
	# Convert incoming JSON POST body to a Python dictionary
	# force=True ensures parsing even if the Content-Type header isn't perfectly set
	data = request.get_json(force=True, silent=True)
	base.debugmsg(5, "Request data:", data)

	resp = base.qhandler._Scripts(data)

	return jsonify(resp['message']), int(resp['status'])

		# "/File", 
@v1_blueprint.route('/File', methods=['POST'])
def post_v1_File():
	core = current_app.config['APP_CORE']
	base = current_app.config['APP_BASE']
	
	# Convert incoming JSON POST body to a Python dictionary
	# force=True ensures parsing even if the Content-Type header isn't perfectly set
	data = request.get_json(force=True, silent=True)
	base.debugmsg(5, "Request data:", data)

	resp = base.qhandler._File(data)

	return jsonify(resp['message']), int(resp['status'])

		# "/Result", 
@v1_blueprint.route('/Result', methods=['POST'])
def post_v1_Result():
	core = current_app.config['APP_CORE']
	base = current_app.config['APP_BASE']
	
	# Convert incoming JSON POST body to a Python dictionary
	# force=True ensures parsing even if the Content-Type header isn't perfectly set
	data = request.get_json(force=True, silent=True)
	base.debugmsg(5, "Request data:", data)

	resp = base.qhandler._Result(data)

	return jsonify(resp['message']), int(resp['status'])

		# "/Metric"
@v1_blueprint.route('/Metric', methods=['POST'])
def post_v1_Metric():
	core = current_app.config['APP_CORE']
	base = current_app.config['APP_BASE']
	
	# Convert incoming JSON POST body to a Python dictionary
	# force=True ensures parsing even if the Content-Type header isn't perfectly set
	data = request.get_json(force=True, silent=True)
	base.debugmsg(5, "Request data:", data)

	resp = base.qhandler._Metric(data)

	return jsonify(resp['message']), int(resp['status'])


