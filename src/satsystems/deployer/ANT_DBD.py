from .deployer import Deployer, Deployable


class ANT_DBD(Deployer):
    
    def __init__(self):
        super().__init__()

    def arm_deployment(self):
        '''Prepare the system for deployment.'''

        self.logger.critical('arming deployment!')
    
    def fire_deployment(self):
        '''Deploy the provided system.'''

        self.logger.critical('firing deployment!')