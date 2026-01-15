# px4_comm.py
# communicate with px4: send/receive messages

from pymavlink import mavutil
import time
import threading
import queue 
from collections import deque 


# queue for data; type of data structure 
dataQ1 = queue.Queue() # FIFO: first-in, first-out 
dataQ2 = queue.Queue() # FIFO: first-in, first-out 

#deque;  stack data structure
de = deque() # add/remove elements from both ends; FIFO and LIFO (last-in, first-out)

# set mavlink dialect
mavutil.set_dialect("development")

# Start a listening connection
the_connection2 = mavutil.mavlink_connection(device='/dev/ttyUSB0', baud=57600) 
the_connection1 = mavutil.mavlink_connection(device='/dev/ttyUSB1', baud=57600)

# # Wait for the first heartbeat
##  This sets the system and component ID of remote system for the link
the_connection1.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection1.target_system, the_connection1.target_component))
the_connection2.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection2.target_system, the_connection2.target_component))


# sensor_avs message ID
message_id = 296 #292

message1 = the_connection1.mav.command_long_encode(   
        the_connection1.target_system,  # Target system ID
        the_connection1.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
        0,  # Confirmation
        message_id,   # param1: Message ID to be streamed
        0, # param2: Interval in microseconds
        0,0,0,0,0)
print(message1)

# # Send the COMMAND_LONG
the_connection1.mav.send(message1)

msg1 = the_connection1.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
print(msg1) 
print('')

message2 = the_connection2.mav.command_long_encode(   
        the_connection2.target_system,  # Target system ID
        the_connection2.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
        0,  # Confirmation
        message_id,   # param1: Message ID to be streamed
        0, # param2: Interval in microseconds
        0,0,0,0,0)
print(message2)

# # Send the COMMAND_LONG
the_connection2.mav.send(message2)

msg2 = the_connection2.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
print(msg2) 
print('')


# data storage 
max_data = 100
actv1 = deque(maxlen=max_data)
actv2 = deque(maxlen=max_data)
tt1 = deque(maxlen=max_data)
tt2 = deque(maxlen=max_data)

#------------------------------------------------------------------------------
# Time synchronization thread
def sync_time():
    """Send SYSTEM_TIME messages to both flight controllers"""

    while True: 
        # Get current UTC time in microseconds
        time_unix_usec = int(time.time() * 1e6)
        print("system time: ", time_unix_usec)
        # readable_time = datetime.fromtimestamp(time_unix_usec/1e6)
        # print(readable_time)

        # Send to both connections
        the_connection1.mav.system_time_send(time_unix_usec, 0)
        the_connection2.mav.system_time_send(time_unix_usec, 0)

        time.sleep(1.0)  # Send at 1 Hz

#data acquisition thread
def getFPV_data1():
    
    """thread for connection 1"""

    while True:            
        msg1 = the_connection1.recv_match(type='SENSOR_AVS_LITE',blocking=True)  
        #print(msg1)

        if msg1: 

            t1 = msg1.time_utc_usec #timestamp 
            act1= msg1.active_intensity 

            print("t1: ",tt1, "act_int1: ", act1)
        dataQ1.put((t1,act1)) 
        #print("t1: ",tt1, "act_int1: ", act1)

# data acquisition thread
def getFPV_data2():
    
    """thread for connection 2"""

    while True: 
        msg2 = the_connection2.recv_match(type = 'SENSOR_AVS_LITE',blocking=True) #type='SENSOR_AVS', 

        if msg2:
            
            t2 = msg2.time_utc_usec #timestamp #timestamp_sample
            act2= msg2.active_intensity 

            print("t2: ",t2, " act_int2: ", act2)
        dataQ2.put((t2,act2)) #mel2
        #print("t2: ",t2, " act_int2: ", act2)

                             

# -------- threads ---------
threading.Thread(target=sync_time, daemon=True).start()  
threading.Thread(target=getFPV_data1, daemon=True).start()
threading.Thread(target=getFPV_data2, daemon=True).start()


