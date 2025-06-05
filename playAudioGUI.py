# updateGUIcode.py

# import libraries
import tkinter as tk
from tkinter import ttk 
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.image as mpimg 

import sounddevice as sd
from scipy.io import wavfile
from playsound import playsound

import time
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
import os
import numpy as np
import math

import threading


class PlayAudio(): #defines new class name PlayAudio
    def __init__(self, root):   # sets up an instance of a class
        self.root=root

        #### self is the instance of a class

        #settings
        self.fs = 44100 # samplerate
        self.totalSpeakers = 4
        self.t = np.arange(0,0.1,1/self.fs) #0,5
        self.whichSpeakers = np.array(["1", "2", "3", "4"])
        self.wt = np.array(['1', '1','1','1'])  #default amplitude
        self.freq = np.array([200, 300, 400, 500, 600])
        self.signalType = ['tone', 'white noise', 'arbitrary sound']
        self.img = mpimg.imread("head_topview.jpg")
        self.NFFT = 1024  
        # self.samplerate, self.data = wavfile.read('car-horn.wav')

        
        self.xt = np.shape(self.t) 
        self.xtt = np.zeros((self.totalSpeakers,len(self.t)))

        # label frame for drop-down menu, entries and buttons
        self.input_frame = tk.LabelFrame(root, text="User Input", padx=10, pady=10) #, height =10)
        self.input_frame.pack(side = 'top', fill="both", padx=10, pady=10)

        # label frame for plots (head and spectrogam) 
        self.plot_frame = tk.LabelFrame(root, padx=10, pady=10)
        self.plot_frame.pack(side='top', fill="both", expand=True,  padx=10, pady=10)

        # # # PLAY AUDIO button 
        # self.startButton = tk.Button(master=self.plot_frame, text = 'PLAY AUDIO', bg ='red', fg= 'black',  
        #                              width=8, height=1, padx=5, pady=5, command=lambda: [self.displayPlots()])  #self.updateSpeaker,
        # self.startButton.pack(side="top", padx=10)  #grid(row = 2, column=3, sticky= 'E') #, sticky=tk.W)


        # store in lists
        self.getSignalType = []   # store signal type
        self.freqBtn_list = []    # list to hold the freq button object
        self.freqIdxList=[]       # list to hold users preferred frequency
        self.selectIdx = []       # store selected button index 
        self.storeInputWt = []    # store entry object as list     
        #self.getInputWts = []    # store new weight/amplitude (user input)
        self.viewWeights =[]
    

        self.createDropDownMenu()
        self.createButtons()
        self.createEntries()
        self.createSliders()
        self.createImgPlot()
        self.createPlots()
        self.readWavFile()

        self.phase = 0  #ongoing position in sine wave cycle
        # ensure smooth and continuous waveform generation between audio blocks
        # It's used to keep the waveform continuous when generating it in chunks (audio buffers or "frames").
        # If you generate a sine wave from scratch each time inside the callback, you'd get clicks or glitches, 
        # because the wave might not line up smoothly at the buffer boundaries.
        self.channel = ''  # which speaker 
        
        # Start audio stream: 4 output channels
        self.stream = sd.OutputStream(callback=self.audioCallback, channels=4, samplerate=self.fs)
        #self.stream.start()     

        # Close stream on exit
        #self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.frames = 1136
        self.output = np.zeros((self.frames,4), dtype = np.float32)

    def createDropDownMenu(self):
        # create drop-down menu
        self.cb = ttk.Combobox(self.input_frame, state="readonly", values= self.signalType)
        self.cb.set("Signal Type")
        self.cb.grid(row=0,column=0, pady=5, padx=5, sticky='w')
        self.cb.bind('<<ComboboxSelected>>', self.getSignal)

    
    # get users preference for signal type (from drop down menu)
    def getSignal(self,event):
        s = self.cb.get()
        self.getSignalType.append(s)

    
    # create buttons list
    def createButtons(self):
        # create frames to group/organize widgets
        self.frameFreqBtn = tk.Frame(master= self.input_frame,pady=5) #,padx=10, pady=10)#, borderwidth=50) 
        self.frameFreqBtn.grid(row = 1, column=0, sticky='W')

        #create label
        lbl = tk.Label(master=self.frameFreqBtn, text='Frequencies (may select multiple):') #,font = 'times 11 bold')
        lbl.grid(row=1, column=0, sticky='w', pady=5, padx=5)

        idxR = 1 
        idxC= 1
        for fIdx,f in enumerate(self.freq):
            # create button widget
            button3 = tk.Button(master=self.frameFreqBtn, text=str(f), width=10, height=1, 
                                command=lambda idx=fIdx: self.selectBtn(idx))

            button3.grid(row=idxR, column=idxC, padx=5) #,  sticky="W")
            idxC = idxC+1
            self.freqBtn_list.append(button3)  # append button object to list

    # select buttons 
    def selectBtn(self, idx):
        self.freqIdxList.append(idx)  # store index of button selected
        #print(str("idx:"),idx); print(str('freq list:'),self.freqIdxList); print(self.freqIdxList.count(idx))

        # check if index count is odd or even
        # if odd, sink btn (as in selected)
        # if even, raise btn  (as in deselect)
        if self.freqIdxList.count(idx) % 2 == 1:
            self.freqBtn_list[idx].config(relief = 'sunken')  #select btn

            if idx not in self.selectIdx:
                self.selectIdx.append(idx)
                #print(str('selected idx list:'),self.selectIdx)

        else:
            self.freqBtn_list[idx].config(relief = 'raised')  #deselect btn
            self.selectIdx.remove(idx)  #pop did not work here 
            #print(str('updated idx list:'),self.selectIdx)

    def createEntries(self):
        # create frame to group/organize widgets
        frameWtEntries = tk.Frame(master=self.input_frame,pady=5) #,padx=10, pady=10)
        frameWtEntries.grid(row = 2, column=0, sticky='W')

        #create label
        lbl = tk.Label(master=frameWtEntries, text='Amplitude (weight scale):') #, font = 'times 11 bold')
        lbl.grid(row=2, column=0, sticky='w', pady=5, padx=5)

        # create user input entry fields/widgets
        for idx, weight in enumerate(self.viewWeights): #self.wt
            # create entry field
            e = tk.Entry(frameWtEntries, width =10) # , font=('ariel 15'))

            e.insert(0,weight) # default values 
            e.grid(row=2, column= idx+1,sticky = 'w', padx=5, pady=5 )  #+1 for indexing 
            self.storeInputWt.append(e) #append user's input to list
    
    def createSliders(self):
        # create slider frame
        sliderFrame = tk.Frame(self.plot_frame)
        sliderFrame.pack(side="left", padx=10)

        #slider1
        self.slider = tk.Scale(sliderFrame, from_=0, to=360,command=self.sliderCallback) #updateSpeaker
        self.slider.pack(side='left')

        # #slider2
        # self.slider2 = tk.Scale(sliderFrame, from_=0, to=360,command = self.updateCirclePlot)
        # self.slider2.pack(side='right')

        #self.createImgPlot(self.slider.get())

    def sliderCallback(self,val):
        val = int(val)

        self.stream.start()

        if val > 0 and val < 90:
            self.channel =  0  #right
            #self.wt =  np.array(['0', '0','1','1'])  

        # if val == 90:
        #     self.channel = np.array([0,1])

        if val > 90 and val < 180:
            self.channel = 1 #right
            #self.wt =  np.array(['0', '0','1','1'])

        if val > 180 and val < 270:
            self.channel =  2  #left
            #self.wt =  np.array(['1', '1','0','0']) 

        # if val == 270:
        #     self.channel = np.array([2,3])

        if val > 270 and val < 360:
            self.channel = 3  #left 
            #self.wt =  np.array(['1', '1','0','0'])  

        if val == 0:
            self.stream.stop()


        self.updateCirclePlot(val)
        self.determineWeights(val)

 
        #self.displayPlots()
        ##self.playContinuousSound()

    def determineWeights(self,val):
        
        soundTheta = int(val)
                                # [LF,LB, RF, RB]
        spkrThetaArr = np.array([315, 225, 45, 135]) #[45, 135, 225, 315])
        print('soundTheta:', soundTheta)

        self.viewWeights.clear()

        for idx, spkrTheta in enumerate(spkrThetaArr):
            print('spkrTheta:', spkrTheta)
            # wt = np.float16((1+math.cos(spkrTheta-soundTheta))/2)
            # print('wt:', wt)
            #print(type(wt))
            
            if soundTheta == 0 or soundTheta == 360:
                 self.viewWeights = [1,0,1,0]
            # elif soundTheta == 90:
            #     self.viewWeights = [0,0,1,1]
            # elif soundTheta == 180:
            #     self.viewWeights = [0,1,0,1]
            # elif soundTheta == 270:
            #     self.viewWeights = [1,1,0,0]
            
            else:
                wt = np.float16((1+math.cos(math.radians(spkrTheta-soundTheta)))/2)
                print('wt:', wt)
                self.viewWeights.append(wt)

        print('view weights:',self.viewWeights)
        self.createEntries()
  
    
    def createPlots(self):
        # create frame
        plotFrame = tk.Frame(master=self.plot_frame) #,padx=10, pady=10)
        plotFrame.pack(side='right') #grid(row=0,column=3)
    
        # Create the plots for waveform and spectrogram
        self.fig, (self.ax1, self.ax2) = plt.subplots(figsize=(5, 3), nrows=2)  # Adjust plot size here
        self.canvas = FigureCanvasTkAgg(self.fig, master=plotFrame)  # Place in the plot frame
        plt.subplots_adjust(hspace=0.5)
        self.fig.patch.set_alpha(0) 
        
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True) #fill="both", expand=True, padx=5, pady=5)
        self.canvas.get_tk_widget().configure(bg= '#F0F0F0')
        self.canvas.draw()


    def createImgPlot(self):
        # create frame
        imgFrame = tk.Frame(master=self.plot_frame) #,padx=10, pady=10)
        imgFrame.pack(side="left")#grid(row=0, column=2)
        #create plot with slider value updates 

        self.fig3, self.ax3 = plt.subplots(figsize=(5,4)) 
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=imgFrame)  # Place in the plot frame
        self.ax3.patch.set_facecolor('white') 
        # #self.fig3.patch.set_facecolor('none') 
        self.fig3.patch.set_alpha(0) # background (outside of figure)
        self.canvas3.get_tk_widget().pack() # fill=tk.BOTH, expand=True) 
        self.canvas3.get_tk_widget().configure(bg= '#F0F0F0')

         # add image axes (position: [left, bottom, width, height])
        #image_xaxis, image_yaxis, image_width, image_height
        ax_img = self.fig3.add_axes([.364, .35, .3, .3]) 
        ax_img.imshow(self.img)
        ax_img.axis('off')

        self.updateCirclePlot(self.slider.get())


    def updateCirclePlot(self,val): #,val

        val = int(val)
        rad = math.radians(val)
        #print('rad:', rad)

        self.ax3.set_aspect('equal') #cirularizes (oval without this)
        self.ax3.set_xlim([-1.5,1.5])
        self.ax3.set_ylim(-1.5,1.5)
        
        #flipped to start at 90 degree and rotate clockwise
        updateY = 1*np.cos(rad)  #X 
        updateX = 1*np.sin(rad)  #Y
        
        circle = plt.Circle((0,0), 1, fill=False)
        self.circle2 = plt.Circle((updateX,updateY),.05, color = 'red')

        self.ax3.add_patch(circle)
        self.ax3.add_patch(self.circle2)

        self.canvas3.draw()
        self.circle2.remove()
       
        # self.ax3.axis('off')  this removes plot entirely (box)
        # remove x and y axis ticks/labels
        self.ax3.set_xticks([])
        self.ax3.set_yticks([])

        #self.updateSpeaker(val)
        self.determineWeights(val)


    # def updateSpeaker(self,val):
    #     #val = float(val)
    #     #print('deg:', val)

    #     # speakerTheta= 45 #[45, 135, 270, 315]
    #     # soundTheta= val

    #     # th = (1+ np.cos(math.radians(speakerTheta)-math.radians(soundTheta)))/2
    #     # print(math.degrees(th))

    #     val = int(val)

    #     # play sound out of specifc speakers based on user input
    #     if val > 0 and val < 180:
    #         self.wt =  np.array(['0', '0','1','1'])  #right side only 
            
    #     if val > 180 and val < 360:
    #         self.wt = np.array(['1', '1','0','0'])  #left side only 

    #     # might not be necessary
    #     if val == 0 or val ==360: #front
    #         self.wt = np.array(['1', '0','1','0'])  
        
    #     if val == 180: #back
    #         self.wt = np.array(['0', '1','0','1'])

    #     #print('wt slider:', self.wt)
    #     self.createEntries()
    #     #self.displayPlots()


    def readWavFile(self):

        self.samplerate, self.data = wavfile.read('car-horn.wav')  #print(samplerate); print(data); print(np.shape(data)); 
        self.length = self.data.shape[0] / self.samplerate #print(f"length = {length}s")
        self.time = np.linspace(0., self.length, self.data.shape[0])
        self.data2=self.data
        self.xttArb = np.zeros((self.totalSpeakers,len(self.time)))
        #print('samplerate:', self.samplerate)

        #self.displayPlots()
        #self.playContinuousSound()


    # # plot 
    # def displayPlots(self):

    #     #self.getEntryVals()

    #     s = self.getSignalType
    #     s = ' '.join(s) # convert list to string
    #     #print(s); print(type(s))
    #     # wtt =self.getInputWts #weights
    #     # print(str('weight:'), str(wtt))

    #     wtt=self.wt
    #     print('wtt:', wtt)

    #     if s == 'arbitrary sound':
    #         #playsound('car-horn.wav')
    #         # xttArb = np.zeros((self.totalSpeakers,len(time)))

    #         for idxWt, valWt in enumerate(wtt):
    #             # print('in for loop')
    #             # print(int(valWt))
    #             # print(type(valWt))

    #             self.data2 = int(valWt)*self.data

    #             self.xttArb[idxWt,:] = np.array(self.data2)

    #             self.ax1.plot(self.time,self.data) #plot waveform
    #             self.ax2.specgram(self.data, NFFT=self.NFFT, Fs=self.samplerate) #plot spectrogram

    #             self.canvas.draw()
    #             self.ax1.clear()
    #             self.ax2.clear()

    #         sd.play(np.transpose(self.xttArb), mapping=[1,2,3,4])   
    #         sd.wait()

    #     else:
    #         newFreq = self.freq[self.freqIdxList]  #print(str('frequency:'), str(newFreq)); print(newFreq)
    #         # wtt =self.getInputWts #weights
    #         # print(str('weight:'), str(wtt))

    #         #xtt = np.zeros((4,len(self.t)))
    #         checkFreq = []
    #         # this section plays sounds out of speakers
    #         # weight values will reflect which speaker to play sound from 
    #         for valF in newFreq:
    #             for idxWt, valWt in enumerate(wtt):
    #                 #print('valWt:', valWt)

    #                 if s == 'tone':
    #                     saveXt = np.sin(2*np.pi*valF*self.t)
    #                     self.xt = int(valWt)*np.sin(2*np.pi*valF*self.t) #/10 
    #                     print(np.shape(self.xt))

    #                 if s == 'white noise':
    #                     #noise
    #                     xt = np.random.normal(0,1,len(self.t))/40
    #                     b, a = butter(2, valF/22050, btype='high', analog=False)
    #                     saveXt = filtfilt(b, a, xt)
    #                     self.xt = int(valWt)*filtfilt(b, a, xt)

    #                 self.xtt[idxWt,:]= np.array(self.xt) 

    #                 # plot figure only once
    #                 if valF not in checkFreq:
    #                     checkFreq.append(valF)

    #                     self.ax1.plot(self.t, saveXt)
    #                     self.ax2.specgram(saveXt, NFFT=self.NFFT, Fs=self.fs)
     
    #                     self.canvas.draw()
    #                     self.canvas.get_tk_widget().pack() 
    #                     self.canvas.flush_events()
    #                     self.ax1.clear() # clear waveform
    #                     self.ax2.clear() # clear spectrogram

    #             sd.play(np.transpose(self.xtt), mapping=[1,2,3,4]) #, blocking=True)   
    #             sd.wait() # wait for sound to play
    

    # def determineWeights(self,val):
        
    #     soundTheta = int(val)
    #     spkrThetaArr = np.array([315, 225, 135, 45]) #[45, 135, 225, 315])
    #     print('soundTheta:', soundTheta)

    #     self.viewWeights.clear()

    #     for idx, spkrTheta in enumerate(spkrThetaArr):
    #         print('spkrTheta:', spkrTheta)
    #         wt = np.float16((1+math.cos(spkrTheta-soundTheta))/2)
    #         print('wt:', wt)
    #         print(type(wt))

    #         self.viewWeights.append(wt)

    #     print('view weights:',self.viewWeights)
    #     self.createEntries()
  




    def audioCallback(self,outdata,frames, time, status):

        """
        outdata:  write audio data 
        |          Whatever you put into outdata[:], gets sent to the soundcard in real time.

        frames: how many audio frames to generate
        |          Used to generate frames worth of samples (usually per channel).

        time: timestamps for sync (optional)
        status: flags for underruns, errors, etc

        """

        self.frames = frames
        t = (np.arange(self.frames) + self.phase) / self.fs
        self.phase = (self.phase + self.frames) % self.fs

        # print("outdata:", np.shape(outdata));print("frames:", np.shape(frames));print("time:", time);print("status:", status)

        s = self.getSignalType
        s = ' '.join(s) # convert list to string

        newFreq = self.freq[self.freqIdxList]  #print(str('frequency:'), str(newFreq)); print(newFreq)

        # this section plays sound based on frequency and speaker (channel)
        for valF in newFreq:
            for idxWt,valWt in enumerate(self.viewWeights):

                if s == 'tone':
                    self.xt = valWt * np.sin(2*np.pi*valF*t) #/10  #int(valWt)*

                if s == 'white noise':
                    #noise
                    xt = np.random.normal(0,1,len(t))/40
                    b, a = butter(2, valF/22050, btype='high', analog=False)
                    saveXt = filtfilt(b, a, xt)
                    self.xt = valWt*filtfilt(b, a, xt) # int(valWt)*

                # output = np.zeros((frames,4), dtype = np.float32)
                self.output[:,idxWt]=self.xt #self.channel
                outdata[:] = self.output         # [:] after a variable name denotes slicing a list or string. 
                                                 # It's a way to extract a portion of the original sequence and create a new one.




    # if np.all(self.channel): 
    #     output[:,0:1]=self.xt  
    # elif  np.all(self.channel): # == np.array([2, 3]): 
    #     output[:,1:2]=self.xt
    # else:
    

    # def close(self):
    #     # if self.playing:
    #     self.stream.stop()
    #     self.stream.close()
    #     self.root.destroy()



