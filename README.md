# satellite-systems
Package for common satellite systems to be used across multiple projects.

## Setup 
```
cd satellite-systems/
pip3 install --user .

```

Ensure all your path variables are set on your computer. You may need to include the following paths in your environment variables: 
- python path
- /home/your-usr-name/.local/bin

## Application
You can use this as a package in a seperate python project, or you can have access to each of the satellite systems seperately through a Command Line Interface (CLI). 


## RADIO
An example import into a python project is given below: 

```
from satsystems import radio

comms = radio.open_resource('arduino-radio-1')
comms.receive()
```
And an example of the CLI is given below: 

```
radio --port '/dev/ttyUSB0' send 'importantdatatosend'
```
