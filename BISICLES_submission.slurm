#!/bin/bash -l
#SBATCH -J bisicles
#SBATCH -q np
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=128
#SBATCH -t 00:30:00

module load prgenv/gnu
module load python3/3.8.8-01
module load gcc/11.2.0
module load openmpi/4.1.1.1
module load hdf5-parallel/1.10.6
module load netcdf4-parallel/4.7.4

start_dir=/etc/ecmwf/nfs/dh2_perm_b/nlcd/ecearth3-bisi/r9469-cmip6-bisi-knmi/runtime/classic

# Define driver 
export DRIVER=/perm/nlcd/ecearth3-bisicles/r9411-cmip6-bisicles-knmi/sources/BISICLES/code/exec2D/driver2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex
# Define input files
export INFILEBASE="$start_dir/BasalMeltCoupling/inputs.ECEbasal"
export INFILE=$start_dir/BasalMeltCoupling/inputs.ECEbasal.$SLURM_JOBID
echo "INFILE = $INFILE"
cp $INFILEBASE $INFILE

expname=TST2
bisi_input=/scratch/nlcd/bisicles_setup
outpath=/ec/res4/scratch/nlcd/r9469-cmip6-bisi-knmi/TST2/output/bisicles
checkpoints=$outpath/checkpoints
plots=$outpath/plots/hdf5
bm=$outpath/basal_melt.2d.hdf5


sed -i s+@EXP+$expname+ $INFILE
sed -i s+@OUT+$outpath+ $INFILE
sed -i s+@BM_DATA+$bm+ $INFILE
sed -i s+@BISI_INPUT+$bisi_input+ $INFILE

# Count the number of checkpoints to increase time to run to incrementally 
# Test that number of plots is equal to count
count=$(find $checkpoints/chk.* -maxdepth 1 -type f|wc -l)
plot_count=$(find $plots/plot.* -maxdepth 1 -type f|wc -l)

if test $count -eq 0
then
    let count=count+1
    sed -i s+@TIME+$count+ $INFILE
else
    let count=count # Increase by one, for the next file number
    sed -i s+@TIME+$count+ $INFILE
    if test $plot_count -ne $count
    then
        echo "Number of plots not equal to number of checkpoints, exiting"
        exit
    fi
    # If check point is found, get the latest and add it for restart
    echo "Checkpoint found"
    LCHK=`ls $checkpoints/chk.$expname.??????.2d.hdf5 | tail -n 1`
    echo "" >> $INFILE #ensure line break
    echo "amr.restart_file=$LCHK" >> $INFILE
    echo "amr.restart_set_time=false" >> $INFILE
    echo "" >> $INFILE #ensure line break
fi 


export PYTHONPATH=`pwd`
export LD_LIBRARY_PATH=$HDF5_PARALLEL_DIR/lib:$PYTHON3_DIR/lib:$LD_LIBRARY_PATH
export CH_OUTPUT_INTERVAL=0

echo "Calculating timestep $count"

srun $DRIVER $INFILE > $start_dir/BasalMeltCoupling/pout.0 2>$start_dir/BasalMeltCoupling/err.0
touch $start_dir/BasalMeltCoupling/$SLURM_JOBID.txt