import pickle
from race_cls import race
import os
from datetime import datetime, timedelta
import time
from datetime import date
import pprint
import pdb
import smtplib
from email.message import EmailMessage
from traceback import format_exc

def load_pickle(fname):
    """Function returns the pickle file"""
    try:
        with open(f'{fname}.pickle','rb') as pickle_in:
            data = pickle.load(pickle_in)
    except FileNotFoundError:
        print(f'{fname}.pickle doesn''t exist')
        print('run get_events_dict first')
        exit()
    return data

if __name__ == '__main__':
    FINDING_GOOD_BETS = 0
    try:
        # change cwd to file location
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        url = 'https://www.oddschecker.com/'

        # get the events dict
        events = load_pickle('events')
        races = load_pickle('races')

        for  (cc,v) in events.items():
            for venue, times in v.items():
                for time in times.keys():
                    print(f'{venue}, {cc} at {time}')
                    start_time = events[cc][venue][time]
                    start_collection = start_time - timedelta(hours=5)
                    collect_results = start_time + timedelta(hours=1)
                    races[f'{venue}_{time}'].get_result_and_stall()
                    # 2. If the time now is after the start_data_collection datetime but before the time of the race.  Start looking for good bets
                    if (datetime.now() > start_collection) and (datetime.now() < start_time ) and (FINDING_GOOD_BETS==1):
                        races[f'{venue}_{time}'].get_current_odds()
                    # 4. If the time if after 1 hour after the race collect the result
                    elif (datetime.now() > collect_results) and races[f'{venue}_{time}'].race_finished==False:
                        #   a) Collect the result.

                        races[f'{venue}_{time}'].get_full_bet_history(start_collection, start_time)
                        races[f'{venue}_{time}'].get_result_and_stall()

                    # 1. If time now before the start_data_collection datetime put in the dictionary.  Do nothing
                    # 3. If the time is between the time of the race and 2 hour afterwards.  Do nothing
                    # 5. Result has been collected. do nothing
                    elif (datetime.now() < start_collection) or \
                        (datetime.now() > start_time) and (datetime.now() < collect_results) or \
                        (races[f'{venue}_{time}'].race_finished == True):
                        print(f'Nothing to do for: {venue}, {cc} at {time}')
                        # new_events[cc][venue][time] = start_time
                    with open('races.pickle', 'wb') as pickle_out:
                        pickle.dump(races, pickle_out)
        try:
            with open('races.pickle', 'wb') as pickle_out:
                pickle.dump(races, pickle_out)
                print('races updated')
        except FileNotFoundError:
            print('races.pickle doesn''t exist')

    except EnvironmentError as e:

        EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
        EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

        contacts = ['thigton@gmail.com']

        msg = EmailMessage()
        msg['Subject'] = 'Get_data.py failed - Error message'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = contacts

        msg.set_content(f'''Get_data.py failed at {datetime.now().strftime("%H:%M:%S")}.
        Race: {venue} at {time}

        {format_exc()}''')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)



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
