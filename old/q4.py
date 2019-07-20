from navigation.rc import RCLib
from navigation.ac import ACLib
import time
import navigation.imu as imu

rc = RCLib()
ac = ACLib()

rc.setmode('MANUAL')

rc.arm()

print(rc.getDeg())

# global "origin" parameter
START = 239
DEPTH_SEC = 5.2
SEC_PER_METER = 1
GATECENTER = 2500
def leftAlign(value) :
    pingReturn = ac.get_distance_fwd()
    wallDist = pingReturn[0]
    confidence = pingReturn[1]
    counter = 0
    while ((confidence < 70) and (counter < 50)):
        pingReturn = ac.get_distance_fwd()
        wallDist = pingReturn[0]
        confidence = pingReturn[1]
        counter = counter + 1
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
    while ((confidence < 70) and (counter < 50)):
        pingReturn = ac.get_distance_right()
        wallDist = pingReturn[0]
        confidence = pingReturn[1]
        counter = counter + 1
    print 'wall' , wallDist 
    print 'counter ' , counter 
    diff =   wallDist - value
    print 'Laterl diff ' , diff
    rc.lateralDist(diff)


# depth hold and go down
rc.setmode('ALT_HOLD')
rc.throttle("time", DEPTH_SEC, -0.25)

# align with the origin 
rc.imu_turn(START)

rc.forward("time", 10, 0.35)
leftAlign(2400)
rc.imu_turn(START)
rc.forward("time", 10, 0.35)
leftAlign(1500)
rc.imu_turn(START)
rc.forward("time", 13, 0.35)
leftAlign(3600)

rc.imu_turn(START+182)
rc.forward("time", 13, 0.25)
rc.imu_turn(START+182)
rightAlign(2300)
rc.forward("time", 13, 0.35)
rightAlign(2300)
rc.imu_turn(START+182)
rc.forward("time", 10, 0.35)

rc.close()