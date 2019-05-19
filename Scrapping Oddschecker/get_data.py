import pickle
from race_cls import race
import os
from datetime import datetime, timedelta




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

    races = {}
    no_of_races = 0 
    for  (cc,v) in events.items():
        for venue, times in v.items():
            for time in times.keys():
                start_collection = events[cc][venue][time]
                start_time = start_collection + timedelta(hours = 5)
                collect_results = start_time + timedelta(hours = 2)
                # 1. If time now before the start_data_collection datetime put in the dictionary.  Do nothing
                if datetime.now() < start_collection:
                    break

                # 2. If the time now is after the start_data_collection datetime but before the time of the race.  
                elif (datetime.now() > start_collection) and (datetime.now() < start_time ):
                    try: # update odds and statistics
                        races[f'{venue}_{time}'].get_current_odds()
                    except KeyError: # If the key doesn't exist, create the race class
                        races[f'{venue}_{time}'] = race(url,'horses',cc,venue,time)

                # 3. If the time is between the time of the race and 2 hour afterwards.  Do nothing
                elif (datetime.now() > start_time) and (datetime.now() < collect_results ):
                    break

                # 4. If the time if after 2 hour after the race.  
                elif (datetime.now() > collect_results):
                    pass
                #   a) Collect the result.  
                #   b) Save data to SQL database.  
                #   c) Remove event from the events dictionary and update the pickle

            #     no_of_races += 1
            #     print(f'times : {start_data_collection}')
                # break
            # break
        # break
    # print(no_of_races)


    