# -*- coding: utf-8 -*-
"""
Ed learning how this all fits together...
cc == country codes
['UK','IRE','AUS']
"""

import os
import imp
os.getcwd()
os.chdir('C:/dev/horsing_around/Scrapping Oddschecker')

import get_data, race_cls, horse_cls, get_events_dict
get_events_dict = imp.reload(get_events_dict)

# use get_events_dict to pull data off website (get_soup) and create
#   dictionary of events that day (get_events_dict)

bsoup = get_events_dict.get_soup(base_url = 'https://www.oddschecker.com/')

eventDict = get_events_dict.get_races(bsoup = bsoup,
                                      country_codes = ['UK','IRE','AUS'])

# use eventDict to set variables when creating a race class (race_cls)
print([(key, len(eventDict[key])) for key in eventDict.keys()])

redcar2pm = race_cls.race(base_url = 'https://www.oddschecker.com/',
                          sport='horses',
                          cc=['UK','IRE','AUS'],
                          venue='Redcar', # from eventDict
                          time='14:00') # from eventDict

# interrogating various attributes of the race and horse classes within
[horse.name for horse in redcar2pm.horses] 
redcar2pm.horses[0].name
redcar2pm.horses[0].latest_odds # odds from all the bookies
redcar2pm.horses[0].stats  # statistics of the various bookies odds

#### AUTOMATED SCRIPTS STUFF ####
'''
Running the file get_events_dict.py creates a pickle file of the dictionary.

This pickle file is an input in the get_data.py file.

The get_data.py file 


















