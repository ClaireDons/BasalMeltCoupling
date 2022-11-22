import numpy as np
import xarray as xr
from glob import glob
import os 
import subprocess
import bisiclesh5 as b5
import pandas as pd
import h5py
from joblib import Parallel, delayed

### 1. Flatten file (Maybe I don't even need this step)

def open_files(path):
    files = glob(os.path.join(path, "*.2d.hdf5"))
    return files

def find_name(path,f):
    name = os.path.splitext(os.path.basename(f))[0]
    return name

def flattenAMR(path,files,flatten):
    for f in files:
        name = find_name(path,f)
        nc = path + '/' + name + '.nc'
        flattenOutput = subprocess.Popen([flatten, f, nc, "0", "-3333500", "-3333500"], stdout=subprocess.PIPE)
        print(flattenOutput)
        output = flattenOutput.communicate()[0]

files = open_files(path)
flattenAMR(path,files,flatten)

### 2. Pull 2 most recent files, if 2 files don't exist then end the process


### 3. Compute integrated mean over all the variables, and create a df


def var_mean(var, level=0):
    '''Calculate the mean value for each variable in bisicles file'''
    box_mean = [i.mean() for i in var.data[level]]
    mean0 = np.mean(box_mean)
    return mean0


def get_varnames(file):
    '''Extract variable names and number of components for bisicles file'''
    h5file = h5py.File(file,'r')
    n_components = h5file.attrs['num_components']
    names = [h5file.attrs['component_'+str(i)].decode('utf-8') 
             for i in range(n_components)]
    h5file.close
    return names, n_components


def unpack_amr(file):
    '''Unpack all the variables in bisicles file. 
    This function in current form needs work.'''
    h5file = h5py.File(file,'r')
    n_components = h5file.attrs['num_components']
    for i in range(n_components):
        name = h5file.attrs['component_'+str(i)].decode('utf-8')
        globals()[str(name)] =  b5.bisicles_var(file, i)
        print(name)
    h5file.close
    return 


def amr_varmeans(file):
    '''Create pandas dataseries with means and names of each variable, 
    append to dataframe. Not sure this function is useful anymore.'''
    names, n_components = get_varnames(file)
    df = pd.DataFrame(columns=names)
    var = [b5.bisicles_var(file, i) 
           for i in range(n_components)]
    means = [var_mean(i) for i in var]
    series = pd.Series(means, index = df.columns)
    df = df.append(series, ignore_index=True)
    return df


def get_varmeans(file, df, n_components):
    '''Create pandas dataseries of means and names of each 
    bisicles variable and extract time var.'''
    var = [b5.bisicles_var(file, i) for i in range(n_components)]
    means = [var_mean(i) for i in var]
    series = pd.Series(means, index = df.columns)
    t = var[0].time
    return series, t


def amr_meansdf(files):
    '''For each file in directory of files in a timeseries, 
    get var names, mean and time, appending to sorted dataframe.
    input: files in directory
    output: pandas dataframe'''
    names, n_components = get_varnames(files[0])
    df = pd.DataFrame(columns=names)
        
    res = Parallel(n_jobs=2)(delayed(get_varmeans)
                                            (f, df, n_components)
                                            for f in files) 
    series = [i[0] for i in res]
    time = [i[1] for i in res]
    
    df = df.append(series, ignore_index=True)
    df['time'] = time
    df = df.sort_values(by=['time'])
    df = df.reset_index(drop =True)
    return df

### 4. Compute the volume difference
### 5. Compute discharge, U
### 6. Compute BMB
### 7. Pass values to dataframe, as input to EC-Earth