from .gps import Gps

class Grove(Gps):
    
    def __init__(self, uid, **kwargs):
        self.uid = uid 
        super().__init__(**kwargs)

    def get_location(self):
        print('grove getting location...')
