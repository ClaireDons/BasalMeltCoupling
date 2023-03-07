from AMRflatten import flatten as flt
from BasalMelt import LevermannMask as lvm
import pandas as pd
from scipy import ndimage
import numpy as np

# To Do:
# 1. Should fix anta to be 1 for all of antarctica


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
        """Get region masks and extract them, not sure I need a function for it"""
        x,y,masks = lvm(mask_path,nc_out,driver).OpenMasks()
        return x,y,masks


    def get_sum(self,f):
        """Get the sum for each variable based on a file"""
        df = flt(f).sum(self.flatten)
        return df


    def Calving(self,smb,bmb,vol1,vol2):
        """Discharge Calculation"""
        div_h = vol2 -vol1
        div_vol = div_h * self.area
        U = (smb + bmb - div_vol)/(10**9)
        return U


    def BasalMelt(self,var):
        """Basal melt calculation"""
        div_vol = var * self.area
        bmb =div_vol/(10**9)  
        return -bmb


    def AntarcticCalvingContribution(self):
        """Calving Contribution"""
        df1 = self.get_sum(self.file1)
        df2 = self.get_sum(self.file2)
        U = self.Calving(df2.activeSurfaceThicknessSource,df2.activeBasalThicknessSource,df1.thickness,df2.thickness)
        return U


    def AntarcticBasalContribution(self):
        """Basal Melt Contribuition"""
        df2 = self.get_sum(self.file2)
        bmb = self.BasalMelt(df2.activeBasalThicknessSource)     
        return bmb


    def maskRegion(self,dat, m):
        """Downsample masks, mask out region, take sum, output to dataframe"""
        mint = m.astype(int)
        new_m = ndimage.interpolation.zoom(mint,0.125)
        assert dat.thickness.shape == new_m.shape, "arrays are not the same shape"
        cols = []
        sums = []
        for i in dat:
            ar = np.array(dat[i])
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
        """Calving and Basal melt contribution for each region of Antarctica"""
        df1 = self.maskRegion(dat1,m)
        df2 = self.maskRegion(dat2,m)
        U = self.Calving(df2.activeSurfaceThicknessSource,df2.activeBasalThicknessSource,df1.thickness,df2.thickness)
        bmb = self.BasalMelt(df2.activeBasalThicknessSource)
        return U, bmb


    def RegionalContribution(self,mask_path,nc_out,driver):
        """Calving and Basal melt contribution for each region of Antarctica"""
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