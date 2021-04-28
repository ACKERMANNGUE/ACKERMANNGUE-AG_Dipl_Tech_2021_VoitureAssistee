#!/usr/bin/env python3

from pylgbst.hub import MoveHub
from pylgbst.peripherals import Motor, EncodedMotor
from pylgbst import *
from time import sleep
import atexit

MY_MOVEHUB_ADD = "90:84:2B:50:36:43"
MY_BTCTRLR_HCI = "hci0"

def forward(motor_1, motor_2, motor_3):
    motor_1.start_power(-1)
    motor_2.start_power(-1)
    motor_3.angled(0)
    print("done!")
    
def downward(motor_1, motor_2, motor_3):
    motor_1.start_power(1)
    motor_2.start_power(1)
    motor_3.angled(0)
    print("done!")
    
def go_left(motor_3):
    motor_3.angled(-180)
    print("done!")
    
def go_right(motor_3):
    motor_3.angled(180)
    print("done!")

def stop_moving(motor_1, motor_2):
    motor_1.start_power(0)
    motor_2.start_power(0)
    print("done!")

def reset_angle(motor_3):
    motor_3.angled(degrees=-150)
    print("test 1")
    sleep(1)
    motor_3.angled(degrees=-75)
    print("test 2")
    sleep(1)

def show_angle_value(angle):
    print("Angle: %s" % angle)

def play_scenario(movehub):
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
    
    print("Downward:")
    downward(motor_a, motor_b, motor_c)
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
    print("bye")
    connection.disconnect()

conn = get_connection_gatt(hub_mac=MY_MOVEHUB_ADD)
atexit.register(exiting, connection=conn)

try:
    movehub = MoveHub(conn)
    play_scenario(movehub)
    exiting(conn)
finally:
    exiting(conn)


