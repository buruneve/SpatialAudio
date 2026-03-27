#changeParams.py

from doctest import master 

from pymavlink import mavutil
import tkinter as tk
from tkinter import ttk
import struct

import serial.tools.list_ports
import time
import threading 
import csv
import os
import datetime
import matplotlib.image as mpimg 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import queue
from collections import deque 
import numpy as np
from parameters import all_params   #parameters.py
from parameters import hap_description
from parameters import avs_description


# set mavlink dialect
mavutil.set_dialect("development")

### check comm port availability 
# List all available COM ports
ports = serial.tools.list_ports.comports()

img = mpimg.imread("head_topview.jpg")
img2 = mpimg.imread("side_profile3.jpg")

# queue for data; type of data structure 
dataQ = queue.Queue() # FIFO: first-in, first-out 
dataQSpec = queue.Queue() # FIFO: first-in, first-out 
dataNEDQ = queue.Queue() # FIFO: first-in, first-out
dataQAct = queue.Queue() # FIFO: first-in, first-out

#deque;  stack data structure
de = deque() # add/remove elements from both ends; FIFO and LIFO (last-in, first-out)
ind=0

# event manages internal flag
# event by default is false
# set() method signals event is true
# clear() method resets to false
# wait() method blocks until event is true

#is_set() method checks if event is true or false

#flags to signal threads to stop when = True
log_stop_event = threading.Event() 
fpv_stop_event = threading.Event() 
spec_stop_event = threading.Event()
traj_stop_event = threading.Event()
actv_stop_event = threading.Event() 

updateXaz_r = 0
updateYaz_r = 0
updateXaz_l = 0
updateYaz_l = 0

updateY_el=0 
updateX_el=0

act_l = 0.0
act_r = 0.0

# CSV write lock for thread safety
csv_lock = threading.Lock()

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

root.title("Flight Controller and ARES Control Panel")

# #get computers screen dimensions 
screen_width = root.winfo_screenwidth();   #print('screen_width:', screen_width )
screen_height = root.winfo_screenheight();  #print('screen_height:', screen_height)
# #root.geometry("%dx%d" % (screen_width, screen_height))
# #root.state('zoomed')
root.geometry("+200+100") 

# # set minimum window size value
# root.minsize(1100, 750)

# # set maximum window size value
# root.maxsize(1100, 750)

# make the font bigger globally
default_font = tk.font.nametofont("TkDefaultFont")
default_font.configure(size=18)
root.option_add("*Font", default_font) 

root.resizable(False, False)

# screen_width: 1920
# screen_height: 1080

#root.resizable(True, True)
#root.geometry(f"{int(screen_width*.5)}" + 'x' + f"{int(screen_height*.8)}")

tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl)
tab11 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
tab4 = ttk.Frame(tabControl)
tab5 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Change Parameters')
tabControl.add(tab11, text='ARES')
tabControl.add(tab2, text='Visuals')
tabControl.add(tab3, text='Spectrogram')
tabControl.add(tab4, text='Trajectory')
tabControl.add(tab5, text='Intensity Plot')

tabControl.pack(expand=1, fill = 'both') #grid()

#frame for tab1
frame = tk.LabelFrame(tab1, padx=10, pady=10)
frame.pack(expand = True,fill="both", padx=10, pady=10)
#frame.pack(side='top', fill="both", expand=True,  padx=10, pady=10)

aresFrame = tk.LabelFrame(tab11, padx=10, pady=10)
aresFrame.pack(expand = True,fill="both", padx=10, pady=10)

# #frame for tab2
frame2 = tk.LabelFrame(tab2, padx=5) #, pady=5)
frame2.pack(side ='left', padx=5)
# frame2.pack(expand=True, padx=10, pady=10) #side='top', fill="both", expand=True,  padx=10, pady=10)

# #frame for tab3
frame3 = tk.LabelFrame(tab3, padx=5) #, pady=5)
frame3.pack(expand=True, side ='left', padx=5)

## frame for tab4
nedFrame = tk.LabelFrame(tab4, padx=5) #, pady=5)
nedFrame.pack(expand=True, side ='left', padx=5)

## frame for tab5
frame5 = tk.LabelFrame(tab5, padx=5) #, pady=5)
frame5.pack(expand=True, side ='left', padx=5)

##################################################################
####                        TAB 2
##################################################################

#####   TOP VIEW 

# create frame  #frame2
imgFrame = tk.Frame(master=frame2, padx=5, pady=5) #,padx=10, pady=10) master=visuals_row,
#imgFrame.pack(side="top",padx=5)#grid(row=0, column=2)
imgFrame.grid(row=0, column=0, padx=5, pady=5)

fig3, ax3 = plt.subplots(figsize=(6,5))  #5,4
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

circle_inner = plt.Circle((0,0), 1.15, fill=False)
ax3.add_patch(circle_inner)   # patch object to first create circle; patch is any 2D geometric shape (circle, rectangle, etc) 


# self.ax3.axis('off')  this removes plot entirely (box)
# remove x and y axis ticks/labels
ax3.set_xticks([]) # remove x and y axis ticks/labels
ax3.set_yticks([])

# -----------------------------------------------------------------------------------

# --- red and blue circles 
circle_red_az_r = plt.Circle((0,0), 0.05, color='red', label ='right node')
ax3.add_patch(circle_red_az_r)

