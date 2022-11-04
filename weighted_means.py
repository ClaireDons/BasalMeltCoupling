import numpy as np
import xarray as xr
import pandas as pd

import data_variables_parameters as dvp

def area_weighted_mean(ds_var,ds_area,sector):
    '''Compute area weighted mean oceanic temperature over specific oceanic sector
    Args:
        ds_var (xarray dataset): thetao dataset
        ds_area (xarray dataset): areacello dataset
        sector (str): sector name
    Returns:
        area_weighted_mean (dataarray): area weighted mean of thetao
    '''
    mask_sector = dvp.sel_mask(ds_area,sector)
    area_weights = ds_area.areacello
    area_weighted = ds_var.where(mask_sector).weighted(area_weights.fillna(0)) #DataArrayWeighted with weights along dimensions: j, i
    lat = ds_var.dims[2]
    lon = ds_var.dims[3]
    
    try: 
        ((lat=='y') or (lat=='j') or (lat=='lat') or (lat=='latitude')) and ((lon=='x') or (lon=='i') or (lon=='lon') or (lon =='longitude'))
    except:
        print("Check if these dimensions are correct to compute weighted mean")

    area_weighted_mean = area_weighted.mean((lat,lon))
    return area_weighted_mean #2D field: time,levs
    

def nearest_mask(diff):
    """Mask the values outside of target
    Args:
        diff ():
    Returns:
        masked_diff (): 
    """
    mask = np.ma.less_equal(diff, 0)
    if np.all(mask):
        return None # returns None if target is greater than any value
    masked_diff = np.ma.masked_array(diff, mask)
    # Returns the index of the minimum value
    return masked_diff


def nearest_above(my_array, target):
    '''Find nearest value in array that is greater than target value and return corresponding index
    Args:
        my_array ():
        target ():
    Returns:
        masked_diff.argmin() ():
    '''
    diff = my_array - target
    masked_diff = nearest_mask(diff)
    return masked_diff.argmin() 


def nearest_below(my_array, target):
    '''Find nearest value in array that is smaller than target value and return corresponding index
        Args:
        my_array ():
        target ():
    Returns:
        masked_diff.argmin() ():
    '''
    diff = target - my_array
    masked_diff = nearest_mask(diff)
    return masked_diff.argmin()


def lev_weighted_mean(ds,lev_bnds,sector):
    '''Compute volume or depth weighted mean oceanic temperature over specific oceanic
    sector and specific depth layers (centered around ice shelf depth)
    Args:
        ds (xarray dataset): 2D or 3D thetao dataset
        lev_bnds (xarray dataarray): ocean depth bands array
        sector (str): sector name
    Returns:
        levs_weighted_means (float): volume weighted mean of ocean temperature
    '''
   
    # Select depth bounds of sector
    depth_bnds_sector = dvp.sel_depth_bnds(sector)     
    depth_top = depth_bnds_sector[0]
    depth_bottom = depth_bnds_sector[1]
    print(depth_bnds_sector)
    
    # Find oceanic layers covering the depth bounds and take a slice of these
    # layers
    lev_ind_bottom= nearest_above(lev_bnds[:,1],depth_bottom)
    lev_ind_top = nearest_below(lev_bnds[:,0],depth_top)
    levs_slice = ds.isel(lev=slice(lev_ind_top,lev_ind_bottom+1))
    
    # Create weights for each oceanic layer, correcting for layers that fall only partly within specified depth range 
    lev_bnds_sel = lev_bnds.values[lev_ind_top:lev_ind_bottom+1]
    lev_bnds_sel[lev_bnds_sel > depth_bottom] = depth_bottom
    lev_bnds_sel[lev_bnds_sel < depth_top] = depth_top
    # Weight equals thickness of each layer
    levs_weights = lev_bnds_sel[:,1]-lev_bnds_sel[:,0] 
    # DataArray required to apply .weighted on DataArray
    levs_weights_DA = xr.DataArray(levs_weights,coords={'lev': levs_slice.lev},
             dims=['lev'])
    
    # Compute depth weighted mean of ocean slice
    levs_slice_weighted = levs_slice.weighted(levs_weights_DA)
    levs_weighted_mean = levs_slice_weighted.mean(("lev"))
    
    # Return layer-weighted ocean temperature
    return levs_weighted_mean

def weighted_mean_df(area_file, thetao_file, sectors):
    """ Compute volume weighted mean for one year of thetao
    Args:
        area_file (str): file name for file containing areacello data
        thetao_file (str): file name for file containing ocean data
        sectors (list of str): list of sector names
    Returns:
        df (pandas dataframe): dataframe with volume weighted mean for each sector
    """
    # Open thetao dataset
    ds = xr.open_dataset(thetao_file)
    ds_year = ds.groupby('time.year').mean('time') #Compute annual mean
    ds.close()
    area_ds = xr.open_dataset(area_file)

    # Loop over oceanic sectors
    df = pd.DataFrame()
    for sector in sectors:
        # Compute area weighted mean
        #print('Computing area weighted mean of thetao for ', sector, 'sector')           
        thetaoAWM = area_weighted_mean(ds_year["thetao"],area_ds,sector)
        thetaoVWM = lev_weighted_mean(thetaoAWM, ds_year.lev_bnds.mean("year").copy(),sector)
        df[sector] = thetaoVWM

    ds_year.close()
    area_ds.close()
    return df