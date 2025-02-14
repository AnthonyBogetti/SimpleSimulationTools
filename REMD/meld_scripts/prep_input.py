import numpy as np
import os
import subprocess
import sys

status = sys.argv[1]
exchange = int(sys.argv[2])
prev_exchange = str((exchange-1)).zfill(5)

if os.path.exists("meld.groupfile"):
    os.remove("meld.groupfile")


if status == "new":

    ladder = np.loadtxt("../../common_files/ladder", dtype=str)

    for rep in ladder:
        irep = str(rep[0]).zfill(3)
        temp = rep[1]
        replace_temp = "s/TTTTT/%s/g"%temp

        with open("meld.in."+irep, "w") as file:
            subprocess.run(['sed', replace_temp, '../../common_files/meld.in'], stdout=file, text=True)

        with open("meld.groupfile", "a") as file:
            file.write("-O -rem 0 -i meld.in."+irep+" -o meld.out."+irep+" -e meld.ene."+irep+" -c ../../bstates/eq.rst."+irep+" -r meld.rst."+irep+" -x meld.nc."+irep+" -p ../../common_files/4ake.prmtop"+"\n" )

elif status == "cont":

    ladder = np.loadtxt("../"+prev_exchange+"/ladder", dtype=str)

    for rep in ladder:
        irep = str(rep[0]).zfill(3)
        temp = rep[1]
        replace_temp = "s/TTTTT/%s/g"%temp

        with open("meld.in."+irep, "w") as file:
            subprocess.run(['sed', replace_temp, '../../common_files/meld.in'], stdout=file, text=True)

        with open("meld.groupfile", "a") as file:
            file.write("-O -rem 0 -i meld.in."+irep+" -o meld.out."+irep+" -e meld.ene."+irep+" -c ../"+prev_exchange+"/meld.rst."+irep+" -r meld.rst."+irep+" -x meld.nc."+irep+" -p ../../common_files/4ake.prmtop"+"\n" )
