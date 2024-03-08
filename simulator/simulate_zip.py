# This script simulates a single zip code's bid stream data
import matplotlib.pyplot as plt
#plt.ion()
import numpy as np
import time, requests, json
from population import Population


# bidder:
BPORT = "8020"
bidder_url = "http://0.0.0.0:%s/bid" % BPORT

def fire(event):
    resp = requests.post(bidder_url, json=event)
    
if __name__ == "__main__":
    # Define the frequency of events.
    N_EVENTS_PER_SECOND = 4 # (~350k events per day)
    N_millisec = 1.0 / N_EVENTS_PER_SECOND * 1000
    print(N_millisec)
    population = Population(_zip="80226", N_HOUSEHOLD=25000)

    # Run a loop:
    while True:

        start = int(time.time() * 1000)  #ms

        event = population.generate_event()
        
        #resp = api.query(event)

        print(event)
        with open('sim.out', 'a') as fout:
            fout.write(json.dumps(event) + "\n")
        #fire(event)
        
        ## plot ##
        
        map_img = plt.imread('map.png')
        plt.figure()  # Create a new figure for each iteration
        plt.imshow(map_img)
        
        xs, ys = [100, 200], [100, 200]
        #xs.append(event.lat)
        #ys.append(event.lon)
       
        # initially all red, eventually all green
        plt.scatter(xs, ys, color='red', marker='x')
        plt.draw()  # Update the plot
        plt.show()
        #plt.pause(0.001)


        elapsed = int(time.time() * 1000) - start
        if elapsed < N_millisec:
            print('sleeping for %f ms' % ((N_millisec - elapsed)/1000.0))
            time.sleep((N_millisec - elapsed)/1000.0)
         
