# Basic commands and Files to run jobs on a SLURM server (Bell, Halstead, Brown)

First install enhanced terminal for Windows with X11 server, tabbed SSH client, we recommend MobaXterm:

+ [MobaXterm](https://mobaxterm.mobatek.net/download-home-edition.html)
+ [PuTTY](https://www.putty.org/)

### Remote Host

+ Bell     -> bell-fe05.rcac.purdue.edu
+ Halstead -> halstead-fe00.rcac.purdue.edu
+ Brown    -> brown-fe01.rcac.purdue.edu

![Domes](Figures/Remote_Host.PNG)


You can also access the server online using the following links (Remote Desktop):

+ [Bell](https://www.rcac.purdue.edu/compute/bell)
+ [Halstead](https://www.rcac.purdue.edu/compute/halstead)
+ [Brown](https://www.rcac.purdue.edu/compute/brown)

## This repository includes

+   ABAQUS_RUN.sh               ->  Bash file to run Abaqus job
+   ABAQUS_Array_Submission     ->  Bash file to run Parallel Abaqus job with SLURM array submission

## Running Commands

 + Run bash File                                            -> sbatch FILE_NAME.sh
 + Cancel Job (Job ID can be found using "squeue -u $USER") -> scancel JOBID 

## General information commands

+ Show the number of available cpus                 ->  myquota
+ Show all jobs running under "aarrieta" account    ->  squeue -A aarrieta
+ Show all jobs running under "aarrieta" account    ->  squeue -u $USER

## Check ABAQUS Tokens

ml bioinfo lmstat

lmstat -a -c 1736@mooring.ecn.purdue.edu 

lmstat -f abaqus -c 1736@mooring.ecn.purdue.edu | grep -iE "ARRIETA|aarrieta|hwang125|riley104|dmboston|jrivaspa|thakkara|chan160|rojas23|osorio2|caddis|morga263|kboddapa|sadeghs|liang287|yki"

IF YOU ARE NOT ON THE LIST, PLEASE ADD YOURSELF

## Purge List
- Avoid files been deleted after 60 days from the scratch folder
- Touch every file in the folder to updated the modified dat

+ Go to user scratch                        ->  cd $CLUSTER_SCRATCH
+ Change the date of all your files         ->  find . -exec touch {} \;
+ Check if there are still files to remove  ->  purgelist
