### Pi Camera Code
### https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4

from picamzero import Camera
import time
import os
### Camera Initialization ###

home_dir = None
cam = None

def init_camera():
    global home_dir, cam
    home_dir = os.environ['HOME'] # set the location of your home directory
    cam = Camera()

def run_camera():
    global cam
    try:
        cam.take_photo(f"{home_dir}/CanSat-Flight/onboard/pics/new_image.jpg")
    except:
        pass
