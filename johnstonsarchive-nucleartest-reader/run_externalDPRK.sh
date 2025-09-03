

# Run johnstonarchive web to dataframe reading

python3.13 read_johnston_data.py -i yaml -o ../obtained_data/johnstonarchive_nucleartests_dataframe.pkl 

# First, delete DPRK data extracted from Johnson archive, append DPRK data from external
cd ../extra/append_data

python3.13 append_data.py -i ../../obtained_data/johnstonarchive_nucleartests_dataframe.pkl -a DPRK_data_complete.yml -o ../../obtained_data/johnstonarchive_nucleartests_externalDPRK_dataframe.pkl -d DPRK

cd ../../johnstonsarchive-nucleartest-reader/

# Export data to html, hdf, and csv
cd ../extra/export_data
python3.13 to_html.py -i ../../obtained_data/johnstonarchive_nucleartests_externalDPRK_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_externalDPRK_dataframe.html 

 python3.13 to_hdf.py -i ../../obtained_data/johnstonarchive_nucleartests_externalDPRK_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_externalDPRK_dataframe.h5 

 python3.13 to_csv.py -i ../../obtained_data/johnstonarchive_nucleartests_externalDPRK_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_externalDPRK_dataframe.csv 

 cd ../../johnstonsarchive-nucleartest-reader/
