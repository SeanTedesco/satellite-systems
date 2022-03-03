import serial
from serial.serialutil import SerialException
import argparse

class Radio:
    '''Interface class to control a radio.'''

    def __init__(self, port, baudrate, **kwargs):
        self.port = port
        self.baudrate = baudrate
        try:
            self.arduino = 'ARDUINO OBJECT'
            #self.arduino = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=10, rtscts=True)
        except SerialException as e:
            raise e('is the radio connected?')

    def send(self, **kwargs):
        '''Send a message.'''
        raise NotImplementError('Should be implemented by derived class.')


    def receive(self, **kwargs):
        '''Receive a message.'''
        raise NotImplementError('Should be implemented by derived class.')


def parse_cmdline():
    pass

def main():
    from .rf24 import RF24

    #options = parse_cmdline()
    radio = RF24(uid='radio_uid', port='/dev/ttyUSB2', baudrate=115200)
    radio.send()
    #options.functions(options, radio)

if __name__ == '__main__':
    main()
