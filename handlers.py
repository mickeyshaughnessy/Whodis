from database import Database

db = Database()

def db_resolve(req):
    return db.get_by_event(req) 

def db_inject(reslv, req):
    # return db.inject(req)
    pass

if __name__ == "__main__":

    # test the db get functionality here
    redis.delete("REDHASH_TEST")
    db = database()

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

    query_events = [{"features" : [random.random() for j in range(FEATURE_D)]} for i in range(DB_SIZE)] 
    for i, e in enumerate(query_events):
        # get identity of e
        print(e)
        _id = db.get_by_event(e)
        if _id == None:
            print("got None from db.get_by_event call")
            e["candles"] = []
            db.set(i, e, _hash="REDHASH_TEST")
        # insert e into db
        # distances hack to insert event here
        # db.get_by_event(e, resolution=0.5)
        #db.insert(_id, e, distances)
