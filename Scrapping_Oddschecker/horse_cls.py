from datetime import datetime
import pandas as pd
import numpy as np
import pytz


class horse():

    def __init__(self, container, bookies):

        '''Creates a horse object. Will initialise the dataframe to contain the odds data '''

        name_nationality = container.find('a',{'class':'hl-name-wrap beta-footnote bold'}).text.split('(')
        self.name = name_nationality[0].strip()
        if len(name_nationality) > 1:
            self.nationality = name_nationality[1].replace(')','')
        else:
            self.nationality = None

        jockey_trainer = list(container.find('div', {'class' : 'hl-cell hl-jockey beta-caption4'}).stripped_strings)
        try:
            self.trainer = jockey_trainer[0]
        except IndexError:
            self.trainer = None
        try:
            self.jockey = jockey_trainer[1]
            jockey_claim = self.jockey.split('(')
            try:
                self.jockey_claim = jockey_claim[1].replace(')','')
            except IndexError:
                self.jockey_claim = 0
        except IndexError:
            self.jockey = None
            self.jockey_claim = None

        try:
            self.days_since_last_run = container.find('span', {'class' : 'lastrundays'}).text.split('(')[0]

        except AttributeError:
            self.days_since_last_run = None
        self.form = container.find('div', {'class' : 'hl-cell hl-form'}).text
        self.age = container.find('div', {'class' : 'hl-cell hl-age beta-footnote'}).text

        weights = list(container.find('div',{'class' : 'hl-cell hl-weight beta-footnote'}).stripped_strings)
        self.weight = weights[0] # in stone and pounds
        try:
            self.head_gear = weights[1]
            self.head_gear = [c for c in self.head_gear if c.isalpha()]
            self.head_gear = ''.join(self.head_gear)
            if self.head_gear == '':
                self.head_gear = None
        except IndexError:
            self.head_gear = None

        self.notables = ''
        if container.find('a', {'class':'history-cd racecard-icon'}) is not None:
            self.notables = f'{self.notables}CD/'
        if container.find('a', {'class':'history-d racecard-icon'}) is not None:
            self.notables = f'{self.notables}D/'
        if container.find('a', {'class':'history-c racecard-icon'}) is not None:
            self.notables = f'{self.notables}C/'
        if container.find('a', {'class':'history-bf racecard-icon'}) is not None:
            self.notables = f'{self.notables}BF/'
        if len(self.notables) > 1:
            self.notables = self.notables[:-1]
        else:
            self.notables = None

        self.analysis_text = container.find('div', {'class' : 'hl-comment beta-footnote'}).text
        self.position = None

    def get_jockey_form(self, container):
        '''returns the jockeys form as an attribute.
        This is hidden in a different table to the container for the __init__'''
        try:
            self.jockey_form = container.find('span', {'class': 'current-form'}).text
        except AttributeError:
            self.jockey_form = None

    def __str__(self):
        return f'{self.name} ridden by {self.jockey}'


    def get_stats(self):
        '''Return some basic stats for the horses odds at a certain time'''
        self.consensus_mean = self.latest_odds.mean().values[0]
        self.latest_prob = 1 / self.consensus_mean # use this to try and order the horses and give them a rank.

    def update_odds(self, container, bookies):
        '''returns a list of the odds for the horse
        the container needs to be the row in the main table with the odds info in it.'''
        odds_dict = {}
        for bookie in bookies:
            odds = container.find('td', {'data-bk' : bookie})
            if odds['data-o'] == 'SP': # 0 is assigned if it is SP
                odds_dict[bookie] = None
            else:
                odds_dict[bookie] = float(odds['data-odig'])
        self.latest_odds = pd.DataFrame(list(odds_dict.items()), columns=['bookies','odds'])
        self.latest_odds.set_index('bookies', inplace=True)

    def get_position(self, container):
        '''gets the position of the horse.
        container, is the row containing the horses data on the website
        placed = int, this is the number of horses which are considered to have placed'''
        try:
            self.position = int(container.find('td', {'class' : 'position-cell'}).text[:-2])
        except ValueError:
            self.position = 'N/R'
        except AttributeError:
            print('There is something wrong with the URL!')
            self.position = None
        if self.position == 1 :
            self.win = True
        else:
            self.win = False

    def get_stall(self, container):
        """Stalls aren't released early enough for the initial grab at 9am.
        So run at time of results collection"""
        card_stall = container.find('div', {'class': 'hl-cell hl-card'}).text.split('(')
        try:
            self.card = card_stall[0]
            self.stall = card_stall[1].replace(')','')
        except IndexError:
            self.stall = None



