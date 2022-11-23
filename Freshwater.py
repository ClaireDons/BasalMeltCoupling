import AMRtools as amr
import xarray as xr
import pandas as pd

class BISICLES:
    def __init__(self, file):
        self.file = file


    def open(self,flatten):
        amrobj = amr.AMRobject(self.file)
        amrobj.flatten(flatten)
        name = amrobj.find_name()
        nc = name + ".nc"
        dat = xr.open_dataset(nc)
        #assess
        return dat


    def varMeans(dat):
        means = {}
        for i in dat:
            mean = i.mean()
            means[i] = mean
        return means


    def flattenStats(self,flatten):
        dat = self.open(flatten)
        vars = []
        means = []
        for i in dat:
            m = dat[i].mean().values
            vars.append(i)
            means.append(m)
        df = pd.DataFrame(columns=vars)
        series = pd.Series(means, index = df.columns)
        df = df.append(series, ignore_index=True)
        assert df.empty == False, "Dataframe should not be empty"
        return df
pass  

class Freshwater(BISICLES):
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