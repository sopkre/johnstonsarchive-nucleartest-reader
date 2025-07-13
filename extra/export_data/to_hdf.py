#!/usr/bin/env python3.13

import pickle
import argparse

def main(infilename, outfilename): 
    """
    Exports pd.Dataframe to hdf table. 

    Parameters
    ---------
    infilename : str 
        Filename of pickled pd.Dataframe. 
    outputfilename : str 
        Filename to save the output hdf to.
    """
    infile = open(infilename, 'rb')
    df = pickle.load(infile)
    
    # Cannot convert to hdf if those cols are of mixed types 
    # (appears when appending DPRK data)
    df["CRAT_occured"] = df["CRAT_occured"].astype(str)
    df["VENT_occured"] = df["VENT_occured"].astype(str)

    df.to_hdf(outfilename, key='data', data_columns=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infilename", help="pickled pd.Dataframe containing nuclear tests from johnston archive", required=True)
    parser.add_argument("-o", "--outfilename", help="file to save exported hdf to", required=True)

    args = parser.parse_args()

    main(args.infilename, args.outfilename)