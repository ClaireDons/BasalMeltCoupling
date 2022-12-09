import Freshwater as FW
from glob import iglob


# Define paths
path =  "/ec/res4/scratch/nlcd/CMIP6/bm_coupling/"
mask_path = path + "levermann_masks/"
nc_out = path 
plot_path = path + "plots/"

# Define parameters
filetoolsPath = r'/perm/nlcd/bisicles/BISICLES/code/filetools/'
filetoolFlatten = 'flatten2d.Linux.64.mpiCC.gfortran.DEBUG.MPI.ex'
flatten = filetoolsPath + filetoolFlatten

PenultimateFile = sorted(iglob(plot_path + "*.2d.hdf5"), reverse = True)[1]
LatestFile = sorted(iglob(plot_path + "*.2d.hdf5"), reverse = True)[0]
print(PenultimateFile)
print(LatestFile)


fw = FW.Freshwater(flatten, PenultimateFile, LatestFile)
discharge, basal = fw.RegionalContribution(mask_path,nc_out,flatten)
print(discharge)
print(basal)