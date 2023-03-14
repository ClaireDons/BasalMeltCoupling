"""Basal Melt Calculation

This script calculates basal melt for the Levermann regions,
based on an EC-Earth ocean temperature file and maps them 
to a BISICLES AMR file

This script requires paths to EC-Earth area and ocean temperature files,
path to levermann region maks, chosen gamma value and path to bisisles nc2amr tool.
Requires the BasalMelt module.
"""

import BasalMelt as BM

# Define parameters
path = "/ec/res4/scratch/nlcd/CMIP6/bm_coupling/"
area_file = path + "inputs/ec-earth_data/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
thetao_file = path + "inputs/ec-earth_data/thetao_Omon_EC-Earth3_historical_r1i1p1f1_gn_201401-201412.nc"
gamma = 0.05
name = 'basal_melt'

# Define paths
mask_path = path + "inputs/levermann_masks/"
nc_out = path

# Load leverman masks (Maybe in future should just be replaces with coordinates)
driver = '/perm/nlcd/ecearth3-bisicles/r9411-cmip6-bisicles-knmi/sources/BISICLES/code/filetools/nctoamr2d.Linux.64.mpiCC.mpif90.DEBUG.OPT.MPI.PETSC.ex' # nc to amr hdf5 tool 

# Calculate basal melt
OceanTemp = BM.BasalMelt(thetao_file,area_file,gamma)
OceanTemp.mapBasalMelt(mask_path,nc_out,driver,name)

print("Basal Melt Calculated")