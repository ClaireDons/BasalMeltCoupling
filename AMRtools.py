import numpy as np
import xarray as xr
from glob import glob
import os 
import subprocess
import bisiclesh5 as b5
import pandas as pd
import h5py
from joblib import Parallel, delayed

class AMRobject:
    def __init__(self,file):
        self.file = file
        

    def var_mean(var, level=0):
        '''Calculate the mean value for each variable in bisicles file'''
        box_mean = [i.mean() for i in var.data[level]]
        mean0 = np.mean(box_mean)
        return mean0


    def get_varnames(self):
        '''Extract variable names and number of components for bisicles file'''
        h5file = h5py.File(self.file,'r')
        n_components = h5file.attrs['num_components']
        names = [h5file.attrs['component_'+str(i)].decode('utf-8') 
                for i in range(n_components)]
        h5file.close
        return names, n_components


    def unpack_amr(self):
        '''Unpack all the variables in bisicles file. 
        This function in current form needs work.'''
        h5file = h5py.File(self.file,'r')
        n_components = h5file.attrs['num_components']
        for i in range(n_components):
            name = h5file.attrs['component_'+str(i)].decode('utf-8')
            globals()[str(name)] =  b5.bisicles_var(self.file, i)
            print(name)
        h5file.close
        return 


    def amr_varmeans(self):
        '''Create pandas dataseries with means and names of each variable, 
        append to dataframe. Not sure this function is useful anymore.'''
        names, n_components = self.get_varnames()
        df = pd.DataFrame(columns=names)
        var = [b5.bisicles_var(self.file, i) 
            for i in range(n_components)]
        means = [self.var_mean(i) for i in var]
        series = pd.Series(means, index = df.columns)
        df = df.append(series, ignore_index=True)
        return df


    def get_varmeans(self, df, n_components):
        '''Create pandas dataseries of means and names of each 
        bisicles variable and extract time var.'''
        var = [b5.bisicles_var(self.file, i) for i in range(n_components)]
        means = [self.var_mean(i) for i in var]
        series = pd.Series(means, index = df.columns)
        t = var[0].time
        return series, t
    pass


class AMRtools(AMRobject):
    def __init__(self, path, files):
        self.path = path
        self.files = files


    def open_files(self):
        files = glob(os.path.join(self.path, "*.2d.hdf5"))
        return files


    def find_name(self,f):
        name = os.path.splitext(os.path.basename(f))[0]
        return name


    def flattenAMR(self,flatten):
        for f in self.files:
            name = self.find_name(self.path,f)
            nc = self.path + '/' + name + '.nc'
            flattenOutput = subprocess.Popen([flatten, f, nc, "0", "-3333500", "-3333500"], stdout=subprocess.PIPE)
            print(flattenOutput)
            output = flattenOutput.communicate()[0]
        return output


    def amr_meansdf(self):
        '''For each file in directory of files in a timeseries, 
        get var names, mean and time, appending to sorted dataframe.
        input: files in directory
        output: pandas dataframe'''
        names, n_components = AMRobject.get_varnames(self.files[0])
        df = pd.DataFrame(columns=names)
            
        res = Parallel(n_jobs=2)(delayed(AMRobject.get_varmeans)
                                                (f, df, n_components)
                                                for f in self.files) 
        series = [i[0] for i in res]
        time = [i[1] for i in res]
        
        df = df.append(series, ignore_index=True)
        df['time'] = time
        df = df.sort_values(by=['time'])
        df = df.reset_index(drop =True)
        return df
    pass