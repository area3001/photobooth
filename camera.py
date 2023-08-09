from picamera2 import Picamera2
from libcamera import Transform, ColorSpace
from os import path
import datetime

import config

camera = Picamera2()
camera.preview_configuration.main.size = config.resolution
camera.preview_configuration.main.format = 'BGR888'
camera.preview_configuration.transform = Transform(hflip=True)
camera.configure("preview")

capture_config = camera.create_still_configuration()
camera.still_configuration.enable_raw()
camera.still_configuration.main.size = camera.sensor_resolution
camera.still_configuration.buffer_count = 2
camera.still_configuration.colour_space = ColorSpace.Sycc()

camera.start()


def take_photo():
    print("capture image")
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
    filename = path.join('./pictures/', filename)
    camera.switch_mode_and_capture_file(capture_config, filename)
    print("display image")
    return filename


def buffer():
    return camera.capture_array().data
