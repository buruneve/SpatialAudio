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



# queue for data; type of data structure 
dataQ1 = queue.Queue() # FIFO: first-in, first-out 
dataQ2 = queue.Queue() # FIFO: first-in, first-out 

#deque;  stack data structure
de = deque() # add/remove elements from both ends; FIFO and LIFO (last-in, first-out)

# set mavlink dialect
mavutil.set_dialect("development")

# Start a listening connection
the_connection2 = mavutil.mavlink_connection(device='COM7', baud=57600) #COM6  115200
the_connection1 = mavutil.mavlink_connection(device='COM9', baud=57600)

# # Wait for the first heartbeat
# #   This sets the system and component ID of remote system for the link
the_connection1.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection1.target_system, the_connection1.target_component))
the_connection2.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection2.target_system, the_connection2.target_component))


# sensor_avs message ID
message_id = 292

message1 = the_connection1.mav.command_long_encode(   
        the_connection1.target_system,  # Target system ID
        the_connection1.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
        0,  # Confirmation
        message_id,   # param1: Message ID to be streamed
        50000, # param2: Interval in microseconds
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
        50000, # param2: Interval in microseconds
        0,0,0,0,0)
print(message2)

# # Send the COMMAND_LONG
the_connection2.mav.send(message2)

msg2 = the_connection2.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
print(msg2) 
print('')


# # -------------------------- Launch the GUI ----------------------------------------
root = tk.Tk()
#get computers screen dimensions 
screen_width = root.winfo_screenwidth()    #print('screen_width:', screen_width )
screen_height = root.winfo_screenheight()  #print('screen_height:', screen_height)

# root window title & set display dimension to fit users screen
root.title("GUI")
root.geometry(f"{int(screen_width*.7)}" + 'x' + f"{int(screen_height*.6)}")  #width x height+x+y

# label frame for plots (head and spectrogam) 
plot_frame = tk.LabelFrame(root, padx=10, pady=10)
plot_frame.pack(side='top', fill="both", expand=True,  padx=10, pady=10)
img = mpimg.imread("head_topview.jpg")

quitButton =  tk.Button(plot_frame, text = 'QUIT', bg ='red', fg= 'black',
                                width=8, height=1, padx=5, pady=5, command= root.quit) #root.destroy
quitButton.pack(side="top") 

# create frame
imgFrame = tk.Frame(master=plot_frame) #,padx=10, pady=10)
imgFrame.pack(side="left")#grid(row=0, column=2)
#create plot with slider value updates 

# frame for spectrogram plot
specFrame = tk.Frame(master=plot_frame) #,padx=10, pady=10)
specFrame.pack(side="right")


# ---- directional head plot --------
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
# spectrograms
ind =0
ind2=0
spec = np.zeros((60,16)) # storage for spectrogram; x: time steps to keep visible; y: number of mel bands
spec2 = np.zeros((60,16))

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,4))
im1 = ax1.imshow(spec, aspect='auto', origin='lower',cmap='magma',interpolation='nearest', animated=True) #initialize and show image once
ax1.set_ylabel("Time"); ax1.set_xlabel("Mel bands"); ax1.set_title("Real-time Mel Spectrogram")
im1.set_clim(vmin=40, vmax=90)  # rescale colors
#plt.draw # redraws entire figure (axes, labels, ticks, background, image, etc)

im2 = ax2.imshow(spec2, aspect='auto', origin='lower',cmap='magma',interpolation='nearest', animated=True) #initialize and show image once
ax2.set_ylabel("Time"); ax2.set_xlabel("Mel bands"); ax2.set_title("Real-time Mel Spectrogram")
im2.set_clim(vmin=40, vmax=90)  # rescale colors

# Adjust spacing between subplots
plt.tight_layout()

canvas = FigureCanvasTkAgg(fig, master=specFrame)
canvas_widget1 = canvas.get_tk_widget()
canvas_widget1.pack(side = tk.RIGHT) #fill=tk.BOTH, expand=True)

# # Tell matplotlib we will use blitting
# # blitting -- aka block image transfer; plots only part of an image that have changed instead of entire figure 
background = fig.canvas.copy_from_bbox(fig.bbox) # saves a clean background (the static parts: axes, ticks, grid, etc.)
ax1.draw_artist(im1) # Draw initial state
ax2.draw_artist(im2) # Draw initial state
fig.canvas.blit(fig.bbox)  #bbox- bounding box 

# data acquisition thread
def getFPV_data1():
    
    """thread for connection 1"""

    while True: #time.time() < t_end:                   # COMMAND_ACK  #UNKNOWN_292 type='SENSOR_AVS', 
        msg1 = the_connection1.recv_match(blocking=True)  # type='SENSOR_AVS',  receive only SENSOR_AVS messages   #print(sys.getsizeof(msg))

        if msg1: 
            azimuth_deg = the_connection1.messages['SENSOR_AVS'].azimuth_deg #float               
            mel_intensity = the_connection1.messages['SENSOR_AVS'].mel_intensity #list              
            active_intensity = the_connection1.messages['SENSOR_AVS'].active_intensity
            #q_factor = the_connection1.messages['SENSOR_AVS'].q_factor  
            yaw = the_connection1.messages['ATTITUDE'].yaw
            pitch = the_connection1.messages['ATTITUDE'].pitch                                      
            roll = the_connection1.messages['ATTITUDE'].roll 


            # mel_intesity=msg1.mel_intensity
            #print("msg1: ", ms1)
            #ts1=datetime.datetime.now()#time.time
            #print("ts1: ",ts1)

        dataQ1.put((yaw,pitch,roll,azimuth_deg, mel_intensity,active_intensity)) #((north,east,down, yaw, pitch, roll))  

