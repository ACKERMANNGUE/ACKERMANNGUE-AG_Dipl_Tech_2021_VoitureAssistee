#!/usr/bin/env python3

from pyb00st.movehub import MoveHub
from pyb00st.constants import *

from time import sleep

MY_MOVEHUB_ADD = '90:84:2B:50:36:43'
MY_BTCTRLR_HCI = 'hci0'

mymovehub = MoveHub(MY_MOVEHUB_ADD, 'BlueZ', MY_BTCTRLR_HCI)

try:
    mymovehub.start()
    mymovehub.subscribe_all()
    mymovehub.listen_hubtilt(MODE_HUBTILT_BASIC)

    while True:
        print('Is connected: ', mymovehub.is_connected())
        sleep(1)

finally:
    mymovehub.stop()

