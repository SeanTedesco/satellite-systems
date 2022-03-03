import serial
from serial.serialutil import SerialException
import argparse
import serial
import sys
import time
import base64

class Radio:
    '''Interface class to control a radio.'''

    def __init__(self, port, baud=115200, start_marker='<', end_marker='>'):
        try:
            self.arduino = 'OBJECT'
            '''
            self.arduino = serial.Serial(port=port, baudrate=baud, timeout=10, rtscts=True)
            self._wait_for_ready(self)
            '''
        except SerialException as e:
            raise e

        self._start_marker = start_marker
        self._end_marker = end_marker
        self._data_buffer = ""
        self._data_started = False
        self._message_complete = False


    def send(self, **kwargs):
        '''Send a message.'''
        raise NotImplementedError('Should be implemented by derived class.')


    def receive(self, **kwargs):
        '''Receive a message.'''
        raise NotImplementedError('Should be implemented by derived class.')


    def _wait_for_ready(self):
        msg = ""
        while msg.find("<arduino is ready>") == -1:
            msg = self.receive_from_arduino()
            if not (msg == "xxx"):
                print(msg)


    def _receive_from_arduino(self):

        if self.arduino.inWaiting() > 0 and self._message_complete == False:
            x = self.arduino.read().decode("utf-8")  # decode needed for Python3

            if dataStarted == True:
                if x != self._end_marker:
                    self._data_buffer = self._data_buffer + x
                else:
                    dataStarted = False
                    self._message_complete = True
            elif x == self._start_marker:
                self._data_buffer = ""
                dataStarted = True

        if self._message_complete == True:
            self._message_complete = False
            return self._data_buffer
        else:
            return "xxx"


    def _send_to_arduino(self, data:str):

        stringWithMarkers = self.start_marker
        stringWithMarkers += data
        stringWithMarkers += self.end_marker

        try:
            self.arduino.write(stringWithMarkers.encode("utf-8"))
        except Exception as e:
            raise e


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control Radio Module.')
    parser.add_argument('-p', '--port', metavar='port', type=str, help='The port the radio is connected to.')

    subparser = parser.add_subparsers()

    transmit_parser = subparser.add_parser('transmit', help='Transmit data.')
    transmit_parser.set_defaults(function=do_transmit)

    receive_parser = subparser.add_parser('receive', help='Receive data.')
    receive_parser.set_defaults(function=do_receive)

    return parser.parse_args()

def do_transmit(radio, **kwargs):
    print(f'do transmit with: {kwargs}')
    radio.send()

def do_receive(radio, **kwargs):
    print(f'do receive with: {kwargs}')
    radio.receive()

def main():
    from .rf24 import RF24

    options = parse_cmdline()
    radio = RF24(port=options.port)
    options.function(radio, option=options)

if __name__ == '__main__':
    main()
