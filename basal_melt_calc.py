import xarray as xr
import pandas as pd
import numpy as np

import data_variables_parameters as dvp
import weighted_means as comp

def weighted_mean_df(area_file, thetao_file, sectors):
    """ Compute volume weighted mean for one year of thetao
    Args:
        area_file (str): file name for file containing areacello data
        thetao_file (str): file name for file containing ocean data
        sectors (list of str): list of sector names
    Returns:
        df (pandas dataframe): dataframe with volume weighted mean for each sector
    """
    # Open thetao dataset
    ds = xr.open_dataset(thetao_file)
    ds_year = ds.groupby('time.year').mean('time') #Compute annual mean
    ds.close()
    area_ds = xr.open_dataset(area_file)

    # Loop over oceanic sectors
    df = pd.DataFrame()
    for sector in sectors:
        # Compute area weighted mean
        print('Computing area weighted mean of thetao for ', sector, 'sector')           
        thetaoAWM = comp.area_weighted_mean(ds_year["thetao"],area_ds,sector)
        thetaoVWM = comp.lev_weighted_mean(thetaoAWM, ds_year.lev_bnds.mean("year").copy(),sector)
        df[sector] = thetaoVWM

    ds_year.close()
    area_ds.close()
    return df

def quadBasalMeltAnomalies(gamma, thetao, Tf , baseline):
    """Function to compute basal melt anomalies based on quadratic parameterization
    Args:
        gamma (float): Calibration parameter
        thetao (float): Ocean temperature from ESM model
        Tf (float): Freeing point temperature based on GREP reanalysis
        baseline (float): baseline ocean temperature (1850-1930)
    Returns:
        dBM (float): Basal melt anomaly
    """

    # Parameters to compute basal ice shelf melt (Favier 2019)
    rho_i = 917. #ice density kg m-3
    rho_sw = 1028. # sea water density
    c_po = 3974. # specific heat capacity of ocean mixed layer J kg-1 K-1
    L_i = 3.34*10**5 # latent heat of fusion of ice

    c_lin = (rho_sw*c_po)/(rho_i*L_i)
    c_quad = (c_lin)**2

    ## Compute quadratic basal melt anomalies with gamma (array or single value)
    # Quadratic constant
    ms = gamma * 10**5 * c_quad

    # Quadratic melt baseline (negative if To < Tf)
    BM_base = (baseline - Tf)*(abs(baseline) - Tf) * ms
    # Compute basal melt timeseries
    BM = (thetao - Tf) * (abs(thetao) - Tf) * ms  
    # Compute basal melt anomalies
    dBM = BM - BM_base

    # return: basal melt anomalies
    return dBM