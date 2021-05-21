import subprocess
from subprocess import Popen
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import math
import sys
import asyncio
from asyncio.subprocess import PIPE
from asyncio import create_subprocess_exec

rows = []


def get_radar_data(row):
    global rows
    # row = row.replace('\n', '')
    # tmp = row.split(",")
    tmp = row
    if len(tmp) == 2:
        angle = int(tmp[0])
        dist = tmp[1].replace(b'\n', b'')
        rows[angle] = float(dist)
    if angle == 359:
        make_graph(0)

def make_graph(time_redraw):
    global rows
    area = 5
    colors = [(1, 0.2, 0.3), (1, 0.8, 0), (0.1, 0.5, 0.1)]  # near -> mid -> far
    cmap_name = "distance_warning"
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(cmap_name, colors)
    data_x = []
    data_y = []
    angle = 0
    # Create the colors I need, values between 0 and 1 for (r, g, b)
    # add angle in radian and his value in two array x and y
    for distance in rows:
        data_x.append(math.radians(angle))
        data_y.append(distance)
        angle += 1

    # set the projection to polar
    plt.title("Lidar : ")
    plt.subplot(projection="polar")
    plt.scatter(data_x, data_y, s=area, c=data_y, cmap=cmap)
    plt.pause(0.05)
    plt.savefig("test.png")
    time.sleep(time_redraw)
    plt.clf()


async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line.split(b','))
        else:
            break


async def run(should_scan):
    command = ("./simple_grabber /dev/ttyUSB0 " + should_scan).split()
    process = await create_subprocess_exec(*command, stdout=PIPE, stderr=PIPE)
    await asyncio.wait(
        [
            _read_stream(
                process.stdout,
                lambda x: {
                    get_radar_data(x)
                }
            )
        ]
    )
    await process.wait()


async def main(should_scan):
    await run(should_scan)

size_rows = 360
rows = [0] * size_rows

if __name__ == "__main__":
    
    time_between_scans = 6
    run_scan = True
    should_scan = "1"

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(should_scan))

    except KeyboardInterrupt:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main("0"))
