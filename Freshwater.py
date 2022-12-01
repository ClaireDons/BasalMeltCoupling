from AMRtools import flatten as flt
from BasalMelt import LevermannMask as lvm
import pandas as pd
from scipy import ndimage
import numpy as np

# To Do:
# 1. Redo functions so that the regional ones are based on the single ones and that they are shorter
# 2. Ought to figure out why the resolution is so low in the flattened file
# 3. Also make sure the downsampling has worked and that it covers the correct regions

class Freshwater:
    """Class for Freshwater input calculation"""

    regions = {"smask0":"anta","smask1":"apen", "smask2":"amun","smask3":"ross","smask4":"eais","smask5":"wedd"}

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
        div_vol = vol2 -vol1
        U = smb + bmb - div_vol
        return U


    def CalvingContribution(self):
        """Calving Contribution"""
        df1 = self.get_sum(self.file1)
        df2 = self.get_sum(self.file2)
        U = (self.Calving(df2.activeSurfaceThicknessSource,df2.activeBasalThicknessSource,df1.thickness,df2.thickness))/(10**3)
        return U


    def BasalContribution(self):
        """Basal Melt Contribuition"""
        df2 = self.get_sum(self.file2)
        bmb = df2.activeBasalThicknessSource/(10**3)        
        return -bmb


    def maskRegion(self,dat, m):
        """Downsample masks, mask out region, take sum, output to dataframe"""
        new_m = ndimage.interpolation.zoom(m,0.125)
        assert dat.thickness.shape == new_m.shape, "arrays are not the same shape"
        cols = []
        sums = []
        for i in dat:
            ar = np.array(dat[i])
            r = np.where(new_m != 0, ar, np.nan)
            sum = np.nansum(r)
            cols.append(i)
            sums.append(sum)
        df = pd.DataFrame(columns=cols)
        series = pd.Series(sums, index=df.columns)
        df = df.append(series, ignore_index=True)
        assert df.empty == False, "Dataframe is empty"
        return df


    def RegionalContribution(self,mask_path,nc_out,driver):
        """Calving and Basal melt contribution for each region of Antarctica"""
        x,y,masks = self.region(mask_path,nc_out,driver)
        dat1 = flt(self.file1).open(driver)
        dat2 = flt(self.file2).open(driver)
        discharge = {}
        basal = {}
        for key, m in masks.items():
            reg = self.regions.get(key)
            df1 = self.maskRegion(dat1,m)
            df2 = self.maskRegion(dat2,m)
            U = (self.Calving(df2.activeSurfaceThicknessSource,df2.activeBasalThicknessSource,df1.thickness,df2.thickness))/(10**3)
            bmb = -df2.activeBasalThicknessSource/(10**3)
            discharge[reg] = U
            basal[reg] = bmb
        discharge_df = pd.DataFrame.from_dict(discharge)
        basal_df = pd.DataFrame.from_dict(basal)
        return discharge_df, basal_df
    pass