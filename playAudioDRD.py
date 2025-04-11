#playAudio.py

#imports
import sounddevice as sd
import numpy as np
import time
from scipy.signal import butter, filtfilt
# PROMPT USER + SETTINGS
# - total number of speakers
# - to determine which speakers to play sound from 
#       all 4 speakers: [1,2,3,4] [LF, RF, LB, RB]
#       front two: [1,2]; back two: [3,4]
# - which frequencies to play

userInputNumSpeakers = input('Total number of speakers?: ')
numSpeakers = np.arange(1, int(userInputNumSpeakers)+1)

userInputSpeakers = input('Which speakers to play sound from? Enter values separated by space: ')
userInputSpeakers = userInputSpeakers.split()
whichSpeakers = np.array(userInputSpeakers, dtype=int) 

userInputFreq = input('Frequency values? Enter values separated by space: ')
userInputFreq = userInputFreq.split()
freq = np.array(userInputFreq, dtype=int) 

# settings
fs = 44100
sd.default.samplerate = fs
sd.default.channels = userInputNumSpeakers
t = np.arange(0, 1, 1/fs)


# view device info
getDeviceInfo = sd.query_devices(kind = 'output')  #print(dict(getDeviceInfo)) #dictionary (key, value)
x = getDeviceInfo["index"] # device ID  #print(x)


# play sound 
indx=0  #indexing starts at 0
for idxF in freq:
    xt = np.sin(2*np.pi*freq[indx]*t) / 10
    xt = np.random.normal(0,1,len(xt))/ 40

    b, a = butter(2, freq/22050, btype='high', analog=False)
    xt = filtfilt(b, a, xt)
    indx = indx+1
    
    for spkr in whichSpeakers:
        xtt = np.zeros((len(t),len(numSpeakers)))
        xtt[:,spkr-1]= np.array(xt) # spkr-1 bc of indexing 

        sd.play(xtt, mapping=[1,2,3,4])   
        sd.wait() # wait for sound to play
        time.sleep(1)
