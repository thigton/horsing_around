import pandas as pd
import numpy as np
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import string
from datetime import datetime, timedelta
import operator
import pickle
import os



def get_soup(base_url, sport = 'horses', event_url = None):
    '''Uses beautiful soup to get parse the url
    base_url = str, www.oddschecker.com/
    sport = str, which sport do you want to look at
    event_url = str, of the url extension which will take you to the '''
    
    if sport == 'horses':
        sport = 'horse-racing'
    
    url = base_url + sport
    if event_url != None:
        url += event_url
    
    req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    return soup(webpage, "html.parser")



def get_races(bsoup, country_codes, sport = 'horses'):
    '''Will return a dictionary of the events displayed on www.oddschecker.com
        Only does horse_racing atm.
        dict structure = events[countrycode][venue][list of event times]
        bsoup = the page parse with beautifulsoup4
        country_codes = countries you want to get events for
        sport = the sport you want''' 
    
    events = {code:{} for code in country_codes}
    
    # website has both todays and tomorrows races on it.  Need to only get todays races
    # this returns two objects as UK and International races are in different sections
    today  = bsoup.findAll('div', {'data-day' : 'today'}) 

    for i in range(len(today)):
        result = today[i].findAll('div', {'class' : 'race-details'})
        containers = result if i == 0  else containers + result
    
    
    for container in containers:
        txt = container.find('div', {'class' : 'venue-details'}).text
        
        for code in country_codes:
            # extract country code and venue
            if code in txt[:3]:
                cc = code
                venue = txt.replace(code, '')
                break
                
        # get event times 
        events[cc][venue] = {} # dictionary for event times
        times = [x.text for x in container.findAll('div', {'class' : 'racing-time'})]
        for t in times:
            # convert to datetime
            d_time_now = datetime.combine(datetime.today(),datetime.strptime(t, '%H:%M').time()) 
            # have a datetime 5 hours before the race as a marker to start collecting data
            start_data_collection = d_time_now - timedelta(hours=5) 
            # print(f'd_time_now = {d_time_now} , start_data_collection = {start_data_collection}')
            
            events[cc][venue][t] = start_data_collection

    return events


if __name__ == '__main__':

    # change cwd to file location
    os.chdir(os.path.dirname(os.path.realpath(__file__))) 

    url = 'https://www.oddschecker.com/'

    country_code = ['UK','IRE','AUS']

    page_soup = get_soup(url)

    events = get_races(page_soup, country_code)

    # pickle the dictionary
    try:
        os.remove('events.pickle')
        print('existing events dictionary overwritten')
    except FileNotFoundError:
        print('events.pickle doesn''t exist.  Will create now')
    
    with open('events.pickle', 'wb') as pickle_out:
            pickle.dump(events, pickle_out)