# px4_comm.py
# communicate with px4: send/receive messages

from pymavlink import mavutil
import time
import threading
import queue 
from collections import deque 
import csv
import datetime
import sys
import os

import serial.tools.list_ports

### check comm port availability 

# List all available COM ports
ports = serial.tools.list_ports.comports()

deviceList = []
for port in ports:
    #print(f"Device: {port.device}")
    deviceList.append(port.device)

# queue for data; type of data structure 
dataQ1 = queue.Queue() # FIFO: first-in, first-out 
dataQ2 = queue.Queue() # FIFO: first-in, first-out 

#deque;  stack data structure
de = deque() # add/remove elements from both ends; FIFO and LIFO (last-in, first-out)

# set mavlink dialect
mavutil.set_dialect("development")

# CSV write lock for thread safety
csv_lock = threading.Lock()

########################
# # Start a listening connection
connection1 = None
connection2 = None

# loop through available devices
# for dev in deviceList: 

if len(deviceList) == 2:
    #try both connections

    # Try Connection 1
    try: 
        connection1 = mavutil.mavlink_connection(device=deviceList[0], baud=57600)
        connection1.wait_heartbeat(timeout=5)  
        print("Connection 1: Heartbeat from system (system %u component %u)" % 
            (connection1.target_system, connection1.target_component))
    except Exception as e:
        print(f"Connection 1 {deviceList[0]} failed: {e}")
        connection1 = None

    # Try Connection 2 
    try: 
        connection2 = mavutil.mavlink_connection(device=deviceList[1], baud=57600)
        connection2.wait_heartbeat(timeout=5)  
        print("Connection 2: Heartbeat from system (system %u component %u)" % 
            (connection2.target_system, connection2.target_component))
    except Exception as e:
        print(f"Connection 2 {deviceList[1]} failed: {e}")
        connection2 = None

    # Check if at least one connection succeeded
    if connection1 is None and connection2 is None:
        print("ERROR: Both connections failed! Exiting...")
        sys.exit(1)

    print(f"\nActive connections: {deviceList[0]} = {connection1 is not None}, {deviceList[1]} = {connection2 is not None}\n")

elif len(deviceList) == 1:
    # try if only one connection available 

    # Try Connection 1
    try: 
        connection1 = mavutil.mavlink_connection(device=deviceList[0], baud=57600)
        connection1.wait_heartbeat(timeout=5)  
        print("Connection 1: Heartbeat from system (system %u component %u)" % 
            (connection1.target_system, connection1.target_component))
    except Exception as e:
        print(f"Connection 1 {deviceList[0]} failed: {e}")
        connection1 = None

    print(f"\nActive connections: {deviceList[0]}={connection1 is not None}\n")

else: 
    print('ERROR: No avaialble connections. Check if usbs are plugged in. Exiting...')
    sys.exit(1)        


############
# sensor_avs message ID
message_id = 297 #292

if connection1:
    message1 = connection1.mav.command_long_encode(   
            connection1.target_system,  # Target system ID
            connection1.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
            0,  # Confirmation
            message_id,   # param1: Message ID to be streamed
            0, # param2: Interval in microseconds
            0,0,0,0,0)
    print(message1)

    # # Send the COMMAND_LONG
    connection1.mav.send(message1)

    msg = connection1.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
    print(msg) 
    print('')

if connection2:
    message2 = connection2.mav.command_long_encode(   
            connection2.target_system,  # Target system ID
            connection2.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
            0,  # Confirmation
            message_id,   # param1: Message ID to be streamed
            0, # param2: Interval in microseconds
            0,0,0,0,0)
    print(message2)

    # # Send the COMMAND_LONG
    connection2.mav.send(message2)

    msg = connection2.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
    print(msg) 
    print('')

# create directory to store logging data
dirName = 'sensor_avs_logging_data'

# Create the directory
try:
    os.mkdir(dirName)
    print(f"Directory '{dirName}' created successfully.")
except FileExistsError:
    print(f"Directory '{dirName}' already exists.")

# ------ write to CSV (logging) ------

fieldnames = ['node_id','time_utc_usec', 'active_intensity', 'azimuth', 'elevation', 'heading', 'north', 'east', 'down']
timestamp_str = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
csv_file_name = f"{timestamp_str}.csv"

# Open CSV once at start (append mode)
csv_file = open(os.path.join(dirName,csv_file_name), mode='a', newline='')
csv_writer = csv.writer(csv_file)
csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

# Write header only if file is empty
if csv_file.tell() == 0:
    csv_writer.writeheader()  