# data acquisition thread
def getFPV_data2():
    
    """thread for connection 2"""

    while True: 
        msg2 = the_connection2.recv_match(blocking=True) #type='SENSOR_AVS', 
        if msg2:
            azimuth_deg = the_connection2.messages['SENSOR_AVS'].azimuth_deg #float               
            mel_intensity = the_connection2.messages['SENSOR_AVS'].mel_intensity #list              
            active_intensity = the_connection2.messages['SENSOR_AVS'].active_intensity
            #q_factor = the_connection2.messages['SENSOR_AVS'].q_factor  

            yaw = the_connection2.messages['ATTITUDE'].yaw
            pitch = the_connection2.messages['ATTITUDE'].pitch                                      
            roll = the_connection2.messages['ATTITUDE'].roll                   

        dataQ2.put((yaw,pitch,roll,azimuth_deg, mel_intensity,active_intensity))
                                
def updateSpectrogram1():
        # # --------------------- Spectrogram ----------------------
    global ind,spec #background,

    try:
        yaw,pitch,roll,azimuth_deg, mel_intensity,active_intensity  = dataQ1.get_nowait() #north, east, down,yaw,pitch,roll 
        #print(active_intensity)
    #print('north:', north)
    except queue.Empty:
         root.after(1,updateSpectrogram1)
         return

    roll = (math.degrees(roll) +360) % 360 #normalize roll

    #Update spectrogram data 
    new_row = mel_intensity  # shape: (16,)
    spec = np.roll(spec, -1, axis=0)   # rolls vertically 
    spec[-1, :] = new_row              # insert data in new row

    #flipped to start at 90 degree and rotate clockwise
    updateYaz = 1*np.cos(azimuth_deg)  #X #az 
    updateXaz = 1*np.sin(azimuth_deg)  #Y
    updateYyaw = 1.25*np.cos(yaw)  #X #yaw
    updateXyaw = 1.25*np.sin(yaw)  #Y


    #Update data: change your artist
    im1.set_data(spec)         # update existing image; replace old array without creating new imshow object
    ax1.draw_artist(im1)        # Redraw just the changed artist
    fig.canvas.blit(ax1.bbox)  # Blit the updated area (blit on screen)

    root.after(1, updateSpectrogram1) # after 1ms run updateSpectrogram() without freezing/lag in tkinter

def updateSpectrogram2():
        # # --------------------- Spectrogram ----------------------
    global ind2,spec2 

    try:
        yaw,pitch,roll,azimuth_deg, mel_intensity,active_intensity = dataQ2.get_nowait() #north, east, down,yaw,pitch,roll 
    except queue.Empty:
         root.after(1,updateSpectrogram2)
         return

    roll = (math.degrees(roll) +360) % 360 #normalize roll

    #Update spectrogram data 
    new_row = mel_intensity  # shape: (16,)
    spec2 = np.roll(spec2, -1, axis=0)   # rolls vertically 
    spec2[-1, :] = new_row              # insert data in new row

    im2.set_data(spec2)         # update existing image; replace old array without creating new imshow object
    ax2.draw_artist(im2)        # Redraw just the changed artist
    fig.canvas.blit(ax2.bbox)  # Blit the updated area (blit on screen)

    root.after(1, updateSpectrogram2) # after 1ms run updateSpectrogram() without freezing/lag in tkinter


# -------- threads ---------
threading.Thread(target=getFPV_data1, daemon=True).start()
threading.Thread(target=getFPV_data2, daemon=True).start()
root.after(5, updateSpectrogram1)
root.after(5,updateSpectrogram2)
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

# ms2=msg2.mel_intensity
# print("msg2: ", ms2)
# ts2=datetime.datetime.now()#time.time
# print("ts2: ",ts2)


# print(ms)
# aI= msg.active_intensity
# print(sys.getsizeof(aI))
# tstamp=msg.timestamp
# print(tstamp)
# tstamp_smpl = msg.timestamp_sample
# # print(tstamp_smpl)
# time=msg.time_usec
# print(time)s
# q_factor = the_connection.messages['SENSOR_AVS'].q_factor  


# try:
#     # Get the most recent data, discard old frames
#     data = None
#     while True:
#         try:
#             data = dataQ1.get_nowait()
#         except queue.Empty:
#             break
    
#     if data is None:
#         root.after(1, updateSpectrogram1)
#         return
        
#     yaw, pitch, roll, azimuth_deg, mel_intensity, active_intensity = data
    
# except Exception as e:
#     root.after(1, updateSpectrogram1)
#     return