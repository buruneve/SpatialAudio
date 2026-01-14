# px4_comm.py
# communicate with px4: send/receive messages

from pymavlink import mavutil
# import numpy as np
#import matplotlib.pyplot as plt
import time
#import pandas as pd  # data analysis & manipulation library 

# import tkinter as tk
# from tkinter import ttk 
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import math
# import matplotlib.image as mpimg 
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
the_connection2 = mavutil.mavlink_connection(device='COM7', baud=57600) #COM6  115200
#the_connection1 = mavutil.mavlink_connection(device='COM9', baud=57600)

# # Wait for the first heartbeat
##  This sets the system and component ID of remote system for the link
# the_connection1.wait_heartbeat()  
# print("Heartbeat from system (system %u component %u)" % (the_connection1.target_system, the_connection1.target_component))
the_connection2.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection2.target_system, the_connection2.target_component))


# sensor_avs message ID
message_id = 296 #292

# message1 = the_connection1.mav.command_long_encode(   
#         the_connection1.target_system,  # Target system ID
#         the_connection1.target_component,  # Target component ID
#         mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send  
#         0,  # Confirmation
#         message_id,   # param1: Message ID to be streamed
#         0, # param2: Interval in microseconds
#         0,0,0,0,0)
# print(message1)

# # # Send the COMMAND_LONG
# the_connection1.mav.send(message1)

# msg1 = the_connection1.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
# print(msg1) 
# print('')

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
# root = tk.Tk()
# #get computers screen dimensions 
# screen_width = root.winfo_screenwidth()    #print('screen_width:', screen_width )
# screen_height = root.winfo_screenheight()  #print('screen_height:', screen_height)

# # root window title & set display dimension to fit users screen
# root.title("GUI")
# root.geometry(f"{int(screen_width*.7)}" + 'x' + f"{int(screen_height*.6)}")  #width x height+x+y

# # label frame for plots (head and spectrogam) 
# plot_frame = tk.LabelFrame(root, padx=10, pady=10)
# plot_frame.pack(side='top', fill="both", expand=True,  padx=10, pady=10)
# img = mpimg.imread("head_topview.jpg")

# quitButton =  tk.Button(plot_frame, text = 'QUIT', bg ='red', fg= 'black',
#                                 width=8, height=1, padx=5, pady=5, command= root.quit) #root.destroy
# quitButton.pack(side="top") 

# # create frame
# imgFrame = tk.Frame(master=plot_frame) #,padx=10, pady=10)
# imgFrame.pack(side="left")#grid(row=0, column=2)
# #create plot with slider value updates 

# fig = plt.figure(figsize=(8,4))
# ax = fig.add_subplot(111)
# canvas = FigureCanvasTkAgg(fig, master=imgFrame)
# canvas.get_tk_widget().pack()

# ax.set_xlabel("Time")
# ax.set_ylabel("Active intesity")



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
        #the_connection1.mav.system_time_send(time_unix_usec, 0)
        the_connection2.mav.system_time_send(time_unix_usec, 0)

        time.sleep(1.0)  # Send at 1 Hz

# data acquisition thread
# def getFPV_data1():
    
#     """thread for connection 1"""

#     while True:            
#         msg1 = the_connection1.recv_match(type='SENSOR_AVS_LITE',blocking=True)  
#         #print(msg1)

#         if msg1: 

#             t1 = msg1.time_utc_usec #timestamp 
#             act1= msg1.active_intensity 

#         dataQ1.put((t1,act1)) 

# data acquisition thread
def getFPV_data2():
    
    """thread for connection 2"""

    while True: 
        msg2 = the_connection2.recv_match(type = 'SENSOR_AVS_LITE',blocking=True) #type='SENSOR_AVS', 

        if msg2:
            
            t2 = msg2.time_utc_usec #timestamp #timestamp_sample
            act2= msg2.active_intensity 

        dataQ2.put((t2,act2)) #mel2
        print("t2: ",t2, " act_int2: ", act2)


                             
# def updateLinePlot():
#         # --------------------- line plot ----------------------

#     try:
#        # t1,act1 = dataQ1.get_nowait()
#         t2,act2= dataQ2.get_nowait() 
#     except queue.Empty:
#          #root.after(1,updateLinePlot)
#          return


#     # actv1.append(act1)
#     # tt1.append(t1)

#     actv2.append(act2)
#     tt2.append(t2)

#     #print("t1: ",tt1, "act_int1: ", actv1)
#     print("t2: ",tt2, "act_int2: ", actv2)


    # ax.cla() # clear previous frame
    # ax.plot(tt1,actv1, 'b',tt2,actv2, 'r')  #  ax.plot(tt1,actv1, 'b', ,tt2,actv2, 'r'

    # canvas.draw_idle()

    # root.after(1, updateLinePlot) # after 1ms run updateSpectrogram() without freezing/lag in tkinter


# -------- threads ---------
threading.Thread(target=sync_time, daemon=True).start()  
#threading.Thread(target=getFPV_data1, daemon=True).start()
#threading.Thread(target=getFPV_data2, daemon=True).start()
getFPV_data2()
#updateLinePlot()
#root.mainloop()




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


