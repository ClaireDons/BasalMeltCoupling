"""Freshwater Calculation

This script calculates freshwater input for the Levermann regions,
based on BISICLES output.

This script requires paths to levermann region masks, bisicles plot files,
BISICLES flatten tool.
Requires the Freshwater modules and glob
"""

import Freshwater as FW
from glob import iglob
import pandas as pd


# Define paths
path =  "/ec/res4/scratch/nlcd/CMIP6/bm_coupling/"
mask_path = path + "inputs/levermann_masks/"
nc_out = path + "outputs/plots/nc/"
plot_path = path + "outputs/plots/hdf5/"

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
discharge.to_csv("outputs/csv/discharge.csv", index=False)
basal.to_csv("outputs/csv/basal.csv", index=False)
print(discharge)
print(basal)