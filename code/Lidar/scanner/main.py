import subprocess
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import math

# Execute the following command
command = "./simple_grabber /dev/ttyUSB0".split()
sp = subprocess.run(command, capture_output=True, text=True)
# Split data into rows
data = sp.stdout.split("\n")
rows = []
for s in data:
  
    tmp = s.split(",")
    if len(tmp) != 2:
        continue
    rows.append((int(tmp[0]), float(tmp[1])))


data_x = []
data_y = []
for angle, distance in rows:
    data_x.append(math.radians(angle))
    data_y.append(distance)


# print(data_pos)

# np.random.seed(1) 

# Compute areas and colors
# N = 150
# data_y = 100 * np.random.rand(N)
# data_x = 2 * np.pi * np.random.rand(N)
# print(theta)

# area = 60* r**2
# colors = theta

plt.subplot(projection="polar")
plt.scatter(data_x, data_y, s=1)
# plt.scatter(data_x, data_y, c=colors, s=area, cmap="hsv", alpha=0.75)
plt.savefig("test.png")

# fig.savefig('test.png')
