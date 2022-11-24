from AMRtools import AMRfile as amr
import xarray as xr
import pandas as pd


class Freshwater:
    def __init__(self,df):
        self.df = df

    def volume_change(vol1,vol2):
        div_vol = vol2 - vol1
        return div_vol

    def CalvingContribution(self,smb,bmb,vol1,vol2):
        div_vol = self.volume_change(vol1,vol2)
        U = smb + bmb - div_vol
        return U

    def BasalContribution(bmb):        
        return -bmb

    pass