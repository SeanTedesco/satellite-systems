from ..common.logger import SatelliteLogger
from ..common.mcu import MCU
import argparse
import time

class OBC:
    '''Interface class to control communication between RPi and a MCU.'''

    def __init__(self):
        self.logger = SatelliteLogger.get_logger('obc')

    def get_devices_on_bus(self, **kwargs):
        '''Get all the devices currently active on the i2c bus.'''
        raise NotImplementedError('Should be implemented by derived class.')


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control OBC Module.')
    parser.add_argument('-p', '--port', type=str, help='The port of the communication channel.')
    parser.add_argument('-a', '--address', type=int, help='The port of the communication channel.')
    subparser = parser.add_subparsers()

    utx_parser = subparser.add_parser('uart_tx', help='Transmit over UART.')
    utx_parser.add_argument('-d', '--data', type=str, help='The string of data to be transmitted.')
    utx_parser.set_defaults(function=do_uart_tx)

    urx_parser = subparser.add_parser('uart_rx', help='Receive over UART.')
    urx_parser.add_argument('-d', '--data', type=str, help='The string of data to be transmitted.')
    urx_parser.set_defaults(function=do_uart_rx)

    itx_parser = subparser.add_parser('i2c_tx', help='Transmit over I2C.')
    itx_parser.add_argument('-d', '--data', type=str, help='The string of data to be transmitted.')
    itx_parser.set_defaults(function=do_i2c_tx)

    irx_parser = subparser.add_parser('i2c_rx', help='Receive over I2C.')
    irx_parser.add_argument('-d', '--data', type=str, help='The string of data to be transmitted.')
    irx_parser.set_defaults(function=do_i2c_rx)

    return parser.parse_args()


def do_uart_tx(obc, options):
    obc.send_over_serial(options.data)

def do_uart_rx(obc, options):
    start_time = time.time()
    received = 'xxx'
    while received == 'xxx':
        received = obc.receive_over_serial()
        if time.time() > start_time + 60.0:
            print('no message for 60s')
    print(f'received: {received}')

def do_i2c_tx(obc, options):
    obc.send_over_i2c(options.data)

def do_i2c_rx(obc, options):
    start_time = time.time()
    received = 'xxx'
    while received == 'xxx':
        received = obc.receive_over_i2c()
        if time.time() > start_time + 60.0:
            print('no message for 60s')
    print(f'received: {received}')

def main():
    from ..common.mcu import MCU

    options = parse_cmdline()
    obc = MCU(port=options.port, address=options.address)
    options.function(obc, options)

if __name__ == '__main__':
    main()
