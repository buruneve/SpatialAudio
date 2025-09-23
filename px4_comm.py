# px4_comm.py
# communicate with px4: send/receive messages

from pymavlink import mavutil
import sys
import numpy as np
import matplotlib.pyplot as plt
mavutil.set_dialect("development")
import time
import csv
import json



import csv
import pandas as pd  # data analysis & manipulation library 
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import ttk 
#from PIL import ImageTk, Image # install pillow
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import numpy as np
import matplotlib.image as mpimg 
import time

import matplotlib.animation as animation
from matplotlib import style


# Start a listening connection
the_connection = mavutil.mavlink_connection(device='COM5', baud=115200) #, dialect = 'custom'
#time.sleep(1)

# # Wait for the first heartbeat
# #   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()  
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

#time.sleep(1)

# the_connection.mav.command_cancel_send(the_connection.target_system, the_connection.target_component, 
#                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM)

the_connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS,
                                                mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)

#msg = the_connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
#print(msg) 

# print("heartbeat sent")


the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, 
                                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1,21196,0,0,0,0,0) # force arm



# time.sleep(3)

# the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, 
#                                      mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,0,0,0,0,0,0,0) # force arm

# #MAV_CMD_MISSION_START
# # the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, 
# #                                      mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,0,0,0,0,0,0,0) # force: 21196

# time.sleep(2)

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

#time.sleep(2)
msg2 = the_connection.recv_match(type='COMMAND_ACK',blocking=True)  # acknowledge command 
print(msg2) 
print('')

# msg = the_connection.recv_match(type='SENSOR_AVS',blocking=True)
# if not msg:
#         print('vvvv')
# if msg.get_type() == "BAD_DATA":
#         if mavutil.all_printable(msg.data):
#                 sys.stdout.write(msg.data)
#                 sys.stdout.flush()
# else:
#         #Message is valid
#         # Use the attribute
#         print('Mode: %s' % msg.mode)

# extract: azimuth deg 
# tresholds 
# active intensity - how loud sound is 
# q_factor - diffusion/concentration of sound 
# plot - mel intesity
# spectrograms 

#  uint64_t timestamp; /*<  time since system start (microseconds)*/
#  uint64_t time_utc_usec; /*<  Timestamp (microseconds, UTC)*/
#  uint32_t timestamp_sample; /*<  AVS sensor sample index since system SYNC*/
#  uint32_t device_id; /*<  unique device ID for the sensor that does not change between power cycles*/
#  float azimuth_deg; /*<  azimuth in degrees*/
#  float elevation_deg; /*<  elevation in degrees*/
#  float active_intensity; /*<  active intensity level re: 1 pW*/
#  float q_factor; /*<  Q-factor of the histogram peak for this detected source*/
#  float mel_intensity[16]; /*<  MEL Intensity spectrum*/
#  uint16_t source_index; /*<  index of detected source_index*/
#  uint16_t histogram_count; /*<  number of hits for this azim/elev histogram bin*/



t_end = time.time() + 4 #run for 5 seconds

get_azDeg = []
get_qFactor = []
get_melInt = []
get_timeBootMs =[]
get_yaw = []
get_pitch = []
get_roll = []
# with open("px4_data.txt", "w", encoding="utf-8") as f: # "w" to write to file
#         print("opened file")

fig = plt.figure() 
ax1 = fig.add_subplot(1,1,1)

