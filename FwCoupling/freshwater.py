"""This module contains the methods and attributes for freshwater
calculations for different regions of Antarctica

Classes: Freshwater
"""

import numpy as np
import pandas as pd
from scipy import ndimage
from FwCoupling.amr_tools import Flatten as flt
from FwCoupling.amr_tools import Masks as bisi_masks


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

    area = 64000000

    def __init__(self, flatten, file1, file2):
        self.flatten = flatten
        self.file1 = file1
        self.file2 = file2

    def region(self, mask_path):
        """Get region masks and extract them
        Args:
            mask_path (str): path to amr mask files
        Returns:
            x,y: co-ordinate series
            masks:  np.array of Anatrctica sectore masks
        """
        x, y, masks = bisi_masks(mask_path).bisicles_masks()
        return x, y, masks

    def get_sum(self, file):
        """Get the sum for each variable based on a file
        Args:
            f (str): Name of file to flatten and take sum of
        Returns:
            Dataframe with the sum of values for each variable
            in bisicles netcdf file
        """

        sum_df = flt(file).sum(self.flatten)
        return sum_df

    def calving(self, smb, bmb, vol1, vol2):
        """Discharge Calculation
        Args:
            smb (float): surface mass balance
            bmb (float): basal mass balance
            vol1, vol2 (float): ice volume at timestep 1 and 2
        Returns:
            Calving discharge for one region (float)
        """
        div_h = vol2 - vol1
        div_vol = div_h * self.area
        calving_flux = (smb + bmb - div_vol) / (10**9)
        return calving_flux

    def basal_melt(self, bmb):
        """Basal melt calculation
        Args:
            bmb (float): basal melt balance in m yr-1
        Returns:
            basal melt in gigatonnes (float)
        """
        bmb_vol = bmb * self.area
        bmb_gt = bmb_vol / (10**9)
        return -bmb_gt

    def mask_region(self, plot_dat, mask_dat):
        """Downsample masks, mask out region, take sum, output to dataframe
        Args:
            plot_dat (xarray dataset): xarray dataset of BISICLES plot file
            mask_dat (xarray dataset): xarray dataset of original mask file
        Returns:
            df (pandas dataframe): Dataframe of sum of each variable in
            BISICLES plot file for a certain region
        """
        mask_int = mask_dat.astype(int)
        new_mask = ndimage.interpolation.zoom(mask_int, 0.125)
        assert plot_dat.thickness.shape == new_mask.shape, "arrays are not the same shape"
        cols = []
        sums = []
        for i in plot_dat:
            area = np.array(plot_dat[i])
            mask_area = np.where(new_mask == 1, area, np.nan)
            mask_sum = np.nansum(mask_area)
            cols.append(i)
            sums.append(mask_sum)
        sum_df = pd.DataFrame(columns=cols)
        series = pd.Series(sums, index=sum_df.columns)
        sum_df = sum_df.append(series, ignore_index=True)
        assert sum_df.empty is False, "Dataframe is empty"
        return sum_df

    def contributions(self, dat1, dat2, mask_file):
        """Calving and Basal melt contribution for a certain region of
        Antarctica
        Args:
            dat1 (xarray dataset): BISICLES plot file timestep 1
            dat2 (xarray dataset): BISICLES plot file timestep 2
            mask_file (xarray dataset): mask file of region
        returns:
            calving_flux (float): Calving contribution in gigatonnes and bmb (float)
            basal melt contribution in gigatonnes
        """
        df1 = self.mask_region(dat1, mask_file)
        df2 = self.mask_region(dat2, mask_file)
        calving_flux = self.calving(
            df2.activeSurfaceThicknessSource,
            df2.activeBasalThicknessSource,
            df1.thickness,
            df2.thickness,
        )
        bmb = self.basal_melt(df2.activeBasalThicknessSource)
        return calving_flux, bmb

    def regional_contribution(self, mask_path, nc_out, driver):
        """Calving and Basal melt contribution for each region of Antarctica
        Args:
            mask_path (str): path to mask files
            nc_out (str): path to netcdf output
            driver (str): BISICLES nc2amr driver path
        Returns:
            discharge_df (pandas dataframe) and
            basal_df (pandas dataframe): dataframes of calving
            and basal melt contribution for all regions of Antarctica
        """
        x, y, masks = self.region(mask_path)
        dat1 = flt(self.file1).open(driver, nc_out)
        dat2 = flt(self.file2).open(driver, nc_out)
        discharge = {}
        basal = {}
        for key, mask in masks.items():
            calving_flux, bmb = self.contributions(dat1, dat2, mask)
            discharge[key] = calving_flux
            basal[key] = bmb
        discharge_df = pd.DataFrame.from_dict(discharge)
        basal_df = pd.DataFrame.from_dict(basal)
        return discharge_df, basal_df
