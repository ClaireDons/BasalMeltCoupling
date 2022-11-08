import numpy as np
from glob import glob
import os
import xarray as xr
import pandas as pd

#import weighted_means as comp
import BasalMelt as BM
import AntarcticaSectors as AS

# Define parameters
path = "/net/pc200037/nobackup/users/linden/cmip6data/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3/historical/r1i1p1f1/" 
area_file = path + "Ofx/areacello/gn/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
thetao_file = path + "Omon/thetao/gn/thetao_Omon_EC-Earth3_historical_r1i1p1f1_gn_201401-201412.nc"
sectors = ['eais','wedd','amun','ross','apen']
gamma = 0.05
Tf = -1.6
baseline = 1

# Define paths
gen_path = "/nobackup/users/donnelly/"
mask_path = gen_path + "levermann-masks/"
nc_out = gen_path + 'BasalMeltCoupling/'

# Load leverman masks (Maybe in future should just be replaces with coordinates)
nc_files = glob(os.path.join(mask_path, "*.2d.nc")) # sector masks
driver = '/usr/people/donnelly/bisicles/BISICLES/code/filetools/nctoamr2d.Linux.64.g++.gfortran.DEBUG.ex' # nc to amr hdf5 tool 

# Open ncfiles and create masks for BISICLES
for file in nc_files:
    key = os.path.splitext(os.path.basename(file))[0][15:-3]
    name = 'smask' + str(key)
    dat = xr.open_dataset(file)
    globals()['smask' + str(key)] = np.array(dat['smask'])

x = np.array(dat['x'])
y = np.array(dat['y'])

# Calculate volume weighted mean
OceanTemp = AS.OceanData(thetao_file,area_file)
df = OceanTemp.weighted_mean_df()
#df = comp.weighted_mean_df(area_file, thetao_file, sectors)

# Calculate basal melt
df2 =  pd.DataFrame()
for column in df:
    thetao = df[column].values
    b = BM.BasalMelt(gamma, thetao)
    dBM = b.quadBasalMeltAnomalies()
    df2[column]=dBM
print(df2)

# Write out to nc and hdf5
for i, row in df2.iterrows():
    name = "basal_melt"
    new_mask = np.where(smask1 == 1, row.apen, smask1)
    new_mask = np.where(smask2 == 1, row.amun, new_mask)
    new_mask = np.where(smask3 == 1, row.ross, new_mask)
    new_mask = np.where(smask4 == 1, row.eais, new_mask)
    new_mask = np.where(smask5 == 1, row.wedd, new_mask)
    da = xr.DataArray(data= new_mask, coords=[("x", x),("y",y)], name="bm")
    da.to_netcdf(nc_out+ name + '.nc')
    os.system(driver + " " + nc_out + name + ".nc " + nc_out + name + ".2d.hdf5 bm")
