from time import sleep
from flask import Flask, request, render_template, Response, redirect
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from pylgbst.comms.cgatt import GattConnection
from car import CarController
import RPi.GPIO as GPIO
import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory
import subprocess
from subprocess import Popen
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import math
import sys
import asyncio
from asyncio.subprocess import PIPE
from asyncio import create_subprocess_exec
import cv2
from PIL import Image
import datetime


DEFAULT_MODE = False
MODE_OFF = 0
MODE_ON = 1
DEFAULT_SPEED = 0
DEFAULT_ANGLE = 0

BTN_REQUEST_VALIDATE = "validate"
BTN_REQUEST_STOP = "stop"
BTN_REQUEST_DISCONNECT = "disconnect"

FRONT_PI_IP = "192.168.50.133"
RIGHT_PI_IP = "192.168.50.XX"
BACK_PI_IP = "192.168.50.XX"
LEFT_PI_IP = "192.168.50.XX"

SENSOR_BRIGHTPI = "bright-pi"
SENSOR_CAMERA = "camera"
SENSOR_FLYINGFISH = "flying-fish"

CHART_PATH = "static/img/"
CHART_NAME = "chart.jpg"

GPIO_FLYING_FISH_FRONT_RIGHT = 17
NAME_FLYING_FISH_FRONT_RIGHT = "Détecteur avant droit"
GPIO_FLYING_FISH_FRONT_LEFT = 23
NAME_FLYING_FISH_FRONT_LEFT = "Détecteur avant gauche"


GPIO_FLYING_FISH = [
    (GPIO_FLYING_FISH_FRONT_LEFT, NAME_FLYING_FISH_FRONT_LEFT),
    (GPIO_FLYING_FISH_FRONT_RIGHT, NAME_FLYING_FISH_FRONT_RIGHT)
    ]


def get_grounded_state(self):
    """Will stop the motors if the ground isn't detected anymore"""
    global car
    for sensor_gpio, sensor_name in GPIO_FLYING_FISH:
        if self == sensor_gpio:
            if car != None:
                car.stop_moving()
            print(datetime.datetime.now())
            print(sensor_gpio)
            print(sensor_name)
            break
    


def get_radar_data(row):
    """
    Will parse the data received in text by the Lidar

    row : Row to read and to add or modify in the array of angles
    """
    global rows
    # row normaly is like [angle, distance]
    tmp = row
    if len(tmp) == 2:
        angle = int(tmp[0])
        # remove the line return
        dist = tmp[1].replace(b"\n", b"")
        rows[angle] = float(dist)
    # 360 values but it begins at 0
    if angle == 359:
        make_chart(0.05)


def make_chart(time_redraw):
    """
    Will process the chart and save it into a png


    time_redraw : The time to wait before "refreshing" the picture
    """
    global rows
    area = 5
    colors = [(1, 0.2, 0.3), (1, 0.8, 0), (0.1, 0.5, 0.1)]  # near -> mid -> far
    cmap_name = "distance_warning"
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(cmap_name, colors)
    data_x = []
    data_y = []
    angle = 0
    # Create the colors I need, values between 0 and 1 for (r, g, b)
    # add angle in radian and his value in two array x and y
    for distance in rows:
        data_x.append(math.radians(angle))
        data_y.append(distance)
        angle += 1

    # set the projection to polar
    plt.subplot(projection="polar")
    plt.scatter(data_x, data_y, s=area, c=data_y, cmap=cmap)
    plt.pause(time_redraw)
    plt.ylim(0, 2000)
    plt.savefig(CHART_PATH + CHART_NAME)
    Image.open(CHART_PATH + CHART_NAME).save(CHART_PATH + CHART_NAME, "JPEG")
    time.sleep(time_redraw)
    plt.clf()


async def _read_stream(stream, callback):
    """
    Will read the text in the console from the process simple_grabber

    stream : The streaming of the data in the console
    callback : The method to call when data has been received

    """
    while True:
        line = await stream.readline()
        if line:
            callback(line.split(b","))
        else:
            break


async def run(should_scan):
    """
    Will run the subprocess and bind the async method

    should_scan : The code to know if the program should scan or not
    """
    command = ("./scanner/simple_grabber /dev/ttyUSB0 " + should_scan).split()
    process = await create_subprocess_exec(*command, stdout=PIPE, stderr=PIPE)
    await asyncio.wait([_read_stream(process.stdout, lambda x: {get_radar_data(x)})])
    await process.wait()


async def main(should_scan):
    """
    The main function which calls the run loop async

    should_scan : The code to know if the program should scan or not
    """
    await run(should_scan)


# Init
size_rows = 360
rows = [0] * size_rows

loop = asyncio.new_event_loop()

app = Flask(__name__)

car = None


def lidar_stream(state=None):
    
    while state == MODE_ON:
        try:
            # get the picture
            radar = cv2.imread(CHART_PATH + CHART_NAME)
            radar = cv2.imencode(".jpg", radar)[1]
            # convert it to bytes
            radar_bytes = radar.tobytes()
            # async encoding
            yield (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + radar_bytes + b'\r\n\r\n')
        except RuntimeError:
            print("error")
            
        
