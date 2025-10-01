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

    html_table = df.to_html(index=False, border=1)

    styled_html = f"""
    <html>
    <head>
        <style>
            table {{
                width: 60%;
                border-collapse: collapse;
                margin: 20px auto;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: center;
                white-space: nowrap;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        {html_table}
    </body>
    </html>
    """

    outfile = open(outfilename, "w")
    outfile.write(styled_html)
    outfile.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infilename", help="pickled pd.Dataframe containing nuclear tests from johnston archive", required=True)
    parser.add_argument("-o", "--outfilename", help="file to save exported html table to", required=True)

    args = parser.parse_args()

    main(args.infilename, args.outfilename)