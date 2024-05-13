import config
import redis, json, random

FEATURE_D = 8
DB_SIZE = 10000
THRESH = 0.6
VERY_LARGE = 100
CANDLE_LEN = 12

redis = redis.StrictRedis(charset="utf-8", decode_responses=True)


class Database:
    def __init__(self):
        self.candles = []
        self.CANDLE_LEN = CANDLE_LEN
        self.stopping_criteria = THRESH  # for recursive descent stopping

    def get_salt(self, key):
        return redis.hget(config.REDHASH_SALTS, key)

    def set(self, key, value, _hash=config.REDHASH_PROFILES):
        if len(self.candles) < self.CANDLE_LEN:
               self.candles.append(key)
        v = json.dumps(value)
        redis.hset(_hash, key, v) if _hash else redis.set(key, v)

    #def get(self, key, _hash=config.REDHASH_PROFILES):
    def get(self, key, _hash="REDHASH_TEST"):
        v = redis.hget(_hash, key) if _hash else redis.get(key)
        #return json.loads(v) if v else None
        return json.loads(v) if v else None

    def distance_function(self, event, db_event):
        # Placeholder for actual distance computation
        # test: assume they are vectors 10 long
        if not event or not db_event:
            return None
        import math
        return math.sqrt(sum([(event.get("features")[i] - db_event.get("features")[i])**2 for i in range(FEATURE_D)]))

        # to handle JSON-JSON pairs, eventually we use ML distance metric
        # for demo, use deterministic matching on ids

    def recursive_descent(self, event, db_events_keys, last_distances):
        if not db_events_keys:
            #print('event keys not found')
            return None  # Base case
        db_events = [self.get(str(k)) for k in db_events_keys]
        if not db_events:
            #print('no input events')
            return None  # Safety check

        distances = [(self.distance_function(event, db_event), db_event) for db_event in db_events]

        distances.sort(key=lambda x: x[0])
        best_match = distances[0][1]  # closest point
        new_best_distance = distances[0][0]  # closest point
        print(distances[0][0])

        if new_best_distance < self.stopping_criteria + 0.0 : # inject noise here
            print('made it out under stopping criteria')
            return best_match  # Stopping condition met
        elif last_distances and new_best_distance > last_distances[0]:
            print(new_best_distance, last_distances[0])
            print('made it out under best effort search criteria')
            return event
        else:
            return self.recursive_descent(event, best_match.get("candles", []), distances)

    def get_by_event(self, event, resolution=None):
        #_profile = self.recursive_descent(event, self.candles, VERY_LARGE)
        _profile = self.recursive_descent(event, self.candles, last_distances=None)

        return _profile

    def insert_event(self, event):
        # this needs to be working properly, with key and value determined
        reslv = self.get_by_event(self, event)
        key = reslv.get("id")
        self.set(self, reslv) 

if __name__ == "__main__":
    # test the db get functionality here
    redis.delete("REDHASH_TEST")
    db = Database()

    ## fill in the test db here ('candles' and 'features') fields
    #for i in range(DB_SIZE):
    #    features = [random.random() for j in range(FEATURE_D)]
    #    candles = []
    #    for j,v in redis.hscan_iter("REDHASH_TEST"): # getting keys
    #        v = json.loads(v)
    #        d = db.distance_function(v, {"features" : features}) # distance between ith and jth element of the db
    #        candles.append((j, d))
    #        candles.sort(key=lambda x : -x[1])
    #    redis.hset("REDHASH_TEST", i, json.dumps({"features" : features, "candles" : [c[0] for c in candles[-12:]]}))
    #print('finished loading db')

    # single test query event
    #query_event = {"features" : [random.random() for j in range(FEATURE_D)]}
    #res = db.get_by_event(query_event)
    #if res:
    #    print(res, query_event)

    ### TEST SECTION ###
    query_events = [{"features" : [random.random() for j in range(FEATURE_D)]} for i in range(DB_SIZE)]
    for i, e in enumerate(query_events):
        # get identity of e
        print(e)
        _id = db.get_by_event(e)
        if _id == None:
            #print("got None from db.get_by_event call")
            e["candles"] = []
            db.set(i, e, _hash="REDHASH_TEST")
        else:
            print("Got %s result" % e)
        # insert e into db
        # distances hack to insert event here
        # db.get_by_event(e, resolution=0.5)
        #db.insert(_id, e, distances)
