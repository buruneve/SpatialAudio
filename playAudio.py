#playAudio.py

#imports
import sounddevice as sd
import numpy as np



getDeviceInfo = sd.query_devices(kind = 'output')
#print(getDeviceInfo)  #dictionary (key, value)

#settings
fs = 44100
sd.default.samplerate = fs
#sd.default.channels = 8

print(dict(getDeviceInfo))

x = getDeviceInfo["index"]
print(x)


f = np.array([200, 300, 400, 500, 600])
t = np.arange(0, 3, 1/44100)
print(f)
print(np.shape(t))

xt1 = np.sin(2*np.pi*f[0]*t)
xt2 = np.sin(2*np.pi*f[1]*t)
xt3 = np.sin(2*np.pi*f[2]*t)
xt4 = np.sin(2*np.pi*f[3]*t)
print(np.shape(xt1))

xtt = np.zeros((132300,4))
print(np.shape(xtt))

xtt[:,0]= np.array(xt1)
sd.play(xtt, mapping=[1,1,1,1]) #,2,3,4]) 
sd.wait() # wait for sound to play

xtt = np.zeros((132300,4))
xtt[:,1] = np.array(xt2)
sd.play(xtt,mapping=[1,2,3,4])
sd.wait()

xtt = np.zeros((132300,4))
xtt[:,2] = np.array(xt3)
sd.play(xtt, mapping=[1,2,3,4])
sd.wait() 

xtt = np.zeros((132300,4))
xtt[:,3] = np.array(xt4)
sd.play(xtt, mapping=[1,2,3,4])
sd.wait() 