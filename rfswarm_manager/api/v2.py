from flask import Blueprint, current_app, jsonify, request

v2_blueprint = Blueprint('v2_blueprint', __name__)

@v2_blueprint.route('/update', methods=['POST'])
def post_v2_update():
    core = current_app.config['APP_CORE']
    
    # 1. Convert incoming JSON POST body to a Python dictionary
    # force=True ensures parsing even if the Content-Type header isn't perfectly set
    data = request.get_json(force=True, silent=True)
    
    # 2. Condition Validation for Error Response Codes
    if not data:
        return jsonify({"error": "Bad Request", "message": "Missing or invalid JSON body"}), 400
        
    if "status_update" not in data:
        return jsonify({"error": "Unprocessable Entity", "message": "Missing 'status_update' key"}), 422

    # 3. Update the shared parent dictionary
    new_status = data["status_update"]
    core.shared_data["status"] = new_status
    
    # 4. Return success along with HTTP status code 201
    return jsonify({
        "message": "Data updated successfully",
        "current_shared_state": core.shared_data
    }), 201
