#!/bin/bash
#SBATCH --job-name=SST-REMD
#SBATCH --partition gpu_amber
#SBATCH --nodes=1
#SBATCH --gres=gpu:2080:4
#SBATCH --ntasks=4
#SBATCH --output=job_logs/slurm.out
#SBATCH --error=job_logs/slurm.err
#SBATCH --time=12:00:00

module load amber cuda12.2 openmpi

N_REPS=4
TOTAL_X=10

if [ -z "$( ls -A 'rep_segs' )" ]; then
    if [ -s meld.log ]; then
	rm meld.log
    fi
    echo "Beginning a new MELD simulation." >> meld.log
    X=0
else
    X=$(ls rep_segs | tail -n 1 | sed "s/^0*//")
    X_LST=$(ls rep_segs | tail -n 1)
    if [ -s meld.log ]; then
        mv meld.log rep_segs/$X_LST
    fi
    echo "Continuing an existing MELD simulation." >> meld.log
    echo "The old meld.log was moved to rep_segs/$X_LST." >> meld.log

    if [ -s rep_segs/$X_LST/rem.log ]; then
        let X+=1
    else
        echo "The most recent exchange failed. Repeating..." >> meld.log
        rm -r rep_segs/$X_LST
    fi
fi

while [ $X -lt $TOTAL_X ]; do

    X_PRV=`printf "%05d" $X`
    let X+=1
    X_FMT=`printf "%05d" $X`

    echo "Starting exchange $X at `date "+%Y-%m-%d %H:%M:%S"`." >> meld.log

    if [ ! -d rep_segs/$X_FMT ]; then
        mkdir rep_segs/$X_FMT
    fi

    cd rep_segs/$X_FMT

    ln -s ../../common_files/REST .
    ln -s ../../meld_scripts/prep_input.py .
    ln -s ../../meld_scripts/exchange.py .
    ln -s ../../meld_scripts/rescale.cpp .

    if (( X == 1 )); then 
        python prep_input.py new $X
    else
        python prep_input.py cont $X
    fi

    mpirun -np $N_REPS pmemd.cuda.MPI -ng $N_REPS -groupfile meld.groupfile

    if (( X == 1 )); then 
        python exchange.py new $X
    else
        python exchange.py cont $X
    fi

    CHECK=$(cat ladder | wc -l)

    if [ $CHECK == $N_REPS ]; then
        echo "Successfully completed exchange." >> ../../meld.log
    else
        echo "Failed to complete exchange. Shutting down..." >> ../../meld.log
	exit
    fi

    cd ../../

done

echo "The MELD simulation completed successfully." >> meld.log
