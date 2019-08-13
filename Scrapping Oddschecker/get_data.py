import pickle
from race_cls import race
import os
from datetime import datetime, timedelta
import time
from datetime import date
import pprint
import pdb



if __name__ == '__main__':

    # change cwd to file location
    os.chdir(os.path.dirname(os.path.realpath(__file__))) 
    url = 'https://www.oddschecker.com/'

    # get the events dict
    try:
        with open('events.pickle','rb') as pickle_in:
            events = pickle.load(pickle_in)
    except FileNotFoundError:
        print('events.pickle doesn''t exist')
        exit()



        # get the races dict
    try:
        with open('races.pickle','rb') as pickle_in:
            races = pickle.load(pickle_in)
    except FileNotFoundError:
        print('races.pickle doesn''t exist, initialising now')
        races = {}
        with open('races.pickle', 'wb') as pickle_out:
            pickle.dump(races, pickle_out)

    try:
        with open('races_for_database.pickle','rb') as pickle_in:
            races_for_database = pickle.load(pickle_in)
    except FileNotFoundError:
        print('races_for_database.pickle doesn''t exist, initialising now')
        races_for_database = {}
        with open('races_for_database.pickle', 'wb') as pickle_out:
            pickle.dump(races_for_database, pickle_out)

    
    no_of_races = 0 

    for  (cc,v) in events.items():
        for venue, times in v.items():
            for time in times.keys():
                
                start_time = events[cc][venue][time] 
                start_collection = start_time - timedelta(hours=5)
                collect_results = start_time + timedelta(hours=2)
                
                # races[f'{venue}_{time}'] = race(url, 'horses', cc, venue, time)
                
                # 2. If the time now is after the start_data_collection datetime but before the time of the race.  
                if (datetime.now() > start_collection) and (datetime.now() < start_time ):
                    try: # update odds and statistics
                        races[f'{venue}_{time}'].get_current_odds()
                        print(f'Updating Odds: {venue}, {cc} at {time}')
                    except KeyError: # If the key doesn't exist, create the race class
                        print(f'Creating race: {venue}, {cc} at {time}')
                        races[f'{venue}_{time}'] = race(url,'horses',cc,venue,time)
                        print(f'Updating Odds: {venue}, {cc} at {time}')
                        races[f'{venue}_{time}'].get_current_odds(first_time = True)
                
                # 4. If the time if after 2 hour after the race.  
                elif (datetime.now() > collect_results):
                    #   a) Collect the result. 
                    try:
                        print(f'Collecting Results: {venue}, {cc} at {time}')
                        races[f'{venue}_{time}'].get_result()
                        races_for_database[f'{venue}_{time}'] = races.pop(f'{venue}_{time}')

                    except KeyError:
                        print(f'{venue}, {cc} at {time} hasn''t been created.  Will do it now.')
                        races[f'{venue}_{time}'] = race(url,'horses',cc,venue,time)
                        races[f'{venue}_{time}'].get_result()

                # 1. If time now before the start_data_collection datetime put in the dictionary.  Do nothing
                # 3. If the time is between the time of the race and 2 hour afterwards.  Do nothing
                # 5. Result has been collected. do nothing
                elif (datetime.now() < start_collection) or \
                    (datetime.now() > start_time) and (datetime.now() < collect_results):
                    print(f'Nothing to do for: {venue}, {cc} at {time}')
                    continue
                
    # write races and races_for_database dict to pickle
    try:
        with open('races.pickle', 'wb') as pickle_out:
            pickle.dump(races, pickle_out)
            print('races updated')
    except FileNotFoundError:
        print('races.pickle doesn''t exist')

    try:
        with open('races_for_database.pickle', 'wb') as pickle_out:
            pickle.dump(races_for_database, pickle_out)
            print('races_for_database updated')
    except FileNotFoundError:
        print('races_for_database.pickle doesn''t exist')





    # # Bookie Codes used on the website.  Might be useful in the future
    # bookies = {'Bet365': {'web_code' : 'B3'}, 
    #             'SkyBet': {'web_code' : 'SK'}, 
    #             'Ladbrokes': {'web_code' : 'LD'}, 
    #             'William Hill': {'web_code' : 'WH'}, 
    #             'Marathon': {'web_code' : 'MR'},
    #             'Betfair_SP': {'web_code' : 'FB'},  
    #             'BetVictor': {'web_code' : 'VC'},
    #             'Paddy Power': {'web_code' : 'PP'}, 
    #             'Unibet': {'web_code' : 'UN'}, 
    #             'Coral': {'web_code' : 'CE'}, 
    #             'BetFred': {'web_code' : 'FR'}, 
    #             'BetWay': {'web_code' : 'WA'}, 
    #             'ToteSport': {'web_code' : 'BX'},
    #             'BlackType': {'web_code' : 'BL'}, 
    #             'RedZone': {'web_code' : 'RZ'}, 
    #             'BoyleSports': {'web_code' : 'BY'}, 
    #             'SportPesa': {'web_code' : 'PE'}, 
    #             '10Bet': {'web_code' : 'OE'},
    #             'SportingBet': {'web_code' : 'SO'}, 
    #             'BetHard': {'web_code' : 'BH'}, 
    #             '888sport': {'web_code' : 'EE'}, 
    #             'MoPlay': {'web_code' : 'YP'}, 
    #             'SpreadEx': {'web_code' : 'SX'}, 
    #             'Sportnation': {'web_code' : 'SA'}, 
    #             'Betfair_EX': {'web_code' : 'BF'},
    #             'BetDaq': {'web_code' : 'BD'}, 
    #             'Matchbook': {'web_code' : 'MA'}, 
    #             'Smarkets': {'web_code' : 'MK'}}
    