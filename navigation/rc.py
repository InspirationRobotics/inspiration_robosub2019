# Import mavutil
import time
import imu
from pymavlink import mavutil
import math

# Create the connection

class RCLib:

    def __init__(self):
        try: 

            self.master = mavutil.mavlink_connection(
                '/dev/ttyACM0',
                baud=115200)

            self.master.wait_heartbeat()

        except Exception as e:

            print(e)
        
    # This function is responsible for sending RC channel overrides
    def set_rc_channel_pwm(self, id, pwm=1500):
        
        if id < 1:
            print("Channel does not exist.")
            return
    
        # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
        if id < 9:
            
            rc_channel_values = [65535 for _ in range(8)]
            rc_channel_values[id - 1] = pwm
            self.master.mav.rc_channels_override_send(
                self.master.target_system,                # target_system
                self.master.target_component,             # target_component
                *rc_channel_values)

    def raw (self, id, pwm=1900) :

        if (id == "pitch") :

            self.set_rc_channel_pwm(1, pwm)
            
        if (id == "roll") :

            self.set_rc_channel_pwm(2, pwm)

        if (id == "throttle") :

            self.set_rc_channel_pwm(3, pwm)

        if (id == "yaw") :

            self.set_rc_channel_pwm(4, pwm)

        if (id == "forward") :

            self.set_rc_channel_pwm(5, pwm)

        if (id == "lateral") :

            self.set_rc_channel_pwm(6, pwm)
            
    def arm (self) :
    
        self.master.arducopter_arm()
        
    def throttle (self, unit, value, power) :
	
	pwm = 1500 + (400 * power)
	
	if unit == "time" :

	    runtime = time.time() + value
	    while runtime > time.time() :
	        self.raw("throttle", pwm)
            self.raw("throttle", 1500)

    def forwardAngle (self, unit, value, power, angle) :
        
	if unit == "time" :
            
	    self.setmode('ALT_HOLD')
	    pwm = 1500 + (400 * power)
	    runtime = time.time() + value
            while runtime > time.time() :
                self.raw("forward", pwm)
                print(runtime - time.time())
    
            self.raw("forward", 1500)
    	    self.setmode('MANUAL')
 
		
    def forward (self, unit, value, power) :
        
	if unit == "time" :
            
	    self.setmode('ALT_HOLD')
	    pwm = 1500 + (400 * power)
	    runtime = time.time() + value
            while runtime > time.time() :
                self.raw("forward", pwm)
                print(runtime - time.time())

            self.raw("forward", 1500)
    	    self.setmode('MANUAL')
    
    def deg (self) :

        print(imu.getDeg(self.master)) 

    def yaw (self, unit, value, power) :

        power = power * (value/abs(value))
    
        pwm = 1500 + (400 * power)
    
        if unit == "time" :
   
            runtime = time.time() + value
            while runtime > time.time() :
    
                self.raw("yaw", pwm)
    
            self.raw("yaw", 1500)
    
        if unit == "imu" :

            start = imu.getDeg(self.master)
            print('start angle: %s' % start)

            end = start + value
            offset = 0
            flag = 0
            
            if value > 0 :

                if (end > 360) :

                    offset = 360
                    
                self.raw("yaw", pwm)
                while imu.getDeg(self.master) + (offset * flag) < end:
                    #print('Loop 1')
                    pwm = 1500 + (end - (imu.getDeg(self.master) + (offset * flag)))*0.5 + 100
                    print ('pwm = %d') % pwm

                    if imu.getDeg(self.master) < (start - 10):
                        flag = 1

                    self.raw("yaw", pwm)
                    #print(imu.getDeg(self.master))
                    #print(time.time())
                self.raw("yaw", 1500)
    
            if value < 0 :

                if (end < 0) :

                    offset = -360

                self.raw("yaw", pwm)
                while imu.getDeg(self.master) + (offset * flag) > end:

                    pwm = 1500 - ((imu.getDeg(self.master) + (offset * flag)) - end)*0.5 - 100

                    if imu.getDeg(self.master) > (start + 10):
                        flag = 1

                    self.raw("yaw", pwm)
                    #print(imu.getDeg(self.master))

                self.raw("yaw", 1500)

            #print('before delay')
	    #print(imu.getDeg(self.master))
            #r = time.time() + 20
	    #while (r > time.time()):
		#print(imu.getDeg(self.master)) 

            #time.sleep(10) 
	    #print('after delay')
	    #print(imu.getDeg(self.master))
            
            print('Expected End angle: %s' % end)
            print('Actual End angle: %s' % imu.getDeg(self.master))

    def getDeg (self) :
        r = imu.getDeg(self.master)
        print(r)
        return imu.getDeg(self.master) 
                  
    def lateral (self, unit, value, power) :

        if unit == "time" :

            self.setmode('ALT_HOLD')
            pwm = 1500 + (400 * power)
            runtime = time.time() + value
            while runtime > time.time() :

                self.raw("lateral", pwm)
                print(runtime - time.time())

            self.raw("lateral", 1500)
            self.setmode('MANUAL')
    
    def killall (self) :
    
        self.set_rc_channel_pwm(1, 1500)
        self.set_rc_channel_pwm(2, 1500)
        self.set_rc_channel_pwm(3, 1500)
        self.set_rc_channel_pwm(4, 1500)
        self.set_rc_channel_pwm(5, 1500)
        self.set_rc_channel_pwm(6, 1500)
        
    def setmode (self, mode_val) :
    
        mode = mode_val
        mode_id = self.master.mode_mapping()[mode]
        self.master.mav.set_mode_send(
                self.master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                mode_id)
        
    def imu_turn (self, angle):

        #TURN_THRESHOLD = 3
        TURN_THRESHOLD = 3
        self.setmode('ALT_HOLD')
        #error = angle - self.getDeg()

        print(self.getDeg())
        print("target = ", angle)
        
        while (abs(self.getError(angle)) > TURN_THRESHOLD):
            
            pwm = self.getSteer(self.getError(angle))
            print('speed: ', pwm)
            self.raw('yaw', pwm)
            
        self.raw('yaw', 1500)

                
    def getError(self, angle):
        error = angle - self.getDeg()
        return error

    def getSteer (self, error):
        kP = 0.015
        #kP = 0.05
        end_speed = abs(kP*error)
        #final_speed = np.clip(end_speed, 0.1, 1)
        #converted_speed = 1500 + (end_speed*400)
        if (end_speed > 0.25):
            final_speed = 0.25
        elif (end_speed < 0.08):
            final_speed = 0.08
        else:
            final_speed = end_speed


        if (error > 0):
            #turn right
            return_speed = 1500 + (400*final_speed)
        else:
            return_speed = 1500 - (400*final_speed)
            
            
        return return_speed

    def move_dist(self, distance_in, speed):
        DISTANCE_CONSTANT = 48.181818
        time = (distance_in)/(speed*DISTANCE_CONSTANT)

        self.forward('time', time, speed)