circle_green_az_l = plt.Circle((0,0), 0.05, color='green', label = 'left node')
ax3.add_patch(circle_green_az_l)

ax3.legend(handles=[circle_red_az_r, circle_green_az_l], loc='upper right', fontsize=8)

canvas3.draw()  # initial draw
background2 = canvas3.copy_from_bbox(ax3.bbox) # snapshot BEFORE circles

##### TOP VIEW 2 for IMU

# second top view frame - underneath first
imgFrame3 = tk.Frame(master=frame2, padx=5, pady=5)
#imgFrame3.pack(side="top", padx=5)
imgFrame3.grid(row=1, column=0, padx=5, pady=5)

fig5, ax5 = plt.subplots(figsize=(6,5))
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

circle_inner2 = plt.Circle((0,0), 1.15, fill=False)
ax5.add_patch(circle_inner2)

# circle_outer2 = plt.Circle((0,0), 1.15, fill=False)
# ax5.add_patch(circle_outer2)

ax5.set_xticks([])
ax5.set_yticks([])


# circles for second plot
circle_red_yaw = plt.Circle((0,0), 0.05, color='red', label='IMU')
ax5.add_patch(circle_red_yaw)


ax5.legend(handles=[circle_red_yaw], loc='upper right', fontsize=8)

canvas5.draw()
background4 = canvas5.copy_from_bbox(ax5.bbox)  # snapshot BEFORE circles

##### SIDE VIEW for AVS
# create frame
imgFrame2 = tk.Frame(master=frame2)
#imgFrame2.pack(side="right", padx=5)
imgFrame2.grid(row=0, column=1, padx=5, pady=5)

fig4, ax4 = plt.subplots(figsize=(6,5)) 
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

circle_inner = plt.Circle((0,0), 1.15, fill=False)
ax4.add_patch(circle_inner)   # patch object to first create circle; patch is any 2D geometric shape (circle, rectangle, etc) 

# self.ax4.axis('off')  this removes plot entirely (box)
# remove x and y axis ticks/labels
ax4.set_xticks([]) # remove x and y axis ticks/labels
ax4.set_yticks([])

# -----------------------------------------------------------------------------------

canvas4.draw()  # initial draw
background3 = canvas4.copy_from_bbox(ax4.bbox) # snapshot BEFORE circles

# --- red and blue circles 
circle_red_elev = plt.Circle((0,0), 0.05, color='red')
ax4.add_patch(circle_red_elev)


#------------------------------------------------------------------------
##### SIDE VIEW for IMU

# create frame
imgFrame4 = tk.Frame(master=frame2)
#imgFrame2.pack(side="right", padx=5)
imgFrame4.grid(row=1, column=1, padx=5, pady=5)

fig6, ax6 = plt.subplots(figsize=(6,5)) 
canvas6 = FigureCanvasTkAgg(fig6, master=imgFrame4)  # Place in the plot frame
ax6.patch.set_facecolor('white') 
#fig4.patch.set_facecolor('none') 
fig6.patch.set_alpha(0) # background (outside of figure)
canvas6.get_tk_widget().pack() # fill=tk.BOTH, expand=True) 
canvas6.get_tk_widget().configure(bg= '#F0F0F0')

# add image axes (position: [left, bottom, width, height])
# image_xaxis, image_yaxis, image_width, image_height
ax_img = fig6.add_axes([.364, .35, .3, .3]) 
ax_img.imshow(img2)
ax_img.axis('off')

ax6.set_aspect('equal') #cirularizes (oval without this)
ax6.set_xlim([-1.5,1.5])
ax6.set_ylim(-1.5,1.5)

circle_inner3 = plt.Circle((0,0), 1.15, fill=False)
ax6.add_patch(circle_inner3)   # patch object to first create circle; patch is any 2D geometric shape (circle, rectangle, etc) 

# self.ax4.axis('off')  this removes plot entirely (box)
# remove x and y axis ticks/labels
ax6.set_xticks([]) # remove x and y axis ticks/labels
ax6.set_yticks([])

# -----------------------------------------------------------------------------------

canvas6.draw()  # initial draw
background6 = canvas6.copy_from_bbox(ax6.bbox) # snapshot BEFORE circles

circle_red_roll = plt.Circle((0,0), 0.05, color='red')
ax6.add_patch(circle_red_roll)

# ####----------------------------------------------

#spectrogram plot

# frame for spectrogram plot
specFrame = tk.Frame(master=frame3)
specFrame.grid(row=1, column=1, padx=5, pady=5)
#specFrame.pack(side="left", padx=5)

ind = 0
ind2=0
spec = np.zeros((60,16)) # storage for spectrogram; x: time steps to keep visible; y: number of mel bands
spec2 = np.zeros((60,16))

fig, ax = plt.subplots(2,1,figsize=(10, 8))
im0 = ax[0].imshow(spec, aspect='auto', origin='lower',cmap='magma',interpolation='nearest', animated=True) #initialize and show image once
ax[0].set_ylabel("Time"); ax[0].set_xlabel("Mel bands"); ax[0].set_title("Real-time Mel Spectrogram")
im0.set_clim(vmin=0, vmax=100)  # rescale colors #40, 90

im1 = ax[1].imshow(spec, aspect='auto', origin='lower',cmap='magma',interpolation='nearest', animated=True) #initialize and show image once
ax[1].set_ylabel("Time"); ax[1].set_xlabel("Mel bands"); ax[1].set_title("Real-time Mel Spectrogram")
im1.set_clim(vmin=0, vmax=100)  # rescale colors #40, 90

