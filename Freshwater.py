from AMRtools import flatten as flt
import xarray as xr
import pandas as pd


class Freshwater:
    def __init__(self,flatten,file1,file2):
        self.flatten = flatten
        self.file1 = file1
        self.file2 = file2

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

    pass