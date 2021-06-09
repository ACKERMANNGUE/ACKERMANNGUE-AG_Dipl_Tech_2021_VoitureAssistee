from time import sleep
from flask import Flask, request, render_template, Response, redirect
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from flask_cors import *
from car import CarController
import RPi.GPIO as GPIO
import matplotlib
import matplotlib.pyplot as plt
import threading
import math
import asyncio
from asyncio.subprocess import PIPE
from asyncio import create_subprocess_exec
import cv2
import static.constants as constants

flying_fish_state = [
    constants.FLYING_FISH_STATE_GROUNDED,
    constants.FLYING_FISH_STATE_GROUNDED,
    constants.FLYING_FISH_STATE_GROUNDED,
    constants.FLYING_FISH_STATE_GROUNDED,
]

# Init
size_rows = 360
rows = [0] * size_rows

automatic_mode_state = constants.MODE_OFF

loop = asyncio.new_event_loop()

app = Flask(__name__)

car = None

obstacles_distances_front_left = []
obstacles_distances_front_right = []


def get_grounded_state(self):
    """Will stop the motors if the ground isn't detected anymore"""
    global car
    global flying_fish_state

    for i in range(len(constants.GPIO_FLYING_FISH)):
        for sensor_state in flying_fish_state:
            input_values = not GPIO.input(constants.GPIO_FLYING_FISH[i][0])
            print(input_values)
            if sensor_state != input_values:
                if car != None and (input_values) != True:
                    car.stop_moving()
                # Invert his state
                sensor_state = input_values
        flying_fish_state[i] = sensor_state
    print(flying_fish_state)


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


