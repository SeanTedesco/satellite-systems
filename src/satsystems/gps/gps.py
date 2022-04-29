import argparse

class Gps:
    '''Interface class to control a GPS.'''

    def __init__(self, **kwargs):
        pass 

    def get_location(self, **kwargs):
        '''Get the current location of the satellite.'''
        raise NotImplementedError('Should be implemented by derived class.')


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control GPS Module.')

    subparser = parser.add_subparsers()

    location_parser = subparser.add_parser('location', help='Get location data.')
    #location_parser.add_argument('-d', '--data', type=str, help='The string of data to be transmitted.')
    location_parser.set_defaults(function=do_location)

    return parser.parse_args()

def do_location(gps, options):
    gps.get_location()

def main():
    from .grove import Grove

    options = parse_cmdline()
    gps = Grove(uid='gps_uid', port='/dev/ttyUSB2', baudrate=115200)
    options.function(gps, options)

if __name__ == '__main__':
    main()
