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
            self.arduino = serial.Serial(port=port, baudrate=baud, timeout=10, rtscts=True)
            self._wait_for_ready(self)
        except SerialException as e:
            raise e

        self._start_marker = start_marker
        self._end_marker = end_marker
        self._data_buffer = ""
        self._data_started = False
        self._message_complete = False


    def transmit(self, data:str):
        '''Send a message.'''
        raise NotImplementedError('Should be implemented by derived class.')


    def receive(self, output_file:str):
        '''Receive a message.'''
        raise NotImplementedError('Should be implemented by derived class.')


    def command(self, command_code:int):
        '''Send a command/request to the other radio, await for a response.'''
        raise NotImplementedError('Should be implemented by derived class.')


    def _wait_for_ready(self):
        msg = ""
        while msg.find("<ready: serial>") == -1:
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
        self.arduino.flush()
        try:
            self.arduino.write(stringWithMarkers.encode("utf-8"))
        except Exception as e:
            raise e


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control Radio Module.')
    parser.add_argument('-p', '--port', metavar='port', type=str, help='The port the radio is connected to.')

    subparser = parser.add_subparsers()

    transmit_parser = subparser.add_parser('transmit', help='Transmit data.')
    transmit_parser.add_argument('-d', '--data', type=str, help='The string of data to be transmitted.')
    transmit_parser.set_defaults(function=do_transmit)

    receive_parser = subparser.add_parser('receive', help='Receive data.')
    receive_parser.add_argument('-f', '--filename', type=str, default="output-logs", help='The filename to save the output of the received transmission')
    receive_parser.set_defaults(function=do_receive)

    return parser.parse_args()

def do_transmit(radio, options):
    print(f'do transmit with: {options}')
    data = options.data
    radio.transmit(data)

def do_receive(radio, options):
    print(f'do receive with: {options}')
    output = options.output
    radio.receive(output)

def main():
    from .rf24 import RF24

    options = parse_cmdline()
    radio = RF24(port=options.port)
    options.function(radio, options)

if __name__ == '__main__':
    main()
