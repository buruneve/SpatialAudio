#changeParams.py

from pymavlink import mavutil
import tkinter as tk
import struct

import serial.tools.list_ports

### check comm port availability 
# List all available COM ports
ports = serial.tools.list_ports.comports()

deviceList = []
for port in ports:
    deviceList.append(port.device)

# Connect to the vehicle
master = mavutil.mavlink_connection(device=deviceList[0], baud=57600)  # or your connection string
master.wait_heartbeat()
print("Heartbeat received")

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
            bytes_value = struct.pack('i', int(get_param_value))  
            param_value = struct.unpack('f', bytes_value)[0]

        elif (param_name== 'HAP_MODE'):
            param_type = mavutil.mavlink.MAV_PARAM_TYPE_INT32
            param_value = int(get_param_value)
        else:
            param_type = mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            param_value = float(get_param_value)
        
        print(f"{param_name}: {param_value}\n")

        # send updated parameters to px4
        master.mav.param_set_send(
        master.target_system,
        master.target_component,
        param_name.encode('utf-8'),
        param_value,
        param_type)
    

#param description
param_description = [
    '(active intensity)',
    '(maximum azimuth angle (AVS))',
    '(minimum azimuth angle (AVS))',
    '(bottom haptic waveform effect (1-123))',
    '(top haptic waveform effect (1-123))',
    '(maximum elevation angle (AVS))',
    '(maximum elevation angle (AVS))',
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
    '(maximum yaw angle (IMU))'

]

# Request ALL parameters
master.mav.param_request_list_send(
    master.target_system,
    master.target_component
)

# Receive all parameters
getParams = {} # dictionary: key,value pairs
while True:
    message = master.recv_match(type='PARAM_VALUE', blocking=True,timeout=1)
    if message is None:
        break
    if message.param_id.startswith("HAP_"):
        #print(f"{message.param_id}: {message.param_value}")
        if ((message.param_id == 'HAP_SENSE') or (message.param_id == 'HAP_MULTIPLEX') or (message.param_id == 'HAP_DRV_EFFECT_T') or (message.param_id ==  'HAP_DRV_EFFECT_B')) and (message.param_type == 6):
            bytes_value = struct.pack('f', message.param_value)  # Pack as float
            int_value = struct.unpack('i', bytes_value)[0]  # Unpack as signed int32
            getParams[message.param_id] = int_value

        elif (message.param_id == 'HAP_MODE') and (message.param_type == 6):
            getParams[message.param_id] =int(message.param_value)
        else:
            getParams[message.param_id] = message.param_value
#print(getParams)

# input specification labels 
lbl = tk.Label(frame, text= 'HAPTIC PARAMETERS:') #, font = 'times 11 bold') #font = 'roman 10 bold'
lbl.grid(row=0, column=0, sticky='w')

updateParams ={}
count = 2
idx=0
for name, value in getParams.items():  #for x, y in thisdict.items():

    new = name + ' ' + param_description[idx]
    #print(new)

    # create Label to display text 
    lbl5 = tk.Label(frame, text = new) # font = 'roman 11')
    lbl5.grid(row=count+1,sticky = 'w')

    e = tk.Entry(frame)  # create Entry fields for user input
    e.insert(0, value) #insert default param values 

    e.grid(row=count+1, column=1, padx=5, pady=5)
    updateParams[name]=e    # store user input with associated specification 
                                # in a dictionary
    count += 1
    idx+=1

# UPDATE button 
updateButton = tk.Button(frame, text = 'UPDATE', bg ='gray', fg= 'black', padx=5, pady=5, command=lambda: [run(updateParams)]) 
updateButton.grid(row=28, column=1, sticky='e')

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