if __name__ =="__main__":

    # Launch the GUI
    root = tk.Tk()
    root.title("PLAY AUDIO")

    sd.default.samplerate = 44100
    sd.default.channels = 4

    #get computers screen dimensions 
    screen_width = root.winfo_screenwidth()    #print('screen_width:', screen_width )
    screen_height = root.winfo_screenheight()  #print('screen_height:', screen_height)

    # root window title & set display dimension to fit users screen
    root.title("PLAY AUDIO")
    #root.configure(bg='lightblue')
    root.geometry(f"{int(screen_width*.7)}" + 'x' + f"{int(screen_height*.6)}")  #width x height+x+y

    gui = PlayAudio(root)  #object of a class

    root.mainloop()




    ######################################################################
    # threading 
    ######################################################################

    # def playContinuousSound(self):

    #     def play_cont_sound():

    #         s = self.getSignalType
    #         s = ' '.join(s) # convert list to string
    #         #print(s); print(type(s))
    #         # wtt =self.getInputWts #weights
    #         # print(str('weight:'), str(wtt))

    #         wtt=self.wt
    #        # print('wtt:', wtt)

    #         if s == 'arbitrary sound':
    #             #playsound('car-horn.wav')
    #             # xttArb = np.zeros((self.totalSpeakers,len(time)))

    #             while self.running:

    #                 for idxWt, valWt in enumerate(wtt):
    #                     # print('in for loop')
    #                     # print(int(valWt))
    #                     # print(type(valWt))

    #                     self.data2 = int(valWt)*self.data

    #                     self.xttArb[idxWt,:] = np.array(self.data2)

    #                     # self.ax1.plot(self.time,self.data) #plot waveform
    #                     # self.ax2.specgram(self.data, NFFT=self.NFFT, Fs=self.samplerate) #plot spectrogram

    #                     # self.canvas.draw()
    #                     # self.ax1.clear()
    #                     # self.ax2.clear()


    #                 sd.play(np.transpose(self.xttArb), mapping=[1,2,3,4])#, blocking=True)   
    #                 sd.wait()

    #     threading.Thread(target=play_cont_sound, daemon=False).start() #daemon=True

    # def playContinuousSound(self):

    #     def play_cont_sound():

            
    #         s = self.getSignalType
    #         s = ' '.join(s) # convert list to string

    #         newFreq = self.freq[self.freqIdxList]  #print(str('frequency:'), str(newFreq)); print(newFreq)
    #         # wtt =self.getInputWts #weights
    #         # print(str('weight:'), str(wtt))

    #         wtt=self.wt

    #         #xtt = np.zeros((4,len(self.t)))
    #         checkFreq = []
    #         # this section plays sounds out of speakers
    #         # weight values will reflect which speaker to play sound from 
    #         for valF in newFreq:
    #             for idxWt, valWt in enumerate(wtt):
    #                 #print('valWt:', valWt)

    #                 if s == 'tone':
    #                     saveXt = np.sin(2*np.pi*valF*self.t)
    #                     self.xt = int(valWt)*np.sin(2*np.pi*valF*self.t) #/10 
    #                     #print(np.shape(self.xt))

    #                 if s == 'white noise':
    #                     #noise
    #                     xt = np.random.normal0(0,1,len(self.t))/40
    #                     b, a = butter(2, valF/22050, btype='high', analog=False)
    #                     saveXt = filtfilt(b, a, xt)
    #                     self.xt = int(valWt)*filtfilt(b, a, xt)

    #                 self.xtt[idxWt,:]= np.array(self.xt) 

    #                 # # plot figure only once
    #                 # if valF not in checkFreq:
    #                 #     checkFreq.append(valF)

    #                 #     self.ax1.plot(self.t, saveXt)
    #                 #     self.ax2.specgram(saveXt, NFFT=self.NFFT, Fs=self.fs)
     
    #                 #     self.canvas.draw()
    #                 #     self.canvas.get_tk_widget().pack() 
    #                 #     self.canvas.flush_events()
    #                 #     self.ax1.clear() # clear waveform
    #                 #     self.ax2.clear() # clear spectrogram

    #             sd.play(np.transpose(self.xtt), mapping=[1,2,3,4], blocking=True)   # maybe this only plays sounds once instead of continuously?
    #             #sd.wait() # wait for sound to play

    #     threading.Thread(target=play_cont_sound, daemon=True).start() #daemon=True
    