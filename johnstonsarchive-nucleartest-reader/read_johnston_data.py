#!/usr/bin/env python3.13

import os
import yaml
import pickle 
import argparse

import pandas as pd

import JohnstonarchiveReader


def get_data_from_johnstonarchive(urls, lines, indices, statename):
    """
    Helper function to read data from the Johnstonarchive using the JohnstonarchiveReader
    
    Parameters
    ---------
    urls : list of strings
        urls of tables to read in
    lines: list of int
        lines in html file where tabular data starts 
    indices: dict 
    Nested dictionary. Keys: names/description for each col in table. Values: dicts with keys (1) "indices" (list of (int,int)) corresponding to the table cols (start, end of col)) and (2) "dtypes" (list of types) for reading the table col values. 
    statename: str
        name of the state; used for hardcoded typo fixes. 
    
    Returns
    -------
    data : pd.Dataframe
        Dataframe with extracted data. 
    """
    for i, url in enumerate(urls): 

        reader = JohnstonarchiveReader.JohnstonarchiveReader(statename=statename)
        reader.set_table_params(url=url, firstline=lines[i][0], lastline=lines[i][1])

        for key in indices: 
            reader.add_col_params(col_description=key, str_index_start=indices[key][0], str_index_end=indices[key][1], col_datatype=indices[key][2])

        reader.read_from_url()
        reader.read_data()

        reader.add_full_timestamp()

        if i==0:
            data = reader.get_dataframe()
        else: 
            data = pd.concat([data, reader.get_dataframe()])

        # reader.print_for_visual_check_of_col_indices()

    return data


def main(yamlfilename, outputfilename):
    """
    Main function to read data from the johnston nuclear weapon test database. 

    Parameters
    ---------
    yamlfilename : str or list of str
        Settings for data reading. Can be single yaml-file or folder with yaml-files.
    outputfilename : str 
        Filename to save the output pickle to.
    """

    print("----------------------------------")
    print(f"### INPUTFILE: {yamlfilename} ###")
    print("----------------------------------")
    print()

    yamlfilename_list = [yamlfilename]

    if os.path.isdir(yamlfilename): 
        yamlfilename_list = [f"{yamlfilename}/{f}" for f in os.listdir(yamlfilename)]

    data = 0
    for i, yamlfilename in enumerate(yamlfilename_list):

        print(f"[INFO] Extracting data using {yamlfilename}.")

        with open(yamlfilename, 'r') as file:
            settings = yaml.safe_load(file)

        statename = settings["general"]["state"]
        urls = settings["html_general"]["urls"]
        table_lines_in_html = settings["html_general"]["table_lines_in_html_file"]
        indices_dtypes = settings["columns"]

        dataypes_map = {"int" : int, "float": float, "str": str }
        for key in indices_dtypes:
            indices_dtypes[key][2] = dataypes_map[indices_dtypes[key][2]]

        data_state = get_data_from_johnstonarchive(urls, table_lines_in_html, indices_dtypes, statename)
        data_state["STATE"] = statename

        if i==0:
            data = data_state
        else: 
            data = pd.concat([data, data_state])

    data.reset_index(drop = True, inplace = True)

    output = open(outputfilename, 'wb')
    pickle.dump(data, output)
    output.close()

    print(f"[INFO] Saved extracted output at {outputfilename}.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--infilename", help="yaml file with settings", required=True)
    parser.add_argument("-o", "--outfilename", help="pickle with read data", required=True)

    args = parser.parse_args()

    main(args.infilename, args.outfilename)
