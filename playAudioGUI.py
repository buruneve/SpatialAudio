#playAudioGUI.py 

# import libraries
import tkinter as tk
from tkinter import ttk 
import numpy as np
import sounddevice as sd
from PIL import ImageTk, Image
import time
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pathlib import Path
from scipy.io import wavfile
import os
from playsound import playsound


# settings
fs = 44100 
sd.default.samplerate = fs
sd.default.channels = 4
t = np.arange(0, 5, 1/fs)
numSpeakers = np.array([1,2,3,4]) 
whichSpeakers = np.array(["1", "2", "3", "4"]) #np.array(["Left Front", "Right Front", "Left Back", "Right Back"]) 

# settings user will select
wt = np.array(['1', '1','1','1'])  #np.array([1.0, -0.5, 0.5, 0]) #amplitude # if want default
freq = np.array([200, 300, 400, 500, 600])
signalType = ['tone', 'white noise', 'arbitrary sound']

# create root/main window
root= tk.Tk() #main window

# create frames to group/organize widgets
## questions
frame1 = tk.Frame(master= root)#, borderwidth=50) 
frame1.grid(row = 0, column=0, sticky='W')
frame2 = tk.Frame(master= root)
frame2.grid(row = 1, column=0, sticky='W')

#weights
frame3 = tk.Frame(master= root)
frame3.grid(row = 0, column=1, sticky='w')

#freq buttons
frame4 = tk.Frame(master= root)
frame4.grid(row = 1, column=1, sticky='W')

#start button
frame5 = tk.Frame(master= root)
frame5.grid(row = 4, column=1, sticky='E')

#drop-down menu
frame6 = tk.Frame(master= root)
frame6.grid(row = 3, column=0) #, sticky='W')

# root frame
rootFrame = tk.Frame(master= root, height = 300, width = 300,bg = 'red') # highlightbackground="red", highlightthickness=2) 
rootFrame.grid(row = 5, column = 1,sticky = 'W')

#image
frame7 = tk.Frame(master= rootFrame, height = 200, width = 200) #,highlightbackground="red", highlightthickness=1) #, bg = 'white')
frame7.place(x=50,y=50) #grid(row = 5, column=0, sticky='W')

#spectrogram
frame8 = tk.Frame(master= root)
frame8.grid(row = 5, column=2, sticky='W')

#scrollbar
frame9 = tk.Frame(master= rootFrame)
frame9.place(x=10,y=10) #grid(row = 5, column=1, sticky='W')

qframe= [frame1, frame2] # store frames in a list

#get computers screen dimensions 
screen_width = root.winfo_screenwidth()    #print('screen_width:', screen_width )
screen_height = root.winfo_screenheight()  #print('screen_height:', screen_height)


# root window title & set display dimension to fit users screen
root.title("PLAY AUDIO")
root.geometry(f"{int(screen_width*.7)}" + 'x' + f"{int(screen_height*.5)}")  #width x height+x+y

# questions for user
questions = [
    'Amplitude (weight scale):',
    'Frequencies (may select multiple):'
]

# create labels that prompt user for preferred settings 
for idx, qs in enumerate(questions):
    lbl = tk.Label(master=qframe[idx], text = qs, font = 'times 12 bold')
    lbl.grid(row = idx, column = 0, sticky = 'w') #idx+1


# store new inputs
getInputWts = []

# get user input for weights
# each box corresponds to specific speaker
# [1,2,3,4] = ["Left Front", "Right Front", "Left Back", "Right Back"]
def getVals():
    getInputWts.clear()

    for idx in range(4):  # 4 speakers
        newWts = storeInputWt[idx].get()   # use get to access users input
        getInputWts.append(float(newWts))   # store in list 
    
    print(getInputWts)
    print(type(getInputWts))


# store in lists 
freqBtn_list = [] # list to hold the button object
freqIdxList=[]  # list to hold users preferred frequency
storeInputWt = []  # store entry object as list

# create user input entry fields/widgets
for idx, weight in enumerate(wt):
    # create entry field
    e = tk.Entry(frame3, width =10) # , font=('ariel 15'))

    e.insert(0,weight) # default values 
    e.grid(row=0, column= idx+1, padx=5, pady=5,sticky = 'w' )  #+1 for indexing 
    storeInputWt.append(e) #append user's input to list

print(type(storeInputWt))


selectIdx = []
def selectBtn(idx):
    freqIdxList.append(idx)  # store index of button selected
    print(str("idx:"),idx)
    print(str('freq list:'),freqIdxList)
    print(freqIdxList.count(idx))

    # check if index count is odd or even
    # if odd, sink btn (as in selected)
    # if even, raise btn  (as in deselect)
    if freqIdxList.count(idx) % 2 == 1:
        freqBtn_list[idx].config(relief = 'sunken')  #select btn

        if idx not in selectIdx:
            selectIdx.append(idx)
            print(str('selected idx list:'),selectIdx)

    else:
        freqBtn_list[idx].config(relief = 'raised')  #deselect btn
        selectIdx.remove(idx)  #pop did not work here 
        print(str('updated idx list:'),selectIdx)

