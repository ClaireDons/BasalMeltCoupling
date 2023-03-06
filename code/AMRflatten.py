import os
import subprocess
import pandas as pd
import xarray as xr


class flatten:
    """ Class for BISICLES amr files and methods relating to flatten
    ...
    Attributes
    ----------
    file (str): name of BISICLES amr file
    
    Methods
    -------
    find_name
        find base name of file
    flatten
        flatten amr file to netcdf
    open
        flatten amr file and open dataset
    flattenMean
        Take mean of each variable in flattened file
    flattenSum
        Take sum of each variable in flattened file
    mean
        Flatten amr file and take mean
    sum
        Flatten amr file and take sum
    """
    def __init__(self,file):
        self.file = file

    def find_name(self):
        """Find the base name of the file
        Returns:
            basename of BISICLES amr file
        """
        name = os.path.splitext(os.path.basename(self.file))[0]
        assert len(name) > 0, "name is empty"
        return name

    def flatten(self,flatten,path):
        """Flatten AMR file to netcdf
        Args:
            flatten (str): path to flatten driver
            path (str): path to netcdf output    
        Returns:
            netcdf of flattend AMR file
        """
        name = self.find_name()
        nc = path + name + '.nc'
        flattenOutput = subprocess.Popen([flatten, self.file, nc, "0", "-3333500", "-3333500"], stdout=subprocess.PIPE)
        # assess
        flattenOutput.communicate()[0]


    def open(self,flatten,path):
        """Flatten AMR file and open it
        Args:
            flatten (str): path to flatten driver
            path (str): path to netcdf output
        Returns:
            xarray dataset of flattened BISICLES file
        """
        self.flatten(flatten,path)
        name = self.find_name()
        nc = path + name + ".nc"
        dat = xr.open_dataset(nc)
        assert dat.time.size != 0, "dataset is empty"
        return dat
    

    def flattenMean(self,dat):
        """Take mean of each variable in flattened file
        Args:
            dat (xarray dataset): BISICLES flattened file
        Returns:
            pandas dataframe (df) of mean values for each variable 
        """
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
        """Take sum of each variable in flattened file
        Args:
            dat (xarray dataarray): BISICLES flattened file
        Returns:
            pandas dataframe (df) of sum of values for each variable 
        """
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
        """Flatten amr file and take mean
         Args:
            flatten (str): path to flatten driver
        Returns:
            pandas dataframe (df) of mean values for each variable  
        """
        dat = self.open(flatten)
        df = self.flattenMean(dat)
        return df

    def sum(self,flatten):
        """Flatten amr file and take sum
        Args:
            flatten (str): path to flatten driver
        Returns:
            pandas dataframe (df) of sum of values for each variable  
        """
        dat = self.open(flatten)
        df = self.flattenSum(dat)
        return df

    pass  
