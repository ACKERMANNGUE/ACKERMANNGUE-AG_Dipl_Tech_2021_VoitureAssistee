# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Pybricks Authors

"""
Hardware Module: 1

Description: This tests the lights on the Ultrasonic Sensor. No external
sensors are used to verify that it works.
"""

from pybricks.pupdevices import UltrasonicSensor
from pybricks.parameters import Port
from pybricks.tools import wait
from urandom import randint

# Initialize devices.
lights = UltrasonicSensor(Port.C).lights

# Turn on all lights at full brightness.
lights.on()
wait(500)

# Turn on all lights.
for i in range(-50, 150, 2):
    lights.on(i)
    wait(20)

# Turn of all lights.
lights.off()
wait(500)

# Turn on all lights.
for i in range(50):
    lights.on([randint(0, 100) for j in range(4)])
    wait(50)
