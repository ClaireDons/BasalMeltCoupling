import xarray as xr
import pandas as pd
import numpy as np

def quadratic_basal_melt_anomalies(gamma, file_thetao, file_Tf):
    '''Compute basal melt anomalies based on quadratic parameterization with 
    chosen gamma, ocean temperatures and freezing point temperatures'''

    # Parameters to compute basal ice shelf melt (Favier 2019)
    rho_i = 917. #ice density kg m-3
    rho_sw = 1028. # sea water density
    c_po = 3974. # specific heat capacity of ocean mixed layer J kg-1 K-1
    L_i = 3.34*10**5 # latent heat of fusion of ice

    c_lin = (rho_sw*c_po)/(rho_i*L_i)
    c_quad = (c_lin)**2

    ############################################
    # Read thetao file
    ds_thetao = xr.open_dataarray(file_thetao)
    models = ds_thetao.model
    years = ds_thetao.year

    # Read freezing point temperatures (from GREP Reanalysis)
    da_Tf = xr.open_dataArray(file_Tf)

    # Compute baseline climate (1850-1930 - 80 yr)
    ds_thetao_base = ds_thetao.sel(year=slice(1850, 1930)).mean('year')

    ##############################################
    # Create empty datasets for storage of basal melt timeseries (BM)
    ds_basal_melt = xr.full_like(ds_thetao, fill_value=np.nan)
    # Add gamma as a dimension
    ds_basal_melt = ds_basal_melt.expand_dims({'gamma': gamma_values}, 0)
    ds_BM = ds_basal_melt.copy()

    # Same for baseline (BMbase)
    ds_basal_melt_base = xr.full_like(ds_thetao_base, fill_value=np.nan)
    ds_basal_melt_base = ds_basal_melt_base.expand_dims({'gamma': gamma_values}, 0)
    ds_BM_base = ds_basal_melt_base.copy()

    # Same for change in basal melt (dBM)
    ds_D_basal_melt=xr.full_like(ds_thetao,fill_value=np.nan)
    ds_D_basal_melt = ds_D_basal_melt.expand_dims({'gamma': gamma_values}, 0)
    ds_dBM = ds_D_basal_melt.copy()

    ## Compute quadratic basal melt anomalies with gamma (array or single value)
    # Quadratic constant
    ms = gamma * 10**5 * c_quad

    # Quadratic melt baseline (negative if To < Tf)
    ds_BM_base = (ds_thetao_base - da_Tf)*(abs(ds_thetao_base) - da_Tf[:]) * ms
    # Compute basal melt timeseries
    ds_BM = (ds_thetao - da_Tf) * (abs(ds_thetao) - da_Tf) * ms  
    # Compute basal melt anomalies
    ds_dBM = ds_BM - ds_BM_base

    # return: basal melt anomalies
    return(ds_dBM)