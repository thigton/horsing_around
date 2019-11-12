import pandas as pd
import numpy as np
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import string
from datetime import datetime
import race_cls
import operator
import pickle
import os
import time
import random
import smtplib
from email.message import EmailMessage
from traceback import format_exc


def get_soup(base_url, sport = 'horses', event_url = None, horse_url = None):
    '''Uses beautiful soup to get parse the url
    base_url = str, www.oddschecker.com/
    sport = str, which sport do you want to look at
    event_url = str, of the url extension which will take you to the '''

    if sport == 'horses':
        sport = 'horse-racing'

    url = base_url + sport
    if event_url != None and horse_url == None:
        url += event_url
    elif event_url != None and horse_url != None:
        url += f'{event_url}/bet-history/{horse_url}/'
    endswith=''
    req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
    while endswith != '</body></html>':
        try:
            webpage = urlopen(req).read()
            time.sleep(random.uniform(2,4))
        except:
            print('Request didn''t work!')
            print('Will try again in 5 seconds...')
            time.sleep(5)
            webpage = urlopen(req).read()
        endswith = webpage[-14:].decode(encoding='UTF-8',errors='strict')
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

                # get event times
                events[cc][venue] = {} # dictionary for event times
                times = [x.text for x in container.findAll('div', {'class' : 'racing-time'})]

                for t in times:
                    # convert to datetime
                    d_time_now = datetime.combine(datetime.today(), datetime.strptime(t, '%H:%M').time())
                    events[cc][venue][t] = d_time_now

    return events





if __name__ == '__main__':
    try:
        # change cwd to file location
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        try:
            os.remove("races.pickle")
        except:
            print('making races.pickle')

        url = 'https://www.oddschecker.com/'

        # country_code = ['UK','IRE','AUS']
        country_code = ['UK','IRE']
        page_soup = get_soup(url)
        events = get_races(page_soup, country_code)

        ## INIT the race classes - no odds data
        races = {}

        new_events = {}
        for  (cc,v) in events.items():
            new_events[cc] = {}
            for venue, times in v.items():
                new_events[cc][venue] = {}
                for time in times.keys():
                    try:
                        print(f'{venue}, {cc} at {time}')
                        races[f'{venue}_{time}'] = race_cls.race(url, 'horses', cc, venue, time)
                        new_events[cc][venue][time] = events[cc][venue][time]
                    except AttributeError:
                        print('Error occurred - Meeting cancelled?')
                        # races[f'{venue}_{time}'] = race_cls.race(url, 'horses', cc, venue, time)
                        print('Tried again and it worked')

                        ##races.pop(f'{venue}_{time}')
        events = new_events
        new_events = {}
        # Check to see if there is an empty dictionary as a meeting isn't going ahead
        for (cc, v) in events.items():
            new_events[cc] = {}
            for venue in v.keys():
                if venue: # if venue dictionary is empty
                    new_events[cc][venue] = events[cc][venue]
        events = new_events


        # pickle the dictionary
        try:
            os.remove('events.pickle')
            print('existing events dictionary overwritten')
        except FileNotFoundError:
            print('events.pickle doesn''t exist.  Will create now')

        with open('events.pickle', 'wb') as pickle_out:
                pickle.dump(events, pickle_out)

        try:
            with open('races.pickle', 'wb') as pickle_out:
                pickle.dump(races, pickle_out)
                print('races updated')
        except FileNotFoundError:
            print('races.pickle doesn''t exist')


    except Exception as e:

        EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
        EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

        contacts = ['thigton@gmail.com']

        msg = EmailMessage()
        msg['Subject'] = 'Get_events_dict.py failed - Error message'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = contacts
        msg.set_content(f'''Get_events_dict.py failed at {datetime.now().strftime("%H:%M:%S")}.

        {format_exc()}''')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)