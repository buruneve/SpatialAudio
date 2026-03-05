#changeParams.py

from doctest import master

from pymavlink import mavutil
import tkinter as tk
from tkinter import ttk
import struct

import serial.tools.list_ports
import time
import threading 
import matplotlib.image as mpimg 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import queue
import numpy as np
import math
from parameters import param_names   #parameters.py
from parameters import param_description

from concurrent.futures import ThreadPoolExecutor
from tkinter import font

# set mavlink dialect
mavutil.set_dialect("development")

### check comm port availability 
# List all available COM ports
ports = serial.tools.list_ports.comports()

img = mpimg.imread("head_topview.jpg")
img2 = mpimg.imread("side_profile3.jpg")

# queue for data; type of data structure 
dataQ = queue.Queue() # FIFO: first-in, first-out 
ind=0

# at the top of your file with other globals
updateXaz_r = 0
updateYaz_r = 0
updateXaz_l = 0
updateYaz_l = 0

updateY_el=0 
updateX_el=0

act_l = 0.0
act_r = 0.0

# root = tk.Tk()
# screen_width = root.winfo_screenwidth()    
# print('screen_width:', screen_width )
# screen_height = root.winfo_screenheight()  
# print('screen_height:', screen_height)

deviceList = []
for port in ports:
    deviceList.append(port.device)
print(deviceList)

# # Connect to the vehicle
connection = mavutil.mavlink_connection(device=deviceList[0], baud=57600) 
connection.wait_heartbeat(timeout=5) #timeout=5
print("Heartbeat received")
print()



root = tk.Tk()
# setting attribute

#get computers screen dimensions 
screen_width = root.winfo_screenwidth()    #print('screen_width:', screen_width )
screen_height = root.winfo_screenheight()  #print('screen_height:', screen_height)
#root.geometry("%dx%d" % (screen_width, screen_height))
#root.state('zoomed')

# make the font bigger globally
default_font = tk.font.nametofont("TkDefaultFont")
default_font.configure(size=12)
root.option_add("*Font", default_font) 

#root.geometry(f"{int(screen_width*.8)}" + 'x' + f"{int(screen_height*.9)}")
# root.geometry(f"{int(screen_width)}" + 'x' + f"{int(screen_height)}")
#frame = tk.Frame(root)

tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Change Parameters')
tabControl.add(tab2, text='Visuals')

tabControl.pack(expand=1, fill = 'both') #grid()


#frame for tab1
frame = tk.LabelFrame(tab1, padx=10, pady=10)
frame.pack(expand = True,fill="both", padx=10, pady=10)
#frame.pack(side='top', fill="both", expand=True,  padx=10, pady=10)

# #frame for tab2
frame2 = tk.LabelFrame(tab2, padx=5) #, pady=5)
frame2.pack(side ='left', padx=5)
# frame2.pack(expand=True, padx=10, pady=10) #side='top', fill="both", expand=True,  padx=10, pady=10)

# # wrap all three panels in a centered row container
# visuals_row = tk.Frame(frame2)
# visuals_row.pack(expand=True)

##################################################################
####                        TAB 2
##################################################################

#####   TOP VIEW 

# create frame  #frame2
imgFrame = tk.Frame(master=frame2, padx=5, pady=5) #,padx=10, pady=10) master=visuals_row,
imgFrame.pack(side="top",padx=5)#grid(row=0, column=2)

fig3, ax3 = plt.subplots(figsize=(5,4))  #5,4
canvas3 = FigureCanvasTkAgg(fig3, master=imgFrame)  # Place in the plot frame
ax3.patch.set_facecolor('white') 
# #self.fig3.patch.set_facecolor('none') 
fig3.patch.set_alpha(0) # background (outside of figure)
canvas3.get_tk_widget().pack() # fill=tk.BOTH, expand=True) 
canvas3.get_tk_widget().configure(bg= '#F0F0F0')

