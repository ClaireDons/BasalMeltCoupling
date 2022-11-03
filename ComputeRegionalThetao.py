import numpy as np
import pandas as pd
import xarray as xr

import func_data_variables_parameters as dvp
import func_weighted_means as comp

area_file = "area_file"
file_thetao = "thetao_file"
data_dir  = '/ESM_data/'
sectors = ['eais','wedd','amun','ross','apen']

# Open thetao dataset
ds = xr.open_dataset(file_thetao)
ds_year = ds.groupby('time.year').mean('time') #Compute annual mean
ds.close()

# Loop over oceanic sectors
for sector in sectors:

    print(sector)
    area_ds = xr.open_dataset(area_file)

    # Compute area weighted mean
    print('Computing area weighted mean of thetao for ', sector, 'sector')           
    thetao_area_weighted_mean = comp.area_weighted_mean(ds_year["thetao"],area_ds,sector)
    thetao_volume_weighted_mean = comp.lev_weighted_mean(thetao_area_weighted_mean, ds_year.lev_bnds.mean("year").copy(),sector)
    print(thetao_volume_weighted_mean)

    ds_year.close()
    area_ds.close()