import RPi.GPIO as GPIO
import time

# Set the mode into Broadcom SOC channel
# It allows to use GPIO number instead of pin number
GPIO.setmode(GPIO.BCM)

# Set the GPIO 23 into input mode
GPIO.setup(23, GPIO.IN)

while True:
    # The actual state of the GPIO 23
    input_state = GPIO.input(23)
    if input_state == True:
        print("ATTENTION ! IL N'Y A PLUS DE SOL !")
        time.sleep(0.5)
    else:
        print("Sol détecté")
        time.sleep(0.5)
        