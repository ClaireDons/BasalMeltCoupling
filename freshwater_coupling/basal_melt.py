""" This module is for calculating basal melt based on
ocean temperature from EC-Earth.

Classes: OceanData, BasalMelt
"""

import numpy as np
import xarray as xr
import pandas as pd
from freshwater_coupling.antarctic_sectors import LevermannSectors as levermann


class OceanData:
    """Class of ocean output file related calculations
    ...

    Attributes
    ----------
    thetao (str): name of ocean temperature file
    area (str): name of areacello file

    Methods
    -------
    area_weighted_mean
        Compute area weighted mean of ocean temperature over a sector
    nearest_mask
        Mask the values outside of target depth
    nearest_above
        Find nearest value above target value
    nearest_below
        Find nearest value below target value
    lev_weighted_mean
        Compute depth weighted mean oceanic temperature over specific
        oceanic sector and specific depth layers
    ShelfBase
        select oceanic layers based on shelf depth
    select_depth_range
        Select depth bounds of sector
    select_lev_mean
        Compute mean of depth bounds
    select_area_mean
        Compute area mean of sector
    weighted_mean_df
        Compute volume weighted mean for one year of thetao
    """

    # Sectors
    sectors = ["eais", "wedd", "amun", "ross", "apen"]

    # Sector-specific depths (based on shelf base depth)
    find_shelf_depth = {"eais": 369, "wedd": 420, "amun": 305, "ross": 312, "apen": 420}

    def __init__(self, thetao, area):
        self.thetao = thetao
        self.area = area

    def open_datasets(self):
        """Open datasets
        Args:
            thetao (str): path to ocean temperature dataset
            area (str): path to area dataset
        Returns:
            xarray datasets of ocean temperature and area dataset
        """
        thetao_ds = xr.open_dataset(self.thetao)
        area_ds = xr.open_dataset(self.area)
        return thetao_ds, area_ds

    def area_weighted_mean(self, ds_sel, ds_area):
        """Compute area weighted mean oceanic temperature over specific oceanic sector
        Args:
            ds_var (xarray dataset): thetao dataset
            ds_area (xarray dataset): areacello dataset
        Returns:
            area_weighted_mean (dataarray): area weighted mean of thetao
        """

        area_weights = ds_area.areacello.fillna(0)
        area_weighted = ds_sel.weighted(area_weights)
        lat = "j"
        lon = "i"

        area_weighted_mean = area_weighted.mean((lat, lon))

        return area_weighted_mean

    def nearest_mask(self, diff):
        """Mask the values outside of target
        Args:
            diff (xarray dataset):
        Returns:
            masked_diff (xarray dataset):
        """
        mask = np.ma.less_equal(diff, 0)
        if np.all(mask):
            return None
        masked_diff = np.ma.masked_array(diff, mask)
        return masked_diff

    def nearest_above(self, my_array, target):
        """Find nearest value in array that is greater than target value
        and return corresponding index
        Args:
            my_array (xarray dataset): ocean data array
            target (float): depth to calculate around
        Returns:
            masked_diff.argmin() ():
        """
        diff = my_array - target
        masked_diff = self.nearest_mask(diff)
        return masked_diff.argmin()

    def nearest_below(self, my_array, target):
        """Find nearest value in array that is smaller than target value
        and return corresponding index
            Args:
            my_array (xarray dataset): ocean data array
            target (float): depth to calculate around
        Returns:
            masked_diff.argmin() ():
        """
        diff = target - my_array
        masked_diff = self.nearest_mask(diff)
        return masked_diff.argmin()

    def lev_weighted_mean(self, thetao_ds, lev_bnds, top, bottom):
        """Compute volume or depth weighted mean oceanic temperature over specific oceanic
        sector and specific depth layers (centered around ice shelf depth)
        Args:
            thetao_ds (xarray dataset): 2D or 3D thetao dataset
            lev_bnds (xarray dataarray): ocean depth bands array
            sector (str): sector name
        Returns:
            levs_weighted_means (float): volume weighted mean of ocean temperature
        """

        # Find oceanic layers covering the depth bounds and take a slice of these
        # layers
        lev_ind_bottom = self.nearest_above(lev_bnds[:, 1], bottom)
        lev_ind_top = self.nearest_below(lev_bnds[:, 0], top)
        levs_slice = thetao_ds.isel(lev=slice(lev_ind_top, lev_ind_bottom + 1))

        # Create weights for each oceanic layer, correcting for layers
        # that fall only partly within specified depth range
        lev_bnds_sel = lev_bnds.values[lev_ind_top : lev_ind_bottom + 1]
        lev_bnds_sel[lev_bnds_sel > bottom] = bottom
        lev_bnds_sel[lev_bnds_sel < top] = top
        # Weight equals thickness of each layer
        levs_weights = lev_bnds_sel[:, 1] - lev_bnds_sel[:, 0]
        # DataArray required to apply .weighted on DataArray
        levs_weights_da = xr.DataArray(
            levs_weights, coords={"lev": levs_slice.lev}, dims=["lev"]
        )

        # Compute depth weighted mean of ocean slice
        levs_slice_weighted = levs_slice.weighted(levs_weights_da)
        levs_weighted_mean = levs_slice_weighted.mean(("lev"))

        # Return layer-weighted ocean temperature
        return levs_weighted_mean

    def shelf_base(self, sector):
        """select oceanic layers based on shelf depth
        Args:
            sector (str): name of sector
        Returns:
            ocean_slice (numpy array): shelfbase slice which is dependent on sector
        """

        shelf_depth = self.find_shelf_depth[sector]
        ocean_slice = np.array([shelf_depth - 50, shelf_depth + 50])

        return ocean_slice

    def select_depth_range(self, sector):
        """Select depth bounds of sector
        Args:
            sector (str): name of sector
        Returns:
            top (float) and bottom (float) ocean depth range limits
        """
        depth_bnds_sector = self.shelf_base(sector)
        top = depth_bnds_sector[0]
        bottom = depth_bnds_sector[1]
        return top, bottom

    def sector_lev_mean(self, thetao_ds, lev_bnds, sector):
        """Compute mean of depth bounds
        Args:
            thetao_ds (xarray dataset): ocean temperature dataset
            lev_bands (array): array of depth level bands
            sector (str): sector name
        Returns:
            lev_weighted_mean (xarray dataarray) depth weighted mean of ocean depth range
        """
        top, bottom = self.select_depth_range(sector)
        lev_weighted_mean = self.lev_weighted_mean(thetao_ds, lev_bnds, top, bottom)
        return lev_weighted_mean

    def weighted_mean_df(self):
        """Compute volume weighted mean for one year of thetao
        Args:
            area_file (str): file name for file containing areacello data
            thetao_file (str): file name for file containing ocean data
            sectors (list of str): list of sector names
        Returns:
            df (pandas dataframe): dataframe with volume weighted mean for each sector
        """
        # Open thetao dataset
        thetao_ds, area_ds = self.open_datasets()
        thetao_ds = thetao_ds.rename(
            {
                "y": "j",
                "x": "i",
                "nav_lon": "longitude",
                "nav_lat": "latitude",
                "olevel": "lev",
            }
        )
        ds_year = thetao_ds.groupby("time_counter.year").mean(
            "time_counter"
        )  # Compute annual mean
        masks = levermann().sector_masks(thetao_ds)

        # Loop over oceanic sectors
        mean_df = pd.DataFrame()
        for sector in self.sectors:
            mask = masks[sector]
            ds_sel = ds_year["thetao"].where(mask)
            ds_lev_bnds = ds_year.olevel_bounds.mean("year").copy()
            # ds_lev_bnds = ds_year.lev_bnds.mean("year").copy()
            thetao_awm = self.area_weighted_mean(ds_sel, area_ds)
            print(thetao_awm)
            thetao_vwm = self.sector_lev_mean(thetao_awm, ds_lev_bnds, sector)
            print(thetao_vwm)
            mean_df[sector] = thetao_vwm

        ds_year.close()
        area_ds.close()
        print("ocean T: ", mean_df)
        return mean_df


