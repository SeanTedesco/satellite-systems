import argparse
from ..common.logger import SatelliteLogger
from dataclasses import dataclass

@dataclass
class Deployable:
    '''A helper class used to describe a single deployable system.'''
    uid: str
    arm_pin: int
    fire_pin: int
    deployment_delay: float = 1.0


class Deployer:
    '''Interface class to control deployable systems.'''

    def __init__(self):
        self.deployable_list = []
        self.logger = SatelliteLogger.get_logger('deployer')

    def set_config(self, filename:str):
        pass

    def arm_deployment(self, **kwargs):
        '''Prepare the system for deployment.'''
        raise NotImplementedError('Should be implemented by derived class.')
    
    def fire_deployment(self, **kwargs):
        '''Deploy the provided system.'''
        raise NotImplementedError('Should be implemented by derived class.')


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control deployable systems.')
    subparser = parser.add_subparsers()

    arm_fire_parser = subparser.add_parser('arm-fire', help='Arm and fire the deployer.')
    arm_fire_parser.add_argument('-c', '--config', type=str, help='The configuration file for the deployer system.')
    arm_fire_parser.set_defaults(function=do_arm_fire)

    return parser.parse_args()

def do_arm_fire(ant_dbd, options):

    ant_dbd.set_config(options.config)
    ant_dbd.arm_deployment()
    ant_dbd.fire_deployment()

def main():
    from .ANT_DBD import ANT_DBD

    options = parse_cmdline()
    antennta_deployer = ANT_DBD()
    options.function(antennta_deployer, options)

if __name__ == '__main__':
    main()