#def animate(i):
with open('px4_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        fieldnames = ['azimuth deg', 'q factor', 'time utc usec', 'time boot ms', 'yaw', 'pitch', 'roll', 'active intensity', 'mel intensity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
                # writer.writerow(name)
                
#                fig = plt.figure() 
        #plt.ion() # enable interactive mode; initialize gui

                        # Launch the GUI
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

        fig3, ax3 = plt.subplots(figsize=(5,4)) 
        canvas3 = FigureCanvasTkAgg(fig3, master=imgFrame)  # Place in the plot frame
        ax3.patch.set_facecolor('white') 
        # #self.fig3.patch.set_facecolor('none') 
        fig3.patch.set_alpha(0) # background (outside of figure)
        canvas3.get_tk_widget().pack() # fill=tk.BOTH, expand=True) 
        canvas3.get_tk_widget().configure(bg= '#F0F0F0')

        # add image axes (position: [left, bottom, width, height])
        #image_xaxis, image_yaxis, image_width, image_height
        ax_img = fig3.add_axes([.364, .35, .3, .3]) 
        ax_img.imshow(img)
        ax_img.axis('off')

        ax3.set_aspect('equal') #cirularizes (oval without this)
        ax3.set_xlim([-1.5,1.5])
        ax3.set_ylim(-1.5,1.5)

        circle = plt.Circle((0,0), 1, fill=False)
        ax3.add_patch(circle)
        canvas3.draw()

        circle3 = plt.Circle((0,0), 1.25, fill=False)
        ax3.add_patch(circle3)
        canvas3.draw()

        # self.ax3.axis('off')  this removes plot entirely (box)
        # remove x and y axis ticks/labels
        ax3.set_xticks([])
        ax3.set_yticks([])

        while True: #time.time() < t_end: # while True:   #COMMAND_ACK  #UNKNOWN_292 type='SENSOR_AVS', 
                res = the_connection.recv_match(blocking=True)  # receives all the messages available 
                # print(res) # get a lot of data 

                azimuth_deg = the_connection.messages['SENSOR_AVS'].azimuth_deg  #float
                #print("azimuth_deg: ",azimuth_deg)
                get_azDeg.append(azimuth_deg)
                
                q_factor = the_connection.messages['SENSOR_AVS'].q_factor
                #print("q factor: ", q_factor)
                get_qFactor.append(q_factor)

                mel_intensity = the_connection.messages['SENSOR_AVS'].mel_intensity #list
                get_melInt.append(mel_intensity)

                active_intensity = the_connection.messages['SENSOR_AVS'].active_intensity

                time_utc_usec = the_connection.messages['SENSOR_AVS'].time_utc_usec
                #print(time_utc_usec)

                time_boot_ms  = the_connection.messages['ATTITUDE'].time_boot_ms 
                get_timeBootMs.append(time_boot_ms)
                #print(time_boot_ms)

                yaw = the_connection.messages['ATTITUDE'].yaw  #GUI 
                get_yaw.append(yaw)

                pitch = the_connection.messages['ATTITUDE'].pitch
                get_pitch.append(pitch)

                roll = the_connection.messages['ATTITUDE'].roll
                get_roll.append(roll)

                        #time.sleep(.1)

                        #print("data extraction succesfull")

                        #data = [azimuth_deg,q_factor, time_boot_ms, yaw, pitch, roll, mel_intensity]

                        #['azimuth deg', 'q factor', 'mel intensity', 'time boot ms', 'yaw', 'pitch', 'roll']
                        #writer.writerow({'azimuth deg': azimuth_deg,'q factor': q_factor,'time utc usec': time_utc_usec,'time boot ms': time_boot_ms, 'yaw': yaw, 'pitch': pitch,'roll': roll, 'active intensity': active_intensity, 'mel intensity': mel_intensity})

                #print("writing data to file")
                # f.write('azimuth deg: ' + str(get_azDeg) + '\n')
                # f.write('q factor: ' + str(get_qFactor) + '\n')         
                # f.write('mel intesity: ' + str(get_melInt) + '\n')
                # f.write('time boot ms: ' + str(get_timeBootMs) + '\n')
                # f.write('yaw: ' + str(get_yaw) + '\n')
                # f.write('pitch: ' + str(get_pitch) + '\n')
                # f.write('roll: ' + str(get_roll) + '\n')
        #       print("data extraction succesfull")
        #print("file closed")



        # writer = csv.writer(file)
        # writer.writerow(name)
        #writer.writerows(str(azimuth_deg))



        #with open('data.json', 'w', encoding='utf-8') as file:
                #name = ['azimuth deg'] #, 'q factor', 'mel intensity', 'time boot ms', 'yaw', 'pitch', 'roll']
                #f.write(name)


                # ax1.clear() 
                # plt.plot(np.arange(0,16),mel_intensity)
                # fig.canvas.draw() #redraw figure
                # fig.canvas.flush_events() # flush events 
                # time.sleep(0.1)
                # plt.show()
                # plt.clf() # clear figure 

# ani = animation.FuncAnimation(fig, animate, interval=1000)
# plt.show()


                        # res = ' '.join([str(s) for s in mel_intensity[0]])
                        # print('res',type(res))
                        # st = res.split()


                        #ACTIVE INTENSITY not the same as mel intensity
                        # active is how loud sound is 
                        # --> marker size 


                        # ###

                # # Launch the GUI
                # radAz = math.radians(azimuth_deg)
                # radYaw = math.radians(yaw)
                # print('yaw:', yaw)

                #flipped to start at 90 degree and rotate clockwise
                updateYaz = 1*np.cos(azimuth_deg)  #X 
                updateXaz = 1*np.sin(azimuth_deg)  #Y

                circle2 = plt.Circle((updateXaz,updateYaz),.05, color = 'red')
                ax3.add_patch(circle2)
                canvas3.draw()

                updateY2yaw = 1.25*np.cos(yaw)  #X 
                updateX2yaw = 1.25*np.sin(yaw)  #Y

                circle4 = plt.Circle((updateX2yaw,updateY2yaw),.05, color = 'blue')
                ax3.add_patch(circle4)
                canvas3.draw()

                ax3.set_xticks([])
                ax3.set_yticks([])
                canvas3.flush_events()  
                #time.sleep(.1)
                circle2.remove()
                circle4.remove()


        root.mainloop()