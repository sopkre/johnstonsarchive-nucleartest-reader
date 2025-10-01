#!/usr/bin/env python3.13

"""
Snippet to add country codes and regions to dataframe containing longitude and latitude data.  

usage: add_geolocations.py [-h] -i INFILENAME -o OUTFILENAME -g OCEANSGEOMETRIES -j COUNTRYREGIONJSON
"""

import argparse
import helpers
import os.path

def get_cc_from_coordinates(coordlist, ocean_gpkg):
    """Get country codes from coordinate list via Nominatim and data on oceans.
    Parameters
    ---------
        coordlist : list of tuple 
            list of coordinates as (latitude, longitude) 
        ocean_gpkg : geopandas dataframe
            dataframe containing oceans (names and geometries, i.e. polygons)
    Returns
    ---------
        ccs : list of str 
            country codes (or ocean names with prefix "O_")    
        full_locations : list of dict
            full locations from Nominatim (or None, if ocean)
    """
    import geopy as gpy
    import geopandas as gp
    from geopy.extra.rate_limiter import RateLimiter
    from shapely.geometry import Point

    ccs = []
    full_locations = []

    # geopy for locations
    geolocator = gpy.Nominatim(user_agent="myapp")
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    # for seas
    seas_gdf = gp.read_file(ocean_gpkg)

    for i, coord in enumerate(coordlist):
        if (i%5==0):
            print(f'\r>> Processing... ({int(i/len(coordlist)*100)}%)', end='')
        geolocs = reverse(coord)

        if geolocs is not None and "country_code" in geolocs.raw["address"]:
            ccs += [ geolocs.raw["address"]["country_code"] ]
            full_locations += [ geolocs.raw ]
            continue
        
        full_locations += [None]

        p = Point(coord[1], coord[0])
        seas = seas_gdf[seas_gdf["geometry"].contains(p)]

        if len(seas) == 0: 
            print(f"[WARNING] No location for {coord}.")
            ccs += [None]
        elif len(seas) == 1:
            ccs += [f"O_{seas["name"].iloc[0]}"]
        else: 
            print("[ERROR] Found more than one matching ocean!")
            print(f"{seas["name"]}")
            ccs += [None]
    
    print('\r>> Processing... (100%)')

    return (ccs, full_locations)    


def get_regions_from_cc(cclist, jsonfile):
    """Convert list of country codes to list of regions.
    Parameters
    ---------
        cclist : list of str
            list of country codes (e.g., 'au' for Australia)
        jsonfile : str
            jsonfile with country codes and regions.
    """
    region_cc_dict = make_region_dict(jsonfile, key="cc")
    regions = []
    for cc in cclist:
        if cc[0:2]=="O_":
            regions += [cc[2:]]
        else:
            regions += [region_cc_dict[cc.upper()]]
    return regions


def make_region_dict(jsonfile, key="CC"): 
    """Take data from json file to get map for states, country codes, and UN geoscheme regions. 
    Parameters
    ---------
        key : str 
            "cc", for dict[CC]->region; "region", for dict[region)->[CC1,CC2,...] with cc is 2-digit country code
        jsonfile : str
            filename for json file countainig the data
    """
    import json
    with open(jsonfile, 'rb') as f:
        jsonfile = json.load(f)

    region_dict = {}

    for j in jsonfile:
        cc = j['alpha-2']
        region = j['sub-region']
        name = j['name']

        if key=='cc':
            region_dict[cc] = region
        elif key=='region':
            if region not in region_dict:
                region_dict[region] = [name]
            else: 
                region_dict[region] += [name]

    return region_dict


def main(infilename, outfilename, country_region_json, oceansgeometries):
    """Main. 
    Parameters
    ---------
        infilename : str 
            filename of pickled pd.Dataframe with explosion locations
        outfilename : str
            filename for pickled go.Figure
    """
    
    if not os.path.isfile(country_region_json):
        input(f"[WARNING] Json that connects states to regions does not exist. Will download it and save it as '{country_region_json}'. Press enter to continue...")
        import urllib.request
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/refs/heads/master/all/all.json", 
            country_region_json
        )

    df = helpers.load_pkl(infilename)
    df = df.drop(df[df.LAT.isnull()].index)

    df['coords'] = [ t for t in zip(df.LAT, df.LONG) ]
    (df['CC'], df['FULL_LOC']) = get_cc_from_coordinates(df.coords, ocean_gpkg=oceansgeometries)
    df['REGION'] = get_regions_from_cc(df['CC'], country_region_json)

    helpers.save_pkl(df, outfilename)
    print(f"[INFO] Saved dataframe as {outfilename}.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infilename", help="input data in pandas dataframe", required=True)
    parser.add_argument("-o", "--outfilename", help="output file, either html or pkl format.", required=True)
    parser.add_argument("-g", "--oceansgeometries", help="dataframe with ocean names and corresponding geometries as polygons. Can be obtained from Flanders Marine Institute (2021). Global Oceans and Seas, version 1. Available online at https://www.marineregions.org/. https://doi.org/10.14284/542", required=True)
    parser.add_argument("-j", "--countryregionjson", help="json that maps states to region. If file does not exist, it is downloaded.", required=True)
    args = parser.parse_args()

    main(args.infilename, args.outfilename, args.countryregionjson, args.oceansgeometries)
