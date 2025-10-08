# px4_comm.py
# communicate with px4: send/receive messages

from pymavlink import mavutil
import serial

import sys
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd  # data analysis & manipulation library 

import tkinter as tk
from tkinter import ttk 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import matplotlib.image as mpimg 
import threading
import queue 
from collections import deque 

import csv
import datetime

# ------ write to CSV (logging) ------

# timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# csvFilename = f"px4_data_{timestamp_str}.csv"
# fieldnames = ['north','east','down', 'yaw', 'pitch', 'roll']

# # Open CSV once at start (append mode)
# csv_file = open(csvFilename, mode='a', newline='')
# csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

# # Write header only if file is empty
# if csv_file.tell() == 0:
#     csv_writer.writeheader()


# queue for data; type of data structure 
dataQ = queue.Queue() # FIFO: first-in, first-out 

#deque;  stack data structure
de = deque() # add/remove elements from both ends; FIFO and LIFO (last-in, first-out)


# set mavlink dialect
mavutil.set_dialect("development")

# Start a listening connection
the_connection = mavutil.mavlink_connection(device='COM5', baud=115200) 

# # Wait for the first heartbeat
# #   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

# sensor_avs message ID
message_id = 292 
#print("message_id: ",message_id)

message = the_connection.mav.command_long_encode(   
        the_connection.target_system,  # Target system ID
        the_connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
        0,  # Confirmation
        message_id,   # param1: Message ID to be streamed
        50000, # param2: Interval in microseconds
        0,0,0,0,0)
print(message)

# # Send the COMMAND_LONG
the_connection.mav.send(message)

msg2 = the_connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
print(msg2) 
print('')

# ------- serial port connnection ---------
try:
    # initialize and open serial port (if port is given)
    serialPort = serial.Serial(port='COM4', baudrate=115200, timeout=1) #115200
    time.sleep(2)  # Wait for Arduino to reset

except serial.SerialException:
    print("could not open arduino serial port")


# # -------------------------- Launch the GUI ----------------------------------------
#def runGUI():
 #       pass

root = tk.Tk()
#get computers screen dimensions 
screen_width = root.winfo_screenwidth()    #print('screen_width:', screen_width )
screen_height = root.winfo_screenheight()  #print('screen_height:', screen_height)

# root window title & set display dimension to fit users screen
root.title("GUI")
#.7, .6
root.geometry(f"{int(screen_width*.7)}" + 'x' + f"{int(screen_height*.6)}")  #width x height+x+y

# label frame for plots (head and spectrogam) 
plot_frame = tk.LabelFrame(root, padx=10, pady=10)
plot_frame.pack(side='top', fill="both", expand=True,  padx=10, pady=10)

img = mpimg.imread("head_topview.jpg")

#plot button
# plotBtn = tk.Button(master=plot_frame, text = 'PLOT', bg = 'gray', fg ='black',
#                 width=8, height=1, padx=5, pady=5, command=lambda: plot())
# plotBtn.pack(side="top", padx=10)  #grid(row = 2, column=3, sticky= 'E') #, sticky=tk.W)

quitButton =  tk.Button(plot_frame, text = 'QUIT', bg ='red', fg= 'black',
                                width=8, height=1, padx=5, pady=5, command= root.quit) #root.destroy
quitButton.pack(side="top") 

#def createImgPlot(self):
# create frame
imgFrame = tk.Frame(master=plot_frame) #,padx=10, pady=10)
imgFrame.pack(side="left")#grid(row=0, column=2)
#create plot with slider value updates 

# frame for spectrogram plot
specFrame = tk.Frame(master=plot_frame) #,padx=10, pady=10)
specFrame.pack(side="right")

# frame for NED plot
nedFrame = tk.Frame(master=plot_frame) #,padx=10, pady=10)
nedFrame.pack(side="right")

fig3, ax3 = plt.subplots(figsize=(5,4)) 
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
circle_red = plt.Circle((0,0), 0.05, color='red')
ax3.add_patch(circle_red)

circle_blue = plt.Circle((0,0), 0.05, color='blue')
ax3.add_patch(circle_blue)

canvas3.draw()  # initial draw
background2 = canvas3.copy_from_bbox(ax3.bbox)

# ------------------------------------------------------------------------------------
ind = 0
ind2=0
spec = np.zeros((60,16)) # storage for spectrogram; x: time steps to keep visible; y: number of mel bands

