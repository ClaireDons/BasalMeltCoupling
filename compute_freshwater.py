"""Freshwater Calculation

This script calculates freshwater input for the Levermann regions,
based on BISICLES output.

This script requires paths to levermann region masks, bisicles plot files,
BISICLES flatten tool.
Requires the Freshwater modules and glob
"""

import os
from glob import iglob
from FwCoupling import freshwater as FW


# Define paths
PATH = os.path.dirname(os.path.realpath(__file__))
SCRATCH = "/scratch/nlcd/"
PERM = "/perm/nlcd/"
EXP_NAME = "COUPLING_TEST"
BISICLES_HOME = (
    PERM + "ecearth3-bisicles/r9411-cmip6-bisicles-knmi/sources/BISICLES/"
)

# Define parameters
FILETOOLS_PATH = BISICLES_HOME + "code/filetools/"
FILETOOLS_FLATTEN = "flatten2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex"
FLATTEN = FILETOOLS_PATH + FILETOOLS_FLATTEN


MASK_PATH = PATH + "/inputs/levermann_masks/"
NC_OUT = SCRATCH + EXP_NAME + "/plots/nc/"
PLOT_PATH = SCRATCH + EXP_NAME + "/plots/hdf5/"
CSV_OUT = SCRATCH + EXP_NAME + "/csv/"

if __name__ == "__main__":
    PENULTIMATE_FILE = sorted(iglob(PLOT_PATH + "*.2d.hdf5"), reverse=True)[1]
    LATEST_FILE = sorted(iglob(PLOT_PATH + "*.2d.hdf5"), reverse=True)[0]
    print(PENULTIMATE_FILE)
    print(LATEST_FILE)

    FRESHWATER = FW.Freshwater(FLATTEN, PENULTIMATE_FILE, LATEST_FILE)
    DISCHARGE, BASAL = FRESHWATER.regional_contribution(MASK_PATH, NC_OUT, FLATTEN)
    DISCHARGE.to_csv(CSV_OUT + "discharge.csv", index=False)
    BASAL.to_csv(CSV_OUT + "basal.csv", index=False)
    print(DISCHARGE)
    print(BASAL)