# add image axes (position: [left, bottom, width, height])
# image_xaxis, image_yaxis, image_width, image_height
ax_img = fig3.add_axes([.364, .35, .3, .3]) 
ax_img.imshow(img)
ax_img.axis('off')

ax3.set_aspect('equal') #cirularizes (oval without this)
ax3.set_xlim([-1.5,1.5])
ax3.set_ylim(-1.5,1.5)

circle_inner = plt.Circle((0,0), 1, fill=False)
ax3.add_patch(circle_inner)   # patch object to first create circle; patch is any 2D geometric shape (circle, rectangle, etc) 
#canvas3.draw()

circle_outer = plt.Circle((0,0), 1.25, fill=False)
ax3.add_patch(circle_outer) 
canvas3.draw()

# self.ax3.axis('off')  this removes plot entirely (box)
# remove x and y axis ticks/labels
ax3.set_xticks([]) # remove x and y axis ticks/labels
ax3.set_yticks([])

# -----------------------------------------------------------------------------------

# --- red and blue circles 
circle_red = plt.Circle((0,0), 0.05, color='red', label ='right node')
ax3.add_patch(circle_red)

circle_green = plt.Circle((0,0), 0.05, color='green', label = 'left node')
ax3.add_patch(circle_green)

circle_blue = plt.Circle((0,0), 0.05, color='blue')
ax3.add_patch(circle_blue)

ax3.legend(handles=[circle_red, circle_green], loc='upper right', fontsize=8)

canvas3.draw()  # initial draw
background2 = canvas3.copy_from_bbox(ax3.bbox) # snapshot BEFORE circles



##### TOP VIEW 2 for IMU

# second top view frame - underneath first
imgFrame3 = tk.Frame(master=frame2, padx=5, pady=5)
imgFrame3.pack(side="top", padx=5)

fig5, ax5 = plt.subplots(figsize=(5,4))
canvas5 = FigureCanvasTkAgg(fig5, master=imgFrame3)
ax5.patch.set_facecolor('white')
fig5.patch.set_alpha(0)
canvas5.get_tk_widget().pack()
canvas5.get_tk_widget().configure(bg='#F0F0F0')

# add head image
ax_img2 = fig5.add_axes([.364, .35, .3, .3])
ax_img2.imshow(img)
ax_img2.axis('off')

ax5.set_aspect('equal')
ax5.set_xlim([-1.5, 1.5])
ax5.set_ylim(-1.5, 1.5)

circle_inner2 = plt.Circle((0,0), 1.25, fill=False)
ax5.add_patch(circle_inner2)

# circle_outer2 = plt.Circle((0,0), 1.25, fill=False)
# ax5.add_patch(circle_outer2)

ax5.set_xticks([])
ax5.set_yticks([])


# circles for second plot
circle_red3 = plt.Circle((0,0), 0.05, color='red', label='IMU')
ax5.add_patch(circle_red3)

# circle_green3 = plt.Circle((0,0), 0.05, color='green', label='Left node (44)')
# ax5.add_patch(circle_green3)

ax5.legend(handles=[circle_red3], loc='upper right', fontsize=8)

canvas5.draw()
background4 = canvas5.copy_from_bbox(ax5.bbox)  # snapshot BEFORE circles

##### SIDE VIEW
# create frame
imgFrame2 = tk.Frame(master=tab2)
imgFrame2.pack(side="left", padx=5)

fig4, ax4 = plt.subplots(figsize=(5,4)) 
canvas4 = FigureCanvasTkAgg(fig4, master=imgFrame2)  # Place in the plot frame
ax4.patch.set_facecolor('white') 
#fig4.patch.set_facecolor('none') 
fig4.patch.set_alpha(0) # background (outside of figure)
canvas4.get_tk_widget().pack() # fill=tk.BOTH, expand=True) 
canvas4.get_tk_widget().configure(bg= '#F0F0F0')


