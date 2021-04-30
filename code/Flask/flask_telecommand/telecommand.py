
from time import sleep
from flask import Flask, request, render_template, Response
from car import CarController 

DEFAULT_MODE = False
DEFAULT_SPEED = 0
DEFAULT_ANGLE = 0

car = None

app = Flask(__name__)

@app.route('/')
def hello():
    return "Bonjour à vous"


@app.route('/create_car')
def create_car():
    car = CarController()
    
    return car.MY_MOVEHUB_ADD

@app.route('/close_connection')
def close_connection():
    output = "Connexion toujours en cours"
    car = CarController()
    if car.connection != None:
        car.connection.disconnect()
        output = "Connexion fermée"
    return output


@app.route('/control_car')
def control_car():
    return render_template("form.html", mode = DEFAULT_MODE, speed = DEFAULT_SPEED, angle = DEFAULT_ANGLE)

@app.route('/form_response', methods=['POST'])
def form_response():
    car = CarController()
    automatic_mode = DEFAULT_MODE
    move_speed = DEFAULT_SPEED
    angle_rotation = DEFAULT_ANGLE
    if request.method == 'POST':
        if request.form["send_request"] == "validate":
            automatic_mode = request.form.get("cbxMode")
            if request.form.get("cbxMode") != None:
                automatic_mode = True
            move_speed = request.form["rngMove"]
            angle_rotation = request.form["rngRotationAngle"]
            if car != None :
                car.move(float(move_speed), int(angle_rotation))
        elif request.form["send_request"] == "stop":
            if car != None :
                car.stop_moving()
    return render_template("form.html", mode = automatic_mode, speed = move_speed, angle = angle_rotation)
            

if __name__ == '__main__':
    # Lance le serveur et donne l'accès à toutes les personnes sur le réseaux
    app.run(host='0.0.0.0', debug=True)

