# container-noresm

Containers (docker &amp; singularity) for NorESM, the Norwegian Earth System Model.

[![DOI](https://zenodo.org/badge/355181297.svg)](https://zenodo.org/badge/latestdoi/355181297)

## hpccm to create Dockerfile and associated containers

We use [HPC Container Maker](https://github.com/NVIDIA/hpc-container-maker)  (HPCCM - pronounced H-P-see-M), an open source tool to easily generate container specification files.

```
 hpccm --recipe noresm_gnu.py --format docker > Dockerfile
```

## Docker container

The docker container is automatically generated (github actions) and pushed to [quay.io](https://quay.io/):

```
docker pull quay.io/nordicesmhub/container-noresm:v1.0.0
```

## Singularity container

### Pull singularity container

We can then pull the image to generate a singularity image:

```
singularity pull docker://quay.io/nordicesmhub/container-noresm:v1.0.0
```

The previous command generates `container-noresm_v1.0.0.sif` that is ready to be run on your HPC, desktop/laptop, etc.

### Create NorESM case, compile and prepare input data

We will be using [Betzy](https://documentation.sigma2.no/hpc_machines/betzy.html), the most powerful supercomputer in Norway (2021) and prepare a case for running on one single node e.g. 128 processors. 

The creation, setup and compilation of the case as well as a check of the availability of the necessary of the input data can be done interactively on an interactive node on Betzy. All NorESM/CESM input data can be found in `/cluster/shared/noresm/inputdata` and this is why we are binding this folder to  `/opt/esm/inputdata`. We also want to make sure we can access both the work and archive directories so these two folders are bound to `$USERWORK/work` and `$USERWORK/archive`, respectively. Please note that at this stage only the work directory will be used.

```
export COMPSET='NF2000climo'
export RES='f19_f19_mg17'
export CASENAME='noresm-gnu-container-mpich-'$SLURM_JOB_NUM_NODES'x128p-'$COMPSET'-'$RES
echo $CASENAME
#
singularity exec --bind $USERWORK/work:/opt/esm/work,/cluster/shared/noresm/inputdata:/opt/esm/inputdata,$USERWORK/archive:/opt/esm/archive container-noresm_v1.0.0.sif /opt/esm/prepare
```

An example of the script `prepare` is available in the container (and also in this repository).

Once it is successfully completed, we can then run the NorESM model (corresponding to `case.submit`). Below is an example of the slurm job we used to run on Betzy:


```
#!/bin/bash
#
#SBATCH --account=nn9560k
#SBATCH --job-name=noresm-gnu-container-mpich
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=128
#SBATCH --qos=devel
#SBATCH --export=ALL
#SBATCH --switches=1
#SBATCH --exclusive
#
module purge
module load intel/2020b
#
export KMP_STACKSIZE=64M
#
export COMPSET='NF2000climo'
export RES='f19_f19_mg17'
export CASENAME='noresm-gnu-container-mpich-'$SLURM_JOB_NUM_NODES'x128p-'$COMPSET'-'$RES
echo $CASENAME
#
mpirun -np $SLURM_NTASKS singularity exec --bind $USERWORK/work:/opt/esm/work,/cluster/shared/noresm/inputdata:/opt/esm/inputdata,$USERWORK/archive:/opt/esm/archive container-noresm_v1.0.0.sif /opt/esm/execute
```

Once finalized, the results of your norESM run is available on betzy in `$USERWORK/archive`.

The timing information (including model cost, throughput, etc.) can be found in a folder called `timing` in the case directory:


