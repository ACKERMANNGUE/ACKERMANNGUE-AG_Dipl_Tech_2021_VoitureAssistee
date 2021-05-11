from time import sleep
from flask import Flask, request, render_template, Response, redirect
import RPi.GPIO as GPIO
from brightpi import brightpilib
from brightpi.brightpilib import BrightPiSpecialEffects
from camera import VideoCamera
import time
import threading
import os
import cv2
from sensor import Sensor
import json
import constants

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/<sensor>/<state>')
def sensor_control(sensor=None, state=None):
    #print(brightpi_state)
    state = int(state)
    
    global brightpi_state
    global camera_state
    global flyingfish_state
    global light
    
    sensors = []
    if sensor == constants.SENSOR_BRIGHTPI:
        if state == constants.STATE_ON:
            brightpi_state = constants.STATE_ON
        elif state == constants.STATE_OFF:
            brightpi_state = constants.STATE_OFF
        light.set_led_on_off(brightpilib.LED_ALL, brightpi_state)

    if sensor == constants.SENSOR_CAMERA:
        if state == constants.STATE_ON:
            camera_state = constants.STATE_ON
        elif state == constants.STATE_OFF:
            camera_state = constants.STATE_OFF

    if sensor == constants.SENSOR_FLYINGFISH:
        if state == constants.STATE_ON:
            flyingfish_state = constants.STATE_ON
        elif state == constants.STATE_OFF:
            flyingfish_state = constants.STATE_OFF

    sensors.append(Sensor(constants.SENSOR_BRIGHTPI, brightpi_state))
    sensors.append(Sensor(constants.SENSOR_CAMERA, camera_state))
    sensors.append(Sensor(constants.SENSOR_FLYINGFISH, flyingfish_state))

    return convert_array_to_json(sensors)


def convert_array_to_json(array):
    json_string = "["
    for i in range(len(array)):
        if i + 1 < len(array):
            json_string += array[i].convert_to_json() + ","
        else:
            json_string += array[i].convert_to_json() + "]"
    return json_string


def a(self):
    print("a")

@app.route('/stream')
def stream():
    global camera_state
    print(camera_state)
    return render_template('index.html', name=constants.CAMERA_FRONT, mode=camera_state, on=constants.STATE_ON, off=constants.STATE_OFF)

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    global pi_camera
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__': 
    # Set the mode into Broadcom SOC channel
    # It allows to use GPIO number instead of pin number
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO 23 into input mode
    GPIO.setup(23, GPIO.IN)
    # Add the event
    GPIO.add_event_detect(
        23, GPIO.RISING, callback=a, bouncetime=100)

    brightpi_state = constants.STATE_OFF
    camera_state = constants.STATE_OFF
    flyingfish_state = constants.STATE_OFF
    
    light = BrightPiSpecialEffects()
    light.reset()
    pi_camera = VideoCamera()
    
    # Start the server and make it accessible by all user in the network
    app.run(host='0.0.0.0', debug=True)