canvas = FigureCanvasTkAgg(fig, master=specFrame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side = tk.RIGHT) #fill=tk.BOTH, expand=True)

fig.tight_layout() 
# Draw once fully before capturing background
fig.canvas.draw()  # 1. draw everything
background = fig.canvas.copy_from_bbox(ax[0].bbox) # 2.snapshot clean background; no im data (the static parts: axes, ticks, grid, etc.)
backgroundd = fig.canvas.copy_from_bbox(ax[1].bbox) 



##################################################################
#-----------------------------------------------------
##################################################################

# ----------- NED plot ---------------------------------------

# Create NED plot
figNED = plt.figure(figsize=(8,8))
axNED = figNED.add_subplot(111, projection='3d')
canvasNED = FigureCanvasTkAgg(figNED, master=nedFrame)
canvasNED.get_tk_widget().pack()

axNED.set_title("NED Trajectory")
axNED.set_xlabel("North")
axNED.set_ylabel("East")
axNED.set_zlabel("Down")
axNED.grid(True)
#axNED.set_aspect("equal")
#axNED.legend()

ned_line, = axNED.plot([], [], [], color='blue')  # create empty 3d line object

# data storage 
max_data = 2000
north_data = deque(maxlen=max_data)
east_data = deque(maxlen=max_data)
down_data = deque(maxlen=max_data)


##################################################################
#
##################################################################

# ----------- active intensity plot ---------------------------------------

# create frame
intFrame = tk.Frame(master=frame5) #,padx=10, pady=10)
intFrame.pack(side="left")#grid(row=0, column=2)

intFig, (intAx, azAx) = plt.subplots(2, 1, figsize=(8, 8)) # one figure containing two subplots
intCanvas = FigureCanvasTkAgg(intFig, master=intFrame) #create canvas for figure
intCanvas.get_tk_widget().pack()

intAx.set_xlabel("Time")
intAx.set_ylabel("Active intensity")
intAx.set_title("Active Intensity Over Time")

azAx.set_xlabel("Time")
azAx.set_ylabel("Azimuth")
azAx.set_title("Azimuth Over Time")

# # create empty line objects
line1, = intAx.plot([], [], 'b')
line2, = intAx.plot([], [], 'r')
line3, = azAx.plot([], [], 'g')
line4, = azAx.plot([], [], 'm')

intAx.set_ylim(0,60)
azAx.set_ylim(0,360)

intFig.tight_layout()

intCanvas.draw()  # draw once fully

# data storage 
max_data = 100 
actv1 = deque(maxlen=max_data) 
actv2 = deque(maxlen=max_data)
tt1 = deque(maxlen=max_data)
tt2 = deque(maxlen=max_data)
az1 = deque(maxlen=max_data)
az2 = deque(maxlen=max_data)

#-----------------------------------------------------------------------

postUpdate = {}
def run(updateHapParams):

    print()
    print("-------- Updated Haptic Parameters -------")

    for param_name, entry_field in updateHapParams.items():
        get_param_value = entry_field.get()  #get() method: access/read content of Entry fields/user input
        
        if ((param_name == 'HAP_SENSE_AVS_R') or (param_name== 'HAP_MODE') or  (param_name =='HAP_IMU_UP_DOWN') or (param_name == 'HAP_SENSE_AVS_L') or  
            (param_name == 'HAP_SENSE_IMU')or (param_name == 'HAP_MULTIPLEX') or (param_name== 'HAP_DRV_EFFECT_T') or (param_name ==  'HAP_DRV_EFFECT_B')):

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

def run2(updateAvsParams):

    print()
    print("-------- Updated AVS Parameters -------")

    for param_name, entry_field in updateAvsParams.items():
        get_param_value = entry_field.get()  #get() method: access/read content of Entry fields/user input

        param_type =  mavutil.mavlink.MAV_PARAM_TYPE_INT32
        bytes_value = struct.pack('i', int(get_param_value))  # convert python values into binary data (bytes
        param_value = struct.unpack('f', bytes_value)[0] # convert binary data into python values 

        print(f"{param_name}: {param_value}")

        #send updated parameters to px4
        connection.mav.param_set_send(
        connection.target_system,
        connection.target_component,
        param_name.encode('utf-8'),
        param_value,
        param_type)



def getParams():
    storeHapParams = {} # dictionary: key,value pairs
    storeAvsParams = {}

    for names in all_params:
        #param_request_list_send() # requests ALL params 

        # Request haptic parameters only
        connection.mav.param_request_read_send(
        connection.target_system,
        connection.target_component,
        names.encode('utf-8'),
        -1)

        time.sleep(0.05) #0.01 #delay to ensure messages are received in order

        message = connection.recv_match(type='PARAM_VALUE', blocking=True,timeout=0.1) #0.1 #timeout

        if message is None:
            break
        
        print('getting parameters...')

        #print(f"{message.param_id}: {message.param_type}, {message.param_value}\n")

        if ((message.param_id == 'HAP_SENSE_AVS_R') or (message.param_id == 'HAP_MODE') or  (message.param_id  =='HAP_IMU_UP_DOWN') or 
            (message.param_id == 'HAP_SENSE_AVS_L') or (message.param_id == 'HAP_SENSE_IMU') or (message.param_id == 'HAP_MULTIPLEX') 
            or (message.param_id == 'HAP_DRV_EFFECT_T') or (message.param_id ==  'HAP_DRV_EFFECT_B')) and (message.param_type == 6):

            bytes_value = struct.pack('f', message.param_value)  # Pack as float
            int_value = struct.unpack('i', bytes_value)[0]  # Unpack as signed int32
            storeHapParams[message.param_id] = int_value

        elif message.param_type == 9:  # MAV_PARAM_TYPE_REAL32
            storeHapParams[message.param_id] = round(message.param_value,2)

        else:
            bytes_value = struct.pack('f', message.param_value)  # Pack as float
            int_value = struct.unpack('i', bytes_value)[0]  # Unpack as signed int32
            storeAvsParams[message.param_id] = int_value

    #print(storeAvsParams)

    # root.after(delay_ms, function, *args)
    print()
    print('---- parameters displayed in GUI ----')
    print()

    root.after(0, display_params, storeHapParams, storeAvsParams) # update gui from background thread; 0 ms delay to run as soon as possible


