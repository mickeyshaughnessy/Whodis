import json, redis, random, math, uuid
from config import REDHASH_TEST, FEATURE_D

redis_client = redis.StrictRedis(charset="utf-8", decode_responses=True)

class Database:
    def __init__(self):
        self.candles = []
        self.CANDLE_LEN = 12
        self.initial_stopping_criteria = 0.6
        self.stopping_criteria = self.initial_stopping_criteria
        self.recursive_steps = 0

    def set(self, key, value, _hash=REDHASH_TEST):
        if len(self.candles) < self.CANDLE_LEN:
            self.candles.append(key)
        v = json.dumps(value)
        redis_client.hset(_hash, key, v) if _hash else redis_client.set(key, v)

    def get(self, key, _hash=REDHASH_TEST):
        v = redis_client.hget(_hash, key) if _hash else redis_client.get(key)
        return json.loads(v) if v else None

    def distance_function(self, event, db_event):
        if not event or not db_event:
            return None
        return math.sqrt(sum((event.get("features")[i] - db_event.get("features")[i])**2 for i in range(FEATURE_D)))

    def update_stopping_criteria(self, db_size, depth):
        self.stopping_criteria = self.initial_stopping_criteria + (0.001 * depth * math.log(db_size + 1))

    def recursive_descent(self, event, db_events_keys, last_distances, depth=0):
        self.recursive_steps += 1
        if not db_events_keys:
            return None
        db_events = [self.get(str(k)) for k in db_events_keys]
        if not db_events:
            return None

        distances = [(self.distance_function(event, db_event), db_event) for db_event in db_events if db_event]
        distances = [d for d in distances if d[0] is not None]

        if not distances:
            return None

        distances.sort(key=lambda x: x[0])
        best_match = distances[0][1]
        new_best_distance = distances[0][0]

        self.update_stopping_criteria(len(db_events_keys), depth)

        if new_best_distance < self.stopping_criteria:
            return best_match
        elif last_distances and new_best_distance > last_distances[0]:
            return event
        else:
            num_neighbors_to_check = min(5 + depth, len(db_events))
            return self.recursive_descent(event, [k for _, k in distances[:num_neighbors_to_check]], distances, depth + 1)

    def get_by_event(self, event, resolution=None):
        self.recursive_steps = 0
        result = self.recursive_descent(event, self.candles, last_distances=None)
        return result, self.recursive_steps

    def insert_event(self, event):
        if "id" not in event:
            event["id"] = str(uuid.uuid4())
        self.set(event["id"], event)
        if event["id"] not in self.candles:
            self.candles.append(event["id"])

db = Database()

def event_to_features(event):
    features = []
    for key, value in event.items():
        if isinstance(value, (int, float)):
            features.append(value)
        elif isinstance(value, str):
            features.append(hash(value) % 1000 / 1000)
    while len(features) < FEATURE_D:
        features.append(0)
    return features[:FEATURE_D]

def db_resolve(req):
    api_key = req.get('api_key')
    body = req.get('body')
    resolution = req.get('resolution', 0)
    privacy = req.get('privacy', 0)

    if not api_key or not body:
        return {"error": "Invalid request. Missing api_key or body."}

    event = {"features": event_to_features(body)}
    result, steps = db.get_by_event(event)

    if result:
        response = {k: v for k, v in result.items() if k != "features"}
        response["confidence"] = 1 - (steps / db.CANDLE_LEN)
        response["privacy"] = privacy
        return response
    else:
        return {"error": "No matching entity found."}

def db_inject(entity, req):
    privacy = req.get('privacy', 0)
    if not entity:
        return {"error": "Invalid entity for privacy injection."}

    entity["privacy"] = privacy
    db.insert_event(entity)
    return {"message": "Privacy injected successfully."}

def initialize_db():
    sample_data = [
        {"id": "1", "name": "John Doe", "email": "john@example.com", "age": 30},
        {"id": "2", "name": "Jane Smith", "email": "jane@example.com", "age": 28},
        {"id": "3", "name": "Bob Johnson", "email": "bob@example.com", "age": 35}
    ]
    for data in sample_data:
        event = {"features": event_to_features(data)}
        db.insert_event({**data, **event})

initialize_db()
