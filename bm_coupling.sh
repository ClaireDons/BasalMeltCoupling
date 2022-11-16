#!/bin/bash -l

module load prgenv/gnu
module load python3/3.8.8-01
module load gcc/11.2.0
module load openmpi/4.1.1.1
module load hdf5-parallel/1.10.6
module load netcdf4-parallel/4.7.4

export PYTHONPATH=`pwd`
export LD_LIBRARY_PATH=$HDF5_PARALLEL_DIR/lib:$PYTHON3_DIR/lib:$LD_LIBRARY_PATH

### 1. Check for last plot file, if one exists, take most recent one and flatten to NetCDF.

n=coupled_bm
NC_PLOT=plot.$n.nc
plots=/ec/res4/scratch/nlcd/CMIP6/bm_coupling/plots/
FLATTEN="/perm/nlcd/bisicles/BISICLES/code/filetools/flatten2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex"
SH_BISICLES="bisicles_coupledbm.sh"


if test -n "$(find $plots -type f -name "plot.$n.??????.2d.hdf5" -print -quit)"
    then
    echo "Found plot"
    LPLOT=`ls -th plots/plot.$n.??????.2d.hdf5 | head -n 1`
    # Flatten the plot
    $FLATTEN $LPLOT $NC_PLOT 0 -3333500 -3333500
    # Pass on new fields to input file
    echo "$NC_PLOT"
fi

### 2. Run basal melt python script
python3 ComputeBasalMelt.py

### 3. Define new basal melt values in input file
bm=basal_melt.2d.hdf5 

### 4. Run BISICLES and stop once 1 plot file has been created
sbatch bisicles_coupledbm.sh