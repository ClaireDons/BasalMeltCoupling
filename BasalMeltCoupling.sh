#!/bin/bash

# 1. Load relevant modules
module load prgenv/gnu
module load python3/3.8.8-01
module load gcc/11.2.0
module load openmpi/4.1.1.1
module load hdf5-parallel/1.10.6
module load netcdf4-parallel/4.7.4

# 2. Export correct paths to python
export PYTHONPATH=`pwd`
export LD_LIBRARY_PATH=$HDF5_PARALLEL_DIR/lib:$PYTHON3_DIR/lib:$LD_LIBRARY_PATH

# 3. Define names and paths needed
n=coupled_bm
NC_PLOT=plot.$n.nc
plots=/ec/res4/scratch/nlcd/CMIP6/BasalMeltCoupling/outputs/plots/hdf5/
FLATTEN="/perm/nlcd/bisicles/BISICLES/code/filetools/flatten2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex"
SH_BISICLES="BISICLES_submission_template.slurm"
bm=basal_melt.2d.hdf5 

### 4. Run basal melt python script    
python3 ComputeBasalMelt.py ${num} || exit

### 5. Define new basal melt values in input files
export COUPLED=BISICLES_submission.slurm
cp $SH_BISICLES $COUPLED
sed -i s/@melt/$bm/ $COUPLED

# 6. Get job id and wait for BISICLES to finish running
jid=$(sbatch BISICLES_submission.slurm| cut -d ' ' -f4)
echo $jid
echo "waiting for BISICLES..."
until test -f "$jid.txt"
do
    sleep 60
done
rm $jid.txt
echo "...BISICLES done!"

# 7. Check whether plot files exist, if they do calculate freshwater
if test -n "$(find $plots -type f -name "plot.$n.??????.2d.hdf5" -print -quit)"
    then
    echo "Found plot, calculating freshwater"
    python3 ComputeFreshwater.py ${num} || exit
    else
    echo "Something went wrong, no plot"
    exit 
fi

echo "Done!"