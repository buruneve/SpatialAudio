# px4_comm.py
# communicate with px4: send/receive messages

from pymavlink import mavutil
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
import serial 


# from queue import Queue
# q = Queue()
# # The key methods available are:
# qsize() # - Get the size of the queue
# empty() # - Check if queue is empty
# full() # - Check if queue is full
# put(item) # - Put an item into the queue
# get() # - Remove and return an item from the queue
# join() # - Block until all tasks are processed

# queue for data 
#dataQ = queue.Queue()


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

message = the_connection.mav.command_long_encode(    #encode  #.command_long_encode
        the_connection.target_system,  # Target system ID
        the_connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  #MAV_CMD_REQUEST_MESSAGE
        0,  # Confirmation
        message_id, #mavutil.mavlink.MAVLINK_MSG_ID_SENSOR_AVS  # param1: Message ID to be streamed
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
    self.serialPort = serial.Serial(port='COM3', baudrate=9600, timeout=1) #115200
    time.sleep(2)  # Wait for Arduino to reset

except serial.SerialException:
    print("could not open serial port")


# # -------------------------- Launch the GUI ----------------------------------------
#def runGUI():
 #       pass

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
spec = np.zeros((60,16)) # storage for spectrogram; x: time steps to keep visible; y: number of mel bands

fig, ax = plt.subplots()
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


# ---------------------------------------------------------------------------
# timer for data collection
#t_end = time.time() + 10 #run for 5 seconds

# data acquisition thread
def getFPV_data():
    while True: #time.time() < t_end:                                                           #COMMAND_ACK  #UNKNOWN_292 type='SENSOR_AVS', 
            msg = the_connection.recv_match(blocking=True)  # receives all the messages available 

            azimuth_deg = the_connection.messages['SENSOR_AVS'].azimuth_deg #float                                         
            mel_intensity = the_connection.messages['SENSOR_AVS'].mel_intensity #list               
            active_intensity = the_connection.messages['SENSOR_AVS'].active_intensity
            q_factor = the_connection.messages['SENSOR_AVS'].q_factor   
            yaw = the_connection.messages['ATTITUDE'].yaw
            pitch = the_connection.messages['ATTITUDE'].pitch                                      
            roll = the_connection.messages['ATTITUDE'].roll                               

            return mel_intensity, yaw, azimuth_deg, active_intensity, q_factor             
            #yield mel_intensity, yaw, azimuth_deg
                                
def updateSpectrogram():
        # # --------------------- Spectrogram ----------------------
    global spec,ind,background2

    mel_intensity, yaw, azimuth_deg, active_intensity, q_factor  =  getFPV_data()

    if 60 <= active_intensity < 65: 
        size = 1
    if 65 <= active_intensity < 70: 
        size = 1.5
    elif 70 <= active_intensity < 75: 
        size = 2
    elif 75 <= active_intensity < 80: 
        size = 2.5
    elif 80 <= active_intensity < 85: 
        size = 3
    elif 85 <= active_intensity < 90: 
        size = 3.5
    elif 90 <= active_intensity < 95: 
        size = 4
    else:
        size =1 

    # restore background of spectrogram and the head plots; only copies pixels back
    fig.canvas.restore_region(background) 
    canvas3.restore_region(background2)   

    # Update spectrogram data 
    new_row = mel_intensity  # shape: (16,)
    spec = np.roll(spec, -1, axis=0)   # rolls vertically 
    spec[-1, :] = new_row              # insert data in new row

    #flipped to start at 90 degree and rotate clockwise
    updateYaz = 1*np.cos(azimuth_deg)  #X 
    updateXaz = 1*np.sin(azimuth_deg)  #Y
    updateYyaw = 1.25*np.cos(yaw)  #X 
    updateXyaw = 1.25*np.sin(yaw)  #Y

    ind = ind+1
    # count to 5 before plotting then reset to 0
    if ind == 5:
            # Update data: change your artist
            im.set_data(spec)         # update existing image; replace old array without creating new imshow object
            ax.draw_artist(im)        # Redraw just the changed artist
            fig.canvas.blit(ax.bbox)  # Blit the updated area (blit on screen)

            circle_red.set_center((updateXaz, updateYaz))  # set_center() updates/moves circle
            circle_red.set_radius((0.05 * size)) 
            circle_blue.set_center((updateXyaw, updateYyaw))

            # draw artists
            ax3.draw_artist(circle_red)   # redraws circle in new location 
            ax3.draw_artist(circle_blue)
            canvas3.blit(ax3.bbox) 

            ind = 0

    # tkinter timer/scheduler 
    # schedules updates without blocking so GUI stays responsive
    root.after(1, updateSpectrogram) # after 1ms run updateSpectrogram() without freezing/lag in tkinter

def arduinoComm():
    # communicate with Arduino to play haptic feedback

    while True:
        mel_intensity, yaw, azimuth_deg, active_intensity, q_factor  =  getFPV_data()
        deg = (math.degrees(azimuth_deg) +360) % 360 #normalize yaw
   
        if self.serialPort and self.serialPort.is_open:
            if 135 <= deg < 180: 
                self.serialPort.write('R'.encode())

            elif 180 <= deg < 225: 
                self.serialPort.write('L'.encode())

            else:
                self.serialPort.write('C'.encode())

        time.sleep(0.05)


# -------- threads ---------
threading.Thread(target=getFPV_data, daemon=True).start()
threading.Thread(target=arduinoComm, daemon=True).start()
updateSpectrogram()
root.mainloop()




################################################
################################################

# # run GUI on a separate thread
# threading.Thread(target=runGUI, daemon=True).start()