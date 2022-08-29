from ..common.logger import SatelliteLogger
from ..common.mcu import MCU
import argparse
import time


class Reactionwheel:
    '''Interface class to control a reaction wheel.'''

    def __init__(self, uid, port, baud=115200, start_marker='<', end_marker='>'):

        self._uid = uid
        self.logger = SatelliteLogger.get_logger('reactionwheel')

        try:
            self._arduino = MCU(port, baud, start_marker, end_marker)
        except Exception as e:
            self.logger.critical(f'failed to open connection to MCU on port: {port}')
            raise e

        self._wait_for_msg('ready: serial')
        self._set_uid()
        self._wait_for_msg('ready: reactionwheel')

    def rotate_cw(self, degrees:int):
        '''Rotate the body a set amount of degrees clockwise.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def rotate_ccw(self, degrees:int):
        '''Rotate the body a set amount of degrees counter-clockwise.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def stabilize(self):
        '''Hold the body in it's current attitude.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def _set_uid(self):
        if self._uid not in [0, 1, 2]:
            raise ValueError(f'uid must be 0, 1, or 2. Not {self._uid}')
        rw_number = str(self._uid)
        self._arduino.send_over_serial(rw_number)

    def _wait_for_msg(self, msg:str='ready: serial', timeout:int=10):
        start_time = time.time()
        incoming = ''
        while incoming.find(msg) == -1:
            if time.time() > start_time + timeout:
                self.logger.warning(f'no message received, expected: {msg}')
                break
            incoming = self._arduino.receive_over_serial()
            if not (incoming == 'xxx'):
                self.logger.debug(incoming)


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

    detumble_parser = subparser.add_parser('detumble', help='reduce the angular momentum of the satellite.')
    detumble_parser.add_argument('-t', '--timeout', type=float, help='The amount of degrees to turn clockwise.')
    detumble_parser.set_defaults(function=do_detumble)

    return parser.parse_args()

def do_rotate_cw(rw, options):
    degree = options.degree
    rw.rotate_cw(degree)

def do_rotate_ccw(rw, options):
    degree = options.degree
    rw.rotate_ccw(degree)

def do_detumble(rw, options):
    timeout = options.timeout
    rw.detumble(timeout)

def main():
    from .HS08 import HS08

    options = parse_cmdline()
    reactionwheel = HS08(uid=options.uid, port=options.port)
    options.function(reactionwheel, options)

if __name__ == '__main__':
    main()