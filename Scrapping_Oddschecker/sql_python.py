import pymysql
import pandas as pd
import sqlalchemy
import pickle
from datetime import datetime
import os
from race_cls import race
from horse_cls import horse
import mysql.connector
import numpy as np
import pytz 
import smtplib
from email.message import EmailMessage
from traceback import format_exc


if __name__ == '__main__':
    try:

        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        timezone = pytz.timezone("Europe/London")
        try:
            with open('races_for_database.pickle', 'rb') as pickle_in:
                data_dict = pickle.load(pickle_in)
                print('Loading in data for upload')
        except FileNotFoundError:
            print('races_for_database.pickle doesn''t exist')
            exit()

        host=os.environ.get('DB_HOST_IP')
        port=3306
        dbname=os.environ.get('DB_NAME')
        user=os.environ.get('DB_USER')
        password=os.environ.get('DB_PASS')
        print('connecting to database')
        # engine = pymysql.connect(host, user=user,port=port,
        #                            passwd=password, db=dbname)

        # engine = mysql.connector.connect(user=user, password=password,
        #                           host=host,
        #                           database=dbname)
        engine = sqlalchemy.create_engine(f"mysql+mysqldb://{user}:{password}@{host}/{dbname}", encoding='utf-8', echo=False)
        print('CONNECTED! WOOO!')


        # UPDATE VENUES TABLE
        venue_sql = pd.read_sql('select venue_name from venues', engine)
        venues_to_add = pd.DataFrame([(race.venue, race.cc) for race in data_dict.values() if race.venue not in venue_sql['venue_name'].values],
                                     columns=['venue_name','country_code'])
        venues_to_add.drop_duplicates(subset='venue_name', keep='first', inplace=True)
        venues_to_add['venue_added_timestamp'] = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

        # UPDATE RACES, HORSES, ODDS AND EACH WAY TABLE
        races_to_add = pd.DataFrame()
        horses_to_add = pd.DataFrame()
        odds_to_add = pd.DataFrame()
        each_way_to_add = pd.DataFrame()

        for race in data_dict.values():
            race_data = pd.DataFrame({'race_id':race.race_id, 'venue_name':race.venue, 'race_time':race.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                              'number_starters':race.race_info['Starters'], 'class':race.race_info['Class'],
                              'prize':race.race_info['Prize'], 'distance':race.race_info['Distance'],
                              'going_description':race.race_info['Going'],
                              'race_added_timestamp':datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')}, index=[0])
            races_to_add = pd.concat([races_to_add,race_data], axis=0)


            for horse in race.horses:
                horse_data = pd.DataFrame({'horse_name':horse.name, 'race_id':race.race_id, 'form':horse.form, 
                                           'horse_weight':horse.weight, 'days_since_last_run':horse.days_since_last_run, 
                                           'horse_age':horse.age,
                                           'horse_nationality':horse.nationality, 'horse_head_gear':horse.head_gear, 
                                           'horse_notables':horse.notables, 'jockey_name':horse.jockey,
                                           'jockey_form':horse.jockey_form,
                                           'jockey_claim':horse.jockey_claim, 'trainer_name':horse.trainer,
                                           'stall':horse.stall, 
                                           'result':horse.position, 'horse_analysis_text':horse.analysis_text,
                                           'horse_added_timestamp': datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')},
                                           index=[0])
                horses_to_add = pd.concat([horses_to_add,horse_data], axis=0)
                try:
                    odds_data = horse.odds
                    odds_data['race_id'] = race.race_id
                    odds_data['horse_name'] = horse.name
                    odds_data['odds_added_timestamp'] = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
                    odds_to_add = pd.concat([odds_to_add, horse.odds], axis=0, sort=True)


                except AttributeError:
                    continue


            # Some formatting for the each way table
            race_each_way_data = pd.DataFrame(race.each_way).T.rename(columns={0:'number_places_paid',1:'place_terms'})
            race_each_way_data['number_places_paid'].replace('', np.nan, inplace=True)
            race_each_way_data.dropna(inplace=True)
            race_each_way_data['number_starters'] = race.race_info['Starters']
            each_way_to_add = pd.concat([each_way_to_add, race_each_way_data], axis=0)

        odds_to_add.rename(columns={'odds':'odds_decimal', 'time':'time_odds_captured'}, inplace=True)
        odds_to_add.index.name = 'bookmaker_id'    
        odds_to_add.reset_index(inplace=True) 
        races_to_add['prize'] = races_to_add['prize'].apply(lambda x: x.encode('utf-8'))

        # SORT OUT FORMATTING FOR EACH WAY TABLE
        each_way_to_add.index.name = 'bookmaker_id'
        each_way_to_add.reset_index(inplace=True)
        # this is all the unique each way terms 
        each_way_to_add.drop_duplicates(keep='first', inplace=True)
        # Load in the SQL table.
        each_way_sql = pd.read_sql('select * from each_way', engine)
        # Stick everything on the end of the sql table
        each_way_to_add = pd.concat([each_way_sql, each_way_to_add], axis=0, sort=True)
        # Drop duplicates and keep the sql table version
        each_way_to_add.drop_duplicates(subset=['bookmaker_id', 'number_places_paid', 'place_terms', 'number_starters'],
                                        keep='first', inplace=True)
        # Fill in na in the each_way_added_timestamp
        each_way_to_add.fillna(value={'each_way_added_timestamp':datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')},
                               inplace=True)
        each_way_to_add['each_way_last_update_timestamp'] = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

        # UPLOAD BACK TO THE DATABASE
        venues_to_add.to_sql('venues',con=engine, schema='horse_test', if_exists='append',index=False)
        each_way_to_add.to_sql('each_way',con=engine, schema='horse_test', if_exists='replace',index=False)

        races_to_add.to_sql('races',con=engine, schema='horse_test', if_exists='append',index=False)
        horses_to_add.to_sql('horses',con=engine, schema='horse_test', if_exists='append',index=False)
        odds_to_add.to_sql('odds',con=engine, schema='horse_test', if_exists='append',index=False)



        # Delete races pickle files once done ready for the next day.
        os.remove("races.pickle")
        os.remove("races_for_database.pickle")

    except Exception as e:
        print(format_exc)
        exit()
        EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
        EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

        contacts = ['t.higton17@imperial.ac.uk', 'thigton@gmail.com','ed.gent@hotmail.co.uk']

        msg = EmailMessage()
        msg['Subject'] = 'sql_python.py failed - Error message'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = contacts

        msg.set_content(f'''sql_python.py failed at {datetime.now().strftime("%H:%M:%S")}.
        
        {format_exc()}''')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)


