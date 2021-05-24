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


DEFAULT_MODE = False
MODE_OFF = 0
MODE_ON = 1
DEFAULT_SPEED = 0
DEFAULT_ANGLE = 0

BTN_REQUEST_VALIDATE = "validate"
BTN_REQUEST_STOP = "stop"
BTN_REQUEST_DISCONNECT = "disconnect"

FRONT_PI_IP = "192.168.50.240"
RIGHT_PI_IP = "192.168.50.XX"
BACK_PI_IP = "192.168.50.XX"
LEFT_PI_IP = "192.168.50.XX"

SENSOR_BRIGHTPI = "bright-pi"
SENSOR_CAMERA = "camera"
SENSOR_FLYINGFISH = "flying-fish"


def get_grounded_state(self):
    """Will stop the motors if the ground isn't detected anymore"""
    car = CarController()
    if GPIO.input(23):
        car.stop_moving()


rows = []


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
    plt.title("Lidar : ")
    plt.subplot(projection="polar")
    plt.scatter(data_x, data_y, s=area, c=data_y, cmap=cmap)
    plt.pause(time_redraw)
    plt.ylim(0, 2000)
    plt.savefig("static/test.png")
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

app = Flask(__name__)


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
    output = "Tentative de connexion à l'appareil"
    car = CarController()
    if car != None:
        if car.connection != None:
            output = "Tentative de connexion à l'appareil {0} réussie".format(
                car.MY_MOVEHUB_ADD
            )
    return render_template("connection.html", msg=output)


@app.route("/create_car/")
def create_car():
    """Used to the creation of the car"""
    car = None
    while car == None:
        car = CarController()
    if car != None:
        print(type(car.connection) is GattConnection)
        if car.connection != None:
            return render_template("form_remote_car.html")


@app.route("/close_connection/")
def close_connection():
    """Close the connection between the Raspberry Pi and the Technic Hub"""
    output = "Connexion toujours en cours"
    car = CarController()
    if car.connection != None:
        car.disconnect()
        car.instance = None
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
    automatic_mode = MODE_OFF
    # move_speed = DEFAULT_SPEED
    # angle_rotation = DEFAULT_ANGLE
    # if request.form["cbxMode"] != None:
    #     automatic_mode = request.form["cbxMode"]
    move_speed = request.form["rngMove"]
    angle_rotation = request.form["rngRotationAngle"]
    car = CarController()
    # Reverse the result because it returns True if there isn't a ground below
    grounded = not GPIO.input(23)
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

    # Init
    car = CarController()
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
                    grounded = not GPIO.input(23)
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
            returned_value = redirect("/close_connection")
    return returned_value


@app.route("/error/")
def error(msg):
    return render_template("error.html", msg=msg)


loop = asyncio.new_event_loop()

if __name__ == "__main__":
    Bootstrap(app)
    # Set the mode into Broadcom SOC channel
    # It allows to use GPIO number instead of pin number
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO 23 into input mode
    GPIO.setup(23, GPIO.IN)
    # Add the event
    GPIO.add_event_detect(23, GPIO.RISING, callback=get_grounded_state, bouncetime=100)

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
