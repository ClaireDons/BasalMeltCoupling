import numpy as np

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