import sys
from time import sleep
from datetime import datetime
from picamera import PiCamera

class PiCam(PiCamera):
    
    def __init__(self, resolution=(1024, 768), framerate:int=16):
        super().__init__()

        self.resolution = resolution
        self.framerate = framerate

    def shot(self, filename:str='image'):
        time_stamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        output = filename + time_stamp + '.jpg'

        self.start_preview()
        sleep(2)
        self.capture(output)

    def video(self, filename:str='video'):
        time_stamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        output = filename + time_stamp + '.h264'

        self.start_preview()
        self.start_recording(output)
        sleep(5)
        self.stop_recording()
        self.stop_preview()