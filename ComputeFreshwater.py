import Freshwater as FW
from glob import iglob


# Define paths
path =  "/nobackup/users/donnelly/Antarctica/ssp585/shelfbasedepth/"
mask_path = "/nobackup/users/donnelly/levermann-masks/"
nc_out = "/nobackup/users/donnelly/BasalMeltCoupling/"

# Define parameters
filetoolsPath = r'/usr/people/donnelly/bisicles/BISICLES/code/filetools/'
filetoolFlatten = 'flatten2d.Linux.64.g++.gfortran.DEBUG.ex'
flatten = filetoolsPath + filetoolFlatten

LatestFile = sorted(iglob(path + "*.2d.hdf5"), reverse = True)[0]
PenultimateFile = sorted(iglob(path + "*.2d.hdf5"), reverse = True)[1]

fw = FW.Freshwater(flatten, PenultimateFile, LatestFile)
discharge, basal = fw.RegionalContribution(mask_path,nc_out,flatten)
print(discharge)
print(basal)