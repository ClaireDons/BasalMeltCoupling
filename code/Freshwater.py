from AMRflatten import flatten as flt
from BasalMelt import LevermannMask as lvm
import pandas as pd
from scipy import ndimage
import numpy as np


class Freshwater:
    """Class for Freshwater input calculation
    ...

    Attributes
    ----------
    regions (dict): Mapping from mask name to region
    flatten (str): path to flatten driver
    file1 (str): file1 name
    file2 (str): file2 name

    Methods
    -------
    region
        Get region masks and extract them
    get_sum
        Get the sum for each variable based on a file
    Calving
        Discharge Calculation
    BasalMelt
        Basal melt calculation
    AntarcticCalvingContribution
        Calving Contribution
    AntarcticBasalContribution
        Basal Melt Contribuition
    maskRegion
        Downsample masks, mask out region, take sum, output to dataframe
    Contributions
        Calving and Basal melt contribution for each region of Antarctica
    RegionalContribution
        Calving and Basal melt contribution for each region of Antarctica
    """

    regions = {"smask0":"anta","smask1":"apen", "smask2":"amun","smask3":"ross","smask4":"eais","smask5":"wedd"}
    area = 64000000

    def __init__(self,flatten,file1,file2):
        self.flatten = flatten
        self.file1 = file1
        self.file2 = file2


    def region(self, mask_path, nc_out, driver):
        """Get region masks and extract them
        Args:
            mask_path (str): path to amr mask files
            nc_out (str): path to where netcdf will be stored
            driver (str): path to BISICLES nc2amr driver
        Returns:
            x,y: co-ordinate series 
            masks:  np.array of Anatrctica sectore masks
        """
        x,y,masks = lvm(mask_path,nc_out,driver).OpenMasks()
        return x,y,masks


    def get_sum(self,f):
        """Get the sum for each variable based on a file
        Args:
            f (str): Name of file to flatten and take sum of
        Returns:
            Dataframe with the sum of values for each variable in bisicles netcdf file
        """
        
        df = flt(f).sum(self.flatten)
        return df


    def Calving(self,smb,bmb,vol1,vol2):
        """Discharge Calculation
        Args:
            smb (float): surface mass balance
            bmb (float): basal mass balance
            vol1, vol2 (float): ice volume at timestep 1 and 2 
        Returns:
            Calving discharge for one region (float)
        """
        div_h = vol2 -vol1 
        div_vol = div_h * self.area
        U = (smb + bmb - div_vol)/(10**9)
        return U


    def BasalMelt(self,bmb):
        """Basal melt calculation
        Args:
            bmb (float): basal melt balance in m yr-1 
        Returns:
            basal melt in gigatonnes (float)
        """
        bmb_vol = bmb * self.area
        bmb_gt =bmb_vol/(10**9)  
        return -bmb_gt


    def maskRegion(self, plot_dat, mask_dat):
        """Downsample masks, mask out region, take sum, output to dataframe
        Args:
            plot_dat (xarray dataset): xarray dataset of BISICLES plot file
            mask_dat (xarray dataset): xarray dataset of original mask file 
        Returns:
            df (pandas dataframe): Dataframe of sum of each variable in BISICLES plot file for a certain region
        """
        mint = mask_dat.astype(int)
        new_m = ndimage.interpolation.zoom(mint,0.125)
        assert plot_dat.thickness.shape == new_m.shape, "arrays are not the same shape"
        cols = []
        sums = []
        for i in plot_dat:
            ar = np.array(plot_dat[i])
            r = np.where(new_m == 1, ar, np.nan)
            sum = np.nansum(r)
            cols.append(i)
            sums.append(sum)
        df = pd.DataFrame(columns=cols)
        series = pd.Series(sums, index=df.columns)
        df = df.append(series, ignore_index=True)
        assert df.empty == False, "Dataframe is empty"
        return df


    def Contributions(self, dat1, dat2, m):
        """Calving and Basal melt contribution for a certain region of Antarctica
        Args:
            dat1 (xarray dataset): BISICLES plot file timestep 1
            dat2 (xarray dataset): BISICLES plot file timestep 2
            m (xarray dataset): mask file of region
        returns:
            U (float): Calving contribution in gigatonnes and bmb (float) basal melt contribution in gigatonnes
        """
        df1 = self.maskRegion(dat1,m)
        df2 = self.maskRegion(dat2,m)
        U = self.Calving(df2.activeSurfaceThicknessSource,df2.activeBasalThicknessSource,df1.thickness,df2.thickness)
        bmb = self.BasalMelt(df2.activeBasalThicknessSource)
        return U, bmb


    def RegionalContribution(self,mask_path,nc_out,driver):
        """Calving and Basal melt contribution for each region of Antarctica
        Args:
            mask_path (str): path to mask files
            nc_out (str): path to netcdf output
            driver (str): BISICLES nc2amr driver path
        Returns:
            discharge_df (pandas dataframe) and basal_df (pandas dataframe): dataframes of calving 
            and basal melt contribution for all regions of Antarctica
        """
        x,y,masks = self.region(mask_path,nc_out,driver)
        dat1 = flt(self.file1).open(driver, nc_out)
        dat2 = flt(self.file2).open(driver, nc_out)
        discharge = {}
        basal = {}
        for key, m in masks.items():
            reg = self.regions.get(key)
            U,bmb = self.Contributions(dat1,dat2,m)
            discharge[reg] = U
            basal[reg] = bmb
        discharge_df = pd.DataFrame.from_dict(discharge)
        basal_df = pd.DataFrame.from_dict(basal)
        return discharge_df, basal_df
    pass
