from datetime import datetime
from get_events_dict import get_soup
from horse_cls import horse
import operator
import pandas as pd
import numpy as np
import pickle
import itertools
import re



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

        # get alpha values
        try:
            with open('alpha.pickle', 'rb') as pickle_in:
                alpha_mat = pickle.load(pickle_in)
        except FileNotFoundError:
            print('No alpha matrix found!')
        number_starters = int(self.race_info['Starters'])
        self.alpha = alpha_mat[number_starters - 1, :number_starters-1]
        self.race_finished = False


    def __str__(self):
        return f'{self.venue}, {self.cc} at {self.time}'

    def get_current_odds(self):
        '''Will update the odds in the horses class'''
        print(f'Updating Odds...')
        # soup the url
        soup = get_soup(base_url = self.url, sport = self.sport, event_url = self.url_ext)
        for horses in self.horses:
            #this should find the row for the horse we want
            container = soup.findAll('tr', {'data-bname': horses.name})
            if len(container) != 1 :
                return 'Error - more than one row with horses name found - fix the bug'
            horses.update_odds(container[0], self.bookies)
            horses.get_stats()
        self.rank_horses()
        self.find_good_bets()


    def rank_horses(self):
        '''Orders the horses based on the value of their latest odds to find the favourite.'''
        win_prob = [[h.name , h.latest_prob] for h in self.horses]
        win_prob.sort(key=operator.itemgetter(1), reverse = True)
        for horses in self.horses:
            horses.rank = [i for i, win in enumerate(win_prob) if win[0]==horses.name][0]

    def find_good_bets(self):
        '''Function will find good bets based on the simple function'''
        def good_bet_formula(row):
            '''This takes in the rows of latest_odds and
            returns True or False whether you should bet'''
            if row['odds'] > 1/(horses.latest_prob - self.alpha[horses.rank-1]):
                print(f"Good Bet: {horses.name}, Bookies: {row.name}, odds: {row['odds']}")

        for horses in self.horses:
            horses.latest_odds.apply(good_bet_formula, axis=1)



    def get_result_and_stall(self):
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
            if horses.position == None:
                print('Something wrong with the URL - not finding any results yet')
                self.race_finished = False
        self.get_horse_stalls(soup)

    def get_full_bet_history(self, start, end):
        """Scraps the full table of bet history for each horse

        Arguments:
            start {datetime} -- start time of interest
            end {datetime} -- end time of interest
        """

        time_pattern = re.compile('..:..')
        odd_pattern = re.compile('.*/.*')
        for horses in self.horses:
            # print(horses.name)
            horse_url = horses.name.replace(' ', '-')
            soup = get_soup(base_url = self.url, sport = self.sport, event_url = self.url_ext, horse_url=horse_url)
            table = soup.find('table', {'class': 'eventTable'})
            rows = table.findAll('tr',{'class': 'eventTableRow'})
            horses_odds = []
            for row in rows:
                cells = row.findAll('td')
                for i, cell in enumerate(cells):
                    if cell.text == '':
                        continue
                    elif time_pattern.match(cell.text):
                        time = cell.text
                    else:
                        odds = cell.findAll('div')
                        for odd in odds:
                            if odd.text == 'SP':
                                continue
                            elif odd_pattern.match(odd.text):
                                numbers = odd.text.split('/')
                                the_odd = float(numbers[0]) / float(numbers[1]) + 1
                                horses_odds.append((time, the_odd, self.bookies[i-1]))
                            else:
                                horses_odds.append((time, float(odd.text) + 1, self.bookies[i-1]))
            df = pd.DataFrame(horses_odds, columns=['time_odds_captured', 'odds_decimal','bookmaker_id'])
            df.index = pd.to_datetime(df['time_odds_captured'])
            df.drop('time_odds_captured', axis=1, inplace=True)
            df = df[(df.index > start) & (df.index < end)]

            horses.full_betting_data = df

        self.race_finished = True

    def get_horse_stalls(self, soup):

        containers = soup.findAll('div', {'class':'hl-row'})
        for container in containers:
            # strip the name from the each row
            name = container.find('a',{'class':'hl-name-wrap beta-footnote bold'}).text.split('(')
            name = name[0].strip()
            # match the name to one of the horse instances
            horse_obj = next(horses for horses in self.horses if horses.name == name)
            # find the stall for that horse
            horse_obj.get_stall(container)
