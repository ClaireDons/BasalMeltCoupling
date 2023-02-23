import os
import subprocess
import pandas as pd
import xarray as xr


class flatten:
    def __init__(self,file):
        self.file = file

    def find_name(self):
        """Find the base name of the file"""
        name = os.path.splitext(os.path.basename(self.file))[0]
        assert len(name) > 0, "name is empty"
        return name

    def flatten(self,flatten,path):
        """Flatten AMR file to netcdf"""
        name = self.find_name()
        nc = path + name + '.nc'
        flattenOutput = subprocess.Popen([flatten, self.file, nc, "0", "-3333500", "-3333500"], stdout=subprocess.PIPE)
        # assess
        flattenOutput.communicate()[0]


    def open(self,flatten,path):
        """Flatten AMR file and open it"""
        self.flatten(flatten,path)
        name = self.find_name()
        nc = path + name + ".nc"
        dat = xr.open_dataset(nc)
        assert dat.time.size != 0, "dataset is empty"
        return dat


# Build support for regions into these functions

    def flattenMean(self,dat):
        """"""
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

    def flattenSum(self,dat):
        """"""
        vars = []
        means = []
        for i in dat:
            m = dat[i].sum().values
            vars.append(i)
            means.append(m)
        df = pd.DataFrame(columns=vars)
        series = pd.Series(means, index = df.columns)
        df = df.append(series, ignore_index=True)
        assert df.empty == False, "Dataframe should not be empty"
        return df           

    def mean(self,flatten):
        """"""
        dat = self.open(flatten)
        df = self.flattenMean(dat)
        return df

    def sum(self,flatten):
        """"""
        dat = self.open(flatten)
        df = self.flattenSum(dat)
        return df

    pass  