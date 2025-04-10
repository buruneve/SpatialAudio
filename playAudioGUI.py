#playAudioGUI.py 

# import libraries
import tkinter as tk
import numpy as np
import sounddevice as sd


# settings
fs = 44100
sd.default.samplerate = fs
sd.default.channels = 4
t = np.arange(0, 5, 1/fs)

# create root/main window
root= tk.Tk()
frame = tk.Frame(root)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

#print('screen_width:', screen_width )
#print('screen_height:', screen_height)


# root window title & dimension
root.title("PLAY AUDIO")
root.geometry(f"{int(screen_width*.4)}" + 'x' + f"{int(screen_height*.5)}")  #width x height+x+y

# questions for user
questions = [
    'Total number of speakers:',
    'Which speakers to play \n(may select multiple):',
    'Frequencies to play \n (may select multiple):',
    'Weight scale:'
]

for idx, qs in enumerate(questions):
    lbl = tk.Label(root, text = qs, font = 'times 12 bold')
    lbl.grid(row = idx, column = 0, sticky = 'w')

#options for user to select from
numSpeakers = np.array([4]) #np.array([1,2,3,4])
whichSpeakers = np.array(["Left Front", "Right Front", "Left Back", "Right Back"])   #1,2,3,4
freq = np.array([200, 300, 400, 500, 600])


# Lists to hold the button objects
btn_list = [] 
btn2_list = []
btn3_list = []

totSpkrs=[]
wchSpkrList=[]
wchFreqList=[]

input = {}
e = tk.Entry(root)
e.grid(row =3, column = 1, padx=5, pady=5 )
input = e


# select and change button color functions

def chng_btn_color_NumSpkr(idx):
    #nSpkrs = int(btn_list[idx].cget('text')) #get text for the selected button
    #sd.default.channels = nSpkrs
    #getList = nSpkrs

    #print(type(idx))
    totSpkrs.append(idx)
    #print(totSpkrs)
    #print(type(totSpkrs))
    btn_list[idx].config(relief = 'sunken',background= 'white' )
 
def chng_btn_color_WchSpkr(idx):
    #print(idx)
    wchSpkrList.append(idx)
    #print(wchSpkrList)
    #print(type(wchSpkrList))
    btn2_list[idx].config(relief = 'sunken', background= 'white')

def chng_btn_color_WchFreq(idx):
    wchFreqList.append(idx)
    #print(wchFreqList)
    btn3_list[idx].config(relief = 'sunken',background= 'white')


# play sound 
def playAudio():

    newWhichSpeakers = wchSpkrList
    print(str('speakers:'), str(newWhichSpeakers), str('aka:'), str(whichSpeakers[wchSpkrList]))
    #print(newWhichSpeakers)
    newFreq = freq[wchFreqList]
    print(str('frequency:'), str(newFreq))
    #print(newFreq)


    #freq = [300]
    wt =np.array([1, 0, 0.5, 0])
    xtt = np.zeros((len(t),4))
    print(np.shape(xtt))

    #numSpeakers = np.array([1,2,3,4])

    for idxF in newFreq:
        xt = np.sin(2*np.pi*idxF*t) 

        for idxSpkr in newWhichSpeakers:
            xtt[:,idxSpkr-1]= np.array(xt)

    sd.play(wt*xtt, mapping=[1,2,3,4])   
    sd.wait() # wait for sound to play


    # commented out
    # this section plays sounds out of speakers one by one
    # for idxF in newFreq:
    #     xt = np.sin(2*np.pi*idxF*t) 
 
    #     for spkr in newWhichSpeakers:
    #         #print(spkr)
    #         xtt = np.zeros((len(t),int(numSpeakers)))
    #         xtt[:,spkr]= np.array(xt) 
    #         #print(np.shape(xtt))

    #         sd.play(xtt, mapping=[1,2,3,4])   
    #         sd.wait() # wait for sound to play


idxR = 0
idxC= 1
for nSpkrIdx, numSpkr in enumerate(numSpeakers): #enumerate to get index, value

    button = tk.Button(root, text=str(numSpkr), width=10, height=2, command=lambda idx=nSpkrIdx: chng_btn_color_NumSpkr(idx))
    button.grid(row=idxR, column=idxC, padx=5, pady=10)
    idxC = idxC+1

    btn_list.append(button)  # Append button to list


idxR = 1
idxC= 1
for spkrIdx, wchSpkr in enumerate(whichSpeakers):

    button2 = tk.Button(root, text=str(wchSpkr), width=10, height=2,  command=lambda idx=spkrIdx: chng_btn_color_WchSpkr(idx))   
    button2.grid(row=idxR, column=idxC, padx=5, pady=10)
    idxC = idxC+1

    btn2_list.append(button2)

idxR = 2
idxC= 1
for fIdx,f in enumerate(freq):

    button3 = tk.Button(root, text=str(f), width=10, height=2, command=lambda idx=fIdx: chng_btn_color_WchFreq(idx))
    button3.grid(row=idxR, column=idxC, padx=5, pady=10)
    idxC = idxC+1
    btn3_list.append(button3)


# # PLAY AUDIO button 
startButton = tk.Button(root, text = 'PLAY AUDIO', bg ='red', fg= 'black',  width=10, height=1, padx=5, pady=10, command=playAudio) 
startButton.grid(row=5, column=0, sticky='e')






root.mainloop()