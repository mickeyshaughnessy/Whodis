from database import database as DB

import random, json

db = DB()

import json
import random
import config
import redis

class database:
    def __init__(self):
        self.candles = []
        self.stopping_criteria = 0.1  # for recursive descent stopping

    def get_salt(self, key):
        return redis.hget(config.REDHASH_SALTS, key)

    def set(self, key, value, _hash=config.REDHASH_PROFILES):
        v = json.dumps(value)
        redis.hset(_hash, key, v) if _hash else redis.set(key, v)

    def get(self, key, _hash=config.REDHASH_PROFILES):
        v = redis.hget(_hash, key) if _hash else redis.get(key)
        return json.loads(v) if v else None

    def distance_function(self, event, db_event):
        # Placeholder for actual distance computation
        pass

    def recursive_descent(self, event, db_events_keys):
        if not db_events_keys or self.stopping_criteria <= 0:
            return None  # Base case

        db_events = [self.get(k) for k in db_events_keys if self.get(k)]
        if not db_events:
            return None  # Safety check

        distances = [(self.distance_function(event, db_event), db_event) for db_event in db_events]
        distances.sort(key=lambda x: x[0])
        best_match = distances[0][1]  # closest point

        if distances[0][0] < self.stopping_criteria:
            return best_match  # Stopping condition met
        else:
            return self.recursive_descent(event, best_match.get("candles", []))

    def get_by_event(self, event):
        _profile = self.recursive_descent(event, self.candles)
        return _profile

#class database():
#    def __init__(self):
#        self.candles = []
#        self.stopping_criteria = 0.1 # for recursive descent stopping
#
#    def get_salt(self, key):
#        return redis.hget(config.REDHASH_SALTS, key)
#
#    def set(self, key, value, _hash=config.REDHASH_PROFILES):
#        v = json.dumps(value)
#        if not _hash:
#            redis.set(key, value) 
#        else:
#            redis.hset(_hash, key, value)
#
#    def get(self, key, _hash=config.REDHASH_PROFILES):
#        if not _hash:
#            return json.loads(redis.get(key))
#        else:
#            return json.loads(redis.hget(_hash, key))
#   
#    def canonical_profile_event_transform(self, event, profile):
#        # could improve later
#        profile_event = random.choice(profile.get("events_list",[]))
#        return profile_event
#    
#    def get_by_event(self, event):
#        # get the db candles
#        _profile = recursive_descent(self, event, self.candles)
#
#    def recursive_descent(self, event, db_events_keys):
#        # descend into the db recursively until done
#        db_events = [self.get(k) for k in db_events_keys]
#        distances = [(self.distance_function(event, db_event), db_event) for db_event in db_events]
#        distances.sort(key=lambda x : x[0])
#        best = distances[0] # closest point
#        best_candles = best[1].get("candles",[])
#        
#        ret = recursive_descent(self, event, best_candles):
        

        

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
