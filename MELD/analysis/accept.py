import numpy as np
import os
import subprocess

attempts = 0
success = 0

root_dir = "../rep_segs"

paths = []

for rep_dir in os.listdir(root_dir):
        rep_path = os.path.join(root_dir, rep_dir)
        if os.path.isdir(rep_path):
            paths.append(rep_path)

sorted_paths = (sorted(paths))

for path in sorted_paths:
    if os.path.isfile(path+"/success"):
        nums = np.loadtxt(path+"/success", dtype=int)
        attempts += nums[0]
        success += nums[1]

print((success/attempts)*100)
