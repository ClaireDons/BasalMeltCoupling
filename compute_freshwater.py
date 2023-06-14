"""Freshwater Calculation

This script calculates freshwater input for the Levermann regions,
based on BISICLES output.

This script requires paths to levermann region masks, bisicles plot files,
BISICLES flatten tool.
Requires the Freshwater modules and glob
"""

import sys
from glob import iglob
from freshwater_coupling import freshwater as FW

# Define parameters
EXP_NAME = str(sys.argv[1])

# Define paths
PATH = str(sys.argv[2]) + "/BasalMeltCoupling"
MASK_PATH = PATH + "/inputs/levermann_masks/"
FLATTEN = str(sys.argv[3])

AREA_FILE = (
    PATH + "/inputs/ec-earth_data/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
)

DISTRIBUTION_FILE = PATH + "/inputs/ec-earth_data/FriverDistributionMask_AIS_ORCA1.nc"

OUTPATH = str(sys.argv[4])
NC_OUT = OUTPATH + "/plots/nc/"
PLOT_PATH = OUTPATH + "/plots/hdf5/"
CSV_OUT = OUTPATH + "/csv/"

NEMO_PATH = str(sys.argv[5])
THETAO_FILE = sorted(iglob(NEMO_PATH + "*_grid_T_3D.nc"))[0]

if __name__ == "__main__":
    PENULTIMATE_FILE = sorted(iglob(PLOT_PATH + "*.2d.hdf5"), reverse=True)[1]
    LATEST_FILE = sorted(iglob(PLOT_PATH + "*.2d.hdf5"), reverse=True)[0]
    print(PENULTIMATE_FILE, LATEST_FILE) # Test here instead

    FRESHWATER = FW.Freshwater(FLATTEN, PENULTIMATE_FILE, LATEST_FILE)
    DISCHARGE, BASAL = FRESHWATER.regional_contribution(MASK_PATH, NC_OUT, FLATTEN)
    DISCHARGE.to_csv(CSV_OUT + "discharge.csv", index=False)
    BASAL.to_csv(CSV_OUT + "basal.csv", index=False)
    print(DISCHARGE, BASAL) # Test here instead

    FWF_FILE = FRESHWATER.calculate_nemo_forcing(
        DISCHARGE, BASAL, AREA_FILE, DISTRIBUTION_FILE, THETAO_FILE
    )
    print(FWF_FILE)
    FWF_FILE.to_netcdf(
        CSV_OUT + "freshwater_forcing.nc", unlimited_dims=["time_counter"]
    )