# create drop-down menu
cb = ttk.Combobox(frame6, state="readonly", values= signalType)
cb.set("Signal Type")
cb.grid(row=3,column=0)


#signalSelect = cb.get()
getSignalType = []

# bind the selected value changes
def getSignal(event):
    s = cb.get()
    getSignalType.append(s)

cb.bind('<<ComboboxSelected>>', getSignal)
#print('get signal:', getSignalType)

# play sound 
def playAudio():
    s = getSignalType
    s = ' '.join(s) # convert list to string
    print(s)
    #print(type(s))

    fig = Figure(figsize=(5,3))
    canvas2 = FigureCanvasTkAgg(fig,frame8)
    p1 = fig.add_subplot(111) 
    print(p1)
    
    if s == 'arbitrary sound':
        # prompt user to load in wave file
        samplerate, data = wavfile.read('voice.wav')
        print(samplerate)
        print(data)
        print(np.shape(data))

        length = data.shape[0] / samplerate
        print(f"length = {length}s")

        time = np.linspace(0., length, data.shape[0])

        #playsound('car-horn.wav')

        p1.plot(time,data)
        #canvas2 = FigureCanvasTkAgg(fig,frame8)
        #toolbar = NavigationToolbar2Tk(canvas2, frame8)
        #toolbar.update()

        canvas2.draw()
        canvas2.get_tk_widget().pack() 

        canvas2.flush_events()

        sd.play(data, mapping=[1,2,3,4])   
        sd.wait()

    else:
        newFreq = freq[freqIdxList] 
        print(str('frequency:'), str(newFreq))
        #print(newFreq)

        wt =getInputWts #np.array([1, 0, 0.5, 0])
        #print(str('weight:'), str(wt))
        # print(len(wt))

        fig = Figure(figsize=(5,3))
        canvas2 = FigureCanvasTkAgg(fig,frame8)
        p1 = fig.add_subplot(111) 
        # "111" means "1x1 grid, first subplot" and "234" means "2x3 grid, 4th subplot".

        xtt = np.zeros((4,len(t)))
        checkFreq = []
        # commented out
        # this section plays sounds out of speakers one by one
        # weight values will reflect number of speakers as well as
        # which speaker to play sound from 
        for valF in newFreq:
            for idxWt, valWt in enumerate(wt):
                print('valWt:', valWt)

                if s == 'tone':
                    xt = valWt*np.sin(2*np.pi*valF*t) #/10
                    #xtt[idxWt,:]= np.array(xt) 

                if s == 'white noise':
                    #noise
                    xt = np.random.normal(0,1,220500)/40
                    b, a = butter(2, valF/22050, btype='high', analog=False)
                    xt = valWt*filtfilt(b, a, xt)
                    #xtt[idxWt,:]= np.array(xt) 

                xtt[idxWt,:]= np.array(xt) 

                #xtt = np.zeros((len(t),4))
                #print(np.shape(xtt))

                # sd.play(xtt, mapping=[1,2,3,4])   
                # sd.wait() # wait for sound to play
                # time.sleep(1)

                if valF not in checkFreq:
                    checkFreq.append(valF)

                    p1.plot(t, xt)
                    #canvas2 = FigureCanvasTkAgg(fig,frame8)
                    #toolbar = NavigationToolbar2Tk(canvas2, frame8)
                    #toolbar.update()

                    canvas2.draw()
                    canvas2.get_tk_widget().pack() 

                    canvas2.flush_events()
                
                #fig.clf()

                # sd.play(xtt, mapping=[1,2,3,4])   
                # sd.wait() # wait for sound to play
                #time.sleep(1)
            sd.play(xtt, mapping=[1,2,3,4])   
            sd.wait() # wait for sound to play

           
idxR = 1 
idxC= 1
for fIdx,f in enumerate(freq):
    # create button widget
    button3 = tk.Button(master=frame4, text=str(f), width=10, height=2, command=lambda idx=fIdx: selectBtn(idx))

    button3.grid(row=idxR, column=idxC, padx=5, pady=10) #,  sticky="W")
    idxC = idxC+1
    freqBtn_list.append(button3)  # append button object to list


# # PLAY AUDIO button 
startButton = tk.Button(master=frame5, text = 'PLAY AUDIO', bg ='red', fg= 'black',  width=8, height=1, padx=10, pady=10, command=lambda: [getVals(),playAudio()]) #getVals())  # command=lambda: [getVals(inputWt)]#command=playAudio) 
startButton.grid(row=4, column=1) #, sticky=tk.W)

## add image to GUI 
#first create a canvas 
canvas = tk.Canvas(rootFrame, width=250, height = 250)

