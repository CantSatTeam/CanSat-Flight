### Pi Camera Code
### https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4

from picamzero import Camera
import time
import os

### No Pins ###

### Camera Initialization ###

home_dir = os.environ['HOME'] #set the location of your home directory
cam = Camera()

### Main Loop ###

cam.start_preview()
cam.take_photo(f"{home_dir}/Desktop/new_image.jpg") #save the image to your desktop
cam.stop_preview()
