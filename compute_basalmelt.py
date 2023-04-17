"""Basal Melt Calculation

This script calculates basal melt for the Levermann regions,
based on an EC-Earth ocean temperature file and maps them 
to a BISICLES AMR file

This script requires paths to EC-Earth area and ocean temperature files,
path to levermann region maks, chosen gamma value and path to bisisles nc2amr tool.
Requires the BasalMelt module.
"""

import os
from FwCoupling import basal_melt as BM

# Define parameters
PATH = os.path.dirname(os.path.realpath(__file__))
SCRATCH = "/scratch/nlcd/"
PERM = "/perm/nlcd/"
EXP_NAME = "COUPLING_TEST"
BISICLES_HOME = PERM + "ecearth3-bisicles/r9411-cmip6-bisicles-knmi/sources/BISICLES/"

AREA_FILE = (
    PATH + "/inputs/ec-earth_data/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
)
THETAO_FILE = (
    PATH
    + "/inputs/ec-earth_data/thetao_Omon_EC-Earth3_historical_r1i1p1f1_gn_201401-201412.nc"
)
GAMMA = 0.05
NAME = "basal_melt"

# Define paths
MASK_PATH = PATH + "/inputs/levermann_masks/"
NC_OUT = SCRATCH + EXP_NAME + "/plots/nc/"
PLOT_PATH = SCRATCH + EXP_NAME + "/plots/hdf5/"
CSV_OUT = SCRATCH + EXP_NAME + "/csv/"
CHK_OUT = SCRATCH + EXP_NAME + "/checkpoints/"

# Load leverman masks (Maybe in future should just be replaces with coordinates)
DRIVER = (
    BISICLES_HOME
    + "code/filetools/nctoamr2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex"
)


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
    OCEAN_TEMP.map_basalmelt(MASK_PATH, PATH + "/", DRIVER, NAME)

    print("Basal Melt Calculated")
