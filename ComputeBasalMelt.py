import BasalMelt as BM

# Define parameters
path = "/ec/res4/scratch/nlcd/CMIP6/bm_coupling/"
area_file = path + "ec-earth_data/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
thetao_file = path + "ec-earth_data/thetao_Omon_EC-Earth3_historical_r1i1p1f1_gn_201401-201412.nc"
gamma = 0.05
name = 'basal_melt'

# Define paths
mask_path = path + "levermann_masks/"
nc_out = path

# Load leverman masks (Maybe in future should just be replaces with coordinates)
driver = '/perm/nlcd/bisicles/BISICLES/code/filetools/nctoamr2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex' # nc to amr hdf5 tool 

# Calculate basal melt
OceanTemp = BM.BasalMelt(thetao_file,area_file,gamma)
melt = OceanTemp.thetao2basalmelt()


# Open ncfiles and create masks for BISICLES
Levermann = BM.LevermannMask(mask_path,nc_out,driver)
Levermann.map2amr(name,melt)
print("Basal Melt Calculated")