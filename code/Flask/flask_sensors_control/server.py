from time import sleep
from flask import Flask, request, render_template, Response, redirect, jsonify, make_response
from flask_cors import CORS
from flask_cors.decorator import cross_origin
import RPi.GPIO as GPIO
import time
import threading
import os
import cv2
from libs.sensor import Sensor
from libs.brightpi import brightpilib
from libs.brightpi.brightpilib import BrightPiSpecialEffects
from libs.camera import VideoCamera
import libs.constants as constants
import json

app = Flask(__name__)
cors = CORS(app, withCredentials = True)

@app.route('/')
def hello_world():
    """Route used to know if the server is on"""
    return 'Hello, World!'


@app.route('/<string:sensor>/<int:state>', methods=['POST', 'OPTIONS'])
@cross_origin()
def sensor_control(sensor=None, state=None):
    """
    Route used to manage the sensors

    sensors : The sensor's name
    state : The sensor's state
    """
    state = int(state)
    
    global brightpi_led_state
    global brightpi_ir_state
    global camera_state
    global light
    
    sensors = []
    # Check the request method
    if request.method == "POST": 
        # Change the state
        if sensor == constants.SENSOR_BRIGHTPI_LED:
            if state == constants.STATE_ON:
                brightpi_led_state = constants.STATE_ON
            elif state == constants.STATE_OFF:
                brightpi_led_state = constants.STATE_OFF
            light.set_led_on_off(brightpilib.LED_WHITE, brightpi_led_state)
        elif sensor == constants.SENSOR_BRIGHTPI_IR:
            if state == constants.STATE_ON:
                brightpi_ir_state = constants.STATE_ON
            elif state == constants.STATE_OFF:
                brightpi_ir_state = constants.STATE_OFF
            light.set_led_on_off(brightpilib.LED_IR, brightpi_ir_state)

        if sensor == constants.SENSOR_CAMERA:
            if state == constants.STATE_ON:
                camera_state = constants.STATE_ON
            elif state == constants.STATE_OFF:
                camera_state = constants.STATE_OFF

    # Add the sensors into the list
    sensors.append(Sensor(constants.SENSOR_BRIGHTPI_LED, brightpi_led_state))
    sensors.append(Sensor(constants.SENSOR_BRIGHTPI_IR, brightpi_ir_state))
    sensors.append(Sensor(constants.SENSOR_CAMERA, camera_state))

    return convert_array_to_json(sensors)


def convert_array_to_json(array):
    """
    Convert an array into a JSON format

    array : The array to convert
    """

    json_string = "["
    for i in range(len(array)):
        if i + 1 < len(array):
            json_string += array[i].convert_to_json() + ","
        else:
            json_string += array[i].convert_to_json() + "]"
    return json_string


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


if __name__ == '__main__':
    brightpi_led_state = constants.STATE_OFF
    brightpi_ir_state = constants.STATE_OFF
    camera_state = constants.STATE_OFF

    pi_camera = VideoCamera() 
    
    light = BrightPiSpecialEffects()
    light.reset()
    
    # Start the server and make it accessible by all user in the network
    app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)
