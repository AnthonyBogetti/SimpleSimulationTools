import numpy as np
import os
import re 
import subprocess
import sys

kb = 0.001987

status = sys.argv[1]
exchange = int(sys.argv[2])

prev_exchange = str((exchange-1)).zfill(5)

odd_or_even = None

if exchange % 2 == 0:
    odd_or_even = "even"
else:
    odd_or_even = "odd"

if status == "new":
    ladder = np.loadtxt("../../common_files/ladder", dtype=str)
elif status == "cont":
    ladder = np.loadtxt("../%s/ladder"%prev_exchange, dtype=str)

reps = ladder[:,0]
temps = ladder[:,1]
enes = []

print(reps, temps)

for rep in reps:
    irep = str(int(rep)).zfill(3)
    with open("meld.ene.%s"%irep, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = re.split(r'\s+', line)
            if line[0] == "L6":
                if line[3] != "E_vdw":
                    enes.append(float(line[3]))

if odd_or_even == "even":
    reps_to_consider = reps[::2]
elif odd_or_even == "odd":
    reps_to_consider = reps[1::2]

new_ladder = []
success = 0
attempt = 0


for idx, rep in enumerate(reps):
    if rep in reps_to_consider:
        rep = int(rep)
        try:
            nrep = int(reps[idx+1])
            print(rep, nrep)
            temp1 = float(temps[idx])
            epot1 = enes[idx]
            temp2 = float(temps[idx+1])
            epot2 = enes[idx+1]
            print(temp1, temp2)
            metro = np.exp(((1/(kb*temp1))-(1/(kb*temp2)))*(epot1-epot2))
            rand = np.random.rand()
            attempt += 1
            print(rand, metro)
            if rand < metro:
                new_ladder.append([nrep, temp1])
                new_ladder.append([rep, temp2])
                success += 1
                scale1 = np.sqrt(temp2/temp1)
                scale2 = np.sqrt(temp1/temp2)
                rst1 = str(rep).zfill(3)
                rst2 = str(rep+1).zfill(3)
                replace_rst1 = "s/XXX/%s/g"%rst1
                replace_rst2 = "s/XXX/%s/g"%rst2
                replace_scale1 = "s/FFF/%s/g"%scale1
                replace_scale2 = "s/FFF/%s/g"%scale2

#                with open("rescale.cpp."+rst1, "w") as file:
#                    subprocess.run(['sed', '-e', replace_rst1, '-e', replace_scale1, 'rescale.cpp'], stdout=file, text=True)
#
#                with open("rescale.cpp."+rst2, "w") as file:
#                    subprocess.run(['sed', '-e', replace_rst2, '-e', replace_scale2, 'rescale.cpp'], stdout=file, text=True)
#
#                subprocess.run(['cpptraj', '-i', 'rescale.cpp.%s'%rst1])
#                subprocess.run(['cpptraj', '-i', 'rescale.cpp.%s'%rst2])
#
#                os.remove('rescale.cpp.%s'%rst1)
#                os.remove('rescale.cpp.%s'%rst2)

            else:
                new_ladder.append([rep, temp1])
                new_ladder.append([nrep, temp2])

        except:
            new_ladder.append([rep, float(temps[rep])])
            continue
    else:
        rep = int(rep)

        if new_ladder:

            if float(rep) in np.array(new_ladder)[:,0]:
                continue
            else:
                new_ladder.append([rep, float(temps[rep])])
        else:
            new_ladder.append([rep, float(temps[rep])])


with open("ladder", "w") as file:
    for rung in new_ladder:
        file.write(str(rung[0])+" "+str(rung[1])+"\n")

with open("success", "w") as file:
    file.write(str(attempt)+" "+str(success))
