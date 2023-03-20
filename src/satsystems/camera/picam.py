import sys, os, io
from time import sleep
from datetime import datetime
from picamera import PiCamera
import base64
from pathlib import Path
from PIL import Image


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

    def image_to_base64(self, input_file:str):
        output_file = Path(input_file).stem + ".txt"
        output_path = "./data/" + output_file
        with open(input_file, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
        with open(output_path, "wb") as txt_file:
            txt_file.write(b64_string)

    def base64_to_image(self, input_file:str):
        output_file = Path(input_file).stem + ".png"
        output_path = "./data/" + output_file
        with open(input_file, "r") as text_file:
                b64_string = base64.b64decode(text_file.read())
                img = Image.open(io.BytesIO(b64_string))
                img.save(output_path)