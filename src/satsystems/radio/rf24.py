from .radio import Radio

class RF24(Radio):
    
    def __init__(self, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(port, baud, start_marker, end_marker)

    def send(self):
        print('rf24 sending...')

    def receive(self):
        print('rf24 receiving...')
