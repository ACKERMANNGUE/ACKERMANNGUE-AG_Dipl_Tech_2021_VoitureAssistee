from pylgbst.hub import MoveHub
from pylgbst.peripherals import Motor, EncodedMotor
from pylgbst import *

class CarController:
    """Class controlling the car
    """
    instance = None
    
    MY_MOVEHUB_ADD = "90:84:2B:50:36:43"
    MY_BTCTRLR_HCI = "hci0"
    MAX_ANGLE = 150
    MAX_MOTOR_POWER = 1
    MOTOR_STOP_POWER = 0
    
    def __new__(cls):
        if(cls.instance is None):
            cls.instance = super(CarController, cls).__new__(cls)
            cls.connection = get_connection_gatt(hub_mac=cls.MY_MOVEHUB_ADD)
            try:
                # The motors 
                cls.movehub = MoveHub(cls.connection)
                cls.front_motor = Motor(cls.movehub, cls.movehub.PORT_A)
                cls.back_motor = Motor(cls.movehub, cls.movehub.PORT_B)
                cls.directionnal_motor = EncodedMotor(cls.movehub, cls.movehub.PORT_C)
            except:
                cls.movehub = None
                cls.front_motor = None
                cls.back_motor = None
                cls.directionnal_motor = None
        return cls.instance
    
    def move(self, motor_speed, angle_rotation):
        """Moves the car with a specific speed and rotation
        
        motor_speed : The motor's speed
                      NOTE : to move forward, the value must be reversed because it is basically negative
        angle_rotation : The rotation of the directionnal motor
        """
        # Invert the power direction
        motor_speed *= (-1)
        # Max value of motor is -1 and +1 but in the HTML form, the range input can be set between -100 to +100
        motor_speed /= 100
        
        self.front_motor.start_power(motor_speed)
        self.back_motor.start_power(motor_speed)
        self.directionnal_motor.start_power(angle_rotation)
    

    def turn(self, motor, angle):
        """Turn the directionnal motor from the input value

        motor : The directionnal motor
        """
        motor.angled(angle)


    def stop_moving(self):
        """Stop the motors
        """
        self.front_motor.start_power(self.MOTOR_STOP_POWER)
        self.back_motor.start_power(self.MOTOR_STOP_POWER)
        
        
