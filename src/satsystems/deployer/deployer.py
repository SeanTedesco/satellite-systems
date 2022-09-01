import argparse
from ..common.logger import SatelliteLogger
from dataclasses import dataclass
from abc import ABC, abstractmethod
import yaml


@dataclass
class Deployable:
    '''A helper class used to describe a single deployable system.'''
    uid: int
    type: str
    arm_pin: int
    fire_pin: int
    detect_pin: int
    deployment_delay: float
    armed: bool = False


class Deployer(ABC):
    '''Interface class to control deployable systems.

    Upon initialization, the Deployer does not know of any systems
    that are required to be deployed. Users are required to pass in
    a configuration file that specifies what the deployable looks
    like.
    '''

    def __init__(self, deployer_name:str='deployer'):
        self.deployable_list = []
        self.logger = SatelliteLogger.get_logger(deployer_name)

    def set_deployables(self, filename:str):
        '''Specifify the deployables to be used by the Deployer.

        Params:
            - path to a .yaml configuration file. Entries must include:
                name:
                    uid: int
                    type: str
                    arm pin: int
                    fire pin: int
                    delay: float (seconds)

        Return:
            - None

        Raises:
            - YAMLError: if there is an issue with the config file.
        '''
        with open(filename, "r") as stream:
            try:
                configs = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                raise exc

            for config in configs.values():
                deployable = Deployable(
                    config.get('uid'),
                    config.get('type'),
                    config.get('arm pin'),
                    config.get('fire pin'),
                    config.get('detect pin'),
                    config.get('delay'),
                )
                self.deployable_list.append(deployable)

    @abstractmethod
    def arm_deployment(self):
        '''Prepare the system for deployment.'''
        pass

    @abstractmethod
    def fire_deployment(self, deployables:list[Deployable]):
        '''Deploy the provided system.'''
        pass

    @abstractmethod
    def detect_deployment(self, deployables:list[Deployable]):
        '''Detect whether the provided systems truly deployed.'''
        pass


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control deployable systems.')
    parser.add_argument('-c', '--config', type=str, help='The configuration file for the deployer system.')
    subparser = parser.add_subparsers()

    deploy_parser = subparser.add_parser('deploy', help='Arm and fire the antennas.')
    deploy_parser.set_defaults(function=do_deploy)

    detect_parser = subparser.add_parser('detect', help='Detect if antennas are in deployed state.')
    detect_parser.set_defaults(function=do_detect)

    return parser.parse_args()

def do_deploy(ant_dbd:Deployer, options):

    ant_dbd.set_deployables(options.config)
    ant_dbd.arm_deployment()
    ant_dbd.fire_deployment(ant_dbd.deployable_list)

def do_detect(ant_dbd:Deployer, options):

    ant_dbd.set_deployables(options.config)
    ant_dbd.detect_deployment(ant_dbd.deployable_list)

def main():
    from .ant_dbd import ANT_DBD

    options = parse_cmdline()
    antennta_deployer = ANT_DBD()
    options.function(antennta_deployer, options)

if __name__ == '__main__':
    main()