# add image axes (position: [left, bottom, width, height])
# image_xaxis, image_yaxis, image_width, image_height
ax_img = fig4.add_axes([.364, .35, .3, .3]) 
ax_img.imshow(img2)
ax_img.axis('off')

ax4.set_aspect('equal') #cirularizes (oval without this)
ax4.set_xlim([-1.5,1.5])
ax4.set_ylim(-1.5,1.5)

circle_inner = plt.Circle((0,0), 1, fill=False)
ax4.add_patch(circle_inner)   # patch object to first create circle; patch is any 2D geometric shape (circle, rectangle, etc) 
#canvas4.draw()

# circle_outer = plt.Circle((0,0), 1.25, fill=False)
# ax4.add_patch(circle_outer) 
# canvas4.draw()

# self.ax4.axis('off')  this removes plot entirely (box)
# remove x and y axis ticks/labels
ax4.set_xticks([]) # remove x and y axis ticks/labels
ax4.set_yticks([])

# -----------------------------------------------------------------------------------

canvas4.draw()  # initial draw
background3 = canvas4.copy_from_bbox(ax4.bbox) # snapshot BEFORE circles

# --- red and blue circles 
circle_red2 = plt.Circle((0,0), 0.05, color='red')
ax4.add_patch(circle_red2)

# circle_blue = plt.Circle((0,0), 0.05, color='blue')
# ax4.add_patch(circle_blue)


# ####----------------------------------------------

# #spectrogram plot

# # frame for spectrogram plot
# specFrame = tk.Frame(master=tab2)
# specFrame.pack(side="left", padx=5)

# ind = 0
# ind2=0
# spec = np.zeros((60,16)) # storage for spectrogram; x: time steps to keep visible; y: number of mel bands

# fig, ax = plt.subplots(figsize=(5, 4))
# im = ax.imshow(spec, aspect='auto', origin='lower',cmap='magma',interpolation='nearest', animated=True) #initialize and show image once
# ax.set_ylabel("Time"); ax.set_xlabel("Mel bands"); ax.set_title("Real-time Mel Spectrogram")
# im.set_clim(vmin=40, vmax=90)  # rescale colors

# canvas = FigureCanvasTkAgg(fig, master=specFrame)
# canvas_widget = canvas.get_tk_widget()
# canvas_widget.pack(side = tk.RIGHT) #fill=tk.BOTH, expand=True)

# # # Tell matplotlib we will use blitting
# # # blitting -- aka block image transfer; plots only part of an image that have changed instead of entire figure 
# background = fig.canvas.copy_from_bbox(ax.bbox) # saves a clean background (the static parts: axes, ticks, grid, etc.)

# # # Draw initial state
# ax.draw_artist(im)
# fig.canvas.blit(ax.bbox)  #bbox- bounding box 

# ####==================================


postUpdate = {}
def run(updateParams):

    print("-------- Updated Parameters -------")

    for param_name, entry_field in updateParams.items():
        get_param_value = entry_field.get()  #get() method: access/read content of Entry fields/user input
#or (param_name == 'HAP_ENABLE')
        if ((param_name == 'HAP_SENSE_AVS_R') or (param_name== 'HAP_MODE')or (param_name == 'HAP_SENSE_AVS_L') or (param_name == 'HAP_SENSE_IMU')or(param_name == 'HAP_MULTIPLEX') or (param_name== 'HAP_DRV_EFFECT_T') or (param_name ==  'HAP_DRV_EFFECT_B')):
            param_type =  mavutil.mavlink.MAV_PARAM_TYPE_INT32
            bytes_value = struct.pack('i', int(get_param_value))  # convert python values into binary data (bytes
            param_value = struct.unpack('f', bytes_value)[0] # convert binary data into python values 

        else:
            param_type = mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            param_value = float(get_param_value)

        
        print(f"{param_name}: {param_value}")

        # send updated parameters to px4
        connection.mav.param_set_send(
        connection.target_system,
        connection.target_component,
        param_name.encode('utf-8'),
        param_value,
        param_type)


    return param_name, param_value

