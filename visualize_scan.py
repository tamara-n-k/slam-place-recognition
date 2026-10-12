import sys
import struct
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

def convert(x_s, y_s, z_s):
    scaling = 0.005  # 5 mm
    offset = -100.0
    x = x_s * scaling + offset
    y = y_s * scaling + offset
    z = z_s * scaling + offset
    return x, y, z

def read_velodyne_bin(bin_path):
    hits = []
    with open(bin_path, "rb") as f_bin:
        while True:
            x_bytes = f_bin.read(2)
            if len(x_bytes) < 2:
                break  # EOF

            x = struct.unpack('<H', x_bytes)[0]
            y = struct.unpack('<H', f_bin.read(2))[0]
            z = struct.unpack('<H', f_bin.read(2))[0]
            i = struct.unpack('B', f_bin.read(1))[0]
            l = struct.unpack('B', f_bin.read(1))[0]

            x_m, y_m, z_m = convert(x, y, z)
            hits.append([x_m, y_m, z_m])

    return np.array(hits)

def main(bin_path):
    points = read_velodyne_bin(bin_path)

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=1)
    plt.show()

if __name__ == "__main__":
    bin_file = "data/2012-01-08_vel/2012-01-08/velodyne_sync/1326030975726043.bin"
    main(bin_file)
