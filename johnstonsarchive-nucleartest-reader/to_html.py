#!/usr/bin/env python3.13

import pickle
import argparse

def main(infilename, outfilename): 
    """
    Exports pd.Dataframe to html table. 

    Parameters
    ---------
    infilename : str 
        Filename of pickled pd.Dataframe. 
    outputfilename : str 
        Filename to save the output html to.
    """
    infile = open(infilename, 'rb')
    df = pickle.load(infile)

    html_table = df.to_html()

    outfile = open(outfilename, "w")
    outfile.write(html_table)
    outfile.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infilename", help="pickled pd.Dataframe containing nuclear tests from johnston archive", required=True)
    parser.add_argument("-o", "--outfilename", help="file to save exported html table to", required=True)

    args = parser.parse_args()

    main(args.infilename, args.outfilename)