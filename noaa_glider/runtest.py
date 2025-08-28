#!/usr/bin/env python

import pexpect, time, sys, os
from pymavlink import mavutil

import argparse
parser = argparse.ArgumentParser(description='run glider test')
# parser.add_argument('--mission', type=int, default=0, help='mission number')
parser.add_argument('--no-ui', action='store_true', help='disable UI display')
args = parser.parse_args()

# if args.mission == 0:
#     print("You must specify a mission number")
#     sys.exit(1)

def kill_all():
    os.system("pkill mavproxy 2> /dev/null")
    os.system("pkill -9 mavproxy 2> /dev/null")
    os.system("killall -9 xterm 2> /dev/null")
    os.system("killall -9 gdb 2> /dev/null")
    os.system("killall -9 arduplane 2> /dev/null")

def wait_heartbeat(mav, timeout=10):
    '''wait for a heartbeat'''
    start_time = time.time()
    while time.time() < start_time+timeout:
        if mav.recv_match(type='HEARTBEAT', blocking=True, timeout=0.5) is not None:
            return
    raise Exception("Failed to get heartbeat")    

def wait_mode(mav, modes, timeout=10):
    '''wait for one of a set of flight modes'''
    start_time = time.time()
    last_mode = None
    while time.time() < start_time+timeout:
        wait_heartbeat(mav, timeout=10)
        if mav.flightmode != last_mode:
            print("Flightmode %s" % mav.flightmode)
            last_mode = mav.flightmode
        if mav.flightmode in modes:
            return
    print("Failed to get mode from %s" % modes)
    sys.exit(1)

def wait_time(mav, simtime):
    '''wait for simulation time to pass'''
    imu = mav.recv_match(type='RAW_IMU', blocking=True)
    t1 = imu.time_usec*1.0e-6
    while True:
        imu = mav.recv_match(type='RAW_IMU', blocking=True)
        t2 = imu.time_usec*1.0e-6
        if t2 - t1 > simtime:
            break

kill_all()
os.system("rm -rf logs")
time.sleep(3)

# get location of scripts
testdir = os.path.dirname(os.path.realpath(__file__))
SITL_START_LOCATION = mavutil.location(-35.362938, 149.165085, 585, 354)
WIND = "0,180,0.2"  # speed,direction,variance



#cmd = '../../Tools/autotest/sim_vehicle.py -D -f glider -G -L %s --aircraft test' % location
#cmd = '../Tools/autotest/sim_vehicle.py -D -v ArduPlane -f glider'
cmd = '../Tools/autotest/sim_vehicle.py -D -S 100 -N -v ArduPlane -f glider' # --custom-location=-35.38,149.16,20000.0,45.0'

print('--------------------> Starting MAVPROXY: %s' % cmd)
print()
print()

mavproxy = pexpect.spawnu(cmd, logfile=sys.stdout, timeout=300)

mavproxy.expect('ArduPilot Ready')
mavproxy.expect("Saved")
print('\n\n--------------------> MAVPROXY Started.')
print()
print()

print('--------------------> Connecing MAV...')

mav = mavutil.mavlink_connection('127.0.0.1:14550')

print('\n\n--------------------> Loading Mission.....')

mavproxy.send('param set SIM_SPEEDUP 1\n')
mavproxy.send('wp load glider-pullup-mission.txt\n')
mavproxy.expect('Loaded')

print('\n\n--------------------> Mission Loaded.....')

#wait_mode(mav, ['MANUAL'])

mavproxy.send('param ftp\n')
mavproxy.expect("Saved")

print('\n\n--------------------> Parameters Downloaded.\n\n')


# mavproxy.customise_SITL_commandline(
#             [],
#             model="glider",
#             defaults_filepath="Tools/autotest/default_params/glider.parm",
#             wipe=True)

# mavproxy.set_parameters({
#     "PUP_ENABLE": 1,
#     "SERVO6_FUNCTION": 0, # balloon lift
#     "SERVO10_FUNCTION": 156, # lift release
#     "EK3_IMU_MASK": 1, # lane switches just make log harder to read
# })


mavproxy.send('''
set altreadout 1000
set streamrate 1
set distreadout 0
''')

# mission_parm = "missions/mission%u.parm" % args.mission
if os.path.exists("at_1.parm"):
    mavproxy.send("param load at_1.parm\n")
# if os.path.exists(mission_parm):
#     mavproxy.send("param load %s\n" % mission_parm)
# mavproxy.send("fence load %s\n" % fence)


mavproxy.send('set heartbeat 40\n')
mavproxy.send('param set SIM_SPEEDUP 100\n')
mavproxy.send('arm throttle\n')
mavproxy.expect('armed')

print('\n\n--------------------> Starting Mission.\n\n')
mavproxy.send('\n')
mavproxy.send('auto\n')
#wait_mode(mav, ['AUTO'])
mavproxy.expect("AUTO")
mavproxy.send('servo set 6 2000\n')
# if not args.no_ui:
#     mavproxy.send('module load map\n')
#     mavproxy.send('wp list\n')
#     mavproxy.send('gamslft\n')
#     #mavproxy.send("kml load %s\n" % kmz)




mavproxy.expect("DISARMED",timeout=600)



#mavproxy.send('disarm force\n')

kill_all()


# os.system("ln -f logs/00000001.BIN test_runs/mission%u.bin" % args.mission)
# os.system("ls -l test_runs/mission%u.bin" % args.mission)

