#!/bin/bash -l

module load python3/3.8.8-01

### 1. Check for last plot file, if one exists, take most recent one and flatten to NetCDF, 
###    If no plot file then use time=0 values

n=coupled_bm
NC_PLOT=plot.$n.nc
FLATTEN="/perm/nlcd/bisicles/BISICLES/code/filetools/flatten2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex"
SH_BISICLES="bisicles_coupledbm.sh"


if test -n "$(find -type f -name "plot.$n.??????.2d.hdf5" -print -quit)"
    then
    echo "Found plot"
    LPLOT=`ls -th plot.$n.??????.2d.hdf5 | head -n 1`
    # Flatten the plot
    $FLATTEN $LPLOT $NC_PLOT 0 0 0
    # Pass on new fields to input file
    echo "$NC_PLOT"
fi

### 2. Run basal melt python script

### 3. Define new basal melt values in input file

### 4. Run BISICLES and stop once 1 plot file has been created
sbatch bisicles_coupledbm.sh