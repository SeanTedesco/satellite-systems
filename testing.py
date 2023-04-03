import os
from smbus2 import SMBus
import platform
import time

def main():
    my_os = platform.system()
    print("OS in my system : ",my_os)
 
    with SMBus(1) as bus:
        b = bus.read_i2c_block_data(0x08, 0x00, 4)
        print(b)
        time.sleep(2)
        bus.write_i2c_block_data(0x08, 0x00, [0x05, 0x06, 0x07, 0x08])

if __name__ == '__main__':
    main()