def display_params(storeHapParams,storeAvsParams):
    global updateHapParams, updateAvsParams

    lbl = tk.Label(frame, text= 'HAPTIC PARAMETERS:', font = "TkDefaultFont 18 bold") #, font = 'roman 12 bold') #, font = 'times 11 bold') #font = 'roman 10 bold'
    lbl.grid(row=0, column=0, sticky='w')

    updateHapParams ={}
    idx=0
    for name, value in storeHapParams.items(): 

        new = name + ' ' + hap_description[idx]
        
        # create Label to display text 
        lbl5 = tk.Label(frame, text = new) 
        lbl5.grid(row=idx+1,sticky = 'w')
        
        e = tk.Entry(frame)  # create Entry fields for user input
        e.insert(0, value) #insert default param values 

        e.grid(row=idx+1, column=1, padx=5, pady=5)
        updateHapParams[name]=e    # store user input with associated specification 
                                    # in a dictionary
        idx+=1
    
    ####
    avslbl = tk.Label(aresFrame, text= 'AVS PARAMETERS:', font = "TkDefaultFont 18 bold") #, font = 'roman 12 bold') #, font = 'times 11 bold') #font = 'roman 10 bold'
    avslbl.grid(row=0, column=0, sticky='w')

    updateAvsParams ={}
    avs_idx=0

    for name, value in storeAvsParams.items(): 

        new = name  + ' ' + avs_description[avs_idx]
        
        # create Label to display text 
        avslbl = tk.Label(aresFrame, text = new) 
        avslbl.grid(row=avs_idx+1,sticky = 'w')
        
        e = tk.Entry(aresFrame)  # create Entry fields for user input
        e.insert(0, value) #insert default param values 

        e.grid(row=avs_idx+1, column=1, padx=5, pady=5)
        updateAvsParams[name]=e    # store user input with associated specification 
                                    # in a dictionary
        avs_idx+=1

    # UPDATE Haptic params button 
    updateButton = tk.Button(frame, text = 'UPDATE', bg ='gray', fg= 'black', padx=5, pady=5, command=lambda: [run(updateHapParams)]) 
    updateButton.grid(row=idx+1, column=1, sticky='e', pady=5, padx=5)

    # UPDATE ARES params button 
    updateAvsButton = tk.Button(aresFrame, text = 'UPDATE', bg ='gray', fg= 'black', padx=5, pady=5, command=lambda: [run2(updateAvsParams)]) 
    updateAvsButton.grid(row=avs_idx+2, column=1, sticky='e', pady=10, padx=10)

    # sync time 
    sync_timeButton = tk.Button(frame, text = 'SYNC TIME', bg ='gray', fg= 'black', padx=5, pady=5, command=lambda: [sync_time()])
    sync_timeButton.grid(row=idx+1, column=1, sticky='w', pady=5, padx=5)

def set_timer():
    
    t = int(timerEntry.get()) # access user input   #15 #30

    # Record start time for 1-minute timer
    start_timer = time.time()
    end_timer = start_timer + t  # 1 minute from now

    print()
    print(f"Collecting data for: {t} seconds")
    print(f"Data collection start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_timer))}")

    return end_timer
#------------------------------------------------------------------------------
# Time synchronization thread
def sync_time(end_timer):
    """Send SYSTEM_TIME messages to both flight controllers"""

    while time.time() < end_timer: 
        # Get current UTC time in microseconds
        time_unix_usec =  int(time.time() * 1e6)

        # Send 
        if connection:
            connection.mav.system_time_send(time_unix_usec, 0)

        time.sleep(1.0)  # Send at 1 Hz


