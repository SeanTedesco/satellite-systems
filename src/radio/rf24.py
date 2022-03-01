from .radio import Radio

class RF24(Radio):
    
    def __init__(self, uid, port, baudrate, **kwargs):
        self.uid = uid
        
        super().__init__(port, baudrate, **kwargs)

    def send(self):
        print('rf24 sending...')

    def receive(self):
        print('rf24 receiving...')
