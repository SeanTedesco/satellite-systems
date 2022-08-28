from .gps import Gps
from ..common.logger import SatelliteLogger

class Grove(Gps):
    
    def __init__(self, uid, **kwargs):
        self.uid = uid 
        super().__init__(**kwargs)

        self.gps_logger = SatelliteLogger.get_logger('grove.py')

    def get_location(self):
        '''Get the current location of the satellite.'''
        self.gps_logger.info('called get location')
        self.gps_logger.debug('trying again')
        self.gps_logger.warning("Warning message")
        self.gps_logger.error("Error message")
        self.gps_logger.critical("Critical message")