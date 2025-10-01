# johnstonarchive-nucleartest-reader
Code to read, clean up and parse the nuclear test data from https://www.johnstonsarchive.net/nuclear/tests/index.html 


## Run data extraction  

To read the data for the US nuclear weapon tests, you'd run the code as 
```
./read_johnston_data.py -i yaml/US_tables.yml -o US_dataframe.pkl
```
or, if you'd like to run over all yaml files and produce one output dataframe 
```
./read_johnston_data.py -i yaml -o alltests_dataframe.pkl
```

## Append data 

The Johnston Archive only lists two nuclear weapon tests of DPRK. Since 2013, there are four more, which can be added via 
```
./append_data.py -i INPUT.pkl -a DPRK_data.yml -o OUTPUT.pkl
```
in the extra folder.


## Obtained data

In obtained_data, you can find the extracted data as pickled pd.Dataframe or exported html table to directly download and use. The following csv versions are available (other formats similarly): 

- ```johnstonarchive_nucleartests_csvtable.csv```: plain johnston archive data
- ```johnstonarchive_nucleartests_externalDPRK_csvtable.csv```: johnston archive, but DPRK taken from [here](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022JB024728)
- ```johnstonarchive_nucleartests_externalDPRK_inclGeolocs_csvtable.csv```: version above but with geolocation information attached


## Add geolocations 

To add information on the geolocation of test coordinates, use 
```
usage: add_geolocations.py [-h] -i INFILENAME -o OUTFILENAME -g OCEANSGEOMETRIES -j COUNTRYREGIONJSON
```
where ```OCEANSGEOMETRIES``` is a .gpkg file that contains all ocean bounding boxes (I take the file from: Flanders Marine Institute (2021). Global Oceans and Seas, version 1. Available online at https://www.marineregions.org/. https://doi.org/10.14284/542), and ```COUNTRYREGIONJSON``` a file mapping the country code (CC) to the UN geoscheme region (if it does not exist, it will be downloaded from [here](https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/refs/heads/master/all/all.json))