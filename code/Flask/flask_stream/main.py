from flask import Flask, render_template, Response, request
from camera import VideoCamera
import time
import threading
import os
import cv2

pi_camera = VideoCamera(flip=True) # flip pi camera if upside down.


app = Flask(__name__)

@app.route('/stream/<state>')
def index(state):
    return render_template('index.html', name="Caméra avant", mode=state, on="on", off="off") 
    
def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_down')
def video_feed_down():
    image_binary = read_image("./static/camera_down.png")
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False)
    



