from .radio import Radio
import logging

class RF24(Radio):
    
    def __init__(self, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(port, baud, start_marker, end_marker)

        self.logger = logging.getLogger(__file)
        self.logger.setLevel(logging.DEBUG)

    def transmit(self, data:str):
        '''Send a message.

        Note:
            The "T" is required as this is what is expected by the arduino MCU.
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

        data_string = 'T' + data_string
        try:
            _send_to_arduino(data_string)
        except Exception as e:
            raise e

        return data_string_len

        

    def receive(self, output_file:str):
        '''Receive a message.'''
        # verify output file 
        
        received = ''
        while received != 'STOP':
            received = _receive_from_arduino()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(entry)
            print(received)

    def command(self, command_code:int):
        '''Send a command/request to the other radio, await for a response.'''

        # verify request code
        # generate matching checksum with request code
        # change request code to str
        # transmit request str
        # receive responses
        # stop receiving when timeout or ending message
        # compare received with expected checksum
        # inform user of success or faiilure  

        print('rf24 commanding...')
        self.transmit(str(command_code))

    def stream(self, filename:str):
        '''Stream data in a file.'''

        print('rf24 streaming...')

    def beacon(self):
        '''Transmit a beacon message.'''

        print('rf24 beaconing...')