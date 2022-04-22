# satellite-systems
Package for common satellite systems to be used across multiple projects.

## Setup 
```
cd satellite-systems/
python3 -m venv .venv
. .venv/bin/actiave
.venv/bin/python3 -m pip install --upgrade pip
.venv/bin/pip3 install -e .
```

Ensure all your path variables are set on your computer. You may need to include the following paths in your environment variables: 
- python path
- /home/your-usr-name/.local/bin

## Application
You can use this as a package in a seperate python project, or you can have access to each of the satellite systems seperately through a Command Line Interface (CLI). 

## RADIO
An example import into a python project is given below: 

```
from satsystems.radio.rf24 import RF24

comms = RF24(uid='transmitter-1', port='/dev/ttyUSB0', baudrate=115200)
comms.receive()
```
And an example of the CLI is given below: 

```
radio --port '/dev/ttyUSB0' send 'importantdatatosend'
```

## GPS
An example import into a python project is given below: 

```
from satsystems.gps.grove import Grove

grove_gps = Grove(uid='gps-2', port='/dev/ttyUSB1', baudrate=115200)

```
And an example of the CLI is given below: 

```
gps --port '/dev/ttyUSB0' get
```

## CAMERA
:exclamation: When connecting the Pi-Camera to the Raspberry Pi, ensure that the Raspberry Pi is powered off! The camera will be damaged otherwise! :exclamation: You can follow the steps outlined [here](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/2) to configure the Raspberry Pi to use the Pi-Cam. 

An example import into a python project is given below: 

```
from satsystems.camera.picam import PiCam

camera = PiCam(uid='camera-1')

```
And an example of the CLI is given below: 

```
camera shot --filename 'test-shot-1'
```