# container-noresm

Containers (docker &amp; singularity) for NorESM, the Norwegian Earth System Model.

[![DOI](https://zenodo.org/badge/355181297.svg)](https://zenodo.org/badge/latestdoi/355181297)

## hpccm to create Dockerfile and associated containers

We use [HPC Container Maker](https://github.com/NVIDIA/hpc-container-maker)  (HPCCM - pronounced H-P-see-M), an open source tool to easily generate container specification files.

```
 hpccm --recipe noresm_gnu.py --format docker > Dockerfile
```

## Docker container

The docker GNU containers (GNU-MPICH & GNU-OpenMPI) are automatically generated (github actions) and pushed to [quay.io](https://quay.io/):

```
docker pull quay.io/nordicesmhub/container-noresm:gnu_mpich-v3.0.0
```

or 

```
docker pull quay.io/nordicesmhub/container-noresm:gnu_openmpi-v3.0.0
```

To generate containers with Intel compilers, you would need to have an Intel Compiler license. The default
license file is called `license.lic` and can be changed by editing `Dockerfile` (check folders called `intel_mpich` and `intel_openmpi` of this Github repository).

An Intel License is also necessary for running these containers as the NorESM code is being recompiled every time (for each compset and resolution).

## Singularity container

### Pull singularity container

We can then pull the image to generate a singularity image:

```
singularity pull docker://quay.io/nordicesmhub/container-noresm:gnu_mpich-v3.0.0
```

The previous command generates `container-noresm_gnu_mpich-v3.0.0.sif` that is ready to be run on your HPC, desktop/laptop, etc.

### Create NorESM case, compile and prepare input data

We will be using [Betzy](https://documentation.sigma2.no/hpc_machines/betzy.html), the most powerful supercomputer in Norway (2021) and prepare a case for running on one single node e.g. 128 processors. 

The creation, setup and compilation of the case as well as a check of the availability of the necessary of the input data can be done interactively on an interactive node on Betzy. All NorESM/CESM input data can be found in `/cluster/shared/noresm/inputdata` and this is why we are binding this folder to  `/opt/esm/inputdata`. We also want to make sure we can access both the work and archive directories so these two folders are bound to `$USERWORK/work` and `$USERWORK/archive`, respectively. Please note that at this stage only the work directory will be used.

For simplicity and reproducibility, we have put both prepare (preparation of NorESM use case e.g. compilation) and execution scripts in the same batch job.

The script `run-all.bash` is creating automatically all the SLURM batch jobs for each case e.g. number of nodes from 1 to 8 and members from 1 to 10). All the jobs are also submitted by `run-all.bash`.

Below is an example of a SLURM batch job for 8 nodes and an ensemble member (here number 10):

```
#!/bin/bash
#
#SBATCH --account=nn1000k
#SBATCH --job-name=noresm-container_gnu_mpich-v3.0.0_8_10
#SBATCH --time=01:00:00
#SBATCH --nodes=8
#SBATCH --tasks-per-node=128
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
export CASENAME='noresm-gnu-ucx-mpich-container-'$SLURM_JOB_NUM_NODES'x128p-NF2000climo-f19_f19_mg17-10'
echo
#
mkdir -p /opt/uio/noresm-sc2021/work
mkdir -p /opt/uio/noresm-sc2021/archive
mkdir -p /home/centos/.cime

singularity exec --bind /opt/uio/noresm-sc2021/work:/opt/esm/work,/cluster/shared/noresm/inputdata:/opt/esm/inputdata,/opt/uio/noresm-sc2021/archive:/opt/esm/archive container-noresm_gnu_mpich-v3.0.0.sif /opt/esm/prepare

mpirun -np $SLURM_NTASKS singularity exec --bind /opt/uio/noresm-sc2021/work:/opt/esm/work,/cluster/shared/noresm/inputdata:/opt/esm/inputdata,/opt/uio/noresm-sc2021/archive:/opt/esm/archive container-noresm_gnu_mpich-v3.0.0.sif /opt/esm/execute

```

An example of the script `prepare` is available in the container (and also in this repository).

Once finalized, the results of your norESM run is available on betzy in `$USERWORK/archive`.

The timing information (including model cost, throughput, etc.) can be found in a folder called `timing` in the case directory.

All the timings corresponding to the execution of `run-all.bash` can be found in the Github repository [https://github.com/NordicESMhub/noresm-containers-timings](https://github.com/NordicESMhub/noresm-containers-timings) and the folder called `timings`.

