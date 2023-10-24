# BasalMeltCoupling


This repository contains the code for the freshwater coupling between BISICLES and EC-Earth3. 

For this code to function, you need to be working on a branch of EC-Earth3, which contains some changes for the freshwater distribution as well as an option for the BISICLES coupling. This can be found, along with this code, on the svn branch `branch name`. You also need to have BISICLES compiled somewhere on your system, instruction on how to do this can be found [here](https://davis.lbl.gov/Manuals/BISICLES-DOCS/readme.html), more specific ECMWF instructions can be found [here](https://github.com/BISICLES-users/BISICLES-notes/blob/main/BISICLES_ECMWF2020.md). 

This repository contains the following: 

=======
Scripts for basal melt / Freshwater coupling of BISICLES to EC-Earth
Additional changes and scripts are needed within EC-Earth


## Coupling scripts
![image](https://user-images.githubusercontent.com/82878115/221154886-f0c31171-538b-4a80-a459-ee6af2fa5d31.png)

## EC-Earth Changes

## NEMO files (compile nemo after these changes)
path: sources/nemo-3.6/CONFIG/ORCA1L75_LIM3/MY_SRC/
- sbc_oce.F90
- sbccpl.F90
- sbcfwf.F90
- sbcmod.F90
- sbcrnf.F90

## EC-Earth scripts
path: runtimes/classic/

- ece-esm.sh.tmpl
- config-run.xml
- wrapper-hpc2020.sh
- fwfwrapper.sh                 - calls python scripts from ece-esm.sh.tmpl             -
- /ctrl/namelist.nemo-ORCA1L75-coupled.cfg.sh 

### Input files
path: fwf/interactive/input

- areacello_Ofx_EC-Earth3_historical_r1i1p1f1_gn.nc
- basal_melt_mask_ORCA1_ocean.nc
- calving_mask_ORCA1_ocean.nc
- basal_melt_depth1.nc - created by InitialiseFreshwaterForcing.py 
- basal_melt_depth2.nc - created by InitialiseFreshwaterForcing.py
- FWF_LRF_y1850.nc - created by InitialiseFreshwaterForcing.py
- OceanSectorThetao_piControl.csv - mean ocean temperatures at depth of ice shelf base for piControl period

Note: after running InitialiseFreshwaterForcing.py 3 input files are created, you can also copy them from the input directory to the directory fwf/interactive/forcing_files/{exp}

path: fwf/
- runoff_maps_fwf_AIS.nc    - new file for runoff-mapper, excludes Antarctica

### Monitoring/output files
path: fwf/interactive/forcing_files

Output
- FWF_LRF_y????.nc - annual freshwater forcing file (basal melt + calving) to be read in by nemo

Monitoring
- OceanSectorThetao_{exp}_{year_min}_{year_max}.csv
- OceanSectorThetao_30yRM_{exp}_{year_min}_{year_max}.csv - 30 yr running mean
- BasalMeltAnomaly_{exp}_{year_min}_{year_max}.csv
- CumulativeFreshwaterForcingAnomaly_{exp}_{year_min}_{year_max}.csv
- TotalFreshwaterForcing_{exp}_{year_min}_{year_max}.csv - sum of anomalies + baseline

## BISICLES