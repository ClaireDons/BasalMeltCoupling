import Freshwater as FW

# Define parameters
path = "/nobackup/users/donnelly/BasalMeltCoupling/"

# Define paths
mask_path = "/nobackup/users/donnelly/levermann-masks"
nc_out = path

# Load leverman masks (Maybe in future should just be replaces with coordinates)
driver = '/perm/nlcd/bisicles/BISICLES/code/filetools/nctoamr2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex' # nc to amr hdf5 tool 