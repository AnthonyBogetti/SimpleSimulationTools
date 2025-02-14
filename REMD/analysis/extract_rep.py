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

with open("extract_rep.cpp", "w") as file:
    file.write("parm ../common_files/4ake.prmtop"+"\n")
    for path in sorted_paths:
        reps = np.loadtxt(path+"/ladder", dtype=str)[:,0]
        repi = reps[rep]
        repi_str = str(repi).zfill(3)
        file.write("trajin "+path+"/meld.nc."+repi_str+"\n")
    file.write("trajout meld.nc.rep%s"%str(int(repi))+" netcdf"+"\n")
                        
subprocess.run(['cpptraj', '-i', 'extract_rep.cpp'])

os.remove("extract_rep.cpp")
