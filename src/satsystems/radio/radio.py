import serial
from serial.serialutil import SerialException
import argparse
import sys
import time
import base64

class Radio:
    '''Interface class to control a radio.'''

    def __init__(self, port, baud=115200, start_marker='<', end_marker='>'):
        try:
            self.arduino = serial.Serial(port=port, baudrate=baud, timeout=10, rtscts=True)
        except SerialException as e:
            raise e

        self._start_marker = start_marker
        self._end_marker = end_marker
        self._data_buffer = ""
        self._data_started = False
        self._message_complete = False

        self._wait_for_ready()

    def transmit(self, data:str):
        '''Send a message.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def receive(self, output_file:str):
        '''Receive a message.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def command(self, command_code:int):
        '''Send a command/request to the other radio, await for a response.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def stream(self, filename:str):
        '''Stream data in a file.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def beacon(self):
        '''Transmit a beacon message.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def monitor(self):
        '''Constantly listen for a signal.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def _wait_for_ready(self):
        msg = ''
        while msg.find('ready: serial') == -1:
            msg = self._receive_from_arduino()
            if not (msg == 'xxx'):
                print(msg)

    def _receive_from_arduino(self):

        while self.arduino.inWaiting() > 0 and self._message_complete == False:
            x = self.arduino.read().decode('utf-8')  # decode needed for Python3

            if self._data_started == True:
                if x != self._end_marker:
                    self._data_buffer = self._data_buffer + x
                else:
                    self._data_started = False
                    self._message_complete = True
            elif x == self._start_marker:
                self._data_buffer = ''
                self._data_started = True

        if self._message_complete == True:
            self._message_complete = False
            return self._data_buffer
        else:
            return 'xxx'

    def _send_to_arduino(self, data:str):

        stringWithMarkers = self._start_marker
        stringWithMarkers += data
        stringWithMarkers += self._end_marker
        self.arduino.flush()
        try:
            self.arduino.write(stringWithMarkers.encode('utf-8'))
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
    receive_parser.add_argument('-f', '--filename', type=str, default="output-logs.txt", help='The filename to save the output of the received transmission')
    receive_parser.set_defaults(function=do_receive)

    receive_parser = subparser.add_parser('command', help='Send a command, receive acknowledgement.')
    receive_parser.add_argument('-c', '--command', type=str, default='smile', help='The commmand to send to the other radio')
    receive_parser.set_defaults(function=do_command)

    return parser.parse_args()

def do_transmit(radio, options):
    data = options.data
    radio.transmit(data)

def do_receive(radio, options):
    output = options.filename
    radio.receive(output)

def do_command(radio, options):
    cmd = options.command
    radio.command(cmd)

def main():
    from .rf24 import RF24

    options = parse_cmdline()
    radio = RF24(port=options.port)
    options.function(radio, options)

if __name__ == '__main__':
    main()
