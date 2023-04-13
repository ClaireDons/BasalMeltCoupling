"""Freshwater Calculation

This script calculates freshwater input for the Levermann regions,
based on BISICLES output.

This script requires paths to levermann region masks, bisicles plot files,
BISICLES flatten tool.
Requires the Freshwater modules and glob
"""

from glob import iglob
from FwCoupling import freshwater as FW


# Define paths
PATH = "/ec/res4/scratch/nlcd/CMIP6/BasalMeltCoupling/"
MASK_PATH = PATH + "inputs/levermann_masks/"
NC_OUT = PATH + "outputs/plots/nc/"
PLOT_PATH = PATH + "outputs/plots/hdf5/"

# Define parameters
BISICLES_HOME = (
    "/perm/nlcd/ecearth3-bisicles/r9411-cmip6-bisicles-knmi/sources/BISICLES/"
)
FILETOOLS_PATH = BISICLES_HOME + "code/filetools/"
FILETOOLS_FLATTEN = "flatten2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex"
FLATTEN = FILETOOLS_PATH + FILETOOLS_FLATTEN


if __name__ == "__main__":
    PENULTIMATE_FILE = sorted(iglob(PLOT_PATH + "*.2d.hdf5"), reverse=True)[1]
    LATEST_FILE = sorted(iglob(PLOT_PATH + "*.2d.hdf5"), reverse=True)[0]
    print(PENULTIMATE_FILE)
    print(LATEST_FILE)

    FRESHWATER = FW.Freshwater(FLATTEN, PENULTIMATE_FILE, LATEST_FILE)
    DISCHARGE, BASAL = FRESHWATER.regional_contribution(MASK_PATH, NC_OUT, FLATTEN)
    DISCHARGE.to_csv("outputs/csv/discharge.csv", index=False)
    BASAL.to_csv("outputs/csv/basal.csv", index=False)
    print(DISCHARGE)
    print(BASAL)
