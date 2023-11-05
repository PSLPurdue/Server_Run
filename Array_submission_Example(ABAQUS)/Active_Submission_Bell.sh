#!/bin/bash
#!/bin/sh
#SBATCH -A aarrieta
#SBATCH --nodes=1 --ntasks=15
#SBATCH --time=5:00:00
#SBATCH -J Active_Sheet 
#SBATCH -o Active_Sheet%j.out
#SBATCH -e Active_Sheet%j.out
#SBATCH --mail-user=osorio2@purdue.edu # Destination email address
#SBATCH --mail-type=END,FAIL # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --array=1-1000%15 # IMPORTANT! This gives you the paralell runs --> array=initial-last%max jobs at a time

# Go where we were when we typed 'squeue'
if [[ -n $SLURM_SUBMIT_DIR ]]; then
	cd $SLURM_SUBMIT_DIR
fi

# ------------------------------------------------------
# Define object type (Change between square and cylinder)
# ------------------------------------------------------
obj_type="square"
#obj_type="cylinder"

echo "Simulation had started for ${obj_type} Objects"
echo "Starting in: $(pwd)"

# ------------------------------------------------------
# Load Modules
# ------------------------------------------------------
# Halstead: # Use the following line to run Abaqus at Halstead (Check account -A)
# module load abaqus/2018 

# Bell: # Use the following line to run Abaqus at Bell (Check account -A)
module load anaconda/2020.11-py38
module load rcac
module load intel abaqus/2020
unset SLURM_GTIDS

# ------------------------------------------------------
# Create general directories 
# (Directories for converged and Failed Simulations)
# ------------------------------------------------------
# GENERAL
inp_folder="inp_files"
if [ ! -d "${inp_folder}" ]; then
  mkdir -p "${inp_folder}"
fi

# SUCCESS :)!
msg_folder="msg_files"
sta_folder="sta_files"
dat_folder="dat_files"
results_folder="results"

if [ ! -d "${msg_folder}" ]; then
  mkdir -p "${msg_folder}"
fi

if [ ! -d "${sta_folder}" ]; then
  mkdir -p "${sta_folder}"
fi

if [ ! -d "${dat_folder}" ]; then
  mkdir -p "${dat_folder}"
fi

if [ ! -d "${results_folder}" ]; then
  mkdir -p "${results_folder}"
fi

# FAIL :(!
fail_simulations="fail_simulations"

if [ ! -d "${fail_simulations}" ]; then
  mkdir -p "${fail_simulations}"
fi

# ------------------------------------------------------
# Loop over cases
# ------------------------------------------------------
echo "Start Loop"

n=$SLURM_ARRAY_TASK_ID # Get n simulation value from array

# As the array submission is restricted to 1000 simulations, we can use a simple trick
# Just add a constant number every 1000 simulations

fsim=1000
result=$(($fsim+$n))

# Make temporary directory
workingdir="Obj_${result}"
mkdir -p "${workingdir}"

# Copy files to directory
cp common/*.STEP $workingdir  # STEP_Files
cp common/*.csv $workingdir  # CSV_Files
cp common/*.py $workingdir  # Python files

cd $workingdir

# ------------------------------------------------------------------------------------------------------------
# Change as required
# ------------------------------------------------------------------------------------------------------------
# The following line reads a test/csv file with space delimiters that contain the parameters you want to loop
# You can get this file either by LHS or by hand, the only thing you need to be aware is to keep the same format
# n represent the simulation run and is used for parallel runs depending on what you define at the beginning of the file (see Line 12)
# If you only need a number to iterate over your code, you can use just n directly. This is just a simple way to plug multiple parameters with a text file

echo "Beginning Simulation ${result}"

# Get N parameters for simulation (Use any csv file)
iteration=`sed -n "${result} p" Active_Tests_LHD_$obj_type.csv`

# Change this line to the code you want to run
# Input parameters Number of cpus Problem Variables Object type

# Generate Input fule
nCPUS=$SLURM_NTASKS
abaqus cae noGUI=Active_Modality_Cluster.py -- ${nCPUS} ${iteration} ${obj_type}

# Submmit Job with out CAE license
job_name="Active_Obj_${result}"
inp_name="Active_Object_${result}"

abq2020 interactive job="${job_name}" inp="${inp_name}.inp" cpus=15 scratch="$(pwd)"

# ------------------------------------------------------------------------------------------------------------
# Move files
# ------------------------------------------------------------------------------------------------------------
sim_completed="0" # Initialized to 0 and change to 1 if the analysis is successful

dat_files="*.dat"
sta_files="*.sta"
msg_files="*.msg"
inp_files="*.inp"
odb_files="*.odb"      # Results files

if [ -f *.sta ]; then
  sim_completed=$(grep -c 'SUCCESSFULLY' *.sta)
  cp $inp_files -t ../$inp_folder
  
  if [ $sim_completed -eq 0 ]; then
    echo "The analysis was not successful"
    cp $msg_files -t ../$fail_simulations
    cp $sta_files -t ../$fail_simulations
    cp $dat_files -t ../$fail_simulations
    cp $odb_files -t ../$fail_simulations
  else
    echo "The analysis was successful"
    cp $msg_files -t ../$msg_folder
    cp $sta_files -t ../$sta_folder
    cp $dat_files -t ../$dat_folder
  
    cp $odb_files -t ../$results_folder
  fi

else
  echo "Error in simulation files ${result}"
fi
   
# Back to the main folder
cd ..

# ------------------------------------------------------
# Remove working directory
# ------------------------------------------------------
rm -rf "${workingdir}"/*
rm -rf "${workingdir}"
