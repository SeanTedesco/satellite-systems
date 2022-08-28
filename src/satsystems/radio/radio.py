from ..common.logger import SatelliteLogger
from ..common.mcu import MCU
import argparse
import time

class Radio:
    '''Interface class to control a radio.'''

    def __init__(self, uid, port, baud=115200, start_marker='<', end_marker='>'):

        self._uid = uid
        self.logger = SatelliteLogger.get_logger('radio')

        try:
            self._arduino = MCU(port, baud, start_marker, end_marker)
        except Exception as e:
            self.logger.critical(f'failed to open connection to MCU on port: {port}')
            raise e

        self._wait_for_msg('ready: serial')
        self._set_uid()
        self._wait_for_msg('ready: radio')

    def transmit(self, data:str):
        '''Send a message.'''
        raise NotImplementedError('Should be implemented by derived class.')

    def receive(self, output_file:str):
        '''Receive a message.'''
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

    def _set_uid(self):
        if self._uid not in [0, 1]:
            raise ValueError(f'uid must be 0 or 1, not {self._uid}')
        radio_number = str(self._uid)
        self._arduino.send_over_serial(radio_number)

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

    beacon_parser = subparser.add_parser('beacon', help='Send out a beacon signal.')
    beacon_parser.add_argument('-s', '--status', type=str, default='healthy', help='The status of the satellite.')
    beacon_parser.add_argument('-k', '--keep-listening', action='store_true', help='The satellite listens for a response after the beacon.')
    beacon_parser.set_defaults(function=do_beacon)

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

def do_beacon(radio, options):
    stats = options.status
    keep_listening = options.keep_listening
    radio.beacon(stats, keep_listening)

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
