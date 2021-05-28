from pylgbst.comms.cgatt import GattConnection
from pylgbst.hub import MoveHub
from pylgbst.peripherals import Motor, EncodedMotor
from pylgbst import *
import time
import os


class CarController:
    """Class controlling the car"""

    MY_MOVEHUB_ADD = "90:84:2B:50:36:43"
    MY_BTCTRLR_HCI = "hci0"
    MAX_ANGLE = 120
    DEFAULT_ANGLE = 0
    MAX_MOTOR_POWER = 1
    MOTOR_STOP_POWER = 0

    def __init__(cls):
        cls.connection = get_connection_gatt(hub_mac=cls.MY_MOVEHUB_ADD)
        try:
            # The motors
            cls.movehub = MoveHub(cls.connection)
            cls.front_motor = Motor(cls.movehub, cls.movehub.PORT_A)
            cls.back_motor = Motor(cls.movehub, cls.movehub.PORT_B)
            cls.directionnal_motor = EncodedMotor(cls.movehub, cls.movehub.PORT_C)
            cls.old_angle = cls.DEFAULT_ANGLE
        except:
            cls.movehub = None
            cls.front_motor = None
            cls.back_motor = None
            cls.directionnal_motor = None
            cls.instance = None
            cls.connection = None
            cls.old_angle = None

    def __del__(cls):
        cls.disconnect()
        print("disconnection")

    def move(self, motor_speed, angle_rotation, grounded):
        """Moves the car with a specific speed and rotation

        motor_speed : The motor's speed
                      NOTE : to move forward, the value must be reversed because it is basically negative
        angle_rotation : The rotation of the directionnal motor
        grounded : True if there is the ground below,
                   False if there isn't
        """
        # Invert the power direction
        motor_speed *= -1
        # Max value of motor is -1 and +1 but in the HTML form, the range input can be set between -100 to +100
        motor_speed /= 100
        if grounded:
            self.front_motor.start_power(motor_speed)
            self.back_motor.start_power(motor_speed)
        self.turn(angle_rotation)
        time.sleep(0.5)

    def turn(self, angle):
        """Turn the directionnal motor from the input value

        angle : The angle we wants the directionnal motor goes to
        """

        # Reset the angle
        self.directionnal_motor.start_power(angle + (-1) * self.old_angle)
        self.old_angle = angle

    def stop_moving(self):
        """Stop the motors"""
        self.front_motor.start_power(self.MOTOR_STOP_POWER)
        self.back_motor.start_power(self.MOTOR_STOP_POWER)

    def disconnect(self):
        self.connection.disconnect()
        print("stopping bluetooth")
        os.system("sudo systemctl stop bluetooth.service")
        time.sleep(0.5)
        print("starting bluetooth")
        os.system("sudo systemctl start bluetooth.service")
