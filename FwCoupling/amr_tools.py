"""This module is for methods and calculations related to
the BISICLES filetools.

classes: Flatten, Masks
"""

import os
import subprocess
from glob import glob
import numpy as np
import pandas as pd
import xarray as xr


class Flatten:
    """Class for BISICLES amr files and methods relating to flatten
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

    def __init__(self, file):
        self.file = file

    def find_name(self):
        """Find the base name of the file
        Returns:
            basename of BISICLES amr file
        """
        name = os.path.splitext(os.path.basename(self.file))[0]
        assert len(name) > 0, "name is empty"
        return name

    def flatten(self, flatten, path):
        """Flatten AMR file to netcdf
        Args:
            flatten (str): path to flatten driver
            path (str): path to netcdf output
        Returns:
            netcdf of flattend AMR file
        """
        name = self.find_name()
        nc_name = path + name + ".nc"
        flatten_output = subprocess.Popen(
            [flatten, self.file, nc_name, "0", "-3333500", "-3333500"],
            stdout=subprocess.PIPE,
        )
        # assess
        flatten_output.communicate()[0]

    def open(self, flatten, path):
        """Flatten AMR file and open it
        Args:
            flatten (str): path to flatten driver
            path (str): path to netcdf output
        Returns:
            xarray dataset of flattened BISICLES file
        """
        self.flatten(flatten, path)
        name = self.find_name()
        nc_name = path + name + ".nc"
        dat = xr.open_dataset(nc_name)
        assert dat.time.size != 0, "dataset is empty"
        return dat

    def flatten_mean(self, flatten_dat):
        """Take mean of each variable in flattened file
        Args:
            flatten_dat (xarray dataset): BISICLES flattened file
        Returns:
            pandas dataframe (df) of mean values for each variable
        """
        variables = []
        means = []
        for i in flatten_dat:
            val_mean = flatten_dat[i].mean().values
            variables.append(i)
            means.append(val_mean)
        means_df = pd.DataFrame(columns=vars)
        series = pd.Series(means, index=means_df.columns)
        means_df = means_df.append(series, ignore_index=True)
        assert means_df.empty is False, "Dataframe should not be empty"
        return means_df

    def flatten_sum(self, flatten_dat):
        """Take sum of each variable in flattened file
        Args:
            flatten_dat (xarray dataarray): BISICLES flattened file
        Returns:
            pandas dataframe (df) of sum of values for each variable
        """
        variables = []
        means = []
        for i in flatten_dat:
            val_sum = flatten_dat[i].sum().values
            variables.append(i)
            means.append(val_sum)
        sums_df = pd.DataFrame(columns=vars)
        series = pd.Series(means, index=sums_df.columns)
        sums_df = sums_df.append(series, ignore_index=True)
        assert sums_df.empty is False, "Dataframe should not be empty"
        return sums_df

    def mean(self, flatten):
        """Flatten amr file and take mean
         Args:
            flatten (str): path to flatten driver
        Returns:
            pandas dataframe (df) of mean values for each variable
        """
        flatten_dat = self.open(flatten)
        means_df = self.flatten_mean(flatten_dat)
        return means_df

    def sum(self, flatten):
        """Flatten amr file and take sum
        Args:
            flatten (str): path to flatten driver
        Returns:
            pandas dataframe (df) of sum of values for each variable
        """
        flatten_dat = self.open(flatten)
        sums_df = self.flatten_sum(flatten_dat)
        return sums_df


class Masks:
    """Class for opening bisicles amr masks

    Attributes
    ----------
    path (str): path to mask files

    Methods
    -------
    bisicles_masks
        Method opening region masks and creating a dictionary containing them

    """

    def __init__(self, path):
        self.path = path

    def bisicles_masks(self):
        """Open region masks and create dictionary
        Returns:
            x,y co-ordinate np.array and bisicles_mask (np.array) of each Antarctic region
        """
        nc_files = glob(os.path.join(self.path, "*.2d.nc"))
        bisicles_masks = {}
        for file in nc_files:
            key = os.path.splitext(os.path.basename(file))[0][10:-5]
            name = str(key)
            dat = xr.open_dataset(file)
            bisicles_masks[name] = np.array(dat["smask"])
        assert len(bisicles_masks) != 0, "Dictionary should not be empty"

        x = np.array(dat["x"])
        y = np.array(dat["y"])
        return x, y, bisicles_masks
