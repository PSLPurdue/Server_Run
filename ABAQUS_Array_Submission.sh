#!/bin/bash
#!/bin/sh
#SBATCH -A aarrieta
#SBATCH --nodes=1 --ntasks=20
#SBATCH --time=10:00:00
#SBATCH -J Array_Example
#SBATCH -o Array_Example%j.out
#SBATCH -e Array_Example%j.out
#SBATCH --mail-user=osorio2@purdue.edu # Destination email address
#SBATCH --mail-type=END,FAIL # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --array 1-1%1 # IMPORTANT! This gives you the paralell runs --> array initial-last%max jobs at a time

# Go where we were when we typed 'squeue'
if [[ -n $SLURM_SUBMIT_DIR ]]; then
	cd $SLURM_SUBMIT_DIR
fi

echo "Simulation had started for ${obj_type} Objects"
echo "Starting in: $(pwd)"

# ------------------------------------------------------
# Load Modules
# ------------------------------------------------------
module load intel abaqus/2021
unset SLURM_GTIDS

# ------------------------------------------------------
# Set ABAQUYS JOB
# ------------------------------------------------------
n=$SLURM_ARRAY_TASK_ID # Get n simulation value from array

# Submmit Job with out CAE license
job_name="FILE_NAME_${n}"
inp_name="FILE_NAME_${n}"

abaqus interactive job=${job_name} inp=${inp_name}.inp cpus=$SLURM_NTASKS scratch=$PWD

# PRINT A MESSAGE ON THE .out FILE WHEN THE JOB IS FINISH
echo "JOB IS DONE!"