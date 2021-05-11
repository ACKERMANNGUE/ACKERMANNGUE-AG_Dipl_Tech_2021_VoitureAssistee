#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This scrtipt script..

import cv2
from pivideostream import PiVideoStream
import imutils
import time
import numpy as np

class VideoCamera(object):
    def __init__(self, flip = False, fps=10, res=(160, 128)):
        print("cam init")
        self.vs = PiVideoStream(resolution=res, framerate=fps).start()
        time.sleep(10.0)
        if self.vs != None:
            print("cam init done")
        self.flip = flip
        

    def __del__(self):
        print("cam del")
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        ret, png = cv2.imencode('.png', frame)
        return png.tobytes()
