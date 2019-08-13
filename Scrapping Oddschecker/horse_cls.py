from datetime import datetime
import pandas as pd
import numpy as np


class horse():
    def __init__(self, container, bookies):
        '''Creates a horse object. Will initialise the dataframe to contain the odds data '''
        name_nationality = container.find('a',{'class':'hl-name-wrap beta-footnote bold'}).text.split('(')
        self.name = name_nationality[0]
        self.nationality = name_nationality[1].replace(')','')
        jockey_trainer = list(container.find('div', {'class' : 'hl-cell hl-jockey beta-caption4'}).stripped_strings)
        self.trainer = jockey_trainer[0]

        self.jockey = jockey_trainer[1]
        jockey_claim = self.jockey.split('(')
        self.jockey = jockey_claim[0].strip()
        try:
            self.jockey_claim = jockey_claim[1].replace(')','')
        except IndexError:
            self.jockey_claim = 0
        try:
            self.days_since_last_run = container.find('span', {'class' : 'lastrundays'}).text
        except AttributeError:
            self.days_since_last_run = None
        self.form = container.find('div', {'class' : 'hl-cell hl-form'}).text
        self.age = container.find('div', {'class' : 'hl-cell hl-age beta-footnote'}).text
        card_stall = container.find('div', {'class': 'hl-cell hl-card'}).text.split('(')
        try:
            self.card = card_stall[0]
            self.stall = card_stall[1].replace(')','')
        except IndexError:
            self.stall = None

        weights = list(container.find('div',{'class' : 'hl-cell hl-weight beta-footnote'}).stripped_strings)
        self.weight = weights[0] # in stone and pounds

        try:
            self.blinkers = True if 'b' in weights[1] else False
            self.Tongue_strap = True if 't' in weights[1] else False
            self.Cheek_piece = True if 'p' in weights[1] else False
            self.hood =  True if 'h' in weights[1] else False
        except IndexError:
            self.blinkers = False
            self.Tongue_strap = False
            self.Cheek_piece = False
            self.hood =  False

                  
    def __str__(self):
        return f'{self.name} ridden by {self.jockey}'
    
    def get_odds(self, container):
        '''returns a list of the odds for the horse
        the container needs to be the row in the main table with the odds info in it.'''
        
        odds = container.findAll('td') # these should also be in order to match up with the bookies...
        odds_list = []
        for odd in odds:
            try:
                new_odd = float(odd['data-odig'])
                if odd['data-o'] == 'SP': # 0 is assigned if it is SP
                    new_odd = None
                odds_list.append(new_odd)
            except KeyError: 
                continue
        return odds_list
    
    def get_stats(self):
        '''Return some basic stats for the horses odds at a certain time'''
        mean = self.latest_odds.mean()
        std = self.latest_odds.std()
        maxx = self.latest_odds.max()
        minn = self.latest_odds.min()
        self.latest_prob = 1 / mean # use this to try and order the horses and give them a rank.
        return pd.Series( (self.latest_prob, mean,std,maxx,minn), index = ['win_prob','mean','std','max','min'], 
                         name = datetime.now().replace(second = 0, microsecond=0))
    
    def update_odds(self, container,bookies, first_time):
        '''Appends another column of raw odds and stats to their respective dataframes'''
        odds = self.get_odds(container)
        self.latest_odds = pd.Series(self.get_odds(container), index = bookies,
                                     name = datetime.now().replace(second = 0, microsecond=0) )
        if first_time == True:
            self.odds = pd.DataFrame(odds,index = bookies, columns = [datetime.now().replace(second = 0, microsecond=0)])
            self.stats = pd.DataFrame(self.get_stats())
        else:
            self.odds = pd.concat([self.odds, self.latest_odds], axis = 1)
            self.stats = pd.concat([self.stats, self.get_stats()], axis = 1)

    def get_position(self, container):
        '''gets the position of the horse.
        container, is the row containing the horses data on the website
        placed = int, this is the number of horses which are considered to have placed'''
        self.position = int(container.find('td', {'class' : 'position-cell'}).text[:-2])
        
        if self.position == 1 :
            self.win = True
        else:
            self.win = False