def logData(end_timer):
    global log_running

    log_stop_event.clear()  # reset on start; set to False 

    # create directory to store logging data
    dirName = 'sensor_avs_logging_data'

    # Create the directory
    try:
        os.mkdir(dirName)
        print(f"Directory '{dirName}' created successfully.")
        print()
    except FileExistsError:
        print(f"Directory '{dirName}' already exists.")
        print()

    # ------ write to CSV (logging) ------

    fieldnames = ['node_id','time_utc_usec', 'active_intensity', 'azimuth', 'elevation', 'yaw', 'pitch','roll', 'north', 'east', 'down']
    timestamp_str = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    csv_file_name = f"{timestamp_str}.csv"

    # Open CSV once at start (append mode)
    csv_file = open(os.path.join(dirName,csv_file_name), mode='a', newline='')
    csv_writer = csv.writer(csv_file) # 
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write header only if file is empty
    if csv_file.tell() == 0:
        csv_writer.writeheader()  

    message_id = 297 #message ID for SENSOR_AVS_LITE_EXT

    # drain messages in buffer before starting stream to avoid processing old messages
    while connection.recv_match(blocking=False) is not None:
        pass

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
    
    print('writing to csv..')

    while not log_stop_event.is_set() and time.time() < end_timer:   # run until stop signal; until is_set = True
        
        msg = connection.recv_match(type='SENSOR_AVS_LITE_EXT', blocking=True, timeout=0.1)   
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

            #  Thread-safe CSV write
            #  automatically acquires and releases a lock 
            with csv_lock: 
                csv_writer.writerow({
                    'node_id': id,
                    'time_utc_usec': t,
                    'active_intensity': act,
                    'azimuth': az, 
                    'elevation': el,
                    'yaw': yaw,
                    'pitch': pitch, 
                    'roll': roll,
                    'north': north, 
                    'east': east,
                    'down': down
                })
                csv_file.flush()

    csv_file.close()

    print()
    print('stopped logging') #, flush=True)  # flush forces immediate output
    
    log_running = False
    root.after(0, lambda: logButton.config(text='LOG DATA'))  # reset button on main thread
    #lambda allows us to pass arguments to the function; here we want to update the button text from the main thread after logging stops

log_running= False
def startLog():
    global log_running, end_timer, logButton

    if not log_running:

        # start thread
        log_running = True
        logButton.config(text='logging ..')

        end_timer = set_timer()
        
        threading.Thread(target=sync_time, args=(end_timer,), daemon=True).start()
        threading.Thread(target=logData,args=(end_timer,) ,daemon=True).start() #data logging thread

    else:
        # stop thread 
        log_running = False
        log_stop_event.set()  # signals thread to exit; stop = True 
        logButton.config(text='LOG DATA') 
        threading.Thread(target=stopSensorStreams, daemon=True).start()

rowFrame = tk.Frame(frame2) #Create a sub-frame inside intFrame to hold the row
rowFrame.grid(row=2, column=1) 

timerlbl = tk.Label(rowFrame, text= 'Timer (s):', font = "TkDefaultFont 17") 
timerlbl.grid(row=1, column=0, padx=5, pady=5) # pack(side = 'right', padx=5, pady=5)

# UPDATE button 
logButton = tk.Button(rowFrame, text = 'LOG DATA', bg ='gray', fg= 'black', padx=5, pady=5, command= startLog) #lambda: startLog() allows us to pass arguments to the function 
logButton.grid(row=2, column=1, padx=5, pady=5)

timerEntry = tk.Entry(rowFrame)  # create Entry fields for user input
timerEntry.insert(0, '15') #insert default threshold value 
timerEntry.grid(row=1, column=1, padx=5, pady=10) #pack(side = 'right', padx=5, pady=5)


# ###################################################################
nodes = []
def getFPV_data():
    fpv_stop_event.clear()  # reset on start; set to False 

    message_id = 297 #message ID for SENSOR_AVS_LITE_EXT

    # drain messages in buffer before starting stream to avoid processing old messages
    while connection.recv_match(blocking=False) is not None:
        pass

    print()
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
    
    #print('check fpv stop event getFPV:', fpv_stop_event.is_set()) 

    while not fpv_stop_event.is_set():   # run until stop signal; until is_set = True
        
        msg = connection.recv_match(type='SENSOR_AVS_LITE_EXT', blocking=True, timeout=0.1)   
        #print(msg)

        #check if msg arrived 
        if msg: 
            t = msg.time_utc_usec
            id = msg.device_id
            act = msg.active_intensity
            az = msg.azimuth_deg
            el = msg.elevation_deg

            yaw = msg.yaw
            roll = msg.roll
            pitch = msg.pitch

            dataQ.put((t,id,act,az,el,yaw,roll,pitch))

            if id not in nodes:
                nodes.append(id)

def getNED_data():
    # reset on start; set to False 
    traj_stop_event.clear()

    message_id = 297 #message ID for SENSOR_AVS_LITE_EXT

    # drain messages in buffer before starting stream to avoid processing old messages
    while connection.recv_match(blocking=False) is not None:
        pass

    print()
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
    
    while not traj_stop_event.is_set():   # run until stop signal; until is_set = True
        
        msg = connection.recv_match(type='SENSOR_AVS_LITE_EXT', blocking=True, timeout=0.1)   
        #print(msg)

        #check if msg arrived 
        if msg: 
            north = msg.north
            east = msg.east
            down = msg.down
            t= msg.time_utc_usec

            dataNEDQ.put((north,east,down,t))

