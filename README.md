# Basic commands and Files to run jobs on a SLURM server

### Bell
### Halstead
### Brown

## General Comands
#---------------------------------------------------------------------------------
GENERAL INFORMATION COMMANDS
#---------------------------------------------------------------------------------
myquota                 # SHOWS THE NUMBER OF AVAILABLE CPUS
squeue -A aarrieta      # SHOWS ALL JOBS RUNNING UNDER "aarrieta" ACCOUNT
squeue -u $USER         # SHOWS ALL JOBS RUNNING UNDER USER ACCOUNT

#---------------------------------------------------------------------------------
RUNNING COMMANDS
#---------------------------------------------------------------------------------
sbatch FILE_NAME.sh     # RUN BASH FILE
scancel JOBID           # CANCEL JOB (JOB ID CAN BE FOUND USING "squeue -u $USER")

#---------------------------------------------------------------------------------
CHECK ABAQUS TOKENS
#---------------------------------------------------------------------------------
ml bioinfo lmstat
lmstat -a -c 1736@mooring.ecn.purdue.edu 
lmstat -f abaqus -c 1736@mooring.ecn.purdue.edu | grep -iE "ARRIETA|aarrieta|hwang125|riley104|dmboston|jrivaspa|thakkara|chan160|rojas23|osorio2|caddis|morga263|kboddapa|sadeghs|liang287|yki"

IF YOU ARE NOT ON THE LIST, PLEASE ADD YOURSELF

#---------------------------------------------------------------------------------
PURGE LIST (AVOID FILES BEEN DELETED AFTER 60 DAYS FROM FOR SCRATCH FORLDER)
TOUCH AVERY FILE IN THE FOLDER TO UPDATE MODIFIED DAY
#---------------------------------------------------------------------------------
GO TO USER SCRATCH
    cd $CLUSTER_SCRATCH
CHANGE THE DATE OF ALL OF YOUR FILES
    find . -exec touch {} \;
CHECK IF THERE ARE STILL FILES TO REMOVE
    purgelist


