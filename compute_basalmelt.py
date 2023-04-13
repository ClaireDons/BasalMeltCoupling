"""Basal Melt Calculation

This script calculates basal melt for the Levermann regions,
based on an EC-Earth ocean temperature file and maps them 
to a BISICLES AMR file

This script requires paths to EC-Earth area and ocean temperature files,
path to levermann region maks, chosen gamma value and path to bisisles nc2amr tool.
Requires the BasalMelt module.
"""

from FwCoupling import basal_melt as BM

# Define parameters
PATH = "/ec/res4/scratch/nlcd/CMIP6/BasalMeltCoupling/"
AREA_FILE = (
    PATH + "inputs/ec-earth_data/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
)
THETAO_FILE = (
    PATH
    + "inputs/ec-earth_data/thetao_Omon_EC-Earth3_historical_r1i1p1f1_gn_201401-201412.nc"
)
GAMMA = 0.05
NAME = "basal_melt"

# Define paths
MASK_PATH = PATH + "inputs/levermann_masks/"
NC_OUT = PATH

# Load leverman masks (Maybe in future should just be replaces with coordinates)
BISICLES_HOME = (
    "/perm/nlcd/ecearth3-bisicles/r9411-cmip6-bisicles-knmi/sources/BISICLES/"
)
DRIVER = (
    BISICLES_HOME
    + "code/filetools/nctoamr2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex"
)

# Calculate basal melt
if __name__ == "__main__":
    OCEAN_TEMP = BM.BasalMelt(THETAO_FILE, AREA_FILE, GAMMA)
    OCEAN_TEMP.map_basalmelt(MASK_PATH, NC_OUT, DRIVER, NAME)

    print("Basal Melt Calculated")