fig, ax = plt.subplots(figsize=(5,4))
im = ax.imshow(spec, aspect='auto', origin='lower',cmap='magma',interpolation='nearest', animated=True) #initialize and show image once
ax.set_ylabel("Time"); ax.set_xlabel("Mel bands"); ax.set_title("Real-time Mel Spectrogram")
im.set_clim(vmin=40, vmax=90)  # rescale colors
#plt.draw # redraws entire figure (axes, labels, ticks, background, image, etc)

canvas = FigureCanvasTkAgg(fig, master=specFrame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side = tk.RIGHT) #fill=tk.BOTH, expand=True)

# # Tell matplotlib we will use blitting
# # blitting -- aka block image transfer; plots only part of an image that have changed instead of entire figure 
background = fig.canvas.copy_from_bbox(ax.bbox) # saves a clean background (the static parts: axes, ticks, grid, etc.)

# # Draw initial state
ax.draw_artist(im)
fig.canvas.blit(ax.bbox)  #bbox- bounding box 

# ----------- NED plot ---------------------------------------
# --- inside your GUI setup section ---

# Create NED plot
figNED = plt.figure(figsize=(4,4))
axNED = figNED.add_subplot(111, projection='3d')
canvasNED = FigureCanvasTkAgg(figNED, master=nedFrame)
canvasNED.get_tk_widget().pack()


axNED.set_title("NED Trajectory")
axNED.set_xlabel("North [km]")
axNED.set_ylabel("East [km]")
axNED.set_zlabel("Down km]")
axNED.grid(True)
#axNED.set_aspect("equal")
axNED.legend()
#north_data, east_data, down_data = [], [], []
#line, = axNED.plot([],[],[])

# data storage 
max_data = 2000
north_data = deque(maxlen=max_data)
east_data = deque(maxlen=max_data)
down_data = deque(maxlen=max_data)
#
# data acquisition thread
def getFPV_data():
    # timer for data collection
    #t_end = time.time() + 10 #run for 5 seconds
    while True: #time.time() < t_end:                   # COMMAND_ACK  #UNKNOWN_292 type='SENSOR_AVS', 
        msg = the_connection.recv_match(blocking=True)  # receives all the messages available 

        if msg is None:
             continue
        try:
            azimuth_deg = the_connection.messages['SENSOR_AVS'].azimuth_deg #float                                         
            mel_intensity = the_connection.messages['SENSOR_AVS'].mel_intensity #list              
            # active_intensity = the_connection.messages['SENSOR_AVS'].active_intensity
            # q_factor = the_connection.messages['SENSOR_AVS'].q_factor   

            yaw = the_connection.messages['ATTITUDE'].yaw
            pitch = the_connection.messages['ATTITUDE'].pitch                                      
            roll = the_connection.messages['ATTITUDE'].roll                   

            north = the_connection.messages['LOCAL_POSITION_NED'].x  # N
            east = the_connection.messages['LOCAL_POSITION_NED'].y  # E
            down = the_connection.messages['LOCAL_POSITION_NED'].z  # -D   

        except KeyError:
             continue

        dataQ.put(( north, east, down,yaw,pitch,roll,azimuth_deg, mel_intensity )) #((north,east,down, yaw, pitch, roll))     
        
        # ----- write to csv -----
        ##writer.writerow({'azimuth deg': azimuth_deg,'q factor': q_factor,'yaw': yaw, 'pitch': pitch,'roll': roll, 'active intensity': active_intensity, 'mel intensity': mel_intensity})
        
        # csv_writer.writerow({'north': north,'east': east, 'down': down, 'yaw': yaw, 'pitch': pitch,'roll': roll})
        # csv_file.flush()  #if programs stopped, will save last few rows

        #return north, east, down,yaw,pitch,roll,azimuth_deg, mel_intensity  
      
                                
def updateSpectrogram():
        # # --------------------- Spectrogram ----------------------
    global ind,background2,spec