def updatePlots():
    "------------------ HEAD PLOTS ------------------------"

    global background2, background3, background4, updateHapParams, nodes
    global updateXaz_r, updateYaz_r, updateXaz_l, updateYaz_l,updateY_el, updateX_el, act_l, act_r

    if not fpv_running:
        return  # stop rescheduling cleanly

    try:
        t, id, act, az,el, yaw,roll, pitch = dataQ.get_nowait()
    #print('north:', north)
    except queue.Empty:
         root.after(1,updatePlots)
         return

    act0 = 0
    if updateHapParams:
        try:
            act0 = float(updateHapParams['HAP_ACT_INT'].get())
        except ValueError:
            act0 = 0  # fallback if value is invalid/incomplete

    if len(nodes) == 1:
        if id == nodes[0]:
            act_l = act
            updateYaz_l = 1.15*np.cos(np.deg2rad(az))  #X #az 
            updateXaz_l = 1.15*np.sin(np.deg2rad(az))  #Y

            updateY_el = 1.15*np.cos(np.deg2rad(el))  #X 
            updateX_el = 1.15*np.sin(np.deg2rad(el))  #Y

    else:
        if len(nodes) < 2:
            root.after(1, updatePlots)
            return  # wait until both nodes are known
        
        if id == nodes[0]:
            act_l = act
            updateYaz_l = 1.15*np.cos(np.deg2rad(az))  #X #az 
            updateXaz_l = 1.15*np.sin(np.deg2rad(az))  #Y

            updateY_el = 1.15*np.cos(np.deg2rad(el))  #X 
            updateX_el = 1.15*np.sin(np.deg2rad(el))  #Y
    
        if id == nodes[1]:
            act_r = act
            updateYaz_r = 1.15*np.cos(np.deg2rad(az))  #X #az 
            updateXaz_r = 1.15*np.sin(np.deg2rad(az))  #Y

    #fig.canvas.restore_region(background) 
    # restore background of head plots; only copies pixels back
    canvas3.restore_region(background2)   
    canvas4.restore_region(background3)   
    canvas5.restore_region(background4)
    canvas6.restore_region(background6)

    #flipped to start at 90 degree and rotate clockwise
    updateYyaw = 1.15*np.cos(np.deg2rad(yaw))  #X #yaw
    updateXyaw = 1.15*np.sin(np.deg2rad(yaw))  #Y

    if int(updateHapParams['HAP_IMU_UP_DOWN'].get()) == 0:  # up/down mode

        #flipped to start at 90 degree and rotate clockwise
        updateY_up_down = 1.15*np.cos(np.deg2rad(roll))  #X #roll
        updateX_up_down = 1.15*np.sin(np.deg2rad(roll))  #Y
    else: 
        # flipped to start at 90 degree and rotate clockwise
        updateY_up_down = 1.15*np.cos(np.deg2rad(pitch))  #X #pitch
        updateX_up_down = 1.15*np.sin(np.deg2rad(pitch))  #Y

    circle_red_yaw.set_center((updateXyaw, updateYyaw))
    ax5.draw_artist(circle_red_yaw)
    canvas5.blit(ax5.bbox)

    circle_red_roll.set_center((updateX_up_down, updateY_up_down))
    ax6.draw_artist(circle_red_roll)
    canvas6.blit(ax6.bbox)

    if act_l > act0 or act_r > act0:

        # plot azimuth right and left nodes
        circle_red_az_r.set_center((updateXaz_r, updateYaz_r))  # set_center() updates/moves circle
        circle_green_az_l.set_center((updateXaz_l, updateYaz_l))

        # draw artists
        ax3.draw_artist(circle_red_az_r)   # redraws circle in new location 
        ax3.draw_artist(circle_green_az_l)

        # elevation plot    
        circle_red_elev.set_center((updateX_el, updateY_el))
        ax4.draw_artist(circle_red_elev)   # redraws circle in new location 

        canvas3.blit(ax3.bbox) 
        canvas4.blit(ax4.bbox) 

    # tkinter timer/scheduler 
    # schedules updates without blocking so GUI stays responsive
    root.after(1, updatePlots)  #passes results back to main thread to update GUI

fpv_running= False
def startFPV():
    global fpv_running

    if not fpv_running:

        # start thread
        fpv_running = True
        plotButton.config(text='RUNNING...')

        print('check fpv stop event START:', fpv_stop_event.is_set())
        threading.Thread(target=getFPV_data, daemon=True).start() #fpv thread to acquire data in background
    
        root.after(50, updatePlots) 
    else:
        # stop thread 
        fpv_running = False
        fpv_stop_event.set()  # signals thread to exit; stop = True 
        plotButton.config(text='PLOT')

        threading.Thread(target=stopSensorStreams, daemon=True).start()

# UPDATE button 
plotButton = tk.Button(frame2, text = 'PLOT', bg ='gray', fg= 'black', padx=5, pady=5, command=startFPV) #lambda: [updatePlots()]) 
#plotButton.pack(side='bottom', pady=10, padx=10)
plotButton.grid(row=2, column=0, padx=5, pady=5)

specNodes = []
def getSpecData ():
    spec_stop_event.clear()  # reset on start; clear any previous stop signals

    message_id = 292 #message ID for SENSOR_AVS

    # drain any leftover messages
    while connection.recv_match(blocking=False) is not None:  #false returns immediately if no message
        pass

    print("")
    print("--- sending command_long to stream sensor_avs data for mel specs---")  
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

    msg2 = connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command # waits for message to arrive 
    print("ACK:",msg2) 
    print('')

    if not connection:
        return

    while not spec_stop_event.is_set():   # run until stop signal is received # is_set     
     
        msg = connection.recv_match(type='SENSOR_AVS', blocking=True,timeout=0.1)  
        # print(msg)

        #check if msg arrived 
        if msg: 
            mel_intensity = msg.mel_intensity
            id = msg.device_id

            dataQSpec.put((id, mel_intensity))

            if id not in specNodes:
                specNodes.append(id)
    
