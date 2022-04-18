from .radio import Radio
from datetime import datetime

class RF24(Radio):
    
    def __init__(self, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(port, baud, start_marker, end_marker)

    def transmit(self, data:str):
        # verify data (limit of 30 characters)
        # prepare data to be sent to radio
        # send to radio

        print('rf24 sending...')
        data_string = 't' + data
        _send_to_arduino(data_string)

    def receive(self, output_file:str):
        # verify output file 
        # 


        print('rf24 receiving...')
        received = ''
        while received != 'STOP':
            received = _receive_from_arduino()
            entry = str(datetime.now()) + ': ' + received + '\n' 
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(entry)
            print(received)

    def command(self, command_code:int):
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
