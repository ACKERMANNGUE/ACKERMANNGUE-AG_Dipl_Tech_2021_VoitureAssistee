#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This scrtipt script..

import cv2
from libs.pivideostream import PiVideoStream
import imutils
import time
import numpy as np

class VideoCamera(object):
    def __init__(self, flip = True, fps=15, res=(320, 256)):
        """Initialize the camera"""
        print("cam init")
        self.vs = PiVideoStream(resolution=res, framerate=fps).start()
        time.sleep(0.5)
        if self.vs != None:
            print("cam init done")
        self.flip = flip
        

    def __del__(self):
        """Stop the camera"""
        print("cam del")
        self.vs.stop()

    def flip_if_needed(self, frame):
        """Reverse the camera if specified"""
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        """Get the actual frame"""
        frame = self.flip_if_needed(self.vs.read())
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()
