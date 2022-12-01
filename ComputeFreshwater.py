import Freshwater as FW


# Define parameters
path = "/nobackup/users/donnelly/BasalMeltCoupling/"

filetoolsPath = r'/usr/people/donnelly/bisicles/BISICLES/code/filetools/'
filetoolFlatten = 'flatten2d.Linux.64.g++.gfortran.DEBUG.ex'

flatten = filetoolsPath + filetoolFlatten

file_path1 = "/nobackup/users/donnelly/Antarctica/ssp585/shelfbasedepth/plot.ssp585_shelfbase.000061.2d.hdf5"
file_path2 = "/nobackup/users/donnelly/Antarctica/ssp585/shelfbasedepth/plot.ssp585_shelfbase.000120.2d.hdf5"

# Define paths
mask_path = "/nobackup/users/donnelly/levermann-masks/"
nc_out = path

# Load leverman masks (Maybe in future should just be replaces with coordinates)
driver = '/perm/nlcd/bisicles/BISICLES/code/filetools/nctoamr2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex' # nc to amr hdf5 tool 


fw = FW.Freshwater(flatten, file_path1, file_path2)
discharge, basal = fw.RegionalContribution(mask_path,nc_out,flatten)
print(discharge)
print(basal)