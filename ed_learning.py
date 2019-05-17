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
import get_events_dict
imp.reload(get_events_dict)

testRace = race_cls.race(base_url='https://www.oddschecker.com/',
                         sport='horses',
                         cc='UK',
                         venue='Newbury',
                         time='13:35')

testRace.get_current_odds()

testRace.horses
testRace.race_info
testRace.rank_horses()


bsoup = get_events_dict.get_soup(base_url = 'https://www.oddschecker.com/')

eventDict = get_events_dict.get_races(bsoup = bsoup,
                                      country_codes = ['GBR'])





