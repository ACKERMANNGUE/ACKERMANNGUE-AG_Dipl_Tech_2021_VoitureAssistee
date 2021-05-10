from time import sleep
from flask import Flask, request, render_template, Response, redirect
import RPi.GPIO as GPIO
from brightpi import brightpilib
from brightpi.brightpilib import BrightPiSpecialEffects
from camera.camera import VideoCamera
import time
import threading
import os
import cv2

app = Flask(__name__)

SENSOR_BRIGHTPI = 0
SENSOR_CAMERA = 1
SENSOR_FLYINGFISH = 2

STATE_ON = 0
STATE_OFF = 1

light = BrightPiSpecialEffects()
light.reset()
pi_camera = VideoCamera(flip=True) # flip pi camera if upside down.

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/<sensor>/<state>')
def sensor_control(sensor=None, state=None):
    if sensor == SENSOR_BRIGHTPI:
        led_state = brightpilib.OFF
        if state == STATE_ON:
            led_state = brightpilib.ON    
        light.set_led_on_off(brightpilib.LED_ALL, led_state)
    if sensor == SENSOR_CAMERA:
        camera_state = STATE_OFF
        if state == STATE_ON:
            if pi_camera == None:
                pi_camera = VideoCamera(flip=True) # flip pi camera if upside down.
                camera_state = STATE_ON
        else:
            pi_camera = None
            camera_state = STATE_OFF
    if sensor == SENSOR_FLYINGFISH:
        if state == STATE_ON:
            a = 2
            
    return 'Hello, World!'


def a():
    print("a")


def b():
    print("b")

@app.route('/stream/<state>')
def index(state):
    return render_template('index.html', name="Caméra avant", mode=state) 
    
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
    # Set the mode into Broadcom SOC channel
    # It allows to use GPIO number instead of pin number
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO 23 into input mode
    GPIO.setup(23, GPIO.IN)
    # Add the event
    GPIO.add_event_detect(
        23, GPIO.RISING, callback=a, bouncetime=100)
    GPIO.add_event_detect(
        23, GPIO.FALLING, callback=b, bouncetime=100)

    
    # Start the server and make it accessible by all user in the network
    app.run(host='0.0.0.0', debug=True)