from navigation.rc import RCLib
import time
import navigation.imu as imu
from navigation.log import *

log = LogLib()
rc = RCLib(log)

rc.setmode('MANUAL')

rc.disarm()
