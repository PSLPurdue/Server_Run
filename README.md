# Purdue HPC & Abaqus Scripting Tutorial

Guide for running Abaqus jobs on Purdue's SLURM clusters (Negishi, Bell) with scripting, batch submission, and post-processing workflows used by the Arrieta Research Group.

## Contents

+ Cluster access (Remote Desktop, SSH via VS Code)
+ Abaqus scripting (GUI, headless, macros)
+ SLURM job submission (single + array)
+ Results post-processing (single run + batch)

## Clusters

| Cluster  | Front-end Host                     | Hardware                                           |
|----------|------------------------------------|----------------------------------------------------|
| Negishi  | negishi.rcac.purdue.edu            | 2x 64-core AMD Epyc Milan, 256 GB RAM, HDR IB      |
| Bell     | bell.rcac.purdue.edu               | 2x 64-core AMD Epyc Rome, 256 GB RAM               |

Web portal (Remote Desktop, Open OnDemand):

+ [Negishi](https://www.rcac.purdue.edu/compute/negishi)
+ [Bell](https://www.rcac.purdue.edu/compute/bell)

## Install Tools

+ [Visual Studio Code](https://code.visualstudio.com) - editor with Remote-SSH extension
+ [MobaXterm](https://mobaxterm.mobatek.net/download-home-edition.html) - Windows SSH client with X11
+ [PuTTY](https://www.putty.org/) - alternative SSH client

### SSH Host Strings

+ Negishi  -> `<username>@negishi.rcac.purdue.edu`
+ Bell     -> `<username>@bell.rcac.purdue.edu`

## Workspace Setup

Always work on scratch. Do NOT use `/home` for simulation output.

```
/scratch/negishi/<username>/workspace/
```

In VS Code: `Ctrl+Shift+P` -> `Remote-SSH: Connect to Host...` -> enter host -> `Open Folder` -> paste the workspace path.

## Load Modules

Modules do not persist across terminals. Reload in every new session.

+ `ml intel abaqus/2023`
+ `ml anaconda`
+ `module list`

## Launch Abaqus

+ GUI (Remote Desktop)     -> `abaqus cae -mesa`
+ Run script headlessly    -> `abaqus cae NOGUI=your_script.py`
+ Run an input file        -> `abaqus interactive job=NAME inp=NAME.inp cpus=N`

## Job Submission Files

+ `ABAQUS_PYTHON_RUN.sh`       -> Run Abaqus with a Python script
+ `ABAQUS_INP_RUN.sh`          -> Run Abaqus with a `.inp` file
+ `ABAQUS_Array_Submission.sh` -> Parallel runs via SLURM array

Submit:

+ `sbatch FILE_NAME.sh`

Cancel:

+ `scancel <JOBID>`   (find JOBID with `squeue -u $USER`)

## SLURM Commands

+ Show group jobs                          -> `squeue -A aarrieta`
+ Show your jobs                           -> `squeue -u $USER`
+ Show available CPUs                      -> `qlist`
+ Show storage quotas                      -> `myquota`
+ Cancel a job                             -> `scancel <JOBID>`

## SLURM Array Template

```bash
#!/bin/bash
#SBATCH -A aarrieta
#SBATCH --nodes=1 --ntasks=15
#SBATCH --time=02:00:00
#SBATCH -J Tutorial
#SBATCH -o Tutorial%j.out
#SBATCH -e Tutorial%j.out
#SBATCH --mail-user=<username>@purdue.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --array 1-1%12
# array = initial-last%max_concurrent

if [[ -n $SLURM_SUBMIT_DIR ]]; then
    cd $SLURM_SUBMIT_DIR
fi

module load intel abaqus/2023
unset SLURM_GTIDS

n=$SLURM_ARRAY_TASK_ID
job_name="Metasheet_Plastic_Sample_${n}"
inp_name="${job_name}.inp"

abaqus interactive job=${job_name} inp=${inp_name} \
       cpus=$SLURM_NTASKS scratch=$PWD

echo "JOB DONE"
```

## Job Monitoring

+ `squeue -A aarrieta` - list all group jobs with CPU allocation
+ `<job_name>.sta` - status file updated each increment (step, inc, time). Use to estimate remaining runtime and spot hard-to-converge regions.

## Anaconda Environment (Python Package Install)

+ `module load anaconda/5.1.0-py36`
+ `conda-env-mod create -n mypackages`

### Load Custom Environment

+ `module load use.own`
+ `module load conda-env/mypackages-py3.6.4`

## Abaqus Scripting Workflow

1. Record GUI actions with `File > Macro Manager > Create` (save to Work).
2. Perform the operation in the GUI, then `Stop Recording`.
3. Open `abaqusMacros.py` to read the generated API calls.
4. Copy relevant lines into a clean script. Strip view/camera commands.
5. Run headless: `abaqus cae NOGUI=your_script.py`

## Post-Processing

### Single ODB (GUI)

Open `.odb` -> `File > Open` -> filter `Output Database (*.odb)`. Switch to Visualization module.

Useful history outputs:

+ `ALLSE` - strain energy (whole model). Quantifies bistability.
+ `RF2`   - reaction force in Y. Force needed to impose prescribed displacement.
+ `U2`    - Y displacement. Paired with RF2 for force-displacement curves.

### Figures & Animations

+ Apply viridis palette       -> run `Post_Image_ABAQUS_3.py` with an ODB open
+ Image export                -> `File > Print > Destination: File, Format: PNG`
+ Animation                   -> `Animate > Time History` -> time-based, set increment -> `Animate > Save As` (AVI)

### Batch Post-Processing

+ Extract metrics from all ODBs in a directory  -> `abaqus cae NOGUI=Maxstressstrainforarun.py`
+ Quick check plot                              -> `python plotter_stress_strain.py`
+ Publication plots                             -> `SingleInversion.m` (MATLAB). Copy the MATLAB PNG - higher DPI than Matplotlib preview.

CSV columns produced: `Time, MaxStress, MaxStrain, ALLSE, U2, RF2`

## Check Abaqus License Tokens

```
ml bioinfo lmstat
lmstat -a -c 1736@mooring.ecn.purdue.edu
lmstat -f abaqus -c 1736@mooring.ecn.purdue.edu | grep -iE "ARRIETA|aarrieta|hwang125|riley104|dmboston|jrivaspa|thakkara|chan160|rojas23|osorio2|caddis|morga263|kboddapa|sadeghs|liang287|yki"
```

IF YOU ARE NOT ON THE LIST, PLEASE ADD YOURSELF.

## Group Resources

+ Account  -> `aarrieta`
+ Capacity -> 256 CPUs, 220 Abaqus simulation tokens
+ Match `--ntasks` in SLURM to `cpus=` in the `abaqus interactive` call
