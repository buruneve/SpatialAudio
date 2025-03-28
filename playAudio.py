#playAudio.py

## # %%

#imports
import sounddevice as sd
import numpy as np

#settings
# all 4 speakers: [1,2,3,4] [LF, RF, LB, RB]
# front two: [1,2]; back two: [3,4]

userInput = input('Which speakers do you want to play? \nEnter values separated by space: ')
userInput = userInput.split()
whichSpeakers = np.array(userInput, dtype=int) 


fs = 44100
sd.default.samplerate = fs
sd.default.channels = 4

numSpeakers = np.array([1,2,3,4]) # total number of speakers
f = np.array([200, 300]) #, 400, 500, 600])
t = np.arange(0, 5, 1/44100)
print(f); print(len(t)); #print(np.shape(t))

# view device info
getDeviceInfo = sd.query_devices(kind = 'output')
#print(dict(getDeviceInfo)) #dictionary (key, value)

x = getDeviceInfo["index"] # device ID 
#print(x)


# play sound 
indx=0 # indexing starts at 0
for idxF in f:
    xt = np.sin(2*np.pi*f[indx]*t) 
    indx = indx+1

    for spkr in whichSpeakers:
        xtt = np.zeros((len(t),len(numSpeakers)))
        xtt[:,spkr-1]= np.array(xt) # spkr-1 bc of indexing 

        sd.play(xtt, mapping=[1,2,3,4])   
        sd.wait() # wait for sound to play

