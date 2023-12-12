import pymavlink
print(pymavlink.__doc__)
print('hi')
import time
import csv
import matplotlib.pyplot as plt
from drawnow import drawnow
import numpy as np

# Import mavutil
from pymavlink import mavutil

master = mavutil.mavlink_connection('udpin:127.0.0.1:57331')

#master.wait_heartbeat()
#while True:
#    try:
##    except:
 #       pass
 #   time.sleep(0.1)
mxdepth=8

mndepth=0
ms =0
plt.ion()
fig, ax = plt.subplots()
plt.ion()
fig2, ax2 = plt.subplots()
#colors = np.flipud(plt.cm.rainbow(range(1,255)))
#colors = np.flipud(plt.cm.gist_earth(range(1,255)))
colors = np.flipud(plt.cm.terrain(range(1,255)))
fo=open('MavData.txt','w+')

while True:
    msg = master.recv_match()

    if not msg:
        continue
    elif msg.get_type() == 'GLOBAL_POSITION_INT':
        print("\n\n*****Got message: %s*****" % msg.get_type())
        #print("Message: %s" % msg)
        #print("\nAs dictionary: %s" % msg.to_dict())
        # Armed = MAV_STATE_STANDBY (4), Disarmed = MAV_STATE_ACTIVE (3)
        lat=msg.lat
        print(str(lat))
        lng=msg.lon
        print(str(lng))
        gp=1
    elif msg.get_type() == 'RANGEFINDER':
        gr=1
        print("\n\n*****Got message: %s*****" % msg.get_type())

        dist=msg.distance
        print(str(dist))
        cdist=   min(int(round((254./mxdepth)*(dist))),253)
        cdist=cdist-int(round(mndepth*254/mxdepth));
        if cdist <1:
            cdist=1
        #line1,=ax.plot(lng, lat, **{'color': 'lightsteelblue', 'marker': 'o'})
        line1,=ax.plot(lng, lat, color=colors[cdist] ,marker= 'o')
        line1.set_xdata(lng)
        line1.set_ydata(lat)
        fig.canvas.draw()
        fig.canvas.flush_events()
        ms=ms+1
        line2,=ax2.plot(ms,dist, color=colors[cdist] ,marker= 'o')
        line2.set_xdata(ms)
        line2.set_ydata(dist)
        fig2.canvas.draw()
        fig2.canvas.flush_events()
        fo.write((str(lng/1e7)+ ',' +str(lat/1e7)+ ','+str(dist) +'\n') )
        fo.flush()
