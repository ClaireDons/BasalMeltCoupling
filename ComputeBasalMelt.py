import basal_melt_calc as calc
import pandas as pd

# Define parameters
path = "/net/pc200037/nobackup/users/linden/cmip6data/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3/historical/r1i1p1f1/" 
area_file = path + "Ofx/areacello/gn/areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc"
thetao_file = path + "Omon/thetao/gn/thetao_Omon_EC-Earth3_historical_r1i1p1f1_gn_201401-201412.nc"
sectors = ['eais','wedd','amun','ross','apen']
gamma = 0.05
Tf = -1.6
baseline = 1

df = calc.weighted_mean_df(area_file, thetao_file, sectors)

df2 =  pd.DataFrame()
for column in df:
    thetao = df[column].values
    dBM = calc.quadBasalMeltAnomalies(gamma, thetao, Tf, baseline)
    df2[column]=dBM
print(df2)