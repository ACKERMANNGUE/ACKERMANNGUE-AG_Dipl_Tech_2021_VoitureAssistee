import json
class Sensor:
    """Class containing the values of the sensor
    """

    def __init__(cls, sensor_type, sensor_state):
        cls.type = sensor_type
        cls.state = sensor_state
    
    def convert_to_json(self):
            return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)