img = Image.open("head_top_view.jpg")
img = img.resize((200, 200))
img = ImageTk.PhotoImage(img)
tl = tk.Label(master=frame7, image=img) #, anchor = tks.E)
#canvas.create_image(20,20, anchor=tk.NW, image=img)
tl.grid(row=5) #, column = 1)

# add scrollbar
angle  = np.array([0,360,5])
scrollbar = tk.Scrollbar(frame9)
scrollbar.grid(row=5, column=1)

lst = tk.Listbox(rootFrame, yscrollcommand=scrollbar.set)
scrollbar.config(command = angle)


# ## add spectrogram to GUI 
# tt = np.arange(0, 3, .01)
# f = np.array([200, 300])
# fig = Figure(figsize=(5,3))
# canvas2 = FigureCanvasTkAgg(fig,frame8)

# for i in f:
#     xt = np.sin(2*np.pi*i*t) 

#     #noise
#     xt = np.random.normal(0,1,len(xt))/40
#     b, a = butter(2, 300/22050, btype='high', analog=False)
#     xt = filtfilt(b, a, xt)

#     fig.add_subplot(111).plot(t, xt)
#     #canvas2 = FigureCanvasTkAgg(fig,frame8)
#     #toolbar = NavigationToolbar2Tk(canvas2, frame8)
#     #toolbar.update()

#     canvas2.draw()
#     canvas2.get_tk_widget().pack() 

#     canvas2.flush_events()
#    # canvas2.draw_idle()

root.mainloop()







#####################################################################################
##### removed lines of code 
#####################################################################################

# create labels that prompt user for preferred settings 
# lbl = tk.Label(master=frame, text = questions[0], font = 'times 12 bold')
# lbl.grid(row=0, column=0) #pack(side=tk.LEFT)

# lbl = tk.Label(master=frame2, text = questions[1], font = 'times 12 bold')
# lbl.grid(row=0, column=1) #pack(side=tk.LEFT)
# select and change button color functions

# def chng_btn_color_NumSpkr(idx):
#     #nSpkrs = int(btn_list[idx].cget('text')) #get text for the selected button
#     #sd.default.channels = nSpkrs
#     #getList = nSpkrs

#     #print(type(idx))
#     totSpkrs.append(idx)
#     #print(totSpkrs)
#     #print(type(totSpkrs))
#     btn_list[idx].config(relief = 'sunken',background= 'white' )
 
# def chng_btn_color_WchSpkr(idx):
#     #print(idx)
#     wchSpkrList.append(idx)
#     #print(wchSpkrList)
#     #print(type(wchSpkrList))
#     btn2_list[idx].config(relief = 'sunken', background= 'white')



# idxR = 0
# idxC= 1
# for nSpkrIdx, numSpkr in enumerate(numSpeakers): #enumerate to get index, value

#     button = tk.Button(root, text=str(numSpkr), width=10, height=2, command=lambda idx=nSpkrIdx: chng_btn_color_NumSpkr(idx))
#     button.grid(row=idxR, column=idxC, padx=5, pady=10)
#     idxC = idxC+1

#     btn_list.append(button)  # Append button to list


# idxR = 2
# idxC= 1
# for spkrIdx, wchSpkr in enumerate(whichSpeakers):

#     button2 = tk.Button(root, text=str(wchSpkr), width=10, height=2,  command=lambda idx=spkrIdx: chng_btn_color_WchSpkr(idx))   
#     button2.grid(row=idxR, column=idxC, padx=5, pady=10)
#     idxC = idxC+1

#     btn2_list.append(button2)



# sound out of all speakers simultaneously 
#xtt = np.zeros((len(t),4))
# #play sound simultaneously 
# for idxF in newFreq:
#     print(str('idxF:'), idxF)
#     xt = np.sin(2*np.pi*idxF*t) /10
#     xt = np.random.normal(0,1,len(xt))/ 40

#     b, a = butter(2, idxF/22050, btype='high', analog=False)
#     xt = filtfilt(b, a, xt)
#     # indx = indx+1

#     for idxSpkr in numSpeakers:
#         print('idxSpkr:', idxSpkr)
#         xtt[:,idxSpkr-1]= np.array(xt)
#         print(np.shape(xtt))

# sd.play(wt*xtt, mapping=[1,2,3,4])   
# sd.wait() # wait for sound to play
# time.sleep(1)


# don't need this section -- leave for reference
# replacing number of speakers with weights
# the weight values reflect which speaker 
# for spkr in numSpeakers:
#     #print(spkr)
#     xtt = np.zeros((len(t),4))
#     xtt[:,spkr-1]= np.array(xt) 
#     #print(np.shape(xtt))

#     sd.play(xtt, mapping=[1,2,3,4])   
#     sd.wait() # wait for sound to play
#     time.sleep(1)


# path = str(Path.home() / "Downloads")
# print(path)
# #dir_list = os.listdir(path)

# # return all files as a list
# for file in os.listdir(path):
#     # check the files which are end with specific extension
#     if file.endswith('.wav'):
#         # print path name of selected files
#         print(file)