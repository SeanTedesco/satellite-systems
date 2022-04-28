from asyncio.log import logger
from tracemalloc import start
from .radio import Radio
import logging
import time

class RF24(Radio):
    
    def __init__(self, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(port, baud, start_marker, end_marker)

        logging.basicConfig(
            format='%(asctime)s: %(levelname)s: %(message)s',
            filename='output.log',
            level=logging.DEBUG,
            datefmt='%Y/%m/%d %I:%M:%S'
        )
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.DEBUG)
        self.stop_receive = 'STOP'                  # message to stop receiving messages

    def transmit(self, data:str):
        '''Send a message.

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

        formatted_data = self._format_tx_data(data_string)
        try:
            self._send_to_arduino(formatted_data)
        except Exception as e:
            raise e

        return data_string_len

    def receive(self, output_file:str='output.log'):
        '''Receive a message.

        Params:
            output_file: the name of the file to save the received data.
        Return:
            the number of characters received and saved.
        '''

        received = ''
        received_count = 0

        if not output_file.strip():
            raise ValueError('No file specified for output.')

        while received != self.stop_receive:
            received = self._receive_single_message()
            if not (received == "xxx"):
                print(received)
                received_count += len(received)
                self.logger.info(received)

        return received_count

    def command(self, command_code):
        '''Send a command/request to the other radio, await for a response.'''

        # verify request code
        # generate matching checksum with request code
        # change request code to str
        # transmit request str
        # receive responses
        # stop receiving when timeout or ending message
        # compare received with expected checksum
        # inform user of success or faiilure  

        self.transmit(str(command_code))
        got_back = self._receive_single_message()
        logger.info(got_back)

    def stream(self, filename:str):
        '''Stream data in a file.'''

        print('rf24 streaming...')

    def beacon(self):
        '''Transmit a beacon message.'''

        print('rf24 beaconing...')

    def monitor(self):
        '''Constantly listen for a signal.'''

    def _receive_single_message(self, timeout:int=60):
        '''Attempt to receive a message from the arduino.

        Params:
            - Timeout (optional): duration in which to receive a message.
        Raises:
            - TimeoutError: fails if no message is received from the radio.
        Return:
            - the stripped string sent from the arduino over serial.
        '''
        start_time = time.time()
        received = 'xxx'
        while received == 'xxx':
            received = self._receive_from_arduino().strip()
            if time.time() > start_time + timeout:
                raise TimeoutError(f'did not receive message within {timeout}s!')

        return received

    def _format_tx_data(self, data:str):
        '''Formart the data to what the arduino expects for transmissions.

        Return:
            - formatted data to be called with _send_to_arduino
        '''
        return 't' + data