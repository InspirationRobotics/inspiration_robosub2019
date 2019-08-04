from navigation.rc import RCLib
from navigation.ac import ACLib
import time
import navigation.imu as imu

# global "origin" parameter
A1 = 73
A2 = 100
A3 = 55

D1 = 5
D2 = 2
D3 = 5

MIN_BUOY_DIST = 1
MAX_BUOY_DIST = 6

WALL_DIFF = 3

rec_buoy_dist = 0
DEPTH_SEC = 0.5
SEC_PER_METER = 1
GATECENTER = 2500


rc = RCLib()

ac = ACLib()

rc.setmode('MANUAL')

rc.arm()

print("start")

def check() :

    pingReturn = ac.get_distance_left()
    wallDist1 = pingReturn[0]
    confidence = pingReturn[1]
    counter = 0
    while ((confidence < 30) and (counter < 5)):
        pingReturn = ac.get_distance_left()
        wallDist1 = pingReturn[0]
        confidence = pingReturn[1]
        counter = counter + 1
    print 'wall 1' , wallDist1

    pingReturn = ac.get_distance_right()
    wallDist2 = pingReturn[0]
    confidence = pingReturn[1]
    counter = 0
    while ((confidence < 30) and (counter < 5)):
        pingReturn = ac.get_distance_right()
        wallDist2 = pingReturn[0]
        confidence = pingReturn[1]
        counter = counter + 1
    print 'wall 2' , wallDist2

    if(wallDist1 > wallDist2 + WALL_DIFF):
       rc.raw('yaw', 1440);
       time.sleep(0.3)
       #rc.raw('yaw', 1500)

    if(wallDist2 > wallDist1 + WALL_DIFF):
       rc.raw('yaw', 1560);
       time.sleep(0.3)
       #rc.raw('yaw', 1500)

def leftAlign(value) :

    pingReturn = ac.get_distance_left()
    wallDist = pingReturn[0]
    confidence = pingReturn[1]
    counter = 0
    while ((confidence < 65) and (counter < 10)):
        pingReturn = ac.get_distance_left()
        wallDist = pingReturn[0]
        confidence = pingReturn[1]
        counter = counter + 1
    print 'wall' , wallDist 
    if wallDist > 7000:
        wallDist = 7000
    if wallDist <  1000:
        wallDist = 1000
    print 'wall' , wallDist 
    print 'counter ' , counter 
    diff =  value - wallDist
    print 'Laterl diff ' , diff
    rc.lateralDist(diff)

def rightAlign(value) :
    pingReturn = ac.get_distance_right()
    wallDist = pingReturn[0]
    confidence = pingReturn[1]
    counter = 0
    while ((confidence < 90) and (counter < 50)):
        pingReturn = ac.get_distance_right()
        wallDist = pingReturn[0]
        confidence = pingReturn[1]
        counter = counter + 1
    print 'wall' , wallDist 
    if wallDist > 7000:
        wallDist = 7000
    if wallDist <  1000:
        wallDist = 1000
    print 'wall' , wallDist 
    print 'counter ' , counter 
    diff =   wallDist - value
    print 'Laterl diff ' , diff
    rc.lateralDist(diff)


def lowestSonar(speed) :

    global rec_buoy_dist
    #pwm = 1500 + (0.4*speed*1000)
    if (speed > 0):
        pwm=1560
    else:
        pwm = 1440
    
    rc.raw('yaw', pwm)
    
    prev_val = 0
    current_val = ac.get_distance_forward()[0]
    diff_accum = 0
    diff = 0

    while (abs(diff) >25 or abs(diff_accum) < 1000):
        dist = ac.get_distance_forward()[0]
        conf = ac.get_distance_forward()[1]
        if(conf > 70):
            prev_val =  current_val
            current_val = dist
            diff = abs(current_val-prev_val)
            diff_accum = diff+diff_accum
            rc.raw('yaw', pwm)
        else:
            rc.raw('yaw', pwm)
            pass
        time.sleep(0.01)
        rec_buoy_dist = current_val

    rc.raw('yaw', 1500)


# depth hold and go down
rc.setmode('ALT_HOLD')
rc.throttle("time", DEPTH_SEC, -0.25)

ORIG_HEADING = rc.getDeg()

#buoy
print("Starting Buoy Test")
rc.throttle("time", 1, -0.25)
lowestSonar(0.16)
buoyDist  = rec_buoy_dist

'''buoyDist = buoyDist/2000 + MIN_BUOY_DIST
if buoyDist > MAX_BUOY_DIST:
   buoyDist = MAX_BUOY_DIST 
'''
print(buoyDist)
buoyDist = buoyDist/(1000)
buoyDist = buoyDist/(0.45)
buoyDist = buoyDist + 6
rc.forward("time", buoyDist, 0.32)
print("Done Buoy Test")
"""
rc.forward('time', buoyDist, -0.32)
rc.imu_turn(ORIG_HEADING)

lowestSonar(0.16)
buoyDist  = ac.get_distance_forward()[0]
buoyDist = buoyDist/2000 + MIN_BUOY_DIST
if buoyDist > MAX_BUOY_DIST:
   buoyDist = MAX_BUOY_DIST
rc.forward("time", buoyDist, 0.32)
print("Done Buoy Test")
rc.forward('time', buoyDist, -0.32)
"""

rc.close()

