from picamera import PiCamera
from time import sleep

# Initialize the camera
camera = PiCamera()

# Start the preview and wait 5 seconds before closing it
camera.start_preview()
sleep(5)
camera.stop_preview()