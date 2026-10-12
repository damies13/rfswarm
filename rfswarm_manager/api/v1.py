from flask import Blueprint, current_app, jsonify

v1_blueprint = Blueprint('v1_blueprint', __name__)

@v1_blueprint.route('/status', methods=['GET'])
def get_v1_status():
    # Safely retrieve your injected dependencies from current_app
    core = current_app.config['APP_CORE']
    base = current_app.config['APP_BASE']
    
    # Read the data that is actively shared with your parent application
    response_payload = {
        "api_version": "v1 (Legacy)",
        "Agents": base.Agents,
        "app_version": base.version
    }
    return jsonify(response_payload), 200
