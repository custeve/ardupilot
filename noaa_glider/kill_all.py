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

time.sleep(3)

print("Kill All Done.")