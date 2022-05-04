from .radio import Radio
import time

class RF24(Radio):

    def __init__(self, name, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(name, port, baud, start_marker, end_marker)

        self.stop_receive = 'STOP'                  # message to stop receiving messages

    def transmit(self, data:str):
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

        formatted_data = self._format_tx_data(data_string)
        try:
            self._send_to_arduino(formatted_data)
        except Exception as e:
            self.radio_logger.warning(f'failed to transmit: {formatted_data}')
            raise e

        return data_string_len

    def receive(self, timeout:int=60):
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
                self.radio_logger.warning('no message received')
                break

        return received

    def command(self, command_code:str):
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
        self.radio_logger.info(f'transmitted command: {command_code}')
        got_back = self.receive()
        if got_back == 'xxx':
            self.radio_logger.info(f'failed to receive acknowledgement')

    def stream(self, filename:str):
        '''Stream data in a file.'''

        print('rf24 streaming...')

    def beacon(self, status:str='healthy', pulse_count:int=10):
        '''Transmit a beacon message.'''

        for i in range(pulse_count):
            self.transmit('VA3TFO')
            time.sleep(1)
            self.transmit(status)
            time.sleep(1)

    def monitor(self, filename:str):
        '''Constantly listen for a signal.'''

        received = 'xxx'
        received_count = 0

        if not filename.strip():
            raise FileNotFoundError('No file specified for output monitoring.')

        while received != self.stop_receive:
            received = self.receive()
            if not (received == 'xxx'):
                received_count += len(received)
                with open(file=filename, mode='a') as f:
                    f.write(received)

        return received_count

    def _format_tx_data(self, data:str):
        '''Formart the data to what the arduino expects for transmissions.

        Return:
            - formatted data to be called with _send_to_arduino
        '''
        return 't' + data