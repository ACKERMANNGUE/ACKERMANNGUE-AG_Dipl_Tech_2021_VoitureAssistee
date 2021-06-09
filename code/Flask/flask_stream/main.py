from flask import Flask, render_template, Response, request
from camera import VideoCamera
import time
import threading
import os
import cv2

pi_camera = VideoCamera(flip=True) # flip pi camera if upside down.


app = Flask(__name__)

@app.route('/streaming_camera')
def cam_stream():
    """
    Route which display the video feed page
    """
    global camera_state
    return render_template('index.html', name=constants.FRONT_CAM, mode=camera_state, on=constants.STATE_ON, off=constants.STATE_OFF)

def gen(camera):
    """
    Convert the frame into a response in bytes format

    camera : The camera object
    """
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    """Route which returns the video feed of the camera"""
    global pi_camera
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False)
    



