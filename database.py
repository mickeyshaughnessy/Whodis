import redis, json, random, math, time

FEATURE_D = 8
DB_SIZE = 300000
INITIAL_THRESH = 0.6
CANDLE_LEN = 12

redis = redis.StrictRedis(charset="utf-8", decode_responses=True)

class Database:
    def __init__(self):
        self.candles = []
        self.CANDLE_LEN = CANDLE_LEN
        self.initial_stopping_criteria = INITIAL_THRESH
        self.stopping_criteria = self.initial_stopping_criteria
        self.recursive_steps = 0
        self.stopping_criteria_hits = 0

    def set(self, key, value, _hash="REDHASH_TEST"):
        if len(self.candles) < self.CANDLE_LEN:
            self.candles.append(key)
        v = json.dumps(value)
        redis.hset(_hash, key, v) if _hash else redis.set(key, v)

    def get(self, key, _hash="REDHASH_TEST"):
        v = redis.hget(_hash, key) if _hash else redis.get(key)
        return json.loads(v) if v else None

    def distance_function(self, event, db_event):
        if not event or not db_event:
            return None
        return math.sqrt(sum((event.get("features")[i] - db_event.get("features")[i])**2 for i in range(FEATURE_D)))

    def update_stopping_criteria(self, db_size, depth):
        """
        Dynamically adjust the stopping criteria based on the current recursion depth and database size.
        As the database grows, increase the stopping criteria threshold to allow for less strict matching.
        """
        self.stopping_criteria = self.initial_stopping_criteria + (0.001 * depth * math.log(db_size + 1))

    def recursive_descent(self, event, db_events_keys, last_distances, depth=0):
        self.recursive_steps += 1
        if not db_events_keys:
            return None
        db_events = [self.get(str(k)) for k in db_events_keys]
        if not db_events:
            return None

        # Calculate distances and filter out None values
        distances = [(self.distance_function(event, db_event), db_event) for db_event in db_events]
        distances = [d for d in distances if d[0] is not None]

        if not distances:
            return None

        # Sort distances
        distances = sorted(distances, key=lambda x: x[0])

        best_match = distances[0][1]
        new_best_distance = distances[0][0]

        # Update the dynamic stopping criteria
        self.update_stopping_criteria(len(db_events_keys), depth)

        if new_best_distance < self.stopping_criteria:
            self.stopping_criteria_hits += 1
            return best_match
        elif last_distances and new_best_distance > last_distances[0]:
            return event
        else:
            # Dynamic number of neighbors to check based on depth
            num_neighbors_to_check = min(5 + depth, len(db_events))  # More neighbors as depth increases
            return self.recursive_descent(event, [k for _, k in distances[:num_neighbors_to_check]], distances, depth + 1)

    def get_by_event(self, event, resolution=None):
        self.recursive_steps = 0
        result = self.recursive_descent(event, self.candles, last_distances=None)
        return result, self.recursive_steps

    def insert_event(self, event):
        reslv = self.get_by_event(event)[0]
        key = reslv.get("id")
        self.set(key, reslv)

def run_performance_test(db_size):
    db = Database()
    redis.flushall()

    # Generate and insert events
    events = [{"features": [random.random() for _ in range(FEATURE_D)]} for _ in range(db_size)]
    start_time = time.time()
    for i, event in enumerate(events):
        db.set(i, event)
    insert_time = time.time() - start_time

    # Perform queries
    query_events = [{"features": [random.random() for _ in range(FEATURE_D)]} for _ in range(100)]
    start_time = time.time()
    total_steps = 0
    total_error = 0
    for query in query_events:
        result, steps = db.get_by_event(query)
        total_steps += steps
        if result:
            total_error += db.distance_function(query, result)
    query_time = time.time() - start_time

    return insert_time, query_time, total_steps / 100, total_error / 100, db.stopping_criteria_hits

if __name__ == "__main__":
    db_sizes = [0, 10, 100, 1000, 10000, 100000, 200000, 300000]
    results = {}

    for size in db_sizes:
        print(f"Running test with database size: {size}")
        insert_time, query_time, avg_steps, avg_error, stopping_hits = run_performance_test(size)
        results[size] = {
            "insert_time": insert_time,
            "query_time": query_time,
            "avg_insert_time": insert_time / max(size, 1),
            "avg_query_time": query_time / 100,
            "avg_recursive_steps": avg_steps,
            "avg_error": avg_error,
            "stopping_criteria_percentage": (stopping_hits / 100) * 100
        }

    print("\nPerformance Summary:")
    print("--------------------")
    for size, data in results.items():
        print(f"\nDatabase size: {size}")
        print(f"Total insert time: {data['insert_time']:.4f} seconds")
        print(f"Average insert time per event: {data['avg_insert_time']:.6f} seconds")
        print(f"Total query time (100 queries): {data['query_time']:.4f} seconds")
        print(f"Average query time: {data['avg_query_time']:.6f} seconds")
        print(f"Average recursive steps: {data['avg_recursive_steps']:.2f}")
        print(f"Average error: {data['avg_error']:.6f}")
        print(f"Stopping criteria hit percentage: {data['stopping_criteria_percentage']:.2f}%")

    print("\nTest complete. Redis database cleared.")
    redis.flushall()
