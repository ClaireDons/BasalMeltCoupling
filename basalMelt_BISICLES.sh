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
NC_PLOT=plot.$n.nc
plots=/ec/res4/scratch/nlcd/CMIP6/bm_coupling/outputs/plots/hdf5/
FLATTEN="/perm/nlcd/bisicles/BISICLES/code/filetools/flatten2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex"
SH_BISICLES="BISICLES_submission_template.sh"
bm=basal_melt.2d.hdf5 

### 1. Run basal melt python script    
python3 code/ComputeBasalMelt.py ${num} || exit

### 2. Define new basal melt values in input file
export COUPLED=BISICLES_submission.sh
echo "COUPLED = $COUPLED"
cp $SH_BISICLES $COUPLED
sed -i s/@melt/$bm/ $COUPLED


### 3. Run BISICLES and stop once 1 plot file has been created
sbatch $COUPLED