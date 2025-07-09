#PX4_ULOG.py

# script to read ARES output from the ARKFPV via listener command
# COM 5

# This is for python comms to the COM port with ARKFPV: https://mavlink.io/en/mavgen_python/
# Documentation for the FPV: https://docs.px4.io/main/en/flight_controller/ark_fpv.html


import serial   # pip install pyserial 
import time
from pymavlink import mavutil

# # open port
# serial_port = serial.Serial(port='COM5', baudrate=9600, timeout=1) #115200

# create data structures...  append data in loop
mel_spec = []   # 'mel_intensity'
t = []          # 'time_utc_usec'
az = []         # 'azimuth_deg'
hc = []         # 'histogram_count'
ai = []         # 'active_intensity'

# # str = arduino.readline().decode().strip()
# line = serial_port.readline() #.decode().strip() #'utf-8', errors='ignore'
# print(f"Received: {line}")

# # line = serial_port.readline().decode() #.strip() #'utf-8', errors='ignore'
# # print(f"Received: {line}")


# line2 = serial_port.readline().decode('utf-8', errors='ignore').strip() #'utf-8', errors='ignore'
# print(f"Received: {line2}")

# start connection 
connection = mavutil.mavlink_connection(device= 'COM5', baud=9600) #'/dev/ttyUSB0'

# Wait for the first heartbeat to make sure we're connected
#   This sets the system and component ID of remote system for the link
print("Waiting for heartbeat...")
connection.wait_heartbeat()
#print(f"Heartbeat from system (system {connection.target_system} component {connection.target_component})")
print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

# listens to all MAVLink messages and prints them in real-time.
while True:
    msg = connection.recv_match(blocking=True) #recv_match() waits for the next available mavlink message, parses it, & returns a python object representing the message 
    print(f"[{msg.get_type()}] {msg.to_dict()}")
#     print(msg.get_type())

####
# print(connection.messages)

# for key, value in connection.messages.items():
#     print(f"{key}: {value}")

# msg = connection.recv_match(type='ATTITUDE', blocking=True) #blocking=True: waits until a matching message is received
# print(msg.to_dict())
# print(msg)
# print(msg.get_type())

# msg = connection.recv_match(type='GPS_RAW_INT', blocking=True)
# print(msg.to_dict())

# msg = connection.recv_match(type='SYS_STATUS', blocking=True)
# print(msg.to_dict())

# msg = connection.recv_match(blocking=True)
# print(f"[{msg.get_type()}] {msg.to_dict()}")
# print(msg.get_type())