class BasalMelt(OceanData):
    """Class for Basal Melt calculation related calculations
    ...

    Attributes
    ----------
    rho_i (float): ice density kg m-3
    rho_sw (float): sea water density
    c_po (float): specific heat capacity of ocean mixed layer J kg-1 K-1
    L_i (float): latent heat of fusion of ice
    Tf (float): Freezing temperature
    baseline (float): baseline climate mean temperature
    gamma (float): gamma value for chosen model

    Methods
    -------
    quad_constant
        Calculate quadratic constant
    quadBasalMelt
        Calculate basal melt
    BasalMeltAnomalies
        Calculate basal melt anomaly
    thetao2basalmelt
        Calculate basal melt from 3D ocean temperature file
    mapBasalMelt
        Map basal melt values to Antarctic Sectors
    """

    # Parameters to compute basal ice shelf melt (Favier 2019)
    rho_i = 917.0
    rho_sw = 1028.0
    c_po = 3974.0
    L_i = 3.34 * 10**5
    Tf = -1.6
    baseline = {
        "eais": 0.27209795341055726,
        "wedd": -1.471784486780416,
        "amun": 2.1510233407460326,
        "ross": 0.5177848939696833,
        "apen": -0.6192596251283067,
    }

    def __init__(self, thetao, area, gamma):
        OceanData.__init__(self, thetao, area)
        self.gamma = gamma

    def basal_melt_sensitivity(self):
        """Calculate quadratic constant
        Returns:
            melt_sensitivity (float) quadratic constant value
        """
        c_lin = (self.rho_sw * self.c_po) / (self.rho_i * self.L_i)
        c_quad = (c_lin) ** 2
        melt_sensitivity = self.gamma * 10**5 * c_quad  # Quadratic constant
        return melt_sensitivity

    def quadratic_basal_melt(self, thetao):
        """Calculate basal melt
        Args:
            thetao (float): ocean temperature value
        Returns:
            bm (float): basal melt value
        """
        melt_sensitivity = self.basal_melt_sensitivity()
        basalmelt = (thetao - self.Tf) * (abs(thetao - self.Tf)) * melt_sensitivity
        return basalmelt

    def basal_melt_anomalies(self, thetao, base):
        """Calculate basal melt anomaly
        Args:
            thetao (float): ocean temperature value
            base (float): ocean temperature baseline value
        Returns:
            dBM (float) basal melt anomaly
        """
        basalmelt_base = self.quadratic_basal_melt(base)
        basalmelt = self.quadratic_basal_melt(thetao)
        delta_basalmelt = basalmelt - basalmelt_base
        assert delta_basalmelt < 100, "Basal melt too unrealistic"
        assert delta_basalmelt > -100, "Basal melt too unrealistic"
        return delta_basalmelt

    def thetao2basalmelt(self):
        """Calculate basal melt from 3D ocean temperature file
        Returns:
            df2 (pandas dataframe) values of basal melt for each Antarctic region
        """
        wmean_df = self.weighted_mean_df()
        basalmelt_df = pd.DataFrame()
        for column in wmean_df:
            thetao = wmean_df[column].values
            print("ocean T: ", thetao)
            base = self.baseline.get(column)
            print("base: ", base)
            delta_basalmelt = self.basal_melt_anomalies(thetao, base)
            basalmelt_df[column] = delta_basalmelt
        assert basalmelt_df.empty is False, "Dataframe should not be empty"
        print(basalmelt_df)
        return basalmelt_df

    def map_basalmelt(self, mask_path, nc_out, driver, name):
        """Calculate basal melt values and map to Antarctic sectors
        Args:
            mask_path (str): path to mask files
            nc_out (str): path to where basal melt file will be output
            driver (str): path to filetools driver
            name (str): name of basal melt file
        Returns:
            basal melt dataframe and produces netcdf and hdf5 files
        """
        basalmelt_df = self.thetao2basalmelt()
        levermann().map2amr(mask_path, nc_out, driver, name, basalmelt_df)
        return basalmelt_df
