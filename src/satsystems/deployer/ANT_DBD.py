from .deployer import Deployer, Deployable
from typing import List


class ANT_DBD(Deployer):
    
    def __init__(self, deployer_name:str='antenna deployer'):
        self.deployer_name = deployer_name
        super().__init__(self.deployer_name)

    def arm_deployment(self):
        '''Prepare the system for deployment.'''

        self.logger.critical('arming deployment!')
    
    def fire_deployment(self, deployables:List[Deployable]):
        '''Deploy the provided system.'''

        self.logger.critical('firing deployment!')
        for deployable in deployables:
            self.logger.debug(f'deploying: {deployable}')

    def detect_deployment(self, deployables:List[Deployable]):
        '''Detect whether the provided systems truly deployed.'''

        self.logger.debug('confirming deployment!')
        for deployable in deployables:
            self.logger.debug(f'detecting: {deployable}')