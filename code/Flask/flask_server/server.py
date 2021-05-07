
from time import sleep
from flask import Flask, request, render_template, Response, redirect
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from pylgbst.comms.cgatt import GattConnection
from car import CarController
import RPi.GPIO as GPIO


DEFAULT_MODE = False
DEFAULT_SPEED = 0
DEFAULT_ANGLE = 0

BTN_REQUEST_VALIDATE = "validate"
BTN_REQUEST_STOP = "stop"
BTN_REQUEST_DISCONNECT = "disconnect"



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

@app.route("/ui")
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
            return render_template("form.html")


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
    return render_template("form.html", mode=DEFAULT_MODE, speed=DEFAULT_SPEED, angle=DEFAULT_ANGLE)


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
    return render_template("form.html", mode=automatic_mode, speed=move_speed, angle=angle_rotation)


@app.route('/form_response', methods=['POST'])
def form_response():
    """The form's answer processed to execute the different actions below
    """

    # Init
    car = CarController()
    automatic_mode = DEFAULT_MODE
    move_speed = DEFAULT_SPEED
    angle_rotation = DEFAULT_ANGLE

    returned_value = render_template(
        "form.html", mode=automatic_mode, speed=move_speed, angle=angle_rotation)
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
                "form.html", mode=automatic_mode, speed=move_speed, angle=angle_rotation)
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
    GPIO.add_event_detect(23, GPIO.RISING, callback=get_grounded_state, bouncetime=100)

    
    topbar = Navbar(
    View('Accueil', 'home'),
    View('Télécommande', 'control_car'),
    View('Déconnexion', 'close_connection'),
    View('Créer une connexion', 'create_car'),
    )
    
    nav = Nav()    
    nav.register_element('top', topbar)
    nav.init_app(app)
    # Lance le serveur et donne l'accès à toutes les personnes sur le réseaux
    app.run(host='0.0.0.0', debug=True)


