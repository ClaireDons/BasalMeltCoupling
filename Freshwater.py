from AMRtools import flatten as flt
from BasalMelt import LevermannMask as lvm
import xarray as xr
import pandas as pd


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


    def RegionalContribution(self,mask_path,nc_out,driver):
        x,y,masks = self.region(mask_path,nc_out,driver)
        dat = flt(self.file1).open(driver)
        assert dat.thickness.shape == list(masks.values())[0].shape, "arrays are not the same shape"

        #for key, m in masks.items():
          

            #print(m)
            #r = dat.where(m != 0)
            #print(r)

    pass