def plotSpectrogram():
    global ind, spec, specNodes, spec2

    if not spec_running:
        return  # stop rescheduling cleanly

    try:
        id, mel_intensity = dataQSpec.get_nowait() 

    except queue.Empty:
        root.after(1,plotSpectrogram)
        return
    
    if len(specNodes) == 1:
        if id == specNodes[0]:
            fig.canvas.restore_region(background)  
            
            # Update spectrogram data
            new_row = mel_intensity  # shape: (16,)
            spec = np.roll(spec, -1, axis=0)   # rolls vertically 
            spec[-1, :] = new_row  

            # Update the image with new data
            im0.set_data(spec)
            ax[0].draw_artist(im0)        # Redraw just the changed artist
            fig.canvas.blit(ax[0].bbox)  # Blit the updated area (blit on screen)
            fig.canvas.flush_events()  

    else:
        if len(specNodes) < 2:
            root.after(1, plotSpectrogram)
            return  # wait until both nodes are known

        if id == specNodes[0]:
            fig.canvas.restore_region(background)  
            
            # Update spectrogram data
            new_row = mel_intensity  # shape: (16,)
            spec = np.roll(spec, -1, axis=0)   # rolls vertically 
            spec[-1, :] = new_row  

            # Update the image with new data
            im0.set_data(spec)
            ax[0].draw_artist(im0)        # Redraw just the changed artist
            fig.canvas.blit(ax[0].bbox)  # Blit the updated area (blit on screen)
            fig.canvas.flush_events()  
        
        # right node 
        if id == specNodes[1]:
            fig.canvas.restore_region(backgroundd)  
            # Update spectrogram data
            new_row = mel_intensity  # shape: (16,)
            spec2 = np.roll(spec2, -1, axis=0)   # rolls vertically 
            spec2[-1, :] = new_row  

            # Update the image with new data
            im1.set_data(spec2)
            ax[1].draw_artist(im1)        # Redraw just the changed artist
            fig.canvas.blit(ax[1].bbox)  # Blit the updated area (blit on screen)
            fig.canvas.flush_events() 

    root.after(1, plotSpectrogram)  # Schedule next update

spec_running = False
def startSpectrogram():
    global  spec_running

    if not spec_running:
        spec_running = True

        spec.fill(0)  # clear old data
        spec2.fill(0)

        specButton.config(text='RUNNING..')  # re-enable plot button when spectrogram is stopped
        threading.Thread(target=getSpecData, daemon=True).start() #restart fpv thread to acquire data in background
        
        root.after(50, plotSpectrogram)

    else:
        spec_running = False
        spec_stop_event.set()  # signals thread to exit
        specButton.config(text='PLOT SPEC')

        threading.Thread(target=stopSensorStreams, daemon=True).start()  #stop streams in background to avoid blocking GUI

# UPDATE button 
specButton = tk.Button(frame3, text = 'PLOT SPEC', bg ='gray', fg= 'black', padx=5, pady=5, command= startSpectrogram)  
specButton.grid(row=2, column=1, padx=5, pady=5)

def plotTrajectory():

    if not traj_running:
        return  # stop rescheduling cleanly

    try: 
        north, east, down,t =dataNEDQ.get_nowait()
    except queue.Empty:
         root.after(1,plotTrajectory)
         return
 
    north_data.append(north)
    east_data.append(east)
    down_data.append(down)  

    ned_line.set_data(north_data, east_data)
    ned_line.set_3d_properties(down_data)

    # manually set limits based on current data
    if len(north_data) > 1:
        axNED.set_xlim(min(north_data), max(north_data))
        axNED.set_ylim(min(east_data), max(east_data))
        axNED.set_zlim(min(down_data), max(down_data))
    
    canvasNED.draw_idle() # 
    root.after(1, plotTrajectory)


traj_running = False
def startTrajectory():
    global traj_running

    if not traj_running:
        traj_running = True

        north_data.clear(); east_data.clear(); down_data.clear()  # clear old data  
        ned_line.set_data([], []) # clear old line data
        ned_line.set_3d_properties([]) 
        
        trajButton.config(text='RUNNING..')  # re-enable plot button when spectrogram is stopped
        threading.Thread(target=getNED_data, daemon=True).start() #restart fpv thread to acquire data in background
        
        root.after(50, plotTrajectory) 

    else:
        traj_running = False
        traj_stop_event.set()  # signals thread to exit/stop
        trajButton.config(text='PLOT TRAJECTORY')

        threading.Thread(target=stopSensorStreams, daemon=True).start()  #stop streams in background to avoid blocking GUI

# UPDATE button 
trajButton = tk.Button(nedFrame, text = 'PLOT TRAJECTORY', bg ='gray', fg= 'black', padx=5, pady=5, command= startTrajectory)  
trajButton.pack(side='bottom', pady=5, padx=10)

act_start_time = None
actNodes = []
def getActiveIntensity():
    # reset on start; set to False 
    actv_stop_event.clear()

    message_id = 297 #message ID for SENSOR_AVS_LITE_EXT

    # drain any leftover messages
    while connection.recv_match(blocking=False) is not None:  #false returns immediately if no message
        pass

    print("")
    print("--- sending command_long to stream sensor_avs_lite_ext data for active intensity---")  
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

    msg2 = connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command # waits for message to arrive 
    print("ACK:",msg2) 
    print('')
    
    "data acquisition thread"
    "write to queue and csv file"
    
    if not connection:
        return

    while not actv_stop_event.is_set():   # run until stop signal; until is_set = True
        
        msg = connection.recv_match(type='SENSOR_AVS_LITE_EXT', blocking=True, timeout=0.1)   
        #print(msg)

        #check if msg arrived 
        if msg: 
            t = msg.time_utc_usec
            id = msg.device_id
            act = msg.active_intensity
            az = msg.azimuth_deg
            # el = msg.elevation_deg

            dataQAct.put((t,id,act,az))

            if id not in actNodes:
                actNodes.append(id)

