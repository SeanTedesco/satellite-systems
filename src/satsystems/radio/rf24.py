from setuptools import Command
from .radio import Radio
import time

class RF24(Radio):

    def __init__(self, uid, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(uid, port, baud, start_marker, end_marker)

        self.supported_modes = ['T', 'S', 'R']      # transmit, stream, receive
        self.logger.info(f'radio {uid} booted')

    def transmit(self, data:str):
        '''Send a string of characters to the other radio, await for a response.

        Params:
            - data: 32 characters (string or bytes) to send.
        '''

        self._transmit_header(data)
        self.logger.debug(f'transmitted: {data}')
        got_back = self.receive()
        if got_back == 'xxx':
            self.logger.warning(f'failed to receive acknowledgement')
        self.logger.debug(f'received in return: {got_back}')

    def receive(self, timeout:float=60.0):
        '''Attempt to receive a single message from the other radio.

        Params:
            - timeout (optional): duration in which to receive a message.

        Return:
            - if received, the stripped string sent from the arduino over serial.
            - if not received, 'xxx'
        '''
        start_time = time.time()
        received = 'xxx'
        while received == 'xxx':
            received = self._receive_from_arduino().strip()
            if time.time() > start_time + timeout:
                self.logger.warning(f'no message received within {timeout} s.')
                break

        return received

    def stream(self, filename:str):
        '''
        Stream a file to the other radio.

        Params:
            - filename: the file to be transmitted.
        '''
        if not filename.strip():
            raise FileNotFoundError('No file specified to be streamed.')

        # extra the meta data from the file to be sent
        num_characters = self._file_length(filename)
        num_payloads = int(num_characters / 32) + 1 # max number of characters that can be sent with the RF24 radios is 32
        self.logger.debug(f'reading {num_characters} characters ({num_payloads} payloads) from file: {filename}')

        self._transmit_header('receive_stream', 's', num_payloads)
        time.sleep(1)
        with open(filename, mode='r', encoding='utf8') as file:
            lines = file.read()
            start = 0
            stop = 32
            for i in range(num_payloads):
                to_send = lines[start:stop]
                self.logger.debug(f'stream [{i}]: {to_send}')
                self._transmit_raw(to_send)
                start = stop
                stop = start + 32
                time.sleep(0.001) # do not comment out else packets will be dropped
        time.sleep(1)
        self._transmit_header('stop_stream')

    def monitor(self, filename:str, stop_message:str='STOP'):
        '''Constantly listen for a signal until a certian message is received.

        Params:
            - stop_message: the message to stop the monitoring.
            - filename: specify where to save a stream if one is received
                during the monitoring.
        '''
        received = 'xxx'
        while received != stop_message:
            received = self.receive()

            if received == 'receive_stream':
                self.logger.debug('receiving a stream')
                self._receive_stream(filename)
                self.logger.debug('ending a stream')
            elif not (received == 'xxx'):
                self.logger.info(f'received: {received}')

    def beacon(self, status:str='healthy', keep_listening=False, pulse_count:int=10):
        '''Transmit a beacon message.'''

        for i in range(pulse_count):
            self._transmit_header('VA3TFO')
            time.sleep(1)
            self._transmit_header(status)
            time.sleep(1)

    def _receive_stream(self, filename:str):
        '''
        Receive a streamed file from another radio.
        '''
        received = 'xxx'
        while received != 'stop_stream':
            if not (received == 'xxx'):
                with open(filename, mode='a', encoding='utf8') as file:
                    file.write(received)
            received = self.receive()

    def _transmit_raw(self, data:str):
        '''Transmit 32 characters to the radio. No formatting for raw transmission.

        Params:
            data: the raw data to be transmitted to the other radio.
        Raises:
            ValueError: the radio can not transmit an empty message or a string greater
                        that 32 bytes long.
        Return:
            the number of characters transmitted.
        '''
        data_len = len(data)

        if not data: # must not be an empty string
            raise ValueError('passed in an empty string!')

        if data_len > 32: # max 32 bytes for a single transmission
            raise ValueError(f'string is too long, {data_len} is greater than 32 characters')

        try:
            self._send_to_arduino(data)
        except Exception as e:
            self.logger.error(f'failed to transmit: {data}')
            raise e

        return data_len

    def _transmit_header(self, data:str, mode:str='T', num_payloads:int=1):
        '''Send a single header message.

        Params:
            data: the header message to be transmitted to the other radio.
            mode: the mode to switch the radio to. Can be "T" or "S".
        Raises:
            ValueError: the radio can not transmit an empty message or a string greater
                        that 32 bytes long.
        Return:
            the number of characters transmitted.
        '''

        data_len = len(data)

        if not data: # must not be an empty string
            raise ValueError('passed in an empty string!')

        if data_len > 32: # max 32 bytes for a single transmission
            raise ValueError(f'string is too long, {data_len} is greater than 32 characters')

        formatted_data = self._format_header(mode, num_payloads, data)
        try:
            self._send_to_arduino(formatted_data)
        except Exception as e:
            self.logger.error(f'failed to transmit: {formatted_data}')
            raise e

        return data_len

    def _format_header(self, mode:str, num_payloads:int, data:str):
        '''Formart the data to what the arduino expects for transmissions.

        Return:
            - formatted data string to be then called with _send_to_arduino
        '''
        mode = mode.upper()
        if mode not in self.supported_modes:
            raise IndexError(f'Using unsupported mode: {mode}, "T", "S", or "R" are expected.')

        return mode + ':' + str(num_payloads) + ':' + data

    @staticmethod
    def _file_length(filename:str):
        if not filename.strip():
            raise FileNotFoundError('No file specified, can not determine length.')

        with open(filename, mode='r', encoding='utf8') as file:
            return(len(file.read()))