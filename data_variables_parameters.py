import numpy as np

def create_mask(ds,coords):
    """ create a mask based on coordinates
    Args:
        ds (xarray dataset): thetao dataset
        lat1,lat2,lon1,lon2 (int): coordinates of sector
    Returns:
        mask (): mask of sector
    """
    try:
        lat='latitude'
        lon='longitude'
    except:
        lat='lat'
        lon='lon'

    mask = ((ds.coords[lat] > coords[0])
        & (ds.coords[lat] < coords[1])
        & (ds.coords[lon] > coords[2])
        & (ds.coords[lon] < coords[3])
    )
    return mask


def sector_masks(ds):
    '''select mask of sector
    Args:
        ds (xarray dataset): thetao dataset
        sector (str): sector name
    Returns:
        mask (): mask of sector
    '''

    mask_eais = create_mask(ds,[-76,-65,0,173]) + create_mask(ds,[-76,-65,350,0])
    mask_wedd = create_mask(ds,[-90,-72,295,350])
    mask_amun = create_mask(ds,[-90,-70,210,295])
    mask_ross = create_mask(ds,[-90,-76,150,210])
    mask_apen = create_mask(ds,[-70,-65,294,310]) + create_mask(ds,[-75,-70,285,295])
    masks = {'eais': mask_eais, 'wedd': mask_wedd, 'amun': mask_amun, 'ross': mask_ross, 'apen': mask_apen}

    return masks


def sel_depth_bnds(sector):
    '''select oceanic layers based on shelf depth
    Args: 
        sector (str): name of sector
    Returns:
        ocean_slice (): shelfbase slice which is dependent on sector
    '''
    
    # Sector-specific depths (baesd on shelf base depth)
    if type(sector) == str:
        find_shelf_depth = {
        'eais': 369,
        'wedd': 420,
        'amun': 305,
        'ross': 312,
        'apen': 420
        }

        shelf_depth = find_shelf_depth[sector]
        ocean_slice = np.array([shelf_depth-50,shelf_depth+50])
    
    # If number is specified, depth is the same for each sector
    if type(sector) == int:
        shelf_depth = sector
        if shelf_depth == 900: #800-1000m
            ocean_slice = np.array([shelf_depth-100,shelf_depth+100]) 
        if shelf_depth == 550: #400-700m
            ocean_slice = np.array([shelf_depth-150,shelf_depth+150])
      
    return ocean_slice


    """
        mask_eais = (
        (ds.coords[lat] > -76)
        & (ds.coords[lat] < -65)
        & (ds.coords[lon] < 173)
    ) + (
        (ds.coords[lat] > -76)
        & (ds.coords[lat] < -65)
        & (ds.coords[lon] > 350) 
    )
    """