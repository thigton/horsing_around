from datetime import datetime
from get_events_dict import get_soup
from horse_cls import horse
import operator
import pandas as pd
import numpy as np



class race():
    def __init__(self,base_url, sport, cc, venue, time):
        '''have a race as a class which we can add horse classes to.'''
        self.url  = base_url
        self.sport = sport
        self.cc = cc
        self.venue = venue
        self.time = time
        # this returns that the day is 1/1/1990 need to make it today
        self.datetime = datetime.combine(datetime.today(),datetime.strptime(self.time, '%H:%M').time())
        
        self.url_ext = '/' + self.venue.replace(' ','-') + '/' + self.time + '/' + 'winner'
        # soup the url
        soup = get_soup(self.url, self.sport, event_url = self.url_ext)
        
        # Get race data in a dictionary.  Will include things like the going, class, runners, distance, age, prize money
        race_info_container = soup.find('div', {'class':'content-right'}).findAll('li')
        self.race_info = {x.text.split(':')[0] : x.text.split(':')[1] for x in race_info_container}
        
        
        # These containers are the rows in the table on the url
        containers = soup.findAll('tr', {'class' : 'diff-row evTabRow bc'})
        # init horse class
        self.horses = [horse(container) for container in containers]
        self.rank_horses()
        
    def __str__(self):
        return f'{self.venue}, {self.cc} at {self.time}'
        
    def get_current_odds(self):
        '''Will update the odds in the horses class'''
        # soup the url
        soup = get_soup(base_url = self.url, sport = self.sport, event_url = self.url_ext)
        
        for horse in self.horses:
            #this should find the row for the horse we want
            container = soup.findAll('tr', {'data-bname': horse.name}) 
            if len(container) != 1 :
                return 'Error - more than one row with horse name found - fix the bug'
            horse.update_odds(container[0])
        
    def rank_horses(self):
        '''Orders the horses based on the value of their latest odds to find the favourite.'''
        win_prob = [(h.name , h.latest_prob.values[0]) for h in self.horses]
        win_prob.sort(key=operator.itemgetter(1), reverse = True)
        # This just orders the horse objects in the list, need to assign ranks to the horse (with time stamp)
        # And to some object associated with the race?
