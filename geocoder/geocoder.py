#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@ original author: ericlberlow

This script gets latitude and longitude for addresses  using the Google API geocoder
It requires a google api key - which is in the .bash_profile file
To use the .bash_profile you need to launch spyder from the terminal (not Anaconda)
You can either use an auto-rate limiter - or loop through the rows one-by-one with manual rate limiter
It returns the original datafraem with added lat/long columns. 
Addresses that failed lookup have empty lat,long.

"""

# %% ###########
### libraries and file paths
import sys
sys.path.append("../@commonFunctions")
import os
import pandas as pd
from geopy.geocoders import  GoogleV3 #, Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
pd.set_option('display.expand_frame_repr', False) # expand display of data columns if screen is wide


def geocode_addresses(df, address, test=False, autolimiter=True ):
                
    if test == True:
        print("subset 100 for testing")
        df = df.head(100)
    
    print("set up google api")
    KEY= os.environ.get("GOOGLE_MAPS_API_KEY") # start spyder from terminal to get from .bash_profile
    geolocator = GoogleV3(user_agent="ericberlow@gmail.com", api_key=KEY)
    
    if autolimiter == True:
        print("geocode with auto rate limiter")
        geocodeRL = RateLimiter(geolocator.geocode, min_delay_seconds=1)  #auto rate limiter
        df['location'] = df[address].apply(geocodeRL)
        df['Latitude'] = df['location'].apply(lambda x: x.latitude if x else '')
        df['Longitude'] = df['location'].apply(lambda x: x.longitude if x else '')

    else:
        print("geocode row by row with 1 second delay")
        locations = []
        for adrss in df[address]:
            location = geolocator.geocode(adrss)
            locations.append(location)
            time.sleep(1) # sleep for 1 sec between requests

        df['Latitude'] = [location.latitude if location else '' for location in locations]
        df['Longitude'] = [location.longitude if location else '' for location in locations]
        
    return df



