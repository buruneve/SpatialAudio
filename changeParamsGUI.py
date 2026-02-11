#changeParams.py

from pymavlink import mavutil
import tkinter as tk
import struct

import serial.tools.list_ports
import time
import threading 
### check comm port availability 
# List all available COM ports
ports = serial.tools.list_ports.comports()

deviceList = []
for port in ports:
    deviceList.append(port.device)

# Connect to the vehicle
master = mavutil.mavlink_connection(device=deviceList[0], baud=57600) 
master.wait_heartbeat()
print("Heartbeat received")

#time.sleep(3)

root = tk.Tk()
#get computers screen dimensions 
screen_width = root.winfo_screenwidth()    #print('screen_width:', screen_width )
screen_height = root.winfo_screenheight()  #print('screen_height:', screen_height)

# root window title & set display dimension to fit users screen
root.title("Change Parameters GUI")
root.geometry(f"{int(screen_width*.5)}" + 'x' + f"{int(screen_height*.6)}")  #width x height+x+y

#frame 
frame = tk.LabelFrame(root, padx=10, pady=10)
frame.pack(side='top', fill="both", expand=True,  padx=10, pady=10)

def run(updateParams):

    for param_name, entry_field in updateParams.items():
        get_param_value = entry_field.get()  #get() method: access/read content of Entry fields/user input

        if ((param_name == 'HAP_SENSE') or (param_name == 'HAP_MULTIPLEX') or (param_name== 'HAP_DRV_EFFECT_T') or (param_name ==  'HAP_DRV_EFFECT_B')):
            param_type =  mavutil.mavlink.MAV_PARAM_TYPE_INT32
            bytes_value = struct.pack('i', int(get_param_value))  # convert python values into binary data (bytes
            param_value = struct.unpack('f', bytes_value)[0] # convert binary data into python values 

        elif (param_name== 'HAP_MODE'):
            param_type = mavutil.mavlink.MAV_PARAM_TYPE_INT32
            param_value = int(get_param_value)
        else:
            param_type = mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            param_value = float(get_param_value)
        
        #print(f"{param_name}: {param_value}\n")

        # send updated parameters to px4
        master.mav.param_set_send(
        master.target_system,
        master.target_component,
        param_name.encode('utf-8'),
        param_value,
        param_type)

param_names = [
    'HAP_ACT_INT',
    'HAP_AZIMUTH_MAX',
    'HAP_AZIMUTH_MIN',
    'HAP_DRV_EFFECT_B',
    'HAP_DRV_EFFECT_T',
    'HAP_ELEV_MAX',
    'HAP_ELEV_MIN',
    'HAP_MODE',
    'HAP_MULTIPLEX',
    'HAP_OFFSET',
    'HAP_PITCH_MAX',
    'HAP_PITCH_MIN',
    'HAP_Q_FACTOR',
    'HAP_ROLL_MAX',
    'HAP_ROLL_MIN',
    'HAP_SENSE',
    'HAP_TRIG_TIMER',
    'HAP_YAW_MAX',
    'HAP_YAW_MIN'
    ]

#param description
param_description = [
    '(active intensity)',
    '(maximum azimuth angle (AVS))',
    '(minimum azimuth angle (AVS))',
    '(bottom haptic waveform effect (1-123))',
    '(top haptic waveform effect (1-123))',
    '(maximum elevation angle (AVS))',
    '(minimum elevation angle (AVS))',
    '(haptic mode: IMU (0) or AVS (1))',
    '(using multiplexer, 1=enabled)',
    '(offset angle)',
    '(maximum pitch angle (IMU))',
    '(minimum pitch angle (IMU))',
    '(q-factor)',
    '(maximum roll angle about x-axis (IMU))',
    '(minimum roll angle about x-axis (IMU))',
    '(sense  (1 or -1))',
    '(trigger timer)',
    '(maximum yaw angle (IMU))',
    '(minimum yaw angle (IMU))'
]

def getParams():

    storeParams = {} # dictionary: key,value pairs

    for names in param_names:
        #param_request_list_send() # requests ALL params 

        # Request haptic parameters only
        master.mav.param_request_read_send(
        master.target_system,
        master.target_component,
        names.encode('utf-8'),
        -1)

        time.sleep(0.5)

        message = master.recv_match(type='PARAM_VALUE', blocking=True,timeout=0.1)

        if message is None:
            break

        print(f"{message.param_id}: {message.param_value}")

        if ((message.param_id == 'HAP_SENSE') or (message.param_id == 'HAP_MULTIPLEX') or (message.param_id == 'HAP_DRV_EFFECT_T') or (message.param_id ==  'HAP_DRV_EFFECT_B')) and (message.param_type == 6):
            bytes_value = struct.pack('f', message.param_value)  # Pack as float
            int_value = struct.unpack('i', bytes_value)[0]  # Unpack as signed int32
            storeParams[message.param_id] = int_value

        elif (message.param_id == 'HAP_MODE') and (message.param_type == 6):
            storeParams[message.param_id] =int(message.param_value)
        else:
            storeParams[message.param_id] = message.param_value

    # root.after(delay_ms, function, *args)
    root.after(0, display_params, storeParams) # update gui from background thread 


def display_params(storeParams):

    lbl = tk.Label(frame, text= 'HAPTIC PARAMETERS:', font = 'times 11 bold') #font = 'roman 10 bold'
    lbl.grid(row=0, column=0, sticky='w')

    updateParams ={}
    idx=0
    for name, value in storeParams.items():  #for x, y in thisdict.items():

        new = name + ' ' + param_description[idx]
        
        # create Label to display text 
        lbl5 = tk.Label(frame, text = new) 
        lbl5.grid(row=idx+1,sticky = 'w')

        e = tk.Entry(frame)  # create Entry fields for user input
        e.insert(0, value) #insert default param values 

        e.grid(row=idx+1, column=1, padx=5, pady=5)
        updateParams[name]=e    # store user input with associated specification 
                                    # in a dictionary
        idx+=1

    # UPDATE button 
    updateButton = tk.Button(frame, text = 'UPDATE', bg ='gray', fg= 'black', padx=5, pady=5, command=lambda: [run(updateParams)]) 
    updateButton.grid(row=idx+2, column=1, sticky='e')

#background thread to get params 
threading.Thread(target=getParams, daemon=True).start() 

root.mainloop()

##############################

# param_type = 6 = INT32 (32-bit integer) - used for enums, boolean flags, counts, etc.
# param_type = 9 = REAL32 (32-bit float) - used for velocity, position, gains, etc.

# master.mav.param_set_send(
#     master.target_system,
#     master.target_component,
#     param_name.encode('utf-8'),
#     param_value,
#     param_type=mavutil.mavlink.MAV_PARAM_TYPE_int32)
    
# # Wait for confirmation
# message = master.recv_match(type='PARAM_VALUE', blocking=True, timeout=3)
# if message and message.param_id == param_name:
#     print(f"Parameter {param_name} set to {message.param_value}")