def getParams():

    storeParams = {} # dictionary: key,value pairs

    # drain buffer before requesting params
    while connection.recv_match(blocking=False) is not None:
        pass

    print()
    for names in param_names:
        #param_request_list_send() # requests ALL params 

        # Request haptic parameters only
        connection.mav.param_request_read_send(
        connection.target_system,
        connection.target_component,
        names.encode('utf-8'),
        -1)

        time.sleep(0.1) #0.01 #delay to ensure messages are received in order

        message = connection.recv_match(type='PARAM_VALUE', blocking=True,timeout=1) #0.1 #timeout

        if message is None:
            break
        
        print('getting parameters...')
        #print(f"{message.param_id}: {message.param_type}, {message.param_value}\n")
# or (message.param_id == 'HAP_ENABLE') 
        if ((message.param_id == 'HAP_SENSE_AVS_R') or (message.param_id == 'HAP_MODE') or (message.param_id == 'HAP_SENSE_AVS_L') or (message.param_id == 'HAP_SENSE_IMU') or (message.param_id == 'HAP_MULTIPLEX') or (message.param_id == 'HAP_DRV_EFFECT_T') or (message.param_id ==  'HAP_DRV_EFFECT_B')) and (message.param_type == 6):
            bytes_value = struct.pack('f', message.param_value)  # Pack as float
            int_value = struct.unpack('i', bytes_value)[0]  # Unpack as signed int32
            storeParams[message.param_id] = int_value

        # elif (message.param_id == 'HAP_MODE') and (message.param_type == 6):
        #     bytes_value = struct.pack('f', message.param_value)
        #     storeParams[message.param_id] = struct.unpack('i', bytes_value)[0]
        #     #storeParams[message.param_id] =int(message.param_value)

        else:
            storeParams[message.param_id] = message.param_value

    # root.after(delay_ms, function, *args)
    root.after(0, display_params, storeParams) # update gui from background thread 


def display_params(storeParams):
    global updateParams
#frame
    lbl = tk.Label(frame, text= 'HAPTIC PARAMETERS:', font = "TkDefaultFont 18 bold") #, font = 'roman 12 bold') #, font = 'times 11 bold') #font = 'roman 10 bold'
    lbl.grid(row=0, column=0, sticky='w')

    updateParams ={}
    idx=0
    for name, value in storeParams.items(): 

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
    updateButton.grid(row=idx+2, column=1, sticky='e', pady=10, padx=10)


# ###################################################################
nodes = []
def getFPV_data():

    message_id = 297 #message ID for SENSOR_AVS_LITE_EXT

    # drain any leftover messages
    while connection.recv_match(blocking=False) is not None:
        pass

    print("")
    print("--- sending command_long to stream sensor_avs_lite_ext data ---")  
    print()

    message2 = connection.mav.command_long_encode(  
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
            0,  # Confirmation
            message_id,   # param1: Message ID to be streamed
            0, # param2: Interval in microseconds
            0,0,0,0,0)
    print(message2)

    # # Send the COMMAND_LONG
    connection.mav.send(message2)

    msg2 = connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
    print("ACK:",msg2) 
    print('')
    
    "data acquisition thread"
    "write to queue and csv file"
    
    if not connection:
        return
    
    while  True:       
        # recv_match returns one mavlink message  
        # returns only the next message that arrives; one msg type per call 
        # Different message types arrive at different frequencies
          
        msg = connection.recv_match(type='SENSOR_AVS_LITE_EXT', blocking=True)   
        #print(msg)

        #check if msg arrived 
        if msg: 
            t = msg.time_utc_usec
            id = msg.device_id
            act = msg.active_intensity
            az = msg.azimuth_deg
            el = msg.elevation_deg

            yaw = msg.yaw
            pitch = msg.pitch
            roll = msg.roll

            north = msg.north
            east = msg.east
            down = msg.down

        dataQ.put((t,id,act,az,el,yaw,pitch,roll,north,east,down))

        if id not in nodes:
            nodes.append(id)

