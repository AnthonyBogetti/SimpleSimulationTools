import numpy as np
import glob
import os
import re
import subprocess
import sys

status = sys.argv[1]
exchange = int(sys.argv[2])
prev_exchange = str((exchange-1)).zfill(5)

def calc_E(rep_coords, ref_coords, k):
    dx2 = (rep_coords[0] - ref_coords[0])**2
    dy2 = (rep_coords[1] - ref_coords[1])**2
    dz2 = (rep_coords[2] - ref_coords[2])**2
    return (k*dx2+k*dy2+k*dz2)

ladder = np.loadtxt("ladder", dtype=str)
reps = ladder[:,0]
for rep in reps:
    repi = str(rep).zfill(3)
    with open("meld.pdb."+repi, "w") as file:
        subprocess.run(['ambpdb', '-p', '../../common_files/4ake.prmtop', '-c', 'meld.rst.'+repi], stdout=file)

entries = []

with open("../../common_files/ladder", "r") as file:
    lines = file.readlines()
    for line in lines:
        t = float("{:.2f}".format(float(line.split()[1])))
        k = float("{:.2f}".format(float(line.split()[2])))
        entries.append(tuple([t, k]))

tandk = dict(entries)

curr_t = []
curr_k = []
next_t = []
next_k = []

if status == "new":
    prev_ladder = "../../common_files/ladder"
elif status == "cont":
    prev_ladder = "../%s/ladder"%prev_exchange

with open(prev_ladder, "r") as file:
    lines = file.readlines()
    for line in lines:
        curr_t.append(float("{:.2f}".format(float(line.split()[1]))))
        curr_k.append(float("{:.2f}".format(float(line.split()[2]))))

with open("ladder", "r") as file:
    lines = file.readlines()
    for line in lines:
        t = float("{:.2f}".format(float(line.split()[1])))
        next_t.append(t)
        next_k.append(tandk[t])

ref_folder_path = "../../common_files/refs"

atoms = ["CA", "C", "O", "N"]

frac = 1.0

ref_coords = []

for filename in sorted(glob.glob(os.path.join(ref_folder_path, "ref.pdb.*"))):
    with open(filename, 'r') as file:
        coords = []
        lines = file.readlines()
        for line in lines:
            line = re.split(r'\s+', line)
            if line[0] == "ATOM":
                if line[2] in atoms:
                    coords.append([line[6], line[7], line[8]])
        ref_coords.append(coords)

ref_coord_arr = np.array(ref_coords, dtype=float)

rep_coords = []

for filename in sorted(glob.glob(os.path.join(".", "meld.pdb.*"))):
    with open(filename, 'r') as file:
        coords = []
        lines = file.readlines()
        for line in lines:
            line = re.split(r'\s+', line)
            if line[0] == "ATOM":
                if line[2] in atoms:
                    coords.append([line[6], line[7], line[8]])
        rep_coords.append(coords)

rep_coord_arr = np.array(rep_coords, dtype=float)

next_refs = []

for irep, rep in enumerate(rep_coord_arr):
    enes_refA = []
    enes_refB = []
    for iatom, atom in enumerate(rep):
        enes_refA.append(calc_E(ref_coord_arr[0][iatom], atom, curr_k[irep]))
        enes_refB.append(calc_E(ref_coord_arr[1][iatom], atom, curr_k[irep]))
    fracA = int(len(enes_refA)*frac)
    fracB = int(len(enes_refB)*frac)
    enes_refA_arr = np.sort(np.array(enes_refA))[:fracA]
    enes_refB_arr = np.sort(np.array(enes_refB))[:fracB]
    sumA = np.sum(enes_refA_arr)
    sumB = np.sum(enes_refB_arr)
    with open("cartesian.dat", "a") as file:
        if sumA < sumB:
            next_refs.append("A")
        elif sumB < sumA:
            next_refs.append("B")
        else:
            next_refs.append("B")

print(next_t, next_k, next_refs)

with open("ladder", "w") as file:
    for idx, rep in enumerate(reps):
        file.write(str(rep)+" "+str(next_t[idx])+" "+str(next_k[idx])+" "+str(next_refs[idx])+"\n")
