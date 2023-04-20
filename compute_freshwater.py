"""Freshwater Calculation

This script calculates freshwater input for the Levermann regions,
based on BISICLES output.

This script requires paths to levermann region masks, bisicles plot files,
BISICLES flatten tool.
Requires the Freshwater modules and glob
"""

import os
import sys
from glob import iglob
from freshwater_coupling import freshwater as FW

# Define parameters
EXP_NAME = str(sys.argv[1])

# Define paths
PATH = os.path.dirname(os.path.realpath(__file__))
SCRATCH = str(sys.argv[2]) + "/"
FLATTEN = str(sys.argv[3])


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