# # left node 44
# # right nodde 41

def updatePlots():

    "------------------ HEAD PLOTS ------------------------"

    global ind,background2, background3, background4, updateParams
    global updateXaz_r, updateYaz_r, updateXaz_l, updateYaz_l,updateY_el, updateX_el, act_l, act_r

    try:
        t, id, act, az,el, yaw,pitch, roll, north, east, down = dataQ.get_nowait()
    #print('north:', north)
    except queue.Empty:
         root.after(1,updatePlots)
         return
    
    #print(az, el, act)

    if len(nodes) < 1:
        root.after(1, updatePlots)
        return  # wait until both nodes are known

    # left node
    if id == nodes[0]:
        act_l = act
        updateYaz_l = 1*np.cos(np.deg2rad(az))  #X #az 
        updateXaz_l = 1*np.sin(np.deg2rad(az))  #Y

        updateY_el = 1*np.cos(np.deg2rad(el))  #X 
        updateX_el = 1*np.sin(np.deg2rad(el))  #Y
    
    # right node 
    if id == nodes[0]:
        act_r = act
        updateYaz_r = 1*np.cos(np.deg2rad(az))  #X #az 
        updateXaz_r = 1*np.sin(np.deg2rad(az))  #Y


    #fig.canvas.restore_region(background) 
    # restore background of head plots; only copies pixels back
    canvas3.restore_region(background2)   
    canvas4.restore_region(background3)   
    canvas5.restore_region(background4)
    
    
    #flipped to start at 90 degree and rotate clockwise
    updateYyaw = 1.25*np.cos(np.deg2rad(yaw))  #X #yaw
    updateXyaw = 1.25*np.sin(np.deg2rad(yaw))  #Y

    # circle_blue.set_center((updateXyaw, updateYyaw))
    # ax3.draw_artist(circle_blue)
    # canvas3.blit(ax3.bbox) 

    # circle_red2.set_center((updateX_el, updateY_el))
    # ax4.draw_artist(circle_red2)   # redraws circle in new location 
    # canvas4.blit(ax4.bbox) 

    circle_red3.set_center((updateXyaw, updateYyaw))
    ax5.draw_artist(circle_red3)
    canvas5.blit(ax5.bbox)


    if act_l > 25 or act_r > 25:
        circle_red.set_center((updateXaz_r, updateYaz_r))  # set_center() updates/moves circle
        circle_green.set_center((updateXaz_l, updateYaz_l))

        ## circle_red.set_radius((0.05 * size)) 
        ##circle_green.set_center((updateXyaw, updateYyaw))
        #circle_red2.set_center((updateX_el, updateY_el))

        # draw artists
        ax3.draw_artist(circle_red)   # redraws circle in new location 
        ax3.draw_artist(circle_green)

            
        circle_red2.set_center((updateX_el, updateY_el))
        ax4.draw_artist(circle_red2)   # redraws circle in new location 
        canvas4.blit(ax4.bbox) 

        # circle_red3.set_center((updateXyaw, updateYyaw))
        # # #circle_green3.set_center((updateXaz_l, updateYaz_l))
        # ax5.draw_artist(circle_red3)
        # #ax5.draw_artist(circle_green3)
        # canvas5.blit(ax5.bbox)

        # ax3.draw_artist(circle_blue)
        canvas3.blit(ax3.bbox) 


    # tkinter timer/scheduler 
    # schedules updates without blocking so GUI stays responsive
    root.after(1, updatePlots)  #passes results back to main thread to update GUI

# UPDATE button 
plotButton = tk.Button(frame2, text = 'PLOT', bg ='gray', fg= 'black', padx=5, pady=5, command=lambda: [updatePlots()]) 
plotButton.pack(side='bottom', pady=10, padx=10)

