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

# superseded mysql method

#pd.read_sql('select * from horses',engine)

# engine = sqlalchemy.create_engine("mysql+pymysql://Ed:EdTheHorse@146.148.124.146/horse_test")


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    timezone = pytz.timezone("Europe/London")
    try:
        with open('races_for_database.pickle', 'rb') as pickle_in:
            data_dict = pickle.load(pickle_in)
            print('Loading in data for upload')
    except FileNotFoundError:
        print('races_for_database.pickle doesn''t exist')
        exit()

    # USING PYMYSQL TO CONNECT ON MAC AS THERE IS A BUG WITH MACS AND SQLALCHEMY.CREATE_ENGINE.
    # PLAN A IS TO USE SQLALCHEMY.CREATE_ENGINE AS THIS IS COMPATIBLE WITH DF_TO_SQL.
    host="146.148.124.146"
    port=3306
    dbname="horse_test"
    user="Ed"
    password="EdTheHorse"
    print('connecting to database')
    # engine = pymysql.connect(host, user=user,port=port,
    #                            passwd=password, db=dbname)
    
    # engine = mysql.connector.connect(user=user, password=password,
    #                           host=host,
    #                           database=dbname)
    engine = sqlalchemy.create_engine(f"mysql+mysqldb://{user}:{password}@{host}/{dbname}")
    print('CONNECTED! WOOO!')

    cursor = engine.cursor()

    # UPDATE VENUES TABLE
    venue_sql = pd.read_sql('select venue_name from venues', engine)
    venues_to_add = pd.DataFrame([(race.venue, race.cc) for race in data_dict.values() if race.venue not in venue_sql['venue_name']],
                                 columns=['venue_name','country_code'])
    venues_to_add.drop_duplicates(subset='venue_name', keep='first', inplace=True)
    venues_to_add['venue_added_timestamp'] = datetime.now(timezone)
    
        
    # UPDATE RACES, HORSES, ODDS AND EACH WAY TABLE
    races_to_add = pd.DataFrame()
    horses_to_add = pd.DataFrame()
    odds_to_add = pd.DataFrame()
    each_way_to_add = pd.DataFrame()

    for race in data_dict.values():
        race_data = pd.DataFrame({'race_id':race.race_id, 'venue_name':race.venue, 'race_time':race.datetime,
                          'number_starters':race.race_info['Starters'], 'class':race.race_info['Class'],
                          'prize':race.race_info['Prize'], 'distance':race.race_info['Distance'],
                          'going_description':race.race_info['Going'], 'race_added_timestamp':datetime.now(timezone)}, index=[0])
        races_to_add = pd.concat([races_to_add,race_data], axis=0)
        

        for horse in race.horses:
            horse_data = pd.DataFrame({'horse_name':horse.name, 'race_id':race.race_id, 'form':horse.form, 
                                       'horse_weight':horse.weight, 'days_since_last_run':horse.days_since_last_run,' horse_age':horse.age,
                                       'horse_nationality':horse.nationality, 'horse_head_gear':horse.head_gear, 
                                       'horse_notables':horse.notables, 'jockey_name':horse.jockey, 'jockey_form':horse.jockey_form,
                                       'jockey_claim':horse.jockey_claim, 'trainer_name':horse.trainer, 'stall':horse.stall, 
                                       'result':horse.position, 'horse_analysis_text':horse.analysis_text,
                                       'horse_added_timestamp': datetime.now(timezone)}, index=[0])
            horses_to_add = pd.concat([horses_to_add,horse_data], axis=0)
            try:
                odds_data = horse.odds
                odds_data['race_id'] = race.race_id
                odds_data['horse_name'] = horse.name
                odds_to_add = pd.concat([odds_to_add, horse.odds], axis=0)
            except AttributeError:
                continue
        
        # Some formatting for the each way table
        race_each_way_data = pd.DataFrame(race.each_way).T.rename(columns={0:'number_places_paid',1:'place_terms'})
        race_each_way_data['number_places_paid'].replace('', np.nan, inplace=True)
        race_each_way_data.dropna(inplace=True)
        race_each_way_data['number_starters'] = race.race_info['Starters']
        each_way_to_add = pd.concat([each_way_to_add, race_each_way_data], axis=0)
        

    # SORT OUT FORMATTING FOR EACH WAY TABLE
    each_way_to_add.index.name = 'bookmaker_id'
    each_way_to_add.reset_index(inplace=True)
    # this is all the unique each way terms 
    each_way_to_add.drop_duplicates(keep='first', inplace=True)
    # Load in the SQL table.
    each_way_sql = pd.read_sql('select * from each_way', engine)
    # Stick everything on the end of the sql table
    each_way_to_add = pd.concat([each_way_sql, each_way_to_add], axis=0)
    # Drop duplicates and keep the sql table version
    each_way_to_add.drop_duplicates(subset=['bookmaker_id', 'number_places_paid', 'place_terms', 'number_starters'],
                                    keep='first', inplace=True)
    # Fill in na in the each_way_added_timestamp
    each_way_to_add.fillna(value={'each_way_added_timestamp':datetime.now(timezone)}, inplace=True)
    each_way_to_add['each_way_last_update_timestamp'] = datetime.now(timezone)


    # UPLOAD BACK TO THE DATABASE
    venues_to_add.to_sql('venues',con=engine, schema='horse_test', if_exists='append',index=False)
    each_way_to_add.to_sql('each_way',con=engine, schema='horse_test', if_exists='replace',index=False)

    races_to_add.to_sql('races',con=engine, schema='horse_test', if_exists='append',index=False)
    horses_to_add.to_sql('horses',con=engine, schema='horse_test', if_exists='append',index=False)
    odds_to_add.to_sql('odds',con=engine, schema='horse_test', if_exists='append',index=False)

    engine.close()

    # Delete races pickle files once done ready for the next day.
    os.remove("races.pickle")
    os.remove("races_for_database.pickle")

