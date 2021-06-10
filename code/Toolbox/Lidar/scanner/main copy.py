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


def get_radar_data(should_scan):
    # Execute the following command
    command = ("./simple_grabber /dev/ttyUSB0 "+ should_scan).split()
    sp = subprocess.run(command, text=True,  stdout=sys.stdout,  stderr=sys.stderr)
    # Split data into rows
    # data = sp.stdout.readlines().split("\n")
    rows = []
    out = sp.stdout.read(1)
    if out == '' and sp.poll() != None:
        pass
    if out != '':
        tmp = out.split(",")
        if len(tmp) != 2:
            pass
        rows.append((int(tmp[0]), float(tmp[1]))) 

    sys.stdout.flush()
    print(rows)
    # for s in data:
    #     tmp = s.split(",")
    #     if len(tmp) != 2:
    #         continue
    #     rows.append((int(tmp[0]), float(tmp[1]))) 
    return rows

def make_graph(data, time_redraw):
    area = 5
    colors = [(1, 0.2, 0.3), (1, 0.8, 0), (0.1, 0.5, 0.1)]  # near -> mid -> far
    cmap_name = "distance_warning"
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(cmap_name, colors)
    data_x = []
    data_y = []
    # Create the colors I need, values between 0 and 1 for (r, g, b)
    
    # add angle in radian and his value in two array x and y 
    for angle, distance in data:
        data_x.append(math.radians(angle))
        data_y.append(distance)

    # set the projection to polar 
    plt.title("Lidar : ")
    plt.subplot(projection="polar")
    plt.scatter(data_x, data_y, s=area, c=data_y, cmap=cmap)
    plt.savefig("test.png")
    plt.clf()
    time.sleep(time_redraw)

async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line)
        else:
            break

async def run(command):
    process = await create_subprocess_exec(
        *command, stdout=PIPE, stderr=PIPE
    )

    await asyncio.wait(
        [
            _read_stream(
                process.stdout,
                lambda x: print(
                    "STDOUT: {}".format(x.decode("UTF8"))
                ),
            ),
            _read_stream(
                process.stderr,
                lambda x: print(
                    "STDERR: {}".format(x.decode("UTF8"))
                ),
            ),
        ]
    )

    await process.wait()


async def main():
    await run("docker build -t my-docker-image:latest .")

if __name__ == "__main__":
    time_between_scans = 6
    run_scan = True
    get_value = '1'

    try:
        while run_scan:
            make_graph(get_radar_data(get_value), time_between_scans)
        # time.sleep(time_between_scans)
        # get_radar_data('1')

    except KeyboardInterrupt:
        get_radar_data('0')
