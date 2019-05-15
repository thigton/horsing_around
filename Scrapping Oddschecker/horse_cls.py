from datetime import datetime
import pandas as pd
import numpy as np


class horse():
    def __init__(self, container):
        '''Creates a horse object. Will initialise the dataframe to contain the odds data '''
        try:
            self.name = container.find('a', {'class' : 'popup selTxt'}).text
        except:
            self.name = container.find('a', {'class' : 'popup selTxt has-tip'}).text
        # this also contains jockey form, need to seperate if we are going to use
        self.jockey = container.find('div' ,{'class' :'bottom-row jockey'}).text 
        
        # Get the odds
        odds = self.get_odds(container)
        #start a dataframe of the odds
        self.odds = pd.DataFrame(odds,columns = [datetime.now().replace(second = 0, microsecond=0)])
        self.latest_odds = self.odds
        self.stats = pd.DataFrame(self.get_stats())
        
                  
    def __str__(self):
        return f'{self.name} ridden by {self.jockey}'
    
    def get_odds(self, container):
        '''returns a list of the odds for the horse
        the container needs to be the row in the main table with the odds info in it.'''
        odds = container.findAll('p') # these come as strings of fractional odds
        odds_list = []
        for odd in odds:
            if '/' in odd.text:
                numbers = odd.text.split('/')
                new_odd = float(numbers[0]) / float(numbers[1]) + 1.0
            
            elif odd.text == 'SP':
                new_odd = None
            else:
                new_odd = float(odd.text) + 1.0
            odds_list.append(new_odd)
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
    
    def update_odds(self, container):
        '''Appends another column of raw odds and stats to their respective dataframes'''
        self.latest_odds = pd.Series(self.get_odds(container),
                                     name = datetime.now().replace(second = 0, microsecond=0) )
        self.odds = pd.concat([self.odds, self.latest_odds], axis = 1)
        self.stats = pd.concat([self.stats, self.get_stats()], axis = 1)
                  