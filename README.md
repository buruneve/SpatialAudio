README.md

pip install adafruit-circuitpython-drv2605 adafruit-circuitpython-tca9548a

enable i2c interface on Pi:
1 method:
open terminal window: sudo raspi-config
select/highlight "interfacing options"
select/highlight 'I2C'
enable 

2 method:
click on raspberry icon upper left corner
prepreferences --> raspberry pi configuration --> interfaces tab --> enable i2c 
reboot is required 

for ImportError: No module names RPi:
in terminal: pip3 install RPi.GPIO