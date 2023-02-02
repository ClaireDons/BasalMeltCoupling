#!/bin/bash -l
#SBATCH -J freshwater
#SBATCH -q np
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=4
#SBATCH -t 00:01:00

# 1. Load relevant modules
module load prgenv/gnu
module load python3/3.8.8-01
module load gcc/11.2.0
module load openmpi/4.1.1.1
module load hdf5-parallel/1.10.6
module load netcdf4-parallel/4.7.4

# 2. Export paths to correct python
export PYTHONPATH=`pwd`
export LD_LIBRARY_PATH=$HDF5_PARALLEL_DIR/lib:$PYTHON3_DIR/lib:$LD_LIBRARY_PATH

# 3. Define names and paths
n=coupled_bm
plots=/ec/res4/scratch/nlcd/CMIP6/bm_coupling/outputs/plots/hdf5/


# 4. Check whether plot files exist, if they do run python script
if test -n "$(find $plots -type f -name "plot.$n.??????.2d.hdf5" -print -quit)"
    then
    echo "Found plot"
    python3 code/ComputeFreshwater.py ${num} || exit
fi