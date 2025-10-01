"""
Code snippet to jelp plotting, i/o and converting to strings.
"""

import pickle

def load_pkl(infilename): 
    """     
    Helper function to unpickle pkl file.

    Parameters
    ----------
    infilename : str
        input filename
    Returns
    ------
    unpickled file.  
    """
    pkl_file = open(f'{infilename}', 'rb')
    df = pickle.load(pkl_file)
    return df


def save_pkl(something, outfilename):
    """     
    Helper function to save something pkl file.

    Parameters
    ----------
    something : 
        something to pickle
    outfilename : str
        filename to save pkl to
    """
    output = open(outfilename, 'wb')
    pickle.dump(something, output)
    output.close()