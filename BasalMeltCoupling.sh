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
### experiment name and variables
exp_name=COUPLING_TEST
gamma=0.05
bm_name=basal_melt
bm_file=$bm_name.2d.hdf5

### paths
scratch_path=/scratch/nlcd
BISI_INPUT=$scratch_path/bisicles_setup 
outpath=$scratch_path/$exp_name
plots=$outpath/plots/hdf5/

# BISICLES paths + driver and tools
BISICLES_HOME="/perm/nlcd/ecearth3-bisicles/r9411-cmip6-bisicles-knmi/sources/BISICLES"
FLATTEN="$BISICLES_HOME/code/filetools/flatten2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex"
NC2AMR="$BISICLES_HOME/code/filetools/nctoamr2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex"
DRIVER="$BISICLES_HOME/code/exec2D/driver2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex"

### 4. Run basal melt python script    
python3 compute_basalmelt.py $exp_name $gamma $bm_name $scratch_path $NC2AMR ${num} || exit

### 5. Define new basal melt values in input files
COUPLED_TEMPLATE="BISICLES_submission_template.slurm"
export COUPLED=BISICLES_submission.slurm
cp $COUPLED_TEMPLATE $COUPLED

sed -i s+@melt+$bm_file+ $COUPLED
sed -i s+@exp+$exp_name+ $COUPLED
sed -i s+@out+$outpath+ $COUPLED
sed -i s+@driver+$DRIVER+ $COUPLED
sed -i s+@bisi+$BISI_INPUT+ $COUPLED

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
if test -n "$(find $plots -type f -name "plot.$exp_name.??????.2d.hdf5" -print -quit)"
    then
    echo "Found plot, calculating freshwater"
    python3 compute_freshwater.py $exp_name $scratch_path $FLATTEN ${num} || exit
    else
    echo "Something went wrong, no plot"
    exit 
fi

echo "Done!"