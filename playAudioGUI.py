#playAudioGUI.py

# import libraries
import tkinter as tk
from tkinter import ttk 
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

import matplotlib.image as mpimg 


# play audio GUI class 

class PlayAudio: #defines new class name PlayAudio
    def __init__(self, root):   # sets up an instance of a class

        #### self is the instance of a class

        #settings
        self.fs = 44100 # samplerate
        self.totalSpeakers = 4
        # sd.default.samplerate = self.fs
        # sd.default.channels = 4
        self.t = np.arange(0,5,1/self.fs)
        #self.numSpeakers = np.array([1,2,3,4]) #not needed
        self.whichSpeakers = np.array(["1", "2", "3", "4"])

        #settings user will select
        self.wt = np.array(['1', '1','1','1'])  #default amplitude
        self.freq = np.array([200, 300, 400, 500, 600])
        self.signalType = ['tone', 'white noise', 'arbitrary sound']


        # create frames to group/organize widgets
        ## questions
        self.frame1 = tk.Frame(master= root)#, borderwidth=50) 
        self.frame1.grid(row = 0, column=0, sticky='W')
        self.frame2 = tk.Frame(master= root)
        self.frame2.grid(row = 1, column=0, sticky='W')

        #weights
        self.frame3 = tk.Frame(master= root)
        self.frame3.grid(row = 0, column=1, sticky='w')

        #freq buttons
        self.frame4 = tk.Frame(master= root)
        self.frame4.grid(row = 1, column=1, sticky='W')

        #start button
        self.frame5 = tk.Frame(master= root)
        self.frame5.grid(row = 4, column=1, sticky='E')

        #drop-down menu
        self.frame6 = tk.Frame(master= root)
        self.frame6.grid(row = 3, column=0, sticky='W')

        # root frame
        self.rootFrame = tk.Frame(master= root,bg = 'red') #, height = 100, width = 100)
        self.rootFrame.grid(row = 5, column =0,sticky = 'W')

        #image
        self.frame7 = tk.Frame(master= self.rootFrame) #, height = 200, width = 200) #,highlightbackground="red", highlightthickness=1) #, bg = 'white')
        self.frame7.place(x=50,y=50) 
        self.img = mpimg.imread("head_topview.jpg") #Image.open("head_topview.jpg")
        #self.plotImage()

        #spectrogram
        self.frame8 = tk.Frame(master= root)
        self.frame8.grid(row = 5, column=1, sticky='w')
        

        #slider
        self.slider = tk.Scale(root, from_=0, to=360,command = self.updateCirclePlot) #, command= self.getSliderValue)
        self.slider.grid(row=5,column=0,sticky='w') #place(x=00,y=100)
        #self.slider.set(0)

        # #draw circle
        # self.circleFrame = tk.Frame(master=self.rootFrame) #, height =200, width=200)
        # self.circleFrame.grid(row=5, column=0)

        # #image
        # self.frame7 = tk.Frame(master= self.circleFrame) #, height = 75, width = 75) #,highlightbackground="red", highlightthickness=1) #, bg = 'white')
        # #self.frame7.place(x=50,y=50) 
        # self.img = Image.open("head_topview.jpg")
        # #self.plotImage()

        # store new weight/amplitude 
        self.getInputWts = []

        # store in lists 
        self.freqBtn_list = [] # list to hold the button object
        self.freqIdxList=[]  # list to hold users preferred frequency
        self.storeInputWt = []  # store entry object as list     
        self.selectIdx = []  

        # store signal type
        self.getSignalType = []

        # store selected button index 
        self.selectIdx = []

        self.createEntries()
        self.createButtons()


        # create labels that prompt user for preferred settings 
        # q1: amplitude
        # q2: frequency 
        q1_lbl = tk.Label(master=self.frame1, text='Amplitude (weight scale):', font = 'times 12 bold')
        q1_lbl.grid(row=0, column=0, sticky='w')
        q2_lbl = tk.Label(master=self.frame2, text='Frequencies (may select multiple):', font = 'times 12 bold')
        q2_lbl.grid(row=1, column=0, sticky='w')

        # create drop-down menu
        self.cb = ttk.Combobox(self.frame6, state="readonly", values= self.signalType)
        self.cb.set("Signal Type")
        self.cb.grid(row=3,column=0)
        self.cb.bind('<<ComboboxSelected>>', self.getSignal)

        self.NFFT = 1024 
        # # PLAY AUDIO button 
        self.startButton = tk.Button(master=self.frame5, text = 'PLAY AUDIO', bg ='red', fg= 'black',  
                                     width=8, height=1, padx=10, pady=10, command=lambda: [self.displayPlots()]) #, self.playAudio()]) #[getVals(),playAudio()])  # command=lambda: [getVals(inputWt)]#command=playAudio) 
        self.startButton.grid(row=4, column=1) #, sticky=tk.W)

        # Create the plots for waveform and spectragram
        self.fig, (self.ax1, self.ax2) = plt.subplots(figsize=(5, 3), nrows=2)  # Adjust plot size here
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame8)  # Place in the plot frame
        plt.subplots_adjust(hspace=0.5)
        self.fig.patch.set_alpha(0) 
        self.ax1.patch.set_facecolor('none') 
        self.canvas.get_tk_widget().pack() #fill="both", expand=True, padx=5, pady=5)
        self.canvas.get_tk_widget().configure(bg= '#F0F0F0')
        self.canvas.draw()


        #create plot with slider value updates 

        self.fig3, self.ax3 = plt.subplots() 
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.rootFrame)  # Place in the plot frame
        self.ax3.patch.set_facecolor('white') 
        # #self.fig3.patch.set_facecolor('none') 
        self.fig3.patch.set_alpha(0) # background (outside of figure)
        self.canvas3.get_tk_widget().pack() # fill=tk.BOTH, expand=True) 
        self.canvas3.get_tk_widget().configure(bg= '#F0F0F0')

        self.updateCirclePlot(self.slider.get())

         # add image axes (position: [left, bottom, width, height])
        #image_xaxis, image_yaxis, image_width, image_height
        self.ax_img = self.fig3.add_axes([.364, .35, .3, .3]) 
        self.ax_img.imshow(self.img)
        self.ax_img.axis('off')

        self.circle2 = plt.Circle((0,1),.05, color = 'red')
        self.ax3.add_patch(self.circle2)


        # #wave file
        # self.samplerate, self.data = wavfile.read('voice-note.wav')
        # self.length = self.data.shape[0] / self.samplerate

        self.xt = np.shape(self.t)
        self.xtt = np.zeros((self.totalSpeakers,len(self.t)))


    # get user input for weights
    # each box corresponds to specific speaker
    # [1,2,3,4] = ["Left Front", "Right Front", "Left Back", "Right Back"]
    def getEntryVals(self):
        self.getInputWts.clear()
        for idx in range(4):  # 4 speakers
            newWts = self.storeInputWt[idx].get()   # use get to access users input
            self.getInputWts.append(float(newWts))   # store in list 

        print(self.getInputWts)
        #print(type(self.getInputWts))

    def createEntries(self):
    # create user input entry fields/widgets
        for idx, weight in enumerate(self.wt):
            # create entry field
            e = tk.Entry(self.frame3, width =10) # , font=('ariel 15'))

            e.insert(0,weight) # default values 
            e.grid(row=0, column= idx+1, padx=5, pady=5,sticky = 'w' )  #+1 for indexing 
            self.storeInputWt.append(e) #append user's input to list


     # create buttons list
    def createButtons(self):
        idxR = 1 
        idxC= 1
        for fIdx,f in enumerate(self.freq):
            # create button widget
            button3 = tk.Button(master=self.frame4, text=str(f), width=10, height=2, 
                                command=lambda idx=fIdx: self.selectBtn(idx))

            button3.grid(row=idxR, column=idxC, padx=5, pady=10) #,  sticky="W")
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
                print(str('selected idx list:'),self.selectIdx)

        else:
            self.freqBtn_list[idx].config(relief = 'raised')  #deselect btn
            self.selectIdx.remove(idx)  #pop did not work here 
            print(str('updated idx list:'),self.selectIdx)

    # get users preference for signal type
    def getSignal(self,event):
        s = self.cb.get()
        self.getSignalType.append(s)

    # plot 
    def displayPlots(self):

        self.getEntryVals()

        s = self.getSignalType
        s = ' '.join(s) # convert list to string
        #print(s); print(type(s))
    
        if s == 'arbitrary sound':
            # prompt user to load in wave file
            samplerate, data = wavfile.read('car-horn.wav')  #print(samplerate); print(data); print(np.shape(data)); 
            length = data.shape[0] / samplerate #print(f"length = {length}s")
            time = np.linspace(0., length, data.shape[0])

            #playsound('car-horn.wav')

            self.ax1.plot(time,data) #plot waveform
            self.ax2.specgram(data, NFFT=self.NFFT, Fs=self.fs) #plot spectrogram

            self.canvas.draw()
            self.ax1.clear()
            self.ax2.clear()

            sd.play(data, mapping=[1,2,3,4])   
            sd.wait()

        else:
            newFreq = self.freq[self.freqIdxList]  #print(str('frequency:'), str(newFreq)); print(newFreq)
            wtt =self.getInputWts #weights
            print(str('weight:'), str(wtt))

            #xtt = np.zeros((4,len(self.t)))
            checkFreq = []
            # this section plays sounds out of speakers
            # weight values will reflect which speaker to play sound from 
            for valF in newFreq:
                for idxWt, valWt in enumerate(wtt):
                    #print('valWt:', valWt)
                    if s == 'tone':
                        self.xt = valWt*np.sin(2*np.pi*valF*self.t) #/10 
                        print(np.shape(self.xt))

                    if s == 'white noise':
                        #noise
                        xt = np.random.normal(0,1,len(self.t))/40
                        b, a = butter(2, valF/22050, btype='high', analog=False)
                        self.xt = valWt*filtfilt(b, a, xt)

                    self.xtt[idxWt,:]= np.array(self.xt) 
                    #xtt = np.transpose(xtt)

                    # plot figures only once
                    if valF not in checkFreq:
                        checkFreq.append(valF)

                        self.ax1.plot(self.t, self.xt)
                        self.ax2.specgram(self.xt, NFFT=self.NFFT, Fs=self.fs)
     
                        self.canvas.draw()
                        self.canvas.get_tk_widget().pack() 
                        self.canvas.flush_events()
                        self.ax1.clear() # clear waveform
                        self.ax2.clear() # clear spectrogram



                sd.play(np.transpose(self.xtt), mapping=[1,2,3,4])   
                sd.wait() # wait for sound to play
                #self.pause

                self.playAudio()
                
    
    def playSignal(self):
        pass

    def playAudio(self):
        pass

        # sd.play(np.transpose(self.xtt), mapping=[1,2,3,4]) 
        # sd.wait() # wait for sound to play
    #     #time.sleep(1)

    
    def updateCirclePlot(self,val):

        pass
        
        val = float(val)
        rad = math.radians(val)
        print('rad:', rad)

        self.ax3.set_aspect('equal') #cirularizes (oval without this)
        self.ax3.set_xlim([-1.5,1.5])
        self.ax3.set_ylim(-1.5,1.5)
        
        #flipped to start at 90 degree and rotate clockwise
        updateY = 1*np.cos(rad)  #X 
        updateX = 1*np.sin(rad)  #Y
        

        circle = plt.Circle((0,0), 1, fill=False)
        circle2 = plt.Circle((updateX,updateY),.05, color = 'red')


        self.ax3.add_patch(circle)
        self.ax3.add_patch(circle2)

        self.canvas3.draw()
        #self.ax3.axis('off')
        # self.ax3.set_xlabel('')
        # self.ax3.set_ylabel('')
        self.ax3.set_xticks([])
        self.ax3.set_yticks([])

        circle2.remove()
        #self.circleInit =[]
       
    



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