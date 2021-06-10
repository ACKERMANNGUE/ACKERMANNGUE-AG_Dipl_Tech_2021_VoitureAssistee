# @file sensor.py
# @brief The class which determine what is a sensor

# Author : Ackermann Gawen
# Last update : 10.06.2021
import json
class Sensor:
    """Class containing the values of the sensor
    """

    def __init__(cls, sensor_type, sensor_state):
        """Initialize the sensor"""
        cls.type = sensor_type
        cls.state = sensor_state
    
    def convert_to_json(self):
        """Convert the object into json"""
            return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)