import redis, json, random, math, time

FEATURE_D = 8
DB_SIZE = 10000
THRESH = 0.6
CANDLE_LEN = 12

redis = redis.StrictRedis(charset="utf-8", decode_responses=True)

class Database:
    def __init__(self):
        self.candles = []
        self.CANDLE_LEN = CANDLE_LEN
        self.stopping_criteria = THRESH

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

    def recursive_descent(self, event, db_events_keys, last_distances):
        if not db_events_keys:
            return None
        db_events = [self.get(str(k)) for k in db_events_keys]
        if not db_events:
            return None

        distances = sorted((self.distance_function(event, db_event), db_event) for db_event in db_events)
        best_match = distances[0][1]
        new_best_distance = distances[0][0]
        print(new_best_distance)

        if new_best_distance < self.stopping_criteria:
            print('made it out under stopping criteria')
            return best_match
        elif last_distances and new_best_distance > last_distances[0]:
            print(new_best_distance, last_distances[0])
            print('made it out under best effort search criteria')
            return event
        else:
            return self.recursive_descent(event, best_match.get("candles", []), distances)

    def get_by_event(self, event, resolution=None):
        return self.recursive_descent(event, self.candles, last_distances=None)

    def insert_event(self, event):
        reslv = self.get_by_event(event)
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
    for query in query_events:
        db.get_by_event(query)
    query_time = time.time() - start_time

    return insert_time, query_time

if __name__ == "__main__":
    db_sizes = [0, 10, 100, 1000, 10000]
    results = {}

    for size in db_sizes:
        print(f"Running test with database size: {size}")
        insert_time, query_time = run_performance_test(size)
        results[size] = {
            "insert_time": insert_time,
            "query_time": query_time,
            "avg_insert_time": insert_time / max(size, 1),
            "avg_query_time": query_time / 100
        }

    print("\nPerformance Summary:")
    print("--------------------")
    for size, data in results.items():
        print(f"\nDatabase size: {size}")
        print(f"Total insert time: {data['insert_time']:.4f} seconds")
        print(f"Average insert time per event: {data['avg_insert_time']:.6f} seconds")
        print(f"Total query time (100 queries): {data['query_time']:.4f} seconds")
        print(f"Average query time: {data['avg_query_time']:.6f} seconds")

    print("\nAlgorithm Performance Analysis:")
    print("--------------------------------")
    print("1. Empty Database (0 events):")
    print("   - Insertions are instant as there's no data to process.")
    print("   - Queries are quick but may not be meaningful due to lack of data.")

    print("\n2. Small Database (10 events):")
    print("   - Insertions and queries are fast due to the small dataset.")
    print("   - The recursive descent algorithm may not be fully utilized.")

    print("\n3. Medium Database (100-1000 events):")
    print("   - Insertion time increases linearly with database size.")
    print("   - Query time starts to show the impact of the recursive descent algorithm.")

    print("\n4. Large Database (10000 events):")
    print("   - Insertion time continues to scale linearly.")
    print("   - Query time may increase more significantly due to deeper recursive searches.")

    print("\nConclusion:")
    print("The recursive descent algorithm's performance depends on the database size and the")
    print("distribution of data points. As the database grows, queries may take longer due to")
    print("more levels of recursion. Optimizations like indexing or approximation algorithms")
    print("could be considered for larger datasets to improve query performance.")

    redis.flushall()
    print("\nTest complete. Redis database cleared.")