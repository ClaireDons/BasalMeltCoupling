import numpy as np
import xarray as xr

class LevermannSectors:
    """ Class for Levermann region related calculations
    ...

    Attributes
    ----------
    eais1, eais2 (list): coordinates for east antarctica
    wedd (list): coordinates for weddel
    amun (list): coordinates for amundsen
    ross (list): coordinates for ross
    apen1,apen2 (list): corrdinates for antarctic peninsula
    sectors (list): list of region names (str)
    find_shelf_depth (dict): dictionary containing shelfbase depth for each region
    ds (xarray dataset): xarray dataset of ocean temperature

    Methods
    -------
    create_mask
        creates mask based on coordinates
    sector_masks
        create dictionary of masks
    sector_sel
        select a region
    """

    eais1 = [-76,-65,0,173]
    eais2 = [-76,-65,350,0]
    wedd = [-90,-72,295,350]
    amun = [-90,-70,210,295]
    ross = [-90,-76,150,210]
    apen1 = [-70,-65,294,310]
    apen2 = [-75,-70,285,295]


    def __init__(self, ds):
        self.ds = ds


    def create_mask(self,coords):
        """ create a mask based on coordinates
        Args:
            ds (xarray dataset): thetao dataset
            lat1,lat2,lon1,lon2 (int): coordinates of sector
        Returns:
            mask (item): mask of sector
        """
        try:
            lat='latitude'
            lon='longitude'
        except:
            lat='lat'
            lon='lon'

        mask = ((self.ds.coords[lat] > coords[0])
            & (self.ds.coords[lat] < coords[1])
            & (self.ds.coords[lon] > coords[2])
            & (self.ds.coords[lon] < coords[3])
        )
        return mask

    def sector_masks(self):
        '''select mask of sector
        Args:
            ds (xarray dataset): thetao dataset
            sector (str): sector name
        Returns:
            mask (item): mask of sector
        '''

        mask_eais = self.create_mask(self.eais1)     
        + self.create_mask(self.eais2)
        mask_wedd = self.create_mask(self.wedd)
        mask_amun = self.create_mask(self.amun)
        mask_ross = self.create_mask(self.ross)
        mask_apen = self.create_mask(self.apen1) 
        + self.create_mask(self.apen2)
        masks = {'eais': mask_eais, 'wedd': mask_wedd,  
        'amun': mask_amun, 'ross': mask_ross, 'apen': mask_apen}

        assert len(masks) == 5, "There should be 5 regions"

        return masks

    pass