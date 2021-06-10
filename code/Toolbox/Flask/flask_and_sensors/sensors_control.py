# @file sensors_control.py
# @brief Used to test the sensors

# Author : Ackermann Gawen
# Last update : 10.06.2021

from brightpi import *  # Concerne les fichiers relatifs au Bright Pi
# Concerne les classes de Flask à utiliser
from flask import Flask, request, render_template, Response
import time  # Concerne le délai à attendre lors d’instructions
# Concerne la classe nécessaire à la récupération du flux de la caméra
from camera.camera import VideoCamera
import threading  # Concerne les thread (exemple : yield)
import os  # Concerne les éléments relatif à l'os
import subprocess  # Concerne l'exécution de processus


app = Flask(__name__)

# Initialisation of the bright pi
bright_special = BrightPiSpecialEffects()
bright_special.reset()
# Setting up indexes
RIGHT_LEDS = [1, 2]
LEFT_LEDS = [3, 4]

# Initialisation de la caméra
pi_camera = VideoCamera(flip=True)  # retourne la caméra


def blink(repetitions, speed, right_leds, left_leds, side):
    """Make the bright pi leds blink
    
    repetitions : The number of times the blink should appear
    speed : The amount of time a led needs to be activated and disabled. 
            The times is divided by 2, e.g. 1 second will be 0.5 second on and 0.5 off
    right_leds : The indexes of the right leds
    left_leds : The indexes of the left leds
    side : The side we want to make it blinks
    """
    # fait clignoter les leds des côtés spécifiés
    duration = speed / 2
    leds_to_activate = []
    leds_to_desactivate = []
    for i in range(0, repetitions):
        if side == "L":
            leds_to_activate = left_leds
            leds_to_desactivate = right_leds
        if side == "R":
            leds_to_activate = right_leds
            leds_to_desactivate = left_leds

        bright_special.set_led_on_off(leds_to_desactivate, OFF)
        bright_special.set_led_on_off(leds_to_activate, ON)
        time.sleep(duration)
        bright_special.set_led_on_off(leds_to_activate, OFF)
        time.sleep(duration)


@app.route('/blink/<side>')
def blink_brightpi(side):
    """Blinks the bright pi for a specific side
    
    side : Leds' side to blink
    """
    # Clignotant par la route (URL)
    blink(10, 1, RIGHT_LEDS, LEFT_LEDS, side)
    str_output = "La voiture va tourner à "
    if side == "R":
        str_output += "droite"
    else:
        str_output += "gauche"
    return str_output


@app.route('/blink_response', methods=['GET', 'POST'])
def blink_form_response():
    """The form treatement
    """
    # Clignotant par formulaire HTML
    if request.method == 'POST':
        side = request.form["blink_side"]
        blink(10, 1, RIGHT_LEDS, LEFT_LEDS, side)
        str_output = "La voiture va tourner à "
        if side == "R":
            str_output += "droite"
        else:
            str_output += "gauche"
    return str_output


@app.route('/blink_brightpi')
def blink_from():
    """Display the blink form
    """
    # affiche le template form.html
    return render_template("form.html")


@app.route('/stream')
def camera_stream():
    """Display a frame received by the pi camera encoded in MJPEG
    """
    return Response(get_frames(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def get_frames(camera):
    """Get frames in bytes and add them into the content-type
    
    camera : The camera which provides the stream
    """
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\n\n' + frame + b'\n\n')


@app.route('/')
def home():
    """Home root
    """
    return "Bonjour"


@app.route('/lidar')
def activate_lidar():
    """Activate the software of the Lidar on the Raspberry Pi
    """
    os.system("lidar/ultra_simple /dev/ttyUSB0")
    return "radar on ?"

# @app.route('/route_apres_validation', methods=['GET', 'POST'])
# def nom_de_fonction():
#     if request.method == 'POST' and request.form["input_validation"]:
#         valeur = request.form["nom_input_html"]
#         # traitement ...
#     return html_a_afficher
        

if __name__ == '__main__':
    # Lance le serveur et donne l'accès à toutes les personnes sur le réseaux
    app.run(host='0.0.0.0', debug=False)
