import smbus
import serial
from serial.serialutil import SerialException

class MCU:
    '''Generic class to represent a microcontroller.
    '''

    def __init__(self, port='/dev/ttyS0', address=00, baud=115200, start_marker='<', end_marker='>'):
        try:
            self._serial_port = serial.Serial(port=port, baudrate=baud, timeout=10, rtscts=True)
        except SerialException as e:
            raise e
        self._serial_port.reset_input_buffer()
        self._start_marker = start_marker
        self._end_marker = end_marker
        self._data_buffer = ""
        self._data_started = False
        self._message_complete = False

        self._bus = smbus.SMBus(1)
        self.i2c_address = address
        self.reading_i2c = False


    def receive_over_serial(self):
        while self._serial_port.inWaiting() > 0 and self._message_complete == False:
            x = self._serial_port.read().decode('utf-8')  # decode needed for Python3

            if self._data_started == True:
                if x != self._end_marker:
                    self._data_buffer = self._data_buffer + x
                else:
                    self._data_started = False
                    self._message_complete = True
            elif x == self._start_marker:
                self._data_buffer = ''
                self._data_started = True

        if self._message_complete == True:
            self._message_complete = False
            return self._data_buffer
        else:
            return 'xxx'

    def send_over_serial(self, data:str):

        string_with_markers = self._start_marker
        string_with_markers += data
        string_with_markers += self._end_marker
        self._serial_port.flush()
        try:
            self._serial_port.write(string_with_markers.encode('utf-8'))
        except Exception as e:
            raise e

    def receive_over_i2c(self):
        self.reading_i2c == True
        while self._message_complete == False and self.reading_i2c == True:
            x = self._bus.read_byte_data(self.i2c_address, 1)

            if self._data_started == True:
                if x != self._end_marker:
                    self._data_buffer = self._data_buffer + x
                else:
                    self._data_started = False
                    self._message_complete = True
                    self.reading_i2c == False
            elif x == self._start_marker:
                self._data_buffer = ''
                self._data_started = True

        if self._message_complete == True:
            self._message_complete = False
            return self._data_buffer
        else:
            return 'xxx'

    def send_over_i2c(self, string:str):

        count = 0
        for char in string:
            data = int(ord(char))
            try:
                self._bus.write_byte(self.i2c_address, data)
            except Exception as e:
                raise e
            count += 1
        return count
