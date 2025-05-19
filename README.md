# johnstonarchive-nucleartest-reader
Code to read, clean and parse the nuclear test data from https://www.johnstonsarchive.net/nuclear/tests/index.html 

## Run 

To read the data for the US nuclear weapon tests, you'd run the code as 
```
./read_johnston_data.py -i yaml/US_tables.yml -o US_dataframe.pkl
```
or, if you'd like to run over all yaml files and produce one output dataframe 
```
./read_johnston_data.py -i yaml -o alltests_dataframe.pkl
```