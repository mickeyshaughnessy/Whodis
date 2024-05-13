# This script simulates a single zip code's bid stream data
import matplotlib.pyplot as plt
#plt.ion()
import numpy as np
import random, time, requests, json
from population import Population

API_URL = "http://0.0.0.0:8050/resolve"
class Api():
    def __init__(self):
        self.api_url = API_URL

    def query(self, event):
        try:
            resp = requests.post(self.api_url, json=event)
            resp = resp.json()
        except:
            resp = "{}" 
        return resp

# bidder:
BPORT = "8020"
bidder_url = "http://0.0.0.0:%s/bid" % BPORT

def fire(event):
    resp = requests.post(bidder_url, json=event)
    return resp

def tlli(lat, lon):
    # translate_lat_lon_to_img
    x_max, y_max = 1877, 914
    x_min, y_min = 0,0
    lat_max, lat_min, lon_max, lon_min = 39.81, 39.61, -105.08, -105.10
    x = (lat - lat_min) * ((x_max - x_min) / (lat_max - lat_min))
    y = (lon - lon_min) * ((y_max - y_min) / (lon_max - lon_min))
    return x,y


if __name__ == "__main__":
    # Define the frequency of events.
    N_EVENTS_PER_SECOND = 10 # 
    N_millisec = 1.0 / N_EVENTS_PER_SECOND * 1000
    
    population = Population(_zip="80226", N_HOUSEHOLD=250)

    map_img = plt.imread('map.png')
    plt.figure()  # Create a new figure for each iteration
    api = Api()
    xs, ys = [], []
    # Run a loop:
    while True:

        start = int(time.time() * 1000)  #ms
        event = population.generate_event()
        r = api.query(event)
        #resp = r.json()
        #correct = resp.get("canonical_id") == event.get("canonical_id")

        #print(event, correct)
        with open('sim.out', 'a') as fout:
            fout.write(json.dumps(event) + "\n")
        #fire(event)
        
        event = json.loads(event)
        print(event)
        ## plot ##
        plt.imshow(map_img)

        ##################
        x, y = tlli(event["lat"], event["lon"])
        xs.append(x)
        ys.append(y)
      
        # initially all red, eventually all green
        if random.random() < 0.1:
            plt.scatter(xs, ys, color='red', marker='x')
            plt.draw()  # Update the plot
            plt.show()
        #plt.pause(0.001)


        elapsed = int(time.time() * 1000) - start
        if elapsed < N_millisec:
            print('sleeping for %f seconds' % ((N_millisec - elapsed)/1000.0))
            time.sleep((N_millisec - elapsed)/1000.0)
         
