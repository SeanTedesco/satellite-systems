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
        ]
        self.supported_modes = ['T', 'S', 'R']
        self._command_flag = ''

    @property
    def command_flag(self):
        return self._command_flag

    @command_flag.setter
    def command_flag(self, command):
        self._command_flag = command

    @staticmethod
    def _file_length(filename:str):
        if not filename.strip():
            raise FileNotFoundError('No file specified, can not determine length.')

        with open(filename, mode='r', encoding='utf8') as file:
            return(len(file.read()))

    def command(self, command:str):
        '''Send a command/request to the other radio, await for a response.'''

        # verify request code
        # generate matching checksum with request code
        # change request code to str
        # transmit request str
        # receive responses
        # stop receiving when timeout or ending message
        # compare received with expected checksum
        # inform user of success or faiilure  

        self.transmit(command)
        self.logger.debug(f'transmitted command: {command}')
        got_back = self._receive()
        if got_back == 'xxx':
            self.logger.warning(f'failed to receive acknowledgement')

    def stream(self, filename:str):
        if not filename.strip():
            raise FileNotFoundError('No file specified for output monitoring.')

        num_characters = self._file_length(filename)
        self.logger.debug(f'reading {num_characters} number of characters from file {filename}')
        #with open(filename, mode='r', encoding='utf8') as file:2
        #    line = file.readline()

    def beacon(self, status:str='healthy', pulse_count:int=10):
        '''Transmit a beacon message.'''

        for i in range(pulse_count):
            self.transmit('VA3TFO')
            time.sleep(1)
            self.transmit(status)
            time.sleep(1)

    def monitor(self, filename:str):
        '''Constantly listen for a signal.

        Sets the radios command flag if any incoming data matches a supported command
        '''

        received = 'xxx'
        received_count = 0

        if not filename.strip():
            raise FileNotFoundError('No file specified for output monitoring.')

        while received != self.stop_receive:
            received = self._receive()
            if not (received == 'xxx'):
                received_count += len(received)
                self.logger.info(f'received: {received}')
                if received in self.supported_commands:
                    self.command_flag = received
                    self.logger.info(f'raising flag for command: {received}')

        return received_count

    def _format_tx_data(self, mode:str, num_payloads:int, data:str):
        '''Formart the data to what the arduino expects for transmissions.

        Return:
            - formatted data to be called with _send_to_arduino
        '''
        mode = mode.upper()
        if mode not in self.supported_modes:
            raise IndexError(f'Using unsupported mode: {mode}, "T", "S", or "R" are expected.')
        
        return mode + ':' + str(num_payloads) + ':' + data

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

    def transmit(self, data:str, mode='T'):
        '''Send a single message.

        Params:
            data: the message to be transmitted to the other radio.
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

        formatted_data = self._format_tx_data(mode, 1, data_string)
        try:
            self._send_to_arduino(formatted_data)
        except Exception as e:
            self.logger.error(f'failed to transmit: {formatted_data}')
            raise e

        return data_string_len