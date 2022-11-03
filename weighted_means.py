import numpy as np
import xarray as xr

import data_variables_parameters as dvp

###############################################################################

def area_weighted_mean(ds_var,ds_area,sector):
    '''Compute area weighted mean oceanic temperature over specific oceanic sector'''
    mask_sector = dvp.sel_mask(ds_area,sector)
         
    area_weights = ds_area.areacello
        
    area_weighted = ds_var.where(mask_sector).weighted(area_weights.fillna(0)) #DataArrayWeighted with weights along dimensions: j, i
    lat = ds_var.dims[2]
    lon = ds_var.dims[3]
    
    if ((lat=='y') or (lat=='j') or (lat=='lat') or (lat=='latitude')) and ((lon=='x') or (lon=='i') or (lon=='lon') or (lon =='longitude')):
        print('Latitude and longitude coordinates determined as', lat, ' and ', lon, 'respectively')
    else: 
        print('Vertical dimension = ',lat,' Horizontal dimension = ',lon)
        print('Check if these dimensions are correct to compute weighted mean')
    
    #print('Computing area weighted mean')
    area_weighted_mean = area_weighted.mean((lat,lon))
    return area_weighted_mean #2D field: time,levs
    

def lat_weighted_mean(ds_var,ds,sector):
    '''Compute latitude weighted mean oceanic temperature over specific oceanic sector
    (For a rectangular grid the cosine of the latitude is proportional to the grid cell area.)'''
    mask_sector = dvp.sel_mask(ds_var,sector)
 
    # loop over dimensions to find latitude and longitude names
    for i in np.arange(len(ds_var.dims)):
        dim = ds_var.dims[i]
        
        if ((dim=='y') or (dim=='j') or (dim=='lat') or (dim=='latitude')):
            lat_name = ds_var.dims[i]
        elif ((dim=='x') or (dim=='i') or (dim=='lon') or (dim =='longitude')):
            lon_name = ds_var.dims[i]
        else:
            continue
    
    print('Latitude and longitude coordinates determined as', lat_name, ' and ', lon_name, 'respectively')
    
    latitudes = ds[lat_name]
    lat_weights = np.cos(np.deg2rad(latitudes))
    lat_weighted = ds_var.where(mask_sector).weighted(lat_weights.fillna(0))
    
    #print('Computing latitude weighted mean')
    lat_weighted_mean = lat_weighted.mean((lat_name,lon_name))
    return lat_weighted_mean #2D field: time,levs  

def nearest_above(my_array, target):
    '''Find nearest value in array that is greater than target value and return corresponding index'''
    diff = my_array - target
    mask = np.ma.less_equal(diff, 0)
    # We need to mask the negative differences and zero
    # since we are looking for values above
    if np.all(mask):
        return None # returns None if target is greater than any value
    masked_diff = np.ma.masked_array(diff, mask)
    # Returns the index of the minimum value
    return masked_diff.argmin() 

def nearest_below(my_array, target):
    '''Find nearest value in array that is smaller than target value and return corresponding index'''
    diff = target - my_array
    mask = np.ma.less_equal(diff, 0)
    # We need to mask the positive differences and zero
    # since we are looking for values below
    if np.all(mask):
        return None # returns None if target is smaller than any value
    masked_diff = np.ma.masked_array(diff, mask)
    # Returns the index of the minimum value
    return masked_diff.argmin()

def lev_weighted_mean(ds,lev_bnds,sector):
    '''Compute volume weighted mean oceanic temperature over specific oceanic
    sector and specific depth layers (centered around ice shelf depth)'''
   
    print('Select depth bounds of sector')
    depth_bnds_sector = dvp.sel_depth_bnds(sector)     
    depth_top = depth_bnds_sector[0]
    depth_bottom = depth_bnds_sector[1]
    print(depth_bnds_sector)
    
    print('Find oceanic layers covering the depth bounds and take a slice of these')
    # layers
    lev_ind_bottom= nearest_above(lev_bnds[:,1],depth_bottom)
    lev_ind_top = nearest_below(lev_bnds[:,0],depth_top)
    levs_slice = ds.isel(lev=slice(lev_ind_top,lev_ind_bottom+1))
    
    print('Create weights for each oceanic layer, correcting for layers that fall only partly within specified depth range') 
    lev_bnds_sel = lev_bnds.values[lev_ind_top:lev_ind_bottom+1]
    lev_bnds_sel[lev_bnds_sel > depth_bottom] = depth_bottom
    lev_bnds_sel[lev_bnds_sel < depth_top] = depth_top
    # Weight equals thickness of each layer
    levs_weights = lev_bnds_sel[:,1]-lev_bnds_sel[:,0] 
    # DataArray required to apply .weighted on DataArray
    levs_weights_DA = xr.DataArray(levs_weights,coords={'lev': levs_slice.lev},
             dims=['lev'])
    
    print('Compute depth weighted mean of ocean slice')
    levs_slice_weighted = levs_slice.weighted(levs_weights_DA)
    levs_weighted_mean = levs_slice_weighted.mean(("lev"))
    
    print('Return layer-weighted ocean temperature')
    return levs_weighted_mean