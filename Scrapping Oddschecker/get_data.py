import pickle
from race_cls import race
import os




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

    print(events.values().keys())
    exit()
    races = {venue:{} for venue in events.values().keys}
    print(races)
    exit()
    # for each event check the time the script is running to determine what to do.
    # races = {venue : time}
    no_of_races = 0 
    for  (cc,v) in events.items():
        for venue, times in v.items():
            print(f'venue : {venue}')
            print(f'cc : {cc}')
            for (time, start_data_collection) in times.items():
                no_of_races += 1
                print(f'times : {start_data_collection}')
            # for time in times:
                # x = race(url,'horses', cc, venue, time)
                # break
            # break
        # break
    print(no_of_races)
    # 1. If time now before the start_data_collection datetime put in the dictionary.  Do nothing

    # 2. If the time now is after the start_data_collection datetime but before the time of the race.  
    #   a) Collect odds data and run stats
    #   b) For future if the algo finds a good betting opportunity this is where it will go.

    # 3. If the time is between the time of the race and 1 hour afterwards.  Do nothing

    # 4. If the time if after 1 hour after the race.  
    #   a) Collect the result.  
    #   b) Save data to SQL database.  
    #   c) Remove event from the events dictionary and update the pickle
    