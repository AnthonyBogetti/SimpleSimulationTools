import numpy as np
import glob
import os
import re
import subprocess
import sys
from prody import *
from numba import njit

status = sys.argv[1]
exchange = int(sys.argv[2])
prev_exchange = str((exchange-1)).zfill(5)
frac = float(sys.argv[3])

@njit
def calc_E(ref_coords, rep_coords, k):
    enes = []
    for iatom, ref_atom in enumerate(ref_coords):
        rep_atom = rep_coords[iatom]
        dx2 = (rep_atom[0] - ref_atom[0])**2
        dy2 = (rep_atom[1] - ref_atom[1])**2
        dz2 = (rep_atom[2] - ref_atom[2])**2
        enes.append(k*dx2+k*dy2+k*dz2)
    return enes

def convert_list_to_string(numbers):
    numbers.sort()
    ranges = []
    start = numbers[0]
    end = numbers[0]

    for i in range(1, len(numbers)):
        if numbers[i] == end + 1:
            end = numbers[i]
        else:
            if start == end:
                ranges.append(f"{start}")
            else:
                ranges.append(f"{start}-{end}")
            start = numbers[i]
            end = numbers[i]

    if start == end:
        ranges.append(f"{start}")
    else:
        ranges.append(f"{start}-{end}")

    return ",".join(ranges)

ladder = np.loadtxt("ladder", dtype=str)
reps_next = ladder[:,0]
for rep in reps_next:
    repi = str(rep).zfill(3)
    with open("meld"+repi+".pdb", "w") as file:
        subprocess.run(['ambpdb', '-p', '../../common_files/4ake.prmtop', '-c', 'meld.rst.'+repi], stdout=file)

entries = []

with open("../../common_files/ladder", "r") as file:
    lines = file.readlines()
    for line in lines:
        t = float("{:.2f}".format(float(line.split()[1])))
        k = float(line.split()[2])
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
        curr_k.append(float(line.split()[2]))

with open("ladder", "r") as file:
    lines = file.readlines()
    for line in lines:
        t = float("{:.2f}".format(float(line.split()[1])))
        next_t.append(t)
        next_k.append(tandk[t])

print(curr_t, curr_k)
print(next_t, next_k)

ref_folder_path = "../../common_files/refs"

#atoms = ["CA"]
#
#ref_coords = []
refs = []

for filename in sorted(glob.glob(os.path.join(ref_folder_path, "*.pdb"))):
    refi = parsePDB(filename, subset="ca")
    refs.append(refi)
#    with open(filename, 'r') as file:
#        coords = []
#        lines = file.readlines()
#        for line in lines:
#            line = re.split(r'\s+', line)
#            if line[0] == "ATOM":
#                if line[2] in atoms:
#                    coords.append([line[6], line[7], line[8]])
#        ref_coords.append(coords)
#
#ref_coord_arr = np.array(ref_coords, dtype=float)
#
#rep_coords = []

reps = []

for filename in sorted(glob.glob(os.path.join(".", "*.pdb"))):
    repi = parsePDB(filename, subset="ca")
    reps.append(repi)
#    with open(filename, 'r') as file:
#        coords = []
#        lines = file.readlines()
#        for line in lines:
#            line = re.split(r'\s+', line)
#            if line[0] == "ATOM":
#                if line[2] in atoms:
#                    coords.append([line[6], line[7], line[8]])
#        rep_coords.append(coords)
#
#rep_coord_arr = np.array(rep_coords, dtype=float)

next_refs = []
next_sels = []

#for irep, rep in enumerate(rep_coord_arr):
for irep, rep in enumerate(reps):
#    enes_refA = []
#    enes_refB = []
    rep2 = rep.copy()
    rep_ali_refA, T = superpose(rep, refs[0])
    rep_ali_refB, T = superpose(rep2, refs[1])
    refA_coords = refs[0].getCoords()
    refB_coords = refs[1].getCoords()
    rep_ali_refA_coords = rep_ali_refA.getCoords()
    rep_ali_refB_coords = rep_ali_refB.getCoords()

    enes_refA = calc_E(refA_coords, rep_ali_refA_coords, curr_k[irep])
    enes_refB = calc_E(refB_coords, rep_ali_refB_coords, curr_k[irep])
#    print(enes_refA)
#    print(enes_refB)
#    for iatom, atom in enumerate(rep):
#        enes_refA.append(calc_E(ref_coord_arr[0][iatom], atom, curr_k[irep]))
#        enes_refB.append(calc_E(ref_coord_arr[1][iatom], atom, curr_k[irep]))
    resi = np.arange(1,len(enes_refA)+1)
    fracA = int(len(enes_refA)*frac)
    fracB = int(len(enes_refB)*frac)
    sortA = np.argsort(np.array(enes_refA))[:fracA]
    sortB = np.argsort(np.array(enes_refB))[:fracB]
    enes_refA_arr = np.array(enes_refA)[sortA]
    enes_refB_arr = np.array(enes_refB)[sortB]
    res_refA = resi[sortA]
    res_refB = resi[sortB]
    sumA = np.sum(enes_refA_arr)
    sumB = np.sum(enes_refB_arr)
    if sumA < sumB:
        next_refs.append("A")
        sel_str = ':'
        string = convert_list_to_string(list(res_refA))
        sel_str += string
        sel_str += '@CA'
        next_sels.append(sel_str)
    elif sumB < sumA:
        next_refs.append("B")
        sel_str = ':'
        string = convert_list_to_string(list(res_refB))
        sel_str += string
        sel_str += '@CA'
        next_sels.append(sel_str)
    else:
        next_refs.append("B")
        sel_str = ':'
        string = convert_list_to_string(list(res_refB))
        sel_str += string
        sel_str += '@CA'
        next_sels.append(sel_str)

with open("ladder", "w") as file:
    for idx, rep in enumerate(reps_next):
        file.write(str(rep)+" "+str(next_t[idx])+" "+str(next_k[idx])+" "+str(next_refs[idx])+" "+str(next_sels[idx])+"\n")
