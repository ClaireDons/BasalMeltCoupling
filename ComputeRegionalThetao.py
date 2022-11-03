import sys
import os
import numpy as np
import pandas as pd
import xarray as xr
import itertools

import data_variables_parameters as dvp
import computations as comp

from pathlib import Path


ocean_depth = 900
if ocean_depth == 900:
    str_depth = str(ocean_depth-100)+'-'+str(ocean_depth+100) #depth range of ocean slice
if ocean_depth == 550:
    str_depth = str(ocean_depth-150)+'-'+str(ocean_depth+150)


### Function definitions ######################################################
def depth_path(data_dir):
    st = data_dir.split('/')
    st = list(filter(None, st)) # Remove empty '' strings
    return len(st)

def full_data_paths(DataDir, Model):
    '''Provides a list of full paths to piControl data'''   
    DataPath = (f'{DataDir}/{Model}')
    print('Looking for files there:')
    print(DataPath)
    p = Path(DataPath)
    all_files = sorted(p.glob('*.nc'))
    return all_files

def full_data_paths_area(DataDir, ModelList, EXP, VAR):
    '''Provides a list of full paths to CMIP6 data'''
    
    if VAR == 'areacello':
        version = 'Version'
        var_type = 'Ofx'
        MIP='CMIP'
    
    DataPath = (f'{DataDir}{MIP}/{ModelList.Center}/{ModelList.Model}'+
                f'/{EXP}/{ModelList.Ensemble}/{var_type}/{VAR}/'+
                f'{ModelList.Grid}/{ModelList[version]}')
    print('Looking for files there:')
    print(DataPath)
    p = Path(DataPath)
    all_files = sorted(p.glob('*'+VAR+'*.nc'))
    return all_files


EXP='historical'
VAR='thetao'


data_dir  = '/net/pc200008/nobackup/users/bars/synda_data_bck/CMIP6/'
if EXP == 'historical':
    ModelList = pd.read_csv('../inputdata/AvailableExperiments_thetao_historical.csv')
else:
    ModelList = pd.read_csv(f'../inputdata/AvailableExperiments_thetao_{EXP}_historical.csv')
area = pd.read_csv('../inputdata/paths_areacello.csv')
output_dir = f'/net/pc200037/nobackup/users/linden/kpz/thetao_sector_timeseries/{str_depth}m/{EXP}/'

MIP = {'historical': 'CMIP', 'ssp585': 'ScenarioMIP', 'ssp245': 'ScenarioMIP', 'ssp126': 'ScenarioMIP'}
sectors = ['eais','wedd','amun','ross','apen']


if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

# Select only models that are availabe for all ssps
ModelsAllSsps = pd.read_csv('../csvfiles/all_ssp_ESMs.csv')

sectors = ['eais','wedd','amun','ross','apen']

depth = depth_path(data_dir)

#list_paths = []
list_models = []
for root, dirs, files in os.walk(data_dir):
        if files:
            st = root.split('/')
            st = list(filter(None, st)) # Remove empty '' strings
            #list_paths.append(root)
            list_models.append(st[depth])
print('Available piControl models')
print(list_models)
      
depth2 = depth_path(output_dir)
#print(depth2)
    
skip_models = []
for root2, dirs2, files2 in os.walk(output_dir):
        if files2:
            #print(files2)
            for i in np.arange(len(files2)):
                skip_models.append(files2[i].split('_')[2])
print('Models already processed')
print(skip_models)

# Manually add models to skip
#if EXP == 'ssp126':
#skip_models.append('CNRM-CM6-1') #terminated multiple times, no error
#skip_models.append('CNRM-ESM2-1') #terminated  multiple times(too big file?)
#skip_models.append('CIESM') #terminated multiple times, no error

#Add models that in current paper use historical
#skip_models.append('ACCESS-CM2')
#skip_models.append('CAS-ESM2-0')
#skip_models.append('EC-Earth3')
#skip_models.append('MIROC6')
#skip_models.append('MRI-ESM2-0')


for model in skip_models:
    #print(model)
    if model in list_models:
        #print(model)
        list_models.remove(model)
            # Skip model if not available for all three ssp scenarios

#models that are not complete
#list_models = ['BCC-CSM2-MR']
#list_models = ['ACCESS-CM2', 'CanESM5', 'CMCC-CM2-SR5', 'EC-Earth3', 'FIO-ESM-2-0', 'INM-CM4-8', 
#               'MIROC6', 'NESM3', 'ACCESS-ESM1-5', 'CESM2-FV2', 'CMCC-ESM2', 'EC-Earth3-Veg', 'GFDL-CM4',
#               'INM-CM5-0', 'MPI-ESM1-2-HR', 'NorESM2-LM','AWI-CM-1-1-MR','CESM2-WACCM','CNRM-CM6-1', 
#               'EC-Earth3-Veg-LR','GFDL-ESM4','IPSL-CM5A2-INCA',  'MPI-ESM1-2-LR',  'NorESM2-MM',
#               'CAMS-CSM1-0', 'CIESM', 'CNRM-ESM2-1', 'FGOALS-f3-L', 'HadGEM3-GC31-LL', 'IPSL-CM6A-LR', 'MRI-ESM2-0']
            

###############################################################################

###############################################################################
## Select models that have areacello variable
models_with_area = []
models_without_area = []
models_with_multiple_area = []

for i in  range(len(ModelList.Model)):
   
    line_sel = area[(area.Model == ModelList.Model[i]) & (area.Grid == ModelList.Grid[i])]
    
    if len(line_sel) == 0:
        models_without_area.append(i)
    elif len(line_sel) == 1:
        models_with_area.append(i)
    elif len(line_sel) > 1:
        models_with_multiple_area.append(i)

