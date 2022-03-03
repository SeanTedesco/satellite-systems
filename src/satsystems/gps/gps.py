class Gps:
    '''Interface class to control a GPS.'''

    def __init__(self, **kwargs):
        pass 

    def get_location(self, **kwargs):
        '''Send a message.'''
        raise NotImplementError('Should be implemented by derived class.')


def parse_cmdline():
    pass

def main():
    from .grove import Grove

    #options = parse_cmdline()
    gps = Grove(uid='radio_uid', port='/dev/ttyUSB2', baudrate=115200)
    gps.get_location()
    #options.functions(options, gps)

if __name__ == '__main__':
    main()
