import random, json, redis
import config

redis = redis.StrictRedis(charset="utf-8", decode_responses=True)
class database:
    def __init__(self):
        self.candles = [random.choice([j for j in range(100)]) for i in range(12)]
        self.stopping_criteria = 0.001  # for recursive descent stopping

    def get_salt(self, key):
        return redis.hget(config.REDHASH_SALTS, key)

    def set(self, key, value, _hash=config.REDHASH_PROFILES):
        v = json.dumps(value)
        redis.hset(_hash, key, v) if _hash else redis.set(key, v)

    #def get(self, key, _hash=config.REDHASH_PROFILES):
    def get(self, key, _hash="REDHASH_TEST"):
        v = redis.hget(_hash, key) if _hash else redis.get(key)
        #return json.loads(v) if v else None
        return json.loads(v) if v else None 

    def distance_function(self, event, db_event):
        # Placeholder for actual distance computation
        # assume they are vectors 10 long
        import math
        #print(event, db_event)
        return math.sqrt(sum([abs(event.get("features")[i] - db_event.get("features")[i]) for i in range(10)]))

    def recursive_descent(self, event, db_events_keys):
        print(event, db_events_keys)
        if not db_events_keys: 
            print('here')
            return None  # Base case

        print(db_events_keys)
        db_events = [self.get(str(k)) for k in db_events_keys]
        print(db_events)
        if not db_events:
            print('here1')
            return None  # Safety check

        distances = [(self.distance_function(event, db_event), db_event) for db_event in db_events]
        distances.sort(key=lambda x: x[0])
        best_match = distances[0][1]  # closest point

        if distances[0][0] < self.stopping_criteria + 0.0 : # inject noise here
            return best_match  # Stopping condition met
        else:
            return self.recursive_descent(event, best_match.get("candles", []))

    def get_by_event(self, event):
        _profile = self.recursive_descent(event, self.candles)
        return _profile

def validate(req):
    # checks to see if the 
    key = req.get("key")
    if key:
        salt = bd.get_salt(key)
        authed = db.get(key+salt)
        return authed # True or False
    else:
        return False

def db_resolve(req):
    pass

def db_inject(reslv, req):
    pass

if __name__ == "__main__":
    # test the db get functionality here
    db = database()
    redis.delete("REDHASH_TEST")
    for i in range(100):
        features = [random.random() for j in range(10)]
        candles = []
        for j,v in redis.hscan_iter("REDHASH_TEST"): # getting keys
            v = json.loads(v)
            d = db.distance_function(v, {"features" : features})
            #print(d)
            #if len(candles) < 13:
            #    candles.append((j,d))
            #elif d < candles[-12][1]: # (index, distance)
            candles.append((j, d))
            candles.sort(key=lambda x : -x[1])
        print(sum([c[1] for c in candles]))
        redis.hset("REDHASH_TEST", i, json.dumps({"features" : features, "candles" : [c[0] for c in candles[-12:]]})) 
    print('finished loading db')
    query_event = {"features" : [random.random() for j in range(10)]}
    print(query_event)
    res = db.get_by_event(query_event)
    print(res)
