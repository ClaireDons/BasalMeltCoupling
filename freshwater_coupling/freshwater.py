"""This module contains the methods and attributes for freshwater
calculations for different regions of Antarctica

Classes: Freshwater
"""

import numpy as np
import pandas as pd
import xarray as xr
from scipy import ndimage
from freshwater_coupling.amr_tools import Flatten as flt
from freshwater_coupling.amr_tools import Masks as bisi_masks


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
    kg_per_Gt = 1e12  # [kg] to [Gt]
    spy = 3600 * 24 * 365  # [s yr^-1]

    def __init__(self, flatten, amr_file1, amr_file2):
        self.flatten = flatten
        self.amr_file1 = amr_file1
        self.amr_file2 = amr_file2

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
        div_vol = div_h / 1 # Divide by difference in time 
        calving_flux = ((smb + bmb - div_vol) / (10**9)) * (917.0 / 1000)
        return calving_flux

    def basal_melt(self, bmb):
        """Basal melt calculation
        Args:
            bmb (float): basal melt balance in m yr-1
        Returns:
            basal melt in gigatonnes (float)
        """
        bmb_vol = bmb * self.area
        bmb_gt = bmb_vol / (10**9) * (917.0 / 1000)
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
        assert (
            plot_dat.thickness.shape == new_mask.shape
        ), "arrays are not the same shape"
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
            df2.activeSurfaceThicknessSource * self.area,
            df2.activeBasalThicknessSource * self.area,
            df1.thickness * self.area,
            df2.thickness * self.area,
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
        dat1 = flt(self.amr_file1).open(driver, nc_out)
        dat2 = flt(self.amr_file2).open(driver, nc_out)
        discharge = {}
        basal = {}
        for key, mask in masks.items():
            calving_flux, bmb = self.contributions(dat1, dat2, mask)
            discharge[key] = calving_flux
            basal[key] = bmb
        discharge_df = pd.DataFrame.from_dict(discharge)
        basal_df = pd.DataFrame.from_dict(basal)
        return discharge_df, basal_df

    def areaflux_calculation(self, fwf_df, distribution_area, distribution_mask):
        """Calculate area forcing based on freshwater input"""
        flux = fwf_df.values * self.kg_per_Gt / self.spy / float(distribution_area)
        # Apply flux to masked region
        fwforcing = flux * distribution_mask
        #fwforcing = fwforcing.rename({"friver": "freshwater_flux"})
        return fwforcing

    def oceangrid_distribution(
        self, discharge_df, basal_df, file_area, file_basal_melt_mask, file_calving_mask
    ):
        """Distribute freshwater input over ocean grid"""

        basal_melt_mask = xr.open_dataset(file_basal_melt_mask)
        calving_mask = xr.open_dataset(file_calving_mask)

        ds_area = xr.open_dataset(file_area)
        basal_melt_area = ds_area.areacello.where(basal_melt_mask.basal_melt_mask).sum('j').sum('i').values
        calving_area = ds_area.areacello.where(calving_mask.calving_mask).sum('j').sum('i').values

        fwf_calving = self.areaflux_calculation(
            discharge_df, calving_area, calving_mask
        )
        fwf_basal = self.areaflux_calculation(
            basal_df, basal_melt_area, basal_melt_mask
        )

        fwf_basal = fwf_basal.rename({'basal_melt_mask':'sorunoff_f'})
        fwf_calving = fwf_calving.rename({'calving_mask':'socalving_f'})

        return fwf_calving, fwf_basal

    def create_time_dimension(self, file_thetao):
        """Create a new time variable for nemo input"""
        ds_thetao = xr.open_dataset(file_thetao)
        time = ds_thetao.time_counter
        t_new = time + np.timedelta64(365, "D")
        return t_new

    def create_fwf_dataarray(self, time_attr, attr_fwfname, fwfvar):
        """Create a dataarray from freshwater forcing"""
        #fwfvar = fwfvar.rename({"freshwater_flux": attr_fwfname})
        fwfvar = fwfvar[attr_fwfname].expand_dims({"time_counter": time_attr.values})
        fwfvar.attrs = {"long_name": attr_fwfname + "flux", "units": "kg/m^2/s"}
        fwfvar = fwfvar.fillna(0)  # set nans to zeros
        return fwfvar

    def create_nemo_forcing(self, fwf_calving, fwf_basal, file_thetao):
        """Create forcing file for NEMO"""

        time_attr = self.create_time_dimension(file_thetao)
        fwf_calvingda = self.create_fwf_dataarray(time_attr, "socalving_f", fwf_calving)
        fwf_basalda = self.create_fwf_dataarray(time_attr, "sorunoff_f", fwf_basal)

        # Merge dataarrays in one dataset
        ds_fwf = xr.merge([fwf_basalda, fwf_calvingda])
        ds_fwf = ds_fwf.assign_coords({"time_counter": time_attr.values})
        return ds_fwf

    def calculate_nemo_forcing(
        self, discharge_df, basal_df, file_area, file_basal_melt_mask, file_calving_mask, file_thetao
    ):
        """Calculate the freshwater distibution for NEMO based on dataframes of basal melt and calving"""
        sum_calving = discharge_df.sum(axis=1)
        sum_basal = basal_df.sum(axis=1)
        print(sum_calving, sum_basal)
        fwf_calving, fwf_basal = self.oceangrid_distribution(
            sum_calving, sum_basal, file_area, file_basal_melt_mask, file_calving_mask
        )
        ds_fwf = self.create_nemo_forcing(fwf_calving, fwf_basal, file_thetao)
        return ds_fwf
