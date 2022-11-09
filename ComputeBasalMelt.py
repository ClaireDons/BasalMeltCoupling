import BasalMelt as BM

# Define parameters
path = "/net/pc200037/nobackup/users/linden/cmip6data/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3/historical/r1i1p1f1/" 
area_file = path + "Ofx/areacello/gn/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
thetao_file = path + "Omon/thetao/gn/thetao_Omon_EC-Earth3_historical_r1i1p1f1_gn_201401-201412.nc"
gamma = 0.05
name = 'basal_melt'

# Define paths
gen_path = "/nobackup/users/donnelly/"
mask_path = gen_path + "levermann-masks/"
nc_out = gen_path + 'BasalMeltCoupling/'

# Load leverman masks (Maybe in future should just be replaces with coordinates)
driver = '/usr/people/donnelly/bisicles/BISICLES/code/filetools/nctoamr2d.Linux.64.g++.gfortran.DEBUG.ex' # nc to amr hdf5 tool 

# Calculate basal melt
OceanTemp = BM.OceanData(thetao_file,area_file,gamma)
melt = OceanTemp.thetao2basalmelt()

# Open ncfiles and create masks for BISICLES
Levermann = BM.LevermannMask(mask_path,nc_out,driver)
Levermann.map2amr(name,melt)