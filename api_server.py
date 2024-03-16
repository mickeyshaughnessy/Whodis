# This is the whodis api server
# It has a REST API to execute queries and inject privacy:

import json, redis, uuid, time
import config, handlers
from flask import Flask, jsonify, request
redis = redis.StrictRedis()

app = Flask(__name__)

def validate(req):
    req_id, ts = str(uuid.uuid4()), int(time.time()) 
    # put arcane validation logic here
    return req_id, ts

@app.route("/inject", methods=['POST'])
def inject():
    req = request.get_json()
    req_id, ts = validate(req)
    if req_id:
        resp = {}
        reslv = handlers.db_resolve(req) # get the entity
        #resp = handlers.db_inject(reslv, req)  # inject privacy into entity
        redis.hset(config.REDHASH_INJECT_LOG, req_id, json.dumps({"ts" : ts, "request" : req})) 
        return json.dumps(resp)
    else:
        return json.dumps({"message" : "invalid request"})

@app.route("/resolve", methods=['POST'])
def resolve_entity():
    req = request.get_json()
    req_id, ts = validate(req)
    reslv = handlers.db_resolve(req)  
   
    redis.hset(config.REDHASH_QUERY_LOG, req_id, json.dumps({"ts" : ts, "request" : req, "response" : reslv})) 
    return json.dumps(reslv)

@app.route("/ping", methods=['GET', 'POST'])
def ping():
    return json.dumps({"message" : "ok"})

@app.route("/UID2_optout", methods=['GET','POST'])
def UID2_optout():
    req = request.get_json()
    UID2 = req.get('UID2', "")
    redis.hset(config.REDHASH_UID2_OPTOUT, UID2, json.dumps(req)) 
    return json.dumps({"message" : "opted_out %s" % UID2})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