def stopSensorStreams():

    "------------------ STOP SENSOR STREAMS ------------------------"

    print('Stopping sensor_avs streams...')
    message_id = 292
    message = connection.mav.command_long_encode(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,
        message_id,
        -1,  # -1 = disable the stream
        0,0,0,0,0)
    connection.mav.send(message)
    time.sleep(0.1)  # let it settle

    message_id = 296
    message = connection.mav.command_long_encode(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,
        message_id,
        -1,  # -1 = disable the stream
        0,0,0,0,0)
    connection.mav.send(message)
    time.sleep(0.1)  # let it settle


    message_id = 297
    message = connection.mav.command_long_encode(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,
        message_id,
        -1,  # -1 = disable the stream
        0,0,0,0,0)
    connection.mav.send(message)
    time.sleep(0.1)  # let it settle


def runThreads():

    stopSensorStreams()  # stop streams

    # Create and start threads for data acquisition and plotting
    ('getting params')
    t1 = threading.Thread(target=getParams, daemon=True)
    t1.start()
    t1.join()  # Wait for the parameter retrieval thread to finish before starting the plotting thread

    t2 = threading.Thread(target=getFPV_data, daemon=True)
    t2.start()

# # def plotSpectrogram():
# #     global ind, spec


# #     try:
# #         t, id, act, az,el, yaw,pitch, roll, north, east, down = dataQ.get_nowait()
# #     except queue.Empty:
# #          root.after(1,plotSpectrogram)
# #          return

# #     # Update spectrogram data
# #     spec = np.roll(spec, -1, axis=0)  # Shift spectrogram up by one row
# #     spec[-1] = act  # Add new intensity value to the bottom row

# #     # Update the image with new data
# #     im.set_data(spec)
# #     fig.canvas.draw_idle()  # Redraw the canvas

# #     root.after(1, plotSpectrogram)  # Schedule next update



# run threads in background, keeping GUI free
threading.Thread(target=runThreads, daemon=True).start()
updatePlots()

root.mainloop() #drives all GUI updates 




##############################

#

# param_type = 6 = INT32 (32-bit integer) - used for enums, boolean flags, counts, etc.
# param_type = 9 = REAL32 (32-bit float) - used for velocity, position, gains, etc.


# #normalize data
# yaw = (math.degrees(yaw)+360) % 360 #normalize yaw

# pitch =( math.degrees(pitch)  +360) % 360 
# el = (math.degrees(el) +360) % 360 #normalize yaw
#az = (math.degrees(az) +360) % 360 #normalize yaw

# roll = (math.degrees(roll) +360) % 360 #normalize roll

# p = (math.degrees(pitch) +360) % 360 #normalize roll
# print('pitch:', p)



    #print(act)
    # apply transformation if parameters are loaded
    # if updateParams:
    #     try: 
    #         sense = int(updateParams['HAP_SENSE_AVS_R'].get())
    #         offset = float(updateParams['HAP_OFFSET_AVS_R'].get())
    #         #roll_deg = math.degrees(roll)  # if roll is in radians

    #         roll_transformed = (roll - offset) * sense
    #         el_transformed = (el - offset)*sense
    #         yaw_transformed = (yaw - offset) * sense
    #     except ValueError:
    #             roll_transformed = roll  # fallback if value is invalid/incomplete
    #             yaw_transformed = yaw  # fallback if value is invalid/incomplete
    #             el_transformted = el  # fallback if value is invalid/incomplete
    #print("og roll:", roll, "transformed roll:", roll_transformed)

#storeParams[message.param_id] =
#int(message.param_value)

        # elif (param_name== 'HAP_MODE'): # or (param_name == 'HAP_SENSE'):
        #     param_type = mavutil.mavlink.MAV_PARAM_TYPE_INT32
        #     param_value = int(get_param_value)