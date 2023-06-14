"""Basal Melt Calculation

This script calculates basal melt for the Levermann regions,
based on an EC-Earth ocean temperature file and maps them 
to a BISICLES AMR file

This script requires paths to EC-Earth area and ocean temperature files,
path to levermann region maks, chosen gamma value and path to bisisles nc2amr tool.
Requires the BasalMelt module.
"""

import os
import sys
from glob import iglob
from freshwater_coupling import basal_melt as BM

# Define parameters
EXP_NAME = str(sys.argv[1])
GAMMA = float(sys.argv[2])
NAME = str(sys.argv[3])

# Define Paths
PATH = str(sys.argv[4]) + "/BasalMeltCoupling"
MASK_PATH = PATH + "/inputs/levermann_masks/"

OUTPATH = str(sys.argv[5]) + "/"
NC_OUT = OUTPATH + "/plots/nc/"
PLOT_PATH = OUTPATH + "/plots/hdf5/"
CSV_OUT = OUTPATH + "/csv/"
CHK_OUT = OUTPATH + "/checkpoints/"

AREA_FILE = (
    PATH + "/inputs/ec-earth_data/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
)

NEMO_PATH = str(sys.argv[6])
THETAO_FILE = sorted(iglob(NEMO_PATH + "*_grid_T_3D.nc"))[0]

# Load leverman masks (Maybe in future should just be replaces with coordinates)
DRIVER = str(sys.argv[7])

def new_path(path_name):
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    return path_name


# Calculate basal melt
if __name__ == "__main__":
    OUTPUT_NC = new_path(NC_OUT)
    OUTPUT_PLOT = new_path(PLOT_PATH)
    OUTPUT_CSV = new_path(CSV_OUT)
    OUTPUT_CHK = new_path(CHK_OUT)
    OCEAN_TEMP = BM.BasalMelt(THETAO_FILE, AREA_FILE, GAMMA)
    OCEAN_TEMP.map_basalmelt(MASK_PATH, OUTPATH, DRIVER, NAME)

    print("Basal Melt Calculated")
