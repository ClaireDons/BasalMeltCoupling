import numpy as np
import xarray as xr
import os
from FwCoupling.AMRtools import masks as bisi_masks

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


    def create_mask(self,ds,coords):
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

        mask = ((ds.coords[lat] > coords[0])
            & (ds.coords[lat] < coords[1])
            & (ds.coords[lon] > coords[2])
            & (ds.coords[lon] < coords[3])
        )
        return mask

    def sector_masks(self, ds):
        '''select mask of sector
        Args:
            ds (xarray dataset): thetao dataset
            sector (str): sector name
        Returns:
            mask (item): mask of sector
        '''

        mask_eais = self.create_mask(ds, self.eais1)     
        + self.create_mask(ds, self.eais2)
        mask_wedd = self.create_mask(ds, self.wedd)
        mask_amun = self.create_mask(ds, self.amun)
        mask_ross = self.create_mask(ds, self.ross)
        mask_apen = self.create_mask(ds, self.apen1) 
        + self.create_mask(ds, self.apen2)
        masks = {'eais': mask_eais, 'wedd': mask_wedd,  
        'amun': mask_amun, 'ross': mask_ross, 'apen': mask_apen}

        assert len(masks) == 5, "There should be 5 regions"

        return masks

    def map2amr(self, mask_path, nc_out, driver, name, df):
        """Map basal melt values to corresponding masks and create amr file
        Args:
            mask_path (str): path to mask files
            nc_out (str): path to output netcdf
            name (str): name of output netcdf
            df (pandas dataframe): dataframe of basal melt values
        Returns:
            Netcdf and amr file with basal melt mapped for each Levermann region
        """

        x,y,bisicles_masks = bisi_masks(mask_path).bisicles_masks()

        for i, row in df.iterrows():
            new_mask = np.where(bisicles_masks['apen'] == 1, row.apen, bisicles_masks['apen'])
            new_mask = np.where(bisicles_masks['amun'] == 1, row.amun, new_mask)
            new_mask = np.where(bisicles_masks['ross'] == 1, row.ross, new_mask)
            new_mask = np.where(bisicles_masks['eais'] == 1, row.eais, new_mask)
            new_mask = np.where(bisicles_masks['wedd'] == 1, row.wedd, new_mask)
            da = xr.DataArray(data= new_mask, coords=[("x", x),("y",y)], name="bm")
            da.to_netcdf(nc_out+ name + '.nc')
            os.system(driver + " " + nc_out + name + ".nc " + nc_out + name + ".2d.hdf5 bm")
    pass

 