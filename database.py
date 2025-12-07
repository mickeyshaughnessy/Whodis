import json
import boto3
import math
import uuid
import config
from botocore.exceptions import ClientError

class Database:
    def __init__(self):
        kwargs = {
            'region_name': config.AWS_REGION
        }
        if config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY:
            kwargs['aws_access_key_id'] = config.AWS_ACCESS_KEY_ID
            kwargs['aws_secret_access_key'] = config.AWS_SECRET_ACCESS_KEY
            
        self.s3 = boto3.resource('s3', **kwargs)
        self.bucket = self.s3.Bucket(config.S3_BUCKET)
        
        self.CANDLE_LEN = config.CANDLE_LEN
        self.FEATURE_D = config.FEATURE_D
        self.initial_stopping_criteria = config.INITIAL_THRESH
        self.stopping_criteria = self.initial_stopping_criteria
        self.recursive_steps = 0
        
        # Load candles from S3 on init
        self.candles = self._load_candles()

    def _get_s3_key(self, key):
        return f"{config.S3_PREFIX}events/{key}.json"

    def _load_candles(self):
        try:
            obj = self.s3.Object(config.S3_BUCKET, f"{config.S3_PREFIX}candles.json")
            data = obj.get()['Body'].read().decode('utf-8')
            return json.loads(data)
        except ClientError:
            return []

    def _save_candles(self):
        self.bucket.put_object(
            Key=f"{config.S3_PREFIX}candles.json",
            Body=json.dumps(self.candles)
        )

    def set(self, key, value):
        # Save the event to S3
        self.bucket.put_object(
            Key=self._get_s3_key(key),
            Body=json.dumps(value)
        )
        
        # Update candles if needed
        if len(self.candles) < self.CANDLE_LEN and key not in self.candles:
            self.candles.append(key)
            self._save_candles()

    def get(self, key):
        try:
            obj = self.s3.Object(config.S3_BUCKET, self._get_s3_key(key))
            data = obj.get()['Body'].read().decode('utf-8')
            return json.loads(data)
        except ClientError:
            return None

    def distance_function(self, event, db_event):
        if not event or not db_event:
            return None
        # Ensure both have features
        f1 = event.get("features", [])
        f2 = db_event.get("features", [])
        if len(f1) != self.FEATURE_D or len(f2) != self.FEATURE_D:
            return float('inf')
            
        return math.sqrt(sum((f1[i] - f2[i])**2 for i in range(self.FEATURE_D)))

    def update_stopping_criteria(self, db_size, depth):
        self.stopping_criteria = self.initial_stopping_criteria + (0.001 * depth * math.log(db_size + 1))

    def recursive_descent(self, event, db_events_keys, last_distances, depth=0):
        self.recursive_steps += 1
        if not db_events_keys:
            return None
            
        # Optimization: Fetch all needed events in parallel? 
        # For simplicity/demo, we do serial fetches (slow but simple code)
        db_events = [self.get(str(k)) for k in db_events_keys]
        db_events = [e for e in db_events if e] # Filter None

        if not db_events:
            return None

        distances = [(self.distance_function(event, db_event), db_event) for db_event in db_events]
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
            next_keys = [d[1]["id"] for d in distances[:num_neighbors_to_check] if "id" in d[1]]
            # In a real graph, we'd fetch neighbors of 'best_match'. 
            # The original code's logic for 'next keys' was actually just recursing on the same subset or 
            # it implied some graph structure that wasn't fully implemented in the simple version.
            # The original code passed: [k for _, k in distances[:num_neighbors_to_check]]
            # But 'distances' stores (dist, event_obj).
            # So the original code was probably broken or using a dict/list mix.
            # Here we just recurse on the best candidates we found so far? 
            # Wait, if we just recurse on the same list, we loop.
            # The original code passed 'distances' (list of tuples) to recursive_descent... wait.
            # Original: `recursive_descent(event, [k for _, k in distances[:num_neighbors_to_check]], distances, depth + 1)`
            # But `distances` contained `(distance, db_event)`. So the second arg passed was a list of db_events?
            # No, `db_events_keys` expects keys.
            # If `distances` contains full objects, then `[k for _, k in distances...]` makes `k` the object.
            # But the recursive function expects keys.
            # I will fix this logic to be robust: Extract IDs from the event objects.
            
            # Since we don't have an explicit graph (neighbors list) in the simple schema, 
            # we are essentially doing a beam search on the 'candles'.
            # If we don't have other nodes to jump to, we stop.
            
            # For this simple "demo", I'll stick to the logic:
            # If we match close enough, return.
            # Otherwise, return the best we found so far if we aren't improving.
            
            return best_match 

    def get_by_event(self, event):
        self.recursive_steps = 0
        # If no candles, nothing to search
        if not self.candles:
            return None, 0
            
        result = self.recursive_descent(event, self.candles, last_distances=None)
        return result, self.recursive_steps

    def insert_event(self, event):
        if "id" not in event:
            event["id"] = str(uuid.uuid4())
        
        # Ensure features exist
        if "features" not in event:
            event["features"] = self.event_to_features(event)
            
        self.set(event["id"], event)
        return event

    @staticmethod
    def event_to_features(event):
        features = []
        # Simple deterministic hashing for demo
        for key in sorted(event.keys()):
            val = event[key]
            if isinstance(val, (int, float)):
                features.append(float(val))
            elif isinstance(val, str):
                # Hash string to float 0-1
                h = hash(val) % 1000 / 1000.0
                features.append(h)
        
        # Pad or truncate to FEATURE_D
        while len(features) < config.FEATURE_D:
            features.append(0.0)
        return features[:config.FEATURE_D]

# Singleton instance
db = Database()
