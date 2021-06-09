

import RPi.GPIO as GPIO
import time
import asyncio

# Set the mode into Broadcom SOC channel
# It allows to use GPIO number instead of pin number
GPIO.setmode(GPIO.BCM)

# Set the GPIO 23 into input mode
GPIO.setup(23, GPIO.IN)

def get_grounded_state(self):
    """Get the state of the flying-fish
    """
    print(str(not GPIO.input(23)))

if __name__ == '__main__':
    # Add the event to the GPIO
    GPIO.add_event_detect(23, GPIO.RISING, callback=get_grounded_state, bouncetime=100)
    while True:
        time.sleep(0.5)