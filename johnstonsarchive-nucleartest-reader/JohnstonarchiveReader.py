
import numpy as np
import pandas as pd
import urllib.request

import pprint


def make_extended_array(arr, descr_to_add):
    """Helper function to create new array with entries of existing array plus new empty cols. 
    
    Parameters
    ---------
    arr : np.array 
        existing array that is base for new array. 
    descr_to_add : list
        description and type of empty cols to add, e.g. [('TITLE', 'float')] 
    
    Returns
    -------
    new_arr : np.array
        new array with entries of existing array plus new empty cols. 
    """

    new_dt = np.dtype(arr.dtype.descr + descr_to_add)
    new_arr = np.zeros(arr.shape, dtype=new_dt)
    for (descr, dt) in arr.dtype.descr:
        new_arr[descr] = arr[descr]
    return new_arr


class JohnstonarchiveReader():
    """ Class to read tabular data from the johnston archive of nuclear weapons tests, clean it up, and return it as numpy array or pandas dataframe.

    Attributes
    ----------
    col_parameters_ : dict
        Nested dictionary. Keys: names/description for each col in table. Values: dicts with keys (1) "indices" (list of (int,int)) corresponding to the table cols (start, end of col)) and (2) "dtypes" (list of types) for reading the table col values. 
    data_ : numpy array
        Structured array of extracted data. Description contains the keys from col_parameters_ and corresponding dtypes. 
    statename_ : str
        Name of state the data belongs to. 
    firstline_ : int
        Line number of first line in table at url
    lastline_ : int
            Line number of last line in table at url
    """

    def __init__(self, statename = ""): 
        self.col_parameters_ = {}
        self.data_ = []
        self.statename_ = statename

    def set_table_params(self, url, firstline=0, lastline=-1):
        self.url_ = url
        self.firstline_ = firstline
        self.lastline_ = lastline

    def get_col_descriptions(self):
        return [k for k in self.col_parameters_]

    def add_col_params(self, col_description, str_index_start, str_index_end, col_datatype):
        self.col_parameters_[col_description] = {}
        self.col_parameters_[col_description]["indices"] = (str_index_start, str_index_end)
        self.col_parameters_[col_description]["dtype"] = col_datatype

    def read_from_url(self):
        body = urllib.request.urlopen(self.url_).read()
        decoded_body = body.decode("utf-8")
        decoded_body = decoded_body.splitlines()[self.firstline_:self.lastline_]
        self.decoded_body_ = decoded_body

    def read_data(self):
        """
            Goes through table from url and reads values from given indices. Calls certain fix and cleanup functions.  
        """
        data = [ [0 for _ in self.col_parameters_] for j in self.decoded_body_ ]
        
        for i, line in enumerate(self.decoded_body_):
            for j, (descr, par_dict) in enumerate(self.col_parameters_.items()):
                value = line[ par_dict["indices"][0]:par_dict["indices"][1] ]
                if value.strip() == "":
                    data[i][j] = None
                else: 
                    data[i][j] = value.strip()

        dt = [ (n, 'object') for n in self.col_parameters_] # Nones prevent setting better dtypes for array; done later for pandas dataframe however
        self.data_ = np.array( [tuple(x) for x in data], dtype = np.dtype(dt))
        
        self.clean_typos_and_column_spillovers()

        self.fix_yield_values()
        self.fix_est_yield_values()
        self.add_crat_bool_and_values()
        self.add_vent_bool_and_values()

        self.convert_data()

    def convert_data(self):
        """
            Converts read out values to desired datatypes. 
        """
        for (descr, par_dict) in self.col_parameters_.items():
            if par_dict["dtype"] is int or par_dict["dtype"] is float:
                for i, val in enumerate(self.data_[descr]):
                    if val is not None:
                        try:
                            self.data_[descr][i] = par_dict["dtype"] (val)
                        except ValueError:
                            assert False, f"Cannot convert column {descr} to numeric. "

    def clean_typos_and_column_spillovers(self):
        """
            Goes through data and fixes general typos and column values that spill over; details in specific comments. 
        """
        for i, d in enumerate(self.data_):

            d["ID"] = int(d["ID"])

            # Enable int for the DAY column
            if d["DAY"] is None: 
                d["DAY"] = -1 

            # Fix typo in time col (US table)
            t = d["TIME"]
            if t is not None:
                d["TIME"] = t.replace(';', ':') 

            # Fix some typos for USSR in YIELD col
            if self.statename_ == "USSR":
                if (d["ID"] == 158): # removes question mark from col before.
                    print(f"[INFO] (ID {d["ID"]}): ('{d["YIELD"]}') => ('23') for YIELD.")
                    d["YIELD"] = 23 
                elif (d["ID"] == 520): # fixes stray 44 - no idea what it belongs to.
                    print(f"[INFO] (ID {d["ID"]}): ('{d["YIELD"]}') => ('130') for YIELD.")
                    d["YIELD"] = 130 
                elif (d["ID"] == 846): # removes two stray asterisks - no idea what they belong to.  
                    print(f"[INFO] (ID {d["ID"]}): ('{d["YIELD"]}') => ('85') for YIELD.")
                    d["YIELD"] = 85 

            # Fix lines that spill over from SHOTNAME to SHOTTYPE
            s = d["SHOTTYPE"]
            n = d["SHOTNAME"]
            if s not in [None, "SS", "S", "X", "*", "?"]:
                print(f"[INFO] (ID {d["ID"]}): ('{n}' | '{s}') => ('{n+s}' | 'None') for (SHOTNAME | SHOTTYPE)")
                d["SHOTNAME"] = n + s
                d["SHOTTYPE"] = None

            # Fix lines that spill over from WARHEAD to SPONSOR
            s = d["SPONSOR"]
            w = d["WARHEAD"]
            if s not in [None, "KB-11", "Ch-70", "KB-11?", "Ch-70?", "LANL", "LLNL", "DOD", "UK", "SNL"]:
                if w is not None:
                    print(f"[INFO] (ID {d["ID"]}): ('{w}' | '{s}') => ('{w+s}' | 'None') for (WARHEAD | SPONSOR)")
                    d["WARHEAD"] = w + s
                    d["SPONSOR"] = None

            # Fix lines that spill over from SPONSOR to R and N
            s = d["SPONSOR"]
            r = d["R"]
            n = d["N"]
            if r not in [None, "A", "S", "P", "X"]:
                if s is not None and n is not None:
                    print(f"[INFO] (ID {d["ID"]}): ('{s}' | '{r}'| '{n}') => ('{s+r+n}' | 'None' | 'None' )  for (SPONSOR | R | N)")
                    d["SPONSOR"] = s + r + n
                    d["R"] = None
                    d["N"] = None

            # Fix cut off sponsor
            if s == "KB-11/" or s == "KB-11/Ch-7":
                d["SPONSOR"] = "KB-11/Ch-70"

            # Fix lines that spill over from VENT to DEVICE
            dv = d["DEVICE"]
            v = d["VENT"]
            if dv not in [None, "IP", "BF", "TN", "FS", "TN?", "FZ", "IC", "IP", "IU", "ND", "SL"]:
                if v is not None:
                    print(f"[INFO] (ID {d["ID"]}): ('{v}' | '{dv}') => ('{v+dv}' | 'None') for (VENT | DEVICE)")
                    d["VENT"] = v + dv
                    d["DEVICE"] = None 

            # Fix lines that spill over from YD-EST to YIELD-NT
            y = d["YD-EST"]
            ynt = d["NT-YD"]
            if ynt not in [None, "MX", "E", "?", "S", "T", "T*", "S>", "T>", "**", "R? S"]:
                if y is not None:
                    print(f"[INFO] (ID {d["ID"]}): ('{y}' | '{ynt}') => ('{y+ynt}' | 'None') for (YD-EST | NT-YD)")
                    d["YD-EST"] = y + ynt
                    d["NT-YD"] = None

        print("\n ### [INFO] Cleaned general typos and column spillovers. ### \n")

    def get_data(self):
        return self.data_

    def get_dataframe(self):
        df = pd.DataFrame(self.data_)

        for j, (descr, par_dict) in enumerate(self.col_parameters_.items()):
            if par_dict["dtype"] is int or par_dict["dtype"] is float:
                try:
                    df[descr] = pd.to_numeric(df[descr])
                except ValueError:
                    print(f"Cannot convert col {descr} to numeric. ")
        return df

    def print_for_visual_check_of_col_indices(self):
        """
            Helper function to verify index settings for col selection. Prints table from website with pipes to visualise chosen col boundaries. 
        """
        text = self.decoded_body_.copy()

        inds_end = [ par_dict["indices"][1] for (_, par_dict) in self.col_indices_]
        n_added_symbols = 0
        for i in range(len(text)):
            for j, ind_end in enumerate(inds_end):
                ind = ind_end + n_added_symbols
                text[i] = text[i][:ind] + "|" + text[i][ind:]
                n_added_symbols += 1
            n_added_symbols = 0
        
        pprint.pprint(text, width=400)

    def add_full_timestamp(self):
        """
            Adds complete timestamp to the data based on given year, month, day, and time.
        """
        assert len(self.data_) != 0, "[ERROR] Need to read data first. "

        months = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY": 5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}

        datetimes = []
        for d in self.data_:
            (y, m, d, t) = (d["YEAR"], d["MON"], d["DAY"], d["TIME"]) 
            if t is None: 
                datetimes += [np.datetime64("NaT")]
            else:
                datetimes += [ np.datetime64(f"{y}-{months[m]:02}-{d:02} {t}") ]

        data_with_datetimes = make_extended_array(self.data_, [('DATETIME', 'object')]) 
        data_with_datetimes['DATETIME'] = datetimes

        self.data_ = data_with_datetimes


    def add_vent_bool_and_values(self):
        """
            Parses vent values. VENT_orig saves untouched table entry; VENT given value, VENT_occured whether vent occured (indicated with "V" in table); VENT_value_remark if value indicates limit (indicated with < or >); also specific typo fixes. 
        """
        assert len(self.data_) != 0, "[ERROR] Need to read data first."

        self.data_.dtype.names = [f'{x}_orig' if x in ['VENT'] else x for x in self.data_.dtype.names]

        data_with_vent_info = make_extended_array(self.data_, [
            ('VENT', 'float'),
            ('VENT_occured', 'bool'), 
            ('VENT_value_remark', object)
            ]) 

        f = 0
        for i, d in enumerate(data_with_vent_info):
            vent = d["VENT_orig"]
            d["VENT_value_remark"] = None

            if vent in ["", None]:
                d["VENT_occured"] = False
                d["VENT"] = None
                continue

            if vent.find("V") > -1: 
                d["VENT_occured"] = True
                vent = vent.replace("V", "")
                if vent.strip() == "":
                    d["VENT"] = None
                    continue
            
            if self.statename_ == "US" and d["ID"] == 245:
                d["VENT_occured"] = True
                d["VENT"] = 1600
                print(f"[INFO] (ID {d["ID"]}): '{d["VENT"]}' (VENT) => '{d["VENT"]}' (VENT)")
                continue

            if self.statename_ == "US" and d["ID"] == 265:
                d["VENT_occured"] = True
                d["VENT"] = 15e6
                print(f"[INFO] (ID {d["ID"]}): '{d["VENT"]}' (VENT) => '{d["VENT"]}' (VENT)")
                continue

            if self.statename_ == "USSR" and d["ID"] == 356:
                d["VENT_occured"] = True
                d["VENT"] = 2e6
                print(f"[INFO] (ID {d["ID"]}): '{d["VENT"]}' (VENT) => '{d["VENT"]}' (VENT)")
                continue
        
            if self.statename_ == "USSR" and d["ID"] == 378:
                d["VENT_occured"] = True
                d["VENT"] = 15
                print(f"[INFO] (ID {d["ID"]}): '{d["VENT"]}' (VENT) => '{d["VENT"]}' (VENT)")
                continue
            
            if self.statename_ == "USSR" and d["ID"] == 431:
                d["VENT_occured"] = True
                d["VENT"] = 15
                print(f"[INFO] (ID {d["ID"]}): '{d["VENT"]}' => '{d["VENT"]}' for VENT")
                continue

            vent = vent.replace("Ci", "")

            if vent.find("k") > -1:
                vent = vent.replace("k", "")
                f = 1000
            elif vent.find("M") > -1:
                vent = vent.replace("M", "")
                f = 1e6
            else:
                f = 1
        
            if vent.find("<") > -1:
                vent = vent.replace("<", "")
                d["VENT_value_remark"] = "<"
            elif vent.find(">") > -1:
                vent = vent.replace(">", "")
                d["VENT_value_remark"] = ">"
            try: 
                d["VENT"] = f * float(vent)
            except ValueError: 
                assert False, print(f"=========> Issue at ID {d['ID']} and VENT {d['VENT_orig']}")

        print("\n ### [INFO] Cleaned VENT data. ### \n")
        self.data_ = data_with_vent_info


    def fix_yield_values(self):
        """
            Parses yield values. YIELD_orig saves untouched table entry and YIELD_value_remark if value indicates limit (indicated with < or >) or range.
        """
        assert len(self.data_) != 0, "[ERROR] Need to read data first."
        
        if 'YIELD_orig' in self.data_.dtype.names:
            return 0 
        
        self.data_.dtype.names = [f'{x}_orig' if x=='YIELD' else x for x in self.data_.dtype.names]

        data_with_float_yields = make_extended_array(self.data_, [
            ('YIELD', 'float'), 
            ('YIELD_value_remark', object), 
        ]) 

        # Fix yield 
        for i, d in enumerate(data_with_float_yields):
            d["YIELD_value_remark"] = None
            if isinstance(d["YIELD_orig"], float): 
                d["YIELD"] = d["YIELD_orig"]
            elif self.statename_ == "USSR" and d["ID"] == 550:
                d["YIELD"] = 100 # in table: 70-130? - choosing middle
                d["YIELD_value_remark"] = "mid of range"
            else:
                try: 
                    if d["YIELD_orig"] in [None, ""]:
                        d["YIELD"] = None
                    else:
                        d["YIELD"] = float(d["YIELD_orig"])
                except ValueError:
                    assert False, f"=========> ERROR! With ID {d['ID']} and YIELD: {d['YIELD_orig']}"

        self.data_ = data_with_float_yields

        print("\n ### [INFO] Cleaned YIELD data. ### \n")


    def fix_est_yield_values(self):
        """
            Parses estimated yield values. YD-EST_orig saves untouched table entry and YD-EST_value_remark if value indicates limit (indicated with < or >) or range or uncertainty (indicated with ?).
        """

        assert len(self.data_) != 0, "[ERROR] Need to read data first."

        if 'YD-EST_orig' in self.data_.dtype.names:
            return 0 

        self.data_.dtype.names = [f'{x}_orig' if x=='YD-EST' else x for x in self.data_.dtype.names]

        data_with_float_yields = make_extended_array(self.data_, [
            ('YD-EST', 'float'),
            ('YD-EST_value_remark', object)
        ]) 

        # Fix yield 
        for i, d in enumerate(data_with_float_yields):
            d["YD-EST_value_remark"] = None
            if isinstance(d["YD-EST_orig"], float):
                d["YD-EST"] = d["YD-EST_orig"]
            elif self.statename_ == "USSR" and d["ID"] == 158: 
                    d["YD-EST"] = 23.5 # in table: 20-27kt - choosing middle
                    d["YD-EST_value_remark"] = "mid of range"
            elif self.statename_ == "USSR" and d["ID"] == 437: 
                    d["YD-EST"] = 150 # in table: 150/100 - choosing first number
                    d["YD-EST_value_remark"] = "?"
            elif self.statename_ == "USSR" and d["ID"] == 949: 
                    d["YD-EST"] = 150 # in table: 150/118 - choosing first number
                    d["YD-EST_value_remark"] = "?"
            else: 
                try: 
                    if d["YD-EST_orig"] in [None, ""] :
                        d["YD-EST"] = None
                    else: 
                        if d["YD-EST_orig"].find("<") > -1:
                            d["YD-EST_value_remark"] = "<"
                            d["YD-EST"] = float( (d["YD-EST_orig"]).replace("<", "") )
                except ValueError:
                    assert False, f"=========> Issue at ID {d['ID']} and YD-EST: {d['YD-EST_orig']}"
    
        self.data_ = data_with_float_yields

        print("\n ### [INFO] Cleaned YD-EST data. ### \n")


    def add_crat_bool_and_values(self):
        """
            Parses crater values. CRAT_orig saves untouched table entry; CRAT given value; CRAT_occured whether crater occured (indicated with "C" in table); CRAT_value_remark if there is uncertainty (markerd with ?).
        """
        assert len(self.data_) != 0, "[ERROR] Need to read data first."

        if 'CRAT_orig' in self.data_.dtype.names:
            return 0 

        self.data_.dtype.names = [f'{x}_orig' if x in ['CRAT'] else x for x in self.data_.dtype.names]

        data_with_crat_info = make_extended_array(self.data_, [
            ('CRAT', 'float'),
            ('CRAT_occured', 'bool'), 
            ('CRAT_value_remark', object)
            ]) 

        for i, d in enumerate(data_with_crat_info):
            crat = d["CRAT_orig"]
            d['CRAT_value_remark'] = None

            if crat in ["", None]:
                d["CRAT_occured"] = False
                d["CRAT"] = None
                continue

            if crat.find("C") > -1: 
                d["CRAT_occured"] = True
                crat = crat.replace("C", "")
                if crat.strip() == "":
                    d["CRAT"] = None
                    continue
            
            if crat.find("?") > -1: 
                d["CRAT_occured"] = False
                crat = crat.replace("?", "")
                if crat.strip() == "":
                    d["CRAT"] = None
                    d["CRAT_value_remark"] = '?'
                    continue

            try: 
                d["CRAT"] = float(crat)
                if d["CRAT"] > 0 and d["CRAT"] is not None:
                    d["CRAT_occured"] = True
            except ValueError: 
                assert False, f"=========> Issue at ID {d['ID']} and CRAT = {d['CRAT_orig']}"

        print("\n ### [INFO] Cleaned crat data. ### \n")
        self.data_ = data_with_crat_info