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

# sz = Path('Data.csv').stat().st_size
# print(sz)

# queue for data; type of data structure 
dataQ1 = queue.Queue() # FIFO: first-in, first-out 
dataQ2 = queue.Queue() # FIFO: first-in, first-out 

#deque;  stack data structure
de = deque() # add/remove elements from both ends; FIFO and LIFO (last-in, first-out)

# set mavlink dialect
mavutil.set_dialect("development")

########################
# # Start a listening connection
connection1 = None
connection2 = None
#device='/dev/ttyUSB1'
#device='/dev/ttyUSB0'

# Try Connection 1 (COM7)
try: 
    connection1 = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
    connection1.wait_heartbeat(timeout=5)  
    print("Connection 1: Heartbeat from system (system %u component %u)" % 
          (connection1.target_system, connection1.target_component))
except Exception as e:
    print(f"Connection 1 (COM9) failed: {e}")
    connection1 = None

# Try Connection 2 (COM9)
try: 
    connection2 = mavutil.mavlink_connection(device='/dev/ttyUSB1', baud=57600)
    connection2.wait_heartbeat(timeout=5)  
    print("Connection 2: Heartbeat from system (system %u component %u)" % 
          (connection2.target_system, connection2.target_component))
except Exception as e:
    print(f"Connection 2 (COM7) failed: {e}")
    connection2 = None

# Check if at least one connection succeeded
if connection1 is None and connection2 is None:
    print("ERROR: Both connections failed! Exiting...")
    sys.exit(1)

print(f"\nActive connections: COM7={connection1 is not None}, COM9={connection2 is not None}\n")

############
# sensor_avs message ID
message_id = 296 #292

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

    msg1 = connection1.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
    print(msg1) 
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

    msg2 = connection2.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
    print(msg2) 
    print('')

# create directory to store logging data
# Specify the directory name
dirName = 'sensor_avs_logging_data'

# Create the directory
try:
    os.mkdir(dirName)
    print(f"Directory '{dirName}' created successfully.")
except FileExistsError:
    print(f"Directory '{dirName}' already exists.")

# ------ write to CSV (logging) ------

fieldnames = ['node_id','time_utc_usec', 'active_intensity', 'azimuth', 'heading', 'north', 'east', 'down']
timestamp_str = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
csv_file_name = f"{timestamp_str}.csv"

# Check if file exists
# file_exists = os.path.isfile(csv_file_name)
# print(file_exists)

# if file_exists:
#     count = 1
#     csv_file_name =f"sensor_avs_data_{count}.csv"
#     count += 1

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
        #msg = connection1.recv_match(type ='LOCAL_POSITION_NED',blocking=True)  #x,y,z (n,e,d)
        #msg1 = connection1.recv_match(type='SENSOR_AVS_LITE',blocking=True)    
        msg1 = connection1.recv_match(type=['SENSOR_AVS_LITE', 'ATTITUDE', 'LOCAL_POSITION_NED'], 
                                      blocking=True)       
        print(msg1)
        if msg1: 
         
            t1 = connection1.messages['SENSOR_AVS_LITE'].time_utc_usec
            id1 = connection1.messages['SENSOR_AVS_LITE'].device_id
            act1= connection1.messages['SENSOR_AVS_LITE'].active_intensity 
            az1 = connection1.messages['SENSOR_AVS_LITE'].azimuth_deg

            yaw1 = connection1.messages['ATTITUDE'].yaw   
            # pitch1 = connection1.messages['ATTITUDE'].pitch                                      
            # roll1 = connection1.messages['ATTITUDE'].roll 

            north1 = connection1.messages['LOCAL_POSITION_NED'].x  # N
            east1 = connection1.messages['LOCAL_POSITION_NED'].y  # E
            down1 = connection1.messages['LOCAL_POSITION_NED'].z  # -D 

            # yaw1 = msg1.yaw   
            # # pitch1 = msg1.pitch                                      
            # # roll1 = msg1.roll 

            # north1 = msg1.x  # N
            # east1 = msg1.y  # E
            # down1 = msg1.z  # -D 
            
            # t1 = msg1.time_utc_usec #timestamp 
            # id1 = msg1.device_id
            # act1= msg1.active_intensity 
            # az1 = msg1.azimuth_deg
        
        dataQ1.put((t1,id1,act1,az1,yaw1,north1,east1,down1))

        csv_writer.writerow({'node_id': id1,'time_utc_usec': t1,'active_intensity': act1, 'azimuth': az1, 'heading': yaw1, 'north': north1, 'east': east1,'down': down1})
        csv_file.flush()  #if programs stopped, will save last few rows

    else:
        csv_file.close()


# data acquisition thread
def getFPV_data2(end_timer):
    
    """thread for connection 2"""
        
    if not connection2:
        return

    while  time.time() < end_timer:
        msg2 = connection2.recv_match(type=['SENSOR_AVS_LITE', 'ATTITUDE', 'LOCAL_POSITION_NED'], 
                                      blocking=True)

        if msg2:
            
            t2 = connection2.messages['SENSOR_AVS_LITE'].time_utc_usec
            id2 = connection2.messages['SENSOR_AVS_LITE'].device_id
            act2= connection2.messages['SENSOR_AVS_LITE'].active_intensity 
            az2 = connection2.messages['SENSOR_AVS_LITE'].azimuth_deg

            yaw2 = connection2.messages['ATTITUDE'].yaw   
            # pitch1 = connection1.messages['ATTITUDE'].pitch                                      
            # roll1 = connection1.messages['ATTITUDE'].roll 

            north2 = connection2.messages['LOCAL_POSITION_NED'].x  # N
            east2 = connection2.messages['LOCAL_POSITION_NED'].y  # E
            down2 = connection2.messages['LOCAL_POSITION_NED'].z  # -D 

            # yaw2 = msg2.yaw   
            # # pitch1 = msg2.pitch                                      
            # # roll1 = msg2.roll 

            # north2 = msg2.x  # N
            # east2 = msg2.y  # E
            # down2 = msg2.z  # -D 

            # t2 = msg2.time_utc_usec #timestamp #timestamp_sample
            # id2 = msg2.device_id
            # act2= msg2.active_intensity 
            # az2 = msg2.azimuth_deg

        dataQ2.put((t2,id2,act2, az2, yaw2,north2,east2,down2)) 

        csv_writer.writerow({'node_id': id2,'time_utc_usec': t2,'active_intensity': act2, 'azimuth': az2, 'heading': yaw2, 'north': north2, 'east': east2,'down': down2})
        csv_file.flush()  #if programs stopped, will save last few rows

    else:
        csv_file.close()


def updateLinePlot():
        # --------------------- line plot ----------------------
    # Get data from queue 1 if available
    if connection1:
        try:
            t1, id1, act1, az1, yaw1, north1, east1, down1 = dataQ1.get_nowait()
            print("t1:", t1, " id1:", id1, " act_int1:", act1, " az1:", az1, 'heading:', yaw1, 'north:', north1, 'east:', east1,'down:', down1)
        except queue.Empty:
            pass  
    
    # Get data from queue 2 if available
    if connection2:
        try:
            t2, id2, act2, az2, yaw2, north2, east2, down2 = dataQ2.get_nowait()
            print("t2:", t2, " id2:", id2, " act_int2:", act2, " az2:", az2, 'heading:', yaw2, 'north:', north2, 'east:', east2,'down:', down2)
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
    updateLinePlot()
    time.sleep(0.01)

