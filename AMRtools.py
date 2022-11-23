import os
from glob import glob
import numpy as np
import subprocess
from joblib import Parallel, delayed
import multiprocessing
import h5py
import pandas as pd

import bisiclesh5 as b5

class AMRobject:
    def __init__(self,file):
        self.file = file # file name


    def find_name(self):
        name = os.path.splitext(os.path.basename(self.file))[0]
        assert len(name) > 0, "name is empty"
        return name


    def flatten(self,flatten):
        name = self.find_name()
        nc = name + '.nc'
        flattenOutput = subprocess.Popen([flatten, self.file, nc, "0", "-3333500", "-3333500"], stdout=subprocess.PIPE)
        # assess
        flattenOutput.communicate()[0]


    def varmean(var, level=0):
        '''Calculate the mean value for each variable in bisicles file'''
        box_mean = [i.mean() for i in var.data[level]]
        mean0 = np.mean(box_mean)
        return mean0


    def get_names(self):
        '''Extract variable names and number of components for bisicles file'''
        h5file = h5py.File(self.file,'r')
        n_components = h5file.attrs['num_components']
        names = [h5file.attrs['component_'+str(i)].decode('utf-8') 
                for i in range(n_components)]
        h5file.close
        return names, n_components


    def get_varmeans(self, df, n_components):
        '''Create pandas dataseries of means and names of each 
        bisicles variable and extract time var.'''
        var = [b5.bisicles_var(self.file, i) for i in range(n_components)]
        means = [self.varmean(i) for i in var]
        series = pd.Series(means, index = df.columns)
        t = var[0].time
        return series, t


    def statsRun(self, driver):
        '''Function to run the BISICLES stats module and returns the output as plain text.
        path: path to driver
        driver: driver name
        file: plot file to be processed'''
        
        statsCommand = driver + ' ' + self.file + ' 918 1028 9.81 | grep time'
        statsOutput = subprocess.check_output(statsCommand,shell=True)
        statsOutput = statsOutput.decode('utf-8')
        return statsOutput


    def statsSeries(statsOutput, df):
        '''Function to take the BISICLES stats module output and turn it into a pandas data series.
        statsOutput: Output from the stats command
        df: a dataframe with the columns for the variables defined'''
        
        stats = statsOutput.split()
        data = [float(stats[2]),stats[5],stats[8],stats[11],stats[14],stats[17],stats[20]]
        a_series = pd.Series(data, index = df.columns)
        return a_series


    def statsRetrieve(self, driver, df):
        '''Function which calls the BISICLES stats module and returns a pandas data series
        path: path to driver
        driver: driver name
        file: plot file to be processed
        df: a dataframe with the columns for the variables defined'''
        
        statsOutput = self.statsRun(driver)
        a_series= self.statsSeries(statsOutput, df)
        return a_series
    pass


class AMRtools(AMRobject):
    def __init__(self, path):
        self.path = path


    def open_files(self):
        files = glob(os.path.join(self.path, "*.2d.hdf5"))
        return files


    def flattenAMR(self,flatten):
        files = self.open_files()
        for f in files:
            AMRobject.flatten(f,flatten)


    def nc2AMR(self,nc2amr, var):
        files = self.open_files()
        for f in files:
            name = AMRobject.find_name(f)
            amr = self.path + '/' + name + '.2d.hdf5'
            flattenOutput = subprocess.Popen([nc2amr, f, amr, var], stdout=subprocess.PIPE)
            # assess
            output = flattenOutput.communicate()[0]
        return output        

    def lev0means(self):
        '''For each file in directory of files in a timeseries, 
        get var names, mean and time, appending to sorted dataframe.
        input: files in directory
        output: pandas dataframe'''

        files = self.open_files()
        names, n_components = AMRobject.get_varnames(files[0])
        df = pd.DataFrame(columns=names)
            
        res = Parallel(n_jobs=2)(delayed(AMRobject.get_varmeans)
                                                (f, df, n_components)
                                                for f in files) 
        series = [i[0] for i in res]
        time = [i[1] for i in res]
        
        df = df.append(series, ignore_index=True)
        df['time'] = time
        df = df.sort_values(by=['time'])
        df = df.reset_index(drop =True)
        return df


    def stats(self, statsTool):
        '''Function which runs the BISICLES stats module over multiple plot files in parallel
        path: path to driver
        driver: driver name
        files: plot files to be processed'''
        
        files = self.open_files()
        num_jobs = multiprocessing.cpu_count()
        df = pd.DataFrame(columns = 
                        ["time", "volumeAll", "volumeAbove", "groundedArea", 
                        "floatingArea", "totalArea", "groundedPlusLand"])  
        series_list = Parallel(n_jobs=num_jobs)(delayed(self.statsRetrieve)
                                                (statsTool,i,df)
                                                for i in files) 
        df = df.append(series_list, ignore_index=True)
        df = df.sort_values(by=['time'])
        df = df.reset_index(drop =True)
        return df

    pass