window = 10  # rolling window width 
def plotActiveIntensity():
    global actNodes, act_start_time

    if not actv_running:
        return  # stop rescheduling cleanly

    # drain ALL pending messages from queue to prevent lag buildup
    changed = False
    thresh = int(threshEntry.get())

    while True: # ensures we process all data and only update plot once per frame
        try:
            t, id, act, az = dataQAct.get_nowait()
        except queue.Empty:
            break

        changed = True

        # Set start time on first message
        if act_start_time is None:
            act_start_time = t

        # Convert to elapsed seconds
        t_elapsed = (t - act_start_time) / 1e6  # microseconds -> seconds

        if len(actNodes) == 1:
            if id == actNodes[0]:
                tt1.append(t_elapsed)
                actv1.append(act)
                az1.append(az)

        else:
            if len(actNodes) < 2:
                continue # wait until we have data from both nodes to plot
            if id == actNodes[0]:
                tt1.append(t_elapsed)
                actv1.append(act)
                az1.append(az)
            if id == actNodes[1]:
                tt2.append(t_elapsed)
                actv2.append(act)
                az2.append(az)

    # only redraw when we actually received new data
    if changed:
        # --- update line data ---
        line1.set_data(np.array(tt1), np.array(actv1))

        az1thresh = np.array(az1, dtype=float)
        az1thresh[np.array(actv1) < thresh] = np.nan
        line3.set_data(np.array(tt1), az1thresh)

        if len(actNodes) >= 2: 
            line2.set_data(np.array(tt2), np.array(actv2))

            az2thresh = np.array(az2, dtype=float)
            az2thresh[np.array(actv2) < thresh] = np.nan
            line4.set_data(np.array(tt2), az2thresh)

        # --- sliding x-axis window ---
        curr_time = max( # current time is the max of the most recent timestamps from each node (or 0 if no data)
            (tt1[-1] if tt1 else 0),  # grab last (most recent) timestamp from node 1 (or 0 if no data)
            (tt2[-1] if tt2 else 0) 
        )
        if curr_time <= window:
            t_min = 0
            t_max = window
        else:
            t_min = curr_time - window
            t_max = curr_time + 1

        intAx.set_xlim(t_min, t_max)
        azAx.set_xlim(t_min, t_max)

        # full redraw so axes update
        intCanvas.draw_idle()

    root.after(16, plotActiveIntensity)  # give time for GUI to update


actv_running = False
def startActiveIntensity():

    global actv_running, act_start_time

    if not actv_running:
        act_start_time = None  # reset on each new run

        actNodes.clear()  
        tt1.clear(); actv1.clear(); az1.clear() #clear data for new run
        tt2.clear(); actv2.clear(); az2.clear()
        line1.set_data([], []); line2.set_data([], [])  #clear line data
        line3.set_data([], []); line4.set_data([], [])

        actv_running = True
        actvButton.config(text='RUNNING..')  # re-enable plot button when spectrogram is stopped
        threading.Thread(target=getActiveIntensity, daemon=True).start() #restart fpv thread to acquire data in background

        root.after(1, plotActiveIntensity) # Schedule first update for both active intensity and azimuth

    else:
        actv_running = False
        actv_stop_event.set()  # signals thread to exit
        actvButton.config(text='PLOT ACTIVE INTENSITY')

        threading.Thread(target=stopSensorStreams, daemon=True).start()  #stop streams in background to avoid blocking GUI

rowFrame = tk.Frame(intFrame) #Create a sub-frame inside intFrame to hold the row
rowFrame.pack() 

actvButton = tk.Button(intFrame, text = 'PLOT ACTIVE INTENSITY', bg ='gray', fg= 'black', command= startActiveIntensity) #lambda: [startActiveIntensity(), startAz()])
actvButton.pack(side='bottom', pady=5, padx=5)

threshlbl = tk.Label(rowFrame, text= 'Threshold:', font = "TkDefaultFont 17") 
threshlbl.pack(side = 'left', padx=5, pady=5)

threshEntry = tk.Entry(rowFrame)  # create Entry fields for user input
threshEntry.insert(0, '15') #insert default threshold value 
threshEntry.pack(side = 'left', padx=5, pady=5)


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

# Time synchronization for button 
def sync_time():
    """Send SYSTEM_TIME messages to flight controller"""

    print()
    print('-- time synced --')
    print()

    time_unix_usec = int(time.time() * 1e6)     # Get current UTC time in microseconds
    connection.mav.system_time_send(time_unix_usec, 0) # send time to FC


def runThreads():

    stopSensorStreams()  # stop streams
    sync_time() #sync system

    t1 = threading.Thread(target=getParams, daemon=True)
    t1.start()
    t1.join()  # Wait for the parameter retrieval thread to finish before starting the plotting thread


# run threads in background, keeping GUI free
threading.Thread(target=runThreads, daemon=True).start()

root.mainloop() #drives all GUI updates 