def make_chart():
    """
    Will process the chart and save it into a png
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
    plt.ylim(0, 2000)
    plt.savefig(constants.CHART_PATH + constants.CHART_NAME)
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


@app.route("/launch_automatic_mode/<int:state>", methods=["POST"])
def launch_automatic_mode(state=None):
    """
    Launch the automatic_mode on another thread

    state : The state of the automatic mode
    """
    global automatic_mode_state
    automatic_mode_state = state
    # Create the thread
    thread = threading.Thread(target=automatic_mode)
    # Launch it
    thread.start()
    return ""


def automatic_mode():
    """Execute the automatic mode"""
    global car
    global rows
    global automatic_mode_state
    global obstacles_distances_front_left
    global obstacles_distances_front_right

    print("=======================")
    print(automatic_mode_state)
    print("=======================")

    while automatic_mode_state == constants.MODE_ON:
        # Used to store the obstacles detected at left and right
        obstacles_distances_front_left = []
        obstacles_distances_front_right = []
        for i in range(len(rows)):
            distance = rows[i]

            if car != None:
                # Verify that the current angle is between 0 and 15, 345 and 360 
                if (
                    i < constants.MAX_ANGLE_OBSTACLE_DETECTION
                    or i > constants.FULL_ANGLE - constants.MAX_ANGLE_OBSTACLE_DETECTION
                ):
                    # Verify if the distance is lower than the max front distance obstacle detection 
                    if (
                        distance < constants.FRONT_DISTANCE_OBSTACLE_DETECTION
                        and distance > 0
                    ):
                        # If the current angle is lower than the max angle
                        # Add it into the left array
                        if i < constants.MAX_ANGLE_OBSTACLE_DETECTION:
                            obstacles_distances_front_left.append(distance)
                        # If the current angle is greater than the max angle inverted (345 to 360)
                        # Add it into the right array
                        if (
                            i
                            > constants.FULL_ANGLE
                            - constants.MAX_ANGLE_OBSTACLE_DETECTION
                        ):
                            obstacles_distances_front_right.append(distance)
                        # Compute the power, more the obstacle is near, more the motors will be powered
                        speed = distance / constants.FRONT_DISTANCE_OBSTACLE_DETECTION
                        print("reculer")
                        car.auto_move(speed)
                # Verify that the current angle is between 165 and 180, 180 and 195 
                elif (
                    i < constants.HALF_ANGLE + constants.MAX_ANGLE_OBSTACLE_DETECTION
                    or i > constants.HALF_ANGLE - constants.MAX_ANGLE_OBSTACLE_DETECTION
                ):
                    # Verify if the distance is lower than the max front distance obstacle detection 
                    if (
                        distance < constants.BACK_DISTANCE_OBSTACLE_DETECTION
                        and distance > 0
                    ):
                        # Compute the power, more the obstacle is near, more the motors will be powered
                        speed = distance / constants.BACK_DISTANCE_OBSTACLE_DETECTION
                        print("avancer")
                        car.auto_move(speed * (-1))
                else:
                    # If nothing, reset the handlebar and stop the motors
                    car.stop_moving()
                    car.reset_handlebar()

                # Select the smallest element
                lowest_dist_left = constants.FRONT_DISTANCE_OBSTACLE_DETECTION
                for i in range(len(obstacles_distances_front_left)):
                    if lowest_dist_left > obstacles_distances_front_left[i]:
                        lowest_dist_left = obstacles_distances_front_left[i]

                
                # Select the smallest element
                lowest_dist_right = constants.FRONT_DISTANCE_OBSTACLE_DETECTION
                for i in range(len(obstacles_distances_front_right)):
                    if lowest_dist_right > obstacles_distances_front_right[i]:
                        lowest_dist_right = obstacles_distances_front_right[i]
                # Check that their values are not the default one
                if (
                    lowest_dist_right != constants.FRONT_DISTANCE_OBSTACLE_DETECTION
                    and lowest_dist_left != constants.FRONT_DISTANCE_OBSTACLE_DETECTION
                ):
                    # If the nearest obstacle is at left, we need to turn to the right
                    if lowest_dist_left < lowest_dist_right:
                        car.turn(car.MIN_ANGLE)
                    # If the nearest obstacle is at right, we need to turn to the left
                    elif lowest_dist_left > lowest_dist_right:
                        car.turn(car.MAX_ANGLE)
                    # Else, just reset the handlebar
                    else:
                        car.reset_handlebar()


def lidar_stream(state=None):
    """
    Convert the graphic into a streamable picture

    state : The state of the radar's stream
    """
    if state == constants.MODE_OFF:
        radar = cv2.imread(constants.CHART_PATH + constants.CHART_DOWN_NAME)
        radar = cv2.imencode(".jpg", radar)[1]
        # convert it to bytes
        radar_bytes = radar.tobytes()
        # async encoding
        yield (
            b"--frame\r\n"
            b"Content-Type: image/png\r\n\r\n" + radar_bytes + b"\r\n\r\n"
        )
    while state == constants.MODE_ON:
        make_chart()
        try:
            # get the picture
            sleep(1)
            radar = cv2.imread(constants.CHART_PATH + constants.CHART_NAME)
            radar = cv2.imencode(".jpg", radar)[1]
            # convert it to bytes
            radar_bytes = radar.tobytes()
            # async encoding
            yield (
                b"--frame\r\n"
                b"Content-Type: image/png\r\n\r\n" + radar_bytes + b"\r\n\r\n"
            )
        except RuntimeError:
            print("error")


@app.route("/video_feed/<int:state>")
def video_feed(state=None):
    """
    The route which display the graphic's stream

    state : The state of the feed
    """
    # prepare the response to send
    return Response(
        lidar_stream(state), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


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
        return render_template(
            "error.html", msg="Une connexion est nécessaire pour pouvoir intéragir avec"
        )


@app.route("/close_connection/")
def close_connection():
    """Close the connection between the Raspberry Pi and the Technic Hub"""
    global car
    output = "Connexion toujours en cours"
    if car != None:
        print("deco")
        output = "Connexion fermée avec l'appareil {0}".format(car.MY_MOVEHUB_ADD)
        car.disconnect()
        car = None

    return render_template("connection.html", msg=output)


@app.route("/control_car")
def control_car():
    """Render the form which allows to control the car"""
    return render_template(
        "form_remote_car.html",
        speed=constants.DEFAULT_SPEED,
        angle=constants.DEFAULT_ANGLE,
    )


@app.route("/bg_processing_car/", methods=["POST"])
def bg_process_car():
    """Process the values passed by Javascript"""

    global car

    move_speed = request.form["rngMove"]
    angle_rotation = request.form["rngRotationAngle"]

    if car != None:
        # Convert the values
        move_speed = float(move_speed)
        angle_rotation = int(angle_rotation)
        # Get the allowed actions of the car
        actions = get_actions_for_car(move_speed)
        car.move(move_speed, angle_rotation, actions)
    return render_template(
        "form_remote_car.html",
        speed=move_speed,
        angle=angle_rotation,
    )


def get_actions_for_car():
    """Process the actions that the car is allowed to do according to the flying-fish"""
    actions = (constants.CODE_TURN_NOTHING, constants.CODE_MOVE_NOTHING)
    # INDEX 0 represent the turn code
    # INDEX 1 represent the move code
    if (
        GPIO.input(constants.GPIO_FLYING_FISH_FRONT_LEFT)
        and GPIO.input(constants.GPIO_FLYING_FISH_FRONT_RIGHT)
        and not GPIO.input(constants.GPIO_FLYING_FISH_BACK_LEFT)
        and not GPIO.input(constants.GPIO_FLYING_FISH_BACK_RIGHT)
    ):
        print("les deux avant")
        actions = (constants.CODE_TURN_NOTHING, constants.CODE_MOVE_BACKWARD)

    elif GPIO.input(constants.GPIO_FLYING_FISH_FRONT_LEFT):
        print("gauche avant")
        actions = (constants.CODE_TURN_RIGHT, constants.CODE_MOVE_NOTHING)

    elif GPIO.input(constants.GPIO_FLYING_FISH_FRONT_RIGHT):
        print("droite avant")
        actions = (constants.CODE_TURN_LEFT, constants.CODE_MOVE_NOTHING)

    elif (
        not GPIO.input(constants.GPIO_FLYING_FISH_FRONT_LEFT)
        and not GPIO.input(constants.GPIO_FLYING_FISH_FRONT_RIGHT)
        and GPIO.input(constants.GPIO_FLYING_FISH_BACK_LEFT)
        and GPIO.input(constants.GPIO_FLYING_FISH_BACK_RIGHT)
    ):
        print("les deux arrière")
        actions = (constants.CODE_TURN_NOTHING, constants.CODE_MOVE_FORWARD)

    elif GPIO.input(constants.GPIO_FLYING_FISH_BACK_LEFT):
        print("gauche arrière")
        actions = (constants.CODE_TURN_RIGHT, constants.CODE_MOVE_FORWARD)

    elif GPIO.input(constants.GPIO_FLYING_FISH_BACK_RIGHT):
        print("droite arrière")
        actions = (constants.CODE_TURN_LEFT, constants.CODE_MOVE_FORWARD)

    return actions


@app.route("/bg_processing_lidar/<string:state>", methods=["POST"])
def bg_process_lidar(state=None):
    """Process the values passed by Javascript"""

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        loop = asyncio.new_event_loop()
    finally:
        loop.run_until_complete(main(state))

    return ""


@app.route("/form_remote_response/", methods=["POST"])
def form_remote_response():
    """The form's answer of the remote"""
    global car
    # Init
    move_speed = constants.DEFAULT_SPEED
    angle_rotation = constants.DEFAULT_ANGLE

    returned_value = render_template(
        "form_remote_car.html",
        speed=move_speed,
        angle=angle_rotation,
    )
    error = render_template(
        "error.html", msg="Une connexion est nécessaire pour pouvoir intéragir avec"
    )
    if request.method == "POST":
        # Validate will send the values to the car
        if request.form["send_request"] == constants.BTN_REQUEST_RESET_ANGLE:
            if car != None:
                car.reset_handlebar()
            else:
                returned_value = error
        elif request.form["send_request"] == constants.BTN_REQUEST_STOP:
            if car != None:
                car.stop_moving()
            else:
                returned_value = error
        elif request.form["send_request"] == constants.BTN_REQUEST_DISCONNECT:
            returned_value = redirect("/close_connection/")
    return returned_value


