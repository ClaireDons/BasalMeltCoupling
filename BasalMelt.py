import numpy as np
from glob import glob
import os
import xarray as xr
import pandas as pd

class BasalMelt:
    # Parameters to compute basal ice shelf melt (Favier 2019)
    rho_i = 917. #ice density kg m-3
    rho_sw = 1028. # sea water density
    c_po = 3974. # specific heat capacity of ocean mixed layer J kg-1 K-1
    L_i = 3.34*10**5 # latent heat of fusion of ice
    Tf = -1.6
    baseline = 1

    def __init__(self,gamma):
        self.gamma = gamma
        #self.thetao = thetao
        

    def calc_cquad(self):
        c_lin = (self.rho_sw*self.c_po)/(self.rho_i*self.L_i)
        c_quad = (c_lin)**2
        return c_quad


    def quadBasalMeltAnomalies(self, thetao):
        ## Compute quadratic basal melt anomalies with gamma
        c_quad = self.calc_cquad()
        ms = self.gamma * 10**5 * c_quad # Quadratic constant
        # Quadratic melt baseline (negative if To < Tf)
        BM_base = (self.baseline - self.Tf)*(abs(self.baseline) - self.Tf) * ms
        # Compute basal melt
        BM = (thetao - self.Tf) * (abs(thetao) - self.Tf) * ms  
        # Compute basal melt anomalies
        dBM = BM - BM_base
        return dBM

    def thetao2basalmelt(self,df):
        df2 =  pd.DataFrame()
        for column in df:
            thetao = df[column].values
            dBM = self.quadBasalMeltAnomalies(thetao)
            df2[column]=dBM
        return df2

    pass

class LevermannMask:
    def __init__(self,mask_path,nc_out,driver):
        self.mask_path = mask_path
        self.nc_out = nc_out
        self.driver = driver
        
    def OpenMasks(self):
        self.nc_files = glob(os.path.join(self.mask_path, "*.2d.nc"))
        bisicles_masks = {}
        for file in self.nc_files:
            key = os.path.splitext(os.path.basename(file))[0][15:-3]
            name = 'smask' + str(key)
            dat = xr.open_dataset(file)
            bisicles_masks[name] = np.array(dat['smask'])
            #globals()['smask' + str(key)] = np.array(dat['smask'])

        x = np.array(dat['x'])
        y = np.array(dat['y'])
        return x,y,bisicles_masks

    def map2amr(self,name,df2):
        x,y,bisicles_masks = self.OpenMasks()
        for i, row in df2.iterrows():
            new_mask = np.where(bisicles_masks['smask1'] == 1, row.apen, bisicles_masks['smask1'])
            new_mask = np.where(bisicles_masks['smask2'] == 1, row.amun, new_mask)
            new_mask = np.where(bisicles_masks['smask3'] == 1, row.ross, new_mask)
            new_mask = np.where(bisicles_masks['smask4'] == 1, row.eais, new_mask)
            new_mask = np.where(bisicles_masks['smask5'] == 1, row.wedd, new_mask)
            da = xr.DataArray(data= new_mask, coords=[("x", x),("y",y)], name="bm")
            da.to_netcdf(self.nc_out+ name + '.nc')
            os.system(self.driver + " " + self.nc_out + name + ".nc " + self.nc_out + name + ".2d.hdf5 bm")

    pass