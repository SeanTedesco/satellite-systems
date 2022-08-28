import serial
from serial.serialutil import SerialException
from ..common.logger import SatelliteLogger
import argparse
import time


class Reactionwheel:
    '''Interface class to control a reaction wheel.'''

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
        self.logger = SatelliteLogger.get_logger('reactionwheel')

        self.__wait_for_msg('ready: serial')
        self.__set_uid()
        self.__wait_for_msg('ready: reactionwheel')

    def rotate_cw(self, degrees:int):
        '''Rotate the body a set amount of degrees clockwise.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def rotate_ccw(self, degrees:int):
        '''Rotate the body a set amount of degrees counter-clockwise.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def stabilize(self):
        '''Hold the body in it's current attitude.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def __set_uid(self):
        if self._uid not in [0, 1, 2]:
            raise ValueError(f'uid must be 0, 1, or 2 not {self._uid}')
        rw_number = str(self._uid)
        self._send_to_arduino(rw_number)

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
    parser = argparse.ArgumentParser(description='Control Reaction Wheel Module.')
    parser.add_argument('-p', '--port', metavar='port', type=str, help='The port the reaction wheel is connected to.')
    parser.add_argument('-i', '--uid', metavar='uid', type=int, help='The unique identification number of the connected reaction wheel.')

    subparser = parser.add_subparsers()

    cw_parser = subparser.add_parser('rotate-cw', help='Rotate Clockwise')
    cw_parser.add_argument('-d', '--degree', type=int, help='The amount of degrees to turn clockwise.')
    cw_parser.set_defaults(function=do_rotate_cw)

    ccw_parser = subparser.add_parser('rotate-ccw', help='Rotate Counter Clockwise')
    ccw_parser.add_argument('-d', '--degree', type=int, help='The amount of degrees to turn counter clockwise.')
    ccw_parser.set_defaults(function=do_rotate_ccw)

    ccw_parser = subparser.add_parser('rotate-cw', help='Rotate Clockwise')
    ccw_parser.add_argument('-d', '--degree', type=int, help='The amount of degrees to turn clockwise.')
    ccw_parser.set_defaults(function=do_rotate_cw)


    return parser.parse_args()

def do_rotate_cw(rw, options):
    degree = options.degree
    rw.rotate_cw(degree)

def do_rotate_ccw(rw, options):
    degree = options.degree
    rw.rotate_cw(degree)

def main():
    from .rf24 import RF24

    options = parse_cmdline()
    radio = RF24(uid=options.uid, port=options.port)
    options.function(radio, options)

if __name__ == '__main__':
    main()
