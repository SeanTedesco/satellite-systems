from .deployer import Deployer, Deployable
from typing import List
import time
from gpiozero import LED

class ANT_DBD(Deployer):
    
    def __init__(self, deployer_name:str='antenna deployer'):
        self.deployer_name = deployer_name
        super().__init__(self.deployer_name)

        self.led_green = LED(22)
        self.led_yellow = LED(23)
        self.led_red = LED(24)

    def arm_deployment(self):
        '''Prepare the system for deployment.'''

        self.logger.critical('arming deployment!')
        self.led_red.on()
        time.sleep(1)
    
    def fire_deployment(self, deployables:List[Deployable]):
        '''Deploy the provided system.'''

        self.logger.critical('firing deployment!')
        self.led_red.off()
        for deployable in deployables:
            self.logger.debug(f'deploying: {deployable}')
            self.led_yellow.on()
            time.sleep(1)
            self.led_yellow.off()
            time.sleep(1)

    def detect_deployment(self, deployables:List[Deployable]):
        '''Detect whether the provided systems truly deployed.'''

        self.logger.debug('confirming deployment!')
        for deployable in deployables:
            self.logger.debug(f'detecting: {deployable}')
