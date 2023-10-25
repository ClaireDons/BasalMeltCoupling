# BasalMeltCoupling


This repository contains the code for the freshwater coupling between BISICLES and EC-Earth3. 

For this code to function, you need to be working on a branch of EC-Earth3, which contains some changes for the freshwater distribution as well as an option for the BISICLES coupling. This can be found, along with this code, on the svn branch `r9469-cmip6-bisi-knmi`. You also need to have BISICLES compiled somewhere on your system, instruction on how to do this can be found [here](https://davis.lbl.gov/Manuals/BISICLES-DOCS/readme.html), more specific ECMWF instructions can be found [here](https://github.com/BISICLES-users/BISICLES-notes/blob/main/BISICLES_ECMWF2020.md). A brief overview of changes that were made to EC-Earth are also outlined in this document. 

The coupling is closely related to the linear response function freshwater coupling, that has been integrated into OptiESM and uses a similar structure and communal code. 

### Work To Do & current issues
- BISICLES is currently not compiled in the svn branch due to compilation issues.
- Some changes were made to how the freshwater is distributed for Eveline's code, this branch needs to be updated with these changes too.
- How the location of input files is defined in `compute_basalmelt.py` rather than `BasalMeltCoupling.sh` is inconvenient and should be changed
- Note that OptiESM may have taken over option fwf=5 for something else, so it may need to be updated to fwf=6

## Content Table
1. Installation
2. How the coupling works
3. Running EC-Earth with freshwater coupled
4. Changes to EC-Earth (taken from Eveline's LRF changes)

## 1. Installation

### Pre-requisites
- Correct branch of EC-Earth or make your own changes
- BISICLES compiled
- BISICLES initialised set-up, either BEDMAP2 or BedMachine3.
- Input files for freshwater calculation (see section 3)

### Download
- Clone repository from github or if using BISICLES branch then the code will already be there.

- What the file structure looks like 

## 2. How the coupling works
`BasalMeltCoupling.sh` controls the coupling, most changes when running the code are made here. The code loads all necessary modules and python environment and then runs the basal melt calculation `compute_basalmelt.py`, runs BISICLES, waits for it to finish and then runs the freshwater calculation `compute_freshwater.py`. The script is called at the end of each EC-Earth leg. Once it has finished running the following leg is run. This flowchart below depicts how each bit of code work together. 


![image](https://user-images.githubusercontent.com/82878115/221154886-f0c31171-538b-4a80-a459-ee6af2fa5d31.png)


## 3. Running EC-Earth with freshwater coupled

To run the model with the freshwater coupling turned on. Make sure that `config_run.xml` is set to use the fwf=5 option and any other information EC-Earth needs as standard (e.g. experiment name, start date etc). 
The initialised ice sheet model setup is modern day, so it is best to restart EC-Earth from the year 2000 or run BISICLES with 1850 conditions for several years until it stabilises. 

Copy or create a directory with the bisicles input data in your scratch directory. 

!! Due to the file system used in perm and home, the data cannot be read from there and you need to read it from scratch. You can keep a permanent copy in perm or home, but you will get an error if running from there !! 

Within the BasalMeltCoupling directory, create or copy an "inputs" directory, which then contains directories of the following:
- "ec-earth_data": same input as for fwf lrf functions (see section 4)
- "forcing": where fwf files are output, 1st year file needs to be present before running ec-earth
- "levermann_masks": region masks for BISICLES (in hdf5 format)

These can be put elsewhere but then you need to make sure the code points to them correctly. This would require editing `compute_basalmelt.py` where this is defined. 

`BasalMeltCoupling.sh` needs to be edited with the following information:
- Path to compiled BISICLES driver
- BISICLES driver names
- Gamma value that you want to use
- Scratch path
- Location of bisicles input data

- Optionally, you can change the paths in the "paths" section, if you have a different setup

Other files should not need to be edited unless you want to modify functionalities. 

Edit the `wrapper-hpc2020.sh` so that `fwf=5`, then you can run ec-earth by running `wrapper-hpc2020.sh` 

The output files from bisicles should be found alongside the output files from nemo and ifs in the scratch directory with the experiment name. The exception to this is the freshwater forcing files that are currently found in perm. 


## 4. Changes to EC-Earth

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
