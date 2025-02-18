import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
import sys

rep = int(sys.argv[1])

root_dir = "../rep_segs"

paths = []

for rep_dir in os.listdir(root_dir):
        rep_path = os.path.join(root_dir, rep_dir)
        if os.path.isdir(rep_path):
            paths.append(rep_path)

sorted_paths = (sorted(paths))

otemps = np.loadtxt("../common_files/ladder", usecols=1)

for t in otemps:
    plt.axhline(y=t, color="k", alpha=0.1)

plt.yticks(otemps)


temps = []

for path in sorted_paths:
    if os.path.exists(path+"/ladder"):
        ladder = np.loadtxt(path+"/ladder", usecols=(0,1))
        repi = (np.where(ladder==rep))[0][0]
        temps.append(ladder[repi][1])

xs = np.arange(1,len(temps)+1)

plt.plot(xs, temps)

plt.show()