#    north, east, down,yaw,pitch,roll,azimuth_deg,mel_intensity   = getFPV_data()

    try:
          north, east, down,yaw,pitch,roll,azimuth_deg, mel_intensity = dataQ.get_nowait() #north, east, down,yaw,pitch,roll 
         #print(mel_intensity)
    #print('north:', north)
    except queue.Empty:
         root.after(1,updateSpectrogram)
         return
    

    roll = (math.degrees(roll) +360) % 360 #normalize roll
    #print('roll:', roll)

    # if 65 <= active_intensity < 70: 
    #     size = 1.5
    # elif 70 <= active_intensity < 75: 
    #     size = 2
    # elif 75 <= active_intensity < 80: 
    #     size = 2.5
    # elif 80 <= active_intensity < 85: 
    #     size = 3
    # elif 85 <= active_intensity < 90: 
    #     size = 3.5
    # elif 90 <= active_intensity < 95: 
    #     size = 4
    # else:
    #     size =1 

    # restore background of spectrogram and the head plots; only copies pixels back
    fig.canvas.restore_region(background) 
    canvas3.restore_region(background2)   

    #Update spectrogram data 
    new_row = mel_intensity  # shape: (16,)
    spec = np.roll(spec, -1, axis=0)   # rolls vertically 
    spec[-1, :] = new_row              # insert data in new row

    #flipped to start at 90 degree and rotate clockwise
    updateYaz = 1*np.cos(azimuth_deg)  #X #az 
    updateXaz = 1*np.sin(azimuth_deg)  #Y
    updateYyaw = 1.25*np.cos(yaw)  #X #yaw
    updateXyaw = 1.25*np.sin(yaw)  #Y

    ind = ind+1
    # count to 5 before plotting then reset to 0
    if ind == 5:
            #Update data: change your artist
            im.set_data(spec)         # update existing image; replace old array without creating new imshow object
            ax.draw_artist(im)        # Redraw just the changed artist
            fig.canvas.blit(ax.bbox)  # Blit the updated area (blit on screen)

            circle_red.set_center((updateXaz, updateYaz))  # set_center() updates/moves circle
            # circle_red.set_radius((0.05 * size)) 
            circle_blue.set_center((updateXyaw, updateYyaw))

            # draw artists
            ax3.draw_artist(circle_red)   # redraws circle in new location 
            ax3.draw_artist(circle_blue)
            canvas3.blit(ax3.bbox) 

            ind = 0

    # tkinter timer/scheduler 
    # schedules updates without blocking so GUI stays responsive
    root.after(1, updateSpectrogram) # after 1ms run updateSpectrogram() without freezing/lag in tkinter


# def plotTrajectory():

#     # read CSV file
#     df = pd.read_csv('px4_data_2025-10-07_07-35-25.csv')
#     #df = pd.read_csv('px4_data_2025-10-06_20-17-55.csv')

#     north, east, down = df['north'],df['east'],df['down']

#     axNED.plot(north, east, down) 

def realtimeTrajectory():
    global ind2

    north, east, down,yaw,pitch,roll,azimuth_deg, mel_intensity =dataQ.get(timeout=1)

    north_data.append(north)
    east_data.append(east)
    down_data.append(down)  

    ind2 = ind2 +1

    if ind2 == 20:
        axNED.cla() # clear previous frame
        axNED.plot(north_data, east_data, down_data) 
        #line, = axNED.plot([],[],[])

        # line.set_data(north_data, north_data)
        # line.set_3d_properties(down_data)
        ## axNED.view_init(elev=30, azim=(time.time() * 15) % 360)  # rotate plot
    
        canvasNED.draw_idle()
        ind2 = 0

    root.after(1, realtimeTrajectory)



# def arduinoComm():
#     pass
#     # communicate with Arduino to play haptic feedback
#     while True:
#         try:
#             north, east, down,yaw,pitch,roll,azimuth_deg, mel_intensity =dataQ.get(timeout=1) # north,east,down,yaw, pitch, roll

#         except queue.Empty:
#             root.after(1, updateSpectrogram)
#             return

     
#      #   north, east, down,yaw,pitch,roll,azimuth_deg,mel_intensity =getFPV_data()
#         #print(yaw)

#         deg = (math.degrees(yaw) +360) % 360 #normalize yaw
#         print("deg:",deg)
   
#         if serialPort and serialPort.is_open:
#             if 135 <= deg < 180: 
#                 serialPort.write('R'.encode())
#                 #serialPort.write(b'R')
#             elif 180 <= deg < 225: 
#                 serialPort.write('L'.encode())
#             else:
#                 serialPort.write('C'.encode())

#             time.sleep(0.05)


# -------- threads ---------
threading.Thread(target=getFPV_data, daemon=True).start()
#updateSpectrogram()
#plotTrajectory()
#threading.Thread(target=arduinoComm, daemon=True).start()
updateSpectrogram()
realtimeTrajectory()
root.mainloop()




################################################
################################################

# # run GUI on a separate thread
# threading.Thread(target=runGUI, daemon=True).start()

# from queue import Queue
# q = Queue()
# # The key methods available are:
# qsize() # - Get the size of the queue
# empty() # - Check if queue is empty
# full() # - Check if queue is full
# put(item) # - Put an item into the queue
# get() # - Remove and return an item from the queue
# join() # - Block until all tasks are processed