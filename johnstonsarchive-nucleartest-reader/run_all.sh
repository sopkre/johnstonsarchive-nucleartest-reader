

# Run johnstonarchive web to dataframe reading
python3.13 read_johnston_data.py -i yaml -o ../obtained_data/johnstonarchive_nucleartests_dataframe.pkl 

# Append DPRK data 
cd ../extra/append_data
python3.13 append_data.py -i ../../obtained_data/johnstonarchive_nucleartests_dataframe.pkl -a DPRK_data.yml -o ../../obtained_data/johnstonarchive_nucleartests_incl_latestDPRK_dataframe.pkl
cd ../../johnstonsarchive-nucleartest-reader/

# Export data too html, hdf, and csv
cd ../extra/export_data
python3.13 to_html.py -i ../../obtained_data/johnstonarchive_nucleartests_incl_latestDPRK_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_incl_latestDPRK_htmltable.html 
python3.13 to_html.py -i ../../obtained_data/johnstonarchive_nucleartests_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_htmltable.html 

 python3.13 to_hdf.py -i ../../obtained_data/johnstonarchive_nucleartests_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_hdftable.hdf 
 python3.13 to_hdf.py -i ../../obtained_data/johnstonarchive_nucleartests_incl_latestDPRK_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_incl_latestDPRK_hdftable.hdf 

 python3.13 to_csv.py -i ../../obtained_data/johnstonarchive_nucleartests_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_csvtable.csv 
 python3.13 to_csv.py -i ../../obtained_data/johnstonarchive_nucleartests_incl_latestDPRK_dataframe.pkl -o ../../obtained_data/johnstonarchive_nucleartests_incl_latestDPRK_csvtable.csv 
 cd ../../johnstonsarchive-nucleartest-reader/