def set_timer():
    # Record start time for 1-minute timer
    start_timer = time.time()
    end_timer = start_timer + 10  # 1 minute from now

    print(f"Collecting data for 1 hour...")
    print(f"Data collection start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_timer))}")

    return end_timer

#------------------------------------------------------------------------------
# Time synchronization thread
def sync_time(end_timer):
    """Send SYSTEM_TIME messages to both flight controllers"""

    while time.time() < end_timer: 
        # Get current UTC time in microseconds
        time_unix_usec =  int(time.time() * 1e6)
        #print("system time: ", time_unix_usec)
        # readable_time = datetime.fromtimestamp(time_unix_usec/1e6)
        # print(readable_time)

        # Send to both connections
        if connection1:
            connection1.mav.system_time_send(time_unix_usec, 0)

        if connection2:
            connection2.mav.system_time_send(time_unix_usec, 0)

        time.sleep(1.0)  # Send at 1 Hz


#data acquisition thread
def getFPV_data1(end_timer):
    
    """thread for connection 1"""
    
    if not connection1:
        return
    
    while  time.time() < end_timer: #True:        
        # recv_match returns one mavlink message  
        # returns only the next message that arrives; one msg type per call 
        # Different message types arrive at different frequencies
          
        msg = connection1.recv_match(type='SENSOR_AVS_LITE_EXT', blocking=True)       #,timeout=1.0

        #check msg 
        if msg: 
            t = msg.time_utc_usec
            id = msg.device_id
            act = msg.active_intensity
            az = msg.azimuth_deg
            el = msg.elevation_deg

            yaw = msg.yaw
            north = msg.north
            east = msg.east
            down = msg.down

        dataQ1.put((t,id,act,az,el,yaw,north,east,down))
            

        #  Thread-safe CSV write
        #  automatically acquires and releases a lock 
        with csv_lock:
            csv_writer.writerow({'node_id': id,'time_utc_usec': t,'active_intensity': act, 'azimuth': az, 'elevation': el, 'heading': yaw, 'north': north, 'east': east,'down': down})
            csv_file.flush()  #if programs stopped, will save last few rows

    else:
        csv_file.close()


# data acquisition thread
def getFPV_data2(end_timer):
    
    """thread for connection 2"""
        
    if not connection2:
        return

    while  time.time() < end_timer:
        msg = connection2.recv_match(type='SENSOR_AVS_LITE_EXT', blocking=True)

        if msg:
            # connection.messages is a dictionary that stores the LAST received message of each type (Which is an issue)
            # potentially storing old data in csv

            yaw = msg.yaw   
            # pitch1 = msg.pitch                                      
            # roll1 = msg.roll 

            north = msg.north  # N
            east = msg.east  # E
            down = msg.down  # -D 

            t = msg.time_utc_usec #timestamp #timestamp_sample
            id = msg.device_id
            act= msg.active_intensity 
            az = msg.azimuth_deg
            el = msg.elevation_deg

        dataQ2.put((t,id,act,az,el,yaw,north,east,down))

        # Thread-safe CSV write
        with csv_lock:
            csv_writer.writerow({'node_id': id,'time_utc_usec': t,'active_intensity': act, 'azimuth': az, 'elevation': el, 'heading': yaw, 'north': north, 'east': east,'down': down})
            csv_file.flush()  #if programs stopped, will save last few rows`

    else:
        csv_file.close()


def printData():
        # ---------print data  ----------------------
    # Get data from queue 1 if available
    if connection1:
        try:
            t, id, act, az,el, yaw, north, east, down = dataQ1.get_nowait()
            print("t:", t, " id:", id, " act_int:", act, " az:", az, " elevation:",el, ' heading:', yaw, ' north:', north, ' east:', east,' down:', down)
        except queue.Empty:
            pass  
    
    # Get data from queue 2 if available
    if connection2:
        try:
            t, id, act, az, el,yaw, north, east, down = dataQ2.get_nowait()
            print("t:", t, " id:", id, " act_int:", act, " az:", az,  " elevation:",el, ' heading:', yaw, ' north:', north, ' east:', east,' down:', down)
        except queue.Empty:
            pass  
                                

# -------- threads ---------
#if connection1 or connection2:
end_timer = set_timer()
threading.Thread(target=sync_time,args=(end_timer,), daemon=True).start() 
if connection1: 
    threading.Thread(target=getFPV_data1,args=(end_timer,), daemon=True).start()
if connection2:
    threading.Thread(target=getFPV_data2,args=(end_timer,), daemon=True).start()

while time.time() < end_timer: #True:
    printData()
    time.sleep(0.01)