print('There are ', len(models_without_area), ' models without areacello file: ')
print(ModelList.Model[models_without_area])
print('There are ', len(models_with_area), ' models with areacello file: ') 
print(ModelList.Model[models_with_area])

#model_numbers = [28] #5,27, 12 17
#for i in range(len(list_models)):
for i in range(len(ModelList.Model)):
    
    ## Skip model if it has already been processed (check if last model is complete (all sectors)!)
    #if ModelList.Model[i] in skip_models:
    #    print('Skipping model', ModelList.Model[i])
    #    continue
    
        
    # Process one model, skip others
    if ModelList.Model[i] != 'NorESM2-MM':
        print('Skipping model', ModelList.Model[i])
        continue
    
    # Skip model if not available for all three ssp scenarios
    if ModelList.Model[i] not in ModelsAllSsps['models'].values:
        print('Skipping model', ModelList.Model[i])
        continue
    
    print(f'##### Working on {ModelList.Model[i]}')
    files_thetao = dvp.full_data_paths(data_dir, MIP[EXP], ModelList.iloc[i], EXP, VAR)
    
    if (ModelList.Model[i] == 'MRI-ESM2-0') and (EXP != 'historical'):
        files_thetao = files_thetao[0:2] #corrupt files for year>2100

    for file_thetao in files_thetao:
        print(file_thetao)
        ds = xr.open_dataset(file_thetao)

            # Specify global attributes
        mem = ds.attrs['variant_label']  

        
        # Read start and end year of timeseries for filename
        if EXP == 'historical':
            year_min = 1850
            year_max = 2014
        elif EXP[0:3] == 'ssp':
            year_min = 2015
            year_max = 2100
            print(year_min, year_max)
        # Stop after 251 years
        first_year = str(int(float(ds['time.year'].min().values)))
        last_year = str(int(float(ds['time.year'].max().values)))
        #if first_year>year_max:
            #break

        print(first_year, last_year)

        outputfile = f'{output_dir}/thetao_{str_depth}m_{ModelList.Model[i]}_{EXP}_{mem}_{year_min}_{year_max}.csv'

        #processed_regions = []

        #Read existing output file
        #if sector != 'eais':
        #    ### READ OLD CSV file
        if os.path.isfile(outputfile):  
            print('Reading csv file')
            df_thetao = pd.read_csv(outputfile)  
            df_thetao = df_thetao.set_index('year')

            #processed_regions = df_thetao.columns.values
            #print(processed_regions)

        #Compute annual mean values
        ds_year = ds.groupby('time.year').mean('time')
        #ds_year = ds_year.isel(year=slice(0,251)) #Select first 251 years (to reduce computational load)       

        # Loop over oceanic sectors
        for sector in sectors:

            # Go to next region if region is already processed
            #if sector in processed_regions:
            #    print('Skipping processed region '+sector)
            #    continue
            #else: 
            #    print(sector)

            print(sector)

            if i in models_with_area:
                print('### Read areacello file for this model/grid')
                line_sel = area[(area.Model == list_models[i])]

                files_area = full_data_paths_area(data_dir_area, line_sel.iloc[0], 
                                         line_sel.iloc[0].Experiment, 'areacello')
                #print(files_area)
                #print('And this is the areacello dataset:')
                area_ds = xr.open_mfdataset(files_area,combine='by_coords')
                #print(area_ds)
                area_ds.close()

                # Compute area weighted mean
                print('Computing area weighted mean of thetao for ', sector, 'sector')           

                thetao_area_weighted_mean = comp.area_weighted_mean(ds_year["thetao"],area_ds,sector)

                try:
                    thetao_volume_weighted_mean = comp.lev_weighted_mean(thetao_area_weighted_mean,ds_year.lev_bnds.mean("year").copy(),ocean_depth)
                except:
                    thetao_volume_weighted_mean = comp.lev_weighted_mean(thetao_area_weighted_mean,ds_year.lev_bounds.mean("year").copy(),ocean_depth)

            elif i in models_without_area:
                print('Computing latitude weighted mean of thetao for ', sector, 'sector')
                # Compute latitude weighted mean
                thetao_lat_weighted_mean = comp.lat_weighted_mean(ds_year["thetao"],ds_year,sector)

                try:
                    thetao_volume_weighted_mean = comp.lev_weighted_mean(thetao_lat_weighted_mean,ds_year.lev_bnds.mean("year").copy(),ocean_depth)
                except:
                    thetao_volume_weighted_mean = comp.lev_weighted_mean(thetao_lat_weighted_mean,ds_year.lev_bounds.mean("year").copy(),ocean_depth)


            # Create dataframe from dataarray
            print('Create dataframe for sector ', sector)
            df_thetao_year = thetao_volume_weighted_mean.to_dataframe()
            df_thetao_year = df_thetao_year.rename(columns={'thetao': sector})

            # Add time series with new sector  
            if sector == 'eais':
                print('Add eais')
                df_thetao_new = df_thetao_year 
            if sector != 'eais':
                print('Add sector to dataframe')
                df_thetao_new[sector] = df_thetao_year[sector]

        # Add years from next thetao_file to previous
        if file_thetao == files_thetao[0]:
            df_thetao = df_thetao_new
        else:
            df_thetao = pd.concat([df_thetao, df_thetao_new], axis=0)

        print(f'##### Exporting data of {list_models[i]} to csv file ##############')
        print(df_thetao.columns.values)

        print(outputfile)

        if os.path.isfile(outputfile):    
            os.remove(outputfile)    

        #ds_thetao_ts.to_netcdf(outputfile)
        df_thetao.to_csv(outputfile)

        ds.close()
        ds_year.close()