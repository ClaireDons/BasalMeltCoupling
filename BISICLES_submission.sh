#!/bin/bash -l
#SBATCH -J testrun
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

# Define driver 
export DRIVER=/perm/nlcd/bisicles/BISICLES/code/exec2D/driver2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex

# Define input files
export INFILEBASE="inputs.setup"
export INFILE=inputs.setup.$SLURM_JOBID
echo "INFILE = $INFILE"
cp $INFILEBASE $INFILE

n=coupled_bm
checkpoints=/ec/res4/scratch/nlcd/CMIP6/bm_coupling/checkpoints
bm=basal_melt.2d.hdf5

count=$(find checkpoints/chk.* -maxdepth 1 -type f|wc -l)
echo $count
let count=count+1 # Increase by one, for the next file number
echo $count

sed -i s/@NAME/$n/ $INFILE
sed -i s/@BM_DATA/$bm/ $INFILE
sed -i s/@TIME/$count/ $INFILE

export PYTHONPATH=`pwd`
export LD_LIBRARY_PATH=$HDF5_PARALLEL_DIR/lib:$PYTHON3_DIR/lib:$LD_LIBRARY_PATH
export CH_OUTPUT_INTERVAL=0

 # work out what the latest checkpoint file is (if it exists)
if test -n "$(find $checkpoints -type f -name "chk.$n.??????.2d.hdf5" -print -quit)"
    then
    LCHK=`ls checkpoints/chk.coupled_bm.??????.2d.hdf5 | tail -n 1`
    echo "" >> $INFILE #ensure line break
    echo "amr.restart_file=$LCHK" >> $INFILE
    echo "amr.restart_set_time=false" >> $INFILE
    echo "" >> $INFILE #ensure line break
fi

srun $DRIVER $INFILE