# container-noresm

Containers (docker &amp; singularity) for NorESM, the Norwegian Earth System Model.

[![DOI](https://zenodo.org/badge/355181297.svg)](https://zenodo.org/badge/latestdoi/355181297)

## hpccm to create Dockerfile and associated containers

We use [HPC Container Maker](https://github.com/NVIDIA/hpc-container-maker)  (HPCCM - pronounced H-P-see-M), an open source tool to easily generate container specification files.

```
 hpccm --recipe noresm_gnu.py --format docker > Dockerfile
```

## Docker containers

#### GNU MPICH and OpenMPI containers

The docker GNU containers (GNU-MPICH & GNU-OpenMPI) are automatically generated (github actions) and pushed to [quay.io](https://quay.io/):

```
docker pull quay.io/nordicesmhub/container-noresm:gnu_mpich-v3.0.0
```

or 

```
docker pull quay.io/nordicesmhub/container-noresm:gnu_openmpi-v3.0.0
```

#### Intel MPICH and OpenMPI containers

To generate containers with Intel compilers, you would need to have an Intel Compiler license. The default
license file is called `license.lic` and can be changed by editing `Dockerfile` (check folders called `intel_mpich` and `intel_openmpi` of this Github repository). For creating the containers, first clone this repository:

```
git clone https://github.com/NordicESMhub/container-noresm
```

Then change directory:

```
cd container-noresm
```

##### Intel OpenMPI container

To successfully build a container with Intel Compiler and OpenMPI, please add your Intel Compiler license (`license.lic`) in the `intel-openmpi` folder:

```
cd intel-openmpi

docker build . -t  quay.io/nordicesmhub/container-noresm:intel_openmpi-v3.0.0
```

##### Intel MPICH container

To successfully build a container with Intel Compiler and MPICH, please add your Intel Compiler license (`license.lic`) in the `intel-mpich` folder:

```
cd intel-mpich

docker build . -t  quay.io/nordicesmhub/container-noresm:intel_mpich-v3.0.0
```

### Creating and building NorESM containers with Intel compilers

An **Intel License is also necessary for running these containers** as the NorESM code is being recompiled every time (depends on the each compset, resolution, number of processors and number of processors per node).


## Singularity container

### Pull singularity container

To pull the image from quay.io and generate a singularity image:

```
singularity pull docker://quay.io/nordicesmhub/container-noresm:gnu_mpich-v3.0.0
```

The previous command generates `container-noresm_gnu_mpich-v3.0.0.sif` that is ready to be run on your HPC, desktop/laptop, etc.

### Create NorESM case, compile and prepare input data

We will be using [Betzy](https://documentation.sigma2.no/hpc_machines/betzy.html), the most powerful supercomputer in Norway (2021) and prepare a case for running on nodes with 128 processors per node. 

The creation, setup and compilation of the case as well as a check of the availability of the necessary of the input data can be done interactively on an interactive node (here on Betzy). On Betzy, all NorESM/CESM input data can be found in `/cluster/shared/noresm/inputdata` and this is why we are binding this folder to  `/opt/esm/inputdata`. However, input data can be downloaded automatically when preparing the case (`prepare` script) according your machine has an access to internet to download data (by default via `wget`).  We also want to make sure we can access both the work and archive directories so these two folders are bound to `$USERWORK/work` and `$USERWORK/archive`, respectively. `USERWORK` is an environment variable that is predefined on Betzy; if running on another platform, make sure to define this environment variable yourself. Please note that at this stage only the work directory will be used.

For simplicity and reproducibility, we have put both prepare (preparation of NorESM use case e.g. compilation) and execution scripts in the same batch job.

The script `run-all.bash` is creating automatically all the SLURM batch jobs for each case e.g. number of nodes from 1 to 8 and members from 1 to 10). All the jobs are also submitted by `run-all.bash`.

Below is an example of a SLURM batch job for 8 nodes (128 processors per node) and one member (here number 10) of an ensemble run (one SLURM job is submitted per member for NorESM when running in ensemble mode):

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

An example of the script `prepare` is available in the containers (and also in this repository).

Once finalized, the results of your norESM run is available on betzy in `$USERWORK/archive`.

The timing information (including model cost, throughput, etc.) can be found in a folder called `timing` in the case directory. 