@app.route("/error/")
def error(msg):
    """
    The error page

    msg : The message to show on the page
    """
    return render_template("error.html", msg=msg)


def initFlyingfish():
    # Set the mode into Broadcom SOC channel
    # It allows to use GPIO number instead of pin number
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO into input mode
    GPIO.setup(constants.GPIO_FLYING_FISH_FRONT_RIGHT, GPIO.IN)
    GPIO.setup(constants.GPIO_FLYING_FISH_FRONT_LEFT, GPIO.IN)
    GPIO.setup(constants.GPIO_FLYING_FISH_BACK_RIGHT, GPIO.IN)
    GPIO.setup(constants.GPIO_FLYING_FISH_BACK_LEFT, GPIO.IN)
    # Add the event
    GPIO.add_event_detect(
        constants.GPIO_FLYING_FISH_FRONT_RIGHT, 
        GPIO.FALLING,
        callback=get_grounded_state,
        bouncetime=constants.GPIO_BOUNCEBACK,
    )
    GPIO.add_event_detect(
        constants.GPIO_FLYING_FISH_FRONT_LEFT,
        GPIO.FALLING,
        callback=get_grounded_state,
        bouncetime=constants.GPIO_BOUNCEBACK,
    )
    GPIO.add_event_detect(
        constants.GPIO_FLYING_FISH_BACK_RIGHT,
        GPIO.FALLING,
        callback=get_grounded_state,
        bouncetime=constants.GPIO_BOUNCEBACK,
    )
    GPIO.add_event_detect(
        constants.GPIO_FLYING_FISH_BACK_LEFT,
        GPIO.FALLING,
        callback=get_grounded_state,
        bouncetime=constants.GPIO_BOUNCEBACK,
    )


if __name__ == "__main__":
    Bootstrap(app)

    initFlyingfish()
    topbar = Navbar(
        View("Accueil", "home"),
        View("Télécommande", "control_car"),
        View("Tableau de bord", "user_interface"),
        View("Créer une connexion", "create_car"),
        View("Déconnexion", "close_connection"),
    )

    asyncio.set_event_loop(loop)
    asyncio.get_child_watcher().attach_loop(loop)
    nav = Nav()
    nav.register_element("top", topbar)
    nav.init_app(app)
    # Start the server and make it accessible by all user in the network
    app.run(host="0.0.0.0", debug=True)
