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


print(int(time.time()))

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

fig = plt.figure(figsize=(8,4))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=imgFrame)
canvas.get_tk_widget().pack()

ax.set_xlabel("Time")
ax.set_ylabel("Active intesity")

##
# fiG, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4)) #
# canvas = FigureCanvasTkAgg(fiG, master=imgFrame)
# canvas.get_tk_widget().pack()


# ind = 0
# ind2=0
# spec = np.zeros((60,16)) # storage for spectrogram; x: time steps to keep visible; y: number of mel bands

# fig, ax = plt.subplots(figsize=(5,4))
# im = ax.imshow(spec, aspect='auto', origin='lower',cmap='magma',interpolation='nearest', animated=True) #initialize and show image once
# ax.set_ylabel("Time"); ax.set_xlabel("Mel bands"); ax.set_title("Real-time Mel Spectrogram")
# im.set_clim(vmin=40, vmax=90)  # rescale colors
# #plt.draw # redraws entire figure (axes, labels, ticks, background, image, etc)

# canvas = FigureCanvasTkAgg(fig, master=imgFrame)
# canvas_widget = canvas.get_tk_widget()
# canvas_widget.pack(side = tk.RIGHT) #fill=tk.BOTH, expand=True)

# # # Tell matplotlib we will use blitting
# # # blitting -- aka block image transfer; plots only part of an image that have changed instead of entire figure 
# background = fig.canvas.copy_from_bbox(ax.bbox) # saves a clean background (the static parts: axes, ticks, grid, etc.)

# # # Draw initial state
# ax.draw_artist(im)
# fig.canvas.blit(ax.bbox)  #bbox- bounding box 

# data storage 
max_data = 100
actv1 = deque(maxlen=max_data)
actv2 = deque(maxlen=max_data)
tt1 = deque(maxlen=max_data)
tt2 = deque(maxlen=max_data)


#------------------------------------------------------------------------------

# data acquisition thread
def getFPV_data1():
    
    """thread for connection 1"""

    while True:            
        msg1 = the_connection1.recv_match(type='SENSOR_AVS_LITE',blocking=True)  
        #print(msg1)

        if msg1: 

            t1 = msg1.timestamp #_sample
            act1= msg1.active_intensity 
            #print(t1)

        dataQ1.put((t1,act1)) 

# data acquisition thread
def getFPV_data2():
    
    """thread for connection 2"""

    while True: 
        msg2 = the_connection2.recv_match(type = 'SENSOR_AVS_LITE',blocking=True) #type='SENSOR_AVS', 
        if msg2:
            
            t2 = msg2.timestamp #timestamp_sample
            act2= msg2.active_intensity 
            
        dataQ2.put((t2,act2)) #mel2
                             
def updateLinePlot():
        # --------------------- line plot ----------------------

    try:
        t1,act1 = dataQ1.get_nowait()
        t2,act2= dataQ2.get_nowait() 
    except queue.Empty:
         root.after(1,updateLinePlot)
         return

    actv1.append(act1)
    tt1.append(t1)

    actv2.append(act2)
    tt2.append(t2)


    ax.cla() # clear previous frame
    ax.plot(tt1,actv1, 'b',tt2,actv2, 'r')  #  ax.plot(tt1,actv1, 'b',

    # #ax1.cla() # clear previous frame
    # ax1.plot(tt1,actv1, 'b')  
    # #ax2.cla() # clear previous frame
    # ax2.plot(tt2,actv2, 'r')  

    #plt.tight_layout() # Adjust layout to prevent overlap
    canvas.draw_idle()

    root.after(1, updateLinePlot) # after 1ms run updateSpectrogram() without freezing/lag in tkinter

# def plotSpec():
#     global ind,background2,spec

#     try:
#        # t1,act1 = dataQ1.get_nowait()
#         t2,act2,mel2= dataQ2.get_nowait() 
#     except queue.Empty:
#          root.after(1,plotSpec)
#          return

#     #Update spectrogram data 
#     new_row = mel2  # shape: (16,)
#     spec = np.roll(spec, -1, axis=0)   # rolls vertically 
#     spec[-1, :] = new_row   

#     im.set_data(spec)         # update existing image; replace old array without creating new imshow object
#     ax.draw_artist(im)        # Redraw just the changed artist
#     fig.canvas.blit(ax.bbox)  # Blit the updated area (blit on screen)

#     root.after(1, plotSpec) 








# -------- threads ---------
threading.Thread(target=getFPV_data1, daemon=True).start()
threading.Thread(target=getFPV_data2, daemon=True).start()
updateLinePlot()
#plotSpec()
#root.after(5,updateLinePlot)
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