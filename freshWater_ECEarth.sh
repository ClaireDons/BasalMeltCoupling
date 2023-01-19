#!/bin/bash -l

module load prgenv/gnu
module load python3/3.8.8-01
module load gcc/11.2.0
module load openmpi/4.1.1.1
module load hdf5-parallel/1.10.6
module load netcdf4-parallel/4.7.4

export PYTHONPATH=`pwd`
export LD_LIBRARY_PATH=$HDF5_PARALLEL_DIR/lib:$PYTHON3_DIR/lib:$LD_LIBRARY_PATH

n=coupled_bm
plots=/ec/res4/scratch/nlcd/CMIP6/bm_coupling/plots/hdf5/


### 1. Check whether plot files exist, if they do run python script
if test -n "$(find $plots -type f -name "plot.$n.??????.2d.hdf5" -print -quit)"
    then
    echo "Found plot"
    python3 ComputeFreshwater.py ${num} || exit
fi

### 2. Input BISICLES data into EC-Earth
### 3. Run EC-Earth