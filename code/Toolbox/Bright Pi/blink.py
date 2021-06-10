# @file blink.py
# @brief Make the Bright Pi blink

# Author : Ackermann Gawen
# Last update : 10.06.2021

from brightpi import *  # Concerne les fichiers relatifs au Bright Pi
import time  # Concerne le délai à attendre lors d’instructions

def blink(repetitions, speed, right_leds, left_leds, side):
    """Make the bright pi leds blink
    
    repetitions : The number of times the blink should appear
    speed : The amount of time a led needs to be activated and disabled. 
            The times is divided by 2, e.g. 1 second will be 0.5 second on and 0.5 off
    right_leds : The indexes of the right leds
    left_leds : The indexes of the left leds
    side : The side we want to make it blinks
    """
    # make the specified led to blink
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

# Initialisation of the bright pi
bright_special = BrightPiSpecialEffects()
bright_special.reset()
# Setting up indexes
RIGHT_LEDS = [1, 2]
LEFT_LEDS = [3, 4]

blink(10, 1, RIGHT_LEDS, LEFT_LEDS, "R")