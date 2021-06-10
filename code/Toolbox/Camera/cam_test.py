# @file cam_test.py
# @brief Used to test the installation of the camera

# Author : Ackermann Gawen
# Last update : 10.06.2021

from picamera import PiCamera
from time import sleep

# Initialize the camera
camera = PiCamera()

# Start the preview and wait 5 seconds before closing it
camera.start_preview()
sleep(5)
camera.stop_preview()