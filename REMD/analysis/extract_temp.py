import numpy as np
import os
import subprocess
import sys

temp = float(sys.argv[1])

root_dir = "../rep_segs"

paths = []

for rep_dir in os.listdir(root_dir):
        rep_path = os.path.join(root_dir, rep_dir)
        if os.path.isdir(rep_path):
            paths.append(rep_path)

sorted_paths = (sorted(paths))

with open("extract_temp.cpp", "w") as file:
    file.write("parm ../common_files/4ake.prmtop"+"\n")
    for path in sorted_paths:
        ladder = np.loadtxt(path+"/ladder")
        repi = (np.where(ladder==temp))[0][0]
        repi_str = str(repi).zfill(3)
        file.write("trajin "+path+"/meld.nc."+repi_str+"\n")
    file.write("trajout meld.nc.%sK"%str(int(temp))+" netcdf"+"\n")
                        
subprocess.run(['cpptraj', '-i', 'extract_temp.cpp'])

os.remove("extract_temp.cpp")
