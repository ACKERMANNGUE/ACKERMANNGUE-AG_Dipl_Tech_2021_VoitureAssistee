
from time import sleep
from brightpi import brightpilib
from brightpi.brightpilib import BrightPiSpecialEffects
from flask import Flask, request, render_template, Response, redirect
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from pylgbst.comms.cgatt import GattConnection
from car import CarController
import RPi.GPIO as GPIO
import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory


DEFAULT_MODE = False
DEFAULT_CHECKBOX_VALUE = False
DEFAULT_SPEED = 0
DEFAULT_ANGLE = 0

BTN_REQUEST_VALIDATE = "validate"
BTN_REQUEST_STOP = "stop"
BTN_REQUEST_DISCONNECT = "disconnect"

factory_front = PiGPIOFactory(host='192.168.50.240')

def get_grounded_state(self):
    """Will stop the motors if the ground isn't detected anymore
    """
    car = CarController()
    if GPIO.input(23):
        car.stop_moving()


app = Flask(__name__)


@app.route('/')
def hello():
    """Route used to know if the server is on
    """
    return render_template("home.html")


@app.route("/dashboard")
def user_interface():
    """Route used to show the User Interface
    """

    return render_template("ui.html")


@app.route('/home')
def home():
    """Route used to know if the server is on
    """
    return render_template("home.html")


@app.route('/create_car_test')
def create_car_test():
    """Used to test the creation of the car
    """
    output = "Tentative de connexion à l'appareil"
    car = CarController()
    if car != None:
        if car.connection != None:
            output = 'Tentative de connexion à l\'appareil {0} réussie'.format(
                car.MY_MOVEHUB_ADD)
    return render_template("connection.html", msg=output)


@app.route('/create_car')
def create_car():
    """Used to the creation of the car
    """
    car = None
    while car == None:
        car = CarController()
    if car != None:
        print(type(car.connection) is GattConnection)
        if car.connection != None:
            return render_template("form_remote_car.html")


@app.route('/close_connection')
def close_connection():
    """Close the connection between the Raspberry Pi and the Technic Hub
    """
    output = "Connexion toujours en cours"
    car = CarController()
    if car.connection != None:
        car.disconnect()
        car.instance = None
        output = "Connexion fermée avec l'appareil {0}".format(
            car.MY_MOVEHUB_ADD)
    return render_template("connection.html", msg=output)


@app.route('/control_car')
def control_car():
    """Render the form which allows to control the car
    """
    return render_template("form_remote_car.html", mode=DEFAULT_MODE, speed=DEFAULT_SPEED, angle=DEFAULT_ANGLE)


@app.route('/bg_processing', methods=['POST'])
def bg_process():
    """Process the values passed by Javascript
    """
    automatic_mode = DEFAULT_MODE
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
    return render_template("form_remote_car.html", mode=automatic_mode, speed=move_speed, angle=angle_rotation)


@app.route('/form_dashboard_response', methods=['POST'])
def form_dashboard_response():
    """The form's answer of the dashboard
    """
    if request.method == 'POST':
        # Init
        light_front = DEFAULT_CHECKBOX_VALUE
        camera_front = DEFAULT_CHECKBOX_VALUE
        ground_detection_front = DEFAULT_CHECKBOX_VALUE
        light_right = DEFAULT_CHECKBOX_VALUE
        camera_right = DEFAULT_CHECKBOX_VALUE
        ground_detection_right = DEFAULT_CHECKBOX_VALUE
        light_back = DEFAULT_CHECKBOX_VALUE
        camera_back = DEFAULT_CHECKBOX_VALUE
        ground_detection_back = DEFAULT_CHECKBOX_VALUE
        light_left = DEFAULT_CHECKBOX_VALUE
        camera_left = DEFAULT_CHECKBOX_VALUE
        ground_detection_left = DEFAULT_CHECKBOX_VALUE
        lidar = DEFAULT_CHECKBOX_VALUE

        if request.form["send_request"] == BTN_REQUEST_VALIDATE:
            # front
            if request.form.getlist("cbxLightFront") != None:
                light_front = request.form.getlist("cbxLightFront")
            if request.form.getlist("cbxCameraFront") != None:
                camera_front = request.form.getlist("cbxCameraFront")
            if request.form.getlist("cbxGroundDetectionFront") != None:
                ground_detection_front = request.form.getlist("cbxGroundDetectionFront")

            # right
            if request.form.getlist("cbxLightRight") != None:
                light_right = request.form.getlist("cbxLightRight")
            if request.form.getlist("cbxCameraRight") != None:
                camera_right = request.form.getlist("cbxCameraRight")
            if request.form.getlist("cbxGroundDetectionRight") != None:
                ground_detection_right = request.form.getlist("cbxGroundDetectionRight")
            # back
            if request.form.getlist("cbxLightBack") != None:
                light_back = request.form.getlist("cbxLightBack")
            if request.form.getlist("cbxCameraBack") != None:
                camera_back = request.form.getlist("cbxCameraBack")
            if request.form.getlist("cbxGroundDetectionBack") != None:
                ground_detection_back = request.form.getlist("cbxGroundDetectionBack")
            # left
            if request.form.getlist("cbxLightLeft") != None:
                light_left = request.form.getlist("cbxLightLeft")
            if request.form.getlist("cbxCameraLeft") != None:
                camera_left = request.form.getlist("cbxCameraLeft")
            if request.form.getlist("cbxGroundDetectionLeft") != None:
                ground_detection_left = request.form.getlist("cbxGroundDetectionLeft")
            # lidar
            lidar = request.form.getlist("cbxScanner")
    return render_template("ui.html")
    


@app.route('/form_remote_response', methods=['POST'])
def form_remote_response():
    """The form's answer of the remote 
    """

    # Init
    car = CarController()
    automatic_mode = DEFAULT_MODE
    move_speed = DEFAULT_SPEED
    angle_rotation = DEFAULT_ANGLE

    returned_value = render_template(
        "form_remote_car.html", mode=automatic_mode, speed=move_speed, angle=angle_rotation)
    error = render_template(
        "error.html", msg="Une connexion est nécessaire pour pouvoir intéragir avec")
    if request.method == 'POST':
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
                "form_remote_car.html", mode=automatic_mode, speed=move_speed, angle=angle_rotation)
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


@app.route("/error")
def error(msg):
    return render_template("error.html", msg=msg)


if __name__ == '__main__':
    Bootstrap(app)
    # Set the mode into Broadcom SOC channel
    # It allows to use GPIO number instead of pin number
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO 23 into input mode
    GPIO.setup(23, GPIO.IN)
    # Add the event
    GPIO.add_event_detect(
        23, GPIO.RISING, callback=get_grounded_state, bouncetime=100)

    topbar = Navbar(
        View('Accueil', 'home'),
        View('Télécommande', 'control_car'),
        View('Déconnexion', 'close_connection'),
        View('Créer une connexion', 'create_car'),
        View('Tableau de bord', 'user_interface'),
    )

    nav = Nav()
    nav.register_element('top', topbar)
    nav.init_app(app)
    # Start the server and make it accessible by all user in the network
    app.run(host='0.0.0.0', debug=True)
