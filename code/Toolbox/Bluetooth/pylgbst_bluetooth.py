#!/usr/bin/env python3

from pylgbst.hub import MoveHub
from pylgbst.peripherals import Motor, EncodedMotor
from pylgbst import *
from time import sleep
import atexit

MY_MOVEHUB_ADD = "90:84:2B:50:36:43"
MY_BTCTRLR_HCI = "hci0"

MAX_ANGLE = 150

def forward(motor_1, motor_2, motor_3):
    """Set the power to their min negative value in order to make it goes forward
    
    motor_1 : Front motor
    motor_2 : Back motor
    motor_3 : The directionnal motor
    """
    motor_1.start_power(-1)
    motor_2.start_power(-1)
    motor_3.angled(0)
    print("done!")
    
def backward(motor_1, motor_2, motor_3):
    """Set the power to their max positive value in order to make it goes backward
    
    motor_1 : Front motor
    motor_2 : Back motor
    motor_3 : The directionnal motor
    """
    motor_1.start_power(1)
    motor_2.start_power(1)
    motor_3.angled(0)
    print("done!")
    
def go_left(motor):
    """Turn the directionnal motor the his negative min value in order to make it go full left
    
    motor : The directionnal motor
    """
    motor.angled(-MAX_ANGLE)
    print("done!")
    
def go_right(motor):
    """Turn the directionnal motor the his positive max value in order to make it go full right
    
    motor : The directionnal motor
    """
    motor.angled(MAX_ANGLE)
    print("done!")

def stop_moving(motor_1, motor_2):
    """Stop the motors
    
    motor_1 : Front motor
    motor_2 : Back motor
    """
    motor_1.start_power(0)
    motor_2.start_power(0)
    print("done!")

def reset_angle(motor):
    """Reset the angle of the directionnal motor
    
    motor : The directionnal motor
    """
    for degrees in range(MAX_ANGLE):
        motor.angled(degrees=(-degrees))
    sleep(1)
        
    for degrees in range(MAX_ANGLE):
        motor.angled(degrees=(degrees))
    sleep(1)
    print("done!")
    

def play_scenario(movehub):
    """Play a scenario
    
    movehub : The hub where motors are connected to
    """
    
    motor_a = Motor(movehub, movehub.PORT_A)
    motor_b = Motor(movehub, movehub.PORT_B)
    motor_c = EncodedMotor(movehub, movehub.PORT_C)
    
    # motor_c.subscribe(show_angle_value, mode=EncodedMotor.SENSOR_ANGLE)
    
    print("Reset angle:")
    reset_angle(motor_c)
    sleep(2)
    
    print("Forward:")
    forward(motor_a, motor_b, motor_c)
    sleep(1)
    
    print("Backward:")
    backward(motor_a, motor_b, motor_c)
    sleep(1)
    
    print("Stop")
    stop_moving(motor_a, motor_b)
    
    print("Left:")
    go_left(motor_c)
    sleep(2)

    print("Right:")
    go_right(motor_c)
    sleep(2)

def exiting(connection):
    """Close a connection
    
    connection : The connection to close
    """
    print("bye")
    connection.disconnect()
# Create a gatt connection from a device
conn = get_connection_gatt(hub_mac=MY_MOVEHUB_ADD)
# Adding event handler on the exiting
atexit.register(exiting, connection=conn)

try:
    # Initialize the hub with the connection
    movehub = MoveHub(conn)
    play_scenario(movehub)
    exiting(conn)
finally:
    exiting(conn)


