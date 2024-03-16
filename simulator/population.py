import json, uuid, random
import numpy as np

xmax, ymax = 1877, 914

with open("urls_sample.txt") as f:
    pages = f.readlines()
    pages = [p.rstrip() for p in pages]
with open("streets.txt") as f:
    streets = f.readlines()
    streets = [s.rstrip() for s in streets]

ZIP = "80226"
N_HOUSEHOLDS = 25000
CITY = "LAKEWOOD"
lat_max, lat_min, lon_max, lon_min = 39.81, 39.61, -105.08, -105.10

ADDRESSES = [str(random.randint(0,999)) + " " + random.choice(streets) for _ in range(N_HOUSEHOLDS)] 
IPS = [i for i in range(N_HOUSEHOLDS)]
random.shuffle(IPS)
DEVICE_TYPES = ["iphone", "android phone", "ipad", "android tablet", "Mac laptop", "WINDOWS laptop", "Linux laptop", "connected TV", "other device type"]
IMP_TYPES = ["video", "250x320", "468x60"]

class Device():
    def __init__(self,user):
        self.user=user
        self.type = random.choice(DEVICE_TYPES)
        self.device_id =  str(uuid.uuid4())

    def make_device_payload(self, location=None):
        if location:
            payload = {"ip" : location.ip}
        else:
            payload = {}
        return payload

class User():
    def __init__(self,household):
        self.household=household
        self.N_DEVICES = random.randint(1,5)
        self.devices = [Device(self) for _ in range(self.N_DEVICES)] 
        self.pages = [random.choice(pages) for p in range(random.randint(10,20))]
        
        # we store the canonical_id in the db, but don't use for matching or learning.
        self.canonical_id = uuid.uuid4()

        self.ids = {
                "base1" : str(random.randint(0,1E10)),
                "hash1" : str(uuid.uuid4()), 
                "hash2" : str(uuid.uuid4()),
                "geo1" : self.household.get_geo()
                }
        self.public_ids = {
                "pubcid.org" : str(uuid.uuid4()),
                "adserver.org" : str(uuid.uuid4()),
                "id5-sync.com" : str(uuid.uuid4()),
                "liveramp.com" : str(uuid.uuid4()),
                }

    def make_user_payload(self):
        # about 1/4 of the time, the `user` object is empty
        # still need to add user.geo and component some of the time

        n_chosen = random.choice([0,1,2,3])
        if n_chosen == 0:
            payload = {}
        elif n_chosen == 1:
            payload = {"id": self.ids['hash1']}
        elif n_chosen > 1:
            payload = {}
            ext = random.choice([{},{"eids":[]}])
            if ext:
                payload["ext"] = ext
                sources = [p for p in list(self.public_ids.keys()) if random.random() > 0.5] 
                for source in sources:
                    payload["ext"]["eids"].append(
                        {
                        'source' : source, 
                        'uids' : self.public_ids[source]
                        })
            else:
                payload = {"id" : random.choice(list(self.ids.values()))} # sometimes just return a random id in place of user.ext 
        return payload

class Household():
    def __init__(self, population):
        self.population = population
        self.address = random.choice(ADDRESSES) 
        self.lat = random.uniform(lat_max, lat_min)
        self.lon = random.uniform(lon_max, lon_min)
        self.ip = IPS[-1]
        del IPS[-1]
        self.users = [User(self) for _ in range(random.randint(1,5))]

    def get_geo(self):
        return random.choice([
            {"zip": ZIP, "lat": round(self.lat, 2), "lon": round(self.lon, 2), "city": CITY, "country": "USA", "region": "CO", "metro": "303", "type": 2},
            {"zip": ZIP, "lat": round(self.lat, 4), "lon": round(self.lon, 4), "city": CITY, "country": "USA", "region": "CO", "metro": "303", "type": 2},
            {"lat": round(self.lat, 2) , "lon": round(self.lon, 2), "country": "USA", "type": 2}])

class Population():
    def __init__(self, _zip, N_HOUSEHOLD):
        self.zip = _zip
        self.households = [Household(self) for _ in range(N_HOUSEHOLD)]

    def generate_event(self):
        event = {}
        household = random.choice(self.households)
        user = random.choice(household.users)
        device = random.choice(user.devices)

        event['lat'] = household.lat
        event['lon'] = household.lon
        event['imp'] = []
        event['site'] = {'page':random.choice(user.pages)}
        event['user'] = user.make_user_payload()
        event['device'] = device.make_device_payload(location=random.choice([household, None])) 
      
        event['canonical_id'] = user.canonical_id
        return event

if __name__ == "__main__":
    pop = Population(_zip=ZIP, N_HOUSEHOLD=N_HOUSEHOLDS)
     

