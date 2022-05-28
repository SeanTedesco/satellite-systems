import serial
from serial.serialutil import SerialException
from ..logger.logger import SatelliteLogger
import argparse
import sys
import time
import base64

class Radio:
    '''Interface class to control a radio.'''

    def __init__(self, uid, port, baud=115200, start_marker='<', end_marker='>'):
        try:
            self._arduino = serial.Serial(port=port, baudrate=baud, timeout=10, rtscts=True)
        except SerialException as e:
            raise e

        self._uid = uid
        self._start_marker = start_marker
        self._end_marker = end_marker
        self._data_buffer = ""
        self._data_started = False
        self._message_complete = False
        self.logger = SatelliteLogger.get_logger('radio')

        self.__wait_for_msg('ready: serial')
        self.__set_uid()
        self.__wait_for_msg('ready: radio')

    def transmit(self, data:str):
        '''Send a message.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def receive(self, output_file:str):
        '''Receive a message.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def command(self, command:str):
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

    def __set_uid(self):
        radio_number = str(self._uid)
        self._send_to_arduino(radio_number)

    def __wait_for_msg(self, msg:str='ready: serial', timeout:int=10):
        start_time = time.time()
        incoming = ''
        while incoming.find(msg) == -1:
            if time.time() > start_time + timeout:
                self.logger.warning(f'no message received, expected: {msg}')
                break
            incoming = self._receive_from_arduino()
            if not (incoming == 'xxx'):
                self.logger.debug(incoming)

    def _receive_from_arduino(self):

        while self._arduino.inWaiting() > 0 and self._message_complete == False:
            x = self._arduino.read().decode('utf-8')  # decode needed for Python3

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
        self._arduino.flush()
        try:
            self._arduino.write(stringWithMarkers.encode('utf-8'))
        except Exception as e:
            raise e


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control Radio Module.')
    parser.add_argument('-p', '--port', metavar='port', type=str, help='The port the radio is connected to.')
    parser.add_argument('-i', '--uid', metavar='uid', type=int, help='The unique identification number of the connected radio.')

    subparser = parser.add_subparsers()

    transmit_parser = subparser.add_parser('transmit', help='Transmit data.')
    transmit_parser.add_argument('-d', '--data', type=str, help='The string of data to be transmitted.')
    transmit_parser.set_defaults(function=do_transmit)

    monitor_parser = subparser.add_parser('monitor', help='Monitor incoming data until "STOP" is received.')
    monitor_parser.add_argument('-f', '--filename', type=str, default='output-logs.txt', help='The filename to save the incoming data.')
    monitor_parser.set_defaults(function=do_monitor)

    command_parser = subparser.add_parser('command', help='Send a command, receive acknowledgement.')
    command_parser.add_argument('-c', '--command', type=str, default='smile', help='The commmand to send to the other radio')
    command_parser.set_defaults(function=do_command)

    stream_parser = subparser.add_parser('stream', help='Stream a file to another radio.')
    stream_parser.add_argument('-f', '--filename', type=str, default='data/test-data.txt', help='The full path of the text file to be streamed.')
    stream_parser.set_defaults(function=do_stream)

    return parser.parse_args()

def do_transmit(radio, options):
    data = options.data
    radio.transmit(data)

def do_monitor(radio, options):
    filename = options.filename
    radio.monitor(filename)

def do_command(radio, options):
    cmd = options.command
    radio.command(cmd)

def do_stream(radio, options):
    input_stream = options.filename
    radio.stream(input_stream)

def main():
    from .rf24 import RF24

    options = parse_cmdline()
    radio = RF24(uid=options.uid, port=options.port)
    options.function(radio, options)

if __name__ == '__main__':
    main()
