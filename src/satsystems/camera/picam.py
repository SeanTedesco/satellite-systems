from picamera import PiCamera
from time import sleep

class PiCam(PiCamera):
    
    def __init__(self, resolution=(1024, 768)):
        super().__init__()

        self.resolution = resolution

    def shot(self, filename: str):
        output = filename + '.jpg'
        self.start_preview()
        sleep(2)
        self.capture(output)

    def video(self):
        print('PiCam is recording!')
    