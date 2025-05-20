#!/usr/bin/env python3.13

import argparse
import pickle
import yaml

import pandas as pd

def main(infilename, appendfilename, outfilename):
    """
    Adds data to the read-in data and saves the result. 

    Parameters
    ---------
    infilename : str 
        Filename of pickled pd.Dataframe. 
    appendfilename: str
        Filename of yaml with data to be added. 
    outputfilename : str 
        Filename to save the output pickle to.
    """
    pkl_file = open(infilename, 'rb')
    df = pickle.load(pkl_file)

    with open(appendfilename, 'r') as file:
        new_data = yaml.safe_load(file)

    new_data_dict = {}
    for test in new_data['data']:
        for cat in new_data['data'][test]:
            if cat not in new_data_dict:
                new_data_dict[cat] = [ new_data['data'][test][cat] ]
            else:
                new_data_dict[cat] += [ new_data['data'][test][cat] ]

    df_new = pd.DataFrame(new_data_dict)
    df = pd.concat([df, df_new], ignore_index=True)
    
    df.reset_index(drop = True, inplace = True)

    output = open(outfilename, 'wb')
    pickle.dump(df, output)
    output.close()

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infilename", help="pickled pd.Dataframe containing nuclear tests from johnston archive", required=True)
    parser.add_argument("-a", "--appendfilename", help="yaml with data to append", required=True)
    parser.add_argument("-o", "--outfilename", help="resulting pickled pd.Dataframe", required=True)

    args = parser.parse_args()

    main(args.infilename, args.appendfilename, args.outfilename)


