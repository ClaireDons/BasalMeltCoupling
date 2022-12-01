from AMRtools import flatten as flt
from BasalMelt import LevermannMask as lvm
import xarray as xr
import pandas as pd
from scipy import ndimage
import numpy as np


class Freshwater:
    def __init__(self,flatten,file1,file2):
        self.flatten = flatten
        self.file1 = file1
        self.file2 = file2


    def region(self, mask_path, nc_out, driver):
        x,y,masks = lvm(mask_path,nc_out,driver).OpenMasks()
        return x,y,masks


    def get_sum(self,f):
        df = flt(f).sum(self.flatten)
        return df


    def Calving(self,smb,bmb,vol1,vol2):
        div_vol = vol2 -vol1
        U = smb + bmb - div_vol
        return U


    def CalvingContribution(self):
        df1 = self.get_sum(self.file1)
        df2 = self.get_sum(self.file2)
        U = (self.Calving(df2.activeSurfaceThicknessSource,df2.activeBasalThicknessSource,df1.thickness,df2.thickness))/(10**3)
        return U


    def BasalContribution(self):
        df2 = self.get_sum(self.file2)
        bmb = df2.activeBasalThicknessSource/(10**3)        
        return -bmb


    def maskRegion(self,dat, m):
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


# Ought to figure out why the resolution is so low in the flattened file
# Also make sure the downsampling has worked and that it covers the correct regions
# Relate the dumb names to actual region names
    def RegionalContribution(self,mask_path,nc_out,driver):
        x,y,masks = self.region(mask_path,nc_out,driver)
        dat1 = flt(self.file1).open(driver)
        dat2 = flt(self.file2).open(driver)
        discharge = {}
        basal = {}
        for key, m in masks.items():
            df1 = self.maskRegion(dat1,m)
            df2 = self.maskRegion(dat2,m)
            U = (self.Calving(df2.activeSurfaceThicknessSource,df2.activeBasalThicknessSource,df1.thickness,df2.thickness))/(10**3)
            bmb = -df2.activeBasalThicknessSource/(10**3)
            discharge[key] = U
            basal[key] = bmb
        discharge_df = pd.DataFrame.from_dict(discharge)
        basal_df = pd.DataFrame.from_dict(basal)
        return discharge_df, basal_df
        
    pass

