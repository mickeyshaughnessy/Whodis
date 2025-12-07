import json
import uuid
import time
from flask import Flask, jsonify, request
from database import db

app = Flask(__name__)

def validate(req):
    # Simple validation
    return str(uuid.uuid4()), int(time.time())

@app.route("/inject", methods=['POST'])
def inject():
    try:
        req = request.get_json()
        if not req or 'body' not in req:
            return jsonify({"error": "Missing body in request"}), 400
            
        body = req['body']
        
        # Insert into DB
        # If ID is provided in body, use it, else generate one
        if 'id' not in body:
            body['id'] = str(uuid.uuid4())
            
        saved_event = db.insert_event(body)
        
        return jsonify({
            "message": "Event injected successfully",
            "id": saved_event['id']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resolve", methods=['POST'])
def resolve_entity():
    try:
        req = request.get_json()
        if not req or 'body' not in req:
            return jsonify({"error": "Missing body in request"}), 400
            
        body = req['body']
        privacy = req.get('privacy', 0)
        
        # Convert body to features for search
        event_features = db.event_to_features(body)
        search_event = {"features": event_features}
        
        result, steps = db.get_by_event(search_event)

        if result:
            # Filter out internal fields for response
            response = {k: v for k, v in result.items() if k != "features"}
            response["confidence"] = 1.0 - (steps / (steps + 5)) # Simple mock confidence
            response["privacy"] = privacy
            return jsonify(response)
        else:
            return jsonify({"error": "No matching entity found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ping", methods=['GET', 'POST'])
def ping():
    return jsonify({"message": "ok"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