@app.route("/video_feed/<int:state>")
def video_feed(state=None):
    # prepare the response to send
    return Response(lidar_stream(state), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/")
def hello():
    """Route used to know if the server is on"""
    return render_template("home.html")


@app.route("/dashboard/")
def user_interface():
    """Route used to show the User Interface"""

    return render_template("ui.html")


@app.route("/home/")
def home():
    """Route used to know if the server is on"""
    return render_template("home.html")


@app.route("/create_car_test/")
def create_car_test():
    """Used to test the creation of the car"""
    global car
    car = CarController()

    output = "Tentative de connexion à l'appareil"
    if car != None:
        if car.connection != None:
            output = "Tentative de connexion à l'appareil {0} réussie".format(
                car.MY_MOVEHUB_ADD
            )
    return render_template("connection.html", msg=output)


@app.route("/create_car/")
def create_car():
    """Used to the creation of the car"""
    global car
    car = CarController()
    print(car)
    if hasattr(car, "connection"):
        return render_template("form_remote_car.html")
    else:
        car = None
        return render_template("error.html", msg="Une connexion est nécessaire pour pouvoir intéragir avec")


@app.route("/close_connection/")
def close_connection():
    """Close the connection between the Raspberry Pi and the Technic Hub"""
    global car
    output = "Connexion toujours en cours"
    if car != None:
        if car.connection != None:
            car.disconnect()
            output = "Connexion fermée avec l'appareil {0}".format(car.MY_MOVEHUB_ADD)
                
    return render_template("connection.html", msg=output)


@app.route("/control_car")
def control_car():
    """Render the form which allows to control the car"""
    return render_template(
        "form_remote_car.html",
        mode=DEFAULT_MODE,
        speed=DEFAULT_SPEED,
        angle=DEFAULT_ANGLE,
    )


@app.route("/bg_processing_car/", methods=["POST"])
def bg_process_car():
    """Process the values passed by Javascript"""

    global car

    automatic_mode = MODE_OFF
    move_speed = request.form["rngMove"]
    angle_rotation = request.form["rngRotationAngle"]
    grounded = True

    for sensor_gpio, sensor_name in GPIO_FLYING_FISH:
        # Will change the value only if there isn't a ground below
        if GPIO.input(sensor_gpio):
            grounded = False
    if not car == None:
        car.move(float(move_speed), int(angle_rotation), grounded)
    return render_template(
        "form_remote_car.html",
        mode=automatic_mode,
        speed=move_speed,
        angle=angle_rotation,
    )


@app.route("/bg_processing_lidar/<string:state>", methods=["POST"])
def bg_process_lidar(state=None):
    """Process the values passed by Javascript"""

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(main(state))

    return ""


@app.route("/form_remote_response/", methods=["POST"])
def form_remote_response():
    """The form's answer of the remote"""
    global car
    # Init
    automatic_mode = DEFAULT_MODE
    move_speed = DEFAULT_SPEED
    angle_rotation = DEFAULT_ANGLE

    returned_value = render_template(
        "form_remote_car.html",
        mode=automatic_mode,
        speed=move_speed,
        angle=angle_rotation,
    )
    error = render_template(
        "error.html", msg="Une connexion est nécessaire pour pouvoir intéragir avec"
    )
    if request.method == "POST":
        # Validate will send the values to the car
        if request.form["send_request"] == BTN_REQUEST_VALIDATE:
            automatic_mode = request.form.get("cbxMode")
            # form.get return a list of values and None if the checkbox isn't checked
            if request.form.get("cbxMode") != None:
                automatic_mode = True
            move_speed = request.form["rngMove"]
            angle_rotation = request.form["rngRotationAngle"]
            # Updates of the inputed values
            returned_value = render_template(
                "form_remote_car.html",
                mode=automatic_mode,
                speed=move_speed,
                angle=angle_rotation,
            )
            if car != None:
                if type(car.connection) is GattConnection:
                    # Convert them into float values because the range are int between negative and positive 100
                    # and the method which activate the motors is a range between negative and positive 1
                    # so in the move methods I divide the input values by 100
                    # Reverse the result because it returns True if there isn't a ground below
                    grounded = not GPIO.input(GPIO_FLYING_FISH_FRONT_RIGHT)
                    car.move(float(move_speed), int(angle_rotation), grounded)
                else:
                    returned_value = error
        elif request.form["send_request"] == BTN_REQUEST_STOP:
            if car != None:
                if car.connection != None:
                    car.stop_moving()
                else:
                    returned_value = error
        elif request.form["send_request"] == BTN_REQUEST_DISCONNECT:
            returned_value = redirect("/close_connection/")
    return returned_value


@app.route("/error/")
def error(msg):
    return render_template("error.html", msg=msg)


if __name__ == "__main__":
    Bootstrap(app)
    # Set the mode into Broadcom SOC channel
    # It allows to use GPIO number instead of pin number
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO into input mode
    GPIO.setup(GPIO_FLYING_FISH_FRONT_RIGHT, GPIO.IN)
    GPIO.setup(GPIO_FLYING_FISH_FRONT_LEFT, GPIO.IN)
    # Add the event
    GPIO.add_event_detect(GPIO_FLYING_FISH_FRONT_RIGHT, GPIO.FALLING, callback=get_grounded_state, bouncetime=2000)
    GPIO.add_event_detect(GPIO_FLYING_FISH_FRONT_LEFT, GPIO.FALLING, callback=get_grounded_state, bouncetime=2000)

    topbar = Navbar(
        View("Accueil", "home"),
        View("Télécommande", "control_car"),
        View("Déconnexion", "close_connection"),
        View("Créer une connexion", "create_car"),
        View("Tableau de bord", "user_interface"),
    )

    asyncio.set_event_loop(loop)
    asyncio.get_child_watcher().attach_loop(loop)
    nav = Nav()
    nav.register_element("top", topbar)
    nav.init_app(app)
    # Start the server and make it accessible by all user in the network
    app.run(host="0.0.0.0", debug=True)
