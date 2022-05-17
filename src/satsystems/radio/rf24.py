from setuptools import Command
from .radio import Radio
import time

class RF24(Radio):

    def __init__(self, uid, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(uid, port, baud, start_marker, end_marker)

        self.stop_receive = 'STOP'                  # message to stop receiving messages
        self.supported_commands = [
            'smile',
            'picture',
            'strobe',
            'receive_stream',
        ]
        self.supported_modes = ['T', 'S', 'R']
        self.logger.info(f'radio {uid} booted')

    def command(self, command:str):
        '''Send a command/request to the other radio, await for a response.'''

        if command not in self.supported_commands:
            raise ValueError(f'command: {command} is not supported.')

        self._transmit_header(command)
        self.logger.debug(f'transmitted command: {command}')
        got_back = self._receive()
        if got_back == 'xxx':
            self.logger.warning(f'failed to receive acknowledgement')

    def stream(self, filename:str):
        if not filename.strip():
            raise FileNotFoundError('No file specified to be streamed.')
        num_characters = self._file_length(filename)
        num_payloads = int(num_characters / 32) + 1 # max number of characters that can be sent with the RF24 radios is 32
        self.logger.debug(f'reading {num_characters} number of characters / ({num_payloads} payloads) from file: {filename}')
        self._transmit_header('receive_stream', 's', num_payloads)
        with open(filename, mode='r', encoding='utf8') as file:
            lines = file.read()
            start = 0
            stop = 31
            for i in range(num_payloads):
                to_send = lines[start:stop]
                self.logger.debug(f'streaming: {to_send}')
                self._transmit_raw(to_send)
                start = stop + 1
                stop = start + 31
                time.sleep(0.001) # do not comment out else packets will be dropped

    def beacon(self, status:str='healthy', pulse_count:int=10):
        '''Transmit a beacon message.'''

        for i in range(pulse_count):
            self._transmit_header('VA3TFO')
            time.sleep(1)
            self._transmit_header(status)
            time.sleep(1)

    def monitor(self, filename:str):
        '''Constantly listen for a signal until a command is received.

        Return: one of the commands in the list of supported commands.
        '''

        received = 'xxx'

        if not filename.strip():
            raise FileNotFoundError('No file specified for output monitoring.')

        while received != self.stop_receive:
            received = self._receive()
            if not (received == 'xxx'):
                self.logger.info(f'received: {received}')
                if received in self.supported_commands:
                    self.logger.debug(f'raising flag for command: {received}')
                    return received

    def receive_stream():
        pass

    def _receive(self, timeout:float=60.0):
        '''Attempt to receive a single message from the arduino.

        Params:
            - Timeout (optional): duration in which to receive a message.
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
        data_string = data.strip()
        data_string_len = len(data_string)

        if not data_string: # must not be an empty string
            raise ValueError('passed in an empty string!')

        if len(data) > 32: # max 32 bytes for a single transmission
            raise ValueError(f'string is too long, {data_string_len} is greater than 32 characters')

        try:
            self._send_to_arduino(data_string)
        except Exception as e:
            self.logger.error(f'failed to transmit: {data_string}')
            raise e

        return data_string_len

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

        data_string = data.strip()
        data_string_len = len(data_string)

        if not data_string: # must not be an empty string
            raise ValueError('passed in an empty string!')

        if len(data) > 32: # max 32 bytes for a single transmission
            raise ValueError(f'string is too long, {data_string_len} is greater than 32 characters')

        formatted_data = self.__format_tx_header(mode, num_payloads, data_string)
        try:
            self._send_to_arduino(formatted_data)
        except Exception as e:
            self.logger.error(f'failed to transmit: {formatted_data}')
            raise e

        return data_string_len

    def __format_tx_header(self, mode:str, num_payloads:int, data:str):
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