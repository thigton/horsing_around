from datetime import datetime
from get_events_dict import get_soup
from horse_cls import horse
import operator
import pandas as pd
import numpy as np



class race():
    def __init__(self,base_url, sport, cc, venue, time):
        '''have a race as a class which we can add horse classes to.'''
        print(f'Creating race...')
        self.url  = base_url
        self.sport = sport
        self.cc = cc
        self.venue = venue
        self.time = time
        self.datetime = datetime.combine(datetime.today(),datetime.strptime(self.time, '%H:%M').time())
        self.race_id = f'{self.venue.upper()}_{self.datetime.strftime("%Y%m%d_%H%M")}'
        self.url_ext = '/' + self.venue.replace(' ','-') + '/' + self.time + '/' + 'winner'

        # soup the url
        soup = get_soup(self.url, self.sport, event_url = self.url_ext)

        # Get race data in a dictionary.  Will include things like the going, class, runners, distance, age, prize money
        container = soup.find('div', {'class':'content-right'}).findAll('li')
        self.race_info = {x.text.split(':')[0] : x.text.split(':')[1] for x in container}
        # Fill in None values is the information is missing
        if 'Starters' not in self.race_info.keys():
            self.race_info['Starters'] = None
        if 'Distance' not in self.race_info.keys():
            self.race_info['Distance'] = None
        if 'Class' not in self.race_info.keys():
            self.race_info['Class'] = None
        if 'Prize' not in self.race_info.keys():
            self.race_info['Prize'] = None
        if 'Going' not in self.race_info.keys():
            self.race_info['Going'] = None
        if 'Age' not in self.race_info.keys():
            self.race_info['Age'] = None
     
            print(self.race_info)
        
        # List of bookies on who are offering odds
        container = soup.find('tr', {'class':'eventTableFooter'}).findAll('td')

        self.bookies = []
        for tag in container:
            try:
                self.bookies.append(tag['data-bk'])
            except KeyError:
                continue
        if self.bookies == []:
            container = soup.find('tr', {'class':'eventTableHeader'}).findAll('td')
            for tag in container:
                try:
                    self.bookies.append(tag['data-bk'])
                except KeyError:
                    continue

        # get the number of horses part of each way (number of horses who will places)
        container = soup.find('tr', {'class' : 'eventTableFooter'})

        self.each_way = {}
        for bookie in self.bookies:
            try:
                X = container.find('td', {'data-bk':bookie})
                self.each_way[bookie] = (X['data-ew-places'], X['data-ew-div'])
            except TypeError:
                self.each_way[bookie] = (None, None)

        # These containers are the rows in the table on the url
        # containers = soup.findAll('tr', {'class' : 'diff-row evTabRow bc'})
        containers = soup.findAll('div', {'class':'hl-row'})
        # init horse class
        self.horses = [horse(container, self.bookies) for container in containers]
        # Have to get the jockey form from a different part of the HTML.
        for horses in self.horses:
            container = soup.findAll('tr', {'data-bname': horses.name}) 
            try:
                horses.get_jockey_form(container[0])
            except IndexError:
                horses.jockey_form = None

        
    def __str__(self):
        return f'{self.venue}, {self.cc} at {self.time}'
        
    def get_current_odds(self, first_time=False):
        '''Will update the odds in the horses class'''
        print(f'Updating Odds...')
        # soup the url
        soup = get_soup(base_url = self.url, sport = self.sport, event_url = self.url_ext)
    
        for horses in self.horses:
            #this should find the row for the horse we want
            container = soup.findAll('tr', {'data-bname': horses.name}) 
            if len(container) != 1 :
                return 'Error - more than one row with horses name found - fix the bug'
            horses.update_odds(container[0], self.bookies, first=first_time)

        
    def rank_horses(self):
        '''Orders the horses based on the value of their latest odds to find the favourite.'''
        win_prob = [(h.name , h.latest_prob.values[0]) for h in self.horses]
        win_prob.sort(key=operator.itemgetter(1), reverse = True)
        # This just orders the horse objects in the list, need to assign ranks to the horse (with time stamp)
        # And to some object associated with the race?
    
    def get_result(self):
        '''Method will:
        1.  Assign the position of each horse to their respective classes
        2.  Assign a True / False attribute to each horse class whether they were a winner or placed
        3.  Asssign the winning and place horse objects to an attribute of the race class. Make sure the objects aren't copied from self.horses but point at them.'''
        print(f'Collecting Results...')
        # Soup it
        soup = get_soup(base_url = self.url, sport = self.sport, event_url = self.url_ext)
        for horses in self.horses:
            #this should find the row for the horse we want
            container = soup.findAll('tr', {'data-bname': horses.name}) 
            if len(container) != 1 :
                return 'Error - more than one row with horse name found - fix the bug'
            else:
                horses.get_position(container[0])