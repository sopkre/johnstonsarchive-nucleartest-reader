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
./append_data.py -i INPUT.pkl -a DPRK_data.yml -o INPUT_PLUS_DATA.pkl
```
in the extra folder.


## Obtained data

In obtained_data, you can find the extracted data as pickled pd.Dataframe or exported html table to directly download and use. Both the pure JohnstonArchive data and these with appended latest DPRK tests is available. 
