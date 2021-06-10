#!/usr/bin/env python3

from pyb00st_lib.movehub import MoveHub

mymovehub = MoveHub("90:84:2B:50:36:43", "hci0")
if not mymovehub.is_connected():
    print("No connection")
    mymovehub.connect()
    
print(mymovehub.getaddress())
print(mymovehub.getname())
