# px4_comm.py
# communicate with px4: send/receiveve messages

from pymavlink import mavutil
import sys
import numpy as np
import matplotlib.pyplot as plt
mavutil.set_dialect("development")

# Start a listening connection
the_connection = mavutil.mavlink_connection(device='COM5', baud=11500) #, dialect = 'custom'

# # Wait for the first heartbeat
# #   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))


#MAV_CMD_MISSION_START
the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, 
                                     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,0,0,0,0,0,0,0)

#the_connection.mav.send(message)
msg = the_connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
print(msg) 

# sensor_avs message ID
message_id = 292 
print("message_id: ",message_id)

message = the_connection.mav.command_long_encode(    #encode
        the_connection.target_system,  # Target system ID
        the_connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  #MAV_CMD_REQUEST_MESSAGE
        0,  # Confirmation
        message_id, #mavutil.mavlink.MAVLINK_MSG_ID_SENSOR_AVS  # param1: Message ID to be streamed
        50000, # param2: Interval in microseconds 1000000
        0,0,0,0,0)
print(message)

# # Send the COMMAND_LONG
the_connection.mav.send(message)
msg2 = the_connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
print(msg2) 
print('')

# extract: azimuth deg 
# tresholds 
# active intensity - how loud sound is 
# q_factor - diffusion/concentration of sound 
# plot - mel intesity
# spectrograms 
while True:   #COMMAND_ACK  #UNKNOWN_292 type='SENSOR_AVS', 
        res = the_connection.recv_match(blocking=True)  # receives all the messages available 
        print(res) # get a lot of data 
        
        azimuth_deg = the_connection.messages['SENSOR_AVS'].azimuth_deg
        print("azimuth_deg: ",azimuth_deg)
        
        q_factor = the_connection.messages['SENSOR_AVS'].q_factor
        print("q_factor: ",q_factor)
        
        mel_intensity = the_connection.messages['SENSOR_AVS'].mel_intensity
        print("mel_intesity: ",mel_intensity)
        print('')

        time_boot_ms  = the_connection.messages['ATTITUDE'].time_boot_ms 
        print("time_boot_ms: ",time_boot_ms )

        yaw = the_connection.messages['ATTITUDE'].yaw  #GUI 
        print("yaw: ",yaw)

        pitch = the_connection.messages['ATTITUDE'].pitch
        print("pitch: ", pitch)

        roll = the_connection.messages['ATTITUDE'].roll
        print("roll: ", roll)
        print()
        