############################################################
# NOT USING ANYTHING BELOW THIS LINE AT THE MOMENT
############################################################

    # df_out = pd.read_sql('select * from horses',engine)
    # df = pd.DataFrame(columns = ['horse_id', 'horse_age'])
    # df.loc[0] = ['steve',8]
    # df.to_sql('horses',con=engine,if_exists='append',index=False)
    # pd.read_sql('select * from horses',engine)

############################################################
# FUNCTIONS BELOW ARE WIP
# DESIGNED FOR USE WITH PYMYSQL AS A BACKUP PLAN
############################################################

    # def input_venue(engine, race):
    #     '''ONLY USE IF USING PYMYSQL INSTEAD OF SQLALCHEMY.CREATE_ENGINE
    #     function will input venue into venue table'''
    #     # Try and find the venue name in the table
    #     cursor.execute("SELECT venue_name FROM venues where venue_name = %s LIMIT 1", (race.venue))
    #     if cursor.fetchone():
    #         pass
    #     else:
    #         cursor.execute("INSERT INTO venues VALUES (%s, %s, timestamp)", 
    #                         (race.venue, race.cc, datetime.now(timezone)))
    #     engine.commit()
    #     exit()
    
            
    
    # def input_race(engine, race):
    #     '''ONLY USE IF USING PYMYSQL INSTEAD OF SQLALCHEMY.CREATE_ENGINE
    #     function will input race into race table'''
    #     cursor.execute("INSERT INTO races VALUES (%s, %s, timestamp, %d, %s, %s, %s, %s, timestamp)", 
    #                     (race.race_id, race.venue, race.datetime, race.race_info['Starters'], 
    #                      race.race_info['Class'], race.race_info['Prize'], race.race_info['Distance'],
    #                      race.race_info['Going'], datetime.now(timezone)) )
    #     engine.commit()
        
    
    #     for horse in race.horses:
    #         input_horses(horse, race)
    
    #     def input_horses(engine, horse, race):
    #         '''ONLY USE IF USING PYMYSQL INSTEAD OF SQLALCHEMY.CREATE_ENGINE
    #         function will input horse into horse table'''
    #         sql = """INSERT INTO horses (horse_name, race_id, form, horse_weight, days_since_last_run, horse_age,
    #                  horse_nationality, horse_head_gear, horse_notables, jockey_name, jockey_form, jockey_claim,
    #                  trainer_name, stall, result, horse_analysis_text, horse_added_timestamp) 
    #                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    #         vals = (horse.name, race.race_id, horse.form, horse.weight, horse.days_since_last_run,
    #         horse.age, horse.nationality, horse.head_gear, horse.notables, horse.jockey,
    #         horse.jockey_form, horse.jockey_claim, horse.trainer, horse.stall, horse.position,
    #         horse.analysis_text, datetime.now(timezone))
    #         cursor.execute(sql, vals)
    #         engine.commit()
    
    
    #     def input_odds(engine, horse_odds_df):
    #         '''ONLY USE IF USING PYMYSQL INSTEAD OF SQLALCHEMY.CREATE_ENGINE
    #         function will input odds into odds table
    #         horse_odds_df - dataframe of odds for a horse (stored in self.horse) 
    #         (index = bookmakers, columns = time collected)'''
    #         pass
    
    
    
    # def input_each_way(engine, race):
    #     '''ONLY USE IF USING PYMYSQL INSTEAD OF SQLALCHEMY.CREATE_ENGINE
    #     function will input each_way into each_way table'''
    